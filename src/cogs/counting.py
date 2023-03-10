#  Copyright (c) 2023 SergSel2006 (Sergey Selivanov).
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

import pathlib

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper
import yaml

from discord.ext import commands
import discord
import gettext
import shared

_ = gettext.gettext


def dump_server_config(message, config):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "w", encoding="utf8"
            ) as config_file:
        yaml.dump(config, config_file, Dumper=Dumper)


async def counting(msg: discord.Message):
    translate = shared.load_server_language(msg).gettext
    config = shared.find_server_config(msg)
    counting_ = config["counting"]
    if counting_["enabled"]:
        if msg.channel.id == counting_["channel"]:
            target_message: str = msg.content.split(" ")[0]
            test_str = [i in "0123456789.()/*-+%" for i in target_message]
            if all(test_str):
                number = int(eval(target_message))
            else:
                return
            if number == int(counting_["number"]) + 1 and \
                    msg.author.id != counting_["last-counted-person"]:
                counting_["number"] = number
                if counting_["number"] <= counting_["huge"]:
                    await msg.add_reaction("✅")
                else:
                    await msg.add_reaction("☑️")
                counting_["last-counted-person"] = msg.author.id
            else:
                await msg.add_reaction("❌")
                if counting_["number"] <= counting_["huge"]:
                    await msg.channel.send(
                        translate(
                            _(
                                "{0} Failed count on {1}! "
                                "Starting from 1 again..."
                                )
                            ).format(
                            msg.author.mention, counting_["number"]
                            )
                        )
                else:
                    await msg.channel.send(
                        translate(
                            _(
                                "NOOOOO! What s shame, {0} Failed count on "
                                "{1} (AKA Big Number)!\n"
                                "Starting from 1 again..."
                                )
                            ).format(
                            msg.author.mention, counting_["number"]
                            )
                        )
                counting_["number"] = 0
                counting_["last-counted-person"] = 0
            dump_server_config(msg, config)


class Counting(commands.Cog):
    description = _("Module to make some counting.")

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            await counting(msg)


async def setup(bot):
    await bot.add_cog(Counting(bot))
