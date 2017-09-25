## building
distro: ## build and upload distro
	clean build upload

init: ## initialize environment
	pip install -r requirements.txt

init-dev: ## initialize dev environment
	pip install -r requirements-dev.txt

doc: ## convert documentation to RST
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

clean: ## cleanup all distro
	-rm -fr dist
	-rm -fr __pycache__
	-rm -fr versionner/__pycache__
	-rm -fr build

build: ## build distro
	python3 setup.py sdist
	python3 setup.py bdist_wheel

upload: ## upload distro
	twine upload dist/versionner*
