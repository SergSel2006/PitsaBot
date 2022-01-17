#  Copyright (C) 2021  SergSel2006
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

# A simple cog file metaclass used for making loading, unloading and reloading
# cogs easier. Also makes pretty names by adding __str__, __repr__ and name
import os
import pathlib

from discord.ext import commands


class Cog_File_Meta:
    def __init__(self, bot: commands.Bot, cog_path: pathlib.Path, name=None):
        self.bot = bot
        self.path = cog_path
        if not name:
            self.name = cog_path.stem
        else:
            self.name = name
        self.active = False

    def __str__(self):
        return f"Cog_File_Meta Class of {self.path}"

    def __repr__(self):
        return f"Cog_File_Meta Class of {self.path}"

    def load(self):
        bot = self.bot
        try:
            bot.load_extension(str(self.path).removesuffix(".py").replace(
                "\\" if
                os.name ==
                "nt" else "/", "."))
            self.active = True
            return f"Success loading of {self.name} cog"
        except commands.errors.ExtensionAlreadyLoaded:
            return "Cog already loaded"
        except commands.errors.ExtensionNotFound:
            del self
            return "Cog not found, deleting meta"
        except Exception as e:
            raise e

    def unload(self):
        bot = self.bot
        try:
            bot.unload_extension(str(self.path).removesuffix(".py").replace(
                "\\" if
                os.name ==
                "nt" else "/", "."))
            self.active = False
            return f"Success unloading of {self.name} cog"
        except commands.errors.ExtensionNotLoaded:
            return "Cog already unloaded"
        except commands.errors.ExtensionNotFound:
            del self
            return "Cog not found, deleting meta"
        except Exception as e:
            raise e

    def reload(self):
        bot = self.bot
        try:
            bot.reload_extension(str(self.path).removesuffix(".py").replace(
                "\\" if os.name == "nt" else "/", "."
            )
            )
            return f"Success reloading of {self.name} cog"
        except commands.errors.ExtensionNotLoaded:
            return "Cog was not loaded"
        except commands.errors.ExtensionNotFound:
            del self
            return "Cog not found, deleting meta"
        except Exception as e:
            raise e

    def self_check(self):
        return self.path.exists()
