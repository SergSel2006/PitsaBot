import os
import pathlib

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

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


class MainCog(commands.Cog):
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
        
        lang = load_server_language(ctx.message)
        
        def help_parser_3000(command):
            if isinstance(command, commands.Command):
                help = lang["help"][command.name]
                cog = lang["cogs"][command.cog_name]["name"]
                descs = (cog, help["short"], help["long"], help["usage"],
                         help["optional"],
                         help["returns"])
                return descs
            elif isinstance(command, str):
                name = lang["cogs"][command]["name"]
                desc = lang["cogs"][command]["desc"]
                return name, desc
            return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
        
        if command:
            command = self.bot.get_command(command)
            if command:
                if not command.hidden:
                    try:
                        descriptions = help_parser_3000(command)
                    except KeyError:
                        descriptions = ('N/A', 'N/A', 'N/A', 'N/A', 'N/A')
                    builder = f"{descriptions[0]} - {command}\n{command} " \
                              f"{'<' + descriptions[3] + '>' if descriptions[3] else ''} " \
                              f"{'{' + descriptions[4] + '}' if descriptions[4] else ''} ->" \
                              f" {descriptions[5]}. " \
                              f"{descriptions[2]}"
                    await ctx.send(builder)
                else:
                    await ctx.send(lang["misc"]["command_not_found_help"])
            else:
                await ctx.send(lang["misc"]["command_not_found_help"])
        
        else:
            builders = []
            owner_id = 457222828811485209
            owner = self.bot.get_user(owner_id)
            
            cogs = self.bot.cogs
            for cog in cogs:
                try:
                    cog_desc = help_parser_3000(cog)
                except KeyError:
                    cog_desc = ('N/A', 'N/A', 'N/A', 'N/A', 'N/A')
                builder = f"\n{cog_desc[0]} - {cog_desc[1]}"
                builders.append(builder)
                for command in cogs[cog].get_commands():
                    if not command.hidden:
                        try:
                            descriptions = help_parser_3000(command)
                        except KeyError:
                            descriptions = ('N/A', 'N/A', 'N/A', 'N/A', 'N/A')
                        cbuilder = f"{command.name} " \
                                   f"{'<' + descriptions[3] + '>' if descriptions[3] else ''} " \
                                   f"{'{' + descriptions[4] + '}' if descriptions[4] else ''} -> " \
                                   f"{descriptions[5]}. {descriptions[1]}"
                        builders.append(cbuilder)
            await ctx.send(lang["misc"]["help_msg"] + owner.name)
            await ctx.send("\n".join(builders))


def setup(bot):
    bot.add_cog(MainCog(bot, pathlib.Path(os.getcwd())))
