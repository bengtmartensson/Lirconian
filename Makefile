PYTHON=python3
PIP=pip3.5
PACKAGE=lirconian
VERSION=$(shell bin/$(PACKAGE) --version)

all: sdist bdist

style: pep8 pylint

pep8:
	-python3-pep8 --config=pep8.conf lirconian/*.py

pylint:
	-python3-pylint --rcfile=pylint.conf lirconian/*.py

install:
	$(PIP) install .

install-user:
	$(PIP) install --user .

uninstall:
	$(PIP) uninstall $(PACKAGE)

sdist: dist/$(PACKAGE)-$(VERSION).tar.gz

bdist: dist/$(PACKAGE)-$(VERSION)-py2.py3-none-any.whl

dist/$(PACKAGE)-$(VERSION).tar.gz: setup.py
	$(PYTHON) setup.py  sdist

dist/$(PACKAGE)-$(VERSION)-py2.py3-none-any.whl:
	$(PYTHON) setup.py bdist_wheel

clean:
	rm -rf dist build __pycache__ $(PACKAGE).egg-info

.PHONY: pep8 pylint clean
