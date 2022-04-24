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

# A cog that does nothing, mustn't be loaded.
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader as Loader
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper as Dumper

from discord.ext import commands


class TemplateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Command
    async def template_command(self, ctx, arg):
        pass

    @commands.Cog.listener()
    async def template_event(self):
        pass


def setup(bot):
    bot.add_cog(TemplateCog(bot))
