.PHONY: validate test doctor index
validate:
	python -m axiom_cli repo validate

test:
	python -m pytest -q

doctor:
	python -m axiom_cli doctor

index:
	python -m axiom_cli graph build .
