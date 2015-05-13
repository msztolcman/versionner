doc:
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

build:
	python setup.py sdist
	python setup.py bdist_wheel

upload:
	twine upload dist/versionner*

