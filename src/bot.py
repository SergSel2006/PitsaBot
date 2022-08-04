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

import logging
import os
import pathlib
import sys

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

intents = discord.Intents.default()
intents.members = True
con_logger = logging.getLogger("Bot")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]: %(message)s')
)
con_logger.addHandler(sh)
con_logger.setLevel(logging.INFO)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='Pitsa.log', encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s:'
        ' %(message)s'
    )
)
logger.addHandler(handler)

hibernated = False


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


async def check_configs(bot):
    for guild in bot.guilds:
        guild_folder = pathlib.Path("..", "data", "servers_config", str(guild.id))
        guild_config = pathlib.Path(
            "..", "data", "servers_config", str(guild.id),
            "config.yml"
        )
        if not guild_folder.exists():
            guild_folder.mkdir()
        if not guild_config.exists():
            con_logger.info(
                f"adding config for {guild.name} with id "
                f"{str(guild.id)}"
            )
            with open(
                    pathlib.Path(f"..", "data", "servers_config", "template.yml"),
                    "r"
            ) as template:
                with open(guild_config, "w+") as config:
                    for i in template.readlines():
                        config.write(i)
        else:
            with open(guild_config, "r") as config_raw:
                with open(
                        pathlib.Path(
                            f"..", "data", "servers_config", "template.yml"
                        ),
                        "r"
                ) as template:
                    config = yaml.load(config_raw, Loader)
                    template = yaml.load(template, Loader)

                    def dict_check(dict_for_check, template_dict):
                        for key in tuple(template_dict):
                            try:
                                if type(dict_for_check[key]) == dict:
                                    dict_check(
                                        dict_for_check[key], template_dict[
                                            key]
                                    )
                            except KeyError:
                                dict_for_check[key] = template_dict[key]

                        for key in tuple(dict_for_check):
                            try:
                                if type(dict_for_check[key]) == dict:
                                    dict_check(
                                        dict_for_check[key], template_dict[key]
                                    )
                            except KeyError:
                                del dict_for_check[key]

                            for key1 in tuple(template_dict):
                                try:
                                    if type(
                                            dict_for_check[key1]
                                    ) == dict:
                                        dict_check(
                                            dict_for_check[key1],
                                            template_dict[
                                                key1]
                                        )
                                except KeyError:
                                    dict_for_check[key1] = \
                                        template_dict[key1]

                    dict_check(config, template)

                    with open(guild_config, "w") as config_change:
                        yaml.dump(config, config_change, Dumper)


def server_prefix(bot, message):
    if isinstance(message.channel, discord.TextChannel):
        with open(
                pathlib.Path(
                    "..", "data", "servers_config",
                    str(message.guild.id), "config.yml"
                ),
                "r"
        ) as config:
            try:
                config = yaml.load(config, Loader)
                prefix = config["prefix"]
                return prefix
            except ValueError:
                return bot.user.mention
    else:
        return bot.user.mention


if '--config' != sys.argv[1]:
    with open('config.yml', 'r') as o:
        settings = yaml.load(o, Loader)
    if not settings:
        raise ValueError("No Settings")
else:
    settings = eval(sys.argv[2])

bot = commands.Bot(command_prefix=server_prefix, intents=intents)
bot.remove_command("help")

devs = settings['developers']
all_cogs = []
loaded_cogs = []


def heartbeat_check(bot):
    if bot.latency > 2:
        con_logger.warning(
            f"Can't keep up! Is the internet overloaded? "
            f"Running {round(bot.latency * 1000) / 1000} s."
        )


@bot.command(hidden=True)
async def load_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**Загружает новый ког в систему"""
    if ctx.message.author.id not in devs:
        await ctx.send(
            "Только Разработчики бота могут пользоваться этой командой"
        )
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) not in loaded_cogs:
                if "dev_" in cog:
                    await ctx.send(
                        "Коги, которые всё ещё в разработке"
                        " нестабильны! Бот может отключится"
                        " при загрузке такого кога!"
                    )
                try:
                    loading_cog = str(pathlib.Path(cog)).replace(
                        "\\" if os.name == "nt" else "/", "."
                    )
                    bot.load_extension(loading_cog)
                    loaded_cogs.append(pathlib.Path(cog))
                    await ctx.send("Ког " + cog + " успешно загружен!")
                except Exception as e:
                    await ctx.send(
                        "Ког " + cog + " Не был загружен!" + "\n" + str(e)
                    )
            else:
                await ctx.send('Ког уже загружен!')
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def unload_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**выключает бота из дискорда"""
    if ctx.message.author.id not in devs:
        await ctx.send(
            "Только Разработчики бота могут пользоваться этой командой"
        )
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) in loaded_cogs:
                try:
                    unloading_cog = str(pathlib.Path(cog)).replace(
                        "\\" if
                        os.name
                        == "nt"
                        else "/",
                        "."
                    )
                    bot.unload_extension(unloading_cog)
                    await ctx.send("Ког " + cog + " успешно выгружен!")
                    loaded_cogs.remove(pathlib.Path(cog))
                except Exception as e:
                    await ctx.send(
                        "Ког " + cog + " не был выгружен!" + "\n" + str(e)
                    )
            else:
                await ctx.send("Ког и так уже разгружен")
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def reload_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**перезагружает ког"""
    if ctx.message.author.id not in devs:
        await ctx.send(
            "Только Разработчики бота могут пользоваться этой командой"
        )
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) in loaded_cogs:
                try:
                    reloading_cog = str(pathlib.Path(cog)).replace(
                        "\\" if os.name == "nt" else "/", "."
                    )
                    bot.unload_extension(reloading_cog)
                    bot.load_extension(reloading_cog)
                    await ctx.send("Ког " + cog + " успешно перезагружен!")
                except Exception as e:
                    await ctx.send(
                        "Ког " + cog + " не был перезагружен!" + "\n" + str(e)
                    )
                    loaded_cogs.remove(pathlib.Path(cog))
            else:
                await ctx.send("сперва загрузите этот ког!")
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def list_cogs(ctx):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**даёт информацию о когах"""
    if ctx.message.author.id not in devs:
        await ctx.send(
            "Только Разработчики бота могут пользоваться этой командой"
        )
    else:
        await ctx.send("Активные коги:")
        for cog in loaded_cogs:
            await ctx.send(str(cog) + "\n")
        await ctx.send("Все Коги:")
        for cog in all_cogs:
            await ctx.send(str(cog) + "\n")
        await ctx.send("Общее количество когов: " + str(len(all_cogs)))


