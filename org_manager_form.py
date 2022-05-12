from asciimatics.widgets import (
    Button,
    Divider,
    Frame,
    Layout,
    RadioButtons,
    Text,
)
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import (
    ResizeScreenError,
    StopApplication,
)

# from asciimatics.parsers import AsciimaticsParser

import json
import os
import sys
import logging
import threading

import console_mode as console_mode
from sf_org_manager import sfdx_cli_utils as sfdx


logging.basicConfig(filename="org_manager_form.log", level=logging.WARN)


# Config
#
TGREEN = "\033[1;32m"
TRED = "\033[1;31m"
ENDC = "\033[m"
#
#


def clean_org_data(org):
    if "alias" not in org:
        a = {"alias": ""}
        org.update(a)

    if "isDevHub" not in org:
        dh = {"isDevHub": False}
        org.update(dh)

    if "defaultMarker" not in org:
        dm = {"defaultMarker": ""}
        org.update(dm)

    if "status" not in org:
        s = {"status": "Active"}
        org.update(s)

    if "expirationDate" not in org:
        dt = {"expirationDate": ""}
        org.update(dt)

    return org


def update_org_list():
    org_list = sfdx.org_list()

    if org_list["status"] == 1:
        message = org_list["message"]
        logging.error(f"MESSAGE: {message}")
        logging.warning(f"{org_list}")
        sys.exit(1)

    json.dump(org_list, open("org_list.json", "w"))

    return org_list


def get_org_list():
    if os.path.isfile("org_list.json"):
        org_list = json.load(open("org_list.json", "r"))
        t = threading.Thread(target=update_org_list)
        t.start()

    else:
        org_list = update_org_list()

    return org_list


def get_orgs_map(org_list):

    try:
        non_scratch_orgs = org_list["result"]["nonScratchOrgs"]
    except KeyError:
        pass

    try:
        non_scratch_orgs = org_list["result"]["salesforceOrgs"]
    except KeyError:
        pass

    try:
        scratch_orgs = org_list["result"]["scratchOrgs"]
    except KeyError:
        pass

    orgs = {}
    defaultusername = 1
    index = 1

    for o in non_scratch_orgs:
        org = {index: clean_org_data(o)}
        orgs.update(org)
        index = index + 1

    for o in scratch_orgs:
        clean_org = clean_org_data(o)

        if clean_org["defaultMarker"] == "(U)":
            defaultusername = index

        org = {index: clean_org}
        orgs.update(org)
        index = index + 1

    return orgs, defaultusername


def get_org_options(orgs):
    options = []

    for idx, o in orgs.items():
        color = TGREEN
        if o["status"] != "Active":
            color = TRED

        options.append(
            (
                f'{o["alias"]:<30} {o["username"]:<45} {o["expirationDate"]:<12} {color}{o["status"]:<10}{ENDC}',
                idx,
            )
        )

    return options


class org_list_frame(Frame):

    cmd_string = ""

    def __init__(self, screen):
        super(org_list_frame, self).__init__(
            screen,
            int(screen.height),
            int(screen.width),
            data=form_data,
            has_shadow=False,
            name="Org List",
            has_border=False,
            hover_focus=False,
        )

        layout = Layout([1, 18, 1])
        self.add_layout(layout)

        layout.add_widget(
            RadioButtons(
                options=org_options,
                label="Orgs List",
                name="radio",
                on_change=self._on_change,
            ),
            1,
        )

        layout.add_widget(Divider(height=3), 1)

        layout.add_widget(Text(label="Org Id", name="org_id", readonly=True), 1)
        layout.add_widget(Text(label="Username", name="username", readonly=True), 1)
        layout.add_widget(Text(label="Url", name="url", readonly=True), 1)
        layout.add_widget(
            Text(label="Access Token", name="access_token", readonly=True), 1
        )

        layout.add_widget(Divider(height=3), 1)

        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)

        layout2.add_widget(Button("Login", self.sf_login, name="login"), 0)
        layout2.add_widget(Button("(Q)uit", self._quit, name="quit"), 2)

        # self.set_theme("default")
        self.set_theme("bright")

        self.fix()

    def _on_change(self):
        self.save()

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code >= 0 and event.key_code <= 255:
                self.cmd_string = self.cmd_string + chr(event.key_code)
                # print(f"{self.cmd_string}")

            if event.key_code in [ord("q"), ord("Q"), Screen.ctrl("c")]:
                self.cmd_string = ""
                console_mode.quickedit(1)
                raise StopApplication("User quit")

            elif self.cmd_string.lower() == "login":
                self.cmd_string = ""
                self.sf_login()

            elif event.key_code in (ord("\n"), ord("\r")):
                self.cmd_string = ""
                if self.focussed_widget.name == "radio":
                    self.get_org_details()

        elif isinstance(event, MouseEvent):
            # MouseEvent !!!
            print("MouseEvent")

        return super(org_list_frame, self).process_event(event)

    def get_org_details(self):
        radio = self.find_widget("radio")
        org_id = self.find_widget("org_id")
        username = self.find_widget("username")
        url = self.find_widget("url")
        access_token = self.find_widget("access_token")

        org = orgs.get(radio.value)
        usr_detail = sfdx.user_details(org["username"])

        org_id.value = f"{usr_detail['result']['orgId']}"
        username.value = f"{usr_detail['result']['username']}"
        url.value = f"{usr_detail['result']['instanceUrl']}"
        access_token.value = f"{usr_detail['result']['accessToken']}"

    def sf_login(self):
        radio = self.find_widget("radio")
        org = orgs.get(radio.value)
        sfdx.org_open(org["username"])

        console_mode.quickedit(1)
        raise StopApplication("User requested exit")

    def _quit(self):
        console_mode.quickedit(1)
        raise StopApplication("User requested exit")


def main(screen, scene):
    screen.clear()

    screen.play(
        [Scene([org_list_frame(screen)], -1)],
        stop_on_resize=True,
        start_scene=scene,
        allow_int=True,
    )


if __name__ == "__main__":

    console_mode.quickedit(0)

    org_list = get_org_list()
    orgs, defaultusername = get_orgs_map(org_list)
    org_options = get_org_options(orgs)
    form_data = {"radio": org_options}
    last_scene = None

    while True:
        try:
            Screen.wrapper(main, catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
