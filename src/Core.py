#  Copyright (c) 2022.
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.

# imports
import asyncio
import gettext
import logging
import pathlib
import sys
import traceback

gettext.bindtextdomain("base", "locales")
gettext.bindtextdomain("moderation", "locales")
gettext.bindtextdomain("settings", "locales")

_ = gettext.gettext

import discord
import yaml
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

from shared import print, printd, printc, printw
import shared

# logger (replaces print)
# Beautiful color formatting


intents = discord.Intents.default()
intents.members = True
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO if "-d" not in sys.argv else logging.DEBUG)
handler = logging.FileHandler(filename='Pitsa.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logger.addHandler(handler)

# interesting functions
# config checker for up-to-date keys with template
def check_configs(bot: discord.ext.commands.Bot):
    template_path = pathlib.Path(
        "data", "servers_config", "template.yml"
    )

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
                dict1[i], other_same = diff(dict1[i], dict2[i])
                if not other_same:
                    same = other_same
        for i in dict2:
            if i not in tuple(dict1.keys()):
                dict1[i] = dict2[i]
                same = False
            if type(dict2[i]) == dict:
                dict1[i], other_same = diff(dict1[i], dict2[i])
                if not other_same:
                    same = other_same
        return dict1, same

    with open(template_path, mode="r", encoding='utf8') as temp:
        for guild in bot.guilds:
            guild_dir = pathlib.Path(
                "data", "servers_config", str(guild.id)
            )
            config_path = guild_dir / "config.yml"
            if not guild_dir.exists():
                print(
                    f"added config for server {guild.name} with id {guild.id}"
                )
                guild_dir.mkdir()
                config_path.touch()
                temp_dict = yaml.load(temp, Loader)
                langs = shared.lang_table.keys()
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
                    with open(config_path, mode='w', encoding='utf8') \
                        as config_raw:
                        yaml.dump(config, config_raw, Dumper)
            temp.seek(0)


# helper function for help
def help_parser_3000(command):
    try:
        pass
    except KeyError:
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'


# server prefix finder, if no prefix, return mention of a bot
def server_prefix(bot: commands.Bot, message):
    if isinstance(message.channel, discord.TextChannel):
        with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
            ), "r"
        ) as config:
            try:
                config = yaml.load(config, Loader)
                prefix = config["prefix"]
                return prefix
            except ValueError:
                return bot.user.mention
    else:
        return bot.user.mention


# cog finder
async def cog_finder(bot: commands.Bot, start_path: pathlib.Path):
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
                            printd(await meta.load())
        else:
            if child.suffix == ".py":
                meta = Cog_File_Meta(bot, child)
                if meta.name not in tuple(Cogs.keys()):
                    printd(f"cog {child.stem} founded")
                    Cogs[f"{meta.name}"] = meta
                    if not child.name.startswith("dev_"):
                        printd(await meta.load())
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
        printc(
            "Your bot cannot connect to discord! your internet or "
            "code issue?"
        )
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
intents.message_content = True


# bot settings
def find_until_next_arg(string):
    return string.find("-")


if len(sys.argv) > 2:
    if '--config' != sys.argv[1]:
        with open('config.yml', 'r') as o:
            settings = yaml.load(o, Loader)
        if not settings:
            raise ValueError("No Settings")
    else:
        settings = eval(
            " ".join(sys.argv[2:find_until_next_arg(" ".join(sys.argv[2:]))])
        )
else:
    with open('config.yml', 'r') as o:
        settings = yaml.load(o, Loader)
    if not settings:
        raise ValueError("No Settings")

# bot  itself
Bot = commands.Bot(
    command_prefix=server_prefix,
    intents=intents,
    owner_ids=settings["developers"]
)
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
    await ctx.send(await meta.load())


# unload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def unload_cog(ctx: commands.Context, cog):
    try:
        meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(await meta.unload())


# reload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def reload_cog(ctx: commands.Context, cog):
    try:
        meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(await meta.reload())


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
        if len(ctx.message.content.split(" ")) > 1:
            command = " ".join(ctx.message.content.split(" ")[1:])
            compiled_code = compile(command, 'in_code', mode="exec")
            locals_before = locals().copy()
            exec(compiled_code)
            locals_after = locals().copy()
            locals_after.pop("locals_before")
            if locals_after != locals_before:
                diff = set(locals_after) - set(locals_before)
                for i in diff:
                    await ctx.send(i + " = " + str(locals_after[i]))

                pass
        elif ctx.message.attachments:
            attach = ctx.message.attachments[0]
            if "text" in attach.content_type:
                data = await attach.read()
                data = data.decode("utf-8")
                locals_before = locals().copy()
                exec(compile(data, 'in_code', mode="exec"))
                locals_after = locals().copy()
                locals_after.pop("locals_before")
                if locals_after != locals_before:
                    result = set(locals_before) - set(locals_after)
                    if result is not None:
                        for i in result:
                            await ctx.send(i + " = " + str(locals_after[i]))
    except Exception as e:
        await ctx.send(''.join(traceback.format_exception(e)))


