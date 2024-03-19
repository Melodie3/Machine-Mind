import discord
import random

owner_id = 546829925890523167
friends_list = {720740678371508326, #peng
                713053430075097119} #Kapola7
enemies_list = {663183409564221441, #mooselord
                712827842299166841} #yeetlord
                
mildly_disliked_list = {270488993500626945, #Shmeverton
                        117093963701157896} #amifama
                        #797186556501688390} #emery #removed from meanie list.... for now.

# checks for "Mother of Bots" tag
def from_owner(user: discord.Member) -> bool:
    """Returns boolean for whether the given member has the same user id as the `owner_id` variable in this file."""
    if (user.id == owner_id):
        return True
    else:
        return False

    #if "mother of bots" in [y.name.lower() for y in ctx.message.author.roles]:
    #    #print("command comes from Mom")
    #    return True
    #else:
    #    #print("command not from Mom")
    #    return False

rejection_reasons = ["You're not my mom.",
                    "Insufficient privileges.",
                    "Please verify your identity first.",
                    "I cannot do that.",
                    "Rejected."]

def get_rejection_reason() -> str:
    """Returns a random item in the rejection_reasons list."""
    return random.choice(rejection_reasons)


def from_friend(user: discord.Member) -> bool:
    """Returns boolean for whether the user is a friend."""
    #print("checking for friend, user is "+str(ctx.message.author.id))
    for id in friends_list:
        if user.id == id:
            return True
    return False


def from_enemy(user: discord.Member) -> bool:
    """Returns boolean for whether the user is an enemy."""
    #print("checking for enemy, user is "+str(ctx.message.author.id))
    for id in enemies_list:
        if user.id == id:
            return True
    return False
    # ctx.message.author

def from_mildly_disliked(user: discord.Member) -> bool:
    """Returns boolean for whether the user is mildly disliked."""
    for id in mildly_disliked_list:
        if user.id == id:
            return True
    return False

def has_role(
        user: discord.Member,
        role_name: str
    ) -> bool:
    """Returns bool for whether the given user has a role matching the given role name."""
    if role_name.lower() in [r.name.lower() for r in user.roles]:
        return True
    return False

def is_owner(user: discord.Member) -> bool:
    """Returns boolean for whether the given member has the same user id as the `owner_id` variable in this file."""
    if (user.id == owner_id):
        return True
    return False