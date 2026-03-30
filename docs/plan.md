# sf-org-manager — Refresh & pipx Packaging Plan

**Goal:** Bring the project up to modern Python packaging standards so it installs cleanly via `pipx install git+https://github.com/MervmessInc/sfdx-scratch-org-builder.git` and works reliably from any working directory.

---

## Current State (scan: 2026-03-30)

The project has a functioning `sf_org_manager` package with two CLI entry points (`sf-orgs`, `sf-org_builder`) wired up in `pyproject.toml`. However, there are several issues preventing a reliable `pipx` install.

### Issues Identified

#### 🔴 Critical — blocks `pipx install`

| # | File | Issue |
|---|---|---|
| C1 | `pyproject.toml` | Line 1 starts with `.v[build-system]` (stray characters) — parse error at install time |
| C2 | `setup.cfg` + `setup.py` | Redundant legacy files conflict with modern `pyproject.toml`; `setup.cfg` uses a different package name (`sf_org_manager` vs `sf-org-manager`) |
| C3 | `org_manager.py` | `org_list.json` cache written to CWD — breaks when invoked from arbitrary directories post `pipx` install |

#### 🟡 Important — quality & reliability

| # | File | Issue |
|---|---|---|
| Q1 | All modules | Version string duplicated in `__init__.py`, `org_manager.py`, `org_builder.py`, `sfdx_cli_utils.py`, and `pyproject.toml` — should be single-sourced |
| Q2 | `org_manager.py`, `org_builder.py` | `logging.basicConfig()` called at module import time — should only be called inside `main()` |
| Q3 | `org_builder.py` | `logging.error()` used throughout for normal status messages — should use `logging.info()` or `print()` |
| Q4 | `org_manager.py` | `get_orgs_map()` uses bare `except KeyError: pass` in consecutive try/except blocks — `scratch_orgs` can be unbound if both fail |
| Q5 | `sfdx_cli_utils.py` | `force:community:create` and `force:community:publish` are legacy `sfdx` namespaced commands; modern equivalents are `sf community create` / `sf community publish` |
| Q6 | `sfdx_cli_utils.py` | `parse_output()` strips content before `{` with `str.index("{")` — fragile; `sf --json` always returns clean JSON |

#### 🟢 Cleanup — housekeeping

| # | File | Issue |
|---|---|---|
| H1 | `sf-orgs_app.py`, `sf-org_builder.py` | Legacy root-level entry scripts superseded by `[project.scripts]` in `pyproject.toml` |
| H2 | `console_mode.py` | Windows-only utility to toggle console QuickEdit mode (prevents hangs over RDP). Not wired up as a CLI command. Should be folded into `sfdx_cli_utils.py` and called automatically on Windows in `main()`, or removed. |
| H3 | `sf_org_manager.egg-info/` | Build artefact checked into repo — add to `.gitignore` |
| H4 | `org_list.json` | Runtime cache file checked into repo — add to `.gitignore` |
| H5 | `org_config.yml` | Decide: personal config (gitignore) or user template (rename to `org_config.yml.example`) |
| H6 | `.github/workflows/python-app.yml` | Uses `actions/checkout@v3`, `actions/setup-python@v3` — update to `@v4`; pytest step is commented out |
| H7 | `pyproject.toml` | `requires-python = ">=3.8"` but Python 3.8 is EOL (Oct 2024); bump to `>=3.10` |
| H8 | `pyproject.toml` | Classifier list missing Python 3.13 |
| H9 | `requirements.txt` | Pinned to `pyyaml==6.0` (pip-compiled against Python 3.10 in 2022) — regenerate |

---

## Proposed Changes

### Phase 1 — Fix Packaging (unblock `pipx install`)

**Files changed:**

