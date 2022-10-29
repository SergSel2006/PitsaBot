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

import os
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


class GodPitsaCog(commands.Cog):
    """Этот модуль имеет всякие гаджеты для питсы, смотрите! Тут даже есть
    встроенная фабрика питсы!"""

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Cog.listener()
    async def on_message(self, message):
        config = find_server_config(message)
        if (message.author.id != 869082304033751120
            and config["react_to_pizza"]):
            pitsas = ['питса', "питсы", "питсу", "питсой", "питсе",
                      "pitsa", "питс", "питсам", "питсами", "питсах"]
            for pitsa in pitsas:
                if pitsa in message.content.lower():
                    await message.channel.send(":pizza:")
                    break
            hleps = ['хлеп', "хлепа", "хлепу", "хлепом", "хлепе", "hlep",
                     "хлепы", "хлепов", "хлепам", "хлепами", "хлепах"]
            for hlep in hleps:
                if hlep in message.content.lower():
                    await message.channel.send(":bread:")
                    break


async def setup(bot):
    await bot.add_cog(GodPitsaCog(bot, pathlib.Path(os.getcwd())))
