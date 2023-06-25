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
import asyncio

import discord

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

import gettext
import shared

from discord.ext import commands

_ = gettext.gettext


class PollsCog(commands.Cog):
    description = _("Polls Made Easy!")
    
    def __init__(self, bot):
        self.bot = bot
    
    polls_attrs = {
        "name": _("polls"),
        "usage": _("<subcommand>"),
        "brief": _("manages polls. See full list of subcommands in the help"),
        "description": _(
            "WIP"
        )
    }
    
    @commands.command(**polls_attrs)
    @shared.can_manage_server()
    async def polls(self, ctx: commands.Context, mode):
        lang = shared.load_server_language(ctx.message)
        _ = lang.gettext
        config = shared.find_server_config(ctx.message)
        mode = mode.lower()
        match mode:
            case "add":
                try:
                    init_msg = await ctx.send(_(
                        "Configuring new poll.\nReply to this and next "
                        "configuration messages to configure"
                        " everything. Step 1: What is the question?"))
                    
                    def check_reply_to(msg, ctx):
                        def check(message: discord.Message):
                            if message.reference:
                                return message.reference.message_id == msg.id \
                                    and message.author.id == ctx.author.id
                        
                        return check
                    
                    reply = await ctx.bot.wait_for("message",
                                                   check=check_reply_to(
                                                       init_msg, ctx),
                                                   timeout=60)
                    header = reply.content
                    next_msg = await ctx.send(
                        _("Alright, your question will be "
                          "{0}. Step 2: How many answers "
                          "will you have? Reply with a "
                          "number of questions.").format(
                            header))
                    reactions_count = await ctx.bot.wait_for(
                        "message",
                        check=check_reply_to(next_msg, ctx), timeout=60)
                    reactions_count = int(reactions_count.content)
                    await ctx.send(_(
                        "You'll have {0} answers. Preparing "
                        "Step 3: configuring answers.").format(reactions_count)
                                   )
                    reactions = []
                    for i in range(reactions_count):
                        i += 1
                        await ctx.send(_("Configuring answer №{"
                                         "0}...").format(i))
                        target_msg = await ctx.send(
                            "React to this message with reaction you would like "
                            "to have on this answer"
                        )
                        
                        def rc(reaction, user):
                            return user.id == ctx.author.id
                        
                        reaction, unused = await ctx.bot.wait_for(
                            "reaction_add", check=rc, timeout=60)
                        reaction = reaction.emoji
                        target_msg = await ctx.send(_("Your reaction for this "
                                                      "answer will be {"
                                                      "0}. Now reply with the "
                                                      "actual answer content."
                                                      "").format(reaction))
                        contents = await ctx.bot.wait_for("message",
                                                          check=check_reply_to(
                                                              target_msg, ctx),
                                                          timeout=60)
                        contents = contents.content
                        await ctx.send(
                            _("Now you have answer №{0} which contents "
                              "{1} and accessible through reaction {"
                              "2}. Writing result...").format(
                                i, contents, reaction))
                        reactions.append((i, contents, reaction))
                    last_msg = await ctx.send(_(
                        "Everything is set up and ready to dispatch. Last step: "
                        "reply with the channel mention where you want to send "
                        "the poll."))
                    channel = await ctx.bot.wait_for(
                        "message", check=check_reply_to(last_msg, ctx),
                        timeout=60
                    )
                    channel = channel.channel_mentions[0]
                    last_open_poll = len(config["polls"])
                    poll_id = last_open_poll + 1  # I don't want the id be even
                    # more than 100. Just be the least from opened polls. Which
                    # might be some... strange...
                    builder = _("Poll №{0}!").format(poll_id)
                    builder += "\n" + header
                    for i in reactions:
                        builder += "\n" + str(i[0]) + ": " + i[1] \
                                   + " ({0}).".format(i[2])
                    msg = await channel.send(builder)
                    for i in reactions:
                        await msg.add_reaction(i[2])
                    config["polls"].append((poll_id, msg.id))
                    shared.dump_server_config(ctx.message, config)
                except asyncio.TimeoutError:
                    await ctx.send("You have been inactive for a while... "
                                   "Cancelling creating a poll")


async def setup(bot):
    await bot.add_cog(PollsCog(bot))
