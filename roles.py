import discord
import datetime
import asyncio

from discord.ext import commands

#local
import verification

# promote all roles to old guard/etc, if they exist. Othewise fail and cry
@commands.command(
    brief = "[Secret]",
    help = "I told you it's a secret."
)
async def promote(ctx):

    # check for mom
    if not verification.from_owner(ctx): 
        await ctx.send("You're not my mom.")
        return
    
    # lazy-ass error handling
    try:

        beginning_of_place = datetime.datetime(2022, 4, 1, 6)
        end_of_place = datetime.datetime(2022, 4, 4, 17)

        guild = ctx.guild

        in_early = discord.utils.get(ctx.guild.roles, name = "Here When it All Began")
        old_guard = discord.utils.get(ctx.guild.roles, name = "Old Guard")
        filler_role = discord.utils.get(ctx.guild.roles, name = "F")
        #i = 0

        for m in guild.members:
            # short test loop
            #i += 1
            #if i > 5: 
            #    break
        
            join_date = m.joined_at

            printout = "User "

            print(m.display_name, "joined", join_date)

            printout = printout + str(m.display_name) + " joined " + str(join_date)
        
            # error handle a null join date
            if join_date == None:
                print("empty join date")
                continue

            # if already processed
            if "old guard" in [y.name.lower() for y in m.roles]:
                print("already succeeded, skipping")
                continue
            #if already processed 2, electric boogaloo
            if "F" in [y.name for y in m.roles]:
                print("already failed, skipping")
                continue

            # Here when it all began
            if (join_date < beginning_of_place):
                print("adding 'in early'")
                printout += "\nAdding 'here when it all began'."
                await m.add_roles(in_early)
            # old guard
            if (join_date < end_of_place):
                print("adding 'old guard")
                printout += "\nAdding 'Old Guard'."
                await m.add_roles(old_guard)
            #filler
            else:
                print("no roles applicable, adding filler")
                printout += "\nno roles applicable, Adding filler."
                await m.add_roles(filler_role)

            
            await ctx.send(printout)
            #await asyncio.sleep(5) #inherently wait limited, no need for the sleep command here
        
    #if error
    except BaseException as err:
        print(err)
        await ctx.send("Unable to comply: "+str(err))

    #if success
    else:
        await ctx.send('Done.')
        print("Done.")

async def setup(bot):
    bot.add_command(promote)