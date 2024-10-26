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
import discord

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

# Some useful constants.
VERSION = "v0.4.0-alpha"
NAME = "PitsaBot"


DEFAULT_CONF = {
    'counting': {
        'channel': '',
        'enabled': False,
        'huge': 100,
        'last-counted-person': 0,
        'number': 0
    },
    'disabled_commands': [],
    'everyonetrigger': False,
    'global_db': True,
    'language': 'en',
    'modlog': {'channel': '', 'enabled': False},
    'modroles': [],
    'polls': [],
    'prefix': 'p',
    'react_to_pizza': False,
    'words': {
        'channel': '',
        'correct-count': 0,
        'dictionary': [],
        'enabled': False,
        'huge': 100,
        'last-counted-person': 0,
        'last-word': '',
        'prohibited_chars': []
    }
}
lang_table = {}
# made to ease creating of new translations. Just add new folder and
# this code will enable it for use (should be translated before)
# P.S: using different domains for different parts of bot was a
# bad idea. Now one domain is created for everything in src/
for i in [i for i in pathlib.Path("src", "locales").iterdir()
          if i.is_dir()]:
    path = i.stem
    lang_table[i] = gettext.translation(
        path, str(pathlib.Path("src", "locales")), languages=["all"],
        fallback=True
    )

_ = gettext.gettext


# find language from message
def load_server_language(ident: int) -> gettext.NullTranslations:
    config = find_server_config(ident)
    language = lang_table[config["language"]]
    return language


# For creating new cogs we need this. Copy sysconfig form Core (except cases)
# to your cog and name it reasonably. Edit for your needs AND edit
# template.yml for your new configuration. Actually soon it will be changed.
def dump_server_config(ident: int, config):
    def diff_default(default, new):
        new = new.copy()
        for i in default.keys():
            if type(default[i]) is dict:
                new[i] = diff_default(default[i], new[i])
                if new[i] == {}:
                    new.pop(i)
            elif new[i] == default[i]:
                new.pop(i)
        for i in set(new.keys()).difference(default.keys()):
            new.pop(i)
            print("The configuration for " + str(ident) +
                  " contained the configuration key which is not "
                  "in the default configuration, that means it was "
                  "probably deprecated for a while and now deleted.\n"
                  "Deleting it now from the configuration.")
        return new
    with open(
            pathlib.Path(
                "data", "servers_config", str(ident),
                "config.yml"
            ), "w", encoding="utf8"
    ) as config_file:
        config = diff_default(DEFAULT_CONF, config)
        yaml.dump(config, config_file, Dumper=Dumper)


# check for settings commands
def can_manage_server():
    async def predicate(ctx: commands.Context):
        if type(ctx.author) is discord.Member:
            perms = ctx.author.guild_permissions
            return perms.administrator
        else:
            return True

    return commands.check(predicate)


# find server config by message
def find_server_config(ident: int) -> dict:
    config: dict
    try:
        with open(
            pathlib.Path(
                "data", "servers_config", str(ident),
                "config.yml"
            ),
            "r",
            encoding="utf8"
        ) as fd:
            assert type(yaml.load(fd, Loader=Loader)) is dict
            # so mypy is not complaining again. You must have weird condition
            # where it is wrong.
            config = yaml.load(fd, Loader=Loader)
    except yaml.YAMLError:
        return DEFAULT_CONF.copy()
    except FileNotFoundError:
        printw("No configuration file created yet for " + str(ident))
        return DEFAULT_CONF.copy()

    def fill_defaults(default: dict, new: dict) -> dict:
        new = new.copy()
        for i in default.keys():
            if type(default[i]) is dict:
                new.setdefault(i, {})
                new[i] = fill_defaults(default[i], new[i])
            else:
                new.setdefault(i, default[i])
        return new
    config = fill_defaults(DEFAULT_CONF, config)
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