@bot.command(hidden=True)
async def shutdown(ctx):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**Вырубает бота"""
    if ctx.message.author.id not in devs:
        await ctx.send(
            "Только Разработчики бота могут пользоваться этой командой"
        )
    else:
        await ctx.send("Shutting Down...")
        await bot.close()
        sys.exit(0)


@bot.command(hidden=True)
async def hibernate(ctx):
    global hibernated
    hibernated = True


@bot.event
async def on_message(message: discord.Message):
    global hibernated
    if hibernated:
        prefix = await bot.get_prefix(message)
        message = await message.channel.history(limit=1).flatten()
        message = message[0]
        await bot.change_presence(status=discord.Status.idle)
        if message.content == prefix + "wakeup":
            hibernated = False
            await bot.change_presence(status=discord.Status.online)
    else:
        await check_configs(bot=bot)
        await bot.process_commands(message)

        def recursive_cog_search_repeat(folder):
            global all_cogs
            if type(folder) != pathlib.Path:
                folder = pathlib.Path(folder)
            for cog in os.listdir(folder):
                if cog != "__pycache__":
                    if cog.endswith(".py") and not pathlib.Path(
                            folder, cog[:-3]
                    ) in all_cogs:
                        con_logger.info(f"Found cog {cog}")
                        all_cogs.append(pathlib.Path(folder, cog[:-3]))
                    elif pathlib.Path(folder, cog).is_dir():
                        if not cog.startswith("unused_"):
                            recursive_cog_search_repeat(
                                pathlib.Path(folder, cog)
                            )

        recursive_cog_search_repeat('cogs')
        author = message.author
        heartbeat_check(bot=bot)


@bot.event
async def on_ready():
    await check_configs(bot=bot)
    con_logger.info("Bot is ready")
    heartbeat_check(bot=bot)


def recursive_cog_search(folder):
    if type(folder) != pathlib.Path:
        folder = pathlib.Path(folder)
    con_logger.info(f"Recursive cogs search started in {pathlib.Path(folder)}")
    for i in os.listdir(folder):
        if i != "__pycache__":
            if i.endswith('.py'):
                con_logger.info("Found cog " + i)
                all_cogs.append(pathlib.Path(folder, i[:-3]))
                if not i.startswith("dev_"):
                    loading_cog = str(pathlib.Path(folder, i[:-3])).replace(
                        "\\" if os.name == "nt" else "/", "."
                    )
                    bot.load_extension(loading_cog)
                    loaded_cogs.append(pathlib.Path(folder, i[:-3]))
                    con_logger.info("Loaded cog " + i)
            elif pathlib.Path(folder, i).is_dir():
                if not i.startswith("unused_"):
                    con_logger.info(
                        f"{i} is a directory, searching"
                        f" cogs here now..."
                    )
                    recursive_cog_search(pathlib.Path(folder, i))
                    con_logger.info(
                        f"Ended searching cogs in {i},"
                        f" continuing in {folder}"
                    )
    con_logger.info(f"Done recursive cogs search in {folder}")


def cog_check():
    for cog in all_cogs:
        parent = cog.parent
        cog_repeats = 0
        for i in all_cogs:
            if str(cog)[len(str(parent)) + 1:] in str(i):
                cog_repeats += 1
        if cog_repeats > 1:
            con_logger.warning(
                f"Cog {cog} was found {cog_repeats} Times! This may create"
                f" an unexpected behaviour"
            )


def command_finder(command):
    probable_commands = []
    for command_real in bot.all_commands:
        if not command.hidden:
            counter = 0
            if len(command_real) > len(command) + 1:
                continue
            for i in range(0, min(len(command), len(command_real))):
                if len(command) == len(command_real):
                    if command[i] == command_real[i]:
                        counter += 1
                else:
                    if command[i] == command_real[min(
                            i + 1, len(command_real) -
                                   1
                    )]:
                        counter += 1
            if counter > abs((len(command_real) - len(command)) - 1):
                probable_commands.append(command_real)
    return probable_commands


async def on_error(ctx, error):
    lang = load_server_language(ctx)
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.guild.owner.dm_channel.send(lang["misc"][
                                                  "not_enough_permissions"])
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(lang["misc"]["not_enough_arguments"])
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(lang["misc"]["command_not_found"])
    elif isinstance(error, SystemExit):
        pass
    else:
        sys.stderr.write(str(error) + "\n")


# bot.on_command_error = on_error

recursive_cog_search("cogs")
cog_check()
bot.run(settings['token'])
