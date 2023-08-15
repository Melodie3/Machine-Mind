import random
import math
import typing

def smart_number(number: int) -> str:
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


def write_number_of_times(number):
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

def write_count(number: int, word: str) -> str:
    if number == 1:
        pass
    else:
        word =  word + "s"
    output = smart_number(number) + " " + word
    return output

def array_subtract(array1, array2):
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


def increment(dictionary: dict, key, amount: int =1) -> dict:
    if key in dictionary:
        dictionary[key] += amount
    else:
        dictionary[key] = amount
    return dictionary

# returns a random number between 0 and 1, biased towards the edges
def rand_sigmoid(x: typing.Optional[int] = None):
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
def rand_logit(x: typing.Optional[int] = None):
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

def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def contains_ping(string: str) -> bool:
    if "<@" in string:
        return True
    elif "@everyone" in string:
        return True
    elif "@here" in string:
        return True
    else:
        return False

def sanitize_ping(string: str) -> str:
    output = string.replace("@everyone", "@\u200beveryone")
    output = output.replace("@here", "@\u200bhere")
    output = output.replace("<@", "<@\u200b")
    return output

# this will first try a regular reply, and if that fails, it will send it as a plain message with a mention
async def smart_reply(ctx, message):
    if message == "" or message is None:
        return None
    try:
        message = await ctx.reply(message)
    except:
        message = await ctx.send(f"{ctx.author.mention}\n\n{message}")
    return message
