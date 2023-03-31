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

import pathlib

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
import discord
import gettext
import shared

_ = gettext.gettext


def dump_server_config(message, config):
    with open(
            pathlib.Path(
                "data", "servers_config", str(message.guild.id),
                "config.yml"
                ), "w", encoding="utf8"
            ) as config_file:
        yaml.dump(config, config_file, Dumper=Dumper)


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
            dump_server_config(msg, config)


class Words(commands.Cog):
    description = _("Module to play words.")

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            await words(msg)


async def setup(bot):
    await bot.add_cog(Words(bot))
