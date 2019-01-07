import json
import os
import sublime

from .. import settings


def get_path(package_name):
    package_path = "Packages/" + package_name
    for res in sublime.find_resources("file_type_default.png"):
        if res.startswith(package_path):
            return os.path.dirname(res)
    return False


def get_missing(theme_package):
    missing_icons = []
    all_icons = sublime.find_resources("*.png")
    package_icons = json.loads(sublime.load_resource("Packages/" +
                                                     settings.PACKAGE_NAME +
                                                     "/common/icons.json"))
    theme_icons_path = get_path(theme_package)
    theme_icons = [
        os.path.basename(os.path.splitext(i)[0])
        for i in all_icons if i.startswith(theme_icons_path)
    ]
    for icon in package_icons:
        if icon not in theme_icons:
            missing_icons.append(icon)

    return missing_icons
