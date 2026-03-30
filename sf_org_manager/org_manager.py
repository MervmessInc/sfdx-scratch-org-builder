# org_manager.py

import argparse
import json
import logging
import sys
import threading
import traceback
from pathlib import Path

import platformdirs
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import sfdx_cli_utils as sfdx

# ---------------------------------------------------------------------------
# Optional clipboard support
# ---------------------------------------------------------------------------
try:
    import pyperclip  # type: ignore[import-untyped]

    _CLIPBOARD_AVAILABLE = True
except ImportError:
    _CLIPBOARD_AVAILABLE = False

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_CACHE_DIR = Path(platformdirs.user_cache_dir("sf-org-manager"))
_ORG_LIST_CACHE = _CACHE_DIR / "org_list.json"

console = Console()


def _ensure_cache_dir():
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Org list helpers
# ---------------------------------------------------------------------------

def get_org_list():
    """Return the org list, serving from cache when available.

    Returns:
        tuple[dict, bool]: (org_list_dict, served_from_cache)
    """
    if _ORG_LIST_CACHE.is_file():
        with open(_ORG_LIST_CACHE, "r") as jsonfile:
            org_list = json.load(jsonfile)
        # Refresh in the background so the next invocation is faster
        t = threading.Thread(target=update_org_list, daemon=True)
        t.start()
        return org_list, True
    else:
        org_list = update_org_list()
        return org_list, False


def update_org_list():
    _ensure_cache_dir()
    org_list = sfdx.org_list()
    with open(_ORG_LIST_CACHE, "w") as jsonfile:
        json.dump(org_list, jsonfile)
    return org_list


def clean_org_data(org):
    org.setdefault("alias", "")
    org.setdefault("isDevHub", False)
    org.setdefault("defaultMarker", "")
    org.setdefault("status", "Active")
    org.setdefault("expirationDate", "")
    return org


def get_orgs_map(orgs):
    """Build an index-keyed map of all orgs, split by type.

    Returns:
        tuple[dict, list[int], list[int], int]:
            orgs_map, non_scratch_indices, scratch_indices, default_idx
    """
    result = orgs.get("result", {})
    non_scratch_orgs = result.get("nonScratchOrgs") or result.get("salesforceOrgs") or []
    scratch_orgs = result.get("scratchOrgs") or []

    orgs_map: dict[int, dict] = {}
    non_scratch_indices: list[int] = []
    scratch_indices: list[int] = []
    defaultusername = 1
    index = 1

    for o in non_scratch_orgs:
        clean = clean_org_data(o)
        if clean["defaultMarker"] == "(U)":
            defaultusername = index
        orgs_map[index] = clean
        non_scratch_indices.append(index)
        index += 1

    for o in scratch_orgs:
        clean = clean_org_data(o)
        if clean["defaultMarker"] == "(U)":
            defaultusername = index
        orgs_map[index] = clean
        scratch_indices.append(index)
        index += 1

    return orgs_map, non_scratch_indices, scratch_indices, defaultusername


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _status_text(status: str) -> Text:
    """Return a coloured Rich Text cell for the org status."""
    if status == "Active":
        return Text(status, style="bold green")
    elif status == "Expired":
        return Text(status, style="bold red")
    else:
        return Text(status, style="yellow")


def _alias_text(org: dict) -> Text:
    """Return alias with an optional DevHub badge."""
    alias = org.get("alias") or ""
    if org.get("isDevHub"):
        t = Text()
        t.append(alias, style="cyan")
        t.append(" [DH]", style="bold magenta")
        return t
    return Text(alias, style="cyan")


def _default_text(marker: str) -> Text:
    if marker == "(U)":
        return Text("●", style="bold yellow")
    return Text("")


def _build_section(table: Table, indices: list[int], orgs_map: dict[int, dict]):
    """Add rows for a set of org indices into *table*."""
    active_count = 0
    expired_count = 0
    for idx in indices:
        o = orgs_map[idx]
        status = o.get("status", "Active")
        if status == "Active":
            active_count += 1
        else:
            expired_count += 1
        table.add_row(
            str(idx),
            _default_text(o["defaultMarker"]),
            _alias_text(o),
            Text(o["username"]),
            Text(o.get("expirationDate", "") or ""),
            _status_text(status),
        )
    return active_count, expired_count


def print_org_list(orgs_map: dict, non_scratch_indices: list[int], scratch_indices: list[int]):
    """Render the full org list as two Rich table sections."""

    def _make_table(title: str) -> Table:
        t = Table(
            title=title,
            title_style="bold white",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold dim",
            expand=False,
            padding=(0, 1),
        )
        t.add_column("#", style="dim", width=4, justify="right")
        t.add_column("", width=2)                          # default marker
        t.add_column("Alias", min_width=20, max_width=32)
        t.add_column("Username", min_width=30, max_width=48)
        t.add_column("Expires", width=12)
        t.add_column("Status", width=10)
        return t

    totals = {"active": 0, "expired": 0}

    if non_scratch_indices:
        ns_table = _make_table("Connected Orgs")
        a, e = _build_section(ns_table, non_scratch_indices, orgs_map)
        totals["active"] += a
        totals["expired"] += e
        console.print(ns_table)
        console.print()

    if scratch_indices:
        sc_table = _make_table("Scratch Orgs")
        a, e = _build_section(sc_table, scratch_indices, orgs_map)
        totals["active"] += a
        totals["expired"] += e
        console.print(sc_table)
        console.print()

    summary_parts = []
    if totals["active"]:
        summary_parts.append(f"[bold green]{totals['active']} active[/]")
    if totals["expired"]:
        summary_parts.append(f"[bold red]{totals['expired']} expired[/]")
    if summary_parts:
        console.print("  " + "  ·  ".join(summary_parts))
        console.print()


