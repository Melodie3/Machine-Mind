from re import S
import aiohttp
import discord
import datetime
import warnings
from discord.ext import commands
import typing
import importlib
import asyncio
import random

import verification
import bread.utility as utility

warnings.filterwarnings("ignore", category=DeprecationWarning)
#intents = discord.Intents.all()
#bot = commands.Bot(command_prefix=['$',], intents=intents)
#bot.session = aiohttp.ClientSession()

golden_brick_emoji = "<:brick_gold:971239215968944168>"

bot_ref = None

def json_data_increment(member: discord.Member, field: str, amount: int):
    try:
        # print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        # print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", create_if_nonexistent=True)
        # print("Cabinet loaded")
        
        id = str(member.id) #needs to be string because ints can't be keys in JSON
        #id = member.id
        
        if id not in cabinet.keys():
            cabinet[id] = {}

        cabinet[id]["username"] = member.name
        cabinet[id]["display_name"] = member.display_name            
        
        file = cabinet[id]

        if field not in file.keys():
            file[field] = 0
        
        file[field] += amount

        JSON_cog.set_filing_cabinet("enforcement", cabinet)
        print(f"Value {field} is now {file[field]}")

    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))

async def timeout_user(*, user_id: int, guild_id: int, until):
    until = int(until)
    if until < 0:
        return
    #print (f"Timeout called on user id {user_id} for {until} minutes")
    result = None
    base_session = aiohttp.ClientSession()
    #async with aiohttp.ClientSession() as rawsession:
    headers = {"Authorization": f"Bot {bot_ref.http.token}"}
    #print ("Bot ref http is "+str(bot_ref.http)+" and token is "+str(bot_ref.http.token))
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    async with base_session.patch(url, json=json, headers=headers) as session:
        if session.status in range(200, 299):
            result = True
        else:
            result = False
    
    await base_session.close()
    return result

async def brick_stats(ctx, member: discord.Member):
    #print("brick_stats called")
    try:
        #print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        #print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", create_if_nonexistent=False)
        #print("Cabinet loaded")
        
        id = str(member.id) #needs to be string because ints can't be keys in JSON
        #id = ctx.author.id

        name = member.display_name
        if utility.contains_ping(name):
            name = member.name
        
        if id not in cabinet.keys():
            await ctx.send(f"{name} has not been bricked yet.")

        file = cabinet[id]

        if "brick_count" not in file.keys():
            file["brick_count"] = 0
        output = f"Brick stats for {name}:\n\n"
        if "bricks" in file.keys():
            output += f":bricks: - {file['bricks']}\n"
        if "golden_bricks" in file.keys():
            output += f"{golden_brick_emoji} - {file['golden_bricks']}\n"
        if "total_timeout" in file.keys():
            output += f"total timeout: {file['total_timeout']} minutes"

        await ctx.send(output)


    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))

async def brick_leaderboard(ctx, user: discord.Member):
    try:

        output = "** -- Brick leaderboard: -- **\n\n"
        inquirer_name = user.display_name
        if utility.contains_ping(inquirer_name):
            inquirer_name = user.name

        #print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        #print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", create_if_nonexistent=False)
        #print("Cabinet loaded")
        
        list_timeouts = {}
        list_bricks = {}
        list_golden_bricks = {}
        for id in cabinet.keys():
            file = cabinet[id]
            if "total_timeout" in file.keys():
                list_timeouts[id] = file["total_timeout"]
            if "bricks" in file.keys():
                list_bricks[id] = file["bricks"]
            if "golden_bricks" in file.keys():
                list_golden_bricks[id] = file["golden_bricks"]

        sorted_timeouts =        sorted(list_timeouts,      key=list_timeouts.get,      reverse=True)
        sorted_bricks =          sorted(list_bricks,        key=list_bricks.get,        reverse=True)
        sorted_golden_bricks =   sorted(list_golden_bricks, key=list_golden_bricks.get, reverse=True)

        #sorted(A, key=A.get, reverse=True)[:5]
        for leaderboard in [sorted_bricks, sorted_golden_bricks, sorted_timeouts]:
            id_str = str(user.id)
            if id_str in leaderboard: # if user is in the leaderboard
                index = leaderboard.index(id_str)
            else:
                index = -1   

            list_ref = None
            if leaderboard == sorted_timeouts:
                output += "**:clock2: Total timeout:**\n"
                list_ref = list_timeouts
            elif leaderboard == sorted_bricks:
                output += f"**:bricks: Bricks:** \n"
                list_ref = list_bricks
            elif leaderboard == sorted_golden_bricks:
                output += f"**{golden_brick_emoji} Golden bricks:**\n"
                list_ref = list_golden_bricks
            
            for i in range(0, 10):
                if i < len(leaderboard):
                    id = leaderboard[i]
                    file = cabinet[id]
                    name = file["display_name"]
                    if utility.contains_ping(name):
                        name = file["username"]
                    if i == index:
                        output += f"**{i+1}. {name}: {list_ref[id]}**\n"
                    else:
                        output += f"{i+1}. {name}: {list_ref[id]}\n"
                else:
                    output += f"{i+1}. \n"

            output += f"\n{inquirer_name} is at position {index+1} with a count of {list_ref[str(user.id)]}.\n"
            output += "\n"
            
        message = await ctx.send(output)

        await asyncio.sleep(30)
        await message.delete()


    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))

"""
@commands.command()
async def timeout(ctx: commands.Context, member: typing.Optional[discord.Member], until: typing.Optional[int]):
    if member is None:
        await ctx.reply("Insufficiently specified user.")
        return

    if until == None:
        until = 1
    
    handshake = await timeout_user(user_id=member.id, guild_id=ctx.guild.id, until=until)
    if handshake is True:
        await ctx.send(f"Successfully timed out {member.display_name} for {until} minutes.")
        return
    else:
        await ctx.send("Unable to complete.")
"""

