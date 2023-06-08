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


try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

import gettext

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
    async def polls(self, ctx):
        pass


async def setup(bot):
    await bot.add_cog(PollsCog(bot))
