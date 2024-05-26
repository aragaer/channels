.PHONY: test dist pypi

test:
	nose2

dist:
	rm -rf dist
	poetry build

pypi: dist
	poetry publish
