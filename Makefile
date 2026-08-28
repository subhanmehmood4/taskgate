PYTHON ?= python3
export PYTHONPATH := $(CURDIR)

.PHONY: list review demo eval holdout results

list:
	$(PYTHON) -m taskgate list

review:
	$(PYTHON) -m taskgate review packs/03-nop-already-green

demo:
	$(PYTHON) -m taskgate baseline packs/03-nop-already-green
	$(PYTHON) -m taskgate review packs/03-nop-already-green
	$(PYTHON) -m taskgate review packs/12-reskin-rollup
	$(PYTHON) -m taskgate review packs/11-timestamp-fold

eval:
	$(PYTHON) -m taskgate eval --stage all

holdout:
	$(PYTHON) -m taskgate eval --holdout

results:
	@ls -1 results
