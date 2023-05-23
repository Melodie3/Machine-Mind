import json
import os
from datetime import datetime
import importlib
import asyncio

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

    default_data = {
        'load_count' : 0,
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
        print('Booting up JSON loop')
        #wait to be closer to the hour
        time = datetime.now()

        if time.minute > 10:
            #wait into next hour
            wait_time = max(70 - time.minute, 0)
            print (f"waiting before JSON loop for {wait_time} minutes")
            await asyncio.sleep(60*wait_time)
            print (time.strftime("Finished waiting at %H:%M:%S"))

    
    def capture_and_save_data(self):

        # save chess data
        try:
            print("JSON Cog: attempting to save Chess data")
            chess_cog = self.bot.get_cog("Chess")
            chess_cog.capture_data(self)
            print("Done.")
        except BaseException as err:
            print("Unable to do so.")
            print(err)

        # save chess data
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

    ####################################
    #####      INTERFACE

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