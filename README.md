[![CircleCI](https://circleci.com/gh/ebridges/plaid2qif/tree/master.svg?style=svg)](https://circleci.com/gh/ebridges/plaid2qif/tree/master)
[![GitHub watchers](https://img.shields.io/github/watchers/badges/shields.svg?style=social&label=Watch&style=flat-square)]()
[![Crates.io](https://img.shields.io/crates/l/rustc-serialize.svg?style=flat-square)]()
[![PyPi](https://img.shields.io/pypi/v/plaid2qif.svg?style=flat-square)](https://pypi.org/project/plaid2qif)
\
\
[![Plaid2QIF Logo](gen-access-token/icon.svg)](https://github.com/eqbridges/plaid2qif)
# Plaid2QIF

## Description

Plaid2QIF downloads transactions from various financial institutions in JSON format and converts to formats usable by financial software.

### Output Formats supported:
* [QIF](https://en.wikipedia.org/wiki/Quicken_Interchange_Format)
* CSV
* JSON
* Extensible to others

### Notes
* Tested extensively with [GnuCash](https://www.gnucash.org/).  Supported by any financial software that supports import from [QIF](https://en.wikipedia.org/wiki/Quicken_Interchange_Format).
* Supports any institution supported by [Plaid](https://www.plaid.com).

## Summary

```
  # Download transactions in various formats (default QIF) from Plaid
  plaid2qif download \
    --account=<account-name> \
    --account-type=<type> \
    --account-id=<acct-id> \
    --from=<from-date> \
    --to=<to-date> \
    [--output-format=<format>] \
    [--output-dir=<path>] \
    [--ignore-pending] \
    [--verbose]
```

## Usage

1. Install the `plaid2qif` command using `pip`

        $ pip install plaid2qif

2. Authenticate and link with your financial institution (first time only).  To do this, follow the steps for using the associated [Account Linker](gen-access-token/README.md) tool.

3. Configure your environment with required values. See "Authentication Configuration" below.

3. Once configured, you're ready to download transactions and save them as QIF files:

        plaid2qif download \
            --from=<yyyy-mm-dd> \
            --to=<yyyy-mm-dd> \
            --account-type=<type> \
            --account=<account-name> \
            --account-id=<plaid-account-id> \
            --credentials=<file>

  * `account` is the path to an account in the ledger in GnuCash that you ultimately want to import the transactions to.  This is added to the `!Account` header in the QIF file.  e.g.: `Assets: Checking Accounts:Personal Checking Account`.  If the name has spaces be sure to quote this param.
  * `account-type` is a GnuCash account identifier type as [documented here](https://github.com/Gnucash/gnucash/blob/cdb764fec525642bbe85dd5a0a49ec967c55f089/gnucash/import-export/qif-imp/file-format.txt#L23).
  * `account-id` is Plaid's account ID for the account you want to download, as obtained via `list-accounts` above.
  * By default, output will go to stdout to be redirected.  If you want it to be written to a location use the `output-dir` parameter.

## Authentication Configuration

* You will need the following information configured in your environment in order to use this tool.
* The suggested way to populate your environment would be to use a file named `.env` in your current working directory.  Alternatively you could put the values in your `~/.profile` or however you normally initialize your environment.

Configuration Parameter | Environment Variable Name | Description | Notes
---------|----------|---------|---------
 Client ID | `PLAID_CLIENT_ID` | Plaid's unique indentifier for your Plaid account. [Obtain from your dashboard](https://dashboard.plaid.com/overview/development) | Required.
 Client Secret | `PLAID_SECRET` | Plaid's authentication token for your Plaid account. [Obtain from your dashboard](https://dashboard.plaid.com/overview/development) | Required.
 Plaid Environment | `PLAID_ENV` | Operating environment. | Optional. Should be one of: `sandbox`, `development`, or `production`.  Defaults to `development`.
 Plaid API Version | `PLAID_API_VERSION` | Version of the API that the `plaid-python` library supports. | Optional.  Defaults to `2020-09-14`
 Access Token location | `ACCESS_TOKEN_FILE` | Location of the token that grants access to a particular financial institution for downloading records from. | Required.

### **Notes on Authentication Configuration**

* The access token and Plaid credentials are sensitive material as they grant access to data within your financial accounts.  They should be handled carefully and not shared.

* These are the most important values that need configuration in order to authenticate with your institution and then download records.  Other values can be found in the [sample.env](./sample.env).

* If you're downloading from different institutions that result in multiple access token files, you can override the location of the file at the command line; see below for an example.  _This approach is open to suggestions for improvement if this doesn't work well for others. See Issue #27._

        $ ACCESS_TOKEN_FILE=./cfg/chase.txt plaid2qif ...
        $ ACCESS_TOKEN_FILE=./cfg/citi.txt plaid2qif ...


## Distribution

```
# increment version in `plaid2qif/__init__.py`
# commit everything & push
$ git tag -s vX.Y.Z
$ git push --tags
$ python3 setup.py sdist bdist_wheel
$ twine upload dist/*
```
