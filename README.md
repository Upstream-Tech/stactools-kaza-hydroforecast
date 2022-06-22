# stactools-kaza-hydroforecast

[![PyPI](https://img.shields.io/pypi/v/stactools-kaza-hydroforecast)](https://pypi.org/project/stactools-kaza-hydroforecast/)

- Name: kaza-hydroforecast
- Package: `stactools.kaza_hydroforecast`
- PyPI: https://pypi.org/project/stactools-kaza-hydroforecast/
- Owner: @aldenks
- Dataset homepage: https://dashboard.hydroforecast.com/public/wwf-kaza
- STAC extensions used:
  - [table](https://github.com/stac-extensions/table/)

This repository generates a STAC catalog for accessing a dataset of daily updated HydroForecast seasonal river flow forecasts at six locations in the Kwando and Upper Zambezi river basins. More details about the locations, project context, and to interactively view current and previous forecasts, visit our [public website](https://dashboard.hydroforecast.com/public/wwf-kaza).

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

## Installation
```shell
pip install stactools-kaza-hydroforecast
```

## Command-line Usage

Description of the command line functions

```shell
$ stac kaza-hydroforecast create-collection destination
$ stac kaza-hydroforecast create-item source destination
```

Use `stac kaza-hydroforecast --help` to see all subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
$ pip install -e .
$ pip install -r requirements-dev.txt
$ pre-commit install
```

To check all files:

```shell
$ pre-commit run --all-files
```

To run the tests:

```shell
$ pytest -vv
```
