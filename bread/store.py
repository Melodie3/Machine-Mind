
import typing
import random 
from numpy import random as rand

import bread.account as account
import bread.values as values
import bread.utility as utility

# loaf converter
# 1 - 2/3 single loafs converted to special
# 2 - all single loaves converted to special
# 3 to 8 - all loaves below 2, 3, 4, 5 converted to special

# daily_rolls
# costs 2^amt, so 128 to start

# Decorative
# flowers


ascension_token_levels = [50, 150, 450, 1000]

daily_rolls_discount_prices = [128, 124, 120, 116, 112, 108, 104, 100]
loaf_converter_discount_prices = [256, 244, 232, 220, 208, 196, 184, 172]
chess_piece_distribution_levels = [25, 33, 42, 50]
moak_booster_multipliers = [1, 1.3, 1.7, 2.1, 2.8,3.7]
chessatron_shadow_booster_levels = [0, 5, 10, 15, 20]
shadow_gold_gem_luck_boost_levels = [0, 10, 20, 30, 40]

class Store_Item:
    name = "generic_item"
    display_name = "Generic Item" # did you just say "generic excuse"??

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 1000

    @classmethod
    def get_price_description(cls, user_account: account.Bread_Account) -> str:
        return f"{utility.smart_number(cls.cost(user_account))} dough"
    
    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "A description"

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return None

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name) + 1
        if cls.max_level(user_account) is None:
            return True
        else:
            if level > cls.max_level(user_account):
                return False
            else:
                return True

    @classmethod
    def is_affordable_for(cls, user_account: account.Bread_Account) -> bool:
        cost = cls.cost(user_account)
        if user_account.get_dough() >= cost:
            return True
        return False

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount:int = 1):
        level = user_account.get(cls.name) + 1

        # then we can purchase it

        # this must be a loop as certain items' prices aren't constant; you can't multiply
        # by amount here.
        for i in range(amount):
            user_account.increment("total_dough", -cls.cost(user_account))
            user_account.increment(cls.name, amount)

    @classmethod
    def get_cost_types(cls, user_account: account.Bread_Account, level: int = None):
        return ["total_dough"]
        
class Custom_price_item(Store_Item):
    name = "custom_price_item"
    display_name = "Custom Price Item"

    #required
    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name) 
        if level >= cls.max_level(user_account):
            return False
        return True

    #required
    @classmethod
    def get_price_description(cls, user_account: account.Bread_Account) -> str:
        # print(f"Price description called for level {user_account.get(cls.name)}")
        cost = cls.cost(user_account)
        output = ""
        for i in range(len(cost)):
            # for pair in cost:
            pair = cost[i]
            output += f"{pair[1]} {pair[0]}"
            if i != len(cost) - 1:
                output += " ,  "
        return output

    #required
    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "An item in the ascension shop"

    #required
    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        cost = cls.cost(user_account)

        for pair in cost:
            user_account.increment(pair[0], -pair[1])

        user_account.increment(cls.name, 1)
        return None

    #required
    @classmethod
    def is_affordable_for(cls, user_account: account.Bread_Account) -> bool:
        cost = cls.cost(user_account)
        for pair in cost:
            if user_account.get(pair[0]) < pair[1]:
                return False
        return True

    #optional
    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        costs = cls.get_costs()
        return len(costs) - 1

    #optional
    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name)
        costs = cls.get_costs()
        return costs[level + 1]

    #required for subclasses
    @classmethod
    def get_costs(cls):
        costs = [
            [],
            [(values.gem_red.text, 1), ("total_dough", 1000)],
        ]

    @classmethod
    def get_cost_types(cls, user_account: account.Bread_Account, level: int = None):
        if level is None: 
            level = user_account.get(cls.name)

        all_costs = cls.get_costs()
        level_costs = all_costs[level]

        retval = []

        for cost in level_costs:
            retval.append(cost[0]) # cost[0] is the type of item, cost[1] is the amount

        return retval

class Welcome_Packet(Store_Item):
    name = "welcome_packet"
    display_name = "Welcome Packet"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 0

    @classmethod
    def get_price_description(cls, user_account: account.Bread_Account) -> str:
        return "Free"

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        prestige_level = user_account.get_prestige_level()
        if prestige_level <= 0:
            return "Welcome to the bread game! This is a free packet of dough, to help you get started."
        else:
            return "Welcome to your ascension! This is a free packet of dough, to help you get started. It's a bit larger this time."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 1

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:

        if user_account.get("welcome_packet") < user_account.get_prestige_level() + 1:
            return True
        else:
            return False
        # lifetime_earned_dough = user_account.get("earned_dough") + user_account.get("lifetime_earned_dough")
        # if lifetime_earned_dough < 128:
        #     return True
        # else:
        #     return False

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):

        prestige_level = user_account.get_prestige_level()

        if prestige_level == 0:
            amount = random.randint(128, 256)
        elif prestige_level >= 1:
            amount = 1024 + random.randint(128, 256)

        amount = user_account.add_dough_intelligent(amount)
        # user_account.increment("total_dough", amount)
        # user_account.increment("lifetime_dough", amount)
        user_account.set("welcome_packet", prestige_level + 1)

        return f"Inside the packet was **{amount} dough**! Congratulations!"


