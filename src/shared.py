#  Copyright (c) 2022.
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""All variables and functions that are shared across code are here"""
import gettext
import logging
import pathlib
import sys

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

lang_table = {}
# made to ease creating of new translations. Just add new folder and
# this code will enable it for use (should be translated before)
# P.S: using different domains for different parts of bot was a
# bad idea. Now one domain is created for everything in src/
for i in [str(i) for i in pathlib.Path("src", "locales").iterdir()
          if i.is_dir()]:
    i = i.removeprefix("src/locales/")
    lang_table[i] = gettext.translation(
        i, "src/locales/", languages=["all"], fallback=True
    )

_ = gettext.gettext


# find language from message
def load_server_language(message):
    config = find_server_config(message)
    language = lang_table[config["language"]]
    return language


# find server config by message
def find_server_config(message):
    with open(
        pathlib.Path(
            "data", "servers_config", str(message.guild.id),
            "config.yml"
        ),
        "r",
        encoding="utf8"
    ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


class CustomFormatter(logging.Formatter):
    """Logging colored formatter,
    adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


con_logger = logging.getLogger("Bot")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(
    CustomFormatter('%(asctime)s {%(levelname)s} [%(name)s]: %(message)s')
)
handler = logging.FileHandler(filename='Pitsa.log', encoding='utf-8', mode='w')
con_logger.addHandler(sh)
con_logger.setLevel(logging.INFO if "-d" not in sys.argv else logging.DEBUG)
con_logger.addHandler(handler)
printd = con_logger.debug
print = con_logger.info
printw = con_logger.warning
printe = con_logger.error
printc = con_logger.critical

# all translations for everything not in code.
# _() FROM HERE WON'T TRANSLATE THEM MAGICALLY IN FUNCTIONS.
# They're just for markup purposes.
# Use function's own _() for translating,
# like ctx.send(_(translation["cogs"]["SettingsCog"]["desc'])).
# Hierarchy is:
# ┌─translation
# └─┬──cogs
#   ├─cog1
#   ├─cog2
#   ├─...
#   ├─cogn
#   ├─desc: cog's description string
#   ├─name: cog's name
#   └─┬─commands
#     ├─command1
#     ├─command2
#     ├─...
#     └─┬─commandn
#       ├─desc: description about commandn for help message
#       ├─required: required arguments for commandn in help message.
#                   List of strings with arguments' names
#       ├─optional: optional arguments for commandn in help message.
#                   List of strings with arguments' names
#       └─result: result of commandn for help message.
# each trunk (└ or ├) is another [] pair with name of that part.
# (yeah I know it is long)
translation = {
    "cogs": {
        "SettingsCog": {
            "desc": _("Changes server settings."),
            "name": _("Settings"),
            "commands": {
                "config": {
                    "desc": _(
                        "Changes bot's config. Available configs:"
                        "\n prefix <prefix>"
                        "\n modrole <add/remove moderator's roles>"
                        "\n modlog <enable/channel/this/disable>"
                        "\n language <language>"
                    ),
                    "required": _("config"),
                    "optional": None,
                    "result": _("bot's config changes")
                }
            }
        },
        "OtherCog": {
            "desc": _("Commands that developers didn't put in any of modules"),
            "name": _("Other"),
            "commands": {

            }
        },
        "ModCog": {
            "desc": _("Commands for moderators. Also is a core for modlog"),
            "name": _("Moderation"),
            "commands": {
                "ban": {
                    "desc": _("bans person"),
                    "required": _("preson and reason"),
                    "optional": None,
                    "result": _("Ban")
                }
            }
        },
        "GodPitsaCog": {
            "desc": _("this module has everything for pitsa and hlep"),
            "name": _("Pitsa's commands (and hlep's)"),
            "commands": {

            }
        },
    }
}
