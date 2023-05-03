#global imports
import discord
import importlib

from discord.ext import commands

# pip3 install python-dotenv
from dotenv import load_dotenv
from os import getenv

#local imports
#from verification import from_owner
#from verification import get_rejection_reason
import verification
"""
#local imports
import roles
import timeout
"""

# bot command arguments doc https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Command

# these extensions are loaded from outside files of the given name. Works like import.
extensions = ['talk', 'roles', 'chess_bot', 'enforcement'] #timeout will be included later

load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')
OWNER_ID = int(getenv('OWNER_ID'))
COMMAND_PREFIX = getenv('COMMAND_PREFIX')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, owner_id=OWNER_ID)


#intents = discord.Intents(messages=True, guilds=True, members=True)
#client = discord.Client()



@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    try:
        bot.load_extension('bootstrap_cog')
    except commands.ExtensionAlreadyLoaded:
        pass
    except:
        #some other exception
        raise
    
    #for extension in extensions:
    #    bot.load_extension(extension)
    print("All extensions loaded.")


@bot.command( hidden = True )
@commands.is_owner()
async def bootstrap(ctx):
    importlib.reload(verification)
    bot.reload_extension('bootstrap_cog')
    await ctx.send("Done.")


@bot.command(
    brief = "[Secret]"
)
async def ready(ctx):
    # check for mom
    if not verification.from_owner(ctx.author): 
        await ctx.send(verification.get_rejection_reason())
        return

    await ctx.send('Yes.')

#make sure that we only deal with non-DMs
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None # no dms


bot.run(TOKEN)
