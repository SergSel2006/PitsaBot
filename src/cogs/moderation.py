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
import os
import pathlib

import discord

from src import shared

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

from discord.ext import commands

_ = gettext.gettext


def is_moderator(ctx, man=None):
    config = shared.find_server_config(ctx.message)
    roles = ctx.author.roles if man is None else man.roles
    modroles = config["modroles"]
    for role in roles:
        if role.id in modroles:
            return True
    perms: discord.Permissions = ctx.author.top_role.permissions
    if (
            perms.administrator or perms.ban_members
            or perms.kick_members or ctx.author.id == ctx.guild.owner_id
    ):
        return True
    else:
        return False


class Moderation(commands.Cog):
    description = _("everything any moderator should like")

    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    ban_attrs = {
        "name": _("ban"),
        "usage": _("<user, reason>"),
        "brief": _("bans person"),
        "description": _(
            "Use to ban <user>. To prevent non-reason bans "
            "<reason> is required"
            )
        }

    @commands.command(**ban_attrs)
    @commands.check(is_moderator)
    async def ban(self, ctx, man: discord.Member, reason):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        if not is_moderator(ctx, man) and man.id != self.bot.user.id:
            await man.ban(reason=reason)
            await ctx.send(
                _("{0} has been banned from the server").format(man.name)
                )
        else:
            await ctx.send(_("cannot mute, kick or ban moderators and myself"))

    purge_attrs = {
        "name": _("purge"),
        "usage": _("<amount> [user]"),
        "brief": _("cleans chat from messages"),
        "description": _(
            "Removes <amount> messages, if [user] is present, "
            "clean messages only by this user"
            )
        }

    @commands.command(**purge_attrs)
    @commands.check(is_moderator)
    async def purge(self, ctx, count=1, man: discord.Member = None):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext

        def is_user(message):
            if man is not None:
                return message.author == man
            else:
                return True

        await ctx.message.delete()
        count = await ctx.channel.purge(
            limit=count, check=is_user,
            bulk=True
            )
        msg = await ctx.send(
            _("{0} messages was purged").format(str(len(count)))
            )
        await msg.delete(delay=5)

    kick_attrs = {
        "name": _("kick"),
        "usage": _("<user, reason>"),
        "brief": _("kicks person"),
        "description": _(
            "Use to kick <user>. To prevent non-reason kicks "
            "<reason> is required"
            )
        }

    @commands.command(**kick_attrs)
    @commands.check(is_moderator)
    async def kick(self, ctx, man: discord.Member, reason):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        if not reason:
            await ctx.send(_("Cannot kick without reason"))
        else:
            if not is_moderator(ctx, man) and man.id != self.bot.user.id:
                await man.kick(reason=reason)
                await ctx.send(
                    _("{0} has been kicked from the server.").format(man.name)
                    )
            else:
                await ctx.send(_("cannot mute, kick or ban moderators"))

    settings_attrs = {
        "name": _("modconfig"),
        "usage": _("<subcommand>"),
        "brief": _(
            "changes moderation settings. use `help config` for "
            "details."
            ),
        "description": _(
            "Available subcommands:"
            "\n  modrole <add/remove moderator's roles>"
            "\n  modlog <enable/channel (this)/disable>"
            )
        }

    @commands.command(**settings_attrs)
    @shared.can_manage_server()
    async def modconfig(self, ctx, mode, *options):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        match mode:
            case "modrole":
                roles = ctx.message.role_mentions
                if options:
                    match options[0].lower():
                        case "add:":
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
                        case "remove":
                            for role in roles:
                                if role.id in config["modroles"]:
                                    config["modroles"].remove(role.id)
                                else:
                                    await ctx.send(
                                        _("{0} is not a moderator").format(
                                            role.mention
                                            )
                                        )
                            await ctx.send(
                                _("Roles was removed from moderators")
                                )
                else:
                    await ctx.send(
                        " ".join(
                            [ctx.guild.get_role(i).mention for i
                             in config["modroles"]]
                            )
                        )
            case "modlog":
                match options[0].lower():
                    case "enable":
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
                    case "channel":
                        if options[1].lower() != "this":
                            channel = ctx.message.channel_mentions[0]
                        else:
                            channel = ctx.channel
                        config["modlog"]["channel"] = channel.id
                        await ctx.send(_("Moderation log channel set"))
                    case "disable":
                        config["modlog"]["enabled"] = False
                        await ctx.send(_("Moderation log disabled"))
        shared.dump_server_config(ctx.message, config)

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        lang = shared.load_server_language(msg)
        _ = lang.gettext
        config = shared.find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            qual_name = msg.author.name + "#" + msg.author.discriminator
            embed = discord.Embed(color=0xE74C3C)
            embed.set_author(
                name=qual_name + _(" Deleted message"),
                icon_url=msg.author.display_avatar.url
                )
            embed.add_field(
                name=_("Content was:"), value=msg.content,
                inline=False
                )
            embed.add_field(
                name=_("At channel:"), value=msg.channel.mention,
                inline=False
                )
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg):
        lang = shared.load_server_language(msg)
        _ = lang.gettext
        config = shared.find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            qual_name = msg.author.name + "#" + msg.author.discriminator
            embed = discord.Embed(color=0xF7DC6F)
            embed.set_author(
                name=qual_name + _(" Changed message"),
                icon_url=msg.author.display_avatar.url
                )
            embed.add_field(
                name=_("Content was:"), value=msg_before.content,
                inline=False
                )
            embed_added = len(msg_before.embeds) < len(msg.embeds)
            embed.add_field(
                name=_("Content now:"), value=msg.content + (_(
                    " (new embed(s))."
                    )
                                                             if embed_added else ""
                                                             ),
                inline=False
                )
            embed.add_field(
                name=_("At channel:"), value=msg.channel.mention,
                inline=False
                )
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if isinstance(msg.channel, discord.abc.Messageable):
            config = shared.find_server_config(msg)
            if msg.mention_everyone and config["everyonetrigger"]:
                await msg.channel.send("TRIGGERED")


async def setup(bot):
    await bot.add_cog(Moderation(bot, pathlib.Path(os.getcwd())))
