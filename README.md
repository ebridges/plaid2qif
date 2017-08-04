[![CircleCI](https://img.shields.io/circleci/project/github/ebridges/plaid2qif.svg?style=flat-square)](https://circleci.com/gh/ebridges/plaid2qif)

### Description

Provides a mechanism for downloading transactions from various financial institutions (as supported by [Plaid](https://www.plaid.com)), and converts to formats (specifically QIF & CSV) usaable by financial software (especially GNUCash).

### Summary

```
  plaid2qif save-access-token --institution=<name> --public-token=<token> [--verbose]
  plaid2qif list-accounts --institution=<name> [--verbose]
  plaid2qif download --from=<from-date> --to=<to-date> --institution=<name> --account=<name> --account-type=<type> --account-id=<id> 
```

### Usage

After cloning this repo, change to the root directory.  Add your own personal credentials for Plaid to `./plaid-credentials.json`.

1. Install the `plaid2qif` command (preferably using a virtualenv)

```
$ mkvirtualenv --python=python3 plaid2qif
$ python setup.py install
```

2. Open a web server on the root directory and open `auth.html`

```
$ python -m SimpleHTTPServer 8000
$ open auth.html
```

3. Follow [instructions here](https://plaid.com/docs/quickstart/#creating-items-with-link-and-the-api) to use the UI to link your financial institution to Plaid.

4. Once you've succesfully linked, look in the browser's console (e.g. on Chrome use `⌘-⌥-i`) and copy the `public_token`.  The `public_token` is a short lived credential.

5. Using the `public_token`, generate and save a long-lived `access_token` credential:

```
$ plaid2qif save-access-token --institution=<name> --public-token=<token>
```

  * `institution` should be a string that can be used as a valid (i.e.: `[a-zA-Z0-9_]`) filename, used to store the `access_token`.

6. List the accounts connected with this institution in order to get Plaid's `account_id`:

```
$ plaid2qif list-accounts --institution=<name>
```

7. Once you've gotten that info configured, you're ready to download transactions and save them as QIF files:

```
plaid2qif download \
    --from=<yyyy-mm-dd> \
    --to=<yyyy-mm-dd> \
    --institution=<name> \
    --account-type=<type> \
    --account=<account-name> \
    --account-id=<plaid-account-id>
```

  * `account` is the path to an account in the ledger in GnuCash that you ultimately want to import the transactions to.  This is added to the `!Account` header in the QIF file.  e.g.: `Assets: Checking Accounts:Personal Checking Account`.  If the name has spaces be sure to quote this param.
  * `account-type` is an account identifier type as [documented here](https://github.com/Gnucash/gnucash/blob/master/src/import-export/qif-imp/file-format.txt#L23).
  * `account-id` is Plaid's account ID for the account you want to download, as obtained via `list-accounts` above.
  * By default, output will go to stdout to be redirected.  If you want it to be written to a location use the `output-dir` parameter.

[![GitHub watchers](https://img.shields.io/github/watchers/badges/shields.svg?style=social&label=Watch&style=flat-square)]()
[![Crates.io](https://img.shields.io/crates/l/rustc-serialize.svg?style=flat-square)]()
