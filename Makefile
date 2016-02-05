doc:
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

clean:
	rm dist/* || true
	rm -fr __pycache__ || true
	rm -fr versionner/__pycache__ || true
	rm -fr build || true

build:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

upload:
	twine upload dist/versionner*

distro: clean build upload

register:
	python setup.py register
