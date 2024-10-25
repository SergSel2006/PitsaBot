#  Copyright (c) 2023 SergSel2006 (Sergey Selivanov).
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

import discord
import shared
from discord.ext import commands

_ = gettext.gettext


async def counting(msg: discord.Message):
    config = shared.find_server_config(msg.id)
    if not config["counting"]["enabled"]:
        return
    if msg.channel.id != config["counting"]["channel"]:
        return
    counting_ = config["counting"]
    translate = shared.load_server_language(msg.id).gettext
    target_message: str = msg.content.split(" ")[0]
    test_str = [i in "0123456789.()/*-+%" for i in target_message]
    if all(test_str):
        number = int(eval(target_message))
    else:
        return
    if number == int(counting_["number"]) + 1 and \
            msg.author.id != counting_["last-counted-person"]:
        counting_["number"] = number
        if counting_["number"] <= counting_["huge"]:
            await msg.add_reaction("✅")
        else:
            await msg.add_reaction("☑️")
        counting_["last-counted-person"] = msg.author.id
    else:
        await msg.add_reaction("❌")
        if counting_["number"] <= counting_["huge"]:
            await msg.channel.send(
                translate(
                    _(
                        "{0} Failed count on {1}! "
                        "Starting from 1 again..."
                    )
                ).format(
                    msg.author.mention, counting_["number"]
                )
            )
        else:
            await msg.channel.send(
                translate(
                    _(
                        "NOOOOO! What s shame, {0} Failed count on "
                        "{1} (AKA Big Number)!\n"
                        "Starting from 1 again..."
                    )
                ).format(
                    msg.author.mention, counting_["number"]
                )
            )
        counting_["number"] = 0
        counting_["last-counted-person"] = 0
    shared.dump_server_config(msg.id, config)


class Counting(commands.Cog):
    description = _("Module to make some counting.")

    def __init__(self, bot):
        self.bot = bot

    settings_attrs = {
        "name": _("countconfig"),
        "usage": _("<subcommand>"),
        "brief": _("changes settings. use `help countconfig` for details."),
        "description": _(
            "Available subcommands:"
            "\n  enable"
            "\n  channel (this)"
            "\n  disable"
            "\n  big (number)"
        )
    }

    @commands.command(**settings_attrs)
    @shared.can_manage_server()
    async def countconfig(self, ctx, mode, *options):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        match mode:
            case "enable":
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
            case "channel":
                if options[0].lower() != "this":
                    channel = ctx.message.channel_mentions[0]
                else:
                    channel = ctx.channel
                config["counting"]["channel"] = channel.id

                await ctx.send(_("Counting channel set"))
            case "disable":
                config["counting"]["enabled"] = False

                await ctx.send(_("Counting disabled"))
            case "big":
                config["counting"]["huge"] = int(options[0])
                await ctx.send(
                    _("Big number is now {0}").format(
                        int(options[0])
                    )
                )
        shared.dump_server_config(ctx.message, config)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            await counting(msg)

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        config = shared.find_server_config(msg.id)
        if not config["counting"]["enabled"]:
            return
        if msg.channel.id != config["counting"]["channel"]:
            return
        counting_ = config["counting"]
        translate = shared.load_server_language(msg.id).gettext
        if msg.author.id == counting_["last-counted-person"]:
            builder = translate(_("{0} Deleted the number.\nCurrent number is {1}")).format(
                msg.author.mention, counting_["number"])
            await msg.channel.send(builder)

    @commands.Cog.listener()
    async def on_message_edit(self, msg_, msg):
        config = shared.find_server_config(msg)
        if not config["counting"]["enabled"]:
            return
        if msg.channel.id != config["counting"]["channel"]:
            return
        counting_ = config["counting"]
        translate = shared.load_server_language(msg).gettext
        if msg.author.id == counting_["last-counted-person"]:
            builder = translate(_("{0} Changed the message.\nCurrent number is {1}. (Just in case)")).format(
                msg.author.mention, counting_["number"])
            await msg.channel.send(builder)


async def setup(bot):
    await bot.add_cog(Counting(bot))
