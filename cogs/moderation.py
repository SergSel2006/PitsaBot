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


class ModCog(commands.Cog, name="Команды для модераторов"):
    """Команды для модераторов сервера. Также имеет модлог"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @staticmethod
    def find_server_config(message):
        return pathlib.Path(
            "data", "servers_config", str(message.guild.id),
            "config.yml"
            )
    
    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        with open(self.find_server_config(msg), 'r') as raw_config:
            config = yaml.load(raw_config, Loader)
            if config["modlog"]["enabled"]:
                ch = self.bot.get_channel(config["modlog"]["channel"])
                await ch.send(
                    f"Пользователь {msg.author} удалил сообщение. "
                    f"Содержание сообщения:\n{msg.content}"
                    )
    
    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg):
        with open(self.find_server_config(msg), 'r') as raw_config:
            config = yaml.load(raw_config, Loader)
            if config["modlog"]["enabled"]:
                ch = self.bot.get_channel(config["modlog"]["channel"])
                await ch.send(
                    f"Пользователь {msg.author.mention} изменил сообщение. "
                    f"Содержание сообщения до изменения:"
                    f"\n{msg_before.content}\nСодержание сообщения "
                    f"после изменения:\n{msg.content}"
                    )


def setup(bot):
    bot.add_cog(ModCog(bot, pathlib.Path(os.getcwd())))
