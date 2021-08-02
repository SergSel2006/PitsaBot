import os
import pathlib

from discord.ext import commands


class MainCog(commands.Cog, name="Основное"):
    """Начало Всех Начал! Этот модуль имеет всё основное для того,
    что бы бот что-то делал"""
    
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
    
    @commands.command()
    async def help_me(self, ctx):
        """Помоги PitsaBot выити из красной книги"""
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
        """помощь по командам!"""
        if command:
            command = self.bot.get_command(command)
            if command:
                if not command.hidden:
                    builder = f"{command.cog_name} -> {command.name}\n" \
                              f"{command.help}"
                    await ctx.send(builder)
                else:
                    await ctx.send("Комманда не найдена!")
            else:
                await ctx.send("Комманда не найдена!")
        
        else:
            cogs = self.bot.cogs
            for cog in cogs:
                builder = f"{cog} - {cogs[cog].description}\n"
                await ctx.send(builder)
                for command in cogs[cog].get_commands():
                    if not command.hidden:
                        command_name = command.name
                        command_desc = command.short_doc
                        cbuilder = f"  {command_name} <{command.usage}>" \
                                   f"- {command_desc}\n"
                        await ctx.send(cbuilder)
    
    help.usage = "команда"
    
    @commands.command()
    async def hello(self, ctx):
        """Поприветствуй питсу"""
        author = ctx.message.author
        await ctx.send(f":pizza:Привет, {author.mention}!")


def setup(bot):
    bot.add_cog(MainCog(bot, pathlib.Path(os.getcwd())))
