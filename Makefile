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

.DEFAULT_GOAL := help
help:
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
