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
import pathlib
from datetime import datetime
import sqlite3

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


def connect(ctx):
    """High-level function to connect to config-specific database"""
    config = find_server_config(ctx.message)
    global_db = config["global_db"]
    try:
        if global_db:
            connection = sqlite3.connect(pathlib.Path("data",
                                                      "MainMainDB.sqlite3"))
            return connection
        else:
            server_db_path = pathlib.Path("data", ctx.server.id,
                                          "MainDB.sqlite3")
            connection = sqlite3.connect(server_db_path)
            return connection
    except sqlite3.Error as e:
        return e


def execute(conn: sqlite3.Connection, command: str, args: tuple = ()):
    """high-level function to execute sqlite commands and return cursor
    object for further work"""
    try:
        cursor = conn.cursor()
        cursor.execute(command, args)
        conn.commit()
        return cursor
    except sqlite3.Error as e:
        return e


class InfractionsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def warn(self, ctx, user: discord.User, reason=None):
        lang = load_server_language(ctx.message)
        conn = connect(ctx)
        if reason:
            execute(conn, "INSERT INTO infractions VALUES (?, ?, ?)",
                    (user.id, reason, datetime.now()))

            await ctx.send(lang["misc"]["warned"].format(user.name))

    @commands.command()
    async def check(self, ctx):
        lang = load_server_language(ctx.message)
        config = find_server_config(ctx.message)
        conn = connect(ctx)
        data = execute(conn, "SELECT * FROM infractions WHERE uid = "
                             "?").fetchall()
        local_or_global = config["global_db"]


def setup(bot):
    bot.add_cog(InfractionsCog(bot))
