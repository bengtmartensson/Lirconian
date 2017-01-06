all: style

style: pep8 pylint


pep8: .phony
	python3-pep8 --config=pep8.conf *.py

pylint: .phony
	python3-pylint --rcfile=pylint.conf *.py


.phony:
