import json
import os
import re
import sublime
import sublime_plugin

from collections import OrderedDict

from ..common import settings
from ..common.templates.theme import INDENT
from ..common.templates.theme import TEMPLATE as THEME
from ..common.utils import path
from ..common.utils import icons
from ..common.utils.logging import log, dump, warning

PATTERN = re.compile(r"^Packages/|\/.*$")
COLOR = "{0}\"layer0.tint\": {1}{2}"
OPACITY = "{0}\"layer0.opacity\": {1}{2}"
SIZE = "{0}\"content_margin\": [{1}, {1}]{2}"
ROW_PADDING = "{0}\"row_padding\": {1}{2}"


def _patch_general(themes, dest, isettings):
    color = isettings.get("color", "[255, 255, 255]")
    color_on_hover = isettings.get("color_on_hover", "")
    color_on_select = isettings.get("color_on_select", "")
    opacity = isettings.get("opacity", "")
    opacity_on_hover = isettings.get("opacity_on_hover", "")
    opacity_on_select = isettings.get("opacity_on_select", "")
    size = isettings.get("size", "")
    row_padding = isettings.get("row_padding", "")

    for theme in themes:
        theme_dest = os.path.join(dest, theme)
        theme_name = os.path.splitext(theme)[0]
        log("Patching `{}`".format(theme))

        with open(theme_dest, "w") as t:
            t.write(THEME % {

                "color": COLOR.format(
                    ",\n" + INDENT, color, ""
                ) if color else "",

                "color_on_hover": COLOR.format(
                    ",\n" + INDENT, color_on_hover, ","
                ) if color_on_hover else ",",

                "color_on_select": COLOR.format(
                    ",\n" + INDENT, color_on_select, ","
                ) if color_on_select else ",",

                "opacity": OPACITY.format(
                    ",\n" + INDENT, opacity, ","
                ) if opacity else ",\n" + INDENT,

                "opacity_on_hover": OPACITY.format(
                    ",\n" + INDENT, opacity_on_hover, ""
                ) if opacity_on_hover else "",

                "opacity_on_select": OPACITY.format(
                    ",\n" + INDENT, opacity_on_select, ""
                ) if opacity_on_select else "",

                "size": SIZE.format(
                    "\n" + INDENT, size, ""
                ) if size else "",

                "row_padding": ROW_PADDING.format(
                    ",\n" + INDENT, row_padding, ""
                ) if row_padding else ""
            })


def _patch_specific(theme, dest, isettings):
    color = isettings.get("color", "")
    color_on_hover = isettings.get("color_on_hover", "")
    color_on_select = isettings.get("color_on_select", "")

    theme_dest = os.path.join(dest, theme)
    theme_name = os.path.splitext(theme)[0]
    log("Patching `{}`".format(theme))

    with open(theme_dest, "w") as t:
        t.write(THEME % {

            "color": COLOR.format(
                ",\n" + INDENT, color, ""
            ) if color else "",

            "color_on_hover": COLOR.format(
                ",\n" + INDENT, color_on_hover, ","
            ) if color_on_hover else ",",

            "color_on_select": COLOR.format(
                ",\n" + INDENT, color_on_select, ","
            ) if color_on_select else ",",

            "opacity": "",
            "opacity_on_hover": "",
            "opacity_on_select": "",
            "size": "",
            "row_padding": ""
        })


def _clean_patches(patches):
    log("Clearing old unnecessary patches")
    try:
        for patch in patches:
            try:
                os.remove(patch)
            except FileNotFoundError:
                pass
    except Exception as error:
        log("Error during patch cleaning")
        dump(error)


def get_current():
    log("Getting the current theme")

    current = settings.subltxt().get("theme")
    dump(current)

    return current


def get_installed(logging=True):
    if logging:
        log("Getting installed themes")

    theme_resources = sublime.find_resources("*.sublime-theme")
    all_themes_ordered = OrderedDict([])
    installed_themes = {}

    for res in theme_resources:
        package = re.sub(PATTERN, "", res)
        all_themes_ordered[package] = []

    for res in theme_resources:
        package = re.sub(PATTERN, "", res)
        theme = os.path.basename(res)

        all_themes_ordered[package].append(theme)

    for k in all_themes_ordered.keys():
        value = all_themes_ordered[k]
        is_addon = False
        is_patch = True if k == settings.OVERLAY_ROOT else False

        for v in installed_themes.values():
            if set(value).issubset(set(v)):
                is_addon = True

        if not (is_addon or is_patch):
            installed_themes[k] = value

    if logging:
        dump(installed_themes)

    return installed_themes


def get_customizable(installed_themes):
    log("Getting the list of theme packages with customization support")

    customizable_themes = []

    theme_res = sublime.find_resources(".supports-a-file-icon-customization")

    for res in theme_res:
        pkg = re.sub(PATTERN, "", res)

        if pkg in installed_themes:
            customizable_themes.append(pkg)

    dump(customizable_themes)

    return customizable_themes


class AfiPatchThemesCommand(sublime_plugin.ApplicationCommand):
    def run(self, overwrite=False):
        log("Preparing to patch")

        installed_themes = get_installed()
        customizable_themes = get_customizable(installed_themes)
        icons_settings = settings.icons()
        force_mode = settings.package().get("force_mode")

        general_to_patch = []
        patches_to_clean = []

        general = path.get_overlay_patches_general()
        specific = path.get_overlay_patches_specific()

        dest_new = "multi"
        dest_old = "single"

        if "color" in icons_settings and icons_settings["color"]:
            dest_new = "single"
            dest_old = "multi"

        general_dest = os.path.join(general, dest_new)

        for pkg in installed_themes:
            is_customizable = pkg in customizable_themes
            missing_icons = []

            if is_customizable:
                missing_icons = icons.get_missing(pkg)

            for theme in installed_themes[pkg]:
                general_old = os.path.join(general, dest_old, theme)
                general_new = os.path.join(general, dest_new, theme)
                specific_old = os.path.join(specific, pkg, dest_old, theme)
                specific_new = os.path.join(specific, pkg, dest_new, theme)
                specific_dest = os.path.join(specific, pkg, dest_new)

                if is_customizable and not force_mode:
                    if os.path.exists(general_old):
                        patches_to_clean.append(general_old)

                    if os.path.exists(general_new):
                        patches_to_clean.append(general_new)

                    if missing_icons:
                        if not os.path.exists(specific_new) or overwrite:
                            try:
                                _patch_specific(
                                    theme, specific_dest, icons_settings
                                )
                            except Exception as error:
                                log("Error during patching")
                                dump(error)

                        if os.path.exists(specific_old):
                            patches_to_clean.append(specific_old)
                else:
                    if not os.path.exists(general_new) or overwrite:
                        general_to_patch.append(theme)

                    if os.path.exists(general_old):
                        patches_to_clean.append(general_old)

                    if os.path.exists(specific_old):
                        patches_to_clean.append(specific_old)

                    if os.path.exists(specific_new):
                        patches_to_clean.append(specific_new)

        _clean_patches(patches_to_clean)

        if general_to_patch:
            try:
                _patch_general(general_to_patch, general_dest, icons_settings)
                log("Patching finished successfully")
            except Exception as error:
                log("Error during patching")
                dump(error)
            else:
                sublime.run_command("refresh_folder_list")
                warning()
        else:
            log("All the themes are already patched")

        settings.add_listener()
