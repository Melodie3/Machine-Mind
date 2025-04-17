#bread account
from __future__ import annotations

import typing 

from bread.values import Emote
import bread.utility as utility
import bread.values as values
import bread.space as space
import bread.store as store # Mel if this causes a circular import please DM me (Duck)
import bread.projects as projects
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
        "daily_rolls" : 0,
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
        "black_hole_conditions" : ["<:anarchy_chess:960772054746005534>", "<:gem_gold:1006498746718244944>", "14+"],
        "gifts_disabled" : False,
        "max_days_of_stored_rolls" : 1,
        "max_random_chess_pieces_per_day": 6400,
        "max_special_bread_packs_per_day": 5000000,
        "brick_troll_percentage" : 0,
        "daily_fuel": 100,
        "hub_credits": 2000,
        "auto_move_map": False,
        "tron_animation": True
    }


    def __init__(
            self: typing.Self,
            user_id: str
        ) -> None:
        self.user_id = user_id

    def reset_to_default(self: typing.Self) -> None:
        """Resets the account to default values."""
        username = self.get("username")
        display_name = self.get("display_name")
        guild_id = self.get("guild_id")
        user_id = self.get("id")
        self.values = {
            "total_dough" : 0,
            "earned_dough" : 0,
            "max_daily_rolls" : 10,
            "daily_rolls" : 0,
            "username": username,
            "display_name": display_name,
            "guild_id": guild_id,
            "id": user_id
        }

    def daily_reset(self: typing.Self) -> None:
        """Runs the daily reset on the account."""
        # self.set("daily_rolls", 0)

        # we need to deal with stored daily rolls, so:
        # first calculate what the max numbber of stored rolls is
        minimum_daily_rolls = -self.get_maximum_stored_rolls()
        # then remove one day of rolls from our counter
        new_daily_rolls = self.get("daily_rolls") - self.get("max_daily_rolls")
        # then make sure that we aren't exceeding our maximum
        new_daily_rolls = max(minimum_daily_rolls, new_daily_rolls)
        # then set the new value
        self.set("daily_rolls", new_daily_rolls)

        self.set("daily_gambles", 0)
        self.set("max_gambles", 20)

        if self.has ("daily_gifts"):
            self.set("daily_gifts", 0)
        if self.has ("first_catch_level"):
            self.set("first_catch_remaining", self.get("first_catch_level"))
        
        if self.has("random_chess_piece_bought"):
            self.set("random_chess_piece_bought", 0)
        if self.has("special_bread_pack_bought"):
            self.set("special_bread_pack_bought", 0)
        
        self.set("daily_fuel", self.get_daily_fuel_cap())
        self.set("hub_credits", self.get_projects_credits_cap())

    def increase_prestige_level(self: typing.Self) -> None:
        """Increases this account's prestige level by 1."""

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
        emotes_to_remove.extend(self.get_all_items_with_attribute("anarchy_pieces"))
        emotes_to_remove.append(values.chessatron)
        emotes_to_remove.append(values.omega_chessatron)
        emotes_to_remove.append(values.anarchy_chessatron)
        emotes_to_remove.append(values.anarchy_omega_chessatron)
        emotes_to_remove.append(values.normal_bread)
        emotes_to_remove.append(values.anarchy_chess)
        emotes_to_remove.append(values.fuel)
        emotes_to_remove.append(values.corrupted_bread)
        # we're keeping OoaKs

        entries_to_remove = [   "total_dough",
                                "bling", "LC_booster", "gambit_shop_level",
                                "daily_gambles", "daily_rolls",
                                "multiroller", "compound_roller", "roll_summarizer", "black_hole", "multiroller_terminal", "multiroller_active",
                                "investment_profit", "gamble_winnings",
                                "space_level", "telescope_level", "autopilot_level", "fuel_tank", "fuel_research", "multiroller_terminal", "advanced_exploration", "engine_efficiency",
                                "galaxy_move_count", "galaxy_xpos", "galaxy_ypos", "system_xpos", "system_ypos", "projects_completed", "trade_hubs_created",
        ]
        untouched =            ["lifetime_earned_dough", "lifetime_dough", "lifetime_gambles","highest_roll", ]

        lifetime_stats = [      "total_rolls", "earned_dough", "loaf_converter",
                                "natural_1", "ten_breads",  
                                "eleven_breads", "twelve_breads", "thirteen_breads", "fourteen_or_higher",
                                "special_bread", "rare_bread", "unique", "chess_pieces", "shiny", "anarchy_pieces",
                                "full_chess_set", "many_of_a_kind", 
                                "lottery_win",
                                "projects_completed", "trade_hubs_created", "full_anarchy_set"

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
        # convert anarchy omegas to shadows
        if self.get(values.anarchy_omega_chessatron.text) > 0:
            self.increment(values.anarchy_shadowmega.text, self.get(values.anarchy_omega_chessatron.text))

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

        # Reset the amount of times First Catch of the Day has been used to the level of FCotD.
        if self.has("first_catch_level"):
            self.set(
                key = "first_catch_remaining",
                value = self.get("first_catch_level")
            )
        
        self.set("daily_fuel", self.get_daily_fuel_cap())

        # reset boosts file
        self.set("dough_boosts", dict())

    def increase_prestige_to_goal(
            self: typing.Self, 
            goal: int
        ) -> None:
        prestige_level = self.get_prestige_level()
        if goal <= prestige_level:
            return
        self.increase_prestige_level()
        
        for i in range(self.get_prestige_level(), goal):
            max_level = store.Daily_rolls.max_level(self)
            for j in range(max_level - self.get("max_daily_rolls")):
                store.Daily_rolls.do_purchase(self)
            
            self.increase_prestige_level()


    ##############################################################
    ######  GETTERS / SETTERS

    

    # simply says if the value is there and nonzero
    def has(
            self: typing.Self,
            key: typing.Union[str, Emote],
            amount: int = 1
        ) -> bool:
        """Returns a boolean for whether the account has the given key and if it is greater than or equal to the given amount."""
        # If the given key is an Emote, set it to the emote's text.
        if isinstance(key, Emote):
            key = key.text

        if not key in self.values:
            return False
        
        return self.values[key] >= amount

    #increases or decreases a value
    def increment(
            self: typing.Self,
            key: typing.Union[str, Emote],
            amount: int = 1
        ) -> None:
        """Increments a key by the given amount."""
        # If the given key is an Emote, set it to the emote's text.
        if isinstance(key, Emote):
            key = key.text
        
        self.values[key] = self.get(key) + amount

    def get(
            self: typing.Self,
            key: str,
            default: typing.Any = 0
        ) -> typing.Any:
        """Gets a value from this account's values dict. If the account does not have it the default values will be returned, and, if all else fails, return the default."""
        if key in self.values.keys():
            return self.values[key]
        elif key in self.default_values.keys():
            return self.default_values[key]
        
        return default

    def set(
            self: typing.Self,
            key: str,
            value: typing.Any
        ) -> None:
        """Sets a value in this account's values dict."""
        self.values[key] = value

    def boolean_is(
            self: typing.Self,
            value: str,
            default: bool = False
        ) -> bool:
        """The same as `.get()`, but used for booleans, and it won't use the default values dict."""
        if value in self.values.keys():
            return self.values[value]
        return default

    def add_item(
            self: typing.Self,
            item: Emote
        ) -> int:
        """Adds 1 of the provided item to this account, and adds the item's value as well. Then it returns the dough added."""
        self.increment(item.text, 1),
        dough_value = self.add_dough_intelligent(item.value)
        for attribute in item.attributes:
            self.increment(attribute, 1)
        return dough_value

    def add_item_attributes(
            self: typing.Self,
            item: Emote,
            amount: int = 1
        ) -> None:
        """Adds an item to the account, but also adds its attributes as stats."""
        self.increment(item.text, amount)
        for attribute in item.attributes:
            self.increment(attribute, amount)

    ##############################################################

    def get_dough(self: typing.Self) -> int:
        """Shortcut for `.get('total_dough')`."""
        return self.get("total_dough")

    def add_dough_intelligent(
            self: typing.Self,
            amount: int
        ) -> int:
        """Adds dough to an account, but accounts for the ascension multiplier. Also adds to the `earned_dough` stat. In the end, it returns the amount of dough added."""
        prestige_mult = self.get_prestige_multiplier()
        amount = round(amount * prestige_mult)
        self.increment("total_dough", amount)
        # self.increment("lifetime_dough", amount)
        self.increment("earned_dough", amount)
        return amount

    def get_prestige_level(self: typing.Self) -> int:
        """Shortcut for `.get('prestige_level')`."""
        return self.get("prestige_level")

    def get_space_level(self: typing.Self) -> int:
        """Shortcut for `.get('space_level')`."""
        return self.get("space_level")
    
    def get_galaxy_location(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            correct_center: bool = False
        ) -> tuple[int, int]:
        """Returns this account's galaxy location in a 2D tuple. This will return the galaxy's spawn location if the player has not moved on the galaxy map."""
        # If the player has moved before, then return their position.
        if self.get("galaxy_move_count") > 0:
            out = (self.get("galaxy_xpos"), self.get("galaxy_ypos"))

            if correct_center and out in space.ALTERNATE_CENTER:
                out = (space.MAP_RADIUS, space.MAP_RADIUS)

            return out
        
        # If the player hasn't moved, then return the spawn point.
        return space.get_spawn_location(
            json_interface = json_interface,
            user_account = self
        )
    
    def get_system_location(self: typing.Self) -> tuple[int, int]:
        """Returns this player's system location in a 2D tuple."""
        return (self.get("system_xpos"), self.get("system_ypos"))

    def get_prestige_multiplier(self: typing.Self) -> float:
        """Returns the ascension multiplier for the ascension this player is on. The equation is `1 + (ascension * 0.10)`."""
        # return prestige_multiplier[self.get_prestige_level()]
        presige_level = self.get_prestige_level()
        multiplier = 1 + (presige_level * 0.10)
        return multiplier

    def get_display_name(self: typing.Self) -> str:
        """Returns this player's display name, including upgrades like bling and the ascension indicator."""
        bling_emotes = [
            "",
            values.gem_red.text,
            values.gem_blue.text,
            values.gem_purple.text,
            values.gem_green.text,
            values.gem_gold.text,
            values.chessatron.text,
            values.anarchy_chess.text,
            values.omega_chessatron.text,
            values.gem_pink.text,
            values.gem_orange.text,
            values.gem_cyan.text,
            values.anarchy_chessatron.text,
            values.anarchy_omega_chessatron.text,
            values.hotdog.text,
            values.gem_white.text,
        ]

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

    def get_portfolio_value(self: typing.Self) -> int:
        """Returns this player's current portfolio value."""
        global bread_cog_ref
        if bread_cog_ref is None:
            bread_cog_ref = bread_cog.bread_cog_ref
        guild_id = self.get("guild_id")
        if guild_id is None or guild_id == 0:
            guild_id = bread_cog.default_guild
        stonks_file = bread_cog_ref.json_interface.get_custom_file("stonks", guild_id)
        own_stonks = self.get_all_items_with_attribute("stonks")

        total_value = 0

        for stonk in own_stonks:
            stonk_count = self.get(stonk.text)
            stonk_value = round(stonks_file[stonk.text])
            #print(f"stonk: {stonk}")
            value = stonk_count * stonk_value
            total_value += value
        return total_value
    
    def get_active_multirollers(self: typing.Self) -> int:
        """Returns the number of active multiroller this player has.
        
        The method for determining the number of active multirollers:
        - If `multiroller_terminal` is less than 1, return `multiroller`.
        - If `active_multirollers` is not -1, return it, otherwise return `multiroller`."""
        multiroller = self.get("multiroller")
        if self.get("multiroller_terminal") < 1:
            return multiroller

        active = self.get("active_multirollers")

        if active == -1:
            return multiroller
        else:
            return active
        
    def get_corruption_negation_multiplier(self: typing.Self) -> float:
        """Returns the multiplier the Corruption Negation hidden bakery upgrade provides for this player. The equation is `1 - (cn * 0.1)`, where `cn` is the player's `corruption_negation` stat."""
        level = self.get("corruption_negation")
        return 1 - (level * 0.1)
    
    def get_fuel_refinement_boost(self: typing.Self) -> float:
        """Returns the multiplier for fuel this player has. The equation is `1 + (fr * 0.25)`, where `fr` is the player's `fuel_refinemnt` stat."""
        level = self.get("fuel_refinement")
        return 1 + (level * 0.25)
    
    def get_recipe_refinement_multiplier(self: typing.Self) -> int:
        """Returns the luck multiplier from recipe refinement. Equation: `2 ^ rr` where `rr` is the player's recipe refinement level."""
        return 2 ** self.get("LC_booster")
    
    def get_anarchy_piece_luck(
            self: typing.Self,
            roll_luck: int
        ) -> float:
        """Returns the luck of anarchy pieces. `roll_luck` is assumed to be `(loaf_converter + 1) * recipe_refinement_multiplier`"""
        return min(
            round(1 + store.Advanced_Exploration.get_contribution(self) * (roll_luck - self.get_recipe_refinement_multiplier()), 5),
            64 # 64 is the cap.
        )
    
    def get_space_gem_luck(
            self: typing.Self,
            roll_luck: int
        ) -> float:
        """Returns the luck of space gems. `roll_luck` is assumed to be `(loaf_converter + 1) * recipe_refinement_multiplier`"""
        return min(
            round(1 + 25 * store.Advanced_Exploration.get_contribution(self) * (roll_luck - self.get_recipe_refinement_multiplier()), 5),
            16384 # 16384 is the cap.
        )
    
    def get_projects_credits_cap(self: typing.Self) -> int:
        """Returns the maximum amount of Trade Hub credits this account can have."""
        return int(2000 + self.get(store.Payment_Bonus.name) * store.Payment_Bonus.per_level)
    
    def get_daily_fuel_cap(self: typing.Self) -> int:
        """Returns the maximum amount of daily fuel this account can have. This is `350 * fuel_tank + 100` where `fuel_tank` is the fuel tank level."""
        return store.Fuel_Tank.multiplier * self.get(store.Fuel_Tank.name) + 100 # 100 base daily fuel.

    def get_shadowmega_boost_count(self: typing.Self) -> int:
        """Returns the amount of shadowmega chessatrons that can be used to get more dough, so the number of active shadowmegas."""
        # from bread.store import chessatron_shadow_booster_levels
        shadowmega_boost_level = self.get("chessatron_shadow_boost")
        # print (f"shadowmega_boost_level: {shadowmega_boost_level}")
        # max_shadowmegas = chessatron_shadow_booster_levels[shadowmega_boost_level]
        max_shadowmegas = shadowmega_boost_level * 5
        # print (f"max_shadowmegas: {max_shadowmegas}")
        shadowmega_count = self.get(values.shadowmega_chessatron.text)
        # print (f"shadowmega_count: {shadowmega_count}")
        affecting_shadowmegas = min(shadowmega_count, max_shadowmegas)
        # print (f"affecting_shadowmegas: {affecting_shadowmegas}")
        return affecting_shadowmegas

    def get_shadowmega_boost_amount(self: typing.Self) -> int:
        """Returns the multiplier applied to omegas this player gets per chessatron from Chessatron Contraption and shadowmega chessatrons."""
        return 1 + 0.02 * self.get_shadowmega_boost_count()

    def get_shadow_gold_gem_boost_count(self: typing.Self) -> int:
        """Returns the amount of shadow gold gems that this player can use to increase their odds of finding gems. Essentially, this is the number of active shadow gold gems."""
        # from bread.store import shadow_gold_gem_luck_boost_levels
        boost_level = self.get("shadow_gold_gem_luck_boost")
        # max_gem_bonus = shadow_gold_gem_luck_boost_levels[boost_level]
        max_gem_bonus = boost_level * 10
        gem_count = self.get(values.shadow_gem_gold.text)
        affecting_gems = min(gem_count, max_gem_bonus)
        return affecting_gems

    def get_maximum_daily_gifts(self: typing.Self) -> int:
        """Calculates the maximum amount of dough that can be gifted to this player, equal to 24 per daily roll and 1,000 per loaf converter."""
        return self.get("max_daily_rolls") * 24 + self.get("loaf_converter") * 1000
    
    def get_maximum_stored_rolls(self: typing.Self) -> int:
        """Calculates the maximum amount of daily rolls this player can store, equal to max_daily_rolls multiplied by max_days_of_stored_rolls."""
        return self.get("max_daily_rolls") * self.get("max_days_of_stored_rolls")
    
    def get_maximum_daily_rolls(self: typing.Self) -> int:
        """Calculates the maximum amount of daily rolls this player can have, equal to 1000 + prestige_level * 100."""
        return 1000 + self.get_prestige_level() * 100

    def get_dough_boost_for_item(
            self: typing.Self,
            item: Emote
        ) -> int:
        """Returns the amount of extra dough this player gets from the Gambit Shop for the given item."""
        boosts_file = self.values.get("dough_boosts", dict())
        if item.text in boosts_file.keys():
            return boosts_file[item.text]
        else:
            return 0

    def set_dough_boost_for_item(
            self: typing.Self,
            item: Emote,
            boost: int
        ) -> None:
        """Sets an item's dough boost for this player to the given value."""
        boosts_file = self.values.get("dough_boosts", dict())
        boosts_file[item.text] = boost
        self.values["dough_boosts"] = boosts_file

    def get_chessatron_dough_amount(
            self: typing.Self,
            include_prestige_boost: bool = True
        ) -> int:
        """Calculates the amount of dough this player gets for each chessatron."""
        amount = values.chessatron.value
        # then we add omegas
        amount += (self.get(values.omega_chessatron.text) * 100) * self.get_shadowmega_boost_amount()
        if include_prestige_boost:
            prestige_mult = self.get_prestige_multiplier()
            amount = round(amount * prestige_mult)  
        return round(amount)
    
    def get_anarchy_chessatron_dough_amount(
            self: typing.Self,
            include_prestige_boost: bool = True
        ) -> int:
        """Calulcates the amount of dough this player gets for each anarchy chessatron."""
        multiplier = 350 + (self.get(values.anarchy_omega_chessatron.text) * 25)
        amount = self.get_chessatron_dough_amount(include_prestige_boost=False) * multiplier
        
        if include_prestige_boost:
            prestige_mult = self.get_prestige_multiplier()
            amount = round(amount * prestige_mult)

        return amount

    def get_maximum_gamble_wager(self) -> int:
        import bread.store as store
        """Returns the maximum amount of dough this account can gamble."""
        gamble_level = self.get("gamble_level")
        gamble_levels = store.High_Roller_Table.gamble_levels
        if gamble_level < len(gamble_levels):
            return gamble_levels[gamble_level]
        else:
            return gamble_levels[-1]

    def has_category(
            self: typing.Self,
            category_name: str
        ) -> bool:
        """Returns a boolean for whether this player has any item in the given category."""
        if len(self.get_category(category_name)) > 0:
            return True
        else:
            return False
                
    def get_category(
            self: typing.Self,
            category: str
        ) -> list[Emote]:
        """Returns a list of values.Emote objects that this player has."""
        items = []
        # we try with both the name and the name minus its last letter, in case there's an 's' at the end
        for category_name in [category, category[:-1]]:
            for item_name in self.values.keys():
                item = values.get_emote(item_name)
                if item is not None:
                    if category_name.lower() in item.attributes:
                        items.append(item)
        return items

    ##############################################################
    # Space related methods.

    def get_engine_efficiency_multiplier(
            self: typing.Self
        ) -> float:
        tiers = store.Engine_Efficiency.consumption_multipliers
        return tiers[self.get(store.Engine_Efficiency.name)]
    
    def get_corruption_chance(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface
        ) -> float:
        """Provides the chance of a loaf becoming corrupted, accounting for Corruption Negation. Is going to be a float between 0 and 1."""
        if self.get_space_level() < 1:
            return 0.0
        
        xpos, ypos = self.get_galaxy_location(json_interface=json_interface)

        base_chance = space.get_corruption_chance(
            xpos - space.MAP_RADIUS,
            ypos - space.MAP_RADIUS
        )

        multiplier = self.get_corruption_negation_multiplier()

        galaxy_tile = self.get_galaxy_tile(json_interface, load_data=True)

        if galaxy_tile.trade_hub is not None:
            multiplier *= projects.Storm_Repulsion_Array.corruption_multipliers[galaxy_tile.trade_hub.get_upgrade_level(projects.Storm_Repulsion_Array)]

        return base_chance * multiplier
    
    def get_anarchy_corruption_chance(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface
        ) -> float:
        """Provides the chance of an anarchy piece becoming corrupted. Is going to be a float between 0 and 1."""
        if self.get_space_level() < 1:
            return 0.0
        
        xpos, ypos = self.get_galaxy_location(json_interface=json_interface)

        return space.get_anarchy_corruption_chance(
            xpos - space.MAP_RADIUS,
            ypos - space.MAP_RADIUS
        )
        

    def get_galaxy_tile(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            load_data: bool = False
        ) -> space.GalaxyTile:
        """Returns a GalaxyTile object for the tile within the galaxy this account is currently on."""
        xpos, ypos = self.get_galaxy_location(json_interface=json_interface)

        return space.get_galaxy_coordinate(
            json_interface = json_interface,
            guild = self.get("guild_id"),
            galaxy_seed = self.get_galaxy_seed(json_interface),
            ascension = self.get_prestige_level(),
            xpos = xpos,
            ypos = ypos,
            load_data = load_data
        )
    
    def get_system_tile(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface
        ) -> space.SystemTile:
        """Returns a SystemTile subclass object for the tile within the system this account is in."""
        galaxy_tile = self.get_galaxy_tile(json_interface)

        xpos, ypos = self.get_system_location()

        return galaxy_tile.get_system_tile(
            json_interface = json_interface,
            system_x = xpos,
            system_y = ypos
        )
    
    def get_galaxy_seed(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface
        ) -> str:
        """Returns the seed of the galaxy this account is in."""
        return json_interface.get_ascension_seed(self.get_prestige_level(), guild=self.get("guild_id"))

    ##############################################################

    #gets all items
    def get_all_items(self: typing.Self) -> list[Emote]:
        """Gets a list of every item this player has."""
        items = []
        for key in self.values.keys():
            item = values.get_emote(key)
            if item is not None:
                items.append(item)
        return items

    def get_all_items_with_attribute(
            self: typing.Self,
            attribute: str
        ) -> list[Emote]:
        """Gets a list of every item this player has, that has the given attribute."""
        items = []
        for key in self.values.keys():
            item = values.get_emote(key)
            if item is not None:
                if attribute in item.attributes:
                    items.append(item)
        return items

    def get_all_items_with_attribute_unrolled(
            self: typing.Self,
            attribute: str
        ) -> list[Emote]:
        """Same as `.get_all_items_with_attribute()`, but each item is in the list an amount of times equal to the amount the player has.
        
        On some accounts this will completely freeze the bot."""
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
    def write_number_of_times(
            self: typing.Self,
            value: str
        ) -> str:
        """Returns the times representation of a stat.
        
        For example, with `.write_number_of_times('lottery_win')`, and the player has 2 lottery_win, it will return `twice`, but with 5 lottery_win, it would return `5 times`."""
        amount = self.get(value)
        if type(amount) is not int:
            return str(amount)
        return utility.write_number_of_times(amount)

    # writes the pluralized count of a value
    def write_count(
            self: typing.Self,
            value: str,
            pretty_name: str
        ) -> str:
        """Writes the count of a stat, with `value` being the stat name and `pretty_name` being the text to put after it.
        
        For example, with `.write_count('loaf_converter', 'Loaf Converters')`, if the player has 2 loaf converters it will return `2 Loaf Converters`, but with 1 loaf converter it would return `1 Loaf Converter`."""
        amount = self.get(value)
        if type(amount) is not int:
            return str(amount)
        return utility.write_count(amount, pretty_name)

    ##############################################################

    # returns NoneType if value does not exist
    def get_value_strict(
            self: typing.Self,
            name: str
        ) -> typing.Any:
        """Stricter version of `.get()`, this doesn't refer to the default values dict, and returns None if the player does not have the stat."""
        if name in self.values.keys():
            return self.values[name]
        return None

    # returns 0 if value does not exist
    def get_value_loose(
            self: typing.Self,
            name: str
        ) -> typing.Any:
        """Slightly different version of `.get()`, this one returns 0 if the key is not found, but does not refer to the default values dict at all."""
        if name in self.values.keys():
            return self.values[name]
        return 0

    def set_value(
            self: typing.Self,
            name: str,
            amount: int
        ) -> None:
        """Same as `.set()`, sets a value in this account's values dict."""
        #if name in self.values.keys():
        self.values[name] = amount

    def increment_value(
            self: typing.Self,
            name: str,
            amount: int
        ) -> None:
        """Similar to `.increment()`, but this sets the stat to 0 if the player doesn't have it, and this doesn't refer to the default values dict."""
        if name not in self.values.keys():
            self.values[name] = 0
        self.values[name] += amount

    ##############################################################
    ######  INPUT / OUTPUT

    def from_dict(
            account_id: str,
            entry: dict
        ) -> Bread_Account:
        """Converts a dictionary and account id into a new Bread_Account object and returns said object."""
        account = Bread_Account(account_id)
        account.values = entry.copy()
        #if "lifetime_dough" not in account.values.keys() \
        #        and "total_dough" in account.values.keys():
        #    account.values["lifetime_dough"] = entry["total_dough"]
        if "earned_dough" not in account.values.keys():
            account.values["earned_dough"] = account.values["total_dough"]
        return account

    def to_dict(self: typing.Self) -> dict:
        """Converts this account to a dict. This is just returning the `values` attribute."""
        return self.values
