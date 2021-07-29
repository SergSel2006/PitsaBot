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


    @commands.command(hidden=True)
    async def fetch_user(self, ctx):
        if ctx.message.author.id != 457222828811485209:
            await ctx.send("Только один человек может воспользоваться этой "
                           "коммандой...")
        else:
            user = ctx.message.mentions[0]
            if user.bot:
                await ctx.send("Этот пользователь - Бот!")
            if user.mutual_guilds:
                await ctx.send("У пользователя обнаружены Сервера!")
                for guild in user.mutual_guilds:
                    await ctx.send("Сервер " + guild.name)

    @commands.command(hidden=True)
    async def destroy_bot(self, ctx):
        if ctx.message.author.id != 457222828811485209:
            await ctx.send("Только один человек может воспользоваться этой "
                           "коммандой...")
        else:
            user = ctx.message.mentions[0]
            for role in user.roles:
                try:
                    await user.remove_roles(role)
                except discord.Forbidden:
                    pass

    @commands.command(hidden=True)
    async def botsay(self, ctx, channel, *, message):
        if ctx.message.author.id != 457222828811485209:
            await ctx.send("Только один человек может воспользоваться этой "
                           "коммандой...")
        else:
            try:
                channel = self.bot.get_channel(int(channel))
            except Exception:
                message = " ".join([channel, message])
            try:
                await channel.send(message)
            except discord.Forbidden:
                try:
                    await ctx.message.delete()
                except discord.Forbidden:
                    pass
                await ctx.send(message)


def setup(bot):
    bot.add_cog(OtherCog(bot, pathlib.Path(os.getcwd())))
