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


def load_server_language(message):
    config = find_server_config(message)
    language = load_language(config["language"])
    return language


def load_language(lang):
    with open(
            pathlib.Path("data", "languages", f"{lang}.yml"), "r",
            encoding="utf8"
            ) as lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


def find_server_config(message):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "r", encoding="utf8"
            ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


def can_manage_channels():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        return perms.manage_channels or perms.administrator
    
    return commands.check(predicate)


class ModCog(commands.Cog):
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        lang = load_server_language(msg)
        config = find_server_config(msg)
        if config["modlog"]["enabled"]:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                lang["misc"]["deleted_message"].replace(
                    "$USER", msg.author.nick).replace("$MESSAGE", msg.content)
                )
    
    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg):
        lang = load_server_language(msg)
        config = find_server_config(msg)
        if config["modlog"]["enabled"]:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                lang["misc"]["changed_message"].replace(
                    "$USER", msg.author.nick).replace(
                    "$OLD_MESSAGE", msg_before.content).replace("$NEW_MESSAGE",
                                                                msg.content)
                )


def setup(bot):
    bot.add_cog(ModCog(bot, pathlib.Path(os.getcwd())))
