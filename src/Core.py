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
import gettext
import logging
import os
import pathlib
import sys
import traceback
from typing import Callable, Mapping, TypeGuard, Any

import discord
import json
from discord.ext import commands

from Cog_MetaFile import Cog_File_Meta

from shared import print, printd, printc, printw
import shared

_: Callable = gettext.gettext

# logger (replaces print)
# Beautiful color formatting


intents: discord.Intents = discord.Intents.default()
intents.members = True
intents.message_content = True
logger: logging.Logger = logging.getLogger('discord')
logger.setLevel(logging.INFO if "-d" not in sys.argv else logging.DEBUG)
handler: logging.FileHandler = logging.FileHandler(
    filename='Pitsa.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
)
logger.addHandler(handler)


# interesting functions
# config checker for up-to-date keys with template
async def check_configs(bot: commands.Bot) -> None:
    for guild in bot.guilds:
        await asyncio.sleep(0)
        guild_dir: pathlib.Path = pathlib.Path(
            "data", "servers_config", str(guild.id)
        )
        config_path: pathlib.Path = guild_dir / "config.yml"
        if not guild_dir.exists():
            print(
                f"added config for server {guild.name} with id {guild.id}"
            )
            guild_dir.mkdir()
            config_path.touch()
            conf = shared.DEFAULT_CONF.copy()
            langs = shared.lang_table.keys()
            if guild.preferred_locale in langs:
                conf["lang"] = guild.preferred_locale
            shared.dump_server_config(guild.id, conf)

        elif not config_path.exists():
            config_path.touch()


# server prefix finder, if no prefix, return mention of a bot
def server_prefix(bot: commands.Bot, message: discord.Message) -> str | tuple:
    if message.guild is not None:
        try:
            config: dict = shared.find_server_config(message.guild.id)
            prefix: str = config["prefix"]
            if prefix and bot.user:
                return bot.user.mention + ' ', prefix
            elif bot.user:
                return bot.user.mention + ' '
            else:
                return "p"
        except KeyError:
            if bot.user:
                return bot.user.mention + ' '
            else:
                return "p"
    elif bot.user:
        return bot.user.mention + ' '
    else:
        return "p"


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
            meta = Cogs.pop(cog)
            if meta.active:
                meta.unload()
            printd(f"cog {meta.name} was deleted")


# ping that returns seconds of latency
def ping(bot: commands.Bot) -> int:
    latency: float = bot.latency
    try:
        return int(round(latency * 1000) / 1000)
    except ValueError:
        return 0
    except OverflowError:
        printc(
            "Your bot cannot connect to discord! your internet or "
            "code issue?"
        )
        return 0


# check for a developer
async def owner_check(ctx: commands.Context) -> bool:
    return await Bot.is_owner(ctx.author)


# bot init


# cog list
Cogs: dict[str, Cog_File_Meta] = dict()

# intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# bot settings
def find_until_next_arg(string):
    return string.find("-")


conf_path: str | None = os.getenv("CONFIG_PATH")
settings: dict
config_loc: pathlib.Path
if conf_path:
    config_loc = pathlib.Path(conf_path)
else:
    config_loc = pathlib.Path().cwd() / "config.yml"
if len(sys.argv) > 2:
    if '--config' != sys.argv[1]:
        with config_loc.open('r') as o:
            settings = json.load(o)
        if not settings:
            raise ValueError("No Settings")
    else:
        settings = eval(
            " ".join(sys.argv[2:find_until_next_arg(" ".join(sys.argv[2:]))])
        )
else:
    with config_loc.open('r') as o:
        settings = json.load(o)
    if not settings:
        raise ValueError("No Settings")

# bot  itself