brick_list = set()

@commands.command(
    brief="The fabled brick.",
    help="Instructions read: keep away from pipi"
)
async def brick(ctx, member: typing.Optional[discord.Member], duration: typing.Optional[typing.Union[str, int]]):
    
    print (f"Brick called by {ctx.author.display_name} with target {member} and duration {duration}")

    duration = str(duration)

    target = None
    internal_duration = 1
    forever = False

    


    # refuse to brick owner
    if member is not None and verification.is_owner(member) and not verification.is_owner(ctx.author):
        print("rejecting attempt to brick owner")
        await ctx.reply("Do you really think I'd brick *my own mother?*")
        target = ctx.author
    elif member is None:
        #no user or unrecognized user. If owner, brick emoji
        if verification.from_owner(ctx.author):

            #chance of golden brick, better for me as the author
            if random.randint(1,10) == 1:
                await ctx.send(golden_brick_emoji)
                json_data_increment(ctx.author, "golden_bricks", 1)
            else:
                await ctx.send(":bricks:")
                json_data_increment(ctx.author, "bricks", 1)
            return
        else:
            #not from owner
            target = ctx.author            

        #if *not* owner, full brickage (done in subcommand)
        pass
    else:
        if verification.has_role(ctx.author, "moderator"):
            #since the sender is authorized, give correct target
            target = member
            if duration is not None and \
                    verification.has_role(ctx.author, "admin"):
                if str(duration).lower() in ["forever", "permanent", "permanently", "ban"]:
                    #ban instead
                    print(f"user {member} will be banned")
                    forever = True
                    #return
                elif str(duration).lower() == "hour":
                    internal_duration = 60
                elif str(duration).lower() == "day":
                    internal_duration = 60*24
                elif str(duration).lower() == "week":
                    internal_duration = 60*24*7
                else:
                    try:
                        internal_duration = int(duration)
                        print(f"duration will be {internal_duration} minutes")
                    except:
                        print("duration not recognized, ignoring")
                    #if is number of minutes
                    
            else: #duration is None, timeout
                pass

        else: #not from author, brick sender
            target = ctx.author
        #we know the member. If owner, brick them based on duration
        #if not owner, brick sender lmao

    # SPECIAL CASES

    # if person calling command is already in the list. Done to prevent spamming during the 10 second interval.
    if target is ctx.author and target in brick_list:
        print(f"rejecting brick spam attempt from {target}")
        await ctx.reply("There's nothing you can do about it now.")
        return

    


    #if verification.has_role(target, 
    success = False
    brick_list.add(target)
    #print(f"Adding {target} to brick list, list is now {brick_list}.")

    # process in a try block because sometimes message gets deleted
    try:

        #easter egg to fast track deletion
        try:
            message = await brick_animation(ctx, target, forever)
        except:
            print("Brick message was deleted, fast-tracking")
            #reject deletion, continue process.
            message = await ctx.send("You can't get away *that* easily.")
            await asyncio.sleep(1)
        if forever is False:
            try:
                success = await timeout_user(user_id=target.id, guild_id=ctx.guild.id, until=internal_duration) 
            except:
                success = False

            if success:
                await message.edit(content = f"{target.mention} has been bricked.")
                json_data_increment(target, "total_timeout", internal_duration)
                # 1 in 128 chance for golden brick, by popular demand
                if random.randint(1,32) == 1:
                    await ctx.send(golden_brick_emoji)
                    json_data_increment(target, "golden_bricks", 1)
                else:
                    await ctx.send(":bricks:")
                    json_data_increment(target, "bricks", 1)
            else:
                await message.edit(content = "Looks like you got away this time.")
        else: #forever is true
            pass
            #success = False # actually = await ban 
            try:
                await ctx.guild.ban(member, 
                                    reason=f"Banned by {ctx.author.name} at moderator discretion",
                                    delete_message_days=0)
                success = True
            except Exception as exception:
                success = False
                print("Exception: {}".format(type(exception).__name__))
                print("Exception message: {}".format(exception))
                print("Failed to ban user.")


            if success:
                await message.edit(content = f"{target.mention} has been bricked. Permanently.")
                #await ctx.send(":bricks:")
                await ctx.send(golden_brick_emoji)
            else:
                await message.edit(content = "Looks like you got away this time.")
    except:
        print("An error occurred during bricking, probably the message was deleted.")
    try:
        brick_list.remove(target)
    except:
        print(f"Error removing {target} from brick list")
    if success:
        pass #add emoji to brick list

    if duration == "stats":
        if member is None:
            member = ctx.author
        await brick_stats(ctx, member)

    if duration == "leaderboard":
        if member is None:
            member = ctx.author
        await brick_leaderboard(ctx, member)

async def brick_animation(ctx, member: discord.Member, forever=False):
    pass
    header = f"For your sins, {member.mention}, you will be bricked."
    if forever:
        header += " Forever."
    header += "\n\n"
    footer = ""
    count = 5

    message = await ctx.send(header+footer)
    await asyncio.sleep(2)

    footer = "Are you ready?"
    await message.edit(content = header+footer)
    await asyncio.sleep(3)

    for i in range(count):
        footer = f"{count}."
        #await message.edit(content = str(count)+".")
        await message.edit(content = header+footer)
        await asyncio.sleep(1)
        count -= 1

    footer = "It was good knowing you."
    await message.edit(content = header+footer)
    #await asyncio.sleep(1)
    return message

async def setup(bot):
    importlib.reload(verification)
    importlib.reload(utility)
    #bot.add_command(timeout)
    bot.add_command(brick)
    global bot_ref
    bot_ref = bot