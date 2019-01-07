import os
import re

import sublime
import sublime_plugin

from collections import OrderedDict

from ..common import settings
from ..common.utils import path
from ..common.utils import icons
from ..common.utils.logging import log, dump, warning

PATTERN = re.compile(r"^Packages/|\/.*$")


def _patch_icon(attrib, color=None, opacity=None):
    icon = {"class": "icon_file_type"}
    if attrib:
        icon["parents"] = [{"class": "tree_row", "attributes": [attrib]}]
    if color:
        icon["layer0.tint"] = color
    if opacity:
        icon["layer0.opacity"] = opacity
    return icon


def _patch_general(themes, dest, isettings):
    theme_content = []

    color = isettings.get("color")
    opacity = isettings.get("opacity")
    size = isettings.get("size")
    row_padding = isettings.get("row_padding")
    if color or opacity or size or row_padding:
        icon = _patch_icon(None, color, opacity)
        if size:
            icon["content_margin"] = [size, size]
        if row_padding:
            icon["row_padding"] = row_padding
        theme_content.append(icon)

    color = isettings.get("color_on_hover")
    opacity = isettings.get("opacity_on_hover")
    if color or opacity:
        theme_content.append(_patch_icon("hover", color, opacity))

    color = isettings.get("color_on_select")
    opacity = isettings.get("opacity_on_select")
    if color or opacity:
        theme_content.append(_patch_icon("selected", color, opacity))

    text = sublime.encode_value(theme_content)

    for theme in themes:
        log("Patching `{}`".format(theme))
        with open(os.path.join(dest, theme), "w") as t:
            t.write(text)


def _patch_specific(theme, dest, isettings):
    log("Patching `{}`".format(theme))

    theme_content = []

    color = isettings.get("color")
    if color:
        theme_content.append(_patch_icon(None, color))

    color_on_hover = isettings.get("color_on_hover")
    if color_on_hover:
        theme_content.append(_patch_icon("hover", color_on_hover))

    color_on_select = isettings.get("color_on_select")
    if color_on_select:
        theme_content.append(_patch_icon("selected", color_on_select))

    text = sublime.encode_value(theme_content)

    with open(os.path.join(dest, theme), "w") as t:
        t.write(text)


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
