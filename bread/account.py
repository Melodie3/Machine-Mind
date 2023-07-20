#bread account

import typing 

from bread.values import Emote
import bread.utility as utility
import bread.values as values
# import bread.store as store
import bread_cog
bread_cog_ref = None


class Bread_Account:


    user_id = None

    values = dict()
    garden = None

    items = None
    achievements = None
    logistics = None

    default_values = {
        "total_dough" : 0,
        "lifetime_dough" : 0,
        "highest_roll" : 0,
        "max_daily_rolls" : 10,
        "allowed" : True,
        "max_games" : 20,
        "max_gamble_amount" : 50,
        "username": "Unknown",
        "prestige_level" : 0,
        "max_gambles" : 20,
        "auto_chessatron" : True,
        "spellcheck" : False,
        "black_hole" : 0,
        "gifts_disabled" : False,
    }


    def __init__(self, user_id):
        self.user_id = user_id

    def reset_to_default(self):
        username = self.get("username")
        display_name = self.get("display_name")
        self.values = {
            "total_dough" : 0,
            "earned_dough" : 0,
            "max_daily_rolls" : 10,
            "daily_rolls" : 0,
            "username": username,
            "display_name": display_name,
        }

    def daily_reset(self):
        self.set("daily_rolls", 0)
        self.set("daily_gambles", 0)
        self.set("max_gambles", 20)
        if self.has ("daily_gifts"):
            self.set("daily_gifts", 0)
        if self.has ("first_catch_level"):
            self.set("first_catch_remaining", self.get("first_catch_level"))

    def increase_prestige_level(self):

        self.increment("prestige_level", 1)
        self.increment(values.ascension_token.text, 1)

        self.set("max_daily_rolls", 10)

        self.increment("lifetime_portfolio_value", self.get_portfolio_value() + self.get("investment_profit"))
        

        emotes_to_remove = []
        emotes_to_remove.extend(self.get_all_items_with_attribute("chess_pieces"))
        emotes_to_remove.extend(self.get_all_items_with_attribute("special_bread"))
        emotes_to_remove.extend(self.get_all_items_with_attribute("rare_bread"))
        emotes_to_remove.extend(self.get_all_items_with_attribute("shiny"))
        emotes_to_remove.extend(self.get_all_items_with_attribute("stonks"))
        emotes_to_remove.append(values.chessatron)
        emotes_to_remove.append(values.omega_chessatron)
        emotes_to_remove.append(values.normal_bread)
        emotes_to_remove.append(values.anarchy_chess)
        # we're keeping OoaKs

        entries_to_remove = [   "total_dough",
                                "bling", "LC_booster", "gambit_shop_level",
                                "daily_gambles", "daily_rolls",
                                "multiroller", "compound_roller", "roll_summarizer", "black_hole",
                                "investment_profit", "gamble_winnings",
        ]
        untouched =            ["lifetime_earned_dough", "lifetime_dough", "lifetime_gambles","highest_roll", ]

        lifetime_stats = [      "total_rolls", "earned_dough", "loaf_converter",
                                "natural_1", "ten_breads",  
                                "eleven_breads", "twelve_breads", "thirteen_breads", "fourteen_or_higher",
                                "special_bread", "rare_bread", "unique", "chess_pieces", "shiny",
                                "full_chess_set", "many_of_a_kind", 
                                "lottery_win",

        ]

        # convert omegas to shadows
        if self.get(values.omega_chessatron.text) > 0:
            self.increment(values.shadowmega_chessatron.text, self.get(values.omega_chessatron.text))
        # convert gold gems to shadows
        if self.get(values.gem_gold.text) > 0:
            self.increment(values.shadow_gem_gold.text, self.get(values.gem_gold.text))
        # convert moaks to shadows
        if self.get(values.anarchy_chess.text) > 0:
            self.increment(values.shadow_moak.text, self.get(values.anarchy_chess.text))

        for stat in lifetime_stats:
            if stat in self.values.keys():
                new_name = "lifetime_" + stat
                self.increment(new_name, self.get(stat))
                self.set(stat, 0)
        
        for stat in entries_to_remove:
            if stat in self.values.keys():
                self.set(stat, 0)

        for emote in emotes_to_remove:
            if emote.text in self.values.keys():
                self.set(emote.text, 0)

        # reset boosts file
        self.set("dough_boosts", dict())




    ##############################################################
    ######  GETTERS / SETTERS

    

    # simply says if the value is there and nonzero
    def has(self, value: typing.Union[str, Emote], amount: int = 1) -> bool:
        if (type(value) is str):
            if (value in self.values.keys()) and \
                        (self.values[value] >= amount):

                return True
        else: #is emote
            if (value.text in self.values.keys()) and \
                        (self.values[value.text] >= amount):

                return True
        
        return False

    #increases or decreases a value
    def increment(self, value: typing.Union[str, Emote], amount: int = 1):
        if (type(value) is str):
            if (value in self.values.keys()):
                self.values[value] += amount
            elif value in self.default_values.keys():
                self.values[value] = self.default_values[value] + amount
            else:
                self.values[value] = amount
        else: #is emote
            if (value.text in self.values.keys()):
                self.values[value.text] += amount
            elif value.text in self.default_values.keys():
                self.values[value.text] = self.default_values[value.text] + amount
            else:
                self.values[value.text] = amount

    def get(self, key: str):
        if key in self.values.keys():
            return self.values[key]
        elif key in self.default_values.keys():
            return self.default_values[key]
        return 0

    def set(self, name: str, value):
        self.values[name] = value

    def boolean_is(self, value: str, default: bool = False):
        if value in self.values.keys():
            return self.values[value]
        return default

    def add_item(self, item: Emote):
        self.increment(item.text, 1),
        dough_value = self.add_dough_intelligent(item.value)
        for attribute in item.attributes:
            self.increment(attribute, 1)
        return dough_value

    def add_item_attributes(self, item: Emote, amount: int = 1):
        self.increment(item.text, amount)
        for attribute in item.attributes:
            self.increment(attribute, amount)

    ##############################################################

    def get_dough(self):
        return self.get("total_dough")

    def add_dough_intelligent(self, amount: int):
        prestige_mult = self.get_prestige_multiplier()
        amount = round(amount * prestige_mult)
        self.increment("total_dough", amount)
        # self.increment("lifetime_dough", amount)
        self.increment("earned_dough", amount)
        return amount

    def get_prestige_level(self):
        return self.get("prestige_level")

    def get_prestige_multiplier(self):
        # return prestige_multiplier[self.get_prestige_level()]
        presige_level = self.get_prestige_level()
        multiplier = 1 + (presige_level * 0.10)
        return multiplier

    def get_display_name(self):

        bling_emotes = ["",
                    values.gem_red.text,
                    values.gem_blue.text,
                    values.gem_purple.text,
                    values.gem_green.text,
                    values.gem_gold.text,
                    values.anarchy_chess.text,]

        bling_level = self.get("bling")
        bling = bling_emotes[bling_level]

        escape_transform = str.maketrans({"_":  r"\_"}) # lol trans

        if "display_name" in self.values.keys():
            output = bling + self.values["display_name"].translate(escape_transform) + bling
            if utility.contains_ping(self.values["display_name"]):
                output = "[invalid username]"
        elif "username" in self.values.keys():
            output = bling + self.values["username"].translate(escape_transform) + bling
        else:
            output = "Unknown"

        prestige = self.get_prestige_level()
        if prestige > 0:
            output += " **" + str(prestige) + "**⭐"
        

        return output

    def get_portfolio_value(self):
        global bread_cog_ref
        if bread_cog_ref is None:
            bread_cog_ref = bread_cog.bread_cog_ref
        stonks_file = bread_cog_ref.json_interface.get_custom_file("stonks")
        own_stonks = self.get_all_items_with_attribute("stonks")

        total_value = 0

        for stonk in own_stonks:
            stonk_count = self.get(stonk.text)
            stonk_value = round(stonks_file[stonk.text])
            #print(f"stonk: {stonk}")
            value = stonk_count * stonk_value
            total_value += value
        return total_value

    def get_shadowmega_boost_count(self):
        from bread.store import chessatron_shadow_booster_levels
        shadowmega_boost_level = self.get("chessatron_shadow_boost")
        # print (f"shadowmega_boost_level: {shadowmega_boost_level}")
        max_shadowmegas = chessatron_shadow_booster_levels[shadowmega_boost_level]
        # print (f"max_shadowmegas: {max_shadowmegas}")
        shadowmega_count = self.get(values.shadowmega_chessatron.text)
        # print (f"shadowmega_count: {shadowmega_count}")
        affecting_shadowmegas = min(shadowmega_count, max_shadowmegas)
        # print (f"affecting_shadowmegas: {affecting_shadowmegas}")
        return affecting_shadowmegas

    def get_shadowmega_boost_amount(self):
        return self.get_shadowmega_boost_count() * 100

    def get_shadow_gold_gem_boost_count(self):
        from bread.store import shadow_gold_gem_luck_boost_levels
        boost_level = self.get("shadow_gold_gem_luck_boost")
        max_gem_bonus = shadow_gold_gem_luck_boost_levels[boost_level]
        gem_count = self.get(values.shadow_gem_gold.text)
        affecting_gems = min(gem_count, max_gem_bonus)
        return affecting_gems

    def get_maximum_daily_gifts(self):
        return self.get("max_daily_rolls") * 24 + self.get("loaf_converter") * 1000

    def get_dough_boost_for_item(self, item: Emote):
        boosts_file = self.values.get("dough_boosts", dict())
        if item.text in boosts_file.keys():
            return boosts_file[item.text]
        else:
            return 0

    def set_dough_boost_for_item(self, item: Emote, boost: int):
        boosts_file = self.values.get("dough_boosts", dict())
        boosts_file[item.text] = boost
        self.values["dough_boosts"] = boosts_file

    ##############################################################

    #gets all items
    def get_all_items(self):
        items = []
        for key in self.values.keys():
            item = values.get_emote(key)
            if item is not None:
                items.append(item)
        return items

    def get_all_items_with_attribute(self, attribute: str):
        items = []
        for key in self.values.keys():
            item = values.get_emote(key)
            if item is not None:
                if attribute in item.attributes:
                    items.append(item)
        return items

    def get_all_items_with_attribute_unrolled(self, attribute: str):
        items = []
        for key in self.values.keys():
            item = values.get_emote(key)
            if item is not None:
                if attribute in item.attributes:
                    # append repeatedly for each item
                    for i in range(self.get(key)):
                        items.append(item)
                    #items.append(item)
        return items

    # output the number of times a value exists, as text
    def write_number_of_times(self, value: str) -> str:
        amount = self.get(value)
        if type(amount) is not int:
            return str(amount)
        return utility.write_number_of_times(amount)

    # writes the pluralized count of a value
    def write_count(self, value: str, pretty_name: str) -> str:
        amount = self.get(value)
        if type(amount) is not int:
            return str(amount)
        return utility.write_count(amount, pretty_name)

    ##############################################################

    # returns NoneType if value does not exist
    def get_value_strict(self, name: str):
        if name in self.values.keys():
            return self.values[name]
        return None

    # returns 0 if value does not exist
    def get_value_loose(self, name: str):
        if name in self.values.keys():
            return self.values[name]
        return 0

    def set_value(self, name: str, amount: int):
        #if name in self.values.keys():
        self.values[name] = amount

    def increment_value(self, name: str, amount: int):
        if name not in self.values.keys():
            self.values[name] = 0
        self.values[name] += amount

    ##############################################################
    ######  INPUT / OUTPUT

    def from_dict(account_id:str, entry: dict):
        account = Bread_Account(account_id)
        account.values = entry.copy()
        #if "lifetime_dough" not in account.values.keys() \
        #        and "total_dough" in account.values.keys():
        #    account.values["lifetime_dough"] = entry["total_dough"]
        if "earned_dough" not in account.values.keys():
            account.values["earned_dough"] = account.values["total_dough"]
        return account

    def to_dict(self):
        return self.values
