#!/usr/bin/env python3

import discord
from utils import fflogs
from discord.ext import commands
import os

description = '''A simple Discord bot that returns FFLOGS.COM Data'''
bot = commands.Bot(command_prefix='?', description=description)
fflogs_request = fflogs.FflogsRequest()
defaults = fflogs.botDefaults()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#
# @bot.command()
# async def setRegion(region):
#     """Sets the default region of the bot."""
#     defaults.setRegion(region)
#     await bot.say("`Set default region name to %s`" % (defaults.defaultRegion))
#
# @bot.command()
# async def setServer(server):
#     """Sets the default server of the bot."""
#     defaults.setServer(server)
#     await bot.say("`Set default server name to %s`" % (defaults.defaultServer))

@bot.command()
async def rank(firstName=None, lastName=None, server=None, region=None):
    """Gets the latest rankings of a character."""
    if all([firstName, lastName, server, region]):
        message = fflogs_request.rank_of("{} {}".format(firstName, lastName), server, region)
    else:
        message = """Usage: ?rank <firstName> <lastName> <server> <region>"""
    await bot.say(message)

@bot.command()
async def bestPct(firstName=None, lastName=None, server=None, region=None):
    """Gets the latest rankings of a character."""
    if all([firstName, lastName, server, region]):
        message = fflogs_request.best_percentile_of("{} {}".format(firstName, lastName), server, region)
    else:
        message = """Usage: ?bestPct <firstName> <lastName> <server> <region>"""
    await bot.say(message)

@bot.command()
async def curPct(firstName=None, lastName=None, server=None, region=None):
    """Gets the latest rankings of a character."""
    if all([firstName, lastName, server, region]):
        message = fflogs_request.current_percentile_of("{} {}".format(firstName, lastName), server, region)
    else:
        message = """Usage: ?curPct <firstName> <lastName> <server> <region>"""
    await bot.say(message)


@bot.command()
async def maxBoss(firstName=None, lastName=None, server=None, region=None, patch=None):
    """Gets the latest rankings of a character."""
    if all([firstName, lastName, server, region, patch]):
        message = fflogs_request.get_max_encounter_per_patch("{} {}".format(firstName, lastName), server, region, patch)
    else:
        message = """Usage: ?maxBoss <firstName> <lastName> <server> <region> <patch>"""
    await bot.say(message)


def check_thank_you(message):
    for thank in ['thank', ' ty']:
        if thank in message.content.lower():
            reply = "You're welcome {}!".format(message.author.mention)
            return reply

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    reply = check_thank_you(message)
    if reply: await bot.send_message(message.channel, reply)

# TODO - API Key should come from a config file
bot.run(os.getenv('DISCORD_API_KEY'))
