"""General-purpose agent comparison arm.

Taskgate itself stays deterministic. This module is the brief's other
baseline: one general-purpose agent with the full pack and a shell.

Default scoring replays committed trials in eval/agent_baseline_trials.json
so a judge needs no API key. `--live` re-runs the same prompt with
Anthropic, OpenAI, or Groq (stdlib urllib only).
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from taskgate.models import FAMILIES, Finding, Review, ToolEvent
from taskgate.tools.fs import list_files, pack_id, read_text
from taskgate.tools.runtime import run_nop, run_oracle

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent
PROMPT_PATH = ROOT / "eval" / "agent_baseline_prompt.md"
TRIALS_PATH = ROOT / "eval" / "agent_baseline_trials.json"

FAMILY_SET = set(FAMILIES)
VERDICT_RE = re.compile(r"^VERDICT:\s*(submit|reject)\s*$", re.I | re.M)
FAMILY_RE = re.compile(r"^FAMILY:\s*([a-z_]+|none)\s*$", re.I | re.M)
SUMMARY_RE = re.compile(r"^SUMMARY:\s*(.+)$", re.I | re.M)
PATH_RE = re.compile(r"^EVIDENCE_PATH:\s*(.+)$", re.I | re.M)
SNIPPET_RE = re.compile(r"^EVIDENCE_SNIPPET:\s*(.+)$", re.I | re.M)
NOP_RE = re.compile(r"^NOP:\s*passed=(\d+)\s+failed=(\d+)\s*$", re.I | re.M)
ORACLE_RE = re.compile(
    r"^ORACLE:\s*apply_ok=(true|false)\s+passed=(\d+)\s+failed=(\d+)\s*$",
    re.I | re.M,
)

LIVE_TOOLS = [
    {
        "name": "list_files",
        "description": "List every file in the pack, relative to the pack root.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "read_file",
        "description": "Read a file in the pack. Path is relative to the pack root.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_nop",
        "description": "Run hidden tests on the starter. Change nothing.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "run_oracle",
        "description": "Run oracle/apply.py from the pack root, then run hidden tests.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "submit_review",
        "description": "Call this once when you have decided. Ends the review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "verdict": {"type": "string", "enum": ["submit", "reject"]},
                "family": {
                    "type": "string",
                    "enum": list(FAMILIES) + ["none"],
                },
                "summary": {"type": "string"},
                "evidence_path": {"type": "string"},
                "evidence_snippet": {"type": "string"},
            },
            "required": ["verdict", "family", "summary", "evidence_path", "evidence_snippet"],
            "additionalProperties": False,
        },
    },
]


def prompt_text() -> str:
    return read_text(PROMPT_PATH)


def user_prompt(pack_dir: Path) -> str:
    pack_dir = pack_dir.resolve()
    names = [str(p.relative_to(pack_dir)) for p in list_files(pack_dir)]
    listed = "\n".join(f"- {n}" for n in names) or "- (empty)"
    return (
        f"{prompt_text().strip()}\n\n"
        f"Pack directory: {pack_dir}\n"
        f"Files:\n{listed}\n"
    )


def load_trial_file(path: Path | None = None) -> dict:
    target = path or TRIALS_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"{target} is missing. Replay needs the committed trials. "
            "Record them with `python3 -m taskgate agent-baseline --live --all` "
            "or restore eval/agent_baseline_trials.json from git."
        )
    return json.loads(target.read_text(encoding="utf-8"))


def trials_for(pack_id_: str, payload: dict | None = None) -> list[dict]:
    data = payload if payload is not None else load_trial_file()
    rows = [t for t in data.get("trials") or [] if t["pack_id"] == pack_id_]
    rows.sort(key=lambda t: int(t.get("trial") or 0))
    return rows


def parse_review_block(text: str) -> dict:
    verdict_m = VERDICT_RE.search(text or "")
    if not verdict_m:
        raise ValueError("agent reply is missing a VERDICT line")
    verdict = verdict_m.group(1).lower()
    family_m = FAMILY_RE.search(text)
    family_raw = (family_m.group(1).lower() if family_m else "none")
    family = "" if family_raw in {"none", "submit"} else family_raw
    if family and family not in FAMILY_SET:
        family = ""
    if verdict == "submit":
        families: list[str] = []
    elif family:
        families = [family]
    else:
        families = []
    summary_m = SUMMARY_RE.search(text)
    path_m = PATH_RE.search(text)
    snippet_m = SNIPPET_RE.search(text)
    nop_m = NOP_RE.search(text)
    oracle_m = ORACLE_RE.search(text)
    return {
        "verdict": verdict,
        "families": families,
        "summary": (summary_m.group(1).strip() if summary_m else ""),
        "evidence_path": (path_m.group(1).strip() if path_m else ""),
        "evidence_snippet": (snippet_m.group(1).strip() if snippet_m else ""),
        "nop_passed": int(nop_m.group(1)) if nop_m else None,
        "nop_failed": int(nop_m.group(2)) if nop_m else None,
        "oracle_passed": int(oracle_m.group(2)) if oracle_m else None,
        "oracle_failed": int(oracle_m.group(3)) if oracle_m else None,
        "apply_ok": None if not oracle_m else oracle_m.group(1).lower() == "true",
        "raw": text,
    }


def majority_verdict(rows: list[dict]) -> tuple[str, list[str]]:
    if not rows:
        raise ValueError("no trials to vote on")
    reject_n = sum(1 for r in rows if r.get("verdict") == "reject")
    submit_n = len(rows) - reject_n
    verdict = "reject" if reject_n > submit_n else "submit"
    if verdict == "submit":
        return verdict, []
    counted: Counter[str] = Counter()
    for row in rows:
        if row.get("verdict") != "reject":
            continue
        for fam in row.get("families") or []:
            if fam in FAMILY_SET:
                counted[fam] += 1
    if not counted:
        return verdict, []
    return verdict, [counted.most_common(1)[0][0]]


def review_from_recorded(pack_dir: Path, payload: dict | None = None) -> Review:
    pack_dir = pack_dir.resolve()
    pid = pack_id(pack_dir)
    rows = trials_for(pid, payload)
    if not rows:
        raise FileNotFoundError(f"no recorded agent_baseline trials for {pid}")
    return _review_from_rows(pid, rows)


def _review_from_rows(pid: str, rows: list[dict]) -> Review:
    verdict, families = majority_verdict(rows)
    events = [
        ToolEvent(
            tool="agent_baseline.prompt",
            input=str(PROMPT_PATH.relative_to(ROOT)),
            output="full pack + shell; no skill file; no mechanics.yml; no gold labels",
        )
    ]
    findings: list[Finding] = []
    for row in rows:
        trial_n = row.get("trial")
        events.append(
            ToolEvent(
                tool=f"agent_baseline.trial_{trial_n}",
                input=str(row.get("model") or "recorded"),
                output=_trial_event_output(row),
            )
        )
        if row.get("verdict") == "reject":
            fams = row.get("families") or []
            findings.append(
                Finding(
                    family=fams[0] if fams else "malformed",
                    summary=row.get("summary") or f"trial {trial_n} rejected",
                    path=row.get("evidence_path") or "NOP",
                    snippet=row.get("evidence_snippet") or "",
                )
            )
    events.append(
        ToolEvent(
            tool="agent_baseline.majority",
            input=f"{len(rows)} trials",
            output=f"verdict={verdict} families={families} votes={_vote_line(rows)}",
        )
    )
    live_findings = []
    if verdict == "reject" and families:
        match = next((f for f in findings if f.family == families[0]), None)
        live_findings = [match] if match else [
            Finding(
                family=families[0],
                summary="Majority of agent trials rejected this pack.",
                path="NOP",
                snippet=_vote_line(rows),
            )
        ]
    source = next((r for r in reversed(rows) if r.get("verdict") == verdict), rows[-1])
    if verdict == "reject" and families:
        source = next(
            (
                r
                for r in reversed(rows)
                if families[0] in (r.get("families") or [])
            ),
            source,
        )
    return Review(
        pack_id=pid,
        stage="agent_baseline",
        verdict=verdict,  # type: ignore[arg-type]
        families=families,
        findings=live_findings,
        events=events,
        notes=[
            "comparison arm: general-purpose agent, full pack + shell",
            f"trials: {_vote_line(rows)}",
        ],
        nop_passed=source.get("nop_passed"),
        nop_failed=source.get("nop_failed"),
        oracle_passed=source.get("oracle_passed"),
        oracle_failed=source.get("oracle_failed"),
    )


def _vote_line(rows: list[dict]) -> str:
    parts = []
    for row in rows:
        fams = ",".join(row.get("families") or ["-"])
        parts.append(f"t{row.get('trial')}={row.get('verdict')}/{fams}")
    return " ".join(parts)


def _trial_event_output(row: dict) -> str:
    fams = ",".join(row.get("families") or []) or "none"
    bits = [
        f"verdict={row.get('verdict')} family={fams}",
        row.get("summary") or "",
        f"evidence={row.get('evidence_path')}: {row.get('evidence_snippet')}",
        f"NOP passed={row.get('nop_passed')} failed={row.get('nop_failed')}",
        f"ORACLE passed={row.get('oracle_passed')} failed={row.get('oracle_failed')}",
    ]
    raw = (row.get("raw") or "").strip()
    if raw:
        bits.append(raw[:900])
    return "\n".join(bit for bit in bits if bit)


def trial_metrics(payload: dict, gold: dict) -> dict:
    """Per-trial accuracy and how often the three runs agreed."""
    by_pack: dict[str, list[dict]] = {}
    for row in payload.get("trials") or []:
        by_pack.setdefault(row["pack_id"], []).append(row)
    per_trial: dict[int, list[bool]] = {}
    unanimous = 0
    scored = 0
    for pid, rows in by_pack.items():
        if pid not in gold:
            continue
        scored += 1
        verdicts = [r.get("verdict") for r in rows]
        if verdicts and all(v == verdicts[0] for v in verdicts):
            unanimous += 1
        for row in rows:
            n = int(row.get("trial") or 0)
            per_trial.setdefault(n, []).append(row.get("verdict") == gold[pid].verdict)
    trial_acc = {
        f"t{n}": (sum(hits) / len(hits) if hits else 0.0)
        for n, hits in sorted(per_trial.items())
    }
    return {
        "n_packs": scored,
        "unanimous": unanimous,
        "unanimous_rate": (unanimous / scored) if scored else 0.0,
        "per_trial_accuracy": trial_acc,
    }


def live_review(pack_dir: Path, trial: int = 1, max_turns: int = 12) -> dict:
    """One live agent review. Requires ANTHROPIC_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY."""
    pack_dir = pack_dir.resolve()
    provider, model, key = _provider()
    events: list[dict] = []
    decision: dict | None = None

    def tool_exec(name: str, args: dict) -> str:
        nonlocal decision
        if name == "submit_review":
            decision = {
                "verdict": str(args.get("verdict") or "submit").lower(),
                "families": []
                if str(args.get("family") or "none").lower() in {"none", "submit"}
                else [str(args["family"]).lower()],
                "summary": str(args.get("summary") or ""),
                "evidence_path": str(args.get("evidence_path") or ""),
                "evidence_snippet": str(args.get("evidence_snippet") or ""),
                "raw": json.dumps(args, indent=2),
            }
            if decision["verdict"] == "submit":
                decision["families"] = []
            elif decision["families"] and decision["families"][0] not in FAMILY_SET:
                decision["families"] = []
            return "recorded"
        return _run_pack_tool(pack_dir, name, args)

    text = _run_provider(
        provider,
        model,
        key,
        user_prompt(pack_dir),
        tool_exec,
        events,
        max_turns,
    )
    if decision is None:
        decision = parse_review_block(text)
    nop = run_nop(pack_dir)
    oracle = run_oracle(pack_dir)
    decision.setdefault("nop_passed", nop.passed)
    decision.setdefault("nop_failed", nop.failed)
    decision.setdefault("oracle_passed", oracle.passed)
    decision.setdefault("oracle_failed", oracle.failed)
    if decision.get("nop_passed") is None:
        decision["nop_passed"] = nop.passed
        decision["nop_failed"] = nop.failed
    if decision.get("oracle_passed") is None:
        decision["oracle_passed"] = oracle.passed
        decision["oracle_failed"] = oracle.failed
    decision.update(
        {
            "pack_id": pack_id(pack_dir),
            "trial": trial,
            "model": f"{provider}:{model}",
            "events": events,
        }
    )
    return decision


def record_live_suite(packs_dir: Path, pack_ids: list[str], trials: int, out: Path) -> dict:
    existing = {"meta": {}, "trials": []}
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))
    kept = [
        t
        for t in existing.get("trials") or []
        if not (t.get("pack_id") in pack_ids and int(t.get("trial") or 0) <= trials)
    ]
    provider, model, _ = _provider()
    old_meta = existing.get("meta") or {}
    keep_keys = ("models", "contamination_note", "recorded_at", "note", "cost")
    meta = {k: old_meta[k] for k in keep_keys if k in old_meta}
    meta.update(
        {
            "prompt": str(PROMPT_PATH.relative_to(ROOT)),
            "n_trials": trials,
            "resources": "full pack + list/read/nop/oracle tools; no skill; no mechanics.yml; no gold",
            "provider_note": "live API run; numbers will drift across models and retries",
            "model": f"{provider}:{model}",
        }
    )
    for pid in pack_ids:
        for trial in range(1, trials + 1):
            row = live_review(packs_dir / pid, trial=trial)
            kept.append({k: row[k] for k in row if k != "events"})
    payload = {"meta": meta, "trials": kept}
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def _run_pack_tool(pack_dir: Path, name: str, args: dict) -> str:
    if name == "list_files":
        names = [str(p.relative_to(pack_dir)) for p in list_files(pack_dir)]
        return "\n".join(names) or "(empty)"
    if name == "read_file":
        path = _safe_path(pack_dir, str(args.get("path") or ""))
        if path.is_dir():
            return f"{path.name}/ is a directory"
        text = path.read_text(encoding="utf-8", errors="replace")
        return text if len(text) <= 8000 else text[:8000] + "\n…[truncated]"
    if name == "run_nop":
        result = run_nop(pack_dir)
        return f"passed={result.passed} failed={result.failed}\n{result.output[-1200:]}"
    if name == "run_oracle":
        result = run_oracle(pack_dir)
        return (
            f"apply_ok={result.apply_ok} passed={result.passed} failed={result.failed}\n"
            f"{result.output[-1200:]}"
        )
    return f"unknown tool: {name}"


def _safe_path(pack_dir: Path, rel: str) -> Path:
    pack = pack_dir.resolve()
    raw = (rel or "").strip() or "."
    path = (pack / raw).resolve()
    if path != pack and pack not in path.parents:
        raise ValueError(f"path escapes pack: {rel}")
    if not path.exists():
        raise FileNotFoundError(rel)
    return path


def _provider() -> tuple[str, str, str]:
    anthropic = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    openai = os.environ.get("OPENAI_API_KEY", "").strip()
    groq = os.environ.get("GROQ_API_KEY", "").strip()
    if anthropic:
        model = os.environ.get("TASKGATE_AGENT_MODEL", "claude-haiku-4-5-20251001")
        return "anthropic", model, anthropic
    if groq:
        model = os.environ.get("TASKGATE_AGENT_MODEL", "qwen/qwen3.8-27b")
        return "groq", model, groq
    if openai:
        model = os.environ.get("TASKGATE_AGENT_MODEL", "gpt-4o-mini")
        return "openai", model, openai
    raise RuntimeError(
        "Live agent-baseline needs ANTHROPIC_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY. "
        "Replay the committed trials instead: python3 -m taskgate eval --stage agent_baseline"
    )


def _run_provider(
    provider: str,
    model: str,
    key: str,
    user: str,
    tool_exec,
    events: list[dict],
    max_turns: int,
) -> str:
    if provider == "anthropic":
        return _run_anthropic(model, key, user, tool_exec, events, max_turns)
    base = (
        "https://api.groq.com/openai/v1"
        if provider == "groq"
        else os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    )
    return _run_openai(model, key, user, tool_exec, events, max_turns, base_url=base)


def _run_anthropic(model, key, user, tool_exec, events, max_turns) -> str:
    messages: list[dict] = [{"role": "user", "content": user}]
    last_text = ""
    for _ in range(max_turns):
        data = _http_json(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            {
                "model": model,
                "max_tokens": 2048,
                "tools": LIVE_TOOLS,
                "messages": messages,
            },
        )
        blocks = data.get("content") or []
        messages.append({"role": "assistant", "content": blocks})
        last_text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        uses = [b for b in blocks if b.get("type") == "tool_use"]
        if not uses:
            return last_text
        results = []
        for block in uses:
            name = block.get("name") or ""
            args = block.get("input") or {}
            try:
                output = tool_exec(name, args)
            except Exception as exc:  # noqa: BLE001 — tool error goes back to the model
                output = f"error: {exc}"
            events.append({"tool": name, "input": json.dumps(args), "output": output[:1500]})
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": output[:8000],
                }
            )
            if name == "submit_review":
                return last_text
        messages.append({"role": "user", "content": results})
    return last_text


def _openai_tools() -> list[dict]:
    out = []
    for tool in LIVE_TOOLS:
        out.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
        )
    return out


def _run_openai(model, key, user, tool_exec, events, max_turns, base_url: str = "https://api.openai.com/v1") -> str:
    messages: list[dict] = [
        {"role": "system", "content": prompt_text()},
        {"role": "user", "content": user},
    ]
    last_text = ""
    url = base_url.rstrip("/") + "/chat/completions"
    for _ in range(max_turns):
        data = _http_json(
            url,
            {
                "authorization": f"Bearer {key}",
                "content-type": "application/json",
                "user-agent": "taskgate-agent-baseline/1.0",
            },
            {
                "model": model,
                "max_tokens": 2048,
                "tools": _openai_tools(),
                "messages": messages,
            },
        )
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        messages.append(message)
        last_text = message.get("content") or last_text
        calls = message.get("tool_calls") or []
        if not calls:
            return last_text or ""
        for call in calls:
            fn = call.get("function") or {}
            name = fn.get("name") or ""
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            try:
                output = tool_exec(name, args)
            except Exception as exc:  # noqa: BLE001
                output = f"error: {exc}"
            events.append({"tool": name, "input": json.dumps(args), "output": output[:1500]})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": output[:8000],
                }
            )
            if name == "submit_review":
                return last_text or ""
    return last_text or ""


def _http_json(url: str, headers: dict, payload: dict) -> dict:
    raw = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(6):
        req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_err = RuntimeError(f"HTTP {exc.code} from {url}: {body[:800]}")
            if exc.code != 429 or attempt == 5:
                raise last_err from exc
            wait = _retry_seconds(body, attempt)
            time.sleep(wait)
    raise last_err or RuntimeError(f"HTTP failure from {url}")


def _retry_seconds(body: str, attempt: int) -> float:
    match = re.search(r"try again in ([0-9.]+)\s*s", body, re.I)
    if match:
        return min(float(match.group(1)) + 0.5, 60.0)
    return min(2 ** attempt, 20)
