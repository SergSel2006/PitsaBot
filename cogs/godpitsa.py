import os
import pathlib

from discord.ext import commands


class GodPitsaCog(commands.Cog):
    """Этот модуль имеет всякие гаджеты для питсы, смотрите! Тут даже есть
    встроенная фабрика питсы!"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != 869082304033751120:
            pitsas = ['питса', "питсы", "питсу", "питсой", "питсе",
                      "pitsa", "питс", "питсам", "питсами", "питсах"]
            flag = True
            for pitsa in pitsas:
                if pitsa in message.content.lower() and flag:
                    await message.channel.send(":pizza:")
                    flag = False


def setup(bot):
    bot.add_cog(GodPitsaCog(bot, pathlib.Path(os.getcwd())))
