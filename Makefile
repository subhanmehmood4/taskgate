PYTHON ?= python3
export PYTHONPATH := $(CURDIR)

.PHONY: list review demo eval holdout agent-baseline results

list:
	$(PYTHON) -m taskgate list

review:
	$(PYTHON) -m taskgate review packs/03-nop-already-green

demo:
	$(PYTHON) -m taskgate baseline packs/03-nop-already-green
	$(PYTHON) -m taskgate review packs/03-nop-already-green
	$(PYTHON) -m taskgate review packs/12-reskin-rollup
	$(PYTHON) -m taskgate review packs/11-timestamp-fold
	$(PYTHON) -m taskgate agent-baseline packs/06-restore-discount

eval:
	$(PYTHON) -m taskgate eval --stage all

holdout:
	$(PYTHON) -m taskgate eval --holdout

agent-baseline:
	$(PYTHON) -m taskgate eval --stage agent_baseline

results:
	@ls -1 results
