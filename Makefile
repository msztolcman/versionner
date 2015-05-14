doc:
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

clean:
	rm dist/*
	rm -fr __pycache__
	rm -fr versionner/__pycache__
	rm -fr build

build:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

upload:
	twine upload dist/versionner*
