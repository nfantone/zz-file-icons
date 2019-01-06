import os
import shutil
import tempfile
import zipfile

import sublime
import sublime_plugin

from ..common import settings
from ..common.utils import path
from ..common.utils.logging import log, dump


def _is_enabled():
    if os.path.exists(path.get_overlay_aliases()):
        return True

    return False


def _remove():
    try:
        shutil.rmtree(path.get_overlay_aliases())
    except Exception as error:
        log("Error during remove")
        dump(error)
    finally:
        sublime.run_command("refresh_folder_list")


def _rename():
    aliases_path = path.get_overlay_aliases()

    try:
        for alias_base in os.listdir(aliases_path):
            alias_path = os.path.join(aliases_path, alias_base)

            if os.path.isfile(alias_path):
                name, ext = os.path.splitext(alias_path)
                os.rename(alias_path, alias_path.replace(".disabled-", "."))
    except Exception as error:
        log("Error during rename")
        dump(error)
    finally:
        sublime.run_command("refresh_folder_list")


def _copy():
    src = path.get_package_aliases()
    dest = path.get_overlay_aliases()

    try:
        shutil.copytree(src, dest)
    except Exception as error:
        log("Error during copy")
        dump(error)
    else:
        _rename()


def _extract():
    temp_dir = tempfile.mkdtemp()
    dest_path = path.get_overlay_aliases()

    try:
        with zipfile.ZipFile(path.get_package_archive(), "r") as z:
            members = z.namelist()
            members_to_extract = [
                m for m in members if m.startswith("aliases")
            ]

            z.extractall(temp_dir, members_to_extract)

            shutil.move(os.path.join(temp_dir, "aliases"), dest_path)
    except Exception as error:
        log("Error during extract")
        dump(error)
    else:
        _rename()


def enable():
    log("Enabling aliases")
    if not _is_enabled():
        if settings.is_package_archive():
            sublime.set_timeout_async(_extract, 0)
        else:
            sublime.set_timeout_async(_copy, 0)
    else:
        dump("Aliases already enabled")


def disable():
    log("Disabling aliases")
    if _is_enabled():
        sublime.set_timeout_async(_remove, 0)
    else:
        dump("Aliases already disabled")


def check():
    log("Checking aliases")

    if settings.package().get("aliases"):
        enable()
    else:
        disable()


class AfiCheckAliasesCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        check()
