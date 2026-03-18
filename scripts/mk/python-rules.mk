# TODO Update this variable
MODULE ?= git_tb

.PHONY: all
all: format lint doc test

.PHONY: deps
deps: .venv  ## Install dependencies in a python virtual environment
	. .venv/bin/activate; pip install -U pip
	. .venv/bin/activate; pip install poetry
	. .venv/bin/activate; python3 -m poetry install --no-root

.PHONY: install
install:
	[ -e "$(HOME)/.local/bin/git-tb" ] || mkdir -p "$(HOME)/.local/bin"
	cp git_tb/git_tb.py "$(HOME)/.local/bin/git-tb" && chmod 0740 "$(HOME)/.local/bin/git-tb"

.venv:
	python3 -m venv .venv

.PHONY: format
format: .venv   ## Apply format rules to the python code
	. .venv/bin/activate; black "${MODULE}"
	. .venv/bin/activate; black tests

.PHONY: lint
lint: .venv  ## Run linter on the python code
	. .venv/bin/activate; pylint "${MODULE}"

.PHONY: run
run: .venv  ## Execute hello_world
	. .venv/bin/activate; python3 -m "${MODULE}"

.PHONY: debug
debug: .venv  ## Run PDB debugger
	. .venv/bin/activate; python3 -m pdb -m "$(MODULE)"

.PHONY: test
test: .venv  ## Run tests
	. .venv/bin/activate; python3 -m pytest

.PHONY: test-cov
test-cov: .venv  ## Get coverage report
	. .venv/bin/activate; python3 -m \
	  pytest --cov=${MODULE}

.PHONY: doc
doc: .venv  ## Generate documentation from the source code
	# TODO Update your module name
	. .venv/bin/activate; pdoc3 --force -o docs/ "${MODULE}"

