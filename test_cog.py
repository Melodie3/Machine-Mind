
import asyncio
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext import tasks
import importlib
import typing

import verification


import json

class Test_cog(commands.Cog, name="Test"):
    pass
    
    def __init__(
            self: typing.Self,
            bot: commands.Bot
        ) -> None:
        print("test __init__ called")
        self.bot = bot
        #self.loop_task.start()

    def cog_unload(self: typing.Self):
        self.loop_task.cancel()
        pass

    @commands.command(
    )
    async def test(self, ctx, *args):
        print("test, "+str(len(args))+" args")

    @commands.command(
        hidden=True
    )
    async def edit_test(ctx):
        #admin only 
        if not verification.from_owner(ctx.author):
            await ctx.reply(verification.get_rejection_reason())
            return
        
        count = 5
        message = await ctx.send("BRICK TIME.")
        await asyncio.sleep(3)

        for i in range(count):
            await message.edit(content = str(count)+".")
            await asyncio.sleep(1)
            count -= 1

        await message.edit(content = ":bricks:")


    ########################################################################################################
    ######### SAVE / LOAD TEST
    
    # data2 = {
    #     'employees' : [
    #         {
    #             'name' : 'John Doe',
    #             'department' : 'Marketing',
    #             'place' : 'Remote'
    #         },
    #         {
    #             'name' : 'Jane Doe',
    #             'department' : 'Software Engineering',
    #             'place' : 'Remote'
    #         },
    #         {
    #             'name' : 'Don Joe',
    #             'department' : 'Software Engineering',
    #             'place' : 'Office'
    #         }
    #     ]
    # }
    
    # data1 = { 'employees' : ["rob", "zeke"] }
    # #json_string = json.dumps(data, indent=4)

    # data = { 'employees' : 0 }

    # @commands.command(
    # )
    # async def test_load(self, ctx):

    #     self.internal_load()
    #     #print("test, 1 arg")
    #     await ctx.send("Done.")
    
    # def internal_load(self):
    #     with open('test_data.json') as json_file:
    #         raw_data = json.load(json_file)
    #         print(raw_data)
        
    #     self.data = json.loads(raw_data)
    #     print("Testing individual data:")
    #     print(self.data['employees'])
    #     print("incrementing by 1")
    #     self.data['employees'] = self.data['employees'] + 1
    #     print("is now "+str(self.data['employees']))

    # @commands.command()
    # async def test_save(self, ctx):
    #     self.internal_save()
    #     await ctx.send("Done.")
    
    # def internal_save(self):
    #     print("saving test data")
    #     json_string = json.dumps(self.data, indent=4)

    #     # "Directly" from dictionary
    #     with open('test_data.json', 'w') as outfile:
    #         json.dump(json_string, outfile)
        

    ########################################################################################################
    ######### GROUP TEST

    @commands.group()
    async def test(self, ctx):
        print("test group called")
        pass

    @test.command()
    async def blackjack(self, ctx, amount: int):
        await ctx.send("Welcome to blackjack!")
        print("test blackjack called")
        playing = True

        while playing:

            await ctx.send("your hand is: AJ5, what would you like to do?")

            try:
                await self.bot.wait_for(event = 'message', check = lambda m: m.author == ctx.author)
            except asyncio.TimeoutError:
                pass
            else:
                pass #handle message here
            pass
            playing = False

    @test.command()
    async def meta_backup(self, ctx):
        try:
            print(f"Bot cogs are {self.bot.cogs}")
        except Exception as exception:
            print("Exception: {}".format(type(exception).__name__))
            print("Exception message: {}".format(exception))


        try:
            print("Attempting reference through cog")
            bread_cog = self.bot.get_cog("Bread")
            print(f"Bread cog is {bread_cog}")
            bread_cog.save()
            print("Bread cog backup called")
        except Exception as exception:
            print("Exception: {}".format(type(exception).__name__))
            print("Exception message: {}".format(exception))

    @test.command()
    async def gift(self, ctx, target: discord.Member, arg1: typing.Union[int, str], arg2:typing.Union[int, str]):
        print(f"arg1 type was {type(arg1)} and arg2 type was {type(arg2)}")
        if type(arg1) is int and type(arg2) is str:
            amount = arg1
            emoji = arg2
        elif type(arg1) is str and type(arg2) is int:
            amount = arg2
            emoji = arg1
        elif type(arg1) is None or type(arg2) is None:
            await ctx.reply("Needs an amount and what to gift.")

    @test.group()
    async def admin(self, ctx):
        print("meta admin called")
        if ctx.invoked_subcommand is None:
            print("admin running internal logic")
    
    @admin.group()
    async def reset(self, ctx):
        print("meta admin reset called")

    ########################################################################################################
    ######### LOOP TEST

    @tasks.loop(seconds=5.0)
    async def loop_task(self: typing.Self):
        second = datetime.now().second
        print ("Test loop running at second "+str(second))
        #if datetime.now().hour == 15:
        if second >= 20 and second < 25:
            # Do something
            print("Event called")

    @loop_task.after_loop
    async def after_loop_task(self):
        print('loop task ended')

def setup(bot: commands.Bot):
    importlib.reload(verification)

    bot.add_cog(Test_cog(bot))
    try:
        Test_cog.internal_load(bot)
    except BaseException as err:
        print(err)
    #bot.add_cog(Chess_game(bot)) #do we want to actually have this be a *cog*, or just a helper class?

#seems mostly useless since we can't call anything async
def teardown(bot: commands.Bot):
    print('test bot is being unloaded.')
    Test_cog.internal_save(bot)
    #await bot.graceful_shutdown()
    #Chess_bot.graceful_shutdown(bot)
