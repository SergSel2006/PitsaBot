import os
import pathlib

import discord
from discord.ext import commands


class MainCog(commands.Cog, name="Основное"):
    """Начало Всех Начал! Этот модуль имеет всё основное для того,
    что бы бот что-то делал"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.command()
    async def help_me(self, ctx):
        """||descstart||
        ||shortstart||Помоги PitsaBot выити из красной книги||shortend||
        ||descend||"""
        await ctx.send(
            ":pizza:PitsaBot внесён в красную книгу и сейчас "
            "находится на грани вымирания\n"
            "Если хочешь помочь ему выжить, то переведи финансовую "
            "помошь в Фонд Спасения!\n"
            "вот один из вариантов: "
            "https://www.donationalerts.com/r/serg_sel"
            )
    
    @commands.command()
    async def help(self, ctx, command=None):
        """||descstart||
        ||shortstart||помощь по командам!||shortend||
        ||longstart||Можно воспользоваться этой коммандой для того,
        чтобы получить больше информации о командах или узнать все
        команды||longend||
        ||usage||команда||end||
        ||descend||"""
        def help_parser_3000(command: commands.Command):
            """this function now just tplit docstring into a sort
            description? long description and usage. Soon will load
             language files."""
            desc = command.help
            desc = desc[desc.find("||descstart||"):desc.find(
                "||descend||")]
            desc_short = desc[desc.find("||shortstart||") + 14:desc.find(
                "||shortend||")]
            desc_long = desc[desc.find("||longstart||") + 13:desc.find(
                "||longend||")]
            desc_usage = "<" + desc[desc.find("||usage||") + 9:desc.find(
                "||end||")] + ">" if "||usage||" in desc else ""
            return desc_short, desc_long, desc_usage
        if command:
            command = self.bot.get_command(command)
            if command:
                if not command.hidden:
                    descriptions = help_parser_3000(command)
                    builder = f"{command.cog_name} -> {command.name} " \
                              f"{descriptions[2]}>\n" \
                              f"{descriptions[1]}"
                    await ctx.send(builder)
                else:
                    await ctx.send("Комманда не найдена!")
            else:
                await ctx.send("Комманда не найдена!")
        
        else:
            owner_id = 457222828811485209
            owner = self.bot.get_user(owner_id)
            await ctx.send(f"PitsaBot 0.1A Pre-Release. Сейчас активно "
                           f"поддерживается {owner.name}\n")
            cogs = self.bot.cogs
            for cog in cogs:
                builder = f"{cog} - {cogs[cog].description}\n"
                await ctx.send(builder)
                for command in cogs[cog].get_commands():
                    if not command.hidden:
                        descriptions = help_parser_3000(command)
                        cbuilder = f"  {command.name} {descriptions[2]}" \
                                   f" - {descriptions[0]}\n"
                        await ctx.send(cbuilder)
    
    help.usage = "команда"
    
    @commands.command()
    async def hello(self, ctx):
        """Поприветствуй питсу"""
        author = ctx.message.author
        await ctx.send(f":pizza:Привет, {author.mention}!")


def setup(bot):
    bot.add_cog(MainCog(bot, pathlib.Path(os.getcwd())))
