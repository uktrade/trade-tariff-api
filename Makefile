.PHONY: check-flake8
check-flake8:
	flake8 .

.PHONY: check-black
check-black:
	black --exclude=venv --skip-string-normalization --check .

.PHONY: check-pylint
check-pylint:
	python3 -m pylint.__main__ --rcfile .pylintrc .

.PHONY: check
check: check-flake8 check-black check-pylint

.PHONY: format
format:
	black --exclude=venv --skip-string-normalization .

.PHONY: save-requirements
save-requirements:
	pip-compile requirements.in
	pip-compile requirements-dev.in