class Daily_rolls(Store_Item):
    name = "max_daily_rolls"
    display_name = "Extra daily roll"

    @classmethod
    def cost(cls, user_account: account.Bread_Account, level: None) -> int:
        if level is None:
            level = user_account.get(cls.name) + 1
        naive_cost = 128 #(max(0, level-10) * 128) # cost will be 256, 512, 768, 1024, ...
        # first few levels are cheaper
        level_discount_card = user_account.get("max_daily_rolls_discount")
        adjusted_cost = daily_rolls_discount_prices[level_discount_card]
        if level < 10:
            return 0
        elif level == 11:
            return 32
        elif level == 12:
            return 64
        elif level == 13:
            return 96
        return adjusted_cost

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1

        output = f"Permanently increases the number of daily rolls you can make to {level}."
        if level <= 13:
            output += " Comes with an introductory discount for new players!"
            
        return output
    
    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 1000 + user_account.get_prestige_level() * 100
    
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        # find the max purchasable amount of the item.

        dough = user_account.get("total_dough")
        level = user_account.get(cls.name) + 1

        # price is not constant. a loop will be important here, but should be faster than looping the entire process.
        purchase = 0
        while 1:
            if dough >= cls.cost(user_account, level) or level > cls.max_level:
                purchase += 1
                dough -= cls.cost(user_account, level)
            else: break
            level += 1

        # which is sooner: the daily rolls limit, or the amount you can buy?
        # subtract the current amount of the item to get the amount purchasable, not the total amount possible.
        return min(user_account.get(cls.name) + level, cls.max_level) - user_account.get(cls.name)

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount: int = 1):
        super().do_purchase(user_account, amount=amount)
        level = user_account.get(cls.name)
        prestige_level = user_account.get_prestige_level()
        if prestige_level >= 1:
            token_text = values.ascension_token.text
            if level in ascension_token_levels:
                user_account.increment(token_text, 1)
                return f"In addition to buying a daily roll, you have acquired **1 {token_text}**! You now have **{user_account.get(token_text)} {token_text}**."


class Loaf_Converter(Store_Item):
    name = "loaf_converter"
    display_name = "Loaf Converter"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        discounted_cost = loaf_converter_discount_prices[user_account.get("loaf_converter_discount")]
        combined_cost =  level * discounted_cost
        return combined_cost

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1  
        description_mult = utility.write_number_of_times(level+1) # its effect starts at one extra
        return f"Each loaf is {description_mult} more likely to be something special, compared to baseline."
        if level == 1:
            return "Twice as many rolls of 1 will become special bread."
        if level == 2:
            return "All rolls of 1 will become a special bread"
        if level == 3:
            return "A roll of 2 or lower will become a special bread."
        if level == 4:
            return "A roll of 3 or lower will become a special bread."
        if level == 5:
            return "A roll of 4 or lower will become a special bread."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 69420
    
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        # find the max purchasable amount of the item.

        # thanks duck

        d = user_account.get("total_dough")
        n = user_account.get(cls.name)
        p = 256 - (user_account.get("loaf_converter_discount") * 12)

        # the Equation
        buyable_lcs = int(
        ((-1 * (((2 * p) * n) + p)) + (((((2 * p) * n) + p)**2 + ((8 * p) * d))**0.5)) // (2 * p))

        # which is sooner? max_level (lol) or the max amount you can buy?
        return min(n + buyable_lcs, cls.max_level())



class Dough_Multiplier(Store_Item):
    name = "dough_multiplier"
    display_name = "Dough Multiplier"

    # costs: similar 30ish percent growth?       250    325   400    500   625   750    875   1000
    # mults: 30ish percent increase each time    1.5x   2x    2.75x  3.5x  4.5x  5.75x  7.5x  10x
    # daily dough:                               75     100   150    175   225   300    415   550
    # potential price                      250   375    500   750    875   1125  1500   1875  2250

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        costs = [250, 375, 500, 750, 875, 1125, 1500, 1875, 2250]

        return costs[level-1]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        description_mult = utility.write_number_of_times(level+1)
        return f"Each roll yields {description_mult} as much dough, compared to baseline."

class Embiggener(Store_Item):
    name = "embiggener"
    display_name = "Embiggener"

    # this will multiply the profit values of special breads, but not regular breads

class Multiroller(Store_Item):
    name = "multiroller"
    display_name = "Multiroller"

    # this item rolls bread multiple times for each command sent

    @classmethod
    def cost(cls, user_account: account.Bread_Account, level:int = None) -> int:
        if level is not None:
            level = user_account.get(cls.name) + 1

        if level == 1:
            return 128
        else:
            return 256
            #naive_cost = (max(0, level-1) * 256)
        #return naive_cost

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        actual_mult = 2 ** (level)
        description_mult = utility.write_number_of_times(actual_mult)
        return f"Every $bread command you send will automatically roll bread {description_mult}. Every additional level rolls twice as many as the last.\nThis is a quality of life item and does not affect the amount of dough you earn."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        prestige_level = user_account.get_prestige_level()
        if prestige_level == 0:
            return 10
        elif prestige_level < 10:
            return 11
        else:
            return 12
        
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        # find the max purchasable amount of the item.

        dough = user_account.get("total_dough")
        level = user_account.get(cls.name) + 1

        # same as before... price is not constant so loop
        purchase = 0
        while level <= cls.max_level(user_account) and dough >= cls.cost(user_account, level):

            purchase += 1
            level += 1
            dough -= cls.cost(user_account, level)
            

        # which is sooner: the multiroller limit, or the amount you can buy?
        # return min(user_account.get(cls.name) + level, cls.max_level) - user_account.get(cls.name)
        return purchase

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name) + 1
        max_level = cls.max_level(user_account)
        compound_roller_level = user_account.get("compound_roller")
        
        if user_account.get("max_daily_rolls") > 23 and level <= max_level:
            if level >= 5 and level <= 10:
                # we require a certain level of compound roller to avoid spam
                if compound_roller_level >= level - 5:
                    return True
                else:
                    return False
            else: # level 1-4 and 11+
                return True 
        else:
            return False