# help command
@Bot.command()
async def help(ctx: commands.Context, command=None):
    _ = shared.load_server_language(ctx.message)
    if command:
        try:
            command = Bot.get_command(command)
            if not command.hidden:
                descriptions = help_parser_3000(command)
                builder = f"{descriptions[0]} - {command}\n{command} " \
                          f"<{descriptions[3]}> [{descriptions[4]}] " \
                          f"-> {descriptions[5]}. {descriptions[2]}"
                await ctx.send(builder)
        except commands.errors.CommandNotFound:
            await ctx.send(_("Command Not Found"))
    else:
        builders = [_("PitsaBot 0.1A Pre-Release")]
        cogs = Bot.cogs
        for cog in cogs:
            cog_desc = help_parser_3000(cog)
            builders.append(f"\n{cog_desc[0]} - {cog_desc[1]}")
            for command in cogs[cog].get_commands():
                if not command.hidden:
                    descriptions = help_parser_3000(command)
                    cbuilder = f"{command.name} " \
                               f"<{descriptions[3]}> [{descriptions[4]}] -> " \
                               f"{descriptions[5]}. {descriptions[1]}"
                    builders.append(cbuilder)
        await ctx.send("\n".join(builders))


@Bot.command()
async def about(ctx):
    builder = _(
        """
            Nice bot for all your needs.
            
              This bot wants to be analogue to that 2 or 3 usual bots you have
              on any server, with all their features in one monolithic bot. 
              Also, any features except API expensive(like auto-translating messages) 
              will be always free and not restricted (except when you restrict it by yourself)
              Also I (Creator) want it to be as simple as possible. 
              Licensed under GNU GPLv3, all source code available on GitHub: https://github.com/SergSel2006/PitsaBot
            """
    )
    await ctx.send(builder)


# bot launching
async def on_tick(tick: int = 5):
    while True:
        await asyncio.sleep(tick)
        try:
            if ping(Bot) > 2:
                to_thread(printw(f"High ping! {ping(Bot)} s"))
<<<<<<< HEAD:src/Core.py
            await cog_finder(
                Bot, pathlib.Path("src", "cogs")
            )  # should be before check_configs as after
=======
            cog_finder(Bot, pathlib.Path("cogs"))  # should be before check_configs as after
>>>>>>> main:Core.py
            # start we should synchronise our config files with cloud.
            check_configs(Bot)
        except Exception as e:
            exc_info = ''.join(traceback.format_exception(e))
            printw(f"error occured, ignoring!\n{exc_info}")


@Bot.event
async def on_ready():
    print(f"bot is ready, ping is {ping(Bot)} seconds")
    asyncio.ensure_future(on_tick())


# error handler for (almost) pretty error handling ;-)
async def on_error(ctx, error):
    lang = shared.load_server_language(ctx.message)
    _ = lang.gettext
    exc_info = ''.join(traceback.format_exception(error))
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(
            _("You don't have enough permissions for executing this command.")
        )
    elif "discord.errors.Forbidden" in exc_info:
        try:
            await ctx.guild.owner.dm_channel.send(
                _(
                    "I don't have enough permissions to do this. Giving bot role with Administator permission will solve all problems with permissions"
                )
            )
        except AttributeError:
            await ctx.guild.owner.create_dm()
            await ctx.guild.owner.dm_channel.send(
                _(
                    "I don't have enough permissions to do this. Giving bot role with Administator permission will solve all problems with permissions"
                )
            )

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(_("Command has not enough arguments. Use command help"))

    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(_("Command not found. Use help command."))
        print("{} issued wrong command".format(ctx.guild.id))
    elif isinstance(error, SystemExit):
        printc("shutting down, goodbye!")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(
            _(
                "You used incorrect arguments(check help for command), please notice that bot cannot do any calculations inside arguments"
            )
        )
    else:
        printw("error occured, ignoring!\n" + exc_info)


Bot.on_command_error = on_error
Bot.settings = settings
Bot.run(settings["token"])
