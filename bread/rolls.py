import random
import bread.values as values
import bread.account as account
import bread.utility as utility
import bread.store as store



def bread_roll(roll_luck = 1, roll_count = 1, user_account: account.Bread_Account = None):

    output = dict()

    output_count_commentary = ""
    output_count_commentary_value = 0

    output_loaf_commentary = ""
    output_loaf_commentary_value = 0

    output_roll_messages = list()

    output_highest_roll = 0

    output_profit = 0
    gambit_shop_bonus = 0

    output["individual_values"] = list()

    # what we'll do, is we'll have one commentary message, and a bunch of roll messages
    # each roll message will have up to 20 emotes in it
    # the commentary message will have the most valuable emote and the most valuable amount message in it
    
    for i in range(roll_count):

        profit = 0
        count_commentary = ""

        #roll 1-10 (or 11 or more) breads, each one has a chance to be something different
        loaf_count = random.randint(1,10)

        out_luck = roll_luck
        lottery = False

        if random.randint(1,4096) == 1: #lottery win
            # if you have more than 100 max daily rolls, you'll get extra rolls on the lottery
            loaf_count = max(100, user_account.get("max_daily_rolls"))
            # but the base profit goes down to compensate
            profit = max(0, 1000-loaf_count)
            out_luck = max(roll_luck*4, 16) # extra lucky
            count_commentary = "You won the lottery!!!! Congratulations!!!"
            output = utility.increment(output, "lottery_win", 1)
            lottery = True
            #lottery
        
        # this section does 11 and higher breads
        elif random.randint(1,512) == 1: # normally 512
            loaf_count = 11
            while random.randint(1,2) == 1:
                loaf_count += 1

        # print (f"roll_count: {roll_count}")

        if loaf_count == 1:
            count_commentary = "Better luck next time."
            output = utility.increment(output, "natural_1", 1)
        elif loaf_count == 10:
            count_commentary = "Congratulations! You found all 10 loaves."
            output = utility.increment(output, "ten_breads", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 11:
            count_commentary = "Eleven breads? How strange."
            output = utility.increment(output, "eleven_breads", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 12:
            count_commentary = "TWELVE BREADS??"
            output = utility.increment(output, "twelve_breads", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 13:
            count_commentary = "NANI????!? THIRTEEN BUREADOS!?!?"
            output = utility.increment(output, "thirteen_breads", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 14:
            count_commentary = "Fourteen breads? That's a lot of breads. Like really a lot."
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 15:
            count_commentary = "Woah! Fifteen breads! It really do be like that."
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 16:
            count_commentary = "Surely that's not possible. Sixteen breads?!"
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 17:
            count_commentary = "Seventeen breads? You're a wizard, Harry."
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 18:
            count_commentary = "A historical occurence! Eighteen breads!"
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count == 19:
            count_commentary = "Nineteen breads. I have no words for such a confluence of events."
            output = utility.increment(output, "fourteen_or_higher", 1)
            output["highest_roll"] = loaf_count
        elif loaf_count > 19 and loaf_count < 100:
            count_commentary = f"Holy hell! {loaf_count} breads!"
            output["highest_roll"] = loaf_count
            output = utility.increment(output, "fourteen_or_higher", 1)
        elif count_commentary is None:
            count_commentary = ""

        # set the highest roll if it's not 100
        if loaf_count < 100:
            output_highest_roll = max(output_highest_roll, loaf_count)

        emote_output = ""

        for i in range(1,loaf_count+1):


            ######
            ############################################################

            roll = loaf_roll(luck=out_luck, 
                            user_account=user_account)

            ############################################################
            ######


            value = roll["emote"].value + roll["extra_profit"]
            gambit_shop_bonus += roll["extra_profit"]
            # emote_text = roll["emote"].get_representation(None)
            emote_text = roll["emote"].text
            profit += value
            # profit += roll["extra_profit"]
            emote_output += emote_text + " "

            if emote_text in output.keys():
                output[emote_text] += 1
            else:
                output[emote_text] = 1

            # add all attributes in
            for attribute in roll["emote"].attributes:
                if attribute in output.keys():
                    output[attribute] += 1
                else:
                    output[attribute] = 1

            # add newlines
            if lottery == False: #user_account.get("compound_roller") == 0:
                if i % 5 == 0:
                    emote_output += "\n"
            else:
                if i % 10 == 0:
                    emote_output += "\n"

            # split into multiple messages if it's too long
            if i % 50 == 0:
                output_roll_messages.append(emote_output)
                emote_output = ""

            # make sure to only include the commentary for the most significant piece
            if value > output_loaf_commentary_value:
                output_loaf_commentary = roll["commentary"]
                output_loaf_commentary_value = value

        #add rest of emote output
        if emote_output != "":
            output_roll_messages.append(emote_output)

        # if the commentary is of a higher value than the previous one, replace it
        if (loaf_count > output_count_commentary_value) and (count_commentary != ""):
            output_count_commentary = count_commentary
            output_count_commentary_value = loaf_count
        
        output_profit += profit
        
        output["individual_values"].append(profit)

        # if profit > output_loaf_commentary_value:
        #     output_loaf_commentary = loaf_commentary
        #     output_loaf_commentary_value = profit

        # if count_commentary != "" and loaf_commentary != "":
        #     output["commentary"] = count_commentary + "\n\n" + loaf_commentary
        # elif count_commentary != "":
        #     output["commentary"] = count_commentary
        # elif loaf_commentary != "":
        #     output["commentary"] = loaf_commentary
        # else:
        #     output["commentary"] = None
        # output["emote_text"] = emote_output
        
        # output["lifetime_dough"] = profit
        # output["total_dough"] = profit

    # now we set all the calculated output values
    output["highest_roll"] = output_highest_roll

    if gambit_shop_bonus > 0:
        output["gambit_shop_bonus"] = gambit_shop_bonus

    # output all the roll messages
    output["roll_messages"] = output_roll_messages


    output["commentary"] = ""

    if roll_count > 1:
        output["commentary"] += f"Multiroll of {roll_count} complete."

    # it's not better luck next time if you got something nice
    if output_count_commentary == "Better luck next time.":
        if output_loaf_commentary != "":
            output_count_commentary = ""

    # add count commentary
    if output_count_commentary != "":
        if output["commentary"] != "": # add newlines to separate
            output["commentary"] += "\n\n"
        output["commentary"] += output_count_commentary

    if output_loaf_commentary != "":
        if output["commentary"] != "": # add newlines to separate
            output["commentary"] += "\n\n"
        output["commentary"] += output_loaf_commentary
    
    if output["commentary"] == "":
        output["commentary"] = None

    # add profit to the output
    # output["lifetime_dough"] = output_profit
    # output["total_dough"] = output_profit
    output["value"] = output_profit

    return output

def loaf_roll(luck = 1, user_account: account.Bread_Account = None):
    #output what it's getting called with
    #print (f"loaf roll called with luck: {luck}, include_moaks: {include_moaks}, max_daily_rolls: {max_daily_rolls}")
    # odds_mult = 4
    moak_rarity_mult = round(user_account.get("max_daily_rolls") / 10)
    gem_boost = user_account.get_shadow_gold_gem_boost_count()

    output = {}
    output["extra_profit"] = 0
    

    moak_luck = round( luck * store.moak_booster_multipliers[ user_account.get("moak_booster") ])
    gem_luck = luck + gem_boost

    lc_booster = user_account.get("LC_booster")
    if lc_booster > 0:
        lc_boost = 2 ** lc_booster
        # luck = (luck - 1) * 4 + 1 # base luck of 1, with 8x multiplier for LCs
        # gem_luck = (gem_luck - 1) * 4 + 1 # base luck of 1, with 8x multiplier for LCs
        luck = (luck - 1) * lc_boost + 1 
        gem_luck = (gem_luck - 1) * lc_boost + 1


    # MoaKs
    if random.randint(1, moak_rarity_mult * 2**15) <= moak_luck:
        # one-of-a-kind
        # output["emote"] = random.choice([
        #                                     #values.holy_hell, 
        #                                     #values.horsey, 
        #                                     values.anarchy_chess,
        #                                     #values.anarchy,
        #                                     ])
        output["emote"] = values.anarchy_chess
        output["commentary"] = "That sure is pretty rare!"
        output["extra_profit"] = user_account.get("max_daily_rolls") * 10 # between 10 and 10,000 extra

    elif random.randint(1, 2**22) <= gem_luck:
        # gold gem
        output["emote"] = values.gem_gold
        output["commentary"] = "The fabled gold gem!"

    # 32768 -> green gem worth 2000
    elif random.randint(1, 2**19) <= gem_luck:
        # green gem
        output["emote"] = values.gem_green
        output["commentary"] = "Incredibly shiny!"

    # 16384 -> purple gem worth 1000
    elif random.randint(1, 2**18) <= gem_luck:
        # purple gem
        output["emote"] = values.gem_purple
        output["commentary"] = "So very shiny."

    # 8192 -> blue gem worth 500
    elif random.randint(1, 2**17) <= gem_luck:
        # blue gem
        output["emote"] = values.gem_blue
        output["commentary"] = "Very shiny."

    # 4096 -> red gem, worth 250
    elif random.randint(1, 2**16) <= gem_luck:
        # red gem
        output["emote"] = values.gem_red
        output["commentary"] = "Shiny."

    elif random.randint(1, 2**11) <= luck:
        #chess piece
        # user_chess_pieces = user_account.get_all_items_with_attribute_unrolled("chess_pieces")

        white_piece_chances = store.chess_piece_distribution_levels[ user_account.get("chess_piece_equalizer") ]

        if random.randint(1,100) <= white_piece_chances: # white pieces
            # unfound_white_pieces = utility.array_subtract(values.chess_pieces_white_biased, user_chess_pieces)
            # if len(unfound_white_pieces) > 0:
            #     awarded_piece = random.choice(unfound_white_pieces)
            #     #pprint.pprint(f"awarded white piece: {awarded_piece}, of choices: {str(unfound_white_pieces)}")
            # else:
            #     awarded_piece = random.choice(values.chess_pieces_white_biased)
                #print("all white pieces found, awarded random white piece")
            #output["emote"] = awarded_piece
            output["emote"] = random.choice(values.chess_pieces_white_biased)
            output["commentary"] = "Your Elo has been increased by 20 points."
        else: # black pieces
            # unfound_black_pieces = utility.array_subtract(values.chess_pieces_black_biased, user_chess_pieces)
            # if len(unfound_black_pieces) > 0:
            #     awarded_piece = random.choice(unfound_black_pieces)
            #     #pprint.pprint(f"awarded black piece: {awarded_piece}, of choices: {str(unfound_black_pieces)}")
            # else:
            #     awarded_piece = random.choice(values.chess_pieces_black_biased)
            #     #print("all black pieces found, awarded random black piece")
            # #output["emote"] = awarded_piece
            output["emote"] = random.choice(values.chess_pieces_black_biased)
            output["commentary"] = "Your Elo has been increased by 10 points."
        
    elif random.randint(1, 2**9) <= luck:
        #rare bread
        output["emote"]= random.choice(values.all_rare_breads)
        output["commentary"] = "Tasty!"
        
    elif random.randint(1, 2**7) <= luck:
        #special bread
        output["emote"] = random.choice(values.all_special_breads)
        output["commentary"] = "Tasty."
        
    else:
        #bread
        output["emote"] = values.normal_bread
        output["commentary"] = ""
        
    if "extra_profit" not in output:
        output["extra_profit"] = 0
    output["extra_profit"] += user_account.get_dough_boost_for_item(output["emote"])

    return output


def bread_roll_test_average(roll_luck, roll_count, iterations):
    total_profit = 0
    for i in range(iterations):
        total_profit += bread_roll(roll_luck, roll_count, include_moaks=True)["total_dough"]
    
    average = total_profit / iterations
    #print(f"For {roll_luck-1} LCs and {roll_count} daily rolls, average profit is {average}")
    return average

def bread_roll_test_suite(max_luck, max_rolls, iterations):
    max_rolls = max(max_rolls, 10)
    for luck in range(1,max_luck):
        print(f"\n{luck}, ", end = ' ')
        for rolls in range(10,max_rolls):
            print(f"{bread_roll_test_average(luck, rolls, iterations)}, ", end = ' ', flush = True)
    print()

def test_account():
    test_account = account.Bread_Account()

    # number of dailies to buy before LC .... anywhere from 0 to 50
    # are we making a tree? We might be.
    # it's basically a decision tree... we start with zero, roll a couple of times
    # each new decision is anywhere from 0 to 50 daily rolls before a LC


# okay so let's write some stuff out
# each roll is worth about 6.2 dough without moaks
# each LC is worth about .3 dough without moaks

# with moaks, each roll is worth about 6.4 dough
# and each LC is worth about .7 dough per roll

def summarize_roll(result):

    removals = []

    output = "\tSummary of results:\n"
    if "value" in result:
        output += f"Total gain: **{utility.smart_number(result['value'])} dough**\n"
        removals.append("value")

    if "gambit_shop_bonus" in result:
        output += f"Gambit shop bonus: {utility.smart_number(result['gambit_shop_bonus'])} dough\n"
        removals.append("gambit_shop_bonus")

    if "highest_roll" in result:
        output += f"The highest roll was {utility.smart_number(result['highest_roll'])}.\n"
        removals.append("highest_roll")

    if "natural_1" in result:
        output += f"Natural 1: {utility.smart_number((result['natural_1'])}\n"
        removals.append("natural_1")

    if "ten_breads" in result:
        output += f"Ten breads: {utility.smart_number(result['ten_breads'])}\n"
        removals.append("ten_breads")

    if ":bread:" in result:
        output += f"\t:bread:: {utility.smart_number(result[':bread:'])}\n"
        removals.append(":bread:")

    # if "special_bread" in result.keys() and "rare_bread" in result.keys():
    #     output += f"Special bread: {result['special_bread'] - result['rare_bread']}\n"
    #     removals.append("special_bread")
    if "special_bread" in result.keys():
        output += f"Special bread: {utility.smart_number(result['special_bread'])}\n"
        removals.append("special_bread")


    for key in result.keys():
        emote = values.get_emote(key)
        if emote is not None and ("special_bread" in emote.attributes):
            output += f"\t{key}: {utility.smart_number(result[key])}"
            removals.append(key)

    if "rare_bread" in result.keys():
        output += f"\nRare bread: {utility.smart_number(result['rare_bread'])}\n"
        removals.append("rare_bread")

    for key in result.keys():
        emote = values.get_emote(key)
        if emote is not None and ("rare_bread" in emote.attributes):
            output += f"\t{key}: {utility.smart_number(result[key])}"
            removals.append(key)

    if "chess_pieces" in result.keys():
        output += f"\nChess pieces: {utility.smart_number(result['chess_pieces'])}\n"
        removals.append("chess_pieces")

    for key in result.keys():
        emote = values.get_emote(key)
        if emote is not None and ("chess_pieces" in emote.attributes):
            output += f"\t{key}: {utility.smart_number(result[key])}"
            removals.append(key)

    if "shiny" in result.keys():
        output += f"\nShiny Items: {utility.smart_number(result['shiny'])}\n"
        removals.append("shiny")

    for key in result.keys():
        emote = values.get_emote(key)
        if emote is not None and ("shiny" in emote.attributes):
            output += f"\t{key}: {utility.smart_number(result[key])}"
            removals.append(key)

    if "many_of_a_kind" in result.keys():
        output += f"\nMany of a kind: {utility.smart_number(result['many_of_a_kind'])}\n"
        removals.append("many_of_a_kind")
        removals.append("one_of_a_kind")
        removals.append("unique")
    
    if values.anarchy_chess.text in result.keys():
        output += f"{values.anarchy_chess.text}: {utility.smart_number(result[values.anarchy_chess.text])}\n"
        removals.append(values.anarchy_chess.text)

    last_header = True
    for key in result.keys():
        if key not in ["commentary", "emote_text",  "roll_messages", "total_dough", "lifetime_dough", "value", "earned_dough", "individual_values"] + removals:
            if last_header:
                output += "\nExtra items:\n"
                last_header = False
            output += f"{key}: {utility.smart_number(result[key])}\n"
    # output += f"{roll['emote']} {roll['commentary']}"
    return output