class Compound_Roller(Store_Item):

    name = "compound_roller"
    display_name = "Compound Roller"

    @classmethod
    def cost(cls, user_account: account.Bread_Account, level:int = None) -> int:
        if level is not None:
            level = user_account.get(cls.name) + 1
        return 128

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        description_mult = utility.write_count(2**level, "roll")
        return f"Every bread multiroll message will have up to {description_mult} contained within. The total number of rolls is still decided by the multirollers you own."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 5
    
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        # find the max purchasable amount of the item.

        dough = user_account.get("total_dough")
        level = user_account.get(cls.name) + 1

        purchase = 0
        while dough >= cls.cost(user_account, level) and level <= cls.max_level(user_account):
            
            purchase += 1
            dough -= cls.cost(user_account, level)
            level += 1

        # which is sooner: the compound roller limit, or the amount you can buy?
        # return min(user_account.get(cls.name) + level, cls.max_level) - user_account.get(cls.name)
        return purchase

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name) + 1
        multiroller_count = user_account.get("multiroller")
        if level <= multiroller_count and level <= 5:
            return True
        else:
            return False
        #return super().can_be_purchased(user_account)

    


class Random_Chess_Piece(Store_Item):
    name = "random_chess_piece"
    display_name = "Random Chess Piece"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        omega_level = user_account.get(values.omega_chessatron.text)
        affecting_shadowmegas = user_account.get_shadowmega_boost_count()
        # shadowmega_boost_level = user_account.get("chessatron_shadow_boost")
        # max_shadowmegas = chessatron_shadow_booster_levels[shadowmega_boost_level]
        # shadowmega_count = user_account.get(values.shadowmega_chessatron.text)
        # affecting_shadowmegas = min(shadowmega_count, max_shadowmegas)
        return 350 + (omega_level * 50) + (affecting_shadowmegas * 20)

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "Purchase a random chess piece which you do not currently have."
    
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        # find the max purchasable amount of the item.

        dough = user_account.get("total_dough")

        return dough // cls.cost(user_account)

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount: int = 1):
        # subtract cost
        user_account.increment("total_dough", -cls.cost(user_account) * amount)

        original_amount = amount

        # increase count
        #user_account.increment("chess_pieces", 1)
        full_chess_set = values.chess_pieces_black_biased + values.chess_pieces_white_biased
        user_chess_pieces = user_account.get_all_items_with_attribute_unrolled("chess_pieces")
        unfound_pieces = utility.array_subtract(full_chess_set, user_chess_pieces)

        purchased_pieces = dict()
        for chess_piece in values.all_chess_pieces:
            purchased_pieces[chess_piece.text] = 0

        
        out_str = ''

        # first we fill in any missing pieces
        while len(unfound_pieces) > 0 and amount > 0:
            
            # if we're buying more than we need, we just buy all the missing pieces
            if amount >= len(unfound_pieces):
                unfound_pieces = utility.array_subtract(full_chess_set, user_chess_pieces)

                amount -= len(unfound_pieces)
                for piece in unfound_pieces:
                    user_account.add_item_attributes(piece)
                    purchased_pieces[piece.text] += 1
                unfound_pieces = []

            # else we buy the pieces we need one at a time
            else:
                piece = random.choice(unfound_pieces)
                user_account.add_item_attributes(piece)
                unfound_pieces.remove(piece)
                purchased_pieces[piece.text] += 1
                amount -= 1

                if original_amount == 1:
                    out_str = f'Congratulations! You have purchased a {piece.text}!'



        while amount > 0:
            # if you have all the chess pieces, you get a random chess piece.
            piece = random.choice(full_chess_set)
            user_account.add_item_attributes(piece)
            purchased_pieces[piece.text] += 1
            amount -= 1

            if original_amount == 1:
                out_str = f'Congratulations! You have purchased a {piece.text}!'

        if original_amount > 1:
            out_str = "Congratulations! You have purchased the following chess pieces:\n"
            for piece in purchased_pieces:
                if purchased_pieces[piece] > 0:
                    out_str += f'{piece}: {purchased_pieces[piece]} \n'

        # # then add random chess piece
        # if (random.randint(1, 4) == 1):
        #     #user_account.increment(random.choice(values.chess_pieces_white_biased).text)
        #     item = random.choice(values.chess_pieces_white_biased)
        #     user_account.add_item_attributes(item)
        # else:
        #     #user_account.increment(random.choice(values.chess_pieces_black_biased).text)
        #     item = random.choice(values.chess_pieces_black_biased)
        #     user_account.add_item_attributes(item)
        
        return out_str

