
format:
	@black .

isort:
	@isort .

optimise-imports:
	@autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports .

pretty: optimise-imports isort format

lint:
	@pylint --rcfile=setup.cfg .

typecheck:
	mypy --show-error-codes .

importcheck:
	@pylint --disable=all --enable=unused-import .

stylecheck:
	@black --check module02
	@isort --check-only module02
	@flake8 module02

check: stylecheck typecheck lint