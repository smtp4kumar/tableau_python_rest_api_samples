
# rest-api-samples
This repository contains Python samples for the Tableau REST API. It is refactoring of original repo https://github.com/tableau/rest-api-samples

# Improvements

1. Refactor to adopt the principle of re-usability. Example - We now have single object to perform workbook related operations.

2. Replace "argparse" with "click"

This project is based on python package named Click to provide command line interface.
This framework is to build complex cli applications that load subcommands dynamically from a plugin folder.

Rationale - https://click.palletsprojects.com/en/7.x/why/

3. Adopt pipenv to manage python virtual environment

The runtime is managed by pyenv, which is a python version manager tool and pipenv, which is a wrapper tool of
pip and virtualenv for dependency and virtual environment management.

Rationale - https://realpython.com/pipenv-guide/#problems-that-pipenv-solves

4. Bundle the samples and runtime environment in a docker file
https://github.com/smtp4kumar/tableau_python_rest_api_samples/blob/master/python/Dockerfile

Rationale - Fast, consistent delivery of the sample scripts