class Random_Special_Bread(Store_Item):
    name = "random_special_bread"
    display_name = "Random Special Bread"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 50

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "Purchase a random special bread."

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        # subtract cost
        user_account.increment("total_dough", -cls.cost(user_account))

        purchased_item = random.choice(values.all_special_breads)
        user_account.add_item_attributes(purchased_item)

        return f"Congratulations! You got a {purchased_item.text}."

        # increase count
        # user_account.increment("special_bread", 1)

        # then add random special bread
        # user_account.increment(random.choice(values.all_special_breads).text)

class Special_Bread_Pack(Store_Item):
    name = "special_bread_pack"
    display_name = "Special Bread Pack"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 350

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "A pack of 100 random special and rare breads."

    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        dough = user_account.get("total_dough")

        return dough // 350

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount = 1):
        # subtract cost
        # can just do * amount bc the price doesn't change.
        user_account.increment("total_dough", -cls.cost(user_account) * amount)

        rng = rand.default_rng()
        count = 100 * amount
        bread_distribution = values.all_special_breads * 3 + values.all_rare_breads

        # this might allow you to see special bread pack changes in full when buying multiple?

        # bought_bread = rng.choice(bread_distribution, count)
        # for item in set(bread_distribution):
            #  user_account.add_item_attributes(item, amount=bought_bread.count(item))

        # output = f"Congratulations! You got the following {count} special breads:\n"
        # for item in set(bread_distribution):
        #     item_text = item.text
        #     if item_text in bought_bread:
        #         #output += f"{all_purchased_items[item_text]} {item_text}\n"
        #         output += f"{item_text} : +{bought_bread.count(item)}, -> {user_account.get(item_text)}\n"

        bought_bread_dict = dict()
        for bread in bread_distribution:
            bought_bread_dict[bread.text] = 0
        for i in range(count):
            bread = random.choice(bread_distribution)
            bought_bread_dict[bread.text] += 1

        # add the breads to our account
        for bread_type in values.all_special_breads+values.all_rare_breads:
            user_account.add_item_attributes(bread_type, amount=bought_bread_dict[bread_type.text])

        output = ""
        for item_text in bought_bread_dict.keys():
            output += f"{item_text} : +{bought_bread_dict[item_text]}, -> {user_account.get(item_text)}\n"
        
        
            
        return output

class Extra_Gamble(Store_Item):
    name = "extra_gamble"
    display_name = "Extra Gamble"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 25

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "Five extra rolls of the dice, just this once."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return None
    
    @classmethod
    def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
        dough = user_account.get("total_dough")

        return dough // 25
    
    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount = 1):
        # subtract cost
        user_account.increment("total_dough", -cls.cost(user_account) * amount)

        # reduce that gamble by 1
        # user_account.increment("daily_gambles", -5)
        user_account.increment("max_gambles", 5 * amount)

        return "Done.\n\nMay the odds be ever in your favor."

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        lifetime_gambles = user_account.get("lifetime_gambles")
        if lifetime_gambles < 10:
            return False
        return True

class Roll_Summarizer(Store_Item):
    name = "roll_summarizer"
    display_name = "Roll Summarizer"

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 1

    @classmethod
    def get_price_description(cls, user_account: account.Bread_Account) -> str:
        return "1 " + values.gem_red.text

    @classmethod
    def is_affordable_for(cls, user_account: account.Bread_Account) -> bool:
        
        if user_account.get(values.gem_red.text) >= 1:
            return True
        else:
            return False

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        if user_account.get("roll_summarizer") == 0 and user_account.get("compound_roller") >= 2:
            return True

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "Creates a summary for each multiroll, which includes the dough gained and stats for each kind of bread found in it."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 1
    
    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        if cls.is_affordable_for(user_account):
            # subtract cost
            user_account.increment(values.gem_red.text, -1)

            # increase count
            user_account.increment("roll_summarizer", 1)

            return "You have purchased the roll summarizer!"

class Black_Hole_Technology(Custom_price_item):
    name = "black_hole"
    display_name = "Black Hole Technology"

    @classmethod
    def get_costs(cls):
        return [
            [],
            [(values.gem_purple.text, 2)],
        ]
    
    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "Allows you to condense all rolls into one message."
    
    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get("black_hole")
        if level > 0:
            return False
        # we need to have: the roll summarizer, and 5 multirollers
        if user_account.get("roll_summarizer") == 0:
            return False
        if user_account.get("multiroller") < 5:
            return False
        return True
    
    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        # subtract cost
        user_account.increment(values.gem_purple.text, -2)

        # increase count
        user_account.set("black_hole", 2)

        return "You have purchased black hole technology! Activate or deactivate it with the command `$bread black_hole`."

    @classmethod
    def get_cost_types(cls, user_account: account.Bread_Account, level: int = None):
        return [values.gem_purple.text]


