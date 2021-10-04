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
            ) as \
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
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Command
    async def meme(self, ctx):
        await ctx.send("мем: питса не делается в пиццерии")
    
    @commands.Command
    async def ping(self, ctx):
        builder = f"Pong! `{round(self.bot.latency  * 1000)} ms`"
        await ctx.send(builder)

def setup(bot):
    bot.add_cog(OtherCog(bot, pathlib.Path(os.getcwd())))
