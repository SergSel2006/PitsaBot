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

import gettext
import pathlib
import traceback

import shared
import yaml
from discord.ext import commands

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

_ = gettext.gettext


def load_language(lang):
    with open(
            pathlib.Path("locales", f"{lang}.yml"), "r",
            encoding="utf8"
            ) as lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


def find_server_config(message):
    with open(
            pathlib.Path(
                "..", "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "r", encoding="utf8"
            ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


def dump_server_config(message, config):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "w", encoding="utf8"
            ) as config_file:
        yaml.dump(config, config_file, Dumper=Dumper)


def can_manage_channels():
    async def predicate(ctx):
        perms = ctx.author.top_role.permissions
        if (
                perms.manage_channels or perms.administrator
                or ctx.author.id == ctx.guild.owner_id
        ):
            return True
        else:
            return False

    return commands.check(predicate)


class Settings(commands.Cog):
    description = _("Configurations for bot")

    def __init__(self, bot):
        self.bot = bot

    settings_attrs = {
        "name": _("config"),
        "usage": _("<configuration of server>"),
        "brief": _("changes settings. use `help config` for details"),
        "description": _(
            "Changes bot's config. Available configs:"
            "\n prefix <prefix>"
            "\n modrole <add/remove moderator's roles>"
            "\n modlog <enable/channel (this)/disable>"
            "\n language <language>"
            "\n counting <enable/channel (this)/disable/big (number)>"
            )
        }

    @commands.command(**settings_attrs)
    @can_manage_channels()
    async def config(self, ctx, mode, *options):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        try:
            if mode == "prefix":
                if options:
                    if options[0] != "delete":
                        config['prefix'] = options[0]
                        await ctx.send(_("Prefix changed successfully."))
                    else:
                        config['prefix'] = ''
                        await ctx.send(
                            _(
                                "Prefix deleted successfully. Use a"
                                " @mention with whitespace to raise"
                                " a command"
                                )
                            )
                else:
                    await ctx.send(
                        _("Your prefix now is: .") +
                        config['prefix']
                        )
            elif mode == "modrole":
                roles = ctx.message.role_mentions
                if options:
                    if options[0].lower() == "add":
                        for role in roles:
                            if role.id not in config["modroles"]:
                                config["modroles"].append(role.id)
                            else:
                                await ctx.send(
                                    _("{0} already in list").format(
                                        role.mention
                                        )
                                    )
                        await ctx.send(_("Roles added to moderators"))
                    elif options[0].lower() == "remove":
                        for role in roles:
                            if role.id in config["modroles"]:
                                config["modroles"].remove(role.id)
                            else:
                                await ctx.send(
                                    _("{0} is not a moderator").format(
                                        role.mention
                                        )
                                    )
                        await ctx.send(_("Roles was removed from moderators"))
                else:
                    await ctx.send(
                        " ".join(
                            [ctx.guild.get_role(i).mention for i
                             in config["modroles"]]
                            )
                        )
            elif mode == "modlog":
                if options[0].lower() == "enable":
                    if config["modlog"]["channel"]:
                        config["modlog"]["enabled"] = True
                        await ctx.send(_("Moderation log enabled"))
                    else:
                        await ctx.send(
                            _(
                                "for activating moderation log, "
                                "you need to specify a channel first."
                                )
                            )
                elif options[0].lower() == "channel":
                    if options[1].lower() != "this":
                        channel = ctx.message.channel_mentions[0]
                    else:
                        channel = ctx.channel
                    config["modlog"]["channel"] = channel.id
                    await ctx.send(_("Moderation log channel set"))
                elif options[0].lower() == "disable":
                    config["modlog"]["enabled"] = False
                    await ctx.send(_("Moderation log disabled"))
            elif mode == "language":
                available = shared.lang_table.keys()
                if options[0] in available:
                    config["language"] = options[0]
                    await ctx.send(_("Language changed successfully"))
                else:
                    await ctx.send(_("Invalid language"))
            elif mode == "trigger":
                if options[0].lower() == "enable":
                    config["everyonetrigger"] = True
                else:
                    config["everyonetrigger"] = False
            elif mode == "react":
                if options[0].lower() == "enable":
                    config["react_to_pizza"] = True
                else:
                    config["react_to_pizza"] = False
            elif mode == "counting":
                if options[0].lower() == "enable":
                    if config["counting"]["channel"]:
                        config["counting"]["enabled"] = True
                        await ctx.send(_("Counting enabled"))
                    else:
                        await ctx.send(
                            _(
                                "for activating counting, "
                                "you need to specify a channel first."
                                )
                            )
                elif options[0].lower() == "channel":
                    if options[1].lower() != "this":
                        channel = ctx.message.channel_mentions[0]
                    else:
                        channel = ctx.channel
                    config["counting"]["channel"] = channel.id

                    await ctx.send(_("Counting channel set"))
                elif options[0].lower() == "disable":
                    config["counting"]["enabled"] = False

                    await ctx.send(_("Counting disabled"))
                elif options[0].lower() == "big":
                    config["counting"]["huge"] = int(options[1])
                    await ctx.send(
                        _("Big number is now {0}").format(
                            int(options[1])
                            )
                        )
            elif mode == "words":
                if options[0].lower() == "enable":
                    if config["words"]["channel"]:
                        config["words"]["enabled"] = True
                        await ctx.send(_("Words enabled"))
                    else:
                        await ctx.send(
                            _(
                                "for activating words, "
                                "you need to specify a channel first."
                                )
                            )
                elif options[0].lower() == "channel":
                    if options[1].lower() != "this":
                        channel = ctx.message.channel_mentions[0]
                    else:
                        channel = ctx.channel
                    config["words"]["channel"] = channel.id

                    await ctx.send(_("Words channel set"))
                elif options[0].lower() == "disable":
                    config["words"]["enabled"] = False

                    await ctx.send(_("Words disabled"))
                elif options[0].lower() == "big":
                    config["words"]["huge"] = int(options[1])
                    await ctx.send(
                        _("Big number is now {0}").format(
                            int(options[1])
                            )
                        )
            else:
                raise NotImplementedError(
                    "Configuration mode {0} Not Implemented".format(mode)
                    )
            dump_server_config(ctx.message, config)
        except Exception as e:
            await ctx.send(
                _(
                    "Oops! Something went wrong! If this happens too often,"
                    " send basic information about"
                    " what you've done and this code: {0} to issue tracker"
                    ).format(ctx.guild.id)
                )
            exc_info = ''.join(traceback.format_exception(e))
            shared.printe(
                "While configuring {0}, error occured and ignored."
                "\n{1}".format(ctx.guild.id, exc_info)
                )


async def setup(bot):
    await bot.add_cog(Settings(bot))