class Bling(Custom_price_item):
    name = "bling"
    display_name = "Bling"

    costs = [(),
             (values.gem_red.text, 3),
             (values.gem_blue.text, 3),
             (values.gem_purple.text, 3),
             (values.gem_green.text, 3),
             (values.gem_gold.text, 3),
             (values.anarchy_chess.text, 3)]

    @classmethod
    def get_costs(cls):
        # I know this is duplicate but it means I don't need to replace some of the lower down code
        return [[],
                [(values.gem_red.text, 3)],
                [(values.gem_blue.text, 3)],
                [(values.gem_purple.text, 3)],
                [(values.gem_green.text, 3)],
                [(values.gem_gold.text, 3)],
                [(values.anarchy_chess.text, 3)]]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get("bling") + 1
        return f"A decorative {cls.costs[level][0]} for your stats and leaderboard pages. Purely cosmetic."

    # @classmethod
    # def get_price_description(cls, user_account: account.Bread_Account) -> str:
    #     level = user_account.get("bling") + 1

    #     return f"{cls.costs[level][1]} {cls.costs[level][0]}"

    # @classmethod
    # def is_affordable_for(cls, user_account: account.Bread_Account) -> bool:
    #     level = user_account.get("bling") + 1
    #     if user_account.get(cls.costs[level][0]) >= cls.costs[level][1]:
    #         return True
    #     else:
    #         return False

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name) + 1
        shiny_level = user_account.get("shiny")
        if shiny_level <= 0:
            return False # we only show it if you have a chance of affording it
        else:
            if level > cls.max_level(user_account):
                return False
            else:
                return True
            
    # @classmethod
    # def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
    #     return len(cls.costs) - 1
    
    #  removed because it caused an error
    # @classmethod
    # def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
    #     level = user_account.get(cls.name)

    #     # only check the ones past your current level
    #     for cost in cls.costs[level:]:
    #         if user_account.get(cost[0]) < cost[1]:
    #             break
    #     return cls.costs.index(cost) + level - 1

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account, amount: int = 1):
        level = user_account.get("bling") + 1

        if cls.is_affordable_for(user_account):
            for i in range(amount):
                user_account.increment(cls.costs[level + i][0], -cls.costs[level + i][1])

            user_account.increment("bling", amount)

            return f"You have purchased a {', '.join([cls.costs[level + x][0] for x in range(amount)])} bling!"
        else:
            return f"You do not have enough {cls.costs[level][0]} to purchase a bling level {level}!"

class LC_booster(Custom_price_item):
    name = "LC_booster"
    display_name = "Recipe Refinement"

    @classmethod
    def get_costs(cls):
        return [
            [],
            [(values.gem_gold.text, 1)],
            [(values.gem_gold.text, 10)],
            [(values.gem_gold.text, 100)],
            [(values.gem_gold.text, 1000)],
        ]
    
    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        boost = 2 ** level
        return f"Massively increases the power of your Loaf Converters. They will be {boost}x more effective for creating everything other than MoaKs."

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        level = user_account.get(cls.name)
        if level >= cls.max_level(user_account):
            return False
        daily_roll_count = user_account.get("max_daily_rolls")
        max_daily_roll_count = Daily_rolls.max_level(user_account)
        if daily_roll_count >= max_daily_roll_count:
            return True
        else:
            return False
        
    # @classmethod
    # def find_max_purchasable_count(cls, user_account: account.Bread_Account) -> int:
    #     level = user_account.get(cls.name) + 1
    #     glods = user_account.get(values.gem_gold)
    #     # gets the amounts of glods needed for each level. this currently gets (1,10,100,1000)[level:]
    #     glods_price = [*zip( *cls.get_costs()[level:] )][1]

    #     for i in range(len(cls.get_costs()[level:])):
    #         if glods < sum(glods_price[:i+1]):
    #             return i
    #     return len(cls.get_costs()[1:]) - level

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        super().do_purchase(user_account)
        level = user_account.get(cls.name)
        return f"You are now at Recipe Refinement level {level}!"




class Test_Strategy_Item(Custom_price_item):
    name = "test_strategy_item"
    display_name = "Test Strategy Item"

    @classmethod
    def get_costs(cls):
        return [
            [],
            [(values.chessatron.text, 10), (values.shadowmega_chessatron.text, 1)],

        ]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "This is a test item. It does nothing."
    
    

normal_store_items = [Welcome_Packet, Daily_rolls, Loaf_Converter, Multiroller, Compound_Roller, Extra_Gamble, Random_Chess_Piece, Special_Bread_Pack, Roll_Summarizer, Black_Hole_Technology, Bling, LC_booster, ]

##############################################################################################################
##############################################################################################################
##############################################################################################################

# todo: make a prestige store base class
# add high roller table, max level 5

class Prestige_Store_Item(Store_Item):
    name = "prestige_store_item"
    display_name = "Prestige Store Item"

    #required
    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        #return super().can_be_purchased(user_account)
        if user_account.get_prestige_level() >= 1:
            level = user_account.get(cls.name) + 1
            if level <= cls.max_level(user_account):
                return True
        return False

    #required
    @classmethod
    def get_price_description(cls, user_account: account.Bread_Account) -> str:
        cost = cls.cost(user_account)
        return f"{cost} {values.ascension_token.text}"

    #required
    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return "An item in the ascension shop"

    #required
    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        cost = cls.cost(user_account)
        user_account.increment(values.ascension_token.text, -cost)
        user_account.increment(cls.name, 1)
        return None

    #required
    @classmethod
    def is_affordable_for(cls, user_account: account.Bread_Account) -> bool:
        cost = cls.cost(user_account)
        if user_account.get(values.ascension_token.text) >= cost:
            return True

    #optional
    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 0

    #optional
    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        return 0
    
    @classmethod
    def get_cost_types(cls, user_account: account.Bread_Account, level: int = None):
        return [values.ascension_token.text]


