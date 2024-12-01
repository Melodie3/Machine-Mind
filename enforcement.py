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

def json_data_increment(
        member: discord.Member,
        field: str,
        amount: int
    ) -> None:
    """Increments a member's data in the JSON data."""
    try:
        # print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        # print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", guild = member.guild.id, create_if_nonexistent=True)
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

        JSON_cog.set_filing_cabinet("enforcement", cabinet = cabinet, guild = member.guild.id)
        print(f"Value {field} is now {file[field]}")

    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))

async def timeout_user(
        *,
        user_id: int,
        guild_id: int,
        until: int
    ) -> bool:
    """Times out the given member for `until` mount of minutes, then retruns a boolean for whether the timeout was successful."""
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

async def brick_stats(
        ctx: commands.Context,
        member: discord.Member
    ) -> None:
    """Sends a member's brick stats."""
    #print("brick_stats called")
    try:
        #print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        #print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", guild = ctx.guild.id, create_if_nonexistent=False)
        #print("Cabinet loaded")
        
        id = str(member.id) #needs to be string because ints can't be keys in JSON
        #id = ctx.author.id

        name = member.display_name
        if utility.contains_ping(name):
            name = member.name
        
        if id not in cabinet.keys():
            await ctx.send(f"{name} has not been bricked yet.")

        file = cabinet[id]

        total_bricks = 0

        sn = utility.smart_number

        if "brick_count" not in file.keys():
            file["brick_count"] = 0
        output = f"Brick stats for {name}:\n\n"
        if "bricks" in file.keys():
            output += f":bricks: - {sn(file['bricks'])}\n"
            total_bricks += file["bricks"]
        if "golden_bricks" in file.keys():
            output += f"{golden_brick_emoji} - {sn(file['golden_bricks'])}\n"
            total_bricks += file["golden_bricks"]
        if "total_timeout" in file.keys():
            output += f"Total timeout: {sn(file['total_timeout'])} minutes\n"
        if total_bricks > 0:
            output += f"Total bricks: {sn(total_bricks)}"

        await ctx.send(output)


    except Exception as exception:
        print("Exception: {}".format(type(exception).__name__))
        print("Exception message: {}".format(exception))

async def brick_leaderboard(
        ctx: commands.Context,
        user: discord.Member
    ) -> None:
    """Sends the brick leaderboard."""
    try:

        output = "** -- Brick leaderboard: -- **\n\n"
        inquirer_name = user.display_name
        if utility.contains_ping(inquirer_name):
            inquirer_name = user.name

        #print("Attempting reference through cog")
        JSON_cog = bot_ref.get_cog("JSON")
        #print(f"JSON cog is {JSON_cog}")
        cabinet = JSON_cog.get_filing_cabinet("enforcement", guild=ctx.guild.id, create_if_nonexistent=False)
        #print("Cabinet loaded")
        
        list_timeouts = {}
        list_bricks = {}
        list_golden_bricks = {}
        list_total_bricks = {}
        for id in cabinet.keys():
            file = cabinet[id]
            total_bricks = 0
            if "total_timeout" in file.keys():
                list_timeouts[id] = file["total_timeout"]
            if "bricks" in file.keys():
                list_bricks[id] = file["bricks"]
                total_bricks += file["bricks"]
            if "golden_bricks" in file.keys():
                list_golden_bricks[id] = file["golden_bricks"]
                total_bricks += file["golden_bricks"]
            if total_bricks > 0:
                list_total_bricks[id] = total_bricks

        sorted_timeouts =        sorted(list_timeouts,      key=list_timeouts.get,      reverse=True)
        sorted_bricks =          sorted(list_bricks,        key=list_bricks.get,        reverse=True)
        sorted_golden_bricks =   sorted(list_golden_bricks, key=list_golden_bricks.get, reverse=True)
        sorted_total_bricks =    sorted(list_total_bricks,  key=list_total_bricks.get,  reverse=True)

        #sorted(A, key=A.get, reverse=True)[:5]
        for leaderboard in [sorted_total_bricks, sorted_bricks, sorted_golden_bricks, sorted_timeouts]:
            id_str = str(user.id)
            if id_str in leaderboard: # if user is in the leaderboard
                index = leaderboard.index(id_str)
            else:
                index = -1   

            list_ref = None
            if leaderboard == sorted_total_bricks:
                output += "**Total bricks:**\n"
                list_ref = list_total_bricks
            elif leaderboard == sorted_timeouts:
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
                        output += f"{i+1}. **{name}: {utility.smart_number(list_ref[id])}**\n"
                    else:
                        output += f"{i+1}. {name}: {utility.smart_number(list_ref[id])}\n"
                else:
                    output += f"{i+1}. \n"

            if index != -1:
                output += f"\n{inquirer_name} is at position {utility.smart_number(index+1)} with a count of {utility.smart_number(list_ref[str(user.id)])}.\n"
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

