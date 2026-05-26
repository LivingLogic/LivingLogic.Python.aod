.PHONY: install build upload clean


install:
	pip install -e .


build: clean
	python$(PYVERSION) -m build


upload: build
	twine upload dist/*


clean:
	rm -rf dist/*