class High_Roller_Table(Prestige_Store_Item):
    name = "gamble_level"
    display_name = "High Roller Table"

    gamble_levels = [50, 500, 1500, 5000, 10000, 100000, 10000000]

    costs = [0, 1, 1, 1, 1, 1, 1]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        level = user_account.get(cls.name) + 1
        return 6

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"Join the high roller table. Increases your maximum bid while gambling to {cls.gamble_levels[level]}."

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        super().do_purchase(user_account)
        return f"You bought your way into the high roller table. Congratulations!"

class Daily_Discount_Card(Prestige_Store_Item):
    name = "max_daily_rolls_discount"
    display_name = "Daily Discount Card"

    costs = [0, 1, 1, 1, 2, 2, 2, 3]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        new_price = daily_rolls_discount_prices[level]
        return f"Reduces the cost of a daily roll by 4, to {new_price}."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 7

class Self_Converting_Yeast(Prestige_Store_Item):
    name = "loaf_converter_discount"
    display_name = "Self Converting Yeast"

    costs = [0, 1, 1, 1, 2, 2, 2, 3]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"Reduces the cost of each loaf converter level by 12, to {loaf_converter_discount_prices[level]}."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 7

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        super().do_purchase(user_account)
        return f"You have purchased some self converting yeast, from a nice capybara in a trench coat and sunglasses."

class Chess_Piece_Equalizer(Prestige_Store_Item):
    name = "chess_piece_equalizer"
    display_name = "Chess Piece Equalizer"

    costs = [0, 1, 2, 3]
    

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"Every Chess piece will have an increased chance of being white, to {chess_piece_distribution_levels[level]}%."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 3

    

class MoaK_Booster(Prestige_Store_Item):
    name = "moak_booster"
    display_name = "MoaK Booster"

    costs = [0, 2, 2, 3, 3, 4]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"Increases the chances of finding a MoaK by 30%, to {round(moak_booster_multipliers[level]*100)}% of base."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return 5

class Chessatron_Contraption(Prestige_Store_Item):
    name = "chessatron_shadow_boost"
    display_name = "Chessatron Contraption"

    costs = [0, 1, 1, 2, 2]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"Allows you to gain a benefit of 100 extra dough on each chessatron you find, for each shadowmega chessatron you own. Works for up to {chessatron_shadow_booster_levels[level]} shadowmega chessatrons."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return len(cls.costs) - 1

class Ethereal_Shine(Prestige_Store_Item):
    name = "shadow_gold_gem_luck_boost"
    display_name = "Ethereal Shine"

    costs = [0, 1, 1, 2, 2]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        max_boost_count = shadow_gold_gem_luck_boost_levels[level]
        return f"Allows your shadow gold gems to help you find new gems. Up to {max_boost_count} shadow gold gems will be counted as 1 extra LC each, for the purposes of searching for gems specifically. This synergizes with Recipe Refinement."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return len(cls.costs) - 1

class First_Catch(Prestige_Store_Item):
    name = "first_catch_level"
    display_name = "First Catch of the Day"

    costs = [0, 1, 1, 2, 2, 3]

    @classmethod
    def cost(cls, user_account: account.Bread_Account) -> int:
        level = user_account.get(cls.name) + 1
        return cls.costs[level]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        return f"The first {utility.write_count(level, 'special item')} you find each day will be worth 4x the original value."

    @classmethod
    def max_level(cls, user_account: account.Bread_Account = None) -> typing.Optional[int]:
        return len(cls.costs) - 1

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        super().do_purchase(user_account)
        user_account.increment("first_catch_remaining", 1)
        return f"Congratulations! You unlocked a level of First Catch of the Day."

prestige_store_items = [Daily_Discount_Card, Self_Converting_Yeast, MoaK_Booster, Chess_Piece_Equalizer, High_Roller_Table, Chessatron_Contraption, Ethereal_Shine, First_Catch]

#############################################################################################################
#############################################################################################################
#############################################################################################################

#gambit shop items

# first we'll make the item for unlocking the store itself
class Gambit_Shop_Level(Custom_price_item):
    name = "gambit_shop_level"
    display_name = "Gambit Shop Level"

    @classmethod
    def get_costs(cls):
        return [
            [],
            [(values.doughnut.text, 10), (values.bagel.text, 10), (values.waffle.text, 10)],
            [(values.gem_red.text, 3)],
            [(values.gem_blue.text, 3)],
            [(values.gem_purple.text, 3)],
        ]

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        level = user_account.get(cls.name) + 1
        if level == 1:
            return "Unlocks the Gambit Shop."
        else:
            return "Unlocks the next level of the Gambit Shop."

    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        super().do_purchase(user_account)
        return f"Congratulations! You unlocked a level of the Gambit Shop."

#this is the generic item we purchase in the strategy shop
class Gambit_shop_Item(Custom_price_item):
    name = "gambit_shop_item"
    display_name = "Gambit Shop Item"
    level_required = 1
    boost_item = values.normal_bread
    boost_amount = 1
    raw_cost = [(values.normal_bread.text, 1000)]

    @classmethod
    def get_costs(cls):
        return [
            [],
            cls.raw_cost
        ]

    @classmethod
    def can_be_purchased(cls, user_account: account.Bread_Account) -> bool:
        
        if user_account.get("gambit_shop_level") >= cls.level_required:
            if user_account.get_dough_boost_for_item(cls.boost_item) < cls.boost_amount:
                return True
        return False


    @classmethod
    def do_purchase(cls, user_account: account.Bread_Account):
        cost = cls.cost(user_account)

        for pair in cost:
            user_account.increment(pair[0], -pair[1])

        user_account.set_dough_boost_for_item(cls.boost_item, cls.boost_amount)

        return f"Congratulations! You purchased the {cls.display_name}."

    @classmethod
    def description(cls, user_account: account.Bread_Account) -> str:
        return f"Boosts the dough you gain from a {cls.boost_item.text} by {cls.boost_amount}."
    
    @classmethod
    def get_cost_types(cls, user_account: account.Bread_Account, level: int = None):
        retval = []

        for cost in cls.raw_cost:
            retval.append(cost[0]) # cost[0] is the type of item, cost[1] is the amount

        return retval

