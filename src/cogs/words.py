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

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

import gettext

import discord
from discord.ext import commands

from src import shared

_ = gettext.gettext


async def words(msg: discord.Message):
    translate = shared.load_server_language(msg).gettext
    config = shared.find_server_config(msg)
    words_ = config["words"]
    if words_["enabled"]:
        if msg.channel.id == words_["channel"]:
            target_word: str = msg.content.split(" ")[0].lower()
            target_word.rstrip(".,?!;:|\\/\"'%&@№")
            last_word = words_["last-word"]
            if target_word[0] != "#" and target_word and target_word != "#":
                if last_word != "":
                    if target_word not in words_["dictionary"] and \
                            target_word[0] == list(last_word)[-1] and \
                            msg.author.id != words_["last-counted-person"]:
                        words_["correct-count"] += 1
                        if words_["correct-count"] <= words_["huge"]:
                            await msg.add_reaction("✅")
                        else:
                            await msg.add_reaction("☑️")
                        words_["last-word"] = target_word
                        words_["dictionary"].append(target_word)
                        words_["last-counted-person"] = msg.author.id
                    else:
                        await msg.add_reaction("❌")
                        if words_["correct-count"] <= words_[
                            "huge"]:
                            await msg.channel.send(
                                translate(
                                    _(
                                        "{0} has written wrong word on {1}! "
                                        )
                                    ).format(
                                    msg.author.mention,
                                    words_["correct-count"]
                                    )
                                )
                        else:
                            await msg.channel.send(
                                translate(
                                    _(
                                        "NOOOOO! What s shame, {0} has "
                                        "written wrong word on {1} "
                                        "(AKA Big Number)!"
                                        )
                                    ).format(
                                    msg.author.mention,
                                    words_["correct-count"]
                                    )
                                )
                        words_["correct-count"] = 0
                        words_["dictionary"] = []
                        words_["last-word"] = ""
                        words_["last-counted-person"] = 0
                else:
                    words_["last-word"] = target_word
                    words_["correct-count"] = 1
                    words_["dictionary"].append(target_word)
                    words_["last-counted-person"] = msg.author.id
                    await msg.add_reaction("✅")
            if len(words_["dictionary"]) > 50:
                words_["dictionary"].pop(-1)
            config["words"] = words_
            shared.dump_server_config(msg, config)


class Words(commands.Cog):
    description = _("Module to play words.")

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    settings_attrs = {
        "name": _("wordsconfig"),
        "usage": _("<subcommand>"),
        "brief": _(
            "changes settings in game of words. use `help wordsconfig` "
            "for details."
            ),
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
    async def wordsconfig(self, ctx, mode, *options):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        match mode:
            case "enable":
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
            case "channel":
                if options[1].lower() != "this":
                    channel = ctx.message.channel_mentions[0]
                else:
                    channel = ctx.channel
                config["words"]["channel"] = channel.id

                await ctx.send(_("Words channel set"))
            case "disable":
                config["words"]["enabled"] = False
                await ctx.send(_("Words disabled"))
            case "big":
                config["words"]["huge"] = int(options[0])
                await ctx.send(
                    _("Big number is now {0}").format(
                        int(options[0])
                        )
                    )

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            await words(msg)


async def setup(bot):
    await bot.add_cog(Words(bot))
