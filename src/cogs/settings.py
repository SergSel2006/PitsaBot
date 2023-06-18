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

import gettext
import pathlib
import traceback

import shared
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

_ = gettext.gettext


def load_language(lang):
    with open(
            pathlib.Path("locales", f"{lang}.yml"), "r",
            encoding="utf8"
            ) as lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


def find_server_config(message):
    with open(
            pathlib.Path(
                "..", "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "r", encoding="utf8"
            ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


class Settings(commands.Cog):
    description = _("Configurations for bot")

    def __init__(self, bot):
        self.bot = bot

    settings_attrs = {
        "name": _("config"),
        "usage": _("<subcommand>"),
        "brief": _("changes settings. use `help config` for details."),
        "description": _(
            "Changes bots configurations. Available subcommands:"
            "\n  prefix <prefix>"
            "\n  modrole <add/remove moderator's roles>"
            "\n  modlog <enable/channel (this)/disable>"
            "\n  language <language>"
            "\n  counting <enable/channel (this)/disable/big (number)>"
            )
        }

    @commands.command(**settings_attrs)
    @shared.can_manage_server()
    async def config(self, ctx, mode, *options):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        try:
            if mode == "trigger":
                if options[0].lower() == "enable":
                    config["everyonetrigger"] = True
                else:
                    config["everyonetrigger"] = False
            elif mode == "react":
                if options[0].lower() == "enable":
                    config["react_to_pizza"] = True
                else:
                    config["react_to_pizza"] = False
            else:
                raise NotImplementedError(
                    "Configuration mode {0} Not Implemented".format(mode)
                    )
            shared.dump_server_config(ctx.message, config)
        except Exception as e:
            await ctx.send(
                _(
                    "Oops! Something went wrong! If this happens too often,"
                    " send basic information about"
                    " what you've done and this code: {0} to issue tracker"
                    ).format(ctx.guild.id)
                )
            exc_info = ''.join(traceback.format_exception(e))
            shared.printe(
                "While configuring {0}, error occurred and ignored."
                "\n{1}".format(ctx.guild.id, exc_info)
                )


async def setup(bot):
    await bot.add_cog(Settings(bot))
