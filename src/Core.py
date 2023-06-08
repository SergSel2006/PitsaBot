#  Copyright (c) 2022-2023 SergSel2006 (Sergey Selivanov).
#
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
import datetime
import gettext
import logging
import pathlib
import sys
import traceback

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

_ = gettext.gettext

# logger (replaces print)
# Beautiful color formatting


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
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
        for i in set(dict2.keys()).difference(dict1.keys()):
            if type(dict2[i]) == dict and i in dict1.keys():
                dict1[i], other_same = diff(dict1[i], dict2[i])
                same = other_same if same else False
            elif type(dict2[i]) == dict:
                dict1[i] = dict2[i]
                same = False
        for i in set(dict1.keys()).difference(dict2.keys()):
            del dict1[i]
            same = False
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
                    config, correct = diff(config, temp_dict)
                if not correct:
                    with open(
                            config_path, mode='w', encoding='utf8'
                            ) as config_raw:
                        yaml.dump(config, config_raw, Dumper)
                        print(f"Changed config file of {guild.name}")
            temp.seek(0)


# server prefix finder, if no prefix, return mention of a bot
def server_prefix(bot: commands.Bot, message: discord.Message):
    if isinstance(message.channel, (discord.TextChannel, discord.Thread)):
        with open(
                pathlib.Path(
                    "data", "servers_config", str(message.guild.id),
                    "config.yml"
                    ), "r"
                ) as config:
            try:
                config: dict = yaml.load(config, Loader)
                prefix: str = config["prefix"]
                if prefix:
                    return prefix
                else:
                    return bot.user.mention + ' '
            except ValueError:
                return bot.user.mention + ' '
    else:
        return bot.user.mention + ' '


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


# ping that returns seconds of latency
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


class TranslatableHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        translate = shared.load_server_language(self.context.message).gettext
        destination = self.get_destination()
        help_payload = "PitsaBot v0.2a\nMade by SergSel2006, idea by cool " \
                       "people from Russian Rec Room\nAvailable commands" \
                       " and modules:\n"
        for cog in mapping.keys():
            cog: commands.Cog
            if cog is None:
                help_payload += "Built-in" + ":\n"
                for command in mapping[None]:
                    if not command.hidden:
                        help_payload += str(
                            "- "
                            + (translate(command.name) if
                               command.name else
                               command.qualified_name)
                            + " "
                            + (translate(command.usage) if
                               command.usage else "N/A")
                            + ": "
                            + (translate(command.brief)
                               if command.brief else
                               "N/A")
                            + "\n"
                            )
            else:
                help_payload += translate(cog.qualified_name)
                if any(cog.get_commands()):
                    help_payload += ":\n"
                    for command in mapping[cog]:
                        if not command.hidden:
                            help_payload += str(
                                "- "
                                + (translate(command.name) if
                                   command.name else
                                   command.qualified_name)
                                + " "
                                + (translate(command.usage) if
                                   command.usage else "N/A")
                                + ": "
                                + (translate(command.brief)
                                   if command.brief else
                                   "N/A")
                                + "\n"
                                )
                else:
                    help_payload += translate(_(" - No commands\n"))
        await destination.send(help_payload)

    async def send_cog_help(self, cog):
        translate = shared.load_server_language(self.get_destination()).gettext
        destination = self.get_destination()
        help_message = ''
        help_message += translate(cog.qualified_name) + " - " \
                        + translate(cog.description) + "\n"
        if any(filter(lambda x: not x.hidden, cog.get_commands())):
            help_message += translate(_("Available commands:\n"))
            for command in cog.walk_commands():
                if not command.hidden:
                    help_message += str(
                        "  - "
                        + (translate(command.name) if
                           command.name else
                           command.qualified_name)
                        + " "
                        + (translate(command.usage) if
                           command.usage else "N/A")
                        + ": "
                        + (translate(command.brief)
                           if command.brief else
                           "N/A")
                        + "\n"
                        )

        else:
            help_message += translate(_("No commands available"))
        await destination.send(help_message)

    async def send_command_help(self, command):
        translate = shared.load_server_language(self.get_destination()).gettext
        destination = self.get_destination()
        payload = ""
        if not command.hidden:
            payload += str(
                (translate(command.name) if
                 command.name else
                 command.qualified_name)
                + " "
                + (translate(command.usage) if
                   command.usage else "N/A")
                + ":\n"
                + (translate(command.description)
                   if command.description else
                   "N/A")
                + "\n"
                )
            await destination.send(payload)
        else:
            await destination.send(
                "This command is hidden and no help is "
                "here"
                )


@Bot.command(name=_("about"))
async def about(ctx):
    translate = shared.load_server_language(ctx.message).gettext
    builder = _(
        """
            Nice bot for all your needs.
            
              This bot wants to be analogue to that 2 or 3 usual bots you have
              on any server, with all their features in one monolithic bot. 
              Also, any features except API expensive
              (like auto-translating messages) will be always free
              and not restricted (except when you restrict it by yourself)
              Also I (Creator) want it to be as simple as possible. 
              Licensed under GNU GPLv3, all source code available on GitHub: 
              https://github.com/SergSel2006/PitsaBot
            """
        )
    await ctx.send(translate(builder))


