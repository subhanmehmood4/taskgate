from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _scrub_pack_paths(text: str, pack_tmp: Path) -> str:
    """Drop the random tempfile prefix so trajectories stay stable."""
    roots = {str(pack_tmp), str(pack_tmp.resolve())}
    extra: set[str] = set()
    for root in roots:
        if root.startswith("/var/"):
            extra.add("/private" + root)
        if root.startswith("/private/var/"):
            extra.add(root[len("/private") :])
    out = text
    for root in sorted(roots | extra, key=len, reverse=True):
        out = out.replace(root + "/", "").replace(root, "<pack>")
    return out


@dataclass
class RunResult:
    passed: int
    failed: int
    output: str
    apply_ok: bool = True
    apply_output: str = ""


def _run_unittests(tmp: Path) -> RunResult:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp / "workspace")
    test_file = tmp / "tests" / "test_task.py"
    if test_file.exists():
        cmd = [sys.executable, str(test_file)]
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(tmp / "tests"), "-t", str(tmp), "-q"]
    proc = subprocess.run(
        cmd,
        cwd=tmp,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    text = _scrub_pack_paths((proc.stdout or "") + (proc.stderr or ""), tmp)
    # unittest -q prints "Ran N tests" and "FAILED (failures=X)" or "OK"
    passed, failed = _parse_unittest(text, proc.returncode)
    return RunResult(passed=passed, failed=failed, output=text[-2000:])


def _parse_unittest(text: str, returncode: int) -> tuple[int, int]:
    ran = 0
    failed = 0
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Ran "):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                ran = int(parts[1])
        if line.startswith("FAILED"):
            # FAILED (failures=2, errors=1)
            import re

            nums = [int(n) for n in re.findall(r"=(\d+)", line)]
            failed = sum(nums) if nums else ran
    if returncode == 0:
        return ran, 0
    if failed == 0:
        failed = ran if ran else 1
    passed = max(ran - failed, 0)
    return passed, failed


def run_nop(pack_dir: Path) -> RunResult:
    tmp = Path(tempfile.mkdtemp(prefix="taskgate-nop-"))
    try:
        shutil.copytree(pack_dir, tmp / "pack", dirs_exist_ok=True)
        return _run_unittests(tmp / "pack")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_oracle(pack_dir: Path) -> RunResult:
    tmp = Path(tempfile.mkdtemp(prefix="taskgate-oracle-"))
    try:
        dest = tmp / "pack"
        shutil.copytree(pack_dir, dest, dirs_exist_ok=True)
        apply = dest / "oracle" / "apply.py"
        apply_ok = True
        apply_out = "no oracle/apply.py"
        if apply.exists():
            proc = subprocess.run(
                [sys.executable, str(apply)],
                cwd=dest,
                capture_output=True,
                text=True,
                timeout=20,
            )
            apply_ok = proc.returncode == 0
            apply_out = _scrub_pack_paths(
                ((proc.stdout or "") + (proc.stderr or ""))[-800:], dest
            )
        tests = _run_unittests(dest)
        tests.apply_ok = apply_ok
        tests.apply_output = apply_out
        return tests
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
