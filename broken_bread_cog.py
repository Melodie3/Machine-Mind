import discord
from discord.ext import commands

broken_bread_text = """The bread shop is completely destroyed. Debris from the bombs set by Prockpj are embedded in every nearby surface.

The bread machine lies in a heap of wreckage strewn about the floor. Burn marks scar the surface of anything remaining.

Occasionally, a stray breath of wind comes through and pushes up small clouds of yeast and flour.

If you want bread, you'll have to go elsewhere."""

class Broken_Bead_cog(commands.Cog, name="Broken_Bread"):
    @commands.command(
        brief="Bread.",
        help="It's bread."
    )
    async def bread(self, ctx): #, *args):
        #print("bread called with "+str(len(args))+" args: "+str(args))

        await ctx.reply(broken_bread_text)

        pass

def setup(bot):
    
    bread_cog = Broken_Bead_cog(bot)
    bot.add_cog(bread_cog)
    print("broken bread bot loaded")