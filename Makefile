.PHONY: bootstrap test

bootstrap:
	bash scripts/bootstrap_repo.sh

test:
	pytest -q
