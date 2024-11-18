import random
import math
import typing
import discord
import hashlib
import copy
from discord.ext import commands

def smart_number(number: int) -> str:
    """Adds commas to the given number, and returns the output."""
    shrink_large_numbers = False
    if shrink_large_numbers is False:
        return f"{number:,}"
    else:
        marker = ""
        fraction = 0
        if number > 1000000000000:
            marker = "T"
            fraction = number / 1000000000000
        elif number > 1000000000:
            marker = "B"
            fraction = number / 1000000000
        elif number > 1000000:
            marker = "M"
            fraction = number / 1000000
        elif number > 10000:
            marker = "K"
            fraction = number / 1000
        else:
            return f"{number:,}"
        
        if fraction > 100:
            return f"{int(fraction):,} {marker}"
        elif fraction > 10:
            return f"{fraction:.1f} {marker}"
        else:
            return f"{fraction:.2f} {marker}"


def write_number_of_times(number: int) -> str:
    """Returns the number of times something has occurred corresponding to the given number. So if 3 is passed it'll return '3 times', but if 1 is passed it will return 'once'."""
    if type(number) is str:
        number = int(number)
    if number == 0:
        return "zero times"
    elif number == 1:
        return "once"
    elif number == 2:
        return "twice"
    else:
        return smart_number(number) + " times"

def write_count(
        number: int,
        word: str
    ) -> str:
    """Writes the count of a number and word, and will pluralize the word if the number is not 1."""
    if number == 1:
        pass
    else:
        word =  word + "s"
    output = smart_number(number) + " " + word
    return output

def array_subtract(
        array1: list,
        array2: list
    ) -> list:
    """Subtracts one list from another by returning all the items in array1 that are not in array2."""
    #return [x for x in array1 if x not in array2]
    output = list()
    output.extend(array1)
    #print(f"Array subtract: subtracting {array2} from {array1}")
    #print(f"output: {output}")
    for object in array2:
    #for i in range(len(array2)):
        
        #object = array2[i]
        #print(f"Object {i} is {object}")
        if object in output:
            #print(f"Object {i} is in output")
            output.remove(object)
            #print(f"Removing. Output is now {output}")
            #this is subtly different, but it means that duplicate members are only removed one at a time
    return output

def dict_subtract(
        dict1: dict,
        dict2: dict
    ) -> dict:
    """Subtracts one dictionary from another by returning a dict containing all the keys and values of dict1, subtraced by the same keys in dict2.
    Via this subtraction, if a value goes less than or equal to 0 it will be removed."""
    output = dict()
    output.update(dict1)
    for key in dict2:
        if key in output:
            output[key] -= dict2[key]
            if output[key] <= 0:
                del output[key]
    return output


def increment(
        dictionary: dict,
        key: str,
        amount: int = 1
    ) -> dict:
    """Increments a key in a dictionary by the given amount."""
    if key in dictionary:
        dictionary[key] += amount
    else:
        dictionary[key] = amount
    return dictionary

# returns a random number between 0 and 1, biased towards the edges
def rand_sigmoid(x: typing.Optional[int] = None) -> float:
    """Returns a random number between 0 and 1, but biased towards the edges."""
    if x is None:
        x = random.uniform(-1, 1)
    else:
        x = x * 2 - 1
    sigmoid =  1 / (1 + math.exp(-x*6))
    linear = (.5 + x/2)

    if sigmoid < 0:
        sigmoid = 0
    elif sigmoid > 1:
        sigmoid = 1

    sig_blend = .5

    output =  (sigmoid * sig_blend) + (linear * (1 - sig_blend))

    return output

#returns a random number between 0 and 1, biased towards the middle
def rand_logit(x: typing.Optional[int] = None) -> float:
    """Returns a random number between 0 and 1, but biased towards the middle."""
    if x is None:
        x = random.uniform(0, 1)
    
    if x == 0:
        return 0
    elif x == 1:
        return 1
    
    logit =  math.log(x / (1 - x)) / 6
    linear = x*2 - 1

    if logit < -1:
        logit = -1
    elif logit > 1:
        logit = 1

    logit_blend = .3

    output =  (logit * logit_blend) + (linear * (1 - logit_blend))

    return remap(output, -1, 1, 0, 1)

