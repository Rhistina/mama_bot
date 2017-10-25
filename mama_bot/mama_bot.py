#!/usr/bin/env python3

import discord
from utils import fflogs_api
from discord.ext import commands


description = '''A simple Discord bot that returns FFLOGS.COM Data'''
bot = commands.Bot(command_prefix='?', description=description)
apiCall = fflogs_api.FflogsRequest()
defaults = fflogs_api.botDefaults()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined the Discord server."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.command()
async def setRegion(region):
    """Sets the default region of the bot."""
    defaults.setRegion(region)
    await bot.say("`Set default region name to %s`" % (defaults.defaultRegion))

@bot.command()
async def setServer(server):
    """Sets the default server of the bot."""
    defaults.setServer(server)
    await bot.say("`Set default server name to %s`" % (defaults.defaultServer))

@bot.command()
async def rank(firstName,lastName,server=None,region=None):
    """Gets the latest rankings of a character."""
    name = firstName + " " + lastName
    if (server == None and region == None):
        server = defaults.defaultServer
        region = defaults.defaultRegion
    message = apiCall.rank_of(name,server,region)
    await bot.say(message)

@bot.command()
async def bestPct(firstName,lastName,server=None,region=None):
    """Gets Percentile of your best HISTORICAL parses."""
    name = firstName + " " + lastName
    if (server == None and region == None):
        server = defaults.defaultServer
        region = defaults.defaultRegion
    message = apiCall.best_percentile_of(name,server,region)
    await bot.say(message)

@bot.command()
async def curPct(firstName,lastName,server=None,region=None):
    """Gets Percentile of your best current parses."""
    name = firstName + " " + lastName
    if (server == None and region == None):
        server = defaults.defaultServer
        region = defaults.defaultRegion
    message = apiCall.current_percentile_of(name,server,region)
    await bot.say(message)

@bot.command()
async def maxBossPatch(firstName,lastName,patch,server=None,region=None):
    """Gets the MAXIMUM boss defeated for this patch."""
    name = firstName + " " + lastName
    if (server == None and region == None):
        server = defaults.defaultServer
        region = defaults.defaultRegion
    message = apiCall.get_max_encounter_per_patch(name,server,region,patch)
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
bot.run('')