- **`pyproject.toml`** — fix line 1 corruption; bump `requires-python` to `>=3.10`; add `platformdirs>=3.0` to dependencies; update Python classifier list; remove duplicate version fields
- **`setup.cfg`** — **DELETE** (superseded by `pyproject.toml`)
- **`setup.py`** — **DELETE** (superseded by `pyproject.toml`)
- **`sf-orgs_app.py`** — **DELETE** (legacy entry script)
- **`sf-org_builder.py`** — **DELETE** (legacy entry script)
- **`sf_org_manager/__init__.py`** — remove hardcoded `__version__`; expose version via `importlib.metadata`
- **`requirements.in`** — add `platformdirs`
- **`requirements.txt`** — regenerate with `pip-compile` against Python 3.10+
- **`.gitignore`** — add `*.egg-info/`, `org_list.json`

### Phase 2 — Fix Runtime Issues

**Files changed:**

- **`sf_org_manager/org_manager.py`**
  - Remove hardcoded `__version__`
  - Move `logging.basicConfig()` into `main()`
  - Fix `get_orgs_map()` bare `except KeyError: pass` — initialise `scratch_orgs` / `non_scratch_orgs` to `[]` before try blocks
  - Move `org_list.json` cache to a platform-appropriate user data dir (`platformdirs.user_cache_dir("sf-org-manager")`)
  - Fold in `console_mode.py` QuickEdit disable call for Windows in `main()` (prevents hang-on-input over RDP)

- **`sf_org_manager/org_builder.py`**
  - Remove hardcoded `__version__`
  - Move `logging.basicConfig()` into `main()`
  - Replace all `logging.error("~~~ ... ~~~")` status banners with `logging.info()` or `print()`
  - Update `force:community:*` → `sf community` modern commands (via `sfdx_cli_utils.py`)

- **`sf_org_manager/sfdx_cli_utils.py`**
  - Remove hardcoded `__version__`
  - Harden `parse_output()` — remove fragile `str.index("{")` strip; trust `sf --json` output directly
  - Update `create_community()` command to `sf community create`
  - Update `publish_community()` command to `sf community publish`

- **`console_mode.py`** — **DELETE** (logic absorbed into `org_manager.py`)

### Phase 3 — Add Tests & Fix CI

- **`tests/__init__.py`** — **NEW** (empty, makes `tests/` a package)
- **`tests/test_sfdx_cli_utils.py`** — **NEW** — unit tests for `parse_output()` with mocked subprocess output
- **`tests/test_org_manager.py`** — **NEW** — unit tests for `clean_org_data()`, `get_orgs_map()`
- **`.github/workflows/python-app.yml`** — update action versions to `@v4`; enable pytest; install `.[dev]` extras; add `ruff` linter

### Phase 4 — Verify `pipx` Install

Manual verification steps:
```bash
# Build check
python -m build --wheel .

# Local pipx install
pipx install .

# Smoke tests
sf-orgs --help
sf-org_builder --help

# Uninstall
pipx uninstall sf-org-manager
```

---

## Dependency Changes

| Package | Before | After | Reason |
|---|---|---|---|
| `pyyaml` | `==6.0` | `>=6.0` | Loosen pin for compatibility |
| `platformdirs` | *(not present)* | `>=3.0` | Platform-aware user cache/config dirs |

**Dev dependencies** (added as `[project.optional-dependencies]` `dev` group):
- `pytest>=7.0`
- `ruff` (replaces `flake8`)

---

## Open Questions

> These should be answered before Phase 2 begins.

1. **`org_config.yml`** — Is this your personal config (gitignore it) or a template for end users (rename to `org_config.yml.example` and commit)?
2. **Community commands** — Do you actively use `TMPLT_NAME` / `SITE_NAME` / Experience Cloud features? If not, those code paths can be marked as untested/deprecated for now.
3. **`org_config.yml` discovery** — Should `sf-org_builder` always look for `org_config.yml` in the current working directory (project-local tool behaviour is fine), or should it walk up the directory tree like `git` does?
4. **Minimum Python** — Confirmed bump to `>=3.10`?

---

## Out of Scope (this iteration)

- No new features — this is a maintenance and packaging refresh only
- The Salesforce CLI Dashboard (`textual` TUI) built in previous sessions is a **separate project** and is not part of this package
- No PyPI publish — `pipx install git+...` is the target install method