@commands.command()
async def unbrick(ctx, member: typing.Optional[discord.Member]):
    if verification.has_role(ctx.author, "moderator") or verification.has_role(ctx.author, "deputized"):
        if member is None:
            await ctx.reply("Please specify a user.")
            return
        await timeout_user(user_id=member.id, guild_id=ctx.guild.id, until=0)
        await ctx.send(f"{member.mention} has been unbricked.")
    else:
        await brick(ctx, None)
    

@commands.command(
    brief="The fabled brick.",
    help="Instructions read: keep away from pipi"
)
# async def brick(ctx, member: typing.Optional[discord.Member], duration: typing.Optional[typing.Union[str, int]]):
async def brick(ctx, member: typing.Optional[discord.Member], *args):
    duration = None
    multiplier = 1 #how many time segments to brick for
    time_segment = 1 #usually minutes, can be hours or days or weeks
    special_command = None
    do_brick_animation = True
    forever = False
    authorized_user = False

    if verification.has_role(ctx.author, "moderator") or verification.has_role(ctx.author, "deputized") or verification.has_role(ctx.author, "admin") or verification.is_owner(ctx.author):
        authorized_user = True

    if len(args) == 0:
        duration = None

    for arg in args:
        if arg.lower() in ["reason", "reason:"]:
            break
        if arg.isnumeric():
            duration = arg
            multiplier = int(arg)
        elif arg.lower() in ["instant", "now", "immediate"] and authorized_user:
            do_brick_animation = False
        elif arg.lower() in ["forever", "permanent", "permanently", "ban"] and authorized_user:
            duration = "forever"
            forever = True
        elif arg.lower() in ["minutes", "minute", "m"]:
            duration = "minute"
            time_segment = 1
        elif arg.lower() in ["hours", "hour", "h"]:
            duration = "hour"
            time_segment = 60
        elif arg.lower() in ["days", "day", "d"]:
            duration = "day"
            time_segment = 60*24
        elif arg.lower() in ["weeks", "week", "w"]:
            duration = "week"
            time_segment = 60*24*7
        elif arg.lower() in ["max"]:
            duration = 60*24*7*3 # 3 weeks
            time_segment = 60*24*7*3
        elif arg.lower() in ["stats", "leaderboard"]:
            duration = arg
            special_command = arg
        else:
            try:
                duration = int(arg)
            except:
                pass
    
    # possible arguments: forever etc, hour, day, week, max, stats, leaderboard, instant

    print (f"Brick called by {ctx.author.display_name} with target {member} and duration {duration}")

    duration = str(duration)

    target = None
    internal_duration = 1
    # forever = False

    


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
        if authorized_user:
            #since the sender is authorized, give correct target
            target = member
            internal_duration = time_segment * multiplier
            

        elif member is ctx.author:
            # people can now brick themselves for arbitraty amounts of time
            target = ctx.author
            forever = False # no self-banning
            do_brick_animation = True
            try:
                # duration = int(duration)
                duration = time_segment * multiplier
                # no more than 1 day
                duration = min(duration, 60*24)
                # but at least 1 minute
                duration = max(duration, 1)
                print(f"duration will be {duration} minutes")
                internal_duration = duration
            except:
                pass  
        else: #not from author, brick sender
            target = ctx.author
        #we know the member. If owner, brick them based on duration
        #if not owner, brick sender lmaos

    # SPECIAL CASES

    # if person calling command is already in the list. Done to prevent spamming during the 10 second interval.
    if target is ctx.author and (target in brick_list or target.is_timed_out()):
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
            if do_brick_animation:
                message = await brick_animation(ctx, target, forever)
            else:
                message = await ctx.send(f"{target.mention} will be bricked immediately.")
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

    if special_command == "stats":
        if member is None:
            member = ctx.author
        await brick_stats(ctx, member)

    if special_command == "leaderboard":
        if member is None:
            member = ctx.author
        await brick_leaderboard(ctx, member)
    
    await asyncio.sleep(5)
    try:
        brick_list.remove(target)
    except:
        print(f"Error removing {target} from brick list")
    if success:
        pass

async def brick_animation(
        ctx: commands.Context,
        member: discord.Member,
        forever = False
    ) -> discord.Message:
    """Runs the brick animation."""
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

async def setup(bot: commands.Bot):
    importlib.reload(verification)
    importlib.reload(utility)
    #bot.add_command(timeout)
    bot.add_command(brick)
    bot.add_command(unbrick)
    global bot_ref
    bot_ref = bot
