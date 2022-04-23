# ##################################################################################################
#  Copyright (c) 2022.                                                                             #
#        This program is free software: you can redistribute it and/or modify                      #
#        it under the terms of the GNU General Public License as published by                      #
#        the Free Software Foundation, either version 3 of the License, or                         #
#        (at your option) any later version.                                                       #
#                                                                                                  #
#        This program is distributed in the hope that it will be useful,                           #
#        but WITHOUT ANY WARRANTY; without even the implied warranty of                            #
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                             #
#        GNU General Public License for more details.                                              #
#                                                                                                  #
#        You should have received a copy of the GNU General Public License                         #
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.                    #
# ##################################################################################################

import os
import pathlib

import discord

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

import yaml
from discord.ext import commands


def load_server_language(message):
    config = find_server_config(message)
    language = load_language(config["language"])
    return language


def load_language(lang):
    with open(
            pathlib.Path("data", "languages", f"{lang}.yml"), "r",
            encoding="utf8"
    ) as lang:
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


def is_moderator(ctx, man=None):
    config = find_server_config(ctx.message)
    roles = ctx.author.roles if man is None else man.roles
    modroles = config["modroles"]
    for role in roles:
        if role.id in modroles:
            return True
    perms: discord.Permissions = ctx.author.top_role.permissions
    if perms.administrator or perms.ban_members or perms.kick_members or \
            ctx.author.id == ctx.guild.owner_id:
        return True
    else:
        return False


class ModCog(commands.Cog):
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd

    @commands.Command
    @commands.check(is_moderator)
    async def ban(self, ctx, man: discord.Member, *, reason=None):
        language = load_server_language(ctx.message)
        if not reason:
            await ctx.send(language["misc"]["ban_no_reason"])
        else:
            if not is_moderator(ctx, man) and man.id != self.bot.user.id:
                await man.ban(reason=reason)
                await ctx.send(
                    language["misc"]["ban_success"].replace(
                        "$USER",
                        man.name
                    )
                )
            else:
                await ctx.send(language["misc"]["no_moderator"])

    @commands.Command
    @commands.check(is_moderator)
    async def purge(self, ctx, count=1, man: discord.Member = None):
        language = load_server_language(ctx.message)

        def is_user(message):
            if man is not None:
                return message.author == man
            else:
                return True

        await ctx.message.delete()
        count = await ctx.channel.purge(limit=count, check=is_user,
                                        bulk=True)
        msg = await ctx.send(language["misc"]["purged"].replace("$COUNT",
                                                                str(len(
                                                                    count))))
        await msg.delete(delay=5)

    @commands.Command
    @commands.check(is_moderator)
    async def unban(self, ctx, man: discord.Member):
        language = load_server_language(ctx.message)
        await man.unban()
        await ctx.send(
            language["misc"]["unban_success"].replace(
                "$USER",
                man.name
            )
        )

    @commands.Command
    @commands.check(is_moderator)
    async def kick(self, ctx, man: discord.Member, *, reason=None):
        language = load_server_language(ctx.message)
        if not reason:
            await ctx.send(language["misc"]["kick_no_reason"])
        else:
            if not is_moderator(ctx, man) and man.id != self.bot.user.id:
                await man.kick(reason=reason)
                await ctx.send(
                    language["misc"]["kick_success"].replace(
                        "$USER",
                        man.name
                    )
                )
            else:
                await ctx.send(language["misc"]["no_moderator"])

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        lang = load_server_language(msg)
        config = find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                lang["misc"]["deleted_message"].replace(
                    "$USER", msg.author.name
                ).replace("$MESSAGE", msg.content)
            )

    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg):
        lang = load_server_language(msg)
        config = find_server_config(msg)
        if config["modlog"]["enabled"] and msg.author != self.bot.user:
            ch = self.bot.get_channel(config["modlog"]["channel"])
            await ch.send(
                lang["misc"]["changed_message"].replace(
                    "$USER", msg.author.name
                ).replace(
                    "$OLD_MESSAGE", msg_before.content
                ).replace(
                    "$NEW_MESSAGE",
                    msg.content
                )
            )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if isinstance(msg.channel, discord.abc.GuildChannel):
            config = find_server_config(msg)
            if msg.mention_everyone and config["everyonetrigger"]:
                await msg.channel.send("TRIGGERED")


def setup(bot):
    bot.add_cog(ModCog(bot, pathlib.Path(os.getcwd())))
