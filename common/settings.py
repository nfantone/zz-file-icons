import json
import os
import re
import sublime

from .vendor import jsonutils
from .vendor import webcolors
from .utils.logging import log, dump, message

PACKAGE_BASE = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
PACKAGE_NAME = os.path.splitext(PACKAGE_BASE)[0]
PACKAGE_MAIN = "A File Icon"
PACKAGE_ARCH = PACKAGE_NAME + ".sublime-package"

PACKAGE_SETTINGS_FILE = "A File Icon.sublime-settings"
SUBLIME_SETTINGS_FILE = "Preferences.sublime-settings"
PKGCTRL_SETTINGS_FILE = "Package Control.sublime-settings"

OVERLAY_ROOT = "{0} {1} {0}".format("zzz", PACKAGE_NAME)

_current_settings = {}
_default_settings = {}
_pattern = re.compile(r"#([0-9a-fA-F]{3}){1,2}")
_uuid = "9ebcce78-4cac-4089-8bd7-d551c634b052"


def _get_default():
    s = json.loads(jsonutils.sanitize_json(sublime.load_resource(
        "Packages/{0}/.sublime/{1}"
        .format(PACKAGE_NAME, PACKAGE_SETTINGS_FILE)
    )))

    del s["dev_mode"]
    del s["dev_trace"]

    return s


def _merge(*settings):
    result = {}
    for dictionary in settings:
        result.update(dictionary)
    return result


def _get_colors():
    colors = {}
    package_settings = package()
    color_options = [
        o for o in _default_settings if o.startswith("color")
    ]

    if package_settings.get("color"):
        for opt in color_options:
            color = package_settings.get(opt)

            if re.match(_pattern, color):
                rgb_color = webcolors.hex_to_rgb(color)

                color = ", ".join(str(e) for e in rgb_color)
                colors[opt] = "[" + color + "]"
            else:
                colors[opt] = ""

    return colors


def _on_aliases_change():
    log("Aliases settings changed")
    sublime.run_command("afi_check_aliases")


def _on_icons_change():
    log("Icons settings changed")
    sublime.run_command("afi_patch_themes", {"overwrite": True})


def _on_force_mode_change():
    log("Force mode settings changed")
    sublime.run_command("afi_patch_themes")


def _on_change():
    is_aliases_changed = False
    is_icons_changed = False
    is_force_mode_changed = False

    global _current_settings
    real_settings = {}

    if is_enabled():
        for s in _default_settings:
            real_settings[s] = package().get(s)

            if real_settings[s] != _current_settings[s]:
                if s.startswith("aliases"):
                    is_aliases_changed = True
                elif s.startswith("force_mode"):
                    is_force_mode_changed = True
                else:
                    is_icons_changed = True

        if is_aliases_changed:
            _on_aliases_change()

        if is_icons_changed:
            _on_icons_change()
        elif is_force_mode_changed:
            _on_force_mode_change()

        if is_aliases_changed or is_force_mode_changed or is_icons_changed:
            _current_settings = real_settings


def _update():
    global _current_settings

    for s in _default_settings:
        _current_settings[s] = package().get(s)


def subltxt():
    return sublime.load_settings(SUBLIME_SETTINGS_FILE)


def pkgctrl():
    return sublime.load_settings(PKGCTRL_SETTINGS_FILE)


def package():
    return sublime.load_settings(PACKAGE_SETTINGS_FILE)


def add_listener():
    package().add_on_change(_uuid, _on_change)


def clear_listener():
    package().clear_on_change(_uuid)


def is_enabled():
    if PACKAGE_NAME in subltxt().get("ignored_packages", []):
        return False
    return True


def is_package_archive():
    if os.path.splitext(PACKAGE_BASE)[1] == ".sublime-package":
        return True
    return False


def icons():
    log("Getting settings of the icons")

    s = _get_colors()
    s["opacity"] = package().get("opacity")
    s["opacity_on_hover"] = package().get("opacity_on_hover")
    s["opacity_on_select"] = package().get("opacity_on_select")
    s["size"] = package().get("size")
    s["row_padding"] = package().get("row_padding")
    dump(s)

    return s


def sublinter():
    sublime_packages_path = sublime.packages_path()

    try:
        if not os.path.exists(os.path.join(
            sublime_packages_path, OVERLAY_ROOT
        )):
            log("Updating linter settings")

            icons = json.loads(sublime.load_resource("Packages/" +
                                                     PACKAGE_NAME +
                                                     "/common/icons.json"))
            aliases = {}

            sl_settings_file = "SublimeLinter.sublime-settings"

            sl_default_resource_path = "Packages/SublimeLinter/{}".format(
                sl_settings_file
            )
            sl_default_settings_path = os.path.join(
                sublime_packages_path, "SublimeLinter", sl_settings_file
            )

            sl_user_resource_path = "Packages/User/{}".format(sl_settings_file)
            sl_user_settings_path = os.path.join(
                sublime_packages_path, "User", sl_settings_file
            )

            sl_input_settings = {}
            sl_output_settings = {"user": {}}

            if os.path.exists(sl_user_settings_path):
                sl_input_settings = json.loads(jsonutils.sanitize_json(
                    sublime.load_resource(sl_user_resource_path)))["user"]
            elif os.path.exists(sl_default_settings_path):
                sl_input_settings = json.loads(jsonutils.sanitize_json(
                    sublime.load_resource(
                        sl_default_resource_path
                    )))["default"]

            if sl_input_settings:
                for i in icons:
                    if "aliases" in icons[i]:
                        for a in icons[i]["aliases"]:
                            if "linter" in a:
                                aliases[a["name"].lower()] = a["linter"]

                new_syntax_map = _merge(
                    aliases, sl_input_settings["syntax_map"]
                )

                sl_input_settings["syntax_map"] = new_syntax_map

                sl_output_settings["user"] = sl_input_settings

                with open(sl_user_settings_path, "w") as f:
                    json.dump(sl_output_settings, f, sort_keys=True, indent=4)
                    f.close()

    except Exception as error:
        log("Error during saving linter settings")
        dump(error)


def init():
    log("Initializing settings")

    global _default_settings
    _default_settings = _get_default()

    _update()
