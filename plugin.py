import sublime

if int(sublime.version()) >= 3114:
    from .common import settings
    from .common.utils import cleaning
    from .common.utils import logging

    from .core import icons
    from .core import aliases

    from .common.utils.environment import AfiEnvironmentCommand
    from .common.utils.reloader import AfiReloadCommand
    from .common.utils.cleaning import AfiCleanCommand
    from .common.utils.cleaning import AfiRevertCommand

    from .core.aliases import AfiCheckAliasesCommand
    from .core.themes import AfiPatchThemesCommand

    from .common.settings import PACKAGE_NAME

    NOPC_MSG = "It seems like you don't have Package Control installed"

    def main():
        """
        The main routine.
        """
        settings.init()
        icons.init()

    def ensure_reload():
        """
        Ensure all modules reload to initialize plugin successfully.
        """
        start_upgrade_msg = "Do not close the Sublime Text. Upgrading {}".format(
            PACKAGE_NAME
        )
        finish_upgrade_msg = "{} upgrade finished.".format(PACKAGE_NAME)

        active_view = sublime.active_window().active_view()
        active_view.set_status("afi_status", start_upgrade_msg)

        def erase_status():
            active_view.erase_status("afi_status")

        def reload():
            sublime.run_command("afi_reload")
            active_view.set_status("afi_status", finish_upgrade_msg)
            sublime.set_timeout(erase_status, 2000)

        sublime.set_timeout_async(reload, 5000)

    def plugin_loaded():
        """
        A File Icon loaded.

        Raises:
            ImportError: If `Package Control` is not installed.
        """
        was_upgraded = False

        try:
            from package_control import events
        except ImportError as error:
            logging.log(NOPC_MSG)
            logging.dump(error)
        else:
            was_upgraded = events.post_upgrade(PACKAGE_NAME)
        finally:
            if was_upgraded:
                ensure_reload()
            else:
                main()

    def plugin_unloaded():
        """
        A File Icon unloaded.

        Raises:
            ImportError: If `Package Control` is not installed.
        """
        is_upgrading = False
        was_removed = False

        settings.clear_listener()

        try:
            from package_control import events
        except ImportError as error:
            logging.log(NOPC_MSG)
            logging.dump(error)
        else:
            is_upgrading = events.pre_upgrade(PACKAGE_NAME)
            was_removed = events.remove(PACKAGE_NAME)
        finally:
            if is_upgrading or was_removed:
                cleaning.clean_all()
else:
    raise ImportWarning("Doesn't support Sublime Text versions prior to 3114")
