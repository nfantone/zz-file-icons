import colorsys
import os
import re
import sublime

from .vendor import webcolors
from .utils.logging import log, dump, message

PACKAGE_BASE = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
PACKAGE_NAME = os.path.splitext(PACKAGE_BASE)[0]
PACKAGE_MAIN = "plugin"
PACKAGE_ARCH = PACKAGE_NAME + ".sublime-package"

PACKAGE_SETTINGS_FILE = "A File Icon.sublime-settings"
SUBLIME_SETTINGS_FILE = "Preferences.sublime-settings"
PKGCTRL_SETTINGS_FILE = "Package Control.sublime-settings"

OVERLAY_ROOT = "{0} {1} {0}".format("zzz", PACKAGE_NAME)

_current_settings = {}
_default_settings = {}
_hsl_pattern = re.compile(r'hsl\(\s*(\d+),\s*(\d+)%,\s*(\d+)%\s*\)')
_uuid = "9ebcce78-4cac-4089-8bd7-d551c634b052"


def _get_default():
    s = sublime.decode_value(sublime.load_resource(
        "Packages/{0}/.sublime/{1}"
        .format(PACKAGE_NAME, PACKAGE_SETTINGS_FILE)
    ))

    del s["dev_mode"]
    del s["dev_trace"]

    return s


def _merge(*settings):
    result = {}
    for dictionary in settings:
        result.update(dictionary)
    return result


def _parse_hsl_color(color):
    h, s, l = _hsl_pattern.match(color).groups()
    r, g, b = colorsys.hls_to_rgb(int(h) / 360, int(l) / 100, int(s) / 100)
    return [round(255 * r), round(255 * g), round(255 *b)]


def _get_colors(package_settings):
    colors = {}
    color_options = [
        o for o in _default_settings if o.startswith("color")
    ]

    if package_settings.get("color"):
        for opt in color_options:
            color = package_settings.get(opt)
            if isinstance(color, list):
                # color: [255, 255, 255]
                try:
                    colors[opt] = [int(color[0]), int(color[1]), int(color[2])]
                    continue
                except:
                    pass

            else:
                # color: hsl(360, 100%, 100%)
                try:
                    colors[opt] = _parse_hsl_color(color)
                    continue
                except:
                    pass

                # color: "white" or "#fff"
                try:
                    colors[opt] = webcolors.html5_parse_legacy_color(color)
                    continue
                except:
                    pass

            colors[opt] = []

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

    package_settings = package()

    if is_enabled():
        for s in _default_settings:
            real_settings[s] = package_settings.get(s)

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
    try:
        return subltxt.cache
    except AttributeError:
        subltxt.cache = sublime.load_settings(SUBLIME_SETTINGS_FILE)
        return subltxt.cache


def pkgctrl():
    try:
        return pkgctrl.cache
    except AttributeError:
        pkgctrl.cache = sublime.load_settings(PKGCTRL_SETTINGS_FILE)
        return pkgctrl.cache


def package():
    try:
        return package.cache
    except AttributeError:
        package.cache = sublime.load_settings(PACKAGE_SETTINGS_FILE)
        return package.cache


def add_listener():
    package().add_on_change(_uuid, _on_change)


def clear_listener():
    package().clear_on_change(_uuid)


def is_enabled():
    return PACKAGE_NAME not in subltxt().get("ignored_packages", [])


def is_package_archive():
    return PACKAGE_BASE.endswith(".sublime-package")


def icons():
    log("Getting settings of the icons")

    package_settings = package()

    s = _get_colors(package_settings)
    s["opacity"] = package_settings.get("opacity")
    s["opacity_on_hover"] = package_settings.get("opacity_on_hover")
    s["opacity_on_select"] = package_settings.get("opacity_on_select")
    s["size"] = package_settings.get("size")
    s["row_padding"] = package_settings.get("row_padding")
    dump(s)

    return s


def init():
    log("Initializing settings")

    global _default_settings
    _default_settings = _get_default()

    _update()
