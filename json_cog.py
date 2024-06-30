import json
import os
from datetime import datetime
import importlib
import asyncio
import typing
import time

import discord
from discord.ext import commands
from discord.ext import tasks

import verification

####################################################
##############   JSON INTERFACE   ##################
####################################################


class JSON_cog(commands.Cog, name="JSON"):
    
    
    ####################################
    #####      SETUP

    file_path = "database.json"

    default_guild = '958392331671830579'

    default_data = {
        'load_count' : 0,
        default_guild: {
            'bread': {},
            'enforcement' : {
                "546829925890523167": {
                    "username": "Melodie",
                    "display_name": "Melodie",
                    "total_timeout": 1,
                    "bricks": 1
                },
            },
        }
    }

    data = dict()

    ########################################################################################################################
    #####      INIT / DE-INIT

    def __init__(self, bot):
        #print("bread __init__ called")
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()
        pass

    ########################################################################################################################
    #####      TASKS

    
    @tasks.loop(minutes=60)
    async def daily_task(self):
        # NOTE: THIS LOOP CANNOT BE ALTERED ONCE STARTED, EVEN BY RELOADING. MUST BE STOPPED MANUALLY
        time = datetime.now()

        self.save_all_data() # save every hour
        print("doing hourly save of JSON data")
        
        if time.hour == 15:
            self.create_backup()
            

            print("Daily JSON backup called")

    @daily_task.before_loop
    async def before_daily(self):
        # This just waits until it's time for the first iteration.
        print("Starting JSON cog hourly loop, current time is {}.".format(datetime.now()))

        minute_in_hour = 5 # 5 would be X:05, 30 would be X:30.

        wait_time = time.time() - (minute_in_hour * 60)
        wait_time = 3600 - (wait_time % 3600) + 2 # Artificially add 2 seconds to ensure it stops at the correct time.

        print("Waiting to start JSON cog hourly loop for {} minutes.".format(round(wait_time / 60, 2)))
        
        await asyncio.sleep(wait_time)
        
        print("Finished JSON cog hourly loop waiting at {}.".format(datetime.now()))

    
    
    def capture_and_save_data(self):

        # save chess data
        try:
            print("JSON Cog: attempting to save Chess data")
            chess_cog = self.bot.get_cog("Chess")
            chess_cog.internal_save(self)
            print("Done.")
        except BaseException as err:
            print("Unable to do so.")
            print(err)

        # save bread data
        try:
            print("JSON Cog: attempting to save Bread data")
            bread_cog = self.bot.get_cog("Bread")
            bread_cog.internal_save(self)
            print("Done.")
        except BaseException as err:
            print("Unable to do so.")
            print(err)

        self.save_all_data()
        print("JSON cog: all data saved.")
        pass

    ########################################################################################################################
    #####      COMMANDS

    @commands.group(
        hidden = True,
        brief="[Restricted]",
    )
    async def JSON(self, ctx):
        if not verification.from_owner(ctx.author):
            await ctx.reply(verification.get_rejection_reason())
        if ctx.invoked_subcommand is None:
            print("admin called on nothing")
            return
    
    @JSON.command()
    @commands.is_owner()
    async def save(self, ctx):
        self.internal_save()
        await ctx.send("Done.")

    @JSON.command()
    @commands.is_owner()
    async def load(self, ctx):
        try:
            self.internal_load()
            await ctx.send("Done.")
        except:
            await ctx.send("Failed.")
            raise


    @JSON.command()
    @commands.is_owner()
    async def show(self, ctx):
        print("Printing all data:")
        print(json.dumps(self.data, indent=2))
        await ctx.send("Done.")

    @JSON.command()
    @commands.is_owner()
    async def backup(self, ctx):
        print("Creating backup")
        self.create_backup()
        await ctx.send("Done.")

    ####################################
    #####      FILE STUFF

    def load_all_data(self):
        self.internal_load()

    def internal_load(self):
        print("JSON internal_load called")
        try:
            with open(self.file_path) as json_file:
                self.data = json.load(json_file)
                #print("Loaded "+self.file_path+", contents are:")
                #print(self.data)
            
            #self.data = json.loads(raw_data)
            self.data['load_count'] += 1

        except:
            print("Error loading "+self.file_path)
            self.data = self.default_data

        self.transfer_data_if_nonexistent()

    def transfer_data_if_nonexistent(self):
        # originallly the format was to have everything stored in a flat heirarchy, but now we have guilds and vaults
        # and we want to transfer the old data into the new format, at least once
        # first we check if we have already done it
        default_guild = '958392331671830579'

        if default_guild in self.data.keys():
            return
        # then we go through the old data and transfer it
        print("Transferring old data to new format")
        self.data[default_guild] = dict()
        if 'bread' in self.data.keys():
            self.data[default_guild]['bread'] = self.data['bread']
            del self.data['bread']
        if 'enforcement' in self.data.keys():
            self.data[default_guild]['enforcement'] = self.data['enforcement']
            del self.data['enforcement']
        if 'chess' in self.data.keys():
            self.data[default_guild]['chess'] = self.data['chess']
            del self.data['chess']
        if 'archived_bread_count' in self.data.keys():
            self.data[default_guild]['archived_bread_count'] = self.data['archived_bread_count']
            del self.data['archived_bread_count']
        print("Done.")

        
    def save_all_data(self):
        self.internal_save()
    
    def internal_save(self):
        print("saving JSON data")
        #json_string = json.dumps(self.data, indent=2)

        # "Directly" from dictionary
        with open(self.file_path, 'w') as outfile:
            json.dump(self.data, outfile, indent=2)

    def create_backup(self):

        #first, make sure there's a backup folder (relative path)
        folder_path = "backup/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        #then, we make the file
        file_name = datetime.now().strftime('database_backup_%Y:%m:%d_%X.json')
        with open(folder_path+file_name, 'w') as outfile:
            print('created ', file_name)
            #json_string = json.dumps(self.data, indent=2)
            json.dump(self.data, outfile, indent=2)

        print("Backup Created.")


    ####################################
    #####      INTERFACE NEW

    # every server has a vault. In each vault there is a "bread" and a "chess" among other things
    def get_vault(self, guild: typing.Union[discord.Guild, int, str]):
        
        if guild is None:
            # print ("No guild was passed, using default vault")
            # vault = self.data.get(self.default_guild, None)
            raise Exception("No guild was passed")
        elif isinstance(guild, discord.Guild):
            vault = self.data.get(str(guild.id), None)
        elif isinstance(guild, int):
            vault = self.data.get(str(guild), None)
        elif isinstance(guild, str):
            vault = self.data.get(guild, None)
        else:
            return None
    
        if vault is None:
            print ("guild not found, creating new vault")
            vault = dict()
            self.set_vault(guild, vault)

        return vault

    def set_vault(self, guild: typing.Union[discord.Guild, int, str], vault: dict):
        if isinstance(guild, discord.Guild):
            self.data[str(guild.id)] = vault
        elif isinstance(guild, int):
            self.data[str(guild)] = vault
        elif isinstance(guild, str):
            self.data[guild] = vault
        elif guild is None:
            self.data[self.default_guild] = vault
            
    
    def get_filing_cabinet(self, name: str, guild: typing.Union[discord.Guild, int, str] = None, create_if_nonexistent=False):
        vault = self.get_vault(guild)

        if name in vault.keys():
            return vault[name]
        elif create_if_nonexistent:
            vault[name] = dict()
            self.set_vault(guild, vault)
            return vault[name]
        else:
            return None
        
    def set_filing_cabinet(self, name: str, cabinet: dict, guild: typing.Union[discord.Guild, int, str] = None):
        vault = self.get_vault(guild)
        vault[name] = cabinet
        self.set_vault(guild, vault)
    
    def set_file_in_filing_cabinet(self, cabinet_name: str, file_name: str, file: dict, guild: typing.Union[discord.Guild, int, str] = None):
        cabinet = self.get_filing_cabinet(cabinet_name, guild, create_if_nonexistent=True)
        cabinet[file_name] = file
        self.set_filing_cabinet(cabinet_name, cabinet, guild)
    
    def delete_file_in_filing_cabinet(self, cabinet_name: str, file_name: str, guild: typing.Union[discord.Guild, int, str] = None):
        cabinet = self.get_filing_cabinet(cabinet_name, guild, create_if_nonexistent=True)
        if file_name in cabinet.keys():
            del cabinet[file_name]
        self.set_filing_cabinet(cabinet_name, cabinet, guild)

    def get_list_of_all_guilds(self):
        output = []
        for key in self.data.keys():
            if key == 'load_count':
                continue
            if key.isnumeric() is False:
                continue
            output.append(key)
        return output
    """
    # cheeky name for the meta-groups such as bread and enforcement
    def get_filing_cabinet(self, name: str, create_if_nonexistent=False):
        if name in self.data.keys():
            return self.data[name]
        elif create_if_nonexistent:
            self.data[name] = dict
            return self.data[name]
        else:
            return None

    def set_filing_cabinet(self, name: str, cabinet: dict):
        self.data[name] = cabinet
    """
    ####################################
    #####      INTERFACE

    """
    def get_file_for_user(self, cabinet_name: str, user: discord.member): 
        key = str(user.id)
        cabinet = self.get_filing_cabinet(cabinet_name)

        if key in cabinet.keys():
            #print("Found")
            return cabinet[key]
        else:
            print(f"Creating new data for {user.display_name} in {cabinet_name}")
            new_file = {
                'username' : user.name,
                'display_name' : user.display_name
            }
            cabinet[key] = new_file
            self.set_filing_cabinet(cabinet_name, cabinet)
            return new_file

    def set_file_for_user(self, cabinet_name: str, user: discord.member, file: dict): 
        key = str(user.id)
        cabinet = self.get_filing_cabinet(cabinet_name)
        cabinet[key] = file
        self.set_filing_cabinet(cabinet_name, cabinet)
    """


json_cog_ref = None

async def setup(bot):
    print("JSON cog being loaded")
    json_cog = JSON_cog(bot)

    importlib.reload(verification)

    
    global json_cog_ref 
    json_cog_ref = json_cog
    await bot.add_cog(json_cog)

    #try:
        #Bread_cog.internal_load(bot)
    json_cog.internal_load()
    #except BaseException as err:
    #    print(err)
    #bot.add_cog(Chess_game(bot)) #do we want to actually have this be a *cog*, or just a helper class?

#seems mostly useless since we can't call anything async
def teardown(bot):
    print('JSON cog is being unloaded.')
    
    #try:
    json_cog_ref.capture_and_save_data()
    #json_cog_ref.internal_save()
    #except BaseException as err:
    #    print(err)

    #Bread_cog.internal_save(bot)
    #await bot.graceful_shutdown()
    #Chess_bot.graceful_shutdown(bot)
