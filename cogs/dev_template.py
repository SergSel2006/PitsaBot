"""Этот ког ничего не делает.
Он просто есть чтобы показать, как добавлять новые коги
P.S: его не надо загружать, и удалять приставку dev_, так как это
может отрицательно скааться на команде help
Зато его очень хорошо скопировать куда-нибудь и чуточку изменить"""

import os
import pathlib

import discord

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


class TemplateCog(commands.Cog):
    """ЭТОТ МОДУЛЬ НЕ ДОЛЖЕН БЫТЬ ЗАГРУЖЕН!"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.Command
    async def template_command(self, ctx, arg):
        pass
    
    @commands.Cog.listener()
    async def template_event(self):
        pass


def setup(bot):
    bot.add_cog(TemplateCog(bot, pathlib.Path(os.getcwd())))
