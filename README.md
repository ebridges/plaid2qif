[![CircleCI](https://circleci.com/gh/ebridges/plaid2qif/tree/master.svg?style=svg)](https://circleci.com/gh/ebridges/plaid2qif/tree/master)

### Description

Provides a mechanism for downloading transactions from various financial institutions (as supported by [Plaid](https://www.plaid.com)), and converts to formats (specifically QIF & CSV, but extensible) usable by financial software (especially GNUCash).

### Summary

```
  # Save a long-lived access token (one-time only)
  plaid2qif save-access-token --institution=<name> --public-token=<token> --credentials=<file> [--verbose]

  # List out accunts that have been linked to Plaid
  plaid2qif list-accounts --institution=<name> --credentials=<file> [--verbose]

  # Download transactions in various formats (default QIF) from Plaid
  plaid2qif download \
    --institution=<name> \
    --account=<account-name> \
    --account-type=<type> \
    --account-id=<acct-id> \
    --from=<from-date> \
    --to=<to-date> \
    --credentials=<file> \
    [--output-format=<format>] \
    [--output-dir=<path>] \
    [--ignore-pending] \
    [--suppress-warnings=<tf>] \
    [--verbose]
```

### Usage

1. Install the `plaid2qif` command using `pip`

```
$ pip install plaid2qif
```

2. Authenticate and link with your financial institution (first time only) -- see "Authentication Prerequisites" below.

3. Once you've gotten that configured, you're ready to download transactions and save them as QIF files:

```
plaid2qif download \
    --from=<yyyy-mm-dd> \
    --to=<yyyy-mm-dd> \
    --institution=<name> \
    --account-type=<type> \
    --account=<account-name> \
    --account-id=<plaid-account-id> \
    --credentials=<file>
```

  * `account` is the path to an account in the ledger in GnuCash that you ultimately want to import the transactions to.  This is added to the `!Account` header in the QIF file.  e.g.: `Assets: Checking Accounts:Personal Checking Account`.  If the name has spaces be sure to quote this param.
  * `account-type` is an account identifier type as [documented here](https://github.com/Gnucash/gnucash/blob/cdb764fec525642bbe85dd5a0a49ec967c55f089/gnucash/import-export/qif-imp/file-format.txt#L23).
  * `account-id` is Plaid's account ID for the account you want to download, as obtained via `list-accounts` above.
  * By default, output will go to stdout to be redirected.  If you want it to be written to a location use the `output-dir` parameter.

### Authentication Prerequisites

* Obtain and save your own personal credentials for Plaid to a local file, e.g. `./plaid-credentials.json`. This JSON file should contain values for the following keys:
```
    {
      "client_id" : "<censored>",
      "public_key" : "<censored>",
      "secret" : "<censored>"
    }
```
* Create a `./cfg` directory for institution configuration data to be stored in.
* Authenticate with your Financial Institution.

#### Steps to Authenticate with your Financial Institution

1. Save this HTML locally, e.g. as `auth.html`

```
<html>
<body>
<button id='linkButton'>Open Link - Institution Select</button>
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<script>
  var linkHandler = Plaid.create({
    env: 'development',
    clientName: 'Plaid2QIF',
    key: '[PUBLIC_KEY]', // Replace with your public_key from plaid-credentials.json
    product: 'auth',
    apiVersion: 'v2',
    onLoad: function() {
      // The Link module finished loading.
    },
    onSuccess: function(public_token, metadata) {
      // Send the public_token to your app server here.
      // The metadata object contains info about the institution the
      // user selected and the account ID, if selectAccount is enabled.
      console.log('public_token: '+public_token+', metadata: '+JSON.stringify(metadata));
    },
    onExit: function(err, metadata) {
      // The user exited the Link flow.
      if (err != null) {
        // The user encountered a Plaid API error prior to exiting.
      }
      // metadata contains information about the institution
      // that the user selected and the most recent API request IDs.
      // Storing this information can be helpful for support.
    }
  });

  // Trigger the standard institution select view
  document.getElementById('linkButton').onclick = function() {
    linkHandler.open();
  };
</script>
</body>
</html>
```

2. Open a web server on the root directory and open `auth.html`

```
$ python3 -m http.server
$ open auth.html # edit first to add the public token from plaid-credentials.json
```

3. Follow [instructions here](https://plaid.com/docs/quickstart/#creating-items-with-link-and-the-api) to use the UI to link your financial institution to Plaid.

4. Once you've succesfully linked, look in the browser's console (e.g. on Chrome use `⌘-⌥-i`) and copy the `public_token`.  The `public_token` is a short lived credential.

5. Using the `public_token`, generate and save a long-lived `access_token` credential:

```
$ plaid2qif save-access-token --institution=<name> --public-token=<token> --credentials=<plaid-credentials-file>
```

  * `institution` should be a string that can be used as a valid (i.e.: `[a-zA-Z0-9_]`) filename, used to store the `access_token`.

6. List the accounts connected with this institution in order to get Plaid's `account_id`:

```
$ plaid2qif list-accounts --institution=<name> --credentials=<plaid-credentials-file>
```

### Distribution

```
# increment version in `plaid2qif/__init__.py`
# commit everything & push
$ git tag -s vX.Y.Z
$ git push --tags
$ python3 setup.py sdist bdist_wheel
$ twine upload dist/*
```

[![GitHub watchers](https://img.shields.io/github/watchers/badges/shields.svg?style=social&label=Watch&style=flat-square)]()
[![Crates.io](https://img.shields.io/crates/l/rustc-serialize.svg?style=flat-square)]()
[![PyPi](https://img.shields.io/pypi/v/plaid2qif.svg?style=flat-square)]()
