import json
import os
import pathlib

import discord
import requests
from discord.ext import commands


class OtherCog(commands.Cog, name="другое"):
    """Всякие комманды которые нельзя определить в какой-либо модуль
    или их тема не соответствует ни одному из модулей"""

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.command()
    async def brawl_stars_cheats(self, ctx):
        """скачать читы на brawl stars(работает но не поддерживается)"""
        response = requests.get('https://some-random-api.ml/animal/cat')
        json_data = json.loads(response.text)
        embed = discord.Embed(color=0xff9900, title='Читы закончились :/,'
                                                    ' держи котика :D')
        embed.set_image(url=json_data['image'])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OtherCog(bot, pathlib.Path(os.getcwd())))