def show_org_list(orgs_map, non_scratch_indices, scratch_indices, from_cache: bool):
    """Display orgs and return the user's validated choice index."""
    if from_cache:
        console.print(
            "  [dim italic]Served from cache — refreshing in background[/]"
        )
        console.print()

    print_org_list(orgs_map, non_scratch_indices, scratch_indices)

    while True:
        try:
            raw = console.input(
                "[bold]Select org[/]  [dim]number / U = default / Q = quit[/]  [bold]>[/] "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            sys.exit(0)

        if not raw:
            continue

        if raw.upper() == "Q":
            sys.exit(0)

        if raw.upper() == "U":
            return _find_default(orgs_map)

        if raw.isnumeric():
            idx = int(raw)
            if idx in orgs_map:
                return idx
            console.print(f"  [red]No org at index {idx}. Try again.[/]")
        else:
            console.print("  [red]Invalid input. Enter a number, U, or Q.[/]")


def _find_default(orgs_map: dict) -> int:
    for idx, o in orgs_map.items():
        if o.get("defaultMarker") == "(U)":
            return idx
    # Fall back to first entry
    return next(iter(orgs_map))


# ---------------------------------------------------------------------------
# User details
# ---------------------------------------------------------------------------

def user_details(org_alias: str):
    """Fetch and display org details in a Rich panel."""
    py_obj = sfdx.user_details(org_alias)

    if py_obj["status"] == 1:
        logging.error(f"MESSAGE: {py_obj.get('message', 'Unknown error')}")
        sys.exit(1)

    r = py_obj["result"]
    login_url = f"{r['instanceUrl']}/secur/frontdoor.jsp?sid={r['accessToken']}"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold dim", justify="right")
    grid.add_column()
    grid.add_row("Org ID",   r.get("orgId", ""))
    grid.add_row("Username", r.get("username", ""))
    grid.add_row("Alias",    r.get("alias", ""))
    grid.add_row("URL",      Text(login_url, style="link " + login_url))
    grid.add_row("Token",    Text(r.get("accessToken", ""), style="dim"))

    console.print(
        Panel(grid, title=f"[bold cyan]{org_alias}[/]", border_style="cyan", expand=False)
    )
    console.print()

    return login_url


# ---------------------------------------------------------------------------
# Action menu
# ---------------------------------------------------------------------------

def action_menu(username: str, login_url: str):
    """Prompt the user to open the org, copy the login URL, or quit."""
    actions = []
    actions.append(("[O]", "Open in browser"))
    if _CLIPBOARD_AVAILABLE:
        actions.append(("[C]", "Copy login URL to clipboard"))
    actions.append(("[Q]", "Quit"))

    menu_text = "  ".join(f"[bold]{k}[/] {v}" for k, v in actions)
    console.print(menu_text)

    while True:
        try:
            raw = console.input(
                f"[bold]Action for[/] [cyan]{username}[/] [bold]>[/] "
            ).strip().upper() or "O"
        except (EOFError, KeyboardInterrupt):
            console.print()
            sys.exit(0)

        if raw in ("O", "OPEN"):
            logging.info(f"Opening org ({username})")
            with console.status("[bold green]Opening org in browser…[/]"):
                sfdx.org_open(username)
            return

        if raw in ("C", "COPY") and _CLIPBOARD_AVAILABLE:
            pyperclip.copy(login_url)
            console.print("  [green]✓ Login URL copied to clipboard.[/]")
            return

        if raw in ("Q", "QUIT"):
            sys.exit(0)

        console.print("  [red]Unrecognised action. Try again.[/]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="sf-orgs",
        description="List authenticated Salesforce orgs and open them in a browser.",
    )
    parser.add_argument("--debug", help="Turn on debug messages", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.ERROR,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    logging.info(f"argv[0] ~ {sys.argv[0]}")

    try:
        with console.status("[bold green]Fetching org list…[/]", spinner="dots"):
            org_list, from_cache = get_org_list()

        orgs_map, non_scratch_indices, scratch_indices, _default = get_orgs_map(org_list)

        if not orgs_map:
            console.print("[yellow]No orgs found. Are you logged in with 'sf org login'?[/]")
            sys.exit(0)

        console.print()
        idx = show_org_list(orgs_map, non_scratch_indices, scratch_indices, from_cache)

        org = orgs_map[idx]
        username = org["alias"] if org["alias"] else org["username"]

        console.print()
        login_url = user_details(username)

        action_menu(username, login_url)

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
