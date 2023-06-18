#  Copyright (c) 2022-2023 SergSel2006 (Sergey Selivanov).
#
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Shared part of code and variables. Also some functionality goes here"""
import gettext
import logging
import pathlib
import sys

import yaml
from discord.ext import commands

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

# Some useful constants.
VERSION = "v0.3.1-alpha"
NAME = "PitsaBot"

lang_table = {}
# made to ease creating of new translations. Just add new folder and
# this code will enable it for use (should be translated before)
# P.S: using different domains for different parts of bot was a
# bad idea. Now one domain is created for everything in src/
for i in [i for i in pathlib.Path("src", "locales").iterdir()
          if i.is_dir()]:
    i = i.stem
    lang_table[i] = gettext.translation(
        i, pathlib.Path("src", "locales"), languages=["all"], fallback=True
        )

_ = gettext.gettext


# find language from message
def load_server_language(message):
    config = find_server_config(message)
    language = lang_table[config["language"]]
    return language


# For creating new cogs we need this. Copy sysconfig form Core (except cases)
# to your cog and name it reasonably. Edit for your needs AND edit
# template.yml for your new configuration. Actually soon it will be changed.
def dump_server_config(message, config):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "w", encoding="utf8"
            ) as config_file:
        yaml.dump(config, config_file, Dumper=Dumper)


# check for settings commands
def can_manage_server():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        if perms.administrator or ctx.author.id == ctx.guild.owner_id:
            return True
        else:
            return False

    return commands.check(predicate)


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


class _ColourFormatter(logging.Formatter):
    """
    Formatter adapted from discord.py code to be familiar with its logging
    """

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them,
    # so here's a refresher
    # It starts off with a format like \x1b[XXXm
    # where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white
    # in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
        ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m '
            f'\x1b[35m%(name)s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
            )
        for level, colour in LEVEL_COLOURS
        }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


con_logger = logging.getLogger("Bot")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(
    _ColourFormatter()
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