def remap(
        x: typing.Union[int, float],
        in_min: typing.Union[int, float],
        in_max: typing.Union[int, float],
        out_min: typing.Union[int, float],
        out_max: typing.Union[int, float]
    ) -> float:
  """Remaps a number between a min and max to a different min and max."""
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def normalize_array_to_ints(
        array: list,
        target_total: int = 1000
    ) -> list[int]:
    """Normalizes a list to shift the total value to the target total."""
    total = sum(array)
    if total == 0:
        return array
    new_array = [x / total for x in array]
    for x in range(len(new_array)):
        new_array[x] = round(new_array[x] * target_total)
    return new_array


def contains_ping(string: str) -> bool:
    """Returns a boolean for whether a given string contains a ping."""
    if "<@" in string:
        return True
    elif "@everyone" in string:
        return True
    elif "@here" in string:
        return True
    else:
        return False

def sanitize_ping(string: str) -> str:
    """Returns the input string but with invisible characters (U+200B) placed to avoid pings."""
    output = string.replace("@everyone", "@\u200beveryone")
    output = output.replace("@here", "@\u200bhere")
    output = output.replace("<@", "<@\u200b")
    return output

# this will first try a regular reply, and if that fails, it will send it as a plain message with a mention
async def smart_reply(
        ctx: typing.Union[commands.Context, discord.Message],
        message: str,
        ping_reply: bool = True
    ) -> typing.Optional[discord.Message]:
    """Attempts to reply nromally, then if that fails tries to send it as a plain message with a ping.
    
    Will abide by the ping reply parameter."""
    if message == "" or message is None:
        return None
        
    # Try except block to catch errors 
    try:
        message = await ctx.reply(message, mention_author=ping_reply)
    except discord.HTTPException:
        # Sending the message has failed, so the message we're trying to reply to has likely been deleted.
        if ping_reply:
            # Ping reply is on, so send the message normally but with a ping at the start.
            message = await ctx.send(f"{ctx.author.mention}\n\n{message}")
        else:
            # Ping reply is off, so send the message and put the author's display name at the top, so they know it's theirs.
            message = await ctx.send(f"{sanitize_ping(ctx.author.display_name)}:\n\n{message}")
    except:
        # Some other exception has occurred, so reraise it.
        raise
        
    return message

def plot_line(
        start: tuple[int, int],
        end: tuple[int, int]
    ) -> list[tuple[int, int]]:
    """Plots a line between two points. Returns a list of points that make the line, in order."""
    points = []

    x1, y1 = start
    x2, y2 = end

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    error = dx - dy
    x, y = x1, y1

    while True:
        points.append((x, y))

        if x == x2 and y == y2:
            break

        e2 = 2 * error
        if e2 > -dy:
            error -= dy
            x += sx
        if e2 < dx:
            error += dx
            y += sy

    return points

def hash_args(*args, separator: str = "") -> str:
    """Converts a list of args into a string, and then returns the SHA-256 hash of it."""
    return hashlib.sha256(separator.join([str(arg) for arg in args]).encode()).digest()

def get_display_name(member: discord.Member) -> str:
    """Gets the display name of a discord.Member object."""
    return (member.global_name if (member.global_name is not None and member.name == member.display_name) else member.display_name)

#################################################################################################################
#################################################################################################################
#################################################################################################################

everyone_prevention = discord.AllowedMentions(everyone=False, roles=False)

class CustomContext(commands.Context):    
    async def safe_reply(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message:        
        kwargs["allowed_mentions"] = everyone_prevention

        return await super().reply(content, **kwargs)
    
    async def send(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message:
        kwargs["allowed_mentions"] = everyone_prevention

        return await super().send(content, **kwargs)
    
    async def reply(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message | None:
        if (content is None or len(str(content)) == 0) and kwargs.get("embed", None) is None and kwargs.get("file", None) is None:
            return None
        
        try:
            return await self.safe_reply(content, **copy.deepcopy(kwargs))
        except discord.HTTPException:
            # If something went wrong replying.
            if kwargs.get("mention_author", True):
                return await self.send(f"{self.author.mention},\n\n{content}", **kwargs)
            else:
                return await self.send(f"{sanitize_ping(self.author.display_name)},\n\n{content}", **kwargs)

class CustomBot(commands.Bot):
    # THIS CAN ONLY BE RELOADED BY RESTARTING THE ENTIRE BOT.
    
    async def get_context(
            self: typing.Self,
            message: discord.Message,
            *,
            cls=CustomContext):
        return await super().get_context(message, cls=cls)