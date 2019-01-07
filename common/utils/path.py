import os
import sublime

from .. import settings


def get_package_archive():
    return os.path.join(sublime.installed_packages_path(),
                        settings.PACKAGE_ARCH)


def get_package_folder():
    return os.path.join(sublime.packages_path(), settings.PACKAGE_NAME)


def get_package_icons():
    return os.path.join(sublime.packages_path(), settings.PACKAGE_NAME,
                        "icons")


def get_package_aliases():
    return os.path.join(sublime.packages_path(), settings.PACKAGE_NAME,
                        "aliases")


def get_overlay():
    return os.path.join(sublime.packages_path(), settings.OVERLAY_ROOT)


def get_overlay_aliases():
    return os.path.join(sublime.packages_path(), settings.OVERLAY_ROOT,
                        "aliases")


def get_overlay_patches():
    return os.path.join(sublime.packages_path(), settings.OVERLAY_ROOT,
                        "patches")


def get_overlay_patches_general():
    return os.path.join(sublime.packages_path(), settings.OVERLAY_ROOT,
                        "patches", "general")


def get_overlay_patches_specific():
    return os.path.join(sublime.packages_path(), settings.OVERLAY_ROOT,
                        "patches", "specific")
