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

import discord
import yaml
from discord.ext import commands

def load_server_language(message):
    config = find_server_config(message)
    language = load_language(config["language"])
    return language


def load_language(lang):
    with open(pathlib.Path("data", "languages", f"{lang}.yml"), "r", encoding="utf8") as \
            lang:
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


class OtherCog(commands.Cog):
    """Всякие комманды которые нельзя определить в какой-либо модуль
    или их тема не соответствует ни одному из модулей"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

def setup(bot):
    bot.add_cog(OtherCog(bot, pathlib.Path(os.getcwd())))
