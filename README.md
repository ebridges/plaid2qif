### Description

Provides a mechanism for downloading transactions from various financial institutions (as supported by [Plaid](https://www.plaid.com)), and converts to formats (specifically QIF & CSV) usaable by financial software (especially GNUCash).

### Authentication

* Run a webserver on this directory and open `auth.html`.
* Enter credentials for chosen institution & copy `public_token` from browser console.
* Add your own personal credentials for Plaid to `./plaid-credentials.json`.
* Add each individual account credentials to a distinct file in `./cfg`.  File should be named as `cfg/<account-name>.json`

### Usage

* Install by running `python3 setup.py install`
* See usage by running `plaid2qif --help`
