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
import random
import sqlite3

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
            pathlib.Path("locales", f"{lang}.yml"), "r",
            encoding="utf8"
    ) as lang:
        lang = yaml.load(lang, Loader=Loader)
        return lang


def find_server_config(message):
    with open(
            pathlib.Path(
                "..", "data", "servers_config", str(message.guild.id),
                "config.yml"
            ), "r", encoding="utf8"
    ) as config:
        config = yaml.load(config, Loader=Loader)
        return config


def connect():
    try:
        connection = sqlite3.connect(pathlib.Path("data", "MainDB.sqlite3"))
        return connection
    except sqlite3.Error as e:
        return e


def execute(conn: sqlite3.Connection, command, args: tuple):
    try:
        cursor = conn.cursor()
        cursor.execute(command, args)
        conn.commit()
        return cursor
    except sqlite3.Error as e:
        return e


class Job:
    def __init__(self, name, min_salary, max_salary):
        self.name = name
        self.min_salary = int(min_salary)
        self.max_salary = int(max_salary)

    def work(self):
        return random.randint(self.min_salary, self.max_salary)

    def __str__(self):
        return self.name


class EconomyCog(commands.Cog):
    def __init__(self, bot, cwd: pathlib.Path):
        self.bot = bot
        self.cwd = cwd
        self.connection = connect()

    @commands.Command
    async def check_balance(self, ctx):
        language = load_server_language(ctx.message)
        conn = self.connection
        id = ctx.message.author.id
        command = """SELECT * FROM balance WHERE uid=?"""
        async with ctx.channel.typing():
            cur = execute(conn, command, (id,))
            if isinstance(cur, sqlite3.Error):
                raise cur
            bal = cur.fetchone()
            if not bal:
                command = """INSERT INTO balance VALUES (?, 0)"""
                execute(conn, command, (id,))
                bal = [id, 0]
            await ctx.send(
                language["misc"]["balance"].replace(
                    "$BAL",
                    str(bal[1])
                )
            )

    async def work(self, ctx):
        pass


def setup(bot):
    bot.add_cog(EconomyCog(bot, pathlib.Path(os.getcwd())))
