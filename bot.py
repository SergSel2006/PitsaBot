import logging
import os
import pathlib
import sys

import yaml
from discord.ext import commands

con_logger = logging.getLogger("Bot")
sh = logging.StreamHandler(stream=sys.stdout)
sh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]: %(message)s'))
con_logger.addHandler(sh)
con_logger.setLevel(logging.INFO)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='Pitsa.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('config.yml', 'r') as o:
    settings = yaml.load(o, yaml.CLoader)
if not settings:
    raise ValueError("No Settings")

bot = commands.Bot(command_prefix=settings['prefix'])
bot.remove_command("help")

devs = settings['developers']
all_cogs = []
loaded_cogs = []


@bot.command(hidden=True)
async def load_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**Загружает новый ког в систему"""
    if ctx.message.author.id not in devs:
        await ctx.send("Только Разработчики бота могут пользоваться этой командой")
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) not in loaded_cogs:
                if "dev_" in cog:
                    await ctx.send("Коги, которые всё ещё в разработке нестабильны! Бот может отключится при загрузке"
                                   " такого кога!")
                try:
                    loading_cog = str(pathlib.Path(cog)).replace("\\", ".")
                    bot.load_extension(loading_cog)
                    loaded_cogs.append(pathlib.Path(cog))
                    await ctx.send("Ког " + cog + " успешно загружен!")
                except Exception as e:
                    await ctx.send("Ког " + cog + " Не был загружен!\n" + str(e))
            else:
                await ctx.send('Ког уже загружен!')
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def unload_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**выгружает ког из бота, используется только в самых плохих ситуациях"""
    if ctx.message.author.id not in devs:
        await ctx.send("Только Разработчики бота могут пользоваться этой командой")
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) in loaded_cogs:
                try:
                    unloading_cog = str(pathlib.Path(cog)).replace("\\", ".")
                    bot.unload_extension(unloading_cog)
                    await ctx.send("Ког " + cog + " успешно выгружен!")
                    loaded_cogs.remove(pathlib.Path(cog))
                except Exception as e:
                    await ctx.send("Ког " + cog + " не был выгружен!\n" + str(e))
            else:
                await ctx.send("Ког и так уже разгружен")
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def reload_cog(ctx, cog):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**перезагружает ког"""
    if ctx.message.author.id not in devs:
        await ctx.send("Только Разработчики бота могут пользоваться этой командой")
    else:
        if pathlib.Path(cog) in all_cogs:
            if pathlib.Path(cog) in loaded_cogs:
                try:
                    reloading_cog = str(pathlib.Path(cog)).replace("\\", ".")
                    bot.unload_extension(reloading_cog)
                    bot.load_extension(reloading_cog)
                    await ctx.send("Ког " + cog + " успешно перезагружен!")
                except Exception as e:
                    await ctx.send("Ког " + cog + " не был перезагружен!\n" + str(e))
                    loaded_cogs.remove(pathlib.Path(cog))
            else:
                await ctx.send("сперва загрузите этот ког!")
        else:
            await ctx.send("Такого кога нет!")


@bot.command(hidden=True)
async def list_cogs(ctx):
    """**ТОЛЬКО ДЛЯ РАЗРАБОТЧИКОВ**даёт информацию о когах"""
    if ctx.message.author.id not in devs:
        await ctx.send("Только Разработчики бота могут пользоваться этой командой")
    else:
        await ctx.send("Активные коги:")
        for cog in loaded_cogs:
            await ctx.send(str(cog) + "\n")
        await ctx.send("Все Коги:")
        for cog in all_cogs:
            await ctx.send(str(cog) + "\n")
        await ctx.send("Общее количество когов: " + str(len(all_cogs)))


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    def recursive_cog_search_repeat(folder):
        global all_cogs
        if type(folder) != pathlib.Path:
            folder = pathlib.Path(folder)
        for cog in os.listdir(folder):
            if cog != "__pycache__":
                if cog.endswith(".py") and not pathlib.Path(folder, cog[:-3]) in all_cogs:
                    con_logger.info(f"Found cog {cog}")
                    all_cogs.append(pathlib.Path(folder, cog[:-3]))
                elif pathlib.Path(folder, cog.removesuffix(".py")).exists():
                    recursive_cog_search_repeat(pathlib.Path(folder, cog))

    recursive_cog_search_repeat('cogs')
    author = message.author
    mentions = message.mentions
    if message.mention_everyone:
        await message.channel.send("я триггернулся от " + author.mention)
        await author.edit(nick='Триггернул PitsaBot', reason="ТРИГГЕРНУЛ МЕНЯ")
    if mentions:
        for mention in mentions:
            if mention.name == "PitsaBot":
                await message.channel.send(":pizza:что надо?")


@bot.event
async def on_ready():
    con_logger.info("Bot is ready")


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
                    loading_cog = str(pathlib.Path(folder, i[:-3])).replace("\\", ".")
                    bot.load_extension(loading_cog)
                    loaded_cogs.append(pathlib.Path(folder, i[:-3]))
                    con_logger.info("Loaded cog " + i)
            elif pathlib.Path(folder, i).exists():
                if not i.startswith("unused_"):
                    con_logger.info(f"{i} is a directory, searching cogs here now...")
                    recursive_cog_search(pathlib.Path(folder, i))
                    con_logger.info(f"Ended searching cogs in {i}, continuing in {folder}")
    con_logger.info(f"Done recursive cogs search in {folder}")


def cog_check():
    for cog in all_cogs:
        parent = cog.parent
        cog_repeats = 0
        for i in all_cogs:
            if str(cog)[len(str(parent)) + 1:] in str(i):
                cog_repeats += 1
        if cog_repeats > 1:
            con_logger.warning(f"Cog {cog} was found {cog_repeats} Times! This may create unexpected behaviour")


recursive_cog_search("cogs")
cog_check()
bot.run(settings['token'])