class CustomBot(commands.Bot):
    settings: dict = {}

    async def on_command_error(self, ctx: commands.Context,
                               error: Exception) -> None:
        lang: gettext.NullTranslations = shared.load_server_language(
            ctx.guild.id)
        _: Callable = lang.gettext
        exc_info: str = ''.join(traceback.format_exception(error))
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send(
                _("You don't have enough permissions "
                  "for executing this command.")
            )
        elif "discord.errors.Forbidden" in exc_info:
            guild: discord.Guild | None = ctx.guild
            if guild:
                owner = guild.owner
                if owner:
                    if not owner.dm_channel:
                        owner.create_dm()
                    else:
                        await owner.dm_channel.send(
                            _(
                                "I don't have enough permissions to do this. "
                                "Giving bot role with Administrator permission"
                                " will solve all problems with permissions"
                            )
                        )
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(_(
                "Command has not enough arguments."
                "Use command help"
            )
            )

        elif isinstance(error, commands.errors.CommandNotFound):
            await ctx.send(_("Command not found. Use help command."))
            guild = ctx.guild
            if guild:
                print("{} issued wrong command".format(guild.id))
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


Bot = CustomBot(
    command_prefix=server_prefix,
    intents=intents,
    owner_ids=settings["developers"]
)


# bot commands


# load_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def load_cog(ctx: commands.Context, cog: str) -> None:
    try:
        meta: Cog_File_Meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(await meta.load())


# unload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def unload_cog(ctx: commands.Context, cog: str) -> None:
    try:
        meta: Cog_File_Meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(await meta.unload())


# reload_cog command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def reload_cog(ctx: commands.Context, cog: str) -> None:
    try:
        meta: Cog_File_Meta = Cogs[cog]
    except KeyError:
        await ctx.send("Cog was not found!")
        return
    await ctx.send(await meta.reload())


# list_cogs command
@Bot.command(hidden=True)
@commands.check(owner_check)
async def list_cogs(ctx: commands.Context) -> None:
    all_cogs: str = '\n'.join([i.name for i in list(Cogs.values())])
    loaded_cogs: str = '\n'.join(
        [i.name for i in list(Cogs.values()) if i.active])
    builder: str = f"All cogs:\n{all_cogs}\nActive cogs:\n" \
        f"{loaded_cogs}"
    await ctx.send(builder)


# eval function (bad idea but with owner check it looks normal)
@Bot.command(hidden=True)
@commands.check(owner_check)
async def evaluate(ctx: commands.Context) -> None:
    try:
        locals_before: dict
        locals_after: dict
        if len(ctx.message.content.split(" ")) > 1:
            command: str = " ".join(ctx.message.content.split(" ")[1:])
            compiled_code: Any = compile(command, 'in_code', mode="exec")
            locals_before = locals().copy()
            exec(compiled_code)
            locals_after = locals().copy()
            locals_after.pop("locals_before")
            if locals_after != locals_before:
                diff: set = set(locals_after) - set(locals_before)
                for i in diff:
                    await ctx.send(i + " = " + str(locals_after[i]))

                pass
        elif ctx.message.attachments is not None:
            attach: discord.Attachment = ctx.message.attachments[0]
            assert attach.content_type is not None
            if "text" in attach.content_type:
                data: str = (await attach.read()).decode("utf-8")
                locals_before = locals().copy()
                exec(compile(data, 'in_code', mode="exec"))
                locals_after = locals().copy()
                locals_after.pop("locals_before")
                if locals_after != locals_before:
                    result: set = set(locals_before) - set(locals_after)
                    if result is not None:
                        for i in result:
                            await ctx.send(i + " = " + str(locals_after[i]))
    except Exception as e:
        await ctx.send(''.join(traceback.format_exception(e)))


# config command itself
settings_attrs: dict = {
    "name": _("sysconfig"),
    "usage": _("<subcommand>"),
    "brief": _(
        "changes server core settings. use `help sysconfig` for "
        "details."
    ),
    "description": _(
        "Available subcommands:"
        "\n  prefix <prefix>"
        "\n  language <language>"
    )
}


