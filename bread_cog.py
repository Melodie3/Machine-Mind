"""
Patch Notes: 
- Purchasing an item will now tell you how much of its cost you have remaining. So if an item costs red gems it will tell you how many red gems you have remaining after you buy it.
- Worked with Aloe to speed up: buying random chess pieces, buying special bread packs, and making chessatrons
- When buying multiple chess pieces and special bread packs, you will see how many of each item you got.
- Fixed bug where getting a multiple of 55 chessatrons would ping you for no reason
- Added alchemy recipe to turn a gold gem into a green gem
- You can now use `$bread chessatron <number>` to make a specific number of chessatrons. Also works with `gem_chessatron`. Thanks to Aloe for this patch
- Gambling now has zero rather than nearly zero chance of failing internally. Thanks to Malte for this patch.
- Added `$bread help`, finally. Thanks to Duck for this patch.

TODO: Do not die to the plague

for server:
    update discord.py
    install numpy
    *possibly* run `python3 -m pip update`
    !bread admin set_max_prestige_level 3


Possible future stuff:

V portfolio shows your gain/loss over last tick
- alchemy profits
V each ascension lets you have 100 additional daily rolls
- stronger LC, or temporary LC
- big bread, rewards 500 normal bread loaves, may be made of 4 emojis

Done and posted:
V ooak leaderboard is ooaks only
V Leaderboard:
    V make leaderboard work for values, not emoji
    V make leaderboard use custom code for stonks (stretch goal)
V Gambling now has many more possible rewards, though the overall reward structure remains the same
V fixed minor gabling bug where waffles would appear but weren't acquirable (thank duck duck go for the meme)
V Multiroller now requires 24 rolls and has a better description
V portfolio command takes user argument
V added capys to the gamble chess set
V added $bread wiki command
V portfolio command now shows how your portfolio changed in the last tick
V multirollers now require compound rollers at higher levels

"""

import asyncio
from datetime import datetime
import json
import random
import typing
import os
import importlib
import math

from os import getenv
from dotenv import load_dotenv



import discord
from discord.ext import commands
from discord.ext import tasks

import verification
import emoji
import bread.values as values
import bread.account as account
import bread.gamble as gamble
import bread.rolls as rolls
import bread.store as store
import bread.utility as utility
import bread.alchemy as alchemy
import bread.stonks as stonks

# roles
# average bread enjoyer
# bread enthusiast
# bread maniac
# galaxy bread

# bread specialist
# bread equalist


# bread channel level meanings
# 0 - never rollable
PERMISSION_LEVEL_NONE = 0
# 1 - can do leaderboards etc
PERMISSION_LEVEL_BASIC = 1
# 2 - can do alchemy and shop
PERMISSION_LEVEL_ACTIVITIES = 2
# 3 - can do bread rolls
PERMISSION_LEVEL_MAX = 3

earnable_channels = ["bread-rolls", "test", "machine-configure", "patch-notes"]
rollable_channels = ["bread", "spam", "smap"]
disallowed_channels = ["brick-jail", "nsfw", "memes", "just-capybaras", "server-meta", "best-moments", "events", 
                        "serious-channel"]

channel_permission_levels = {
    "bread-rolls": 3,
    "test": 3,
    "machine-configure": 3,
    "patch-notes": 3,
    "bread-activities": 2,
    "bread": 1,
    "spam": 1,
    "smap": 1,
}


default_guild = 958392331671830579

announcement_channel_ids = [958705808860921906] # bread on AC
test_announcement_channel_ids = [960871600415178783]  # test on the castle


all_breads = [":bread:",
                ":french_bread:",
                ":croissant:",
                ":flatbread:",
                ":sandwich:",
                ":stuffed_flatbread:"]

rare_breads = [":doughnut:",
                ":bagel:",
                ":waffle:"]



            

one_of_a_kind = ["<:anarchy_chess:960772054746005534>",
                 "<:horsey:960727531592511578>", 
                 "<:holy_hell:961184782253948938>"]     
                 #"<:anarchy:960771114819264533>"] # anarchy symbol - retired

white_pawn = "<:Wpawn:961815364319207516>"
white_rook = "<:Wrook:961815364482793492>"
white_bishop = "<:Wbishop:961815364428263435>"
white_knight = "<:Wknight:958746544436310057>"
white_queen = "<:Wqueen:961815364461809774>"
white_king = "<:Wking:961815364411478016>"

black_pawn = "<:Bpawn:961815364436635718>"
black_rook = "<:Brook:961815364377919518>"
black_bishop = "<:Bbishop:961815364306608228>"
black_knight = "<:Bknight:961815364424048650>"
black_queen = "<:Bqueen:961815364470202428>"
black_king = "<:Bking:961815364327600178>"

# 8 pawns of each color
all_chess_pieces_black = [black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn,
                            black_rook, black_rook,
                            black_bishop, black_bishop,
                            black_knight, black_knight,
                            black_queen,
                            black_king]

                    
all_chess_pieces_white = [white_pawn,white_pawn, white_pawn, white_pawn, white_pawn, white_pawn,white_pawn, white_pawn, 
                            white_rook,  white_rook,
                            white_bishop, white_bishop,
                            white_knight, white_knight,
                            white_queen,
                            white_king]

all_stonks = [":pretzel:", ":cookie:", ":fortune_cookie:"]


####################################################
##############   JSON INTERFACE   ##################
####################################################


class JSON_interface:
    
    
    ####################################
    #####      SETUP

    file_path = "bread_data.json"

    default_data = {
        'load_count' : 0,
        
        'bread' : {
            # "949092523035480134" : { # guild id
            #     'guild_info' : {
            #         'name' : "",
            #         'rolling_channel' : "",
            #         'communications_channel' : "",
            #     },
                546829925890523167 : {
                        'username' : 'Melodie',
                        'total_dough' : 0,
                        'special_bread' : 0
                },
                961567735358291998 : {
                    'username' : 'artemis',
                    'total_dough' : 100,
                    'special_bread' : 1
                }
            # }
        }
        
    }

    data = dict()
    accounts = dict()

    ####################################
    #####      FILE STUFF

    def internal_load(self):
        print("Bread JSON internal_load called")


        JSON_cog = bot_ref.get_cog("JSON")
        JSON_cog.load_all_data() 
        self.data["bread"] = JSON_cog.get_filing_cabinet("bread", create_if_nonexistent=True)
        self.data["archived_bread_count"] = JSON_cog.get_filing_cabinet("archived_bread_count", create_if_nonexistent=False)

        print("Load process complete, one way or another.")

    
    def internal_save(self, json_cog = None):
        print("saving bread data")
        if json_cog is None:
            json_cog = bot_ref.get_cog("JSON")
        json_cog.set_filing_cabinet("bread", self.data["bread"])
        # JSON_cog.set_filing_cabinet("archived_bread_count", self.data["archived_bread_count"])
        json_cog.save_all_data()
        
        

    def create_backup(self):
        pass
        #first, make sure there's a backup folder (relative path)
        folder_path = "backup/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        #then, we make the file
        file_name = datetime.now().strftime('bread_data_backup_%y-%-m-%-d---%H-%M-%S.json')
        with open(folder_path+file_name, 'w') as outfile:
            print('created ', file_name)
            #json_string = json.dumps(self.data, indent=2)
            json.dump(self.data, outfile)

        print("Backup Created.")



    ####################################
    #####      INTERFACE

    def get_account(self, user:typing.Union[discord.Member, int, str]) -> account.Bread_Account:
        #index = str(user.id)
        if type(user) is int:
            index = str(user)
        elif type(user) is discord.Member:
            index = str(user.id)
        else:
            index = str(user)

        if index in self.accounts:
            return self.accounts[index]
        account_raw = account.Bread_Account.from_dict(index, self.get_file_for_user(user))
        self.accounts[index] = account_raw
        return account_raw
        

    def set_account(self, user:typing.Union[discord.Member, int, str], user_account: account.Bread_Account):
        if type(user) is int:
            index = str(user)
        elif type(user) is discord.Member:
            index = str(user.id)
        else:
            index = str(user)

        self.accounts[index] = user_account
        self.data["bread"][index] = user_account.to_dict()

    def has_account(self, user:discord.Member) -> bool:
        index = str(user.id)
        return index in self.data["bread"]

    def get_all_user_accounts(self) -> list:
        #return [account.Bread_Account.from_dict(index, self.data["bread"][index]) for index in self.data["bread"]]
        output = []
        for index in self.data["bread"]:
            if index.isdigit():
                output.append(self.get_account(index))
            # yield account.Bread_Account.from_dict(index, self.data["bread"][index])
        return output

    ####################################
    #####      INTERFACE NICHE

    def get_custom_file(self, label:str):
        if label in self.data["bread"]:
            return self.data["bread"][label]
        else:
            return dict()

    def set_custom_file(self, label:str, file_data:dict):
        self.data["bread"][label] = file_data


    """
    ####################################
    #####      INTERFACE GUILD
    
    def get_guild_name(self, guild_id: int) -> str:
        if guild_id in self.data["bread"]:
            return self.data["bread"][str(guild_id)]["guild_info"]["name"]
        else:
            return ""

    def get_all_rolling_channels(self) -> list:
        for guild_id in self.data["bread"].keys():
            guild = bot_ref.get_guild(int(guild_id))
            if guild is not None:
                #all_channels = guild.get_all_channels()
                for channel in guild.get_all_channels():
                    if channel.name.lower() in rollable_channels:
                        yield channel

    def get_communication_channel(self, guild_id: int) -> discord.TextChannel:
        if guild_id in self.data["bread"]:
            output = bot_ref.get_channel(int(self.data["bread"][str(guild_id)]["guild_info"]["communications_channel"]))
            if output == None:
                pass
            return output
        else:
            return None
    """
    ####################################
    #####      INTERFACE OLD

    

    def get_file_for_user(self, user: typing.Union[discord.Member, int, str]): 
        if type(user) is int:
            key = str(user)
        elif type(user) is discord.Member:
            key = str(user.id)
        else:
            key = str(user)
        #print("Searching database for file for "+user.display_name)
        if key in self.data['bread']:
            #print("Found")
            return self.data['bread'][key]
        else:
            print("Creating new data for "+str(user))
            new_file = {
                'total_dough' : 0,
                'earned_dough' : 0,
                'max_daily_rolls' : 10
            }
            self.data['bread'][key] = new_file
            return new_file

    def update_file_for_user(self, user: typing.Union[discord.Member,str,int], file):
        if type(user) is int:
            key = str(user)
        elif type(user) is discord.Member:
            key = str(user.id)
        else:
            key = str(user)
        print("Updating bread file for "+str(user.display_name))
        # if self.data['bread'][key] is not None:
        #     print("Existing file is:")
        #     print(self.data['bread'][key])
        # print("New file is ")
        # print(file)
        self.data['bread'][key] = file

    # self, Discord user, string, integer
    def increase_value_in_file(self, user: discord.member, key: str, value_change: int):
        file = self.get_file_for_user(user)
        if key not in file:
            file[key] = 0
        file[key] += value_change

        #self.update_file_for_user(user, file) # I believe these are still by reference so the update should be inherent
    def set_value_in_file(self, user: discord.member, key: str, new_value):
        file = self.get_file_for_user(user)
        if key not in file:
            print("Set value - creating new entry")
        file[key] = new_value

    def get_value_in_file(self, user: discord.member, key: str):
        file = self.get_file_for_user(user)
        if key not in file:
            print("Get value - No such value")
            return 0
        else: 
            return file[key]
        





########################################################################################################################################
###############   BREAD COG   ######################
####################################################


