#  Copyright (C) 2021  SergSel2006
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

# imports
import asyncio
import traceback
import logging
import pathlib
import sys
import discord
import yaml
import io
from discord.ext import commands

from Cog_MetaFile import Cog_File_Meta

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

# logger (replaces print)
intents = discord.Intents.default()
intents.members = True
con_logger = logging.getLogger("Bot")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]: %(message)s'))
con_logger.addHandler(sh)
con_logger.setLevel(logging.INFO if "-d" not in sys.argv else logging.DEBUG)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO if "-d" not in sys.argv else logging.DEBUG)
handler = logging.FileHandler(filename='Pitsa.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

printd = con_logger.debug
print = con_logger.info
printw = con_logger.warning
printe = con_logger.error

# interesting functions


# config checker for up-to-date keys with template
def check_configs(bot: discord.ext.commands.Bot):
    template_path = pathlib.Path("data", "servers_config", "template.yml")

    def diff(dict1: dict, dict2: dict):
        same = True
        if dict1 is None:
            dict1 = dict2
            return dict1, False
        for i in tuple(dict1.keys()):
            if i not in dict2:
                del dict1[i]
                same = False
                continue
            if type(dict2[i]) == dict:
                dict1[i], _ = diff(dict1[i], dict2[i])
                if not _:
                    same = _
        for i in dict2:
            if i not in tuple(dict1.keys()):
                dict1[i] = dict2[i]
                same = False
            if type(dict2[i]) == dict:
                dict1[i], _ = diff(dict1[i], dict2[i])
                if not _:
                    same = _
        return dict1, same

    with open(template_path, mode="r", encoding='utf8') as temp:
        for guild in bot.guilds:
            guild_dir = pathlib.Path("data", "servers_config", str(guild.id))
            config_path = guild_dir / "config.yml"
            if not guild_dir.exists():
                print(
                    f"added config for server {guild.name} with id {guild.id}")
                guild_dir.mkdir()
                config_path.touch()
                temp_dict = yaml.load(temp, Loader)
                lang_dir = pathlib.Path("data", "languages")
                langs = [i for i in lang_dir.iterdir() if i.suffix == ".yml"]
                if guild.preferred_locale in langs:
                    temp_dict["lang"] = guild.preferred_locale
                with open(config_path, mode="w", encoding='utf8') as config:
                    yaml.dump(temp_dict, config, Dumper)

            elif not config_path.exists():
                with open(config_path, mode="w", encoding='utf8') as config:
                    config.write(temp.read())
            else:
                with open(config_path, mode="r", encoding='utf8') as config:
                    config = yaml.load(config, Loader)
                    temp_dict = yaml.load(temp, Loader)
                    config, same = diff(config, temp_dict)
                if not same:
                    with open(config_path, mode='w', encoding='utf8')\
                            as config_raw:
                        yaml.dump(config, config_raw, Dumper)
            temp.seek(0)


# find language from message
def load_server_language(message):
    config = find_server_config(message)
    language = load_language(config["language"])
    return language


# load some language
def load_language(lang):
    with open(pathlib.Path("data", "languages", f"{lang}.yml"),
              "r",
              encoding="utf8") as lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


# find server config by message
def find_server_config(message):
    with open(pathlib.Path("data", "servers_config", str(message.guild.id),
                           "config.yml"),
              "r",
              encoding="utf8") as config:
        config = yaml.load(config, Loader=Loader)
        return config


# helper function for help
def help_parser_3000(command, language):
    try:
        if isinstance(command, commands.Command):
            Help = language["help"][command.name]
            cog = language["cogs"][command.cog_name]["name"]
            descs = (cog, Help["short"], Help["long"], Help["usage"],
                     Help["optional"], Help["returns"])
            return descs
        elif isinstance(command, str):
            name = language["cogs"][command]["name"]
            desc = language["cogs"][command]["desc"]
            return name, desc, '', '', '', ''
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
    except KeyError:
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'


# server prefix finder, if no prefix, return mention of a bot
def server_prefix(bot: commands.Bot, message):
    if isinstance(message.channel, discord.TextChannel):
        with open(
                pathlib.Path("data", "servers_config", str(message.guild.id),
                             "config.yml"), "r") as config:
            try:
                config = yaml.load(config, Loader)
                prefix = config["prefix"]
                return prefix
            except ValueError:
                return bot.user.mention
    else:
        return bot.user.mention


# cog finder
def cog_finder(bot: commands.Bot, start_path: pathlib.Path):
    global Cogs
    # add meta for created cogs
    for child in start_path.iterdir():
        if child.is_dir() and child.stem != "__pycache__":
            for i in child.iterdir():
                if i.name == "main.py":
                    meta = Cog_File_Meta(bot, i, name=child.name)
                    if meta.name not in tuple(Cogs.keys()):
                        printd(f"cog {child.name} founded")
                        Cogs[f"{meta.name}"] = meta
                        if not child.name.startswith("dev_"):
                            printd(meta.load())
        else:
            if child.suffix == ".py":
                meta = Cog_File_Meta(bot, child)
                if meta.name not in tuple(Cogs.keys()):
                    printd(f"cog {child.stem} founded")
                    Cogs[f"{meta.name}"] = meta
                    if not child.name.startswith("dev_"):
                        printd(meta.load())
    # delete meta for deleted cogs
    for cog in Cogs:
        if not Cogs[cog].self_check():
            cog = Cogs.pop(cog)
            if cog.active:
                cog.unload()
            printd(f"cog {cog.name} was deleted")


# ping that returns s of latency
def ping(bot: commands.Bot):
    latency = bot.latency
    try:
        return round(latency * 1000) / 1000
    except ValueError:
        return 0
    except OverflowError:
        printe("Your bot cannot connect to discord! your internet or "
               "code issue?")
        return 0


# check for a developer
def owner_check(ctx: commands.Context):
    return Bot.is_owner(ctx.author)


# to_thread decorator
def to_thread(func):

    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


# bot init

# cog list
Cogs = dict()

# intents
intents = discord.Intents.default()
intents.members = True

# bot settings
if len(sys.argv) > 2:
    if '--config' != sys.argv[1]:
        with open('config.yml', 'r') as o:
            settings = yaml.load(o, Loader)
        if not settings:
            raise ValueError("No Settings")
    else:
        settings = eval(" ".join(sys.argv[2:]))
else:
    with open('config.yml', 'r') as o:
        settings = yaml.load(o, Loader)
    if not settings:
        raise ValueError("No Settings")

# bot  itself
Bot = commands.Bot(command_prefix=server_prefix,
                   intents=intents,
                   owner_ids=settings["developers"])
Bot.remove_command("help")

# bot commands


# load_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def load_cog(ctx: commands.Context, cog):
    try:
        meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(meta.load())


# unload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def unload_cog(ctx: commands.Context, cog):
    try:
        meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(meta.unload())


# reload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def reload_cog(ctx: commands.Context, cog):
    try:
        meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(meta.reload())


# list_cogs command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def list_cogs(ctx: commands.Context):
    all_cogs = '\n'.join([i.name for i in list(Cogs.values())])
    loaded_cogs = '\n'.join([i.name for i in list(Cogs.values()) if i.active])
    builder = f"All cogs:\n{all_cogs}\nActive cogs:\n" \
              f"{loaded_cogs}"
    await ctx.send(builder)


# eval function (bad idea but with owner check it looks normal)
@Bot.command(hidden=True)
@commands.check(owner_check)
async def evaluate(ctx):
    try:
        if len(ctx.message.content.split("x")) > 1:
            command = " ".join(ctx.message.content.split(" ")[1:])
            result = exec(compile(command, 'in_code', mode="exec"))
            if result is not None:
                await ctx.send(result)
        elif ctx.message.attachments:
            attach = ctx.message.attachments[0]
            if "text" in attach.content_type:
                data = await attach.read()
                data = data.decode("utf-8")
                result = exec(compile(data, 'in_code', mode="exec"))
                if result is not None:
                    await ctx.send(result)
    except Exception as e:
        await ctx.send(''.join(traceback.format_exception(e)))


# help command
@Bot.command()
async def help(ctx: commands.Context, command=None):
    language = load_server_language(ctx.message)
    if command:
        try:
            command = Bot.get_command(command)
            if not command.hidden:
                descriptions = help_parser_3000(command, language)
                builder = f"{descriptions[0]} - {command}\n{command} " \
                    f"<{descriptions[3]}> [{descriptions[4]}] " \
                    f"-> {descriptions[5]}. {descriptions[2]}"
                await ctx.send(builder)
        except commands.errors.CommandNotFound:
            await ctx.send(language["misc"]["command_not_found_help"])
    else:
        builders = [language["misc"]["help_msg"]]
        cogs = Bot.cogs
        for cog in cogs:
            cog_desc = help_parser_3000(cog, language)
            builders.append(f"\n{cog_desc[0]} - {cog_desc[1]}")
            for command in cogs[cog].get_commands():
                if not command.hidden:
                    descriptions = help_parser_3000(command, language)
                    cbuilder = f"{command.name} " \
                               f"<{descriptions[3]}> [{descriptions[4]}] -> " \
                               f"{descriptions[5]}. {descriptions[1]}"
                    builders.append(cbuilder)
        await ctx.send("\n".join(builders))


# bot launching
async def on_tick(tick: int = 5):
    while True:
        await asyncio.sleep(tick)
        try:
            if ping(Bot) > 2:
                to_thread(printw(f"High ping! {ping(Bot)} s"))
            check_configs(Bot)  # should be before check_configs as after
            # start we should synchronise our config files with cloud.
            cog_finder(Bot, pathlib.Path("cogs"))
        except Exception as e:
            exc_info = ''.join(traceback.format_exception(e))
            printe(f"error occured, ignoring!\n{exc_info}")


@Bot.event
async def on_ready():
    print(f"bot is ready, ping is {ping(Bot)} seconds")
    asyncio.ensure_future(on_tick())


# error handler for (almost) pretty error handling ;-)
async def on_error(ctx, error):
    lang = load_server_language(ctx)
    exc_info = ''.join(traceback.format_exception(error))
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(lang["misc"]["not_enough_permissions"])
    elif "discord.errors.Forbidden" in exc_info:
        try:
            await ctx.guild.owner.dm_channel.send(lang["misc"]["forbidden"])
        except AttributeError:
            await ctx.guild.owner.create_dm()
            await ctx.guild.owner.dm_channel.send(lang["misc"]["forbidden"])
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(lang["misc"]["not_enough_arguments"])
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(lang["misc"]["command_not_found"])
    elif isinstance(error, SystemExit):
        print("shutting down, goodbye!")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(lang["misc"]["bad_argument"])
    else:
        printe(f"error occured, ignoring!\n{exc_info}")


Bot.on_command_error = on_error
Bot.settings = settings
Bot.run(settings["token"])