@Bot.command(name=_("license"))
async def license(ctx, mode=None):
    translate = shared.load_server_language(ctx.message).gettext
    if mode is None:
        payload = _(
            "PitsaBot  Copyright (C) {}  SergSel2006 (Sergey Selivanov)\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details, "
            "use 'licence w'.\n"
            "This is free software, and you are welcome to redistribute it "
            "under certain conditions; use `license c' for details."
            )
        await ctx.send(translate(payload).format(datetime.date.today().year))
    elif mode == 'w':
        payload = _(
            '  15. Disclaimer of Warranty.\n'
            '  THERE IS NO WARRANTY FOR THE PROGRAM, '
            'TO THE EXTENT PERMITTED BY '
            'APPLICABLE LAW.  EXCEPT WHEN OTHERWISE '
            'STATED IN WRITING THE COPYRIGHT '
            'HOLDERS AND/OR OTHER PARTIES PROVIDE '
            'THE PROGRAM "AS IS" WITHOUT WARRANTY '
            'OF ANY KIND, EITHER EXPRESSED OR IMPLIED, '
            'INCLUDING, BUT NOT LIMITED TO, '
            'THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS '
            'FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY '
            'AND PERFORMANCE OF THE PROGRAM '
            'IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME '
            'THE COST OF '
            'ALL NECESSARY SERVICING, REPAIR OR CORRECTION.'
            )
        await ctx.send(translate(payload))
    elif mode == 'c':
        payload = _(
            '  16. Limitation of Liability.\n'
            '  IN NO EVENT UNLESS REQUIRED '
            'BY APPLICABLE LAW OR AGREED TO IN WRITING '
            'WILL ANY COPYRIGHT HOLDER, OR ANY OTHER '
            'PARTY WHO MODIFIES AND/OR CONVEYS '
            'THE PROGRAM AS PERMITTED ABOVE, BE '
            'LIABLE TO YOU FOR DAMAGES, INCLUDING ANY '
            'GENERAL, SPECIAL, INCIDENTAL OR '
            'CONSEQUENTIAL DAMAGES ARISING OUT OF THE '
            'USE OR INABILITY TO USE THE PROGRAM '
            '(INCLUDING BUT NOT LIMITED TO LOSS OF '
            'DATA OR DATA BEING RENDERED INACCURATE '
            'OR LOSSES SUSTAINED BY YOU OR THIRD '
            'PARTIES OR A FAILURE OF THE PROGRAM '
            'TO OPERATE WITH ANY OTHER PROGRAMS), '
            'EVEN IF SUCH HOLDER OR OTHER PARTY '
            'HAS BEEN ADVISED OF THE POSSIBILITY OF '
            'SUCH DAMAGES.'
            )
        await ctx.send(translate(payload))


# bot launching
async def on_tick(tick: int = 10):
    while True:
        await asyncio.sleep(tick)
        try:
            if ping(Bot) > 2:
                printw(f"High ping! {ping(Bot)} s")
            await cog_finder(Bot, pathlib.Path("src", "cogs"))
            check_configs(Bot)
        except Exception as e:
            exc_info = ''.join(traceback.format_exception(e))
            printw(f"error occurred, ignoring!\n{exc_info}")


@Bot.event
async def on_ready():
    print(f"bot is ready, ping is {ping(Bot)} seconds")
    activity = discord.Game(name="Github")
    await Bot.change_presence(activity=activity, status=discord.Status.online)
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
                    "I don't have enough permissions to do this. "
                    "Giving bot role with Administrator permission will "
                    "solve all problems with permissions"
                    )
                )
        except AttributeError:
            await ctx.guild.owner.create_dm()
            await ctx.guild.owner.dm_channel.send(
                _(
                    "I don't have enough permissions to do this. "
                    "Giving bot role with Administrator permission will "
                    "solve all problems with permissions"
                    )
                )

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(_("Command has not enough arguments. Use command help"))

    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(_("Command not found. Use help command."))
        print("{} issued wrong command".format(ctx.guild.id))
    elif isinstance(error, SystemExit):
        print("shutting down, goodbye!")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send(
            _(
                "You used incorrect arguments(check help for command), "
                "please notice that bot cannot do any calculations inside "
                "arguments"
                )
            )
    else:
        printw("error occured, ignoring!\n" + exc_info)


Bot.on_command_error = on_error
Bot.settings = settings
help_attrs = {
    "name": _("help"),
    "brief": _("shows this message."),
    "usage": _("[command or module]"),
    "description": _("totally made for helping you!"),
    }
Bot.help_command = TranslatableHelp(command_attrs=help_attrs)
Bot.run(settings["token"])