class Bread_cog(commands.Cog, name="Bread"):

    json_interface = JSON_interface()
    currently_interacting = list()

    def __init__(self, bot):
        #print("bread __init__ called")
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()
        pass

    ########################################################################################################################
    #####      TASKS

    reset_time = None

    @tasks.loop(minutes=60)
    async def daily_task(self):
        # NOTE: THIS LOOP CANNOT BE ALTERED ONCE STARTED, EVEN BY RELOADING. MUST BE STOPPED MANUALLY
        time = datetime.now()
        print (time.strftime("Hourly bread loop running at %H:%M:%S"))

        self.synchronize_usernames_internal()
        self.json_interface.internal_save() # Save every hour
        self.currently_interacting.clear() # Clear the list of users currently interacting

        #run at 3pm
        if time.hour == 15:
            self.json_interface.create_backup()
            self.reset_internal() # this resets all roll counts to 0
            print("Backup called")
            await self.announce("bread_o_clock", "It's Bread O'Clock!")

        # every 6 hours, based around 3pm
        # print (f"Hour +15 %6 is {(time.hour + 15) % 6}")
        # print (f"Hour -15 %6 is {(time.hour - 15) % 6}")
        if (time.hour - 12) % 6 == 0:
            print("stonk fluctuate called")

            self.stonk_fluctuate_internal()
            await self.stonks_announce()
    
    @daily_task.before_loop
    async def before_daily(self):
        print('Booting up loop')
        #wait to be closer to the hour
        time = datetime.now()

        if time.minute < 5:
            # wait until 5 minutes after the hour
            wait_time = max(5 - time.minute, 0)
            print (f"waiting before bread loop for {wait_time} minutes")
            await asyncio.sleep(60*wait_time)
            print (time.strftime("Finished waiting at %H:%M:%S"))

        elif time.minute > 5:
            #wait into next hour
            wait_time = max(65 - time.minute, 0)
            print (f"waiting before bread loop for {wait_time} minutes")
            await asyncio.sleep(60*wait_time)
            print (time.strftime("Finished waiting at %H:%M:%S"))
    
    ########################################################################################################################
    #####      ANNOUNCE

    previous_messages = dict()

    async def announce(self, key, message: str):

        print("announce called")
        load_dotenv()
        IS_PRODUCTION = getenv('IS_PRODUCTION')
        if IS_PRODUCTION == 'False':
            return
        print("announce continuing")

        for channel_id in announcement_channel_ids:
            channel = self.bot.get_channel(int(channel_id))
            if channel is not None:
                # save message and delete previous one
                # first create a key we'll use to refer to each one
                save_key = str(key) + str(channel_id)

                if save_key in self.previous_messages:
                    try:
                        await self.previous_messages[save_key].delete()
                        self.previous_messages.pop(save_key)
                    except:
                        pass
                    try:
                        message = await channel.send(message)
                        self.previous_messages[save_key] = message
                    except:
                        pass

    ########################################################################################################################
    #####      SYNCHRONIZE_USERNAMES

    def synchronize_usernames_internal(self):
        # we get the guild and then all the members in it
        # guild = default_guild
        guild = self.bot.get_guild(default_guild)
        all_members = guild.members

        print(f"member count is {len(all_members)}, theoretical amount is {guild.member_count}")

        if len(all_members) != guild.member_count:
            print("member count mismatch")

        # we iterate through all the members and rename the key
        for member in all_members:
            # make sure they have an account
            # print (f"Checking {member.display_name}")
            if self.json_interface.has_account(member):
                #print(f"{member.display_name} has account")
                # get the account
                account = self.json_interface.get_account(member)

                account.values["id"] = member.id
                account.values["username"] = member.name
                account.values["display_name"] = member.display_name
                
                # save the account
                self.json_interface.set_account(member, account)

        # save the database      
        self.json_interface.internal_save()

    ########################################################################################################################
    #####      BREAD

    @commands.group(
        brief="Bread.",
        help="It's bread.\n\nUse '$bread wiki' to get a link to the knowledge repository."
    )
    async def bread(self, ctx): #, *args):
        #print("bread called with "+str(len(args))+" args: "+str(args))

        #print(f"bread invoked with passed subcommand {ctx.subcommand_passed}")

        if ctx.invoked_subcommand is None:
            user_account = self.json_interface.get_account(ctx.author)
            spellcheck = user_account.get("spellcheck")
            if spellcheck is False or ctx.subcommand_passed == None:
                await self.roll(ctx)
            else:
                await ctx.send("That is not a recognized command. Use `$help bread` for some things you could call. If you wish to roll, use `$bread` on its own.")

        pass
    
    @bread.command(
        hidden=True,
    )
    async def help(self, ctx):
        await ctx.send_help(Bread_cog.bread)

    ########################################################################################################################
    #####      BREAD WIKI

    @bread.command(
        brief="Links to the wiki."
    )
    async def wiki(self, ctx):
        await ctx.send("The bread wiki is a repository of all information so far collected about the bread game. It can be found here:\nhttps://the-bread-game.fandom.com/wiki/The_Bread_Game_Wiki")

    ###########################################################################################################################
    ######## STATS OLD

    @bread.command(
        hidden = True,
        brief="Stats about bread.",
        help="Gives bread stats about either the person calling it or the named user."
    )
    async def stats_old(self, ctx, user: typing.Optional[discord.Member], archived: typing.Optional[str]):
        #print("stats called for user "+str(user))

        check_archive = False
        if (archived is not None) and (archived.lower() == "archive" or archived.lower() == "archived"):
            check_archive = True

        if user is None:
            user = ctx.author


        output = ""

        #archive check
        if check_archive is False:
            #getting current data
            file = self.json_interface.get_file_for_user(user)
            file["username"] = user.name
        else:
            #getting archived data
            old_data = self.json_interface.data["archived_bread_count"]
            id_str = str(user.id)
            #print(f"Searching for {id_str} in archived data {old_data.keys()}")
            if id_str in old_data.keys():
                file = old_data[id_str]
            else:
                await ctx.send(f"No archive data found for {user.name}")
                return

        output += "Stats for: " + file["username"] + "\n\n"
        output += "You have **" + str(file["total_dough"]) + " dough.**\n\n"
        if "earned_dough"in file.keys():
            output += "You've found " + str(file["earned_dough"]) + " dough through all your rolls.\n"
        if "total_rolls" in file.keys():
            output += "You've bread rolled " + Bread_cog.write_number_of_times( str(file["total_rolls"]) ) + ".\n"
            pass

        if "lifetime_gambles" in file.keys():
            output += "You've gambled your dough " + Bread_cog.write_number_of_times( str(file["lifetime_gambles"]) ) + ".\n"
            pass

        if "max_daily_rolls" in file.keys():
            output += "\nYou can bread roll " + Bread_cog.write_number_of_times( str(file["max_daily_rolls"]) ) + " each day.\n"
            pass
        if ("loaf_converter" in file.keys()) and (file["loaf_converter"] > 0):
            output += f"You have {utility.write_count( file['loaf_converter'], 'Loaf Converter'  )}.\n"
            pass
        if ("multiroller" in file.keys()) and (file["multiroller"] > 0):
            output += f"With your {utility.write_count( file['multiroller'], 'Multiroller'  )}, you roll {utility.write_number_of_times(2 ** file['multiroller'])} with each command.\n"
        output += "\nIndividual stats:\n"
        if ":bread:" in file.keys():
            output += ":bread: - " + str(file[":bread:"]) + " found.\n"

        

        #list all emojis found
        for key in file.keys():   
            if key.startswith(":") and key.endswith(":") and key != ":bread:" and (file[key] != 0):
                output += key + " - " + str(file[key]) + "\n"
            pass

        #list all special emojis
        for key in file.keys():   
            if key.startswith("<") and key.endswith(">") and key not in all_chess_pieces_black and key not in all_chess_pieces_white:
                output += key + " - " + Bread_cog.write_number_of_times( str(file[key]) ) + ".\n"
            pass
        
        #make chess board
        board = Bread_cog.format_chess_pieces(file)
        if board != "":
            output += "\n" + board + "\n"
        
        if "lottery_win"in file.keys() and file["lottery_win"] != 0:
            output += "You've won the lottery " + Bread_cog.write_number_of_times( str(file["lottery_win"]) ) + "!\n\n"
        if "chess_pieces"in file.keys() and file["chess_pieces"] != 0:
            output += "You've found a chess piece " + Bread_cog.write_number_of_times( str(file["chess_pieces"]) ) + ".\n"
        if "special_bread" in file.keys() and file["special_bread"] != 0:
            output += "You've found special bread " + Bread_cog.write_number_of_times( str(file["special_bread"]) ) + ".\n"
        if "highest_roll" in file.keys() and file["highest_roll"] > 10:
            output += "The highest roll you've found so far is " + str(file["highest_roll"]) + ".\n"
        if "twelve_breads" in file.keys():
            output += "You've found twelve bread " + Bread_cog.write_number_of_times( str(file["twelve_breads"]) )+ ".\n"
        if "eleven_breads" in file.keys():
            output += "You've found eleven bread " + Bread_cog.write_number_of_times( str(file["eleven_breads"]) ) + ".\n"
        if "ten_breads" in file.keys():
            output += "You've found the full ten loaves " + Bread_cog.write_number_of_times( str(file["ten_breads"]) ) + ".\n"
        if "natural_1" in file.keys():
            output += "You rolled a single solitary bread " + Bread_cog.write_number_of_times( str(file["natural_1"]) ) + ".\n"

        await ctx.send(output)

    ###########################################################################################################################
    ######## BREAD STATS NEW

    @bread.command(
        brief="Stats about bread.",
        help="Gives bread stats about either the person calling it or the named user. Call as '$bread stats [user]' to get stats about another person. Call as '$bread stats [user] archive' to get stats about the user's archive, or as '$bread stats [user] chess' to get stats about the user's chess piece collection."
    )
    async def stats(self, ctx, user: typing.Optional[discord.Member], modifier: typing.Optional[str]):
        #print("stats called for user "+str(user))

        # make sure we're in the right channel to preven spam
        #if ctx.channel.name not in rollable_channels and ctx.channel.name not in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_BASIC:
            await ctx.send("Sorry, you can't do that here.")
            return

        if (modifier is not None) and (modifier.lower() == "archive" or modifier.lower() == "archived"):
            # just call the old version, not worth it to try and implement it since accounts don't really understand
            # the existence of the archive
            await self.stats_old(ctx, user, modifier)
            return

        
        # new stats command
        
        output = ""

        if user is None:
            user = ctx.author
        print(f"stats called for user {user.display_name} by {ctx.author.display_name}")

        # get account
        account = self.json_interface.get_account(user)

        # bread stats chess
        if (modifier is not None) and (modifier.lower() == "chess" or modifier.lower() == "chess pieces" or modifier.lower() == "pieces"):
            output = f"Chess pieces of {account.get_display_name()}:\n\n"
            for chess_piece in values.all_chess_pieces:
                output += f"{chess_piece.text} - {account.get(chess_piece.text)}\n"
            await ctx.send(output)
            return

        # bread stats gambit
        if (modifier is not None) and (modifier.lower() in ["gambit", "strategy", "gambit shop", "strategy shop"]):
            output = f"Gambit shop bonuses for {account.get_display_name()}:\n\n"
            boosts = account.values.get("dough_boosts", {})
            for item in boosts.keys():
                output += f"{item} - {boosts[item]}\n"
            if len(boosts) == 0:
                output += "You have not bought any gambit shop upgrades yet."
            await ctx.send(output)
            return

        sn = utility.smart_number

        output += f"Stats for: {account.get_display_name()}:\n\n"
        output += f"You have **{account.get_dough()} dough.**\n\n"
        if account.has("earned_dough"):
            output += f"You've found {account.get('earned_dough')} dough through all your rolls and {self.get_portfolio_combined_value(user.id)} dough through stonks.\n"
        if account.has("total_rolls"): 
            output += f"You've bread rolled {account.write_number_of_times('total_rolls')} overall.\n"
        
        if account.has("lifetime_gambles"):
            output += f"You've gambled your dough {account.write_number_of_times('lifetime_gambles')}.\n"
        if account.has("max_daily_rolls"):
            output += f"You've rolled {sn(account.get('daily_rolls'))} of {account.write_number_of_times('max_daily_rolls')} today.\n"
        if account.has("loaf_converter"):
            output += f"You have {account.write_count('loaf_converter', 'Loaf Converter')}"  
            if account.has("LC_booster"):
                LC_booster_level = account.get("LC_booster")
                multiplier = 1
                if LC_booster_level >= 1:
                    multiplier = 2 ** LC_booster_level 
                boosted_amount = account.get("loaf_converter") * multiplier
                output += f", which, with Recipe Refinement level {LC_booster_level}, makes you {boosted_amount} times more likely to find special items.\n"
            else:
                output += ".\n"
        if account.has("multiroller"):
            output += f"With your {account.write_count('multiroller', 'Multiroller')}, you roll {utility.write_number_of_times(2 ** account.get('multiroller'))} with each command. "
        if account.has("compound_roller"):
            output += f"You also get {utility.write_count(2 ** account.get('compound_roller'), 'roll')} per message with your {account.write_count('compound_roller', 'Compound Roller')}.\n"
        else:
            output += "\n"

        # ascension/prestige shop items
        if account.has("prestige_level", 1):
            output += "\n"
            if account.has("gamble_level"):
                output += f"You have level {account.get('gamble_level')} of the High Roller Table.\n"
            if account.has("max_daily_rolls_discount"):
                output += f"You have {utility.write_count(account.get('max_daily_rolls_discount'), 'Daily Discount Card')}.\n"
            if account.has("loaf_converter_discount"):
                output += f"You have {utility.write_count(account.get('loaf_converter_discount'), 'Self Converting Yeast level')}.\n"
            if account.has ("chess_piece_equalizer"):
                output += f"With level {account.get('chess_piece_equalizer')} of the Chess Piece Equalizer, you get {store.chess_piece_distribution_levels[account.get('chess_piece_equalizer')]}% white pieces.\n"
            if account.has("moak_booster"):
                output += f"With level {account.get('moak_booster')} of the Moak Booster, you get {round((store.moak_booster_multipliers[account.get('moak_booster')]-1)*100)}% more Moaks.\n"
            if account.has("chessatron_shadow_boost"):
                output += f"With level {account.get('chessatron_shadow_boost')} of the Chessatron Contraption, you get {account.get_shadowmega_boost_amount()} more dough per Chessatron.\n"
            if account.has("shadow_gold_gem_luck_boost"):
                output += f"With level {account.get('shadow_gold_gem_luck_boost')} of Ethereal Shine, you get {utility.write_count(account.get_shadow_gold_gem_boost_count(), 'more LC')} worth of gem luck.\n"
            if account.has("first_catch_level"):
                output += f"With First Catch of the Day, your first {utility.write_count(account.get('first_catch_level'), 'special item')} each day will be worth 4x more.\n"

        output += "\nIndividual stats:\n"
        if account.has(":bread:"):
            output += f":bread: - {account.get(':bread:')} found.\n"

        # list all special breads
        special_breads = account.get_all_items_with_attribute("special_bread")
        selected_special_breads = list()
        for i in range(len(special_breads)):
            # skip the ones that are also rare
            if "rare_bread" in special_breads[i].attributes:
                continue
            
            if account.has(special_breads[i].text):
                selected_special_breads.append(special_breads[i])

        for i in range(len(selected_special_breads)):

            text = selected_special_breads[i].text

            output += f"{account.get(text)} {text} "
            if i != len(selected_special_breads) - 1:
                output += ", "
            else:
                output += "\n"

        display_list = ["rare_bread", "misc_bread", "shiny", "shadow", "misc", "unique" ]

        #iterate through all the display list and print them
        for item_name in display_list:

            display_items = account.get_all_items_with_attribute(item_name)

            cleaned_items = []
            for display_item in display_items:

                if account.has(display_item.text, 1):
                    cleaned_items.append(display_item)
                    # remove the item from the list if it's quantity zero           

            for i in range(len(cleaned_items)):

                text = cleaned_items[i].text
                # if account.get(text) == 0:
                #     continue #skip empty values
                output += f"{account.get(text)} {text} "
                if i != len(cleaned_items) - 1:
                    output += ", "
                else:
                    output += "\n"

        # # list rare_breads
        # rare_breads = account.get_all_items_with_attribute("rare_bread")
        # for i in range(len(rare_breads)):
        #     text = rare_breads[i].text
        #     output += f"{account.get(text)} {text} "
        #     if i != len(rare_breads) - 1:
        #         output += ", "
        #     else:
        #         output += ".\n"

        # # list misc_breads
        # misc_breads = account.get_all_items_with_attribute("misc_bread")
        # for i in range(len(misc_breads)):
        #     text = misc_breads[i].text
        #     output += f"{account.get(text)} {text} "
        #     if i != len(misc_breads) - 1:
        #         output += ", "
        #     else:
        #         output += ".\n"

        # # list misc. breads
        # misc_items = account.get_all_items_with_attribute("misc")
        # for i in range(len(misc_items)):
        #     text = misc_items[i].text
        #     output += f"{account.get(text)} {text} "
        #     if i != len(misc_items) - 1:
        #         output += ", "
        #     else:
        #         output += ".\n"

        output2 = ""

        #make chess board
        board = Bread_cog.format_chess_pieces(account.values)
        if board != "":
            output2 += "\n" + board + "\n"

        # list highest roll stats

        if account.has("highest_roll", 11):
            output2 += f"Your highest roll was {account.get('highest_roll')}.\n"
            comma = False
            if account.has("eleven_breads"):
                output2 += f"11 - {account.write_number_of_times('eleven_breads')}"
                comma = True
            if account.has("twelve_breads"):
                if comma:
                    output2 += ", "
                output2 += f"12 - {account.write_number_of_times('twelve_breads')}"
                comma = True
            if account.has("thirteen_breads"):
                if comma:
                    output2 += ", "
                output2 += f"13 - {account.write_number_of_times('thirteen_breads')}"
                comma = True
            if account.has("fourteen_or_higher"):
                if comma:
                    output2 += ", "
                output2 += f"14+ - {account.write_number_of_times('fourteen_or_higher')}"
                comma = True
            if comma:
                output2 += "."
            output2 += "\n"

        # list 10 and 1 roll stats
        output2 += f"You've found a single solitary loaf {account.write_number_of_times('natural_1')}, and the full ten loaves {account.write_number_of_times('ten_breads')}.\n"

        # list the rest of the stats

        if account.has("lottery_win"):
            output2 += f"You've won the lottery {account.write_number_of_times('lottery_win')}!\n"
        if account.has("chess_pieces"):
            output2 += f"You have {account.write_count('chess_pieces', 'Chess Piece')}.\n"
        if account.has("special_bread"):
            output2 += f"You have {account.write_count('special_bread', 'Special Bread')}.\n"
        
        if len(output) + len(output2) < 1900:
            await ctx.reply( output + output2 )
        else:
            await ctx.reply( output )
            await ctx.reply( "Stats continued:\n" + output2 )
        # await ctx.reply(output)

        #await self.do_chessboard_completion(ctx)

            
            

    
    ###########################################################################################################################
    ######## BREAD LEADERBOARD

    @bread.command(
        brief="Shows the top earners.",
        help = 
"""Used to see the rankings for any stat or emoji that is tracked. 

Include the word "all" to see the leaderboard for all players, including those of a different ascension level. Include "wide" for a wider leaderboard.

Some of the ones you can use include:

total_dough
earned_dough
portfolio_value
max_daily_rolls
total_rolls

natural_1
ten_breads
eleven_breads
twelve_breads
thirteen_breads
fourteen_or_more
lottery_win

special_bread
rare_bread
chess_pieces

multiroller
loaf_converter""",
        aliases = ["leaderboards", "lb"]
    )
    async def leaderboard(self, ctx, person: typing.Optional[discord.User], *args):

        print(f"Leaderboard called by {ctx.author} for {args}")

        args = list(args)

        if person is None:
            person = ctx.author
        
        search_value = None
        lifetime = False
        search_all = False
        wide_leaderboard = False
        requester_account = self.json_interface.get_account(ctx.author.id)

        if "lifetime" in args:
            lifetime = True
            args.remove("lifetime")

        if "all" in args:
            search_all = True
            args.remove("all")

        if "wide" in args:
            wide_leaderboard = True
            args.remove("wide")

        if len(args) > 0:
            search_value = args[0]
            if utility.contains_ping(search_value):
                search_value = "total_dough"
        else:
            search_value = "total_dough"

        
        search_emoji = values.get_emote_text(search_value)
        if search_emoji is not None:
            search_value = search_emoji
        else:
            pass # search_value is already what we want

        # print(f"Lifetime is {lifetime}, search value is {search_value}")

        if lifetime == False:
            def get_value_of_file(file):
                return file[search_value]
        else: # lifetime is true
            print("lifetime is true so we're using the lifetime function")
            def get_value_of_file(file):
                lifetime_name = "lifetime_" + search_value
                output = 0
                if lifetime_name in file:
                    output += file[lifetime_name]
                    # print(f"adding {file[lifetime_name]} to for lifetime")
                if search_value in file:
                    output += file[search_value]
                    # print(f"adding {file[search_value]} to for current")
                return output

        # TODO: add lifetime_dough_rolled and lifetime_dough_combined
        # thus also dough_rolled and dough_combined

        if search_value.lower() in ["lifetime_dough", "dough_combined", "combined_dough"]:
            def get_value_of_file(file):
                if "earned_dough" in file.keys():
                    dough = file["earned_dough"]
                else:
                    dough = file["lifetime_dough"]
                if "id" in file.keys():
                    portfolio_value = self.get_portfolio_combined_value(file["id"])
                else:
                    portfolio_value = 0

                #dough += file.get("gamble_winnings", 0)

                if lifetime is True:
                    if "lifetime_earned_dough" in file.keys():
                        dough += file["lifetime_earned_dough"]
                    if "lifetime_portfolio_value" in file.keys():
                        portfolio_value += file["lifetime_portfolio_value"]
                return dough + portfolio_value
        if search_value.lower() == "stonk_profit":
            def get_value_of_file(file):
                if "id" in file.keys():
                    return self.get_portfolio_combined_value(file["id"])
                else:
                    return 0
        elif search_value.lower() == "portfolio_value":
            def get_value_of_file(file):
                if "id" in file.keys():
                    portfolio_value =  self.get_portfolio_value(file["id"])
                    if (lifetime is True) and ("lifetime_portfolio_value" in file.keys()):
                        portfolio_value += file["lifetime_portfolio_value"]
                    return portfolio_value
                else:
                    return 0
        
        leaderboard = dict()
        total = 0

        all_files = self.json_interface.data["bread"]
        
        if search_all is True:
            def include_file(file):
                return True
        else:
            def include_file(file):
                if "id" not in file.keys():
                    return False
                checked_account = self.json_interface.get_account(file["id"])
                if requester_account.get("prestige_level") == checked_account.get("prestige_level"):
                    return True
                else:
                    return False

        for key in all_files.keys():
            if not key.isdigit():
                continue # skip non-numeric keys
            file = all_files[key]
            #print (f"Investigating {key}: \n{file}")
            if search_value in file or search_value in ["portfolio_value", "stonk_profit","lifetime_dough","dough_combined", "combined_dough"]:
                if include_file(file):
                    
                    #list under username then store value for it
                    
                    # leaderboard[file["username"]] = file[search_value]
                    # leaderboard[key] = file[search_value] # instead of the username, index by id
                    file_value = get_value_of_file(file)
                    leaderboard[key] = file_value
                    total += file_value

        # print the leaderboard for testing purposes
        # for key in leaderboard.keys():
            # print(f"{key} has {leaderboard[key]}")

        sorted_ids = sorted(leaderboard, key=leaderboard.get, reverse=True)
        #top_ten = sorted_names[:10]
        #sorted(A, key=A.get, reverse=True)[:5]
        try: 
            person_position = sorted_ids.index(str(person.id)) # zero justified
        except:
            person_position = -1 # not on the board

        top_width = 10
        if wide_leaderboard is True:
            top_width = 20
        side_width = 4
        if wide_leaderboard is True:
            side_width = 7

        starting_range = max(0, person_position - side_width)
        ending_range = min(len(sorted_ids)-1, person_position + side_width)
        top_entries_to_display = min(top_width, len(sorted_ids))
        # print(F"Person index is {person_position}, starting range is {starting_range}, end of range is {ending_range}, len is {len(sorted_names)}")


        output = f"Leaderboard for {search_value}:\n\n"

        output += f"The combined amount between all people is {utility.smart_number(total)}.\n\n"

        # escape_transform = str.maketrans({"_":  r"\_"}) # lol trans

        for index in range(0,top_entries_to_display):
            # name = sorted_names[index]
            id = sorted_ids[index]
            name = self.json_interface.get_account(id).get_display_name()
            output_name = name # the output from get_display_name is escaped
            # output_name = name.translate(escape_transform)
            if index == person_position:
                #bold the user's name
                output += f"**{index+1}. {output_name}: {utility.smart_number(leaderboard[id])}**\n"
            else:
                #don't bold anyone else's name
                output += f"{index+1}. {output_name}: {utility.smart_number(leaderboard[id])}\n"

            if len(output) > 1900:
                # print (f"output is {len(output)} long")
                await ctx.send(output)
                output = "Leaderboard continued:\n\n"
            

        if starting_range > top_entries_to_display:
            output += "\n" # add spacer
        for index in range(starting_range, ending_range+1):
            if index > top_entries_to_display-1:
                # name = sorted_names[index]
                # output_name = name.translate(escape_transform)
                id = sorted_ids[index]
                name = self.json_interface.get_account(id).get_display_name()
                output_name = name
                if index == person_position:
                    #bold the user's name
                    output += f"**{index+1}. {output_name}: {utility.smart_number(leaderboard[id])}**\n"
                else:
                    #don't bold anyone else's name
                    output += f"{index+1}. {output_name}: {utility.smart_number(leaderboard[id])}\n"
                
                if len(output) > 1900:
                    # print (f"output is {len(output)} long")
                    await ctx.send(output)
                    output = "Leaderboard continued:\n\n"

        # print (f"person position is {person_position}")

        person_display_name = self.json_interface.get_account(person.id).get_display_name()

        if person_position != -1: #if they're actually on the list
            output += f"\n{person_display_name} is at position {person_position+1}."

        await ctx.send(output)
        #await ctx.reply("This doesn't actually do anything yet.")
        pass

    ########################################################################################################################
    #####      BREAD TOTAL

    # the following code will total up the value of a given emote across all users
    @bread.command(
        hidden = True,
        brief= "Totals up a stat.",
    )
    @commands.is_owner() # depreciated
    async def total(self, ctx, value: typing.Optional[str]):
        if value is None:
            await ctx.reply("Please provide something to total up.")
            return

        # use the values module to get the emoji from the string
        emote = values.get_emote(value)
        if emote is not None:
            value = emote.text
        
        total = 0
        all_files = self.json_interface.data["bread"]
        for key in all_files.keys():
            file = all_files[key]
            if value in file:
                total += file[value]

        await ctx.reply(f"The total for {value} is {total}.")

    ########################################################################################################################
    #####      BREAD BLACK_HOLE

    @bread.command(
        hidden = False,
        brief= "Toggles the black hole.",
        aliases = ["blackhole"]
    )
    async def black_hole(self, ctx, state: typing.Optional[str]):

        user_account = self.json_interface.get_account(ctx.author)
        black_hole_value = user_account.get("black_hole")

        if black_hole_value <= 0:
            await ctx.reply("You don't currenlty possess Black Hole Technology.")
            return

        if state is None:
            if black_hole_value == 1:
                user_account.set("black_hole", 2)
            elif black_hole_value == 2:
                user_account.set("black_hole", 1)
        elif state.lower() == "on":
            user_account.set("black_hole", 2)
        elif state.lower() == "off":
            user_account.set("black_hole", 1)
        else:
            await ctx.reply("Please choose either 'on' or 'off'.")
            return

        if user_account.get("black_hole") == 2:
            await ctx.reply("Black hole enabled.")
        elif user_account.get("black_hole") == 1:
            await ctx.reply("Black hole disabled.")
        


    ########################################################################################################################
    #####      BREAD ROLL NEW

    @bread.command(
        hidden= False,
        brief="A tasty bread roll.",
    )
    async def roll(self, ctx):

        #check if they're already rolling
        if ctx.author.id in self.currently_interacting:
            return
        #otherwise we add them to the list
        self.currently_interacting.append(ctx.author.id)

        user_account = self.json_interface.get_account(ctx.author)
        if not user_account.boolean_is("allowed", default=True):
            await ctx.reply("Sorry, you are not allowed to roll.")
            self.currently_interacting.remove(ctx.author.id)
            return

        # start at 10 max rolls
        if not user_account.has("max_daily_rolls", 10):
            user_account.set_value("max_daily_rolls",10)

        if not user_account.has("daily_rolls", 0):
            user_account.set_value("daily_rolls",0)

        # if user_account.has("daily_rolls", user_account.get("max_daily_rolls")) and ctx.channel.name in earnable_channels:
        #     await ctx.reply("Sorry, but that's all the rolls you can do here for today. New rolls are available each day at <t:1653429922:t>.")
        #     return
        
        user_luck = user_account.get("loaf_converter") + 1

        rolls_remaining = user_account.get("max_daily_rolls") - user_account.get("daily_rolls")
        #if ctx.channel.name in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX:
            user_multiroll = 2 ** (user_account.get("multiroller")) # 2 to power of multiroller
            user_multiroll = min(user_multiroll, rolls_remaining) 
            # kick user out if they're out of rolls
            if rolls_remaining == 0:
                await ctx.reply( "Sorry, but that's all the rolls you can do here for today. New rolls are available each day at <t:1653429922:t>.")
                self.currently_interacting.remove(ctx.author.id)
                return
        else:
            user_multiroll = 1

        max_daily_rolls = user_account.get("max_daily_rolls")
        
        ######
        ############################################################

        result = rolls.bread_roll(roll_luck= user_luck, 
                                    roll_count= user_multiroll,
                                    user_account=user_account)

        ############################################################
        ######


        ###########################################################################
        # now we make sure that it's a place they're allowed to roll
        record = False
        allowed_commentary = None

        #check if it's their first ever roll
        if user_account.get("total_rolls") == 0 and channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_MAX:
            record = True
            allowed_commentary = "Thank you for rolling some bread! Just a note, please move any future rolls over to <#967544442468843560>."
        
         #check if it's just not a place to roll at all. We'll give first-timers a pass.
        elif channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_NONE:
            await ctx.reply("Sorry, but you cannot roll bread here. Feel free to do so in <#967544442468843560>.")
            self.currently_interacting.remove(ctx.author.id)
            return
        
        #can be rolled but not recorded
        elif channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_MAX:
            if user_account.get("daily_rolls") == 0:
                allowed_commentary = "Thank you for rolling. Remember, any new rolls will only be saved in <#967544442468843560>."
                record = True
            else:
                allowed_commentary = "Thank you for rolling. Remember, stats are only saved in <#967544442468843560>."
                record = False

        #can be rolled plenty
        elif channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX:
            record = True
        
        # in neutral land -- NOTE-May not be reached
        else:
            if user_account.get("daily_rolls") == 0:
                allowed_commentary = "Thank you for rolling. Please remember to roll in <#967544442468843560>."
                record = True
            else:
                await ctx.reply("Sorry, you can't roll here. Feel free to do so in <#967544442468843560>.")
                self.currently_interacting.remove(ctx.author.id)
                return

        ###########################################################################

        count_commentary = None

        # check how many rolls we have left, reject if none remain
        if channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX:
            amount_remaining = rolls_remaining - user_multiroll
            # amount_remaining =  user_account.get("max_daily_rolls") - user_account.get("daily_rolls")
            if amount_remaining < 0:
                await ctx.reply( "Sorry, but that's all the rolls you can do here for today. New rolls are available each day at <t:1653429922:t>.")
                self.currently_interacting.remove(ctx.author.id)
                return
            #we remove 1 because this check happens *before* the increment, but talks about what happens *after* the increment.
            elif amount_remaining == 0:
                count_commentary = f"That was your last roll for the day."
                # add a special message for new players
                if user_account.get("max_daily_rolls") == 10:
                    count_commentary += '\n\nWould you like to stop by the shop and see what you can get? Check it out with "$bread shop".'
            elif amount_remaining == 1:
                count_commentary = f"You have one more roll today."
            elif amount_remaining <= 3:
                count_commentary = f"You have {amount_remaining} more rolls today."

        ###########################################################################
        #now we record the roll
        
        summarizer_commentary = None

        if record:

            first_catch_remaining = user_account.get("first_catch_remaining")
            result["value"] = 0

            # save the stats
            for key in result.keys():
                if key not in ["commentary", "emote_text", "highest_roll", "roll_messages", "value", "individual_values"]:
                    # this will increase lifetime dough, total dough, and any special values
                    user_account.increment(key,result[key])

                    #first catch boost
                    if first_catch_remaining > 0 and key != ":bread:":
                        emote = values.get_emote(key)
                        if emote is not None:
                            new_value = (emote.value + user_account.get_dough_boost_for_item(emote)) * 3
                            if result.get("gambit_shop_bonus", 0) > 0:
                                result["gambit_shop_bonus"] += user_account.get_dough_boost_for_item(emote) * 3
                            # new_value = min(new_value, 100)
                            result["value"] += user_account.add_dough_intelligent(new_value)
                            first_catch_remaining -= 1
                            print(f"first catch remaining: {first_catch_remaining}, emote: {emote.name}")
                            
            user_account.set("first_catch_remaining", first_catch_remaining)
            
            # update the values in the account
            user_account.increment("daily_rolls", user_multiroll)
            user_account.increment("total_rolls", user_multiroll)

            total_value = 0
            for individual_value in result["individual_values"]:
                total_value += user_account.add_dough_intelligent(individual_value)
            #value = user_account.add_dough_intelligent(result["value"])
            result["value"] += total_value # this is for the summarizer

            #track highest roll separately
            prev_highest_roll = user_account.get("highest_roll")
            if "highest_roll" in result.keys():
                if result["highest_roll"] > prev_highest_roll:
                    user_account.set_value("highest_roll", result["highest_roll"])
                
            self.json_interface.set_account(ctx.author,user_account)

            if channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX and user_account.has("roll_summarizer"):
                summarizer_commentary = rolls.summarize_roll(result)
            

            print (f"{ctx.author.name} rolled {total_value} dough.")

        compound_rolls = 2 ** user_account.get("compound_roller")
        #compound_rolls = 100

        roll_messages = result["roll_messages"]

        # if black hole is active
        if user_account.get("black_hole") == 2 and channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX:
            # we clear out any "unimportant" rolls
            new_roll_messages = []
            for message in roll_messages:
                if values.anarchy_chess.text in message or \
                   values.gem_gold.text in message:
                    new_roll_messages.append(message)
            roll_messages = new_roll_messages


        # for a non-compound roll, the output is just the input
        if compound_rolls == 1:
            output_messages = roll_messages

        # for a compound roll, we start building the messages up into groups
        elif compound_rolls > 1:
            output_messages = []

            # for as long as we have messages to output
            while len(roll_messages) > 0:
                compound_message = ""
                for i in range(compound_rolls):
                    if len(roll_messages) > 0:
                        potential_addition = roll_messages.pop()

                        # check to make sure we don't hit the length limit
                        if len(compound_message) + len(potential_addition) > 1900:
                            # put it back on the list if it would be too long
                            roll_messages.append(potential_addition)
                            continue

                        compound_message += potential_addition

                        # if there's still messages left, add a space
                        if len(roll_messages) > 0:
                            #if len(compound_message) + len (roll_messages[-1]) < 1900: #getting at -1 is peek function
                            if i < compound_rolls - 1: # if there's still space to go
                                compound_message += "\n---\n"
                output_messages.append(compound_message)
            
        # check if black hole is activated and if we're in #bread-rolls
        if user_account.get("black_hole") == 2 and channel_permission_levels.get(ctx.channel.name, 0) == PERMISSION_LEVEL_MAX:
            await utility.smart_reply(ctx, ":cyclone:")
        
        # black hole is not activated, send messages normally
        for roll in output_messages:
            await utility.smart_reply(ctx, roll)
            if len(output_messages) > 1:
                await asyncio.sleep(.75)
                
        output_commentary = ""

        roll_commentary = result["commentary"]
        if roll_commentary is not None:
            
            output_commentary += roll_commentary

        #add the last bit on
        if allowed_commentary is not None:
            output_commentary += "\n\n" + allowed_commentary


        if count_commentary is not None:
            output_commentary += "\n\n" + count_commentary

        if summarizer_commentary is not None:
            output_commentary += "\n\n" + summarizer_commentary

        try:
            if output_commentary != "" and not output_commentary.isspace():
                
                await utility.smart_reply(ctx, output_commentary)
                
        except:
            pass

        await self.do_chessboard_completion(ctx)

        #now we remove them from the list of rollers, this allows them to roll again without spamming
        self.currently_interacting.remove(ctx.author.id)

    ########################################################################################################################
    #####      do CHESSBOARD COMPLETION

    async def do_chessboard_completion(self, ctx, force: bool = False, amount = None):

        user_account = self.json_interface.get_account(ctx.author)

        if user_account.get("auto_chessatron") is False and force is False:
            return
        
        print ("doing chessatron creation")

        # user_chess_pieces = user_account.get_all_items_with_attribute_unrolled("chess_pieces")
        full_chess_set = values.chess_pieces_black_biased+values.chess_pieces_white_biased

        # leftover_pieces = utility.array_subtract((full_chess_set), user_chess_pieces )
        #print(f"{ctx.author} has {len(leftover_pieces)} pieces left to collect.")
        #print(f"Those pieces are: {leftover_pieces}")

        summary = False
        summary_count = 0

        # pointwise integer division between the full chess set and the set of the user's pieces.
        valid_trons = min([user_account.get(x.text) // full_chess_set.count(x) for x in values.all_chess_pieces])

        # iteration ends at the minimum value, make sure amount is never the minimum. 'amount is None' should mean no max ...
        # ... has been specified, so make as many trons as possible.
        if amount is None: 
            amount = valid_trons + 1

        print(f"valid trons: {valid_trons}, amount: {amount}")

        # stop iteration when you can't make any more trons, or have hit the limit of specified trons; whichever comes first.
        for _ in range(min(valid_trons, amount)):

            board = Bread_cog.format_chess_pieces(user_account.values)

            # start at 2000
            chessatron_value = values.chessatron.value

            # figure out how much shadow boost to add
            shadow_boost_max = store.chessatron_shadow_booster_levels[ user_account.get("chessatron_shadow_boost") ]
            shadowmega_count = user_account.get(values.shadowmega_chessatron.text)
            shadow_boost = min(shadow_boost_max, shadowmega_count) * 100
            chessatron_value += shadow_boost

            # add omegas
            omega_count = user_account.get(values.omega_chessatron.text)
            chessatron_value += omega_count * 250

            # finally add the dough and chessatron
            chessatron_result_value = user_account.add_dough_intelligent(chessatron_value)
            user_account.add_item_attributes(values.chessatron)
            
            # chessatron_value = user_account.add_item(values.chessatron)

            # now remove the chess set and increment some stuff
            for emote in full_chess_set:
                user_account.increment(emote.text, -1)

            if user_account.get(values.chessatron.text) < 5:
                await utility.smart_reply(ctx, f"You have collected all the chess pieces! Congratulations!\n\nWhat a beautiful collection!")
                await asyncio.sleep(1)

                await utility.smart_reply(ctx, f"{board}")
                await asyncio.sleep(1)

                await utility.smart_reply(ctx, f"You will now be awarded the most prestigious of chess pieces: The Mega Chessatron!")
                await asyncio.sleep(1)

                await utility.smart_reply(ctx, f"{values.chessatron.text}")
                await asyncio.sleep(1)
                await utility.smart_reply(ctx, f"May it serve you well. You also have been awarded **{chessatron_result_value} dough** for your efforts.")
            elif user_account.get(values.chessatron.text) < 20:
                await asyncio.sleep(1)
                await utility.smart_reply(ctx, f"Congratulations! You've collected all the chess pieces again! This will be chessatron **#{user_account.get(values.chessatron.text)+1}** for you.\n\n{board}\nHere is your award of **{chessatron_result_value} dough**, and here's your new chessatron!")
                await asyncio.sleep(1)
                await utility.smart_reply(ctx, f"{values.chessatron.text}")
                #await ctx.reply(f"You have collected all the chess pieces! Congratulations!\n\nWhat a beautiful collection!\n\n{board}\n\nYou will now be awarded the most prestigious of chess pieces: The Mega Chessatron!\n\n{values.chessatron.text}\n\nMay it serve you well. You also have been awarded **2000 dough** for your efforts.")
            else:
                summary = True
                summary_count += 1
                
            
            #user_account.increment("total_dough", 2000)
            #user_account.increment("full_chess_set", 1)

            # user_chess_pieces = user_account.get_all_items_with_attribute_unrolled("chess_pieces")
            # leftover_pieces = utility.array_subtract((full_chess_set), user_chess_pieces )

        #after the while loop we take all our summary count of chessatrons and announce them together
        if summary:
            output = f"Congratulations! More chessatrons! You've made {summary_count} of them. Here's your reward of **{utility.smart_number(chessatron_result_value*summary_count)} dough**."
            await utility.smart_reply(ctx, output)
            await asyncio.sleep(1)
            
            output = ""
            for i in range(summary_count):
                output += f"{values.chessatron.text} "
                if len(output) > 1800:
                    await utility.smart_reply(ctx, output)
                    output = ""
                    await asyncio.sleep(1)
            await utility.smart_reply(ctx, output)
    

    ########################################################################################################################
    #####      BREAD CHESSATRON

    @bread.command(
        name="chessatron", 
        aliases=["auto_chessatron"],
        help="Toggle auto chessatron on or off. If no argument is given, it will create as many chessatrons for you as it can.",
        usage="on/off",
        brief="Toggle auto chessatron on or off."

    )
    async def chessatron(self, ctx, arg: typing.Optional[str] = None) -> None:
        """Toggle auto chessatron on or off."""
        
        user_account = self.json_interface.get_account(ctx.author)

        if arg is None:
            arg = ""
        
        if arg.lower() == "on":
            user_account.set("auto_chessatron", True)
            await utility.smart_reply(ctx, f"Auto chessatron is now on.")
        elif arg.lower() == "off":
            user_account.set("auto_chessatron", False)
            await utility.smart_reply(ctx, f"Auto chessatron is now off.")
        else:
            if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
                await utility.smart_reply(ctx, f"Thank you for your interest in creating chessatrons! You can do so over in <#967544442468843560>.")
                return
            
            if arg.isnumeric():
                await self.do_chessboard_completion(ctx, True, amount = int(arg))
            else:
                await self.do_chessboard_completion(ctx, True)

        self.json_interface.set_account(ctx.author, user_account)
        

    ########################################################################################################################
    #####      BREAD GEM_CHESSATRON

    @bread.command(
        help="Create a chessatron from red gems.",
    )
    async def gem_chessatron(self, ctx, arg = None):

        user_account = self.json_interface.get_account(ctx.author)
        gem_count = user_account.get(values.gem_red.text)

        if gem_count < 32:
            await utility.smart_reply(ctx, f"You need at least 32 red gems to create a chessatron.")
            return
        
        number_of_chessatrons = gem_count // 32 # integer division

        user_account.increment(values.gem_red.text, -32*number_of_chessatrons)

        user_account.increment(values.black_pawn.text, 8*number_of_chessatrons)
        user_account.increment(values.black_rook.text, 2*number_of_chessatrons)
        user_account.increment(values.black_knight.text, 2*number_of_chessatrons)
        user_account.increment(values.black_bishop.text, 2*number_of_chessatrons)
        user_account.increment(values.black_queen.text, 1*number_of_chessatrons)
        user_account.increment(values.black_king.text, 1*number_of_chessatrons)

        user_account.increment(values.white_pawn.text, 8*number_of_chessatrons)
        user_account.increment(values.white_rook.text, 2*number_of_chessatrons)
        user_account.increment(values.white_knight.text, 2*number_of_chessatrons)
        user_account.increment(values.white_bishop.text, 2*number_of_chessatrons)
        user_account.increment(values.white_queen.text, 1*number_of_chessatrons)
        user_account.increment(values.white_king.text, 1*number_of_chessatrons)

        self.json_interface.set_account(ctx.author, user_account)

        await utility.smart_reply(ctx, f"You have used {32*number_of_chessatrons} red gems to make chessatrons.")

        if arg.isnumeric():
            arg = int(arg)
        else: arg = None

        await self.do_chessboard_completion(ctx, True, amount = int(arg))

    ########################################################################################################################
    #####      BREAD SPELLCHECK

    # toggles whether the default of calling bread without arguments is to succeed or not
    @bread.command(
        name="spellcheck", 
        aliases=["spell_check"],
        help="Toggle spellcheck on or off. If no argument is given, it will toggle the current setting.",
        usage="on/off",
        brief="Toggle spellcheck on or off."

    )
    async def spellcheck(self, ctx, toggle: typing.Optional[str] = None):
        """Toggle spellcheck on or off."""

        user_account = self.json_interface.get_account(ctx.author)

        if toggle is None:
            toggle = ""
        
        if toggle.lower() == "on":
            user_account.set("spellcheck", True)
            await utility.smart_reply(ctx, f"Spellcheck is now on.")
        elif toggle.lower() == "off":
            user_account.set("spellcheck", False)
            await utility.smart_reply(ctx, f"Spellcheck is now off.")
        else:
            user_account.set("spellcheck", not user_account.get("spellcheck"))
            if user_account.get("spellcheck"):
                await utility.smart_reply(ctx, f"Spellcheck is now on.")
            else:
                await utility.smart_reply(ctx, f"Spellcheck is now off.")

        self.json_interface.set_account(ctx.author, user_account)


    ########################################################################################################################
    #####      BREAD ASCEND

    @bread.command(
        name="ascend", 
        aliases=["ascension", "rebirth", "prestige"]
    )
    async def ascend(self, ctx):
        """Ascend to a higher plane of existence."""
        
        user_account = self.json_interface.get_account(ctx.author)
        prestige_level = user_account.get_prestige_level()

        prestige_file = self.json_interface.get_custom_file("prestige")
        if "max_prestige_level" in prestige_file:
            max_prestige_level = prestige_file["max_prestige_level"]
        else:
            max_prestige_level = 1

        # max_prestige_level = 3

        ascend_dough_cost = (prestige_level * 250000) # starts at 500k and goes up
        daily_rolls_requirement = 1000 + prestige_level * 100
        
        # if prestige_level >= max_prestige_level:
        #     await ctx.reply(f"You are already at the highest level of ascension which is currently available.")
        #     return

        if user_account.get("max_daily_rolls") < 1000:
            await ctx.reply(f"{utility.smart_number(daily_rolls_requirement)} daily rolls is not the only requirement to ascend, but it is the first one. Come back when you have that many.")
            return

        description = "An **ascension** is a powerful thing. It will reset your progress and you will start over from scratch.\n"
        description += "However, in return, you will recieve a few things:\n\n"
        description += "-You will gain access to a special shop, and to the currency you can spend there.\n"
        description += "-You will have a higher limit for how many daily rolls you can buy.\n"
        description += "-And the dough you roll will be worth more.\n\n"

        description += "**In order to ascend, you need the following:**\n"
        description += f"-{utility.smart_number(daily_rolls_requirement)} daily rolls\n"
        # description += f"-{utility.smart_number(ascend_dough_cost)} dough\n"
        # description += "-A golden gem\n\n"
        description += "-128 loaf converters\n"
        description += "-200 chessatrons\n\n"


        can_ascend = (user_account.get("max_daily_rolls") >= daily_rolls_requirement) and \
                        (user_account.get(values.chessatron.text) >= 200) and \
                        (user_account.get("loaf_converter") >= 128)
                        # (user_account.get(values.gem_gold.text) >= 1)
                        # (user_account.get("total_dough") >= ascend_dough_cost) and \

        if prestige_level >= max_prestige_level:
            description += "**You are already at the highest level of ascension which is currently available.**\n\n"
            await ctx.reply(description)
            return

        if not can_ascend:
            description += "\n**You cannot ascend yet.**\n\n"
            await ctx.reply(description)
            return
        else:
            description += "\n**You can ascend!**\n\n"

        description += """If you would like to ascend, please type "I would like to ascend". Remember that this is a permanent action that cannot be undone."""

        await utility.smart_reply(ctx, description)

        def check(m: discord.Message):  # m = discord.Message.
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
        try:
            msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
        except asyncio.TimeoutError: 
            await utility.smart_reply(ctx, "If you are not ready yet, that is okay.")
            return 
        
        response = msg.content
        if "i would like to ascend" in response.lower():
            pass
        else:
            await utility.smart_reply(ctx, "If you are not ready yet, that is okay.")
            return 

        # now we can ascend
        #user_account.increment(values.gem_gold.text, -1) # first remove the golden gem
        user_account.increase_prestige_level()

        description = f"Congratulations! You have ascended to a higher plane of existence. You are now at level {user_account.get_prestige_level()} of ascension. I wish you the best of luck on your journey!\n\n"
        description += f"You have also recieved **1 {values.ascension_token.text}**. You will recieve more as you get more daily rolls. You can spend it at the hidden bakery to buy special upgrades. Find it with \"$bread hidden_bakery\"."
        await utility.smart_reply(ctx, description)

        # and save the account
        self.json_interface.set_account(ctx.author, user_account)

    ########################################################################################################################
    #####      BREAD SHOP / BREAD STORE

    #this one, we'll have display the available items, and have the "buy" function actually purchase them
    @bread.command(
        hidden=False,
        aliases=["store"],
        brief= "Spend your hard-earned dough.",
        help = "Shows what's available to purchase.\n\nUse '$bread buy <item>' to buy an item from the store.\n\nOnly works in #bread-rolls."
    )
    async def shop(self, ctx):

        # first we make sure this is a valid channel
        #if ctx.channel.name not in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Hi! Thanks for visiting the bread shop. Our nearest location is over in <#967544442468843560>.")
            return
        
        # we get the account of the user who called it
        user_account = self.json_interface.get_account(ctx.author)

        # now we get the list of items
        items = self.get_buyable_items(user_account, store.normal_store_items)

        output = ""
        output += f"Welcome to the store! You have **{user_account.get('total_dough')} dough**.\n\*Prices subject to change.\nHere are the items available for purchase:\n\n"
        for item in items:
            output += f"\t**{item.display_name}** - {item.get_price_description(user_account)}\n{item.description(user_account)}\n\n"
        
        if len(items) == 0:
            output += "Sorry, but you can't buy anything right now. Please try again later."
        else:
            output += 'To buy an item, just type "$bread buy [item name]".'

        output += "\n\nDon't forget to check out the **gambit shop**. Find it with \"$bread gambit_shop\"." #

        if user_account.get_prestige_level() >= 1:
            output += "\nYou can also buy items from the **hidden bakery**. Find it with \"$bread hidden_bakery\"."

        await ctx.reply(output)
        return

    ########################################################################################################################
    #####      BREAD ASCENSION_SHOP / BREAD HIDDEN_BAKERY

    #this is the shop for the ascension items, and can only be accessed once a user has at least 1 prestige
    @bread.command(
        aliases = ["hidden", "secret_shop", "ascension_shop"],
        brief = "Spend your ascension tokens.",
    )
    async def hidden_bakery(self, ctx):
            
            # first we make sure this is a valid channel
            #if ctx.channel.name not in earnable_channels:
            if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
                await ctx.reply("Hi! Thanks for visiting the hidden bakery. You can find us in <#967544442468843560>.")
                return
            
            # we get the account of the user who called it
            user_account = self.json_interface.get_account(ctx.author)
    
            if user_account.get_prestige_level() < 1:
                await ctx.reply("The door to this shop seems to be locked.")
                return

            # now we get the list of items
            items = self.get_buyable_items(user_account, store.prestige_store_items)
    
            output = ""
            output += f"Welcome to the hidden bakery! All upgrades in this shop are permanent, and persist through ascensions. You have **{user_account.get(values.ascension_token.text)} {values.ascension_token.text}**.\n\*Prices subject to change.\nHere are the items available for purchase:\n\n"
            for item in items:
                output += f"\t**{item.display_name}** - {item.get_price_description(user_account)}\n{item.description(user_account)}\n\n"
            
            if len(items) == 0:
                output += "**It looks like you've bought everything here. Well done.**"
            else:
                output += 'To buy an item, just type "$bread buy [item name]".'
    
            await ctx.reply(output)
            return

    ########################################################################################################################
    #####      BREAD GAMBIT_SHOP

    # this is the gambit shop, which can be accessed at any point
    @bread.command(
        aliases = ["strategy_store", "strategy_shop", "gambit", "strategy"],
    )
    async def gambit_shop(self, ctx):
        
        # first we make sure this is a valid channel
        #if ctx.channel.name not in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Hi! Thanks for visiting the gambit shop. Our nearest location is over in <#967544442468843560>.")
            return
        
        # we get the account of the user who called it
        user_account = self.json_interface.get_account(ctx.author)

        # now we get the list of items
        items = self.get_buyable_items(user_account, store.gambit_shop_items)

        output = ""
        output += f"Welcome to the gambit shop! Here are the items available for purchase:\n\n"
        for item in items:
            addition = f"\t**{item.display_name}** - {item.get_price_description(user_account)}\n{item.description(user_account)}\n\n"
            if len(output) + len(addition) > 1800:
                await utility.smart_reply(ctx, output)
                output = "Shop Continued:\n\n"
            output += addition
            # if len(output) > 1800:
            #     await utility.smart_reply(ctx, output)
            #     output = "Shop Continued:\n\n"
        
        if len(items) == 0:
            output += "**It looks like you've bought everything here. Well done.**"
        else:
            output += 'To buy an item, just type "$bread buy [item name]".'

        await utility.smart_reply(ctx, output)
        return

    ########################################################################################################################
    #####      BREAD BUY

    # this lets us purchase items we see in the store
    @bread.command(
        hidden=False,
        aliases=["purchase"],
        help= "Usage: $bread buy [item name]\n\nBuys an item from the bread store. Only works in #bread-rolls.",
        brief= "Buy an item from the bread shop.",
    )
    async def buy(self, ctx, *, item_name: typing.Optional[str]):

        if item_name is None:
            await ctx.reply("Please specify an item to buy.")
            return

        # first we make sure this is a valid channel
        #if ctx.channel.name not in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Thank you for your interest in purchasing an item from the store. Please visit our nearby location in <#967544442468843560>.")
            return

        # split the first word of the item name and check if it's a number
        item_count = 1
        item_name_split = item_name.split(" ")
        if len(item_name_split) > 1:
            if item_name_split[0][0] == '-':
                await ctx.reply("You can't buy negative numbers of items.")
                return
            if item_name_split[0].isdigit():
                item_name = " ".join(item_name_split[1:])
                item_count = int(item_name_split[0])
            if item_name_split[0] == "all":
                item_name = " ".join(item_name_split[1:])
                item_count = 100000

        # remove trailing 's' from the item name
        if len(item_name) > 1 and item_name[-1] == "s":
            item_name_2 = item_name[:-1]
        else:
            item_name_2 = item_name

        if item_count < 1:
            await ctx.reply("You can't buy zero of an item.")
            return

        # first we get the account of the user who called it
        user_account = self.json_interface.get_account(ctx.author)

        # now we get the list of items
        if user_account.get_prestige_level() < 1:
            buyable_items = self.get_buyable_items(user_account, store.normal_store_items)
            buyable_items.extend(self.get_buyable_items(user_account, store.gambit_shop_items))
        else: # has achieved a prestige level
            buyable_items = self.get_buyable_items(user_account, store.all_store_items)
        all_items = store.all_store_items


        # now we check if the item is in the list

        item_name = item_name.lower()

        item = None
        for i in all_items:
            if i.name.lower() == item_name or i.display_name.lower() == item_name:
                item = i
                break
            # this is for the item's name minus a trailing "s"
            if i.name.lower() == item_name_2 or i.display_name.lower() == item_name_2:
                item = i
                break
        else: # if the for loop doesn't break, run this. This should run the same as an 'if item is None' check.
            await ctx.reply("Sorry, but I don't recognize that item's name.")
            return


        def describe_cost(item_text):
            amount = user_account.get(item_text)
            if item_text == "total_dough":
                return f"**{utility.smart_number(amount)} dough**"
            else:
                return f"**{utility.smart_number(amount)} {item_text}**"

        def describe_cost_list(cost_list):
            if len(cost_list) == 1:
                cost_text = f"You now have {describe_cost(cost_list[0])} remaining."
            elif len(cost_list) == 2:
                cost_text = f"You now have {describe_cost(cost_list[0])} and {describe_cost(cost_list[1])} remaining."
            else:
                cost_text = "You now have "
                length = len(cost_list)
                for i in range(length):
                    cost_text += describe_cost(cost_list[i])
                    if i < length-1:
                        cost_text += ", " 
                    if i == length-2:
                        cost_text += "and "
                cost_text += " remaining."
            return cost_text

        if item_count == 1:

            # if it exists but can't be bought, we say so
            if item not in buyable_items:
                # removed item is None check, as item will never be None. see above.
                await ctx.reply("Sorry, but you've already purchased as many of that as you can.")
                return

            # now we check if the user has enough dough
            if not item.is_affordable_for(user_account):
                await ctx.reply("Sorry, but you can't afford to buy that.")
                return

            # now we actually purchase the item
            #user_account.increment("total_dough", -item.cost(user_account))
            print(f"{ctx.author.display_name} bought {item.display_name} for {item.cost(user_account)} dough")

            #print(f"item is {item}, user account is {user_account}, tuple is {(item, user_account)}")
            text = item.do_purchase(user_account)
            #user_account.increment(item.name, 1)
            self.json_interface.set_account(ctx.author,user_account)

            all_cost_types = item.get_cost_types(user_account)

            

            if len(all_cost_types) == 1:
                cost_text = f"You now have {describe_cost(all_cost_types[0])} remaining."
            elif len(all_cost_types) == 2:
                cost_text = f"You now have {describe_cost(all_cost_types[0])} and {describe_cost(all_cost_types[1])} remaining."
            else:
                cost_text = "You now have "
                length = len(all_cost_types)
                for i in range(length):
                    cost_text += describe_cost(all_cost_types[i])
                    if i < length-1:
                        cost_text += ", " 
                    if i == length-2:
                        cost_text += "and "
                cost_text += " remaining."

            if item in store.prestige_store_items:
                #await ctx.reply(f"Congratulations! You've unlocked the **{item.display_name}**! {text}")
                if text is None:
                    text = f"Congratulations! You've unlocked the **{item.display_name}** upgrade! You are now at level {user_account.get(item.name)}."
                
                #text += f"\n\nYou now have **{user_account.get(values.ascension_token.text)} {values.ascension_token.text}** remaining."
            else:
                if text is None:
                    text = f"You have purchased a {item.display_name}! You now have {user_account.get(item.name)} of them."

                #text += f"\n\nYou now have **{user_account.get('total_dough')} dough** remaining."

            text += "\n\n" + cost_text

            await ctx.reply(text)

        else: # item count above 1

            # why make a new reference to store.all_store_items? all_items is already set to that.
            buyable_items = self.get_buyable_items(user_account, all_items)

            # revised buying code

            
            # check if the current class has the purchase_upper method
            if 'find_max_purchasable_count' in dir(i):
                max_purchasable = i.find_max_purchasable_count(user_account)

                # what's cool about this is all the price checks are done WITHIN find_max_purchasable_count
                # so we don't even have to check. purchase_num *should* be a valid purchase amount.
                # if item_count is larger than the amount you can afford, max_purchasable should be lower.
                # if you don't want to buy as much as you can, item_count will be lower.
                purchase_num = min(item_count,max_purchasable)

                # purchase the item! do_purchase modified to allow for item counts.
                # only items with the purchase_upper method should have the modified code.
                text = item.do_purchase(user_account,amount = purchase_num)

                purchased_count = purchase_num

            else:
                # old code, for use with items that don't have find_max_purchasable_count
                purchased_count = 0
                for i in range(item_count):

                    # buyable_items = self.get_buyable_items(user_account, all_items)
                    
                    # if item not in buyable_items:
                    #     break # if we've bought as many as we can legally

                    if not item.can_be_purchased(user_account):
                        break # if we've bought as many as we can legally

                    if not item.is_affordable_for(user_account):
                        break # if we've spent all our dough

                    text = item.do_purchase(user_account)
                    #user_account.increment(item.name, 1)

                    purchased_count += 1


            self.json_interface.set_account(ctx.author,user_account)

            print(f"{ctx.author.display_name} bought {purchased_count} {item.display_name}")
            if item in store.prestige_store_items:
                if text is None:
                    text = f"You have purchased {purchased_count} {item.display_name} upgrades! You are now at level {user_account.get(item.name)}."
                # text += f"\n\nYou now have **{user_account.get(values.ascension_token.text)} {values.ascension_token.text}** remaining."
            else: #normal item
                if text is None:
                    text = f"You have purchased {utility.write_count(purchased_count, item.display_name)}."# \n\nYou now have **{user_account.get('total_dough')} dough** remaining."

            # this will only describe the cost for the most recent level of the item purchased, but it's better than nothing.
            all_cost_types = item.get_cost_types(user_account)
            cost_text = describe_cost_list(all_cost_types)

            text += "\n\n" + cost_text

            await ctx.reply(text)


        # complete chessatron on this command
        if ctx.author.id in self.currently_interacting:
            return
        self.currently_interacting.append(ctx.author.id)
        await self.do_chessboard_completion(ctx)
        self.currently_interacting.remove(ctx.author.id)

        return


    # this function finds all the items the user is allowed to purchase
    def get_buyable_items(self, user_account: account.Bread_Account, item_list: "list[store.Store_Item]") -> "list[store.Store_Item]":
        # user_account = self.json_interface.get_account(ctx.author)
        output = []
        #for item in store.all_store_items:
        for item in item_list:
            # level = user_account.get(item.name)
            if item.can_be_purchased(user_account):
                output.append(item)
        return output

    

    ########################################################################################################################
    #####      BREAD GIFT

    bread_gift_text = """
You can gift both dough and items through this command.

For instance, "$bread gift Melodie 5" would gift 5 dough to Melodie.
"$bread gift Melodie 5 dough" also works.

Likewise, "$bread gift Melodie :croissant:" would gift a :croissant:,
and "$bread gift Melodie 5 :croissant:" would gift 5 of them.

Special stats, such as special_bread, cannot be gifted or transferred.
"""

    @bread.command(
        brief="Gives bread away.",
        help="Usage: $bread gift [person] [amount] [item]\n"+bread_gift_text,
        aliases=["pay"]
    )
    async def gift(self, ctx, target: typing.Optional[discord.Member], 
                    arg1: typing.Optional[typing.Union[int, str]], 
                    arg2: typing.Optional[typing.Union[int, str]]):
        # await ctx.reply("This function isn't ready yet.")

        if target is None: #then it's empty and we'll tell them how to use it.
            await ctx.reply(self.bread_gift_text)
            return

        sender_account = self.json_interface.get_account(ctx.author)
        receiver_account = self.json_interface.get_account(target)

        #file = self.json_interface.get_file_for_user(ctx.author)
        if "allowed" in sender_account.values.keys():
            if sender_account.values["allowed"] == False:
                await ctx.reply("Sorry, you are not allowed to gift bread.")
                return

        if receiver_account.get_prestige_level() > sender_account.get_prestige_level():
            if receiver_account.get("id") != 960869046323134514: # always can gift to MM
                await ctx.reply("Sorry, you can't gift to someone who has a higher ascension level than you.")
                return

        #shitty way of converting to int
        try:
            arg1 = int(arg1)
        except:
            pass
        try:
            arg2 = int(arg2)
        except:
            pass
        
        # print(f"arg1 type was {type(arg1)} and arg2 type was {type(arg2)}")
        if type(arg1) is int and type(arg2) is str:
            amount = arg1
            emoji = arg2
        elif type(arg1) is str and type(arg2) is int:
            amount = arg2
            emoji = arg1

        # check if there's just a string, AKA gifting just one    
        elif (type(arg1) is str and arg2 is None):
            emoji = arg1
            amount = 1
        elif (type(arg1) is int and arg2 is None):
            emoji = "dough"
            amount = arg1
        else:
            await ctx.reply("Needs an amount and what to gift.")
            return

        if ctx.author.id == target.id:
            await ctx.reply("You can't gift bread to yourself, silly.")
            print(f"rejecting self gift request from {target.display_name} for amount {amount}.")
            
            return

        if (amount < 0):
            print(f"Rejecting steal request from {ctx.author.display_name}")
            await ctx.reply("Trying to steal bread? Mum won't be very happy about that.")
            await ctx.invoke(self.bot.get_command('brick'), member=ctx.author, duration="10")
            return
        
        if (amount == 0):
            print(f"Rejecting 0 bread request from {ctx.author.display_name}")
            await ctx.reply("That's not much of a gift.")
            return

        

        emote = None

        if (emoji.lower() == "dough"):
            item = "total_dough"
            pass
        else:
            # print(f"checking for gift with text {emoji}")
            emote = values.get_emote(emoji)
            if (emote is None) or (emote.can_be_gifted() == False):
                # print("failed to find emote")
                await ctx.reply("Sorry, that's not a giftable item.")
                return
            
            item = emote.text
        
        # enforce maxumum gift amount to players of lower prestige level
        if receiver_account.get_prestige_level() < sender_account.get_prestige_level() and \
            item == "total_dough" and \
            receiver_account.get("id") != 960869046323134514: #machine mind
            already_gifted = receiver_account.get("daily_gifts")
            max_gift = receiver_account.get_maximum_daily_gifts()
            leftover = max_gift - already_gifted
            if leftover <= 0:
                await ctx.reply("Sorry, they've already received as much dough as they can today.")
                return
            if amount > leftover:
                await ctx.reply(f"Sorry, they can only recieve {leftover} more dough today. I will gift them that much.")
                amount = leftover
            if sender_account.has(item, amount):
                receiver_account.increment("daily_gifts", amount)
            else:
                await ctx.reply("Except you don't have that much dough to give. Too bad.")
                return

        # no gifting stonks to people of lower prestige level
        if receiver_account.get_prestige_level() < sender_account.get_prestige_level() and \
            emote is not None and \
            receiver_account.get("id") != 960869046323134514: #machine mind
            if emote.text in all_stonks:
                await ctx.reply("Sorry, you can't gift stonks to people of lower prestige level.")
                return

        # sender_account = self.json_interface.get_account(ctx.author)
        # receiver_account = self.json_interface.get_account(target)
        #if emote[]
        if emote is None:
            if sender_account.has(item, amount):
                sender_account.increment(item, -amount)
                receiver_account.increment(item, amount)
                print(f"{amount} dough has been gifted to {target.display_name} by {ctx.author.display_name}.")
                await ctx.send(f"{amount} dough has been gifted to {target.mention}.")
            else:
                await ctx.reply("You don't have enough dough to gift that much.")
        else:
            if sender_account.has(item, amount):
                sender_account.increment(item, -amount)
                receiver_account.increment(item, amount)
                print(f"{amount} {item} has been gifted to {target.display_name} by {ctx.author.display_name}.")
                await ctx.send(f"{amount} {item} has been gifted to {target.mention}.")
            else:
                await ctx.reply("You don't have enough of that to gift.")
            #  we will not gift attributes after all, those will be trophies for the roller
            # for atrribute in emote.attributes:
            #     if sender_account.has(atrribute, amount):
            #         sender_account.increment(atrribute, -amount)
            #         receiver_account.increment(atrribute, amount)
        
        self.json_interface.set_account(ctx.author, sender_account)
        self.json_interface.set_account(target, receiver_account)

        # elif type(arg1) is None or type(arg2) is None:
        #     await ctx.reply("Needs an amount and what to gift.")
        #     return
        
        

    ########################################################################################################################
    #####      BREAD GAMBLE

    bread_gamble_info=\
"""In order to gamble, wager an amount.
The minimum wager is 4 and the maximum is 50.
You can gamble up to 20 times a day.
The results are worth the following:
horsey - Nothing.
fruit - 25% of your wager.
bread - 50% of your wager.
special bread - 200% of your wager.
chess piece - 400% of your wager.
anarchy - 1000% of your wager.
"""

    #gamble_list = []

    @bread.command(
        brief= "Risk / Reward.",
        help=bread_gamble_info
    )
    async def gamble(self, ctx, amount: typing.Optional[int] ):
        if amount is None:
            await ctx.send(self.bread_gamble_info)
            return

        #if ctx.channel.name not in earnable_channels:
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Sorry, but you can only do that in <#967544442468843560>.")
            return

        print(f"{ctx.author.display_name} gambled {amount} dough")

        user_account = self.json_interface.get_account(ctx.author)
        if user_account.has("total_dough", amount):
            pass
        else:
            await ctx.reply("You don't have that much dough.")
            return
        

        minimum_wager = 4

        gamble_level = user_account.get("gamble_level")
        gamble_levels = [50, 500, 1500, 5000, 10000, 100000, 10000000]
        if gamble_level < len(gamble_levels):
            maximum_wager = gamble_levels[gamble_level]
        else:
            maximum_wager = 100000

        if amount < minimum_wager:
            await ctx.reply(f"The minimum wager is {minimum_wager}.")
            return

        max_gambles = user_account.get("max_gambles")
        if user_account.has("daily_gambles", max_gambles):
            await ctx.reply(f"Sorry, you can only gamble {max_gambles} times today, unless you'd like to buy more passes at the shop.")
            return
        
        # Checks list of people currently gambling to prevent spam.
        # if they're already on the list
        if ctx.author.id in self.currently_interacting:
            print(f"rejecting duplicate request from {ctx.author.display_name}")
            return
        self.currently_interacting.append(ctx.author.id)

        if amount > maximum_wager:
            await ctx.reply(f"The maximum wager is {maximum_wager}. I'll enter that in for you.")
            await asyncio.sleep(1)
            amount = maximum_wager

        user_account.increment("total_dough", -amount) 
        user_account.increment("daily_gambles", 1)
        user_account.increment("lifetime_gambles", 1)
        
        

        result = gamble.gamble()
        winnings = int(amount * result["multiple"])
        #await ctx.send(f"You got a {result['result'].text} and won {winnings} dough.")

        #make grid
        grid = list()
        grid_size = 4
        for x in range(grid_size):
            grid.append([None] * grid_size)

        # grid.append([None, None, None])
        # grid.append([None, None, None])
        # grid.append([None, None, None])

        winning_x = random.randint(0,grid_size-1)
        winning_y = random.randint(0,grid_size-1)
        winning_text = result['result'].text

        # add winning result to grid
        grid[winning_x][winning_y] = winning_text

        # losing rows/columns that will get deleted
        rows_to_remove = list(range(grid_size))
        rows_to_remove.remove(winning_y)

        columns_to_remove = list(range(grid_size))
        columns_to_remove.remove(winning_x)

        # fill grid with other stuff
        for i in range(grid_size):
            for k in range(grid_size):
                if grid[i][k] is None:
                    filler = gamble.gamble()['result'].text
                    grid[i][k] = filler
                    # grid[i][k] = random.choice(gamble.reward_values).text
        try:  #sometimes we'll get a timeout error and the function will crash, this should allow
              # the user to be removed from the currently_interacting list
            message = await utility.smart_reply(ctx, Bread_cog.show_grid(grid))
            await asyncio.sleep(2)


            #runs as often as rows/columns need to be removed
            for snips_left in range(grid_size*2 - 2, 0, -1):

                # pick a random row/column
                what_to_snip = random.randint(0, snips_left - 1)

                if what_to_snip < len(rows_to_remove): #do row
                    y = rows_to_remove.pop(what_to_snip)
                    for x in range(grid_size):
                        grid[x][y] = None
                    
                else: #do column
                    x = columns_to_remove.pop(what_to_snip - len(rows_to_remove))
                    for y in range(grid_size):
                        grid[x][y] = None
                
                await message.edit(content= Bread_cog.show_grid(grid))
                await asyncio.sleep(1.5)

                
        except: 
            pass
        try: #try block because of potential messsage deletion.
            if result['result'].name == "horsey":
                await utility.smart_reply(ctx, "Sorry, you didn't win anything. Better luck next time.")
            elif result['result'].name in ["brick", "fide_brick", "brick_fide", "brick_gold"]:
                try: # brick avoidance deterrant
                    response = "You found a brick. Please hold, delivering reward at high speed."
                    if result['result'].name == "brick_gold":
                        response += f" Looks like you'll be able to sell this one for {winnings} dough."
                    await utility.smart_reply(ctx, response)
                    await asyncio.sleep(2)
                except:
                    pass 
                await ctx.invoke(self.bot.get_command('brick'), member=ctx.author, duration=None)
            else:
                await utility.smart_reply(ctx, f"With a {winning_text}, you won {winnings} dough.")
        
            daily_gambles = user_account.get_value_strict("daily_gambles")
            if daily_gambles == max_gambles:
                await utility.smart_reply(ctx, "That was all the gambling you can do today.")

            elif daily_gambles >= max_gambles-3:
                #await ctx.reply("You can gamble one more time today.")
                text= "You can gamble "+Bread_cog.write_number_of_times(max_gambles-daily_gambles)+" more today."
                await utility.smart_reply(ctx, text)
        except:
            pass #only happens if original message was deleted.

        user_account.increment("gamble_winnings", winnings - amount)
        user_account.increment("total_dough", winnings)
        self.json_interface.set_account(ctx.author, user_account)

        self.currently_interacting.remove(ctx.author.id)




        # output = ""
        # for i in range(len(grid)):
        #     for k in range(len(grid[i])):
        #         if grid[i][k] is None:
        #             output += ":black_medium_square: "
        #         else:
        #             output += str(grid[i][k]) + " "
        #     output += "\n"
        # await ctx.send(output)


    def show_grid(grid):
        output = ""
        for i in range(len(grid)):
            for k in range(len(grid[i])):
                if grid[i][k] is None:
                    output += ":black_medium_square: "
                else:
                    output += str(grid[i][k]) + " "
            output += "\n"
        return output

    ########################################################################################################################
    #####      BREAD STONKS

    @bread.group(
        name="stonks", 
        aliases=["stonk", "stocks", "stock", "yeast"],
        usage="stonks [buy/sell] [amount] [symbol]",
        brief="See the stonk market.",
    )
    async def stonks(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
            #await ctx.send_help(ctx.command)

        output = "Welcome to the stonk market!\nCurrent values are as follows:\n\n"
        stonks_file = self.json_interface.get_custom_file("stonks")

        #set default values
        save = False
        if values.pretzel.text not in stonks_file.keys():
            stonks_file[values.pretzel.text] = 100
            save = True
        if values.cookie.text not in stonks_file.keys():
            stonks_file[values.cookie.text] = 25
            save = True
        if values.fortune_cookie.text not in stonks_file.keys():
            stonks_file[values.fortune_cookie.text] = 500
            save = True
        if save == True:
            self.json_interface.set_custom_file("stonks", stonks_file)

        for stonk in all_stonks:
            value = round(stonks_file[stonk])
            output += f"{stonk} - {value} dough\n"

        user_account = self.json_interface.get_account(ctx.author)
        output += f"\nYou have **{user_account.get('total_dough')} dough** to spend.\n"
        output += '\nUse "$bread invest <amount> <stonk>" to buy into a stonk.\nUse "$bread divest <amount> <stonk>" to get out while you\'re still behind.\nUse "$bread portfolio" to see your current stonk holdings.'
        await ctx.reply(output)


    previous_messages = list()

    async def stonks_announce(self):
        
        
        load_dotenv()
        IS_PRODUCTION = getenv('IS_PRODUCTION')
        print("IS_PRODUCTION is: "+IS_PRODUCTION)
        # if IS_PRODUCTION == "True":
        #     print("Stonk announce: This is a production server, continuing")
            
        # if IS_PRODUCTION == "False":
        #     print("Stonk announce: This is a development server, aborting")
        #     return
            
        # delete old messages
        for message in self.previous_messages:
            try:
                await message.delete()
            except:
                pass       
        self.previous_messages.clear()

        # define message
        output = "Current stonk values are as follows:\n\n"
        stonks_file = self.json_interface.get_custom_file("stonks")
        for stonk in all_stonks:
            stonk_history_key = stonk+"_history"
            stonk_history = stonks_file[stonk_history_key] # will be a list

            output += f"{stonk}: "

            for entry_number in range(len(stonk_history)): # for each element of a list
                historical_value = stonk_history[entry_number] # get the element
                output += f"{round(historical_value)} -> " 
                

            value = round(stonks_file[stonk])
            output += f"**{value}** dough\n"

        # post messages
        if IS_PRODUCTION == "True":
            channel_ids =  announcement_channel_ids
        if IS_PRODUCTION == "False":
            channel_ids =  test_announcement_channel_ids
        for channel_id in channel_ids:
            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                try:
                    message = await channel.send(output)
                    self.previous_messages.append(message)
                except:
                    pass

    ########################################################################################################################
    #####      BREAD INVEST OLD
    """
    @bread.command(
        brief="Buy into a stonk.",
        help="You can either use the stonk name or the stonk emoji.\nUse as \"$bread invest <amount> <stonk>\". You can also invest a certain amount of dough by using \"$bread invest <amount> dough <stonk>\".",
    )
    async def invest_old(self, ctx, *, args):
        if ctx.channel.name not in earnable_channels:
            await ctx.reply("Thank you for your interest in stonks. They are available for you in <#967544442468843560>.")
            return

        amount = None
        emote = None
        dough_value = False

        args = args.split(" ")
        
        # see if we have 'dough' in the args
        for arg in args:
            if arg.lower() == "dough":
                dough_value = True

        # first get the amount from the args
        for arg in args:
            if arg.isdigit():
                amount = int(arg)
                break
        if amount is None:
            for arg in args:
                if arg == "all":
                    amount = 1000000000
                    break
        if amount is None:
            for arg in args:
                if arg.startswith("-"):
                    await ctx.reply("You can't invest negative dough.")
                    return
        
        # then get the emote from the args
        for arg in args:
            test_emote = values.get_emote(arg)
            if test_emote is not None:
                print(f"found emote: {test_emote}")
                emote = test_emote
                break
        
        if emote is None or amount is None:
            await ctx.reply("Needs an amount and what to invest in.\nUse as \"$bread invest <amount> <stonk>\"")
            return

        if amount == 0:
            await ctx.reply("There's no point in investing 0 dough.")
            return
        
        # now we go through the stonks and see if we can find one that matches the emote
        stonks_file = self.json_interface.get_custom_file("stonks")
        user_account = self.json_interface.get_account(ctx.author)

        print (f"{ctx.author.name} is investing {amount} {emote} stonks for {amount} dough.")
        if emote.text not in stonks_file.keys():
            await ctx.reply("Sorry, I don't recognize that stonk.")
            return
        
        stonk_value = round(stonks_file[emote.text])

        #check if we're buying a certain amount of dough worth of a stonk, rather than a certain amount of stonks
        if dough_value is True:
            amount = math.floor(amount/stonk_value)

        # now we buy the stonks
        amount_purchased = 0
        for i in range(amount):
            if user_account.has("total_dough", stonk_value):
                user_account.increment("total_dough", -stonk_value)
                user_account.increment(emote.text, 1)
                user_account.increment("investment_profit", -stonk_value)
                amount_purchased += 1
            else: 
                break

        self.json_interface.set_account(ctx.author, user_account)
        
        await ctx.reply(f"You invested in {utility.smart_number(amount_purchased)} {emote.text} stonks for **{utility.smart_number(amount_purchased*stonk_value)} dough**.\n\nYou have **{utility.smart_number(user_account.get_dough())} dough** remaining.")
        print(f"{ctx.author.name} invested in {amount_purchased} {emote.name} stonks for {amount_purchased*stonk_value} dough.")
    """

    # BREAD INVEST NEW
    # credit to Aloe for her work on this
    @bread.command(
        brief="Buy into a stonk.",
        help="You can either use the stonk name or the stonk emoji.\nUse as \"$bread invest <amount> <stonk>\". You can also invest a certain amount of dough by using \"$bread invest <amount> dough <stonk>\".",
    )
    async def invest(self, ctx, *, args):
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Thank you for your interest in stonks. They are available for you in <#967544442468843560>.")
            return

        amount = None
        emote = None

        args = args.lower().split(' ')
        
        # check for negatives and valid inputs. priority: negative, digit, all.

        for arg in args:
            if arg.startswith('-'):
                await ctx.reply("You can't invest negative dough.")
                return
            if arg.isdigit():
                amount = int(arg)
            if 'all' in args:
                amount = 1000000000
        
        # get the emote from the args

        # i know readability is important, so let me overview this
        # it packs all values of args run through the values.get_emote function into a map object. this map object is iterated over to find all non-None values.
              
        arg_emotes = [x for x in map(values.get_emote,args) if x]
  
        # if there are non-None values, run this code
        # if length is 0, the if doesn't run
  
        if len(arg_emotes):
            print(f"found emote: {arg_emotes[0]}")
            emote = arg_emotes[0]
        
        if emote is None or amount is None:
            await ctx.reply("Needs an amount and what to invest in.\nUse as \"$bread invest <amount> <stonk>\"")
            return

        if amount == 0:
            await ctx.reply("There's no point in investing 0 dough.")
            return
        
        # now we go through the stonks and see if we can find one that matches the emote
        stonks_file = self.json_interface.get_custom_file("stonks")
        user_account = self.json_interface.get_account(ctx.author)

        print(f"{ctx.author.name} is investing {amount} {emote} stonks for {amount} dough.")
        if emote.text not in stonks_file.keys():
            await ctx.reply("Sorry, I don't recognize that stonk.")
            return
        
        stonk_value = round(stonks_file[emote.text])

        #check if we're buying a certain amount of dough worth of a stonk, rather than a certain amount of stonks
        if 'dough' in args:
            # x //= n is the same as x = x // n, where // is floor division.
            amount //= stonk_value

        # now we buy the stonks

        buy_amount = min(amount,user_account.get('total_dough') // stonk_value)
        user_account.increment('total_dough',(-buy_amount * stonk_value))
        user_account.increment(emote.text, buy_amount)
        user_account.increment('investment_profit', (-buy_amount * stonk_value))

        self.json_interface.set_account(ctx.author, user_account)
        
        await ctx.reply(f"You invested in {utility.smart_number(buy_amount)} {emote.text} stonks for **{utility.smart_number(buy_amount*stonk_value)} dough**.\n\nYou have **{utility.smart_number(user_account.get_dough())} dough** remaining.")
        print(f"{ctx.author.name} invested in {buy_amount} {emote.name} stonks for {buy_amount*stonk_value} dough.")

    ########################################################################################################################
    #####      BREAD DIVEST OLD
    """
    # DIVEST OLD
    @bread.command(
        usage="divest <amount> <stonk>",
        brief="Get out of a stonk.",
        help="You can either use the stonk name or the stonk emoji.\nUse as \"$bread divest <amount> <stonk>\". You can also divest a certain amount of dough by using \"$bread divest <amount> dough <stonk>\".",
    )
    async def divest_old(self, ctx, *, args):
        if ctx.channel.name not in earnable_channels:
            await ctx.reply("Thank you for your interest in buying high and selling low. You can do so in <#967544442468843560>.")
            return

        stonks_file = self.json_interface.get_custom_file("stonks")
        user_account = self.json_interface.get_account(ctx.author)

        amount = None
        emote = None
        dough_value = False

        args = args.split(" ")

        #bread divest all: divests all stonks simultaneously
        if len(args) == 1:
            if args[0] == "all":
                amount_divested = 0
    
                for stonk in all_stonks:
                    while user_account.has(stonk, 1):
                        stonk_cost = round(stonks_file[stonk])
                        user_account.increment(stonk, -1)
                        user_account.increment("total_dough", stonk_cost)
                        user_account.increment("investment_profit", stonk_cost)
                        amount_divested += stonk_cost
                self.json_interface.set_account(ctx.author, user_account)
                await ctx.reply(f"You divested all of your stonks for **{utility.smart_number(amount_divested)} dough**.\n\nYou now have **{utility.smart_number(user_account.get_dough())} dough**.")
                return

        
        # see if we have 'dough' in the args
        for arg in args:
            if arg.lower() == "dough":
                dough_value = True

        # first get the amount from the args
        for arg in args:
            if arg.isdigit():
                amount = int(arg)
                break
        if amount is None:
            for arg in args:
                if arg == "all":
                    amount = 1000000000
                    break
        if amount is None:
            for arg in args:
                if arg.startswith("-"):
                    await ctx.reply("You can't divest negative dough.")
                    return
        
        # then get the emote from the args
        for arg in args:
            test_emote = values.get_emote(arg)
            if test_emote is not None:
                print(f"found emote: {test_emote}")
                emote = test_emote
                break
        
        if emote is None or amount is None:
            await ctx.reply("Needs an amount and what to divest in.\nUse as \"$bread divest <amount> <stonk>\"")
            return

        if amount == 0:
            await ctx.reply("It would be silly to divest 0 stonks.")
            return

        

        # make sure the stonk is in the stonks file
        if emote.text not in stonks_file.keys():
            await ctx.reply("Sorry, I don't recognize that stonk.")
            return

        stonk_value = round(stonks_file[emote.text])
        #check if we're selling a certain amount of dough worth of a stonk, rather than a certain amount of stonks
        if dough_value is True:
            amount = math.ceil(amount/stonk_value)

        # now we sell the stonks
        amount_sold = 0
        for i in range(amount):
            if user_account.has(emote.text):
                user_account.increment("total_dough", stonk_value)
                user_account.increment(emote.text, -1)
                user_account.increment("investment_profit", stonk_value)
                amount_sold += 1
            else: 
                break
            
        self.json_interface.set_account(ctx.author, user_account)

        await ctx.reply(f"You sold {utility.smart_number(amount_sold)} {emote.text} stonks for **{utility.smart_number(amount_sold*stonk_value)} dough**. You now have **{utility.smart_number(user_account.get_dough())} dough** and {utility.smart_number(user_account.get(emote.text))} {emote.text}.")
        print (f"{ctx.author.name} divested in {amount_sold} {emote.text} stonks for {amount_sold*stonk_value} dough.")
    """

    ########################################################################################################################
    #####      BREAD DIVEST

    # DIVEST NEW
    # credit to Aloe for her work on this
    @bread.command(
        usage="divest <amount> <stonk>",
        brief="Get out of a stonk.",
        help="You can either use the stonk name or the stonk emoji.\nUse as \"$bread divest <amount> <stonk>\". You can also divest a certain amount of dough by using \"$bread divest <amount> dough <stonk>\".",
    )
    async def divest(self, ctx, *, args):
        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Thank you for your interest in buying high and selling low. You can do so in <#967544442468843560>.")
            return

        stonks_file = self.json_interface.get_custom_file("stonks")
        user_account = self.json_interface.get_account(ctx.author)

        amount = None
        emote = None
        dough_value = False

        args = args.lower().split(' ')

        # divest all: divests all stonks simultaneously
        if len(args) == 1:
            if args[0] == "all":
                
                amount_divested = 0
                for stonk in all_stonks:
                    stonk_cost = round(stonks_file[stonk])

                    profit = stonk_cost*user_account.get(stonk)
                    amount_divested += profit
                    user_account.increment('total_dough', profit)
                    user_account.increment("investment_profit", profit)
                    user_account.set(stonk, 0) # sell all the stonk by definition

                    self.json_interface.set_account(ctx.author, user_account)
                await ctx.reply(f"You divested all of your stonks for **{utility.smart_number(amount_divested)} dough**.\n\nYou now have **{utility.smart_number(user_account.get_dough())} dough**.")
                return
        
        # check for negatives and valid inputs. priority: negative, digit, all.

        for arg in args:
            if arg.startswith('-'):
                await ctx.reply("You can't divest negative dough.")
                return
            if arg.isdigit():
                amount = int(arg)
            if arg == 'all':
                amount = 1000000000
            if arg == 'dough':
                print("dough arg found in divest")
                dough_value = True
        
        # then get the emote from the args
        for arg in args:
            test_emote = values.get_emote(arg)
            if test_emote is not None:
                # print(f"found emote: {test_emote}")
                emote = test_emote
                break
        
        if emote is None or amount is None:
            await ctx.reply("Needs an amount and what to divest from.\nUse as \"$bread divest <amount> <stonk>\"")
            return

        if amount == 0:
            await ctx.reply("It would be silly to divest 0 stonks.")
            return

        

        # make sure the stonk is in the stonks file
        if emote.text not in all_stonks:
            await ctx.reply("Sorry, I don't recognize that stonk.")
            return

        stonk_value = round(stonks_file[emote.text])
        #check if we're selling a certain amount of dough worth of a stonk, rather than a certain amount of stonks
        if dough_value is True:
            amount = math.ceil(amount/stonk_value)

        # now we adjust the amount to make sure we don't sell more than we have
        if amount > user_account.get(emote.text):
            amount = user_account.get(emote.text)

        # sell the stonks
        user_account.increment('total_dough', stonk_value*amount)
        user_account.increment(emote.text, -amount)
        user_account.increment('investment_profit', stonk_value*amount)
            
        self.json_interface.set_account(ctx.author, user_account)

        await ctx.reply(f"You sold {utility.smart_number(amount)} {emote.text} stonks for **{utility.smart_number(amount*stonk_value)} dough**. You now have **{utility.smart_number(user_account.get_dough())} dough** and {utility.smart_number(user_account.get(emote.text))} {emote.text}.")
        print (f"{ctx.author.name} divested in {amount} {emote.text} stonks for {amount*stonk_value} dough.")

    ########################################################################################################################
    #####      BREAD PORTFOLIO

    @bread.command(
        name="portfolio", 
        aliases = ["investments"],
        brief="See your investments.",
    )
    async def portfolio(self, ctx, user: typing.Optional[discord.Member] = None):
        print(f"{ctx.author.name} requested their portfolio.")

        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_BASIC:
            await ctx.reply("Thank you for your interest in your stonks portfolio. We have it available for you in <#967544442468843560>.")
            return
        
        if user is None:
            user = ctx.author

        user_account = self.json_interface.get_account(user)

        # investments = user_account.get_all_items_with_attribute("stonks")
        stonks_file = self.json_interface.get_custom_file("stonks")

        output = f"Investment portfolio for {user_account.get_display_name()}:\n\n"
        total_value = 0
        history_value = 0
        num_stonks_held = 0

        for stonk in all_stonks:
            if user_account.has(stonk):
                num_stonks_held += 1
                stonk_text = stonk #stonk.text
                stonk_count = user_account.get(stonk_text)
                stonk_value = round(stonks_file[stonk_text])
                #print(f"stonk: {stonk}")
                value = stonk_count * stonk_value
                total_value += value
                output += f"{stonk_text} -- {utility.write_count(stonk_count, 'stonk')}, worth **{utility.smart_number(value)} dough**\n"

                history_name = f"{stonk_text}_history"
                if history_name in stonks_file.keys() and len(stonks_file[history_name]) >= 3:
                    history_value += stonk_count * round(stonks_file[history_name][2])

        if num_stonks_held == 0:
            output += "Your portfolio seems to be empty.\n\n"
        else:
            output += f"\nYour portfolio is worth **{utility.smart_number(total_value)} dough**. In the last tick, your portfolio value changed by **{utility.smart_number(total_value-history_value)} dough**. "
        
        investment_profit = user_account.get("investment_profit")
        output +=  f"So far, you've made **{utility.smart_number(investment_profit+total_value)} dough** from investing."

        await ctx.reply(output)
        
        
    ########################################################################################################################
    #####      Stonk internal stuff

    
    def stonk_fluctuate_internal(self):
        # it's in a try block so that it won't crash if running on a server without the stonks file
        try:
            stonks.stonk_fluctuate(self) # this will forever remain a secret
        except:
            print("stonk fluctuate failed")
        
        # auto split code here?

        # dividend code here?

        
    

    def stonk_reset_internal(self):
        stonks_file = self.json_interface.get_custom_file("stonks")

        #set default values
        stonks_file[values.pretzel.text] = 100
        stonks_file[values.cookie.text] = 25
        stonks_file[values.fortune_cookie.text] = 500

        self.json_interface.set_custom_file("stonks", stonks_file)

    def stonk_split_internal(self, stonk_text: str):
        stonks_file = self.json_interface.get_custom_file("stonks")
        stonk_value = stonks_file[stonk_text]
        stonks_file[stonk_text] = stonk_value/2

        history_file = stonks_file.get(stonk_text+"_history", [])

        for i in range(len(history_file)):
            history_file[i] = history_file[i]/2

        stonks_file[stonk_text+"_history"] = history_file
            

        self.json_interface.set_custom_file("stonks", stonks_file)

        #now we go through everyone's investments and split them
        user_files = self.json_interface.data["bread"]

        #wipe the accounts cache since we'll be direcly manipulating data. 
        # Would be better to avoid this in the future.
        self.json_interface.accounts.clear()

        for file_key in user_files.keys():
            if not file_key.isdigit(): # skip all non-user files
                continue
            file = user_files[file_key]
            #print(f"Individual file is: \n{file}")
            if stonk_text in file.keys():
                file[stonk_text] = file[stonk_text] * 2

        print(f"{stonk_text} has been split into two stonks")


    def get_portfolio_value(self, user_id: int):
        stonks_file = self.json_interface.get_custom_file("stonks")
        user_file = self.json_interface.get_account(user_id)
        investments = user_file.get_all_items_with_attribute("stonks")
        total_value = 0
        for stonk in investments:
            stonk_text = stonk.text
            stonk_count = user_file.get(stonk_text)
            stonk_value = round(stonks_file[stonk_text])
            value = stonk_count * stonk_value
            total_value += value
        return total_value


    def get_portfolio_combined_value(self, user_id: int):
        user_file = self.json_interface.get_account(user_id)
        portfolio_value = self.get_portfolio_value(user_id)
        return portfolio_value + user_file.get("investment_profit")

    

    ########################################################################################################################
    #####      BREAD ALCHEMY

    @bread.command(
        name="alchemy", 
        aliases = ["alchemize", "distill"],
        brief="Create a new item from base materials.",
        usage="<amount> <target item> <recipe number>",
        help="Creates more advanced materials from basic ones. Call the command and follow the instructions, keeping in mind what you would like to create."
    )
    #@commands.is_owner()
    async def alchemy(self, ctx, count: typing.Optional[int] = None, target_item: typing.Optional[str] = None, recipe_num: typing.Optional[int] = None, confirm: typing.Optional[str] = None):
        
        if count is None:
            count = 1
        if count == 0:
            await ctx.reply("Alright, I have made zero of those for you...")
            return
        if count < 0:
            await ctx.reply("The laws of alchemy prevent me from utilizing negative energy.")
            return
        if count > 1000000000000000:
            await ctx.reply("That is an unreasonable number of items to alchemize. Please try again with a smaller number.")
            return

        # print(f"{ctx.author.name} requested to alchemize {count} {target_item}.")

        if channel_permission_levels.get(ctx.channel.name, 0) < PERMISSION_LEVEL_ACTIVITIES:
            await ctx.reply("Thank you for your interest in bread alchemy. Please find the alchemical circle is present in <#967544442468843560>.")
            return

        #check if they're already alchemizing
        if ctx.author.id in self.currently_interacting:
            return
        #otherwise we add them to the list
        self.currently_interacting.append(ctx.author.id)


        user_account = self.json_interface.get_account(ctx.author)

        # transform it into a comprehensible string
        # target_item = values.get_emote(target_item)
        
        # create a reaction collector to listen for reactions
        def check(m: discord.Message):  # m = discord.Message.
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 


        try: # this is to catch any errors on discord's end

            ########################################################################################################################
            #####      GET ITEM

            if (target_item is None):
                await ctx.reply("Welcome to the alchemy circle. Please say the item you would like to create.")
                try:
                    msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
                except asyncio.TimeoutError: 
                    # at this point, the check didn't become True, let's handle it.
                    await ctx.reply(f"My patience is limited. Come back when you know what you want.")
                    self.currently_interacting.remove(ctx.author.id)
                    return
                target_item = msg.content #values.get_emote(msg.content)

            ########################################################################################################################
            #####      GET EMOTE

            # now we turn the target item into a useful emote
            target_emote = values.get_emote(target_item)

            if (target_emote is None):
                await ctx.reply(f"I do not recognize that item. Please start over.")
                self.currently_interacting.remove(ctx.author.id)
                return

            print(f"{ctx.author.name} requested to alchemize {count} {target_emote.name}.")
            # print(f"Available recipes are: {alchemy.recipes}")

            if target_emote.name in alchemy.recipes.keys():
                recipe_list = alchemy.recipes[target_emote.name]
            else:
                await ctx.reply(f"There are no recipes to create {target_emote.text}. Perhaps research has not progressed far enough.")
                self.currently_interacting.remove(ctx.author.id)
                return

            ########################################################################################################################
            #####      GET NUMBER

            if recipe_num is None:

                ingredients = list()

                recipes_description = f"There are {len(recipe_list)} recipes for {target_emote.text}.\n"
                for i in range(len(recipe_list)):
                    recipe = recipe_list[i]
                    recipes_description += f"**[ {i+1} ]**    {alchemy.describe_individual_recipe(recipe)}\n"

                    # print (f"recipe is {recipe}")
                    
                    for pair in recipe:
                        if pair[0] not in ingredients:
                            ingredients.append(pair[0])

                recipes_description += "\nOf the above ingredients, you have:\n"

                # show how much of each ingredient is posessed
                for ingredient in ingredients:
                    recipes_description += f"{ingredient.text}: {user_account.get(ingredient.text)}\n"
            
                recipes_description += "\nPlease reply with either the number of the recipe you would like to use, or \"cancel\"."
                await ctx.reply(recipes_description)
                
                try:
                    msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
                except asyncio.TimeoutError: 
                    # at this point, the check didn't become True, let's handle it.
                    await ctx.reply(f"My patience is limited. This offering is rejected.")
                    self.currently_interacting.remove(ctx.author.id)
                    return

                if "cancel" in msg.content.lower():
                    await ctx.reply("You have cancelled this transaction.")
                    self.currently_interacting.remove(ctx.author.id)
                    return

                try:
                    recipe_num = int(msg.content)
                except ValueError:
                    await ctx.reply(f"I do not recognize that as a number. Please try again from the beginning.")
                    self.currently_interacting.remove(ctx.author.id)
                    return
            
            if recipe_num > len(recipe_list) or recipe_num < 1:
                await ctx.reply(f"That is not a valid recipe number. Please start over.")
                self.currently_interacting.remove(ctx.author.id)
                return

            recipe = recipe_list[recipe_num-1]

            ########################################################################################################################
            #####      GET CONFIRMATION

            already_confirmed = False
            if confirm is not None:
                if confirm.lower() in ["yes", "y", "confirm"]:
                    already_confirmed = True

            if already_confirmed is False:
                question_text = f"You have chosen to create {count} {target_emote.text} from the following recipe:\n{alchemy.describe_individual_recipe(recipe)}\n\n"
                question_text += f"You have the following ingredients:\n"
                for pair in recipe:
                    question_text += f"{pair[0].text}: {user_account.get(pair[0].text)} of {pair[1] * count}\n"
                        
                question_text += "\nWould you like to proceed? Yes or No."
                await ctx.reply(question_text)

                try:
                    msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.reply(f"My patience is limited. This offering is rejected.")
                    self.currently_interacting.remove(ctx.author.id)
                    return
                
                if "yes" in msg.content.lower():
                    pass
                elif "no" in msg.content.lower():
                    await ctx.reply("You have rejected this recipe.")
                    self.currently_interacting.remove(ctx.author.id)
                    return
                else:
                    await ctx.reply("I do not recognize your response. You may come back when you are feeling more decisive.")
                    self.currently_interacting.remove(ctx.author.id)
                    return

            ########################################################################################################################
            #####      CREATE ITEM


            # first we make sure the user has enough ingredients
            for pair in recipe:
                cost = pair[1] * count
                posessions = user_account.get(pair[0].text)
                # print(f"{ctx.author.display_name} is attempting to alchemize {count} {target_emote.name}")
                # print(f"cost is {cost} and posessions is {posessions}")
                if posessions < cost:
                    await ctx.reply(f"You do not have enough {pair[0].text} to create {count} {target_emote.text}. This offering is rejected.")
                    self.currently_interacting.remove(ctx.author.id)
                    return
            
            value = 0

            for i in range(count):
                # we remove the ingredients
                for pair in recipe:
                    user_account.increment(pair[0].text, -pair[1])

                # then we add the item
                
                user_account.add_item_attributes(target_emote)
                if target_emote.gives_alchemy_award():
                    value += user_account.add_dough_intelligent(target_emote.get_alchemy_value() + user_account.get_dough_boost_for_item(target_emote))


            # finally, we save the account
            self.json_interface.set_account(ctx.author, user_account)

            output = f"Well done. You have created {count} {target_emote.text}. You now have {user_account.get(target_emote.text)} of them."
            if target_emote.gives_alchemy_award():
                output += f"\nYou have also been awarded **{value} dough** for your efforts."

            await ctx.reply(output)

            await self.do_chessboard_completion(ctx)

        except:
            pass

        self.currently_interacting.remove(ctx.author.id)
        
    ########################################################################################################################
    #####      BREAD DOUGH

    # get the user's amount of dough and display it
    @bread.command(
        aliases = ["liquid_dough"],
        brief = "Shows how much dough you have.",
    )
    async def dough(self, ctx):
        user_account = self.json_interface.get_account(ctx.author)
        await ctx.reply(f"You have **{utility.smart_number(user_account.get_dough())} dough**.")

    #############################################################################################################################
    ##########      ADMIN   #################
    #########################################


    @bread.group(
        brief="[Restricted]",
    )
    async def admin(self, ctx):
        if not verification.from_owner(ctx.author):
            await ctx.reply(verification.get_rejection_reason())
        if ctx.invoked_subcommand is None:
            print("admin called on nothing")
            return

    async def await_confirmation(self, ctx, force = False, message = "Are you sure you would like to proceed?"):
        load_dotenv()
        IS_PRODUCTION = getenv('IS_PRODUCTION')
        if force or IS_PRODUCTION == 'True':
            def check(m: discord.Message):  # m = discord.Message.
                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id 
            await ctx.reply(message+" y/n.")
            try:
                msg = await self.bot.wait_for('message', check = check, timeout = 60.0)
            except asyncio.TimeoutError: 
                # at this point, the check didn't become True, let's handle it.
                await ctx.reply(f"Timed out.")
                return False
            response = msg.content
            if "y" in response.lower():
                await ctx.reply("Proceeding.")
                return True
            elif "n" in response.lower():
                await ctx.reply("Cancelled.")
                return False
            else:
                await ctx.reply("Unknown response, cancelled.")
                return False
        else:
            return True

    ########################################################################################################################
    #####      ADMIN SET

    @admin.group(
        brief="sets a value manually",
        help = "Usage: bread admin set [optional Member] key value [optional 'force']"
    )
    @commands.is_owner()
    async def set(self, ctx, 
                    user: typing.Optional[discord.Member], 
                    key: str,
                    value: int,
                    do_force: typing.Optional[str]):
        if await self.await_confirmation(ctx) is False:
            return
        output = ""
        print("Bread Admin Set: User is "+str(user)+", key is '"+str(key)+"', value is "+str(value))
        if user is None:
            output += "Applying to self\n"
            user = ctx.author
        
        # file = self.json_interface.get_file_for_user(user)
        account = self.json_interface.get_account(user)
        file = account.values

        
        #use values module to grab emote name
        provisional_emote = values.get_emote_text(key)
        if provisional_emote is not None:
            key_name = provisional_emote
        else:
            #use it straight
            key_name = key
        
        if key_name not in file.keys():
            await ctx.send("Key does not exist.")
            if (do_force is not None and do_force.lower() == "force") or (await self.await_confirmation(ctx, True) is True):
                file[key_name] = 0
            else:
                output += "Aborting.\n"
                await ctx.send(output)
                return

        file[key_name] = value
        # self.json_interface.update_file_for_user(user, file)
        account.values = file
        self.json_interface.set_account(user, account)
        
        await ctx.send(output+"Done.")

    ########################################################################################################################
    #####      ADMIN INCREMEMNT

    @admin.group(
        brief="sets a value manually",
        help = "Usage: bread admin set [optional Member] key value [optional 'force']"
    )
    @commands.is_owner()
    async def increment(self, ctx, 
                    user: discord.Member, 
                    key: str,
                    value: int,
                    do_force: typing.Optional[str]):
        if await self.await_confirmation(ctx) is False:
            return
        output = ""
        print("Bread Admin Increment: User is "+str(user)+", key is '"+str(key)+"', value is "+str(value))
        if user is None:
            output += "Applying to self\n"
            user = ctx.author
        
        # file = self.json_interface.get_file_for_user(user)
        account = self.json_interface.get_account(user)
        file = account.values

        
        #use values module to grab emote name
        provisional_emote = values.get_emote_text(key)
        if provisional_emote is not None:
            key_name = provisional_emote
        else:
            #use it straight
            key_name = key
        
        if key_name not in file.keys():
            await ctx.send("Key does not exist.")
            if (do_force is not None and do_force.lower() == "force") or (await self.await_confirmation(ctx, True) is True):
                file[key_name] = 0
            else:
                output += "Aborting.\n"
                await ctx.send(output)
                return
                

        file[key_name] = value + file[key_name]

        account.values = file
        self.json_interface.set_account(user, account)
        # self.json_interface.update_file_for_user(user, file)

        await ctx.send(output+"Done.")

    ########################################################################################################################
    #####      ADMIN RESET_ACCOUNT

    @admin.group()
    @commands.is_owner()
    async def reset_account(self, ctx, user: discord.Member):
        if await self.await_confirmation(ctx) is False:
            return
        user_account = self.json_interface.get_account(user)
        # username = user_account.get("username")
        # display_name = user_account.get("display_name")
        user_account.reset_to_default()
        # user_account.set("username", username)
        # user_account.set("display_name", display_name)
        self.json_interface.set_account(user, user_account)
        print (f"Reset account for {user.display_name}")
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN COPY_ACCOUNT

    @admin.group()
    @commands.is_owner()
    async def copy_account(self, ctx, origin_user: discord.Member, target_user: discord.Member):
        if await self.await_confirmation(ctx) is False:
            return
    
        origin_account = self.json_interface.get_account(origin_user)
        
        # hacky copy operation
        target_account = account.Bread_Account.from_dict(str(target_user.id), origin_account.to_dict())
        # self.json_interface.set_account(target_user, target_account)
        
        # target_account = self.json_interface.get_account(target_user)
        target_account.values["id"] = target_user.id
        target_account.values["username"] = target_user.name
        target_account.values["display_name"] = target_user.display_name

        self.json_interface.set_account(target_user, target_account)

        print (f"Copied account from {origin_user.name} to {target_user.name}")
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN SERVER_BOOST

    @admin.group()
    @commands.is_owner()
    async def reward_all_server_boosters(self, ctx):
        # we will find the dough from a daily roll, and award some multiple of that amount
        # first get all boosters
        boosters = ctx.guild.premium_subscribers
        for booster in boosters:
            await self.reward_single_server_booster(ctx, booster, 1)
            await asyncio.sleep(1)

        await ctx.send("Done.")


    @admin.group()
    @commands.is_owner()
    async def reward_single_server_booster(self, ctx, user: discord.Member, multiplier: typing.Optional[float] = 1):
        #first get user account
        user_account = self.json_interface.get_account(user)

        result = rolls.bread_roll(roll_luck= user_account.get("loaf_converter")+1, 
                                    roll_count= user_account.get("max_daily_rolls"),
                                    user_account=user_account)

        value = result.get("value")

        portfolio_value = user_account.get_portfolio_value()

        value = round(value + portfolio_value * 0.04) # 4% of portfolio value

        value = round(value * multiplier) # 2 days worth of rolls

        added_value = user_account.add_dough_intelligent(value)
        self.json_interface.set_account(user, user_account)
        await ctx.send(f"Thank you {user.mention} for boosting the server! {added_value} dough has been deposited into your account.")
        

    

    @admin.group()
    @commands.is_owner()
    async def server_boost(self, ctx, user: discord.Member):
        # this will increase their dough by 5x their max daily rolls
            await self.reward_single_server_booster(ctx, user, 1)
    
    @admin.group()
    @commands.is_owner()
    async def server_boost_additional(self, ctx, user: discord.Member):
        
        await self.reward_single_server_booster(ctx, user, .5)


    ########################################################################################################################
    #####      ADMIN SHOW

    @admin.group(
        brief="shows raw values",
        help = "Usage: bread admin show [optional member]"
    )
    @commands.is_owner()
    async def show(self, ctx, user: typing.Optional[discord.Member]):
        output = ""
        if user is None:
            output += "Applying to self.\n"
            user = ctx.author

        file = self.json_interface.get_file_for_user(user)
        for key in file.keys():
            if key == "display_name":
                if file[key] in ["@everyone", "@here"]:
                    output += "display_name -- (not shown)\n"
                    continue

            output += key + " -- " + str(file[key]) + "\n"
            if len(output) > 1900:
                await ctx.send(output)
                output = ""

        print("Outputting file for "+user.display_name)
        print(str(file))
        await ctx.send(output)

    ########################################################################################################################
    #####      ADMIN SHOW_CUSTOM

    @admin.group(
    )
    @commands.is_owner()
    async def show_custom(self, ctx, filename: str):
        output = ""
        file = self.json_interface.get_custom_file(filename)
        for key in file.keys():
            output += str(key) + " -- " + str(file[key]) + "\n"

        print("Outputting file for "+filename)
        print(str(file))
        await ctx.send(output)

    ########################################################################################################################
    #####      ADMIN SET_MAX_PRESTIGE

    @admin.group(
        brief="sets the max prestige level",
        help = "Usage: bread admin set_max_prestige_level [value]"
    )
    @commands.is_owner()
    async def set_max_prestige_level(self, ctx, value: int):
        prestige_file = self.json_interface.get_custom_file("prestige")
        prestige_file["max_prestige_level"] = value
        self.json_interface.set_custom_file("prestige", prestige_file)
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN ALLOW / DISALLOW

    @admin.group(
        brief="Allows usage of the bread machine",
        help = "Usage: bread admin allow [member]"
    )
    @commands.is_owner()
    async def allow(self, ctx, user: typing.Optional[discord.Member]):
        if user is None:
            print("Bread Allow failed to recognize user "+str(user))
            ctx.reply("User reference not resolvable, please retry.")
            return
        
        self.json_interface.set_value_in_file(user, "allowed", True)
        await ctx.send("Done.")
        

    @admin.group(
        brief="Disllows usage of the bread machine",
        help = "Usage: bread admin disallow [member]"
    )
    @commands.is_owner()
    async def disallow(self, ctx, user: typing.Optional[discord.Member]):
        if user is None:
            print("Bread Disallow failed to recognize user "+str(user))
            ctx.reply("User reference not resolvable, please retry.")
            return
        
        self.json_interface.set_value_in_file(user, "allowed", False)
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN BACKUP


    @admin.group()
    @commands.is_owner()
    async def backup(self, ctx):
        print("backing up")
        self.json_interface.create_backup()
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN DAILY_RESET

    @admin.group()
    @commands.is_owner()
    async def daily_reset(self, ctx):
        if await self.await_confirmation(ctx) is False:
            return
        self.reset_internal()
        await ctx.send("Done.")

    def reset_internal(self):
        files = self.json_interface.data["bread"]
        print("Internal daily reset called")

        self.currently_interacting.clear()

        for account in self.json_interface.get_all_user_accounts():
            account.daily_reset()
            self.json_interface.set_account(account.get("id"), account)
        """
        #wipe the accounts cache since we'll be direcly manipulating data. 
        # Would be better to avoid this in the future.
        self.json_interface.accounts.clear()

        #print(f"Daily reset: database is: \n{files}")
        for key in files.keys():
        #for file in files:
            file = files[key]
            #print(f"Individual file is: \n{file}")
            if "daily_rolls" in file.keys():
                file["daily_rolls"] = 0
            if "daily_gambles" in file.keys():
                file["daily_gambles"] = 0
        """

    ########################################################################################################################
    #####      ADMIN PURGE_ACCOUNT_CACHE

    @admin.group()
    @commands.is_owner()
    async def purge_account_cache(self, ctx):
        self.json_interface.accounts.clear()
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN RENAME

    # this will take one value from each account and rename it to something different.

    @admin.group()
    @commands.is_owner()
    async def rename(self, ctx, starting_name: str, ending_name: str):

        # first get the bread database
        JSON_cog = self.bot.get_cog("JSON")
        cabinet = JSON_cog.get_filing_cabinet("bread")

        # we get the guild and then all the members in it
        guild = ctx.guild
        all_members = guild.members

        # we iterate through all the members and rename the key
        for member in all_members:
            # make sure they have an account
            if self.json_interface.has_account(member):
                # get the account
                account = self.json_interface.get_account(member)

                # rename the key
                if starting_name in account.values.keys():
                    account.values[ending_name] = account.values[starting_name]
                    del account.values[starting_name]

                # save the account
                self.json_interface.set_account(member, account)

        # save the database      
        self.json_interface.internal_save()


        await ctx.send("Done.")


    ########################################################################################################################
    #####      ADMIN GOD_ACCOUNT

    @admin.group()
    @commands.is_owner()
    async def god_account(self, ctx, user: typing.Optional[discord.Member]):

        if await self.await_confirmation(ctx) is False:
            return

        if user is None:
            user = ctx.author
        
        account = self.json_interface.get_account(user)

        account.reset_to_default()

        account.set("total_dough", 1000000)
        account.set("loaf_converter", 128)
        account.set("max_daily_rolls", 1000)

        account.set("multiroller", 7)
        account.set("compound_roller", 5)
        account.set("roll_summarizer", 1)

        account.set("prestige_level", 0)
        account.set(values.ascension_token.text, 50)
        account.set(values.chessatron.text, 250)

        for word in [values.gem_red.text, values.gem_blue.text, values.gem_purple.text, values.gem_green.text, values.gem_gold.text]:
            account.set(word, 50)

        account.set(values.anarchy_chess.text, 5)

        for word in [":doughnut:", ":bagel:", ":waffle:", ":croissant:", ":flatbread:", ":stuffed_flatbread:", ":sandwich:", ":french_bread:"]:
            account.set(word, 5000)

        self.json_interface.set_account(user, account)
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN SYNCHRONIZE_USERNAMES

    @admin.command()
    @commands.is_owner()
    async def synchronize_usernames(self, ctx):
        # self.synchronize_usernames_internal()

        guild = self.bot.get_guild(default_guild)
        all_members = guild.members

        print(f"member count is {len(all_members)}, theoretical amount is {guild.member_count}")

        if len(all_members) != guild.member_count:
            async for member in guild.fetch_members(limit=150):
                print(member.name)

        # we iterate through all the members and rename the key
        # for member in all_members:
        async for member in guild.fetch_members(limit=3000):
            # make sure they have an account
            # print (f"Checking {member.display_name}")
            if self.json_interface.has_account(member):
                print(f"{member.display_name} has account")
                # get the account
                account = self.json_interface.get_account(member)

                account.values["id"] = member.id
                account.values["username"] = member.name
                account.values["display_name"] = member.display_name
                
                # save the account
                self.json_interface.set_account(member, account)

        # save the database      
        self.json_interface.internal_save()
        
        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN DO_OPERATION
    
    @admin.command()
    @commands.is_owner()
    async def do_operation(self, ctx):

        if await self.await_confirmation(ctx) is False:
            return
        
        # go through all accounts and do the operation
        for index in self.json_interface.data["bread"].keys():
            if not index.isdigit():
                continue
            user_account = self.json_interface.get_account(index)
            
            if user_account.get("LC_booster") == 1:
                user_account.increment(values.gem_gold.text, 1)

            self.json_interface.set_account(index, user_account)

            # #now we check each dough boost and increase it
            # for special_bread in values.all_special_breads:
            #     if user_account.get_dough_boost_for_item(special_bread) == 1:
            #         user_account.set_dough_boost_for_item(special_bread, 2)

            # for rare_bread in values.all_rare_breads:
            #     if user_account.get_dough_boost_for_item(rare_bread) == 2:
            #         user_account.set_dough_boost_for_item(rare_bread, 4)

            # for chess_piece_black in values.chess_pieces_black_biased:
            #     if user_account.get_dough_boost_for_item(chess_piece_black) == 10:
            #         user_account.set_dough_boost_for_item(chess_piece_black, 20) 
            
            # for chess_piece_white in values.chess_pieces_white_biased:
            #     if user_account.get_dough_boost_for_item(chess_piece_white) == 20:
            #         user_account.set_dough_boost_for_item(chess_piece_white, 40)

        # user_account = self.json_interface.get_account(ctx.author)
        # portfolio_value = user_account.get_portfolio_value()
        # await ctx.reply(f"Your portfolio value is {portfolio_value}")

        # load_dotenv()
        # IS_PRODUCTION = getenv('IS_PRODUCTION')
        # print("IS_PRODUCTION is: "+IS_PRODUCTION)
        # if IS_PRODUCTION == "True":
        #     print("This is a production server")
            
        # if IS_PRODUCTION == "False":
        #     print("This is a development server")
            
        # for index in self.json_interface.data["bread"].keys():
        #     if not index.isdigit():
        #         continue # skip the custom accounts
        #     user_account = self.json_interface.get_account(index)
        #     if user_account.has("one_of_a_kind"):
        #         amount = user_account.get(values.anarchy_chess.text)
        #         user_account.set("one_of_a_kind", 0)
        #     if user_account.has(values.anarchy.text):
        #         amount = user_account.get(values.anarchy.text)
        #         user_account.increment("one_of_a_kind", amount)
        #     if user_account.has(values.horsey.text):
        #         amount = user_account.get(values.horsey.text)
        #         user_account.increment("one_of_a_kind", amount)
        #     if user_account.has(values.holy_hell.text):
        #         amount = user_account.get(values.holy_hell.text)
        #         user_account.increment("one_of_a_kind", amount)

        #     self.json_interface.set_account(index, user_account)

        


        # # what we're going to do is reset highest_roll to a sensible value
        # JSON_cog = self.bot.get_cog("JSON")
        # cabinet = JSON_cog.get_filing_cabinet("bread")

        # # we get the guild and then all the members in it
        # guild = ctx.guild
        # all_members = guild.members

        # # we then iterate through all the members and reset their highest_roll to a sensible amount
        # for member in all_members:
        #     if self.json_interface.has_account(member):
        #         account = self.json_interface.get_account(member)
        #         if account.has("highest_roll"):
        #             # first set it to zero
        #             account.set("highest_roll", 0)

        #             #then, in sequence, we set it to the highest value of all the special ones they've found
        #             if account.has("ten_breads"):
        #                 account.set("highest_roll", 10)
        #             if account.has("eleven_breads"):
        #                 account.set("highest_roll", 11)
        #             if account.has("twelve_breads"):
        #                 account.set("highest_roll", 12)
        #             if account.has("thirteen_breads"):
        #                 account.set("highest_roll", 13)

        #         # finally, we set the account back into the database
        #         self.json_interface.set_account(member, account)
        
        # self.json_interface.internal_save()

        # await ctx.send("Done.")

        # JSON_cog = self.bot.get_cog("JSON")
        # cabinet = JSON_cog.get_filing_cabinet("bread", create_if_nonexistent=False)
        # print (f"cabinet is {cabinet}")
        # # bread_files = self.json_interface.data["bread"]
        # for key in cabinet.keys():
        #     file = cabinet[key]
        #     print (f"file is {file}")
        #     if "lifetime_dough" in file.keys():
        #         pass
        #     else:
        #         file["lifetime_dough"] = file["total_dough"]
        # JSON_cog.set_filing_cabinet("bread", cabinet)
        
        
        # #await ctx.send("Do not use this, it does not work.")
        # bread_files = self.json_interface.data["bread_count"]

        # JSON_cog = self.bot.get_cog("JSON")
        # cabinet = JSON_cog.get_filing_cabinet("bread", create_if_nonexistent=True)

        # for key in bread_files.keys():
        # #for file in files:
        #     bread_file = bread_files[key]
        #     cabinet[key] = bread_file
        #     pass
        # pass
        # JSON_cog.set_filing_cabinet("bread", cabinet)

        # old_data = self.json_interface.data["archived_bread_count"]
        # archive_cabinet = JSON_cog.get_filing_cabinet("archived_bread_count", create_if_nonexistent=True)
        # JSON_cog.set_filing_cabinet("archived_bread_count", old_data)

        await ctx.send("Done.")

    ########################################################################################################################
    #####      ADMIN SAVE / ADMIN LOAD
    
    @admin.command()
    @commands.is_owner()
    async def load(self, ctx):

        self.json_interface.internal_load()
        #print("test, 1 arg")
        await ctx.send("Done.")

    @admin.command()
    @commands.is_owner()
    async def save(self, ctx):
        self.json_interface.internal_save()
        await ctx.send("Done.")

    def internal_save(self, json_cog = None):
        print("Bread_cog save has been called")
        self.json_interface.internal_save(json_cog)

    ########################################################################################################################
    #####      ADMIN STONK_FLUCTUATE

    @admin.command()
    @commands.is_owner()
    async def stonk_fluctuate(self, ctx):
        self.stonk_fluctuate_internal()
        await self.stonks_announce() #TODO: test this shit
        await ctx.send("Done.")
        #await ctx.invoke(self.stonks)

    ########################################################################################################################
    #####      ADMIN STONK_RESET

    @admin.command()
    @commands.is_owner()
    async def stonk_reset(self, ctx):
        self.stonk_reset_internal()
        await ctx.invoke(self.stonks)

    ########################################################################################################################
    #####      ADMIN STONK_SPLIT

    @admin.command()
    @commands.is_owner()
    async def stonk_split(self, ctx, stonk_name: str):
        stonk_text = values.get_emote_text(stonk_name)
        self.stonk_split_internal(stonk_text)
        await ctx.reply("Done.")

    ########################################################################################################################
    #####      ADMIN ADD_CHESS_SET

    @admin.command()
    @commands.is_owner()
    async def add_chess_set(self, ctx, target : typing.Optional[discord.Member]):
        if target is None:
            target = ctx.author

        user_account = self.json_interface.get_account(target)
        full_chess_set = values.chess_pieces_black_biased+values.chess_pieces_white_biased

        # add all pieces to the account
        for emote in full_chess_set:
            user_account.increment(emote.text, 1)

        self.json_interface.set_account(target, user_account)

        await ctx.reply("Done.")

    ########################################################################################################################
    #####      ADMIN INCREASE_PRESTIGE

    @admin.command()
    @commands.is_owner()
    async def increase_prestige(self, ctx, target : typing.Optional[discord.Member]):
        
        if await self.await_confirmation(ctx) is False:
            return
        if target is None:
            target = ctx.author

        user_account = self.json_interface.get_account(target)
        user_account.increase_prestige_level()

        self.json_interface.set_account(target, user_account)

        await ctx.reply(f"Done. Prestige level is now {user_account.get_prestige_level()}.")

    ########################################################################################################################
    #####      STRING FORMATTING

    
    def write_number_of_times(number):
        number = int(number)
        if number == 0:
            return "zero times"
        elif number == 1:
            return "once"
        elif number == 2:
            return "twice"
        else:
            return str(number) + " times"

    def format_chess_pieces(file):
        output = ""

        ###############################################################
        
        newline = False
        #make white setup
        #rook 1 
        if white_rook in file.keys() and file[white_rook] >= 1:
            output += white_rook + " "
            newline = True

        #knight 1 white_knight
        if white_knight in file.keys() and file[white_knight] >= 1:
            output += white_knight + " "
            newline = True

        #bishop 1 white_bishop
        if white_bishop in file.keys() and file[white_bishop] >= 1:
            output += white_bishop + " "
            newline = True

        #queen white_queen
        if white_queen in file.keys() and file[white_queen] >= 1:
            output += white_queen + " "
            newline = True

        #king white_king
        if white_king in file.keys() and file[white_king] >= 1:
            output += white_king + " "
            newline = True

        #bishop 2 white_bishop
        if white_bishop in file.keys() and file[white_bishop] >= 2:
            output += white_bishop + " "
            newline = True

        #knight 2 white_knight
        if white_knight in file.keys() and file[white_knight] >= 2:
            output += white_knight + " "
            newline = True

        #rook 2 white_rook
        if white_rook in file.keys() and file[white_rook] >= 2:
            output += white_rook + " "
            newline = True

        if newline:
            output += "\n"
        
        ###############################################################

        #make white pawns
        if white_pawn in file.keys() and file[white_pawn] >= 1:
            for i in range(0, min(8, file[white_pawn])):
                output += white_pawn + " "
            output += "\n"

        #make black pawns
        if black_pawn in file.keys() and file[black_pawn] >= 1:
            for i in range(0, min(8, file[black_pawn])):
                output += black_pawn + " "
            output += "\n"

        ###############################################################

        newline = False
        #make black setup
        #rook 1 black_rook
        if black_rook in file.keys() and file[black_rook] >= 1:
            output += black_rook + " "
            newline = True

        #knight 1 black_knight
        if black_knight in file.keys() and file[black_knight] >= 1:
            output += black_knight + " "
            newline = True

        #bishop 1 black_bishop
        if black_bishop in file.keys() and file[black_bishop] >= 1:
            output += black_bishop + " "
            newline = True

        #queen black_queen
        if black_queen in file.keys() and file[black_queen] >= 1:
            output += black_queen + " "
            newline = True

        #king black_king
        if black_king in file.keys() and file[black_king] >= 1:
            output += black_king + " "
            newline = True

        #bishop 2 black_bishop
        if black_bishop in file.keys() and file[black_bishop] >= 2:
            output += black_bishop + " "
            newline = True

        #knight 2 black_knight
        if black_knight in file.keys() and file[black_knight] >= 2:
            output += black_knight + " "
            newline = True

        #rook 2 black_rook
        if black_rook in file.keys() and file[black_rook] >= 2:
            output += black_rook + " "
            newline = True

        if newline:
            output += "\n"
        
        return output

    

bread_cog_ref = None
bot_ref = None

async def setup(bot):
    
    bread_cog = Bread_cog(bot)
    await bot.add_cog(bread_cog)

    global bread_cog_ref 
    bread_cog_ref = bread_cog
    
    global bot_ref
    bot_ref = bot

    importlib.reload(emoji)
    importlib.reload(verification)
    importlib.reload(values)
    importlib.reload(account)
    importlib.reload(gamble)
    importlib.reload(rolls)
    importlib.reload(store)
    importlib.reload(utility)
    importlib.reload(alchemy)

    try:
        #Bread_cog.internal_load(bot)
        bread_cog.json_interface.internal_load()
    except BaseException as err:
        print(err)
    #bot.add_cog(Chess_game(bot)) #do we want to actually have this be a *cog*, or just a helper class?

#seems mostly useless since we can't call anything async
def teardown(bot):
    print('bread cog is being unloaded.')
    #print("bot is "+str(bot))
    
    #print("bread cog ref is "+str(bread_cog_ref))
    try:
        print("Saving bread data.")
        bread_cog_ref.internal_save()
        print("Done.")
    except BaseException as err:
        print("An error occurred saving bread data.")
        print(err)

    #Bread_cog.internal_save(bot)
    #await bot.graceful_shutdown()
    #Chess_bot.graceful_shutdown(bot)