@Bot.command(**settings_attrs)
@shared.can_manage_server()
async def sysconfig(ctx: commands.Context, mode: str, *options) -> None:
    lang: gettext.NullTranslations = shared.load_server_language(
        ctx.guild.id)
    _ = lang.gettext
    config: dict = shared.find_server_config(ctx.guild.id)
    mode = mode.lower()
    match mode:
        case "prefix":
            if options:
                match options[0]:
                    case "delete":
                        config['prefix'] = None
                        await ctx.send(
                            _(
                                "Prefix deleted successfully. Use a"
                                " @mention with whitespace to raise"
                                " a command"
                            )
                        )
                    case _:
                        config['prefix'] = "".join(options)
                        await ctx.send(_("Prefix changed successfully."))
            else:
                await ctx.send(
                    _("Your prefix now is: ") +
                    config['prefix']
                )
        case "language":
            available = shared.lang_table.keys()
            if options[0] in available:
                config["language"] = options[0]
                await ctx.send(_("Language changed successfully"))
            else:
                await ctx.send(_("Invalid language"))
        case _:
            await ctx.send(
                _(
                    "Invalid subcommand, use `help sysconfig` to see "
                    "available subcommands"
                )
            )
    shared.dump_server_config(ctx.guild.id, config)


class TranslatableHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping: Mapping) -> None:
        translate: Callable = shared.load_server_language(
            self.context.guild.id).gettext
        destination: discord.abc.Messageable = self.get_destination()
        help_payload: str = translate(
            _(
                "{0} {1}\nMade by SergSel2006, idea by "
                "cool "
                "people from Russian Rec Room\nAvailable commands"
                " and modules:\n"
            )
        ).format(shared.NAME, shared.VERSION)
        cog: commands.Cog
        for cog in mapping.keys():
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

    async def send_cog_help(self, cog) -> None:
        translate: Callable = shared.load_server_language(
            self.get_destination().guild.id).gettext
        destination: discord.abc.Messageable = self.get_destination()
        help_message: str = ''
        help_message += translate(cog.qualified_name) + " - " \
            + translate(cog.description) + "\n"
        # This is required to avoid mypy about complaining
        # that `filter` function gets wrong argument

        def not_hidden(x) -> TypeGuard[bool]:
            return not x.hidden
        if any(filter(not_hidden, cog.get_commands())):
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

    async def send_command_help(self, command) -> None:
        translate: Callable = shared.load_server_language(
            self.get_destination().guild.id).gettext
        destination: discord.abc.Messageable = self.get_destination()
        payload: str = ""
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
async def about(ctx: commands.Context):
    translate: Callable = shared.load_server_language(
        ctx.guild.id).gettext
    builder: str = _(
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
async def license(ctx: commands.Context, mode: str | None = None) -> None:
    translate: Callable = shared.load_server_language(ctx.guild.id).gettext
    payload: str
    match mode:
        case 'w':
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
        case'c':
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
        case _:
            payload = _(
                "{0}  Copyright (C)  SergSel2006 (Sergey Selivanov)\n"
                "This program comes with ABSOLUTELY NO WARRANTY; for details, "
                "use 'licence w'.\n"
                "This is free software, "
                "and you are welcome to redistribute it "
                "under certain conditions; use `license c' for details."
            ).format(shared.NAME)
            await ctx.send(translate(payload))


# bot launching
async def on_tick(tick: int = 10) -> None:
    while True:
        await asyncio.sleep(tick)
        try:
            if ping(Bot) > 2:
                printw(f"High ping! {ping(Bot)} s")
            await cog_finder(Bot, pathlib.Path("src", "cogs"))
            await check_configs(Bot)
        except Exception as e:
            exc_info = ''.join(traceback.format_exception(e))
            printw(f"error occurred, ignoring!\n{exc_info}")


@Bot.event
async def on_ready() -> None:
    print(f"bot is ready, ping is {ping(Bot)} seconds")
    activity = discord.Game(name="Github")
    await Bot.change_presence(activity=activity, status=discord.Status.online)
    asyncio.create_task(on_tick())

Bot.settings = settings
help_attrs: dict = {
    "name": _("help"),
    "brief": _("shows this message."),
    "usage": _("[command or module]"),
    "description": _("totally made for helping you!"),
}
Bot.help_command = TranslatableHelp(command_attrs=help_attrs)
Bot.run(settings["token"])
