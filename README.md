# sfdx_scratch_org_builder

![CI](https://github.com/MervmessInc/sfdx-scratch-org-builder/actions/workflows/python-app.yml/badge.svg)

## Package Install

### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs the package in an isolated environment and makes the CLI commands globally available.

Install from a local clone:

```bash
pipx install .
```

To upgrade:

```bash
pipx upgrade sf-org-manager
```

To uninstall:

```bash
pipx uninstall sf-org-manager
```

### Building & Installing a Wheel

You can build a `.whl` file and distribute it without needing access to the Git repository.

#### 1. Build the wheel

Make sure the `build` package is installed, then run:

```bash
pip install build
python -m build --wheel
```

This creates a `.whl` file in the `dist/` directory, e.g. `dist/sf_org_manager-0.1.0-py3-none-any.whl`.

#### 2. Install the wheel with pipx

```bash
pipx install dist/sf_org_manager-0.1.0-py3-none-any.whl
```

or with clipboard support:

```bash
pipx install "dist/sf_org_manager-0.1.0-py3-none-any.whl[clipboard]"
```

To reinstall or upgrade from a newer wheel:

```bash
pipx install --force dist/sf_org_manager-0.1.0-py3-none-any.whl
```

Or with clipboard support:

```bash
pipx install --force "dist/sf_org_manager-0.1.0-py3-none-any.whl[clipboard]"
```

### Local Development

To run from a local clone without a global install, activate the virtual environment and install in editable mode — changes to source are reflected immediately:

```bash
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev]"
```

The console commands then work normally:

```bash
sf-orgs
sf-org_builder --help
```

Or, if you want to skip the install step entirely, invoke via the module flag:

```bash
# No install needed — useful for a quick one-off test
python -m sf_org_manager.org_manager
python -m sf_org_manager.org_builder --alias my-scratch-org
```

## sf-orgs

org_manager.py is a Salesforce CLI helper script that lists Salesforce orgs and optionally opens one in the browser.

### Usage

```
$ sf-orgs -h
usage: org_manager [-h] [--debug]

Python wrapper for Salesforce CLI (sf) that lists Salesforce orgs.

options:
  -h, --help  show this help message and exit
  --debug     Turn on debug messages
```

```
$ sf-orgs

idx     Alias                          Username                                      Expiration   Status
---     -----                          --------                                      ----------   ------
  1                                    user@brave-goat-76637.com                                  Active
  2                                    user@2gp.testing.net                                       Active
  3     2gp-hub-org                    2pack@2gp.testing.net                                      Active
  4     CCIDevHub                      user@resilient-fox-q2einl.com                              Active
  5     LWC_Workshop                   user@cunning-raccoon-jmz2bj.com                            Active
  6 (D) hub-org                        user@dev-hub-org.com                                       Active
  7     trailhead20190807              user@cunning-bear-7p8yp6.com                               Active
  8                                    test-9lrsnqttbvfm@example.com                 2022-05-23   Active
  9     user-dev                       test-v4ykj3fbwdne@example.com                 2022-06-12   Active
 10 (U) user-dev_II                    test-inilbb6oaint@example.com                 2022-05-23   Active
 11     user-dev_III                   test-8qtkf4vjqxlj@example.com                 2022-05-23   Active

Enter choice 'idx' or 'U' >
```

(D) is the default dev-hub for the project
(U) is the default username (scratch org) for the project

## sf-org_builder

org_builder.py is a Salesforce CLI helper that builds a fresh scratch org or updates an existing one. It installs dependent packages, deploys source code, assigns permission sets and runs anonymous Apex scripts.

### Usage

```
$ sf-org_builder --help
usage: org_builder [-h] [-a ALIAS] [-d DURATION] [-v DEVHUB] [-e EMAIL] [--debug] [--skip]

Python wrapper for a number of Salesforce CLI (sf) commands, to build and setup Scratch Orgs.

options:
  -h, --help            show this help message and exit
  -a ALIAS, --alias ALIAS
                        Scratch Org user alias
  -d DURATION, --duration DURATION
                        Number of days org will last [1..30]. Default: 10
  -v DEVHUB, --devhub DEVHUB
                        Target dev hub username or alias. Default: my-dev-hub-org
  -e EMAIL, --email EMAIL
                        Email address that will be applied to the org's admin user
  --debug               Turn on debug messages
  --skip                Skip source deploy
```

### Config

Copy `org_config.yml.example` to `org_config.yml` in your project directory and customise it.
`org_config.yml` is gitignored so your personal settings won't be committed.

```bash
cp org_config.yml.example org_config.yml   # macOS / Linux
copy org_config.yml.example org_config.yml  # Windows
```

Key fields:

| Field            | Description                                       |
| ---------------- | ------------------------------------------------- |
| `SCRATCH_DEF`    | Path to your scratch org definition JSON file     |
| `DURATION`       | Org lifetime in days (1–30)                       |
| `DEVHUB`         | Your dev hub alias or username                    |
| `USE_NAMESPACE`  | `True` if your project uses a namespace           |
| `PACKAGE_IDS`    | Managed package version IDs to install            |
| `PACKAGE_P_SETS` | Permission sets from installed packages to assign |
| `PRE_DEPLOY`     | Source folders to deploy before the main push     |
| `SRC_FOLDERS`    | Main source folders to deploy                     |
| `P_SETS`         | Permission sets to assign after deploy            |
| `BUILD_DATA_CMD` | Anonymous Apex files to execute                   |
| `POST_DEPLOY`    | Source folders to deploy after the main push      |
| `TMPLT_NAME`     | Experience Cloud template name (optional)         |
| `SITE_NAME`      | Experience Cloud site name to publish (optional)  |

## Project dependencies

- Salesforce CLI (`sf`) — [Installation guide](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_setup_install_cli.htm)
- Python >= 3.10 — <https://www.python.org/downloads/>
