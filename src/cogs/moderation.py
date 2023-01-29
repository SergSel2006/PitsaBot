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

# Only for l10n marking puporses.
import gettext
import os
import pathlib

import discord
import shared

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

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        lang = shared.load_server_language(msg)
        _ = lang.gettext
        config = shared.find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                _("{0} Deleted a message. Content was:\n>>{1}").format(
                    msg.author.name, msg.content
                    )
                )

    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg):
        lang = shared.load_server_language(msg)
        _ = lang.gettext
        config = shared.find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                _(
                    "{0} Changed message. Content was:\n>>{1}\n"
                    "Content now:\n>>{2}"
                    ).format(
                    msg.author.name,
                    msg_before.content,
                    msg.content
                    )
                )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if isinstance(msg.channel, discord.abc.Messageable):
            config = shared.find_server_config(msg)
            if msg.mention_everyone and config["everyonetrigger"]:
                await msg.channel.send("TRIGGERED")


async def setup(bot):
    await bot.add_cog(Moderation(bot, pathlib.Path(os.getcwd())))