class Gambit_Shop_Flatbread(Gambit_shop_Item):
    name = "gambit_shop_flatbread"
    display_name = "Rolling Pin"
    level_required = 1
    boost_item = values.flatbread
    boost_amount = 2
    raw_cost = [(values.flatbread.text, 20),
                (values.stuffed_flatbread.text, 20),
                (values.sandwich.text, 20),
                (values.french_bread.text, 20),
                (values.croissant.text, 20),]

class Gambit_Shop_Stuffed_Flatbread(Gambit_shop_Item):
    name = "gambit_shop_stuffed_flatbread"
    display_name = "Fresh Falafel"
    level_required = 1
    boost_item = values.stuffed_flatbread
    boost_amount = 2
    raw_cost = [(values.flatbread.text, 40),
                (values.stuffed_flatbread.text, 40),
                (values.sandwich.text, 40),
                (values.french_bread.text, 40),
                (values.croissant.text, 40),]

class Gambit_Shop_Sandwich(Gambit_shop_Item):
    name = "gambit_shop_sandwich"
    display_name = "BLT"
    level_required = 1
    boost_item = values.sandwich
    boost_amount = 2
    raw_cost = [(values.flatbread.text, 80),
                (values.stuffed_flatbread.text, 80),
                (values.sandwich.text, 80),
                (values.french_bread.text, 80),
                (values.croissant.text, 80),]

class Gambit_Shop_French_Bread(Gambit_shop_Item):
    name = "gambit_shop_french_bread"
    display_name = "Brie"
    level_required = 1
    boost_item = values.french_bread
    boost_amount = 2
    raw_cost = [(values.flatbread.text, 160),
                (values.stuffed_flatbread.text, 160),
                (values.sandwich.text, 160),
                (values.french_bread.text, 160),
                (values.croissant.text, 160),]

class Gambit_Shop_Croissant(Gambit_shop_Item):
    name = "gambit_shop_croissant"
    display_name = "More Butter"
    level_required = 1
    boost_item = values.croissant
    boost_amount = 2
    raw_cost = [(values.flatbread.text, 320),
                (values.stuffed_flatbread.text, 320),
                (values.sandwich.text, 320),
                (values.french_bread.text, 320),
                (values.croissant.text, 320),]

class Gambit_Shop_Bagel(Gambit_shop_Item):
    name = "gambit_shop_bagel"
    display_name = "Cream Cheese"
    level_required = 1
    boost_item = values.bagel
    boost_amount = 4
    raw_cost = [(values.bagel.text, 200),
                (values.doughnut.text, 200),
                (values.waffle.text, 200),]
            
class Gambit_Shop_Doughnut(Gambit_shop_Item):
    name = "gambit_shop_doughnut"
    display_name = "Jelly Filling"
    level_required = 1
    boost_item = values.doughnut
    boost_amount = 4
    raw_cost = [(values.bagel.text, 400),
                (values.doughnut.text, 400),
                (values.waffle.text, 400),]

class Gambit_Shop_Waffle(Gambit_shop_Item):
    name = "gambit_shop_waffle"
    display_name = "Maple Syrup"
    level_required = 1
    boost_item = values.waffle
    boost_amount = 4
    raw_cost = [(values.bagel.text, 800),
                (values.doughnut.text, 800),
                (values.waffle.text, 800),]

##########################################################################################

# all_chess_pieces = [black_king, black_queen, black_knight, black_bishop, black_rook, black_pawn, white_pawn, white_rook, white_bishop, white_knight, white_queen, white_king]

class Gambit_Shop_Black_Pawn(Gambit_shop_Item):
    name = "gambit_shop_black_ppawn"
    display_name = "e5"
    level_required = 2
    boost_item = values.black_pawn
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.gem_red.text, 1)]

class Gambit_Shop_Black_Knight(Gambit_shop_Item):
    name = "gambit_shop_black_knight"
    display_name = "King's Indian Defense"
    level_required = 2
    boost_item = values.black_knight
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.black_knight.text, 10), (values.gem_red.text, 1)]

class Gambit_Shop_Black_Bishop(Gambit_shop_Item):
    name = "gambit_shop_black_bishop"
    display_name = "Classical Defense"
    level_required = 2
    boost_item = values.black_bishop
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.black_bishop.text, 10), (values.gem_red.text, 1)]

class Gambit_Shop_Black_Rook(Gambit_shop_Item):
    name = "gambit_shop_black_rook"
    display_name = "0-0"
    level_required = 2
    boost_item = values.black_rook
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.black_rook.text, 10), (values.gem_red.text, 1)]

