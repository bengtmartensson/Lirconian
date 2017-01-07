all: style

style: pep8 pylint


pep8:
	-python3-pep8 --config=pep8.conf *.py

pylint:
	-python3-pylint --rcfile=pylint.conf *.py


.PHONY: pep8 pylint
