import json
import os
import sublime
import sublime_plugin

from .. import settings
from ...core.themes import get_current, get_installed


def _get_package_version():
    pkg_json = sublime.load_resource("Packages/" + settings.PACKAGE_NAME +
                                     "/package.json")

    return json.loads(pkg_json)["version"]


def _is_installed_via_pc():
    return str(settings.PACKAGE_NAME in set(settings.pkgctrl()
                                            .get("installed_packages", [])))


class AfiEnvironmentCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        info = {}

        info["platform"] = sublime.platform()
        info["sublime_version"] = sublime.version()

        info["current_theme"] = get_current()
        info["installed_themes"] = "".join([
            "\n  <li>{}</li>".format(k) for k in get_installed().keys()
        ])

        info["package_version"] = _get_package_version()
        info["installed_via_pc"] = _is_installed_via_pc()

        msg = """\
            <b>Platform:</b> %(platform)s<br>
            <b>A File Icon:</b> %(package_version)s<br>
            <b>Sublime Text:</b> %(sublime_version)s<br>
            <b>Package Control:</b> %(installed_via_pc)s<br>
            <b>Current Theme:</b> %(current_theme)s<br>
            <b>Installed Themes:</b><br>
            <ul>%(installed_themes)s
            </ul>
        """ % info

        html = """\
            <div id="afi-environment">
                <style>
                    #afi-environment {
                        padding: 0.5rem;
                        line-height: 1.5;
                    }
                    #afi-environment ul {
                        margin-top: 0.5rem;
                        margin-bottom: 0;
                        margin-left: 1rem;
                    }
                    #afi-environment a {
                        display: inline;
                    }
                </style>
                <a href="copy">Copy</a><br><br>
                %(msg)s
            </div>
        """ % {"msg": msg}

        window = sublime.active_window()
        view = window.active_view()
        window.focus_view(view)
        row = int(view.rowcol(view.visible_region().a)[0] + 1)

        def on_navigate(href):
            if (href.startswith("copy")):
                sublime.set_clipboard(msg.replace("    ", ""))
            view.hide_popup()

        view.show_popup(html,
                        location=view.text_point(row, 5),
                        max_width=800,
                        max_height=800,
                        on_navigate=on_navigate)