class Gambit_Shop_Black_Queen(Gambit_shop_Item):
    name = "gambit_shop_black_queen"
    display_name = "Botez Gambit"
    level_required = 2
    boost_item = values.black_queen
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.black_queen.text, 10), (values.gem_red.text, 1)]

class Gambit_Shop_Black_King(Gambit_shop_Item):
    name = "gambit_shop_black_king"
    display_name = "Bongcloud"
    level_required = 2
    boost_item = values.black_king
    boost_amount = 20
    raw_cost = [(values.black_pawn.text, 25), (values.black_king.text, 10), (values.gem_red.text, 1)]


##########################################################################################

class Gambit_Shop_White_Pawn(Gambit_shop_Item):
    name = "gambit_shop_white_ppawn"
    display_name = "e4"
    level_required = 3
    boost_item = values.white_pawn
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.gem_blue.text, 1)]

class Gambit_Shop_White_Knight(Gambit_shop_Item):
    name = "gambit_shop_white_knight"
    display_name = "Vienna Game"
    level_required = 3
    boost_item = values.white_knight
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.white_knight.text, 10), (values.gem_blue.text, 1)]

class Gambit_Shop_White_Bishop(Gambit_shop_Item):
    name = "gambit_shop_white_bishop"
    display_name = "King's Fianchetto Opening"
    level_required = 3
    boost_item = values.white_bishop
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.white_bishop.text, 10), (values.gem_blue.text, 1)]

class Gambit_Shop_White_Rook(Gambit_shop_Item):
    name = "gambit_shop_white_rook"
    display_name = "Ra4"
    level_required = 3
    boost_item = values.white_rook
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.white_rook.text, 10), (values.gem_blue.text, 1)]

class Gambit_Shop_White_Queen(Gambit_shop_Item):
    name = "gambit_shop_white_queen"
    display_name = "Botez Gambit Accepted"
    level_required = 3
    boost_item = values.white_queen
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.white_queen.text, 10), (values.gem_blue.text, 1)]

class Gambit_Shop_White_King(Gambit_shop_Item):
    name = "gambit_shop_white_king"
    display_name = "Double Bongcloud"
    level_required = 3
    boost_item = values.white_king
    boost_amount = 40
    raw_cost = [(values.white_pawn.text, 25), (values.white_king.text, 10), (values.gem_blue.text, 1)]

class Gambit_Shop_Gem_Red(Gambit_shop_Item):
    name = "gambit_shop_gem_red"
    display_name = "Refined Ruby"
    level_required = 4
    boost_item = values.gem_red
    boost_amount = 150
    raw_cost = [(values.gem_red.text, 10), (values.gem_blue.text, 5)]

class Gambit_Shop_Gem_Blue(Gambit_shop_Item):
    name = "gambit_shop_gem_blue"
    display_name = "Sapphire Ring"
    level_required = 4
    boost_item = values.gem_blue
    boost_amount = 250
    raw_cost = [(values.gem_red.text, 20), (values.gem_blue.text, 10), (values.gem_purple.text, 5)]

class Gambit_Shop_Gem_Purple(Gambit_shop_Item):
    name = "gambit_shop_gem_purple"
    display_name = "Amethyst Amulet"
    level_required = 4
    boost_item = values.gem_purple
    boost_amount = 500
    raw_cost = [(values.gem_red.text, 40), (values.gem_blue.text, 20), (values.gem_purple.text, 10), (values.gem_green.text, 5)]

class Gambit_Shop_Gem_Green(Gambit_shop_Item):
    name = "gambit_shop_gem_green"
    display_name = "Emerald Necklace"
    level_required = 4
    boost_item = values.gem_green
    boost_amount = 750
    raw_cost = [(values.gem_red.text, 80), (values.gem_blue.text, 40), (values.gem_purple.text, 20), (values.gem_green.text, 10), (values.gem_gold.text, 5)]

class Gambit_Shop_Gem_Gold(Gambit_shop_Item):
    name = "gambit_shop_gem_gold"
    display_name = "Gold Ring"
    level_required = 4
    boost_item = values.gem_gold
    boost_amount = 5000
    raw_cost = [(values.gem_red.text, 160), (values.gem_blue.text, 80), (values.gem_purple.text, 40), (values.gem_green.text, 20), (values.gem_gold.text, 10)]

gambit_shop_items = [Gambit_Shop_Level, Gambit_Shop_Flatbread, Gambit_Shop_Stuffed_Flatbread, Gambit_Shop_Sandwich, Gambit_Shop_French_Bread, Gambit_Shop_Croissant, 
                        Gambit_Shop_Bagel, Gambit_Shop_Doughnut, Gambit_Shop_Waffle,
                        Gambit_Shop_Black_Pawn, Gambit_Shop_Black_Knight, Gambit_Shop_Black_Bishop, Gambit_Shop_Black_Rook, Gambit_Shop_Black_Queen, Gambit_Shop_Black_King,
                        Gambit_Shop_White_Pawn, Gambit_Shop_White_Knight, Gambit_Shop_White_Bishop, Gambit_Shop_White_Rook, Gambit_Shop_White_Queen, Gambit_Shop_White_King,
                        Gambit_Shop_Gem_Red, Gambit_Shop_Gem_Blue, Gambit_Shop_Gem_Purple, Gambit_Shop_Gem_Green, Gambit_Shop_Gem_Gold]

all_store_items = prestige_store_items + normal_store_items + gambit_shop_items