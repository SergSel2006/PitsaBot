"""Этот ког ничего не делает.
Он просто есть чтобы показать, как добавлять новые коги
P.S: его не надо загружать, и удалять приставку dev_, так как это
может отрицательно скааться на команде help
Зато его очень хорошо скопировать куда-нибудь и чуточку изменить"""

import os
import pathlib

from discord.ext import commands


class TemplateCog(commands.Cog, name=""):
    """ЭТОТ МОДУЛЬ НЕ ДОЛЖЕН БЫТЬ ЗАГРУЖЕН!"""

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Command
    async def template_command(self, ctx, arg):
        """этак команда ничего не делает, она просто для ознакомления"""
        pass

    @commands.Cog.listener()
    async def template_event(self):
        pass


def setup(bot):
    bot.add_cog(TemplateCog(bot, pathlib.Path(os.getcwd())))
