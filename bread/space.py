from __future__ import annotations

import discord

import math
import typing
import random
import io
import sys

# pip3 install pillow
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw

import bread.account as account
import bread.generation as generation
import bread.values as values
import bread.projects as projects
import bread.utility as utility
import bread.store as store

import bread_cog

sys.set_int_max_str_digits(2 ** 31 - 1)

MAP_SIZE = 256

MAP_RADIUS = MAP_SIZE // 2
MAP_RADIUS_SQUARED = MAP_RADIUS ** 2

## Fuel requirements:
# This is the amount of fuel required for each jump in their respective areas.
MOVE_FUEL_SYSTEM = 25
MOVE_FUEL_GALAXY = 175
MOVE_FUEL_GALAXY_NEBULA = 350
MOVE_FUEL_WORMHOLE = 325

# Alternate center points:
# These are the points that are the same as (MAP_RADIUS, MAP_RADIUS), due to the 2x2 system at the center of the galaxy.
ALTERNATE_CENTER = [(MAP_RADIUS - 1, MAP_RADIUS - 1), (MAP_RADIUS, MAP_RADIUS - 1), (MAP_RADIUS - 1, MAP_RADIUS)]
ALL_CENTER = ALTERNATE_CENTER + [(MAP_RADIUS, MAP_RADIUS)]

HubColor = int
HUB_RED = 0
HUB_ORANGE = 1
HUB_YELLOW = 2
HUB_GREEN = 3
HUB_CYAN = 4
HUB_BLUE = 5
HUB_PURPLE = 6
HUB_PINK = 7

HUB_COLOR_TO_STRING = {
    HUB_RED: "red",
    HUB_ORANGE: "orange",
    HUB_YELLOW: "yellow",
    HUB_GREEN: "green",
    HUB_CYAN: "cyan",
    HUB_BLUE: "blue",
    HUB_PURPLE: "purple",
    HUB_PINK: "pink",
}

# Swap the keys and values so you can go back and forth.
HUB_STRING_TO_COLOR = dict(map(reversed, HUB_COLOR_TO_STRING.items()))

# For the Trade Hub communication bouncing it needs bitboard masks for circles as well as the left and right halves of the map.
MASK_LEFT = sum([(2 ** MAP_RADIUS - 1) << (n * MAP_SIZE) for n in range(MAP_SIZE)])
MASK_RIGHT = MASK_LEFT << 128
CIRCLE_8 = utility.dynamic_circle(8)
CIRCLE_16 = utility.dynamic_circle(16)

BASE_COMMUNICATION_RADIUS = 8

def make_circle_mask(
        x: int,
        y: int,
        radius: int = 8
    ) -> int:
    global circles
    
    x -= radius
    y -= radius
    
    if radius == 8:
        out = CIRCLE_8
    else:
        out = CIRCLE_16

    if x > 0:
        out <<= x
    else:
        out >>= abs(x)
    
    if y > 0:
        out <<= y * 256
    else:
        out >>= abs(y) * 256
    
    # Remove any artifacts caused by wrapping around the left and right edges.
    if x < 64:
        out &= MASK_LEFT
    elif x > 256 - 64:
        out &= MASK_RIGHT
    
    return out

## Emojis:

MAP_EMOJIS = {
    # Backgrounds.
    "empty": ":black_large_square:",
    "nebula": ":purple_square:",
    "fog": ":fog:",
    "border": ":blue_square:",
    "no_entry": ":no_entry_sign:",

    # Stars.
    "star1": ":sunny:",
    "star2": ":star2:",
    "star3": ":star:",
    "black_hole": ":white_square_button:",

    # Misc.
    "rocket": ":rocket:",
    "trade_hub": ":post_office:",
    "asteroid": ":rock:",
    "wormhole": ":hole:",
}

# These are stored as decimal numbers, but are read in binary.
FULL_MAP_NUMBER_DATA = {
    "0": 499878774318, # 0
    "1": 150999273631, # 1
    "2": 499324621087, # 2
    "3": 1031900955710, # 3
    "4": 75517364290, # 4
    "5": 1082900120638, # 5
    "6": 499858851374, # 6
    "7": 1066261352584, # 7
    "8": 499875628590, # 8
    "9": 499878691873, # 9
    "-": 32505856 # -
}

WORMHOLE_COLOR = (94, 9, 188)
ASTEROID_COLOR = (128, 128, 128)
TRADE_HUB_COLOR = (96, 96, 96)

BORDER_REGULAR = (255, 0, 0)
BORDER_NEBULA = (153, 0, 255)

NEBULA_COLOR = (65, 25, 139)
EXPLORED_COLOR = (29, 26, 54)
UNEXPLORED_COLOR = (80, 79, 90)

MAP_TEXT_BACKGROUND = (12, 11, 22)
MAP_TEXT_COLOR = (255, 255, 255)

STAR_COLORS_NO_HUB = {
    "star1": (229, 173, 0),
    "star2": (229, 173, 0),
    "star3": (229, 173, 0),
    "black_hole": (123, 93, 0),
    "supermassive_black_hole": (123, 93, 0)
}

STAR_COLORS_WITH_HUB = {
    "star1": (31, 163, 0),
    "star2": (31, 163, 0),
    "star3": (31, 163, 0),
    "black_hole": (18, 98, 0),
    "supermassive_black_hole": (18, 98, 0)
}

PLANET_COLORS = {
    "bread": (252, 229, 205),
    
    "croissant": (249, 203, 156),
    "flatbread": (249, 203, 156),
    "stuffed_flatbread": (249, 203, 156),
    "french_bread": (249, 203, 156),
    "sandwich": (249, 203, 156),

    "bagel": (246, 178, 107),
    "doughnut": (246, 178, 107),
    "waffle": (246, 178, 107),

    "Bpawn": (183, 183, 183),
    "Bknight": (183, 183, 183),
    "Bbishop": (183, 183, 183),
    "Brook": (183, 183, 183),
    "Bqueen": (183, 183, 183),
    "Bking": (183, 183, 183),

    "Wpawn": (224, 224, 224),
    "Wknight": (224, 224, 224),
    "Wbishop": (224, 224, 224),
    "Wrook": (224, 224, 224),
    "Wqueen": (224, 224, 224),
    "Wking": (224, 224, 224),

    "gem_red": (234, 153, 153),
    "gem_blue": (159, 197, 232),
    "gem_purple": (180, 167, 214),
    "gem_green": (182, 215, 168),
    "gem_gold": (255, 242, 204),
    "gem_pink": (219, 84, 166),
    "gem_orange": (236, 89, 0),
    "gem_cyan": (18, 134, 121),
    "gem_white": (209, 209, 209),

    "anarchy_chess": (224, 104, 104),

    "Bpawnanarchy": (0, 23, 60),
    "Bknightanarchy": (0, 23, 60),
    "Bbishopanarchy": (0, 23, 60),
    "Brookanarchy": (0, 23, 60),
    "Buqeenanarchy": (0, 23, 60),
    "Bkinganarchy": (0, 23, 60),

    "Wpawnanarchy": (255, 156, 174),
    "Wknightanarchy": (255, 156, 174),
    "Wbishopanarchy": (255, 156, 174),
    "Wrookanarchy": (255, 156, 174),
    "Wqueenanarchy": (255, 156, 174),
    "Wkinganarchy": (255, 156, 174),
}

EMOJI_PATHS = {
    # Numbers.
    "1": "images/1.png",
    "2": "images/2.png",
    "3": "images/3.png",
    "4": "images/4.png",
    "5": "images/5.png",
    "6": "images/6.png",
    "7": "images/7.png",
    "8": "images/8.png",
    "9": "images/9.png",
    "10": "images/10.png", # yoggers
    "11": "images/11.png",
    "12": "images/12.png",
    "13": "images/13.png",
    "14": "images/14.png",
    "15": "images/15.png",
    "16": "images/16.png",
    "17": "images/17.png",
    "18": "images/18.png",
    "19": "images/19.png",
    "20": "images/20.png",
    "21": "images/21.png",
    "22": "images/22.png",
    "23": "images/23.png",
    "24": "images/24.png",
    "25": "images/25.png",
    "26": "images/26.png",

    # Letters.
    "a": "images/a.png",
    "b": "images/b.png",
    "c": "images/c.png",
    "d": "images/d.png",
    "e": "images/e.png",
    "f": "images/f.png",
    "g": "images/g.png",
    "h": "images/h.png",
    "i": "images/i.png",
    "j": "images/j.png",
    "k": "images/k.png",
    "l": "images/l.png",
    "m": "images/m.png",
    "n": "images/n.png",
    "o": "images/o.png",
    "p": "images/p.png",
    "q": "images/q.png",
    "r": "images/r.png",
    "s": "images/s.png",
    "t": "images/t.png",
    "u": "images/u.png",
    "v": "images/v.png",
    "w": "images/w.png",
    "x": "images/x.png",
    "y": "images/y.png",
    "z": "images/z.png", # This should be able to handle up to Upgraded Telecopes 10, but not beyond.
    
    # Filler.
    "border": "images/border.png",
    "blocker": "images/blocker.png",
    "background": "images/background.png",
    "nebula": "images/nebula.png",
    "fog": "images/fog.png",

    # Misc.
    "rocket": "images/rocket.png",
    "star1": "images/star1.png",
    "star2": "images/star2.png",
    "star3": "images/star3.png",
    "black_hole": "images/black_hole.png",
    "supermassive_black_hole": "images/black_hole.png", # Glaciers melting in the dead of night.
    "wormhole": "images/wormhole.png",
    "asteroid": "images/asteroid.png",
    "bread": "images/bread.png",

    # Trade Hubs.
    "trade_hub_red": "images/trade_hub_red.png",
    "trade_hub_orange": "images/trade_hub_orange.png",
    "trade_hub_yellow": "images/trade_hub_yellow.png",
    "trade_hub_green": "images/trade_hub_green.png",
    "trade_hub_cyan": "images/trade_hub_cyan.png",
    "trade_hub_blue": "images/trade_hub_blue.png",
    "trade_hub_purple": "images/trade_hub_purple.png",
    "trade_hub_pink": "images/trade_hub_pink.png",
    
    # 2x2 black hole.
    "black_hole_top_left": "images/black_hole_top_left.png",
    "black_hole_top_right": "images/black_hole_top_right.png",
    "black_hole_bottom_left": "images/black_hole_bottom_left.png",
    "black_hole_bottom_right": "images/black_hole_bottom_right.png",

    # Special breads.
    "croissant": "images/croissant.png",
    "flatbread": "images/flatbread.png",
    "stuffed_flatbread": "images/stuffed_flatbread.png",
    "sandwich": "images/sandwich.png",
    "french_bread": "images/french_bread.png",

    # Rare breads.
    "bagel": "images/bagel.png",
    "waffle": "images/waffle.png",
    "doughnut": "images/doughnut.png",

    # Black Chess pieces.
    "Bpawn": "images/bpawn.png",
    "Bknight": "images/bknight.png",
    "Bbishop": "images/bbishop.png",
    "Brook": "images/brook.png",
    "Bqueen": "images/bqueen.png",
    "Bking": "images/bking.png",

    # White Chess pieces.
    "Wpawn": "images/wpawn.png",
    "Wknight": "images/wknight.png",
    "Wbishop": "images/wbishop.png",
    "Wrook": "images/wrook.png",
    "Wqueen": "images/wqueen.png",
    "Wking": "images/wking.png",

    # Black anarchy pieces.
    "Bpawnanarchy": "images/bpawn_anarchy.png",
    "Bknightanarchy": "images/bknight_anarchy.png",
    "Bbishopanarchy": "images/bbishop_anarchy.png",
    "Brookanarchy": "images/brook_anarchy.png",
    "Bqueenanarchy": "images/bqueen_anarchy.png",
    "Bkinganarchy": "images/bking_anarchy.png",

    # White anarchy pieces.
    "Wpawnanarchy": "images/wpawn_anarchy.png",
    "Wknightanarchy": "images/wknight_anarchy.png",
    "Wbishopanarchy": "images/wbishop_anarchy.png",
    "Wrookanarchy": "images/wrook_anarchy.png",
    "Wqueenanarchy": "images/wqueen_anarchy.png",
    "Wkinganarchy": "images/wking_anarchy.png",

    # Gems.
    "gem_red": "images/gem_red.png",
    "gem_blue": "images/gem_blue.png",
    "gem_purple": "images/gem_purple.png",
    "gem_green": "images/gem_green.png",
    "gem_gold": "images/gem_gold.png",
    "gem_pink": "images/gem_pink.png",
    "gem_orange": "images/gem_orange.png",
    "gem_cyan": "images/gem_cyan.png",
    "gem_white": "images/gem_white.png",

    # MoaK.
    "anarchy_chess": "images/anarchy_chess.png",
}

print("Bread Space: Loading map images.")

EMOJI_IMAGES = {}

for key, path in EMOJI_PATHS.items():
    try:
        EMOJI_IMAGES[key] = Image.open(path).resize((128, 128))
    except FileNotFoundError:
        print(f"Bread Space: Map image loading failed for {key} ({path}) as the file does not exist.")

print(f"Bread Space: Map image loading complete. Loaded images: {len(EMOJI_IMAGES)}/{len(EMOJI_PATHS)}.")


########################################################################################
##### Base SystemTile class.

class SystemTile:
    def __init__(
            self: typing.Self,
            galaxy_seed: str,
            
            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int
        ) -> None:
        """Object that represents a tile within a system.

        Tile types:
        - empty
        - planet
        - star
        - asteroid
        - trade_hub

        Args:
            galaxy_seed (str): The seed of this galaxy.
            galaxy_xpos (int): The x position of the system within the galaxy that this tile is in.
            galaxy_ypos (int): The y position of the system within the galaxy that this tile is in.
            system_xpos (int): The x position of this tile within the system.
            system_ypos (int): The y position of this tile within the system.

            planet_type (typing.Optional[typing.Type[values.Emote]], optional): The type of planet that's on this tile. Defaults to None.
            planet_distance (typing.Union[int, float, None], optional): The distance of the planet from the center of the system. Defaults to None.
            planet_angle (typing.Union[int, float, None], optional): The angle of the planet from the center of the system. Defaults to None.
            planet_deviation (typing.Union[int, float, None], optional): The deviation of the roll modifiers for this planet. Defaults to None.

            star_type (typing.Optional[str], optional): The type of star that's on this tile. Defaults to None.

            trade_hub_level (typing.Optional[int], optional): The level of the trade hub that's on this tile. Defaults to None.
        """
        self.type = "base"
        
        self.galaxy_seed = galaxy_seed

        self.galaxy_xpos = galaxy_xpos
        self.galaxy_ypos = galaxy_ypos
        self.system_xpos = round(system_xpos)
        self.system_ypos = round(system_ypos)

        self.galaxy_tile = None
    
    # Optional for subclasses.
    def __str__(self: typing.Self):
        return f"<SystemTile | Type: {self.type} | system_x: {self.system_xpos} | system_y: {self.system_ypos} | galaxy_x: {self.galaxy_xpos} | galaxy_y: {self.galaxy_ypos}>"
    
    # Optional for subclasses.
    def __repr__(self: typing.Self):
        return self.__str__()
    
    # Optional for subclasses.
    def tile_seed(self: typing.Self) -> str:
        """Generates a string with multiple parts, all relating to this tile's position."""
        return f"{self.galaxy_seed}{self.galaxy_xpos}{self.galaxy_ypos}{self.system_xpos}{self.system_ypos}"
    
    ###############################################################################
    ##### Interaction methods.
    
    # Should be overwitten by subclasses.
    def get_emoji(self: typing.Self) -> str:
        """Returns an emoji that represents this tile."""
        return "background"
    
    def get_galaxy_tile(
            self: typing.Self,
            user_account: account.Bread_Account,
            json_interface: bread_cog.JSON_interface,
        ) -> GalaxyTile:
        """Gets the galaxy tile for the tile this is in. This is based off of the `galaxy_tile` attribute, but will load it if it has not been loaded yet."""
        if self.galaxy_tile is None:
            self.galaxy_tile = get_galaxy_coordinate(
                json_interface = json_interface,
                guild = user_account.get("guild_id"),
                galaxy_seed = self.galaxy_seed,
                ascension = user_account.get_prestige_level(),
                xpos = self.galaxy_xpos,
                ypos = self.galaxy_ypos,
                load_data = True
            )
        
        return self.galaxy_tile
        

    ###############################################################################
    ##### Analysis methods.

    # Should be overwitten by subclasses.
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        """Generates a list of strings that describe this tile, to be used by the analysis command."""
        return [self.__str__()]

########################################################################################
##### SystemTile subclasses

class SystemEmpty(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)
        self.type = "empty"
    
    def get_emoji(self: typing.Self) -> str:
        return "background"
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        return ["There seems to be nothing here."]
    
class SystemEdge(SystemEmpty):
    def get_emoji(self: typing.Self) -> str:
        return "blocker"
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        return ["There seems to be nothing here.", "This is the edge of the system."]
    
########################################################

class SystemStar(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int,

            star_type: typing.Optional[str] = None
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)

        self.star_type = star_type
        self.type = "star"
    
    def get_emoji(self: typing.Self) -> str:
        return self.star_type
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        out = [
            "Object type: Star",
            f"Star type: {self.star_type.title()}"
        ]

        if self.star_type == "black_hole" and detailed:
            out.append("Sensors read more interference and")
            out.append("more dynamic deviations than normal.")

        if self.star_type == "supermassive_black_hole" and detailed:
            out.append("Sensors read extremely strong interference")
            out.append("compared to the norm and therefore ")
            out.append("incredibly more dynamic deviations.")

        return out
    
########################################################

class SystemAsteroid(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)
        self.type = "asteroid"
    
    def get_emoji(self: typing.Self) -> str:
        return "asteroid"

    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        result = [
            "Object type: Asteroid",
        ]

        if detailed:
            result.append("Astroid Type: Boinge")
        else:
            result.append("Further details: None")
        
        return result
    
########################################################

class SystemTradeHub(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int,

            trade_hub_level: int = None,
            color: HubColor | None = None,
            upgrades: dict[str, int] = None,
            settings: dict[str, typing.Any] = None
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)
        if upgrades is None:
            upgrades = {}
        if settings is None:
            settings = {}
        if color is None:
            color = HUB_RED

        self.trade_hub_level = trade_hub_level
        self.upgrades = upgrades
        self.settings = settings
        self.project_count = store.trade_hub_projects[trade_hub_level]
        self.type = "trade_hub"
        self.color = color
    
    @property
    def color_str(self: typing.Self) -> str:
        return HUB_COLOR_TO_STRING[self.color]
    
    @property
    def trade_distance(self: typing.Self) -> int:
        return store.trade_hub_distances[self.trade_hub_level]
    
    @property
    def communication_distance(self: typing.Self) -> int:
        return 8 * (1 + self.get_upgrade_level(projects.Detection_Array))
    
    def get_emoji(self: typing.Self) -> str:
        return f"trade_hub_{self.color_str}"
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        day_seed = json_interface.get_day_seed(guild=guild)

        out = [
            "Object type: Trade Hub",
            f"Trade Hub level: {self.trade_hub_level}",
        ]
        
        if detailed:
            out.append("")
            out.append("Purchased upgrades:")
            
            for upgrade in projects.all_trade_hub_upgrades:
                if self.get_upgrade_level(upgrade):
                    out.append(f"- {upgrade.name(day_seed, self)} level {self.get_upgrade_level(upgrade)}")
                    
            out.append("")
            out.append("Available upgrades:")
            
            for upgrade in self.get_available_upgrades(day_seed):
                out.append(f"- {upgrade.name(day_seed, self)}")
                
            out.append("")
        else:
            out.extend([f"Purchased upgrades: {sum(1 for upgrade in projects.all_trade_hub_upgrades if self.get_upgrade_level(upgrade))}", f"Available upgrades: {len(self.get_available_upgrades(day_seed))}"])

        out.extend([f"Trade Hub color: {self.color_str.title()}", "Use '$bread space hub' while over the trade hub to interact with it."])
        
        return out
    
    def get_upgrade_level(
            self: typing.Self,
            upgrade: str | projects.Trade_Hub_Upgrade,
            default: int | None = 0
        ) -> int:
        """Gets the level this trade hub has of the given upgrade."""
        return self.get_upgrade_data(upgrade, dict()).get('level', default)

    def get_upgrade_data(
            self: typing.Self,
            upgrade: str | projects.Trade_Hub_Upgrade,
            default: int | None = 0
        ) -> dict:
        """Gets the data for the given trade hub upgrade."""
        if not isinstance(upgrade, str):
            upgrade = upgrade.internal
        
        return self.upgrades.get(upgrade, default)

    def get_available_upgrades(
            self: typing.Self,
            day_seed: str
        ) -> list[projects.Trade_Hub_Upgrade]:
        """Gives a list of available upgrades for this Trade Hub, factoring in things like required hub tiers and max upgrade levels."""
        return [upgrade for upgrade in projects.all_trade_hub_upgrades if upgrade.is_available(day_seed, self)]

    def get_purchased_upgrades(
            self: typing.Self
        ) -> list[projects.Trade_Hub_Upgrade]:
        return [upgrade for upgrade in projects.all_trade_hub_upgrades if self.get_upgrade_level(upgrade) > 0]
    
    def get_setting(
            self: typing.Self,
            key: str,
            default: typing.Any = None
        ) -> typing.Any:
        return self.settings.get(key, default)
        
    def to_dict(
            self: typing.Self,
            project_data: dict,
            level_progress: dict
        ) -> dict:
        return {
            "location": [self.system_xpos, self.system_ypos],
            "level": self.trade_hub_level,
            "project_progress": project_data,
            "level_progress": level_progress,
            "upgrades": self.upgrades,
            "settings": self.settings
        }
    
########################################################

class SystemPlanet(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int,

            planet_type: typing.Optional[typing.Type[values.Emote]] = None,
            planet_distance: typing.Union[int, float, None] = None,
            planet_angle: typing.Union[int, float, None] = None,
            planet_deviation: typing.Union[int, float, None] = None
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)

        self.planet_type = planet_type
        self.planet_distance = planet_distance
        self.planet_angle = planet_angle
        self.planet_deviation = planet_deviation
        self.type = "planet"
    
    def get_emoji(self: typing.Self) -> str:
        return self.planet_type.name
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        day_seed = json_interface.get_day_seed(guild=guild)
        ascension = json_interface.ascension_from_seed(guild=guild, galaxy_seed=self.galaxy_seed)

        planet_modifiers = get_planet_modifiers(
            json_interface = json_interface,
            ascension = ascension,
            guild=guild,
            day_seed = day_seed,
            tile = self
        )

        categories = {
            "Special Bread": values.croissant,
            "Rare Bread": values.bagel,
            "Chess Piece": values.black_pawn,
            "Red Gems": values.gem_red,
            "Blue Gems": values.gem_blue,
            "Purple Gems": values.gem_purple,
            "Green Gems": values.gem_green,
            "Gold Gems": values.gem_gold,
            "Many of a Kind": values.anarchy_chess,
            "Anarchy Piece": values.anarchy_black_pawn,
            "Space gem": values.gem_pink
        }
        deviation = self.planet_deviation
        
        galaxy_tile = self.get_galaxy_tile(
            json_interface = json_interface,
            user_account = user_account
        )

        if galaxy_tile.in_nebula:
            denominator = 1
        else:
            denominator = math.tau

        if galaxy_tile.star.star_type == "black_hole":
            # If it's a black hole, make it a little crazier by dividing the denominator by 5.
            denominator /= 5
        
        effective_deviation = (1 - self.planet_deviation) / denominator

        ranges = [
            (float('-inf'), 0.75, "Extremely Stable"),
            (0.75, 0.85, "Very Stable"),
            (0.85, 0.95, "Stable"),
            (0.95, 1.05, "Neutral"),
            (1.05, 1.15, "Unstable"),
            (1.15, 1.25, "Very Unstable"),
            (1.25, 1.5, "Extremely Unstable"),
            (1.5, float('inf'), "boinge")
        ]
        
        stability = next(
            text for lower, upper, text in ranges
            if (lower < deviation <= upper and upper > 1) or \
                (lower <= deviation < upper and upper < 1) or \
                (lower <= deviation <= upper and (upper > 1 and lower < 1))
        )

        if not detailed:
            result = [
                "Object type: Planet",
                f"Planet type: {self.planet_type.text}",
                f"Stability: {stability}",
                "",
                "Distance too far to determine more information."
            ]

            return result

        result = [
            "Object type: Planet",
            f"Planet type: {self.planet_type.text}",
            f"Distance: {round(self.planet_distance, 3)}",
            f"Angle: {self.planet_angle}",
            f"Raw deviation: {round(deviation, 3)}",
            f"Effective deviation: {round(effective_deviation, 3)}",
            f"Base stability: {stability}"
            "", # Blank item to add line break.
            "Item modifiers:"
        ]

        # Items in categories have the same chance. e.g., every rare special has the same modifier.
        # This means we only need to get one item in each category.
        for name, item in categories.items():
            result.append(f"- {name}: {round(planet_modifiers.get(item), 3)}")

        return result
    
    def get_priority_item(self: typing.Self) -> typing.Union[values.Emote, str, None]:
        """Returns the item or category that is prioritized by this planet."""
        if self.planet_type in values.all_very_shinies:
            return "space_gem"
        
        if self.planet_type in values.all_anarchy_pieces:
            return "anarchy_piece"
        
        if self.planet_type.text == values.anarchy_chess.text:
            return self.planet_type.name
        
        elif self.planet_type in values.all_shinies:
            return self.planet_type.name
        
        elif self.planet_type in values.chess_pieces_white:
            return "chess_piece"
        
        elif self.planet_type in values.chess_pieces_black:
            return "chess_piece"
        
        elif self.planet_type in values.all_rare_breads:
            return "rare_bread"
        
        elif self.planet_type in values.all_special_breads:
            return "special_bread"
        
        return self.planet_type.name
        
########################################################

class SystemWormhole(SystemTile):
    def __init__(
            self: typing.Self,
            galaxy_seed: str,

            galaxy_xpos: int,
            galaxy_ypos: int,
            system_xpos: int,
            system_ypos: int,

            wormhole_link_location: tuple[int, int] = None
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)

        self.wormhole_link_location = wormhole_link_location
        self.type = "wormhole"
    
    def get_emoji(self: typing.Self) -> str:
        return "wormhole"
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            user_account: account.Bread_Account,
            detailed: bool = False
        ) -> list[str]:
        out = [
            "Object type: Wormhole",
            "Use '$bread space move wormhole' when above."
        ]
        
        if detailed:
            out.append(f"Link location: {self.wormhole_link_location}")
        else:
            out.append("Futher information: Unavailable.")
        
        return out
    
    def get_pair(self: typing.Self) -> SystemWormhole:
        """Returns a SystemWormhole object for this wormhole's pair."""
        xpos, ypos = self.wormhole_link_location
        
        pair_system = generation.generate_system(
            galaxy_seed = self.galaxy_seed,
            galaxy_xpos = xpos,
            galaxy_ypos = ypos
        )

        return SystemWormhole(
            galaxy_seed = self.galaxy_seed,
            galaxy_xpos = xpos,
            galaxy_ypos = ypos,
            system_xpos = pair_system["wormhole"].get("xpos"),
            system_ypos = pair_system["wormhole"].get("ypos"),
            wormhole_link_location = (self.galaxy_xpos, self.galaxy_ypos)
        )







########################################################################################
##### GalaxyTile

class GalaxyTile:
    def __init__(
            self: typing.Self,
            galaxy_seed: str,
            ascension: int,
            guild: typing.Union[discord.Guild, int, str],
            xpos: int,
            ypos: int,
            system: bool,
            json_interface: bread_cog.JSON_interface,
            in_nebula: bool = False,

            raw_system_data: dict | None = None,

            system_radius: int = None,
            star: SystemStar = None,
            trade_hub: SystemTradeHub = False,
            asteroids: list[SystemAsteroid] = None,
            planets: list[SystemPlanet] = None,
            wormhole: SystemWormhole = None,
        ) -> None:
        """Object that represents a tile within the galaxy.

        Args:
            galaxy_seed (str): The seed of this galaxy.
            ascension (int): The ascension of this galaxy.
            xpos (int): The x position of this tile in the galaxy.
            ypos (int): The y position of this tile in the galaxy.
            system (bool): A boolean for whether this tile has a star system on it.
            in_nebula (bool, optional): Boolean for whether this tile is in a nebula. Defaults to False.

            
            ##### These next ones are loaded by obj.load_system_data(). It's preferred if either all or none are passed when initializing.

            star (SystemStar, optional): A SystemTile object for the star in this system. Defaults to None.
            trade_hub (SystemTradeHub, optional): SystemTile object for a trade hub in this system, if there is no trade hub then pass None. Defaults to False, this is not None so it can automatically determine whether the system data has been loaded or not.
            asteroids (list[SystemAsteroid], optional): List of SystemTile objects for each tile in this system that is part of an asteroid belt. If there are no asteroids then pass an empty list. Defaults to None.
            planets (list[SystemPlanet], optional): A list of SystemTile objects for each planet in this system. Defaults to None.
            wormhole (SystemWormhole, optional): A SystemWormhole object for a wormhole in this system. Defaults to None.
        """
        self.galaxy_seed = galaxy_seed
        self.ascension = ascension
        self.guild = guild
        self.json_interface = json_interface

        self.xpos = xpos
        self.ypos = ypos
        self.position_id = xpos + 256 * ypos

        self.in_nebula = in_nebula

        self.system = system
        self.raw_system_data = raw_system_data

        self.system_radius = system_radius
        self.star = star
        self.asteroids = asteroids
        self.trade_hub = trade_hub
        self.planets = planets
        self.wormhole = wormhole

        if self.star is not None and \
                self.asteroids is not None and \
                not isinstance(self.trade_hub, bool) and \
                self.planets is not None:
            self.loaded = True
        else:
            self.loaded = False
        
        if isinstance(self.trade_hub, bool):
            self.trade_hub = None
    
    def __str__(self: typing.Self):
        return f"<GalaxyTile | x: {self.xpos} | y: {self.ypos} | system: {self.system} | in_nebula: {self.in_nebula}>"
    
    def __repr__(self: typing.Self):
        return self.__str__()
    
    def corruption_chance(self: typing.Self) -> float:
        """Returns the chance of a loaf becoming corrupted on this tile. Between 0 and 1."""
        return get_corruption_chance(self.xpos - MAP_RADIUS, self.ypos - MAP_RADIUS)
    
    ###############################################################################
    ##### Methods for the loading of system data.
    
    def smart_load(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            guild: typing.Union[discord.Guild, int, str],
            get_wormholes: bool = True
        ) -> None:
        """Loads the system data, only if it has not already been loaded."""
        if not self.loaded:
            self.load_system_data(
                json_interface = json_interface,
                guild = guild,
                get_wormholes = get_wormholes
            )
    
    def load_system_data(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            guild: typing.Union[discord.Guild, int, str],
            get_wormholes: bool = True
        ) -> None:
        """Loads the specific system data for this tile, including the star type, planets, asteroids, and trade hub level."""

        # If this tile is not a system, then there's nothing to load.
        if not self.system:
            return None
        
        if self.raw_system_data is None:
            raw_data = get_system_raw_data(
                json_interface = json_interface,
                guild = guild,
                galaxy_seed = self.galaxy_seed,
                ascension = self.ascension,
                xpos = self.xpos,
                ypos = self.ypos,
                load_wormholes = get_wormholes
            )

            self.raw_system_data = raw_data
        else:
            raw_data = self.raw_system_data

        # If the generated data is None, then return.
        # It should only be None if there isn't a system here, which should be prevented earlier, but just in case.
        if raw_data is None:
            return None
        
        # Set the system radius.
        self.system_radius = raw_data.get("radius")

        # Set self.star to the star. It's assuming there's a star here, which would be impressive if there wasn't.
        self.star = SystemStar(
            galaxy_seed = self.galaxy_seed,

            galaxy_xpos = self.xpos,
            galaxy_ypos = self.ypos,
            system_xpos = 0,
            system_ypos = 0,

            star_type = raw_data.get("star_type")
        )

        # Set the trade hub to get_trade_hub, which will return None if there is no trade hub here.
        self.trade_hub = get_trade_hub(
            json_interface = json_interface,
            guild = guild,
            ascension = self.ascension,
            galaxy_xpos = self.xpos,
            galaxy_ypos = self.ypos
        )

        if self.trade_hub is not None:
            self.trade_hub.galaxy_tile = self
        
        if raw_data.get("wormhole", {}).get("exists", False):
            wormhole_data = raw_data.get("wormhole", {})

            self.wormhole = SystemWormhole(
                galaxy_seed = self.galaxy_seed,

                galaxy_xpos = self.xpos,
                galaxy_ypos = self.ypos,
                system_xpos = wormhole_data.get("xpos", None),
                system_ypos = wormhole_data.get("ypos", None),

                wormhole_link_location = tuple(wormhole_data.get("link_galaxy", None))
            )
        
        # If there's an asteroid belt, then add an object for the asteroids it contains.
        if raw_data.get("asteroid_belt", False):
            asteroids = []

            asteroid_added = []
            distance = raw_data.get("asteroid_belt_distance", 2)

            for angle in range(360):
                asteroid_x = distance * math.cos(math.radians(angle))
                asteroid_y = distance * math.sin(math.radians(angle))

                # Make sure it hasn't added an asteroid at this point yet.
                if (asteroid_x, asteroid_y) in asteroid_added:
                    continue
                
                asteroids.append(SystemAsteroid(
                    galaxy_seed = self.galaxy_seed,

                    galaxy_xpos = self.xpos,
                    galaxy_ypos = self.ypos,
                    system_xpos = int(asteroid_x),
                    system_ypos = int(asteroid_y)
                ))

                asteroid_added.append((asteroid_x, asteroid_y))
            
            self.asteroids = asteroids
        elif len(raw_data.get("asteroid_belts", [])) > 0:
            asteroids = []

            for distance in raw_data.get("asteroid_belts", []):
                asteroid_added = []

                for angle in range(360):
                    asteroid_x = distance * math.cos(math.radians(angle))
                    asteroid_y = distance * math.sin(math.radians(angle))

                    # Make sure it hasn't added an asteroid at this point yet.
                    if (asteroid_x, asteroid_y) in asteroid_added:
                        continue
                    
                    asteroids.append(SystemAsteroid(
                        galaxy_seed = self.galaxy_seed,

                        galaxy_xpos = self.xpos,
                        galaxy_ypos = self.ypos,
                        system_xpos = int(asteroid_x),
                        system_ypos = int(asteroid_y)
                    ))

                    asteroid_added.append((asteroid_x, asteroid_y))
            
            self.asteroids = asteroids
        else:
            self.asteroids = list()
        
        # Setup the planets.
        planets = []

        for planet_data in raw_data.get("planets", []):
            planets.append(SystemPlanet(
                galaxy_seed = self.galaxy_seed,

                galaxy_xpos = self.xpos,
                galaxy_ypos = self.ypos,
                system_xpos = planet_data.get("xpos", 1),
                system_ypos = planet_data.get("ypos", 1),

                planet_type = values.get_emote(planet_data.get("type")),
                planet_distance = planet_data.get("distance"),
                planet_angle = planet_data.get("angle"),
                planet_deviation = planet_data.get("deviation")
            ))
        
        self.planets = planets
        
        self.loaded = True
    
    ###############################################################################
    ##### Utility methods.

    def _empty_system_tile(
            self: typing.Self,
            system_x: int,
            system_y: int
        ) -> SystemEmpty:
        """Returns an empty SystemTile object for the given system x and y in this galaxy tile.

        Args:
            system_x (int): The x position within this galaxy system to return the tile for.
            system_y (int): The y position within this galaxy system to return the tile for.

        Returns:
            SystemTile: The empty SystemTile object.
        """
        return SystemEmpty(
            galaxy_seed = self.galaxy_seed,
            galaxy_xpos = self.xpos,
            galaxy_ypos = self.ypos,
            system_xpos = system_x,
            system_ypos = system_y
        )
    
    ###############################################################################
    ##### Interaction methods.
    
    def get_emoji(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface
        ) -> str:
        """Returns an emoji that represents this galaxy tile."""

        # If this tile has a system, then get whatever
        if self.system:
            # Handle the 2x2 system:
            if (self.xpos, self.ypos) in ALTERNATE_CENTER or (self.xpos == MAP_RADIUS and self.ypos == MAP_RADIUS):
                if self.xpos == MAP_RADIUS and self.ypos == MAP_RADIUS: # Bottom right.
                    return "black_hole_bottom_right"
                elif self.xpos == MAP_RADIUS - 1 and self.ypos == MAP_RADIUS: # Bottom left.
                    return "black_hole_bottom_left"
                elif self.xpos == MAP_RADIUS and self.ypos == MAP_RADIUS - 1: # Top right.
                    return "black_hole_top_right"
                else:
                    return "black_hole_top_left"
            
            # Load the system data if it has not already been loaded.
            self.smart_load(json_interface=json_interface, guild=self.guild, get_wormholes=False)
            
            # Get the emoji of the star.
            return self.star.get_emoji()
        # If it gets here, then this tile is not a system.

        # If this tile is in a nebula, then return the nebula emoji.
        if self.in_nebula:
            return "nebula"
        
        # If this tile is not a system, and is not in a nebula return the empty emoji.
        return "background"
    
    def get_system_tile(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            system_x: int,
            system_y: int
        ) -> typing.Type[SystemTile]:
        """Returns a SystemTile subclass object for the given system x and y within this system.

        Args:
            system_x (int): The system x position within this system to get the SystemTile object for.
            system_y (int): The system y position within this system to get the SystemTile object for.

        Returns:
            typing.Type[SystemTile]: The found SystemTile subclass object. Note that this may be a SystemEmpty object, representing an empty tile.
        """

        # If this galaxy tile does not have a system, then any tile on the system map is going to be empty.
        if not self.system:
            return self._empty_system_tile(
                system_x = system_x,
                system_y = system_y
            )
        # Due to the previous if statement, if it gets here then this tile has a system.

        # Load the system data if it has not already been loaded.
        self.smart_load(json_interface=json_interface, guild=self.guild, get_wormholes=True)

        # If the given coords are (0, 0), then it's going to be the star.
        if system_x == 0 and system_y == 0:
            return self.star
        
        # If self.trade_hub is None, then this system does not have a trade hub.
        # So if it is *not* None, then check if the coordinates of it match up.
        if self.trade_hub is not None:
            if self.trade_hub.system_xpos == system_x and self.trade_hub.system_ypos == system_y:
                return self.trade_hub
        
        # Now, loop through the planets and see if any match up.
        for planet in self.planets:
            if planet.system_xpos == system_x and planet.system_ypos == system_y:
                return planet
        
        if self.wormhole is not None:
            if self.wormhole.system_xpos == system_x and self.wormhole.system_ypos == system_y:
                return self.wormhole
        
        # Lastly, check if any asteroids match up.
        for asteroid in self.asteroids:
            if asteroid.system_xpos == system_x and asteroid.system_ypos == system_y:
                return asteroid
        
        # If it's the edge of a system return a SystemEdge object.
        if math.hypot(system_x, system_y) >= self.system_radius + 2:
            return SystemEdge(
                galaxy_seed = self.galaxy_seed,
                galaxy_xpos = self.xpos,
                galaxy_ypos = self.ypos,
                system_xpos = system_x,
                system_ypos = system_y
            )
        
        # If nothing else triggers, then this tile is empty.
        return self._empty_system_tile(
            system_x = system_x,
            system_y = system_y
        )
    
    def save_to_database(
            self: typing.Self,
            json_interface: bread_cog.JSON_interface,
            map_data: dict = None
        ) -> dict:
        if map_data is None:
            map_data = json_interface.get_space_map_data(
                ascension_id = self.ascension,
                guild = self.guild
            )

        chunk = self.position_id // 8192
        sub_chunk = self.position_id % 8192

        if not has_seen_tile(
                json_interface = json_interface,
                guild = self.guild,
                ascension = self.ascension,
                xpos = self.xpos,
                ypos = self.ypos,
                map_data = map_data
            ):
            # If the tile hasn't been seen, update it.

            if "seen_tiles" not in map_data:
                map_data["seen_tiles"] = [0, 0, 0, 0, 0, 0, 0, 0]
            
            # Bitwise OR to update the bit without worrying about adding something and messing up other data.
            map_data["seen_tiles"][chunk] |= 2 ** sub_chunk

        if self.in_nebula and not in_nebula_database(
                json_interface = json_interface,
                guild = self.guild,
                ascension = self.ascension,
                xpos = self.xpos,
                ypos = self.ypos,
                map_data = map_data
            ):
            # If the tile has a nebula but the database doesn't think so, update it.

            if "nebula_tiles" not in map_data:
                map_data["nebula_tiles"] = [0, 0, 0, 0, 0, 0, 0, 0]

            # Bitwise OR to update the bit without worrying about adding something and messing up other data.
            map_data["nebula_tiles"][chunk] |= 2 ** sub_chunk
        
        if self.system:
            if str(self.position_id) not in map_data.get("system_data", {}):
                if self.raw_system_data is None:
                    self.load_system_data(json_interface, self.guild, True)
                
                if "system_data" in map_data:
                    map_data["system_data"][str(self.position_id)] = self.raw_system_data
                else:
                    map_data["system_data"] = {
                        str(self.position_id): self.raw_system_data
                    }
            
        # Set the map data to this.
        json_interface.set_space_map_data(
            ascension_id = self.ascension,
            guild = self.guild,
            new_data = map_data
        )
        return map_data

def get_corruption_chance(
        xpos: int,
        ypos: int,
    ) -> float:
    """Returns the chance of a loaf becoming corrupted for any point in the galaxy. Between 0 and 1.
    
    Subtract the map radius from a regular coordinate for this."""
    dist = math.hypot(xpos, ypos)

    # The band where the chance is 0 is between 80 and 87.
    if 80 <= dist <= 87:
        return 0.0
    
    # f\left(x\right)=\left\{x\le2:99,2\le x\le80:\left(\frac{\cos\left(\left(x-2\right)\frac{\pi}{78}\right)}{2}+0.5\right)99,80<x<87:0,87\le x\le241.81799:\left(\frac{\cos\left(\frac{\left(x-87\right)\pi}{154.8179858682464038403596020291203352621852869144970764695290884}\right)}{-2}+0.5\right)99,x>241.81799:99\right\}
    # f\left(x\right)=\left\{x\le2:99,2\le x\le80:\left(\frac{\cos\left(\left(x-2\right)\frac{\pi}{78}\right)}{2}+0.5\right)99,80<x<87:0,87\le x\le241.81799:\left(\frac{\cos\left(\frac{70055\left(x-87\right)\pi}{10845774}\right)}{-2}+0.5\right)99,x>241.81799:99\right\}
    # These two are roughly the same, but the second one doesn't have a random number in the middle.
    # Where `x` is the distance to (0, 0)
    # lmao

    # It's a piecewise function, so `if` statements are used.
    if dist <= 2:
        chance = 99
    elif dist <= 80:
        chance = (math.cos((dist - 2) * (math.pi / 78)) / 2 + 0.5) * 99
    elif dist <= 87:
        chance = 0
    elif dist <= 241.81799:
        # chance = (math.cos(((dist - 87) * math.pi) / 154.8179858682464038403596020291203352621852869144970764695290884) / -2 + 0.5) * 99
        chance = (math.cos((70055 * (dist - 87) * math.pi) / 10845774) / -2 + 0.5) * 99 # Functionally the same.
    else:
        chance = 99

    return chance / 100

def get_anarchy_corruption_chance(
        xpos: int,
        ypos: int
    ) -> float:
    """Returns the chance of an anarchy piece becoming corrupted for any point in the galaxy. Between 0 and 1."""
    regular = get_corruption_chance(xpos, ypos)

    return (regular ** 2) / 1.9602

            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def space_map(
        account: account.Bread_Account,
        json_interface: bread_cog.JSON_interface,
        mode: typing.Union[str, None] = None,
        analyze_position: str = None,
        other_settings: list[str] = None,
        dict_settings: dict[any, any] = None
    ) -> io.BytesIO:
    """Generates the map of a system or galaxy that can be sent in Discord.

    Args:
        account (account.Bread_Account): The account of the player calling the map.
        json_interface: (bread_cog.JSON_interface): The JSON interface.
        mode (typing.Union[str, None], optional): The mode to use. 'galaxy' for the galaxy map. Defaults to the system map for anything else. Defaults to None.
        analyze_position (str, optional): The location to hover the analysis on. Example: `a1` and `e5`. If None is passed it will not add the analysis. Only works on the system map. Defaults to None.
        other_settings (str, optional): Other settings provided by whoever is using the map. Defaults to None.
        dict_settings (dict[Any, Any], optional): Internal settings to be provided to the maps. Defaults to None.

    Returns:
        io.BytesIO: BytesIO object corresponding to the generated image.
    """
    if other_settings is None:
        other_settings = []
    if dict_settings is None:
        dict_settings = {}
        
    galaxy_seed = json_interface.get_ascension_seed(account.get_prestige_level(), guild=account.get("guild_id"))

    guild = account.get("guild_id")

    sensor_level = account.get("telescope_level")

    # Position in the galaxy.
    x_galaxy, y_galaxy = account.get_galaxy_location(json_interface=json_interface)

    radius = sensor_level + 2

    ascension = account.get_prestige_level()

    if mode == "galaxy" or mode == "g":
        return galaxy_map(
            json_interface = json_interface,
            guild = guild,
            galaxy_x = x_galaxy,
            galaxy_y = y_galaxy,
            galaxy_seed = galaxy_seed,
            ascension = ascension,
            telescope_level = sensor_level,
            radius = radius
        )
    elif mode == "full" or mode == "f":
        full_x = None
        full_y = None
        
        analyze_x = None
        analyze_y = None
        
        if len(other_settings) >= 2:
            try:
                full_x = bread_cog.parse_int(other_settings[0])
                full_y = bread_cog.parse_int(other_settings[1])
            except ValueError:
                pass # It failed to parse, so it's probably intended to be something.
        
        if len(other_settings) >= 4:
            try:
                analyze_x = bread_cog.parse_int(other_settings[2])
                analyze_y = bread_cog.parse_int(other_settings[3])
            except ValueError:
                pass # It failed to parse, so it's probably intended to be something.
                
        if full_x is not None and full_y is not None:
            return full_map_system(  
                json_interface = json_interface,
                ascension = ascension,
                guild = guild,
                galaxy_x = full_x,
                galaxy_y = full_y,
                analyze_x = analyze_x,
                analyze_y = analyze_y
            )
            
        return full_map_galaxy(
            json_interface = json_interface,
            ascension = ascension,
            guild = guild,
            home_x = x_galaxy,
            home_y = y_galaxy,
            dict_settings = dict_settings
        )
    else:
        # Position within a system.
        x_system, y_system = account.get_system_location()

        return system_map(
            json_interface = json_interface,
            guild = guild,
            galaxy_x = x_galaxy,
            galaxy_y = y_galaxy,
            system_x = x_system,
            system_y = y_system,
            galaxy_seed = galaxy_seed,
            ascension = ascension,
            telescope_level = sensor_level,
            radius = radius,
            analyze_position = analyze_position
        )

##########################################################################################
##### GALAXY MAP

def galaxy_map(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_x: int,
        galaxy_y: int,
        galaxy_seed: str,
        ascension: int,
        telescope_level: int,
        radius: int
    ) -> io.BytesIO:
    """Generates the galaxy map as an image.

    Args:
        json_interface (bread_cog.JSON_interface): The JSON interface.
        guild (typing.Union[discord.Guild, int, str]): The guild.
        galaxy_x (int): The x position in the galaxy.
        galaxy_y (int): The y position in the galaxy.
        galaxy_seed (str): The seed of the galaxy.
        ascension (int): The player's prestige level.
        telescope_level (int): The player's telescope level.
        radius (int): The radius of the visible area.

    Returns:
        io.BytesIO: BytesIO object corresponding to the generated image.
    """

    bottom_right = (galaxy_x + radius, galaxy_y + radius)
    top_left = (galaxy_x - radius, galaxy_y - radius)

    x_size = max(bottom_right[0], top_left[0]) - min(bottom_right[0], top_left[0]) + 1
    y_size = max(bottom_right[1], top_left[1]) - min(bottom_right[1], top_left[1]) + 1

    letters = "abcdefghijklmnopqrstuvwxyz"

    corners = [
        (0, 0), (0, 1), (1, 0),
        (0, y_size + 3), (1, y_size + 3), (0, y_size + 2),
        (x_size + 3, 0), (x_size + 2, 0), (x_size + 3, 1),
        (x_size + 3, y_size + 3), (x_size + 3, y_size + 2), (x_size + 2, y_size + 3),
    ]
    
    def size_check(x, y):
        return round(math.sqrt(x ** 2 + y ** 2)) <= telescope_level + 2
    
    img = Image.new(
        mode = "RGBA",
        size = ((x_size + 4) * 128, (y_size + 4) * 128),
        color = (0, 0, 0, 0)
    )

    def place(name, x, y):
        nonlocal img
        img.paste(EMOJI_IMAGES.get(name), (x * 128, y * 128), mask=EMOJI_IMAGES.get(name))


    for ypos in range(y_size + 4):
        for xpos in range(x_size + 4):

            if (xpos, ypos) in corners:
                place("border", xpos, ypos)
                continue

            # If we need to put in a letter.
            if ypos == y_size + 3 or ypos == 0:
                place(letters[xpos - 2], xpos, ypos)
                continue

            # If we need to put in a number.
            if xpos == x_size + 3 or xpos == 0:
                place(str(ypos - 1), xpos, ypos)
                continue
            
            if xpos == 1 or ypos == 1 or \
                xpos == x_size + 2 or ypos == y_size + 2:
                place("fog", xpos, ypos)
                continue
            
        
            # Whether this is in the visible area or not.
            if not size_check(xpos - 2 - radius, ypos - 2 - radius):
                place("fog", xpos, ypos)
                continue

            tile_object = get_galaxy_coordinate(
                json_interface = json_interface,
                guild = guild,
                galaxy_seed = galaxy_seed,
                ascension = ascension,
                xpos = xpos - 2 - radius + galaxy_x,
                ypos = ypos - 2 - radius + galaxy_y,
                load_data = False
            )
            
            # Place the background.
            # If something after this fires, that will be put on top of this.
            if tile_object.in_nebula:
                place("nebula", xpos, ypos)
            else:
                place("background", xpos, ypos)

            emoji = tile_object.get_emoji(json_interface)

            if emoji == "background":
                continue

            place(emoji, xpos, ypos)

    place("rocket", radius + 2, radius + 2)

    output = io.BytesIO()
    img.save(output, "png")
    output.seek(0)
        
    return output

##########################################################################################
##### SYSTEM MAP

def system_map(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_x: int,
        galaxy_y: int,
        system_x: int,
        system_y: int,
        galaxy_seed: str,
        ascension: int,
        telescope_level: int,
        radius: int,
        analyze_position: str = None
    ) -> io.BytesIO:
    """Generates the emojis for the space map.

    Args:
        json (bread_cog.JSON_interface): The JSON interface.
        galaxy_x (int): The x coordinate in the galaxy to center on.
        galaxy_y (int): The y coordinate in the galaxy to center on.
        system_x (int): The x coordinate in the system to center on.
        system_y (int): The y coordinate in the system to center on.
        galaxy_seed (str): The seed of the galaxy.
        ascension (int): The ascension of the galaxy.
        telescope_level (int): The telescope level the player has.
        radius (int): The radius of the viewable area.
        analyze_position (str, optional): The location to hover the analysis on. Example: `a1` and `e5`. If None is passed it will not add the analysis. Defaults to None.

    Returns:
        io.BytesIO: BytesIO object corresponding to the generated image.
    """
    
    bottom_right = (system_x + radius, system_y + radius)
    top_left = (system_x - radius, system_y - radius)

    x_size = max(bottom_right[0], top_left[0]) - min(bottom_right[0], top_left[0]) + 1
    y_size = max(bottom_right[1], top_left[1]) - min(bottom_right[1], top_left[1]) + 1

    fill_emoji = "fog"
    border_emoji = "border"
    blocker = "blocker"

    letters = "abcdefghijklmnopqrstuvwxyz"

    corners = [
        (0, 0), (0, 1), (1, 0),
        (0, y_size + 3), (1, y_size + 3), (0, y_size + 2),
        (x_size + 3, 0), (x_size + 2, 0), (x_size + 3, 1),
        (x_size + 3, y_size + 3), (x_size + 3, y_size + 2), (x_size + 2, y_size + 3),
    ]
    
    def size_check(x, y):
        return round(math.sqrt(x ** 2 + y ** 2)) <= telescope_level + 2

    visible_coordinates = []

    def get_fill_emoji(grid_x, grid_y):
        nonlocal visible_coordinates

        # Handling the corners.
        if (grid_x, grid_y) in corners:
            return border_emoji
        
        # The numbers and letters.
        if grid_y == 0 or grid_y == y_size + 3:
            return letters[grid_x - 2]
        
        if grid_x == 0 or grid_x == x_size + 3:
            return str(grid_y - 1)
        
        # The ring of fog emojis just inside the outer blue border.
        if grid_x == 1 or grid_x == x_size + 2:
            return fill_emoji
        
        if grid_y == 1 or grid_y == y_size + 2:
            return fill_emoji
        
        # Whether this is in the visible area or not.
        if size_check(grid_x - 2 - radius, grid_y - 2 - radius):
            visible_coordinates.append(
                (grid_x - 2 - radius + system_x,
                grid_y - 2 - radius + system_y)
            )
            return "background"
        
        # If nothing activates, fog emoji.
        return fill_emoji
    
    grid = [[get_fill_emoji(grid_x, grid_y) for grid_x in range(x_size + 4)] for grid_y in range(y_size + 4)]

    ##### Placing the system features. #####

    system_data = get_galaxy_coordinate(
        json_interface = json_interface,
        guild = guild,
        galaxy_seed = galaxy_seed,
        ascension = ascension,
        xpos = galaxy_x,
        ypos = galaxy_y,
        load_data = False
    )

    # If this location is not a system, place the rocket in the middle and return.
    if system_data.system:    
        system_data.load_system_data(json_interface=json_interface, guild=guild, get_wormholes=True)

        # Place down the border.
        system_radius = system_data.system_radius

        for tile_y in range(y_size):
            for tile_x in range(x_size):
                if grid[tile_y + 2][tile_x + 2] == fill_emoji:
                    continue
                
                if math.hypot(tile_x + top_left[0], tile_y + top_left[1]) >= system_radius + 2:
                    grid[tile_y + 2][tile_x + 2] = blocker
        
        # Star
        star_x = system_data.star.system_xpos
        star_y = system_data.star.system_ypos

        if (star_x, star_y) in visible_coordinates:
            grid[star_y + 2 - system_y + radius][star_x + 2 - system_x + radius] = system_data.star.get_emoji()
        
        # Asteroids (if there are any)
        if system_data.asteroids is not None:
            for asteroid in system_data.asteroids:
                if (asteroid.system_xpos, asteroid.system_ypos) in visible_coordinates:
                    grid[asteroid.system_ypos + 2 - system_y + radius][asteroid.system_xpos + 2 - system_x + radius] = asteroid.get_emoji()
        
        # Planets
        for planet in system_data.planets:
            if (planet.system_xpos, planet.system_ypos) in visible_coordinates:
                grid[planet.system_ypos + 2 - system_y + radius][planet.system_xpos + 2 - system_x + radius] = planet.get_emoji()
                
        # Potential trade hub.
        if system_data.trade_hub is not None:
            trade_hub_x = system_data.trade_hub.system_xpos
            trade_hub_y = system_data.trade_hub.system_ypos

            if (trade_hub_x, trade_hub_y) in visible_coordinates:
                grid[trade_hub_y + 2 - system_y + radius][trade_hub_x + 2 - system_x + radius] = system_data.trade_hub.get_emoji()
        
        # Potential wormhole.
        if system_data.wormhole is not None:
            wormhole_x = system_data.wormhole.system_xpos
            wormhole_y = system_data.wormhole.system_ypos

            if (wormhole_x, wormhole_y) in visible_coordinates:
                grid[wormhole_y + 2 - system_y + radius][wormhole_x + 2 - system_x + radius] = system_data.wormhole.get_emoji()

    # Now, render the image.
    
    img = Image.new(
        mode = "RGBA",
        size = ((x_size + 4) * 128, (y_size + 4) * 128),
        color = (0, 0, 0, 0)
    )
    imgdraw = ImageDraw.Draw(img)

    def place(name, x, y):
        nonlocal img
        img.paste(EMOJI_IMAGES.get(name), (x * 128, y * 128), mask=EMOJI_IMAGES.get(name))

    for ypos, ydata in enumerate(grid):
        for xpos, emoji in enumerate(ydata):
            # If it's part of the map, place a background.
            if not emoji == fill_emoji:
                place("background", xpos, ypos)

            place(emoji, xpos, ypos)

    # Add the rocket.
    place("rocket", radius + 2, radius + 2)
    
    if analyze_position is not None:
        xpos = letters.index(analyze_position[0])
        ypos = int(analyze_position[1:]) - 1
        
        width = 50

        imgdraw.rectangle(
            xy = (
               (xpos + 2) * 128 - width,
               (ypos + 2) * 128 - width,
               (xpos + 3) * 128 + width,
               (ypos + 3) * 128 + width
            ),
            outline = (255, 0, 0),
            width = width
        )

        imgdraw.line(
            xy = (
               (xpos + 2) * 128 - 5,
               (ypos + 2.5) * 128,
               0,
               (ypos + 2.5) * 128
            ),
            fill = (255, 0, 0),
            width = width
        )

        imgdraw.line(
            xy = (
               width / 2 - 1,
               0,
               width / 2 - 1,
               (ypos + 2.5) * 128
            ),
            fill = (255, 0, 0),
            width = width
        )

    output = io.BytesIO()
    img.save(output, "png")
    output.seek(0)
        
    return output

def full_map_galaxy(
        json_interface: bread_cog.JSON_interface,
        ascension: int,
        guild: typing.Union[discord.Guild, int, str],
        home_x: int,
        home_y: int,
        render_grid: bool = True,
        dict_settings: dict[any, any] = None
    ) -> io.BytesIO:
    if dict_settings is None:
        dict_settings = {}
    
    bubble_data = dict_settings.get("bubbles", None)
    
    # Generate the data if it hasn't been passed.
    if bubble_data is None:
        bubble_data = generate_trade_hub_bubbles(
            json_interface = json_interface,
            ascension = ascension,
            guild = guild
        )
    
    bit_check = 1 << (home_x + 256 * home_y)
    
    for bubble in bubble_data:
        if bubble & bit_check:
            break
    else:
        # If there's no bubble found, use the entire map so at least something is shown.
        bubble = MASK_LEFT & MASK_RIGHT
    
    map_data = json_interface.get_space_map_data(
        ascension_id = ascension,
        guild = guild
    )
    
    hub_mask = generate_trade_hub_mask(
        json_interface = json_interface,
        ascension = ascension,
        guild = guild
    )
        
    def convert_index(
            number_index: int,
            place: int
        ) -> tuple[int]:
        """Converts an index in the map to a 0-65535 index."""
        return number_index * 8192 + place

    img = Image.new("RGB", (256, 256), UNEXPLORED_COLOR)

    left = 256
    right = 0
    bottom = 256
    top = 0

    for seen_index, seen_number in enumerate(map_data.get("seen_tiles", [])):
        for bit in utility.iterate_through_bits(seen_number):
            index = convert_index(seen_index, bit)
            
            if not bool((1 << index) & bubble):
                continue
            
            bit_x, bit_y = index_to_coordinate(index)
            
            img.putpixel((bit_x, bit_y), EXPLORED_COLOR)
            
            if bit_x < left:
                left = bit_x
            if bit_x > right:
                right = bit_x
            if bit_y < bottom:
                bottom = bit_y
            if bit_y > top:
                top = bit_y
            
    for seen_index, seen_number in enumerate(map_data.get("nebula_tiles", [])):
        for bit in utility.iterate_through_bits(seen_number):
            index = convert_index(seen_index, bit)
            
            if not bool((1 << index) & bubble):
                continue
            
            bit_x, bit_y = index_to_coordinate(index)
            
            img.putpixel((bit_x, bit_y), NEBULA_COLOR)

    for tile_key, info in map_data.get("system_data").items():
        index = int(tile_key)
        code = 1 << index
        
        if not bool(code & bubble):
            continue
        
        x_coord, y_coord = index_to_coordinate(index)
        
        # Account for the 2x2 system.
        if x_coord == 128 and y_coord == 128:
            # The 2x2 system always spawns with a hub, so always use that color.
            img.putpixel((127, 127), STAR_COLORS_WITH_HUB["supermassive_black_hole"])
            img.putpixel((127, 128), STAR_COLORS_WITH_HUB["supermassive_black_hole"])
            img.putpixel((128, 127), STAR_COLORS_WITH_HUB["supermassive_black_hole"])
        
        star_type = info.get("star_type", "star1")
        
        if code & hub_mask:
            color_data = STAR_COLORS_WITH_HUB
        else:
            color_data = STAR_COLORS_NO_HUB
        
        img.putpixel((x_coord, y_coord), color_data[star_type])

    ######################################
    max_size = max(right - left, top - bottom)
    
    # as max_size goes to 240, this should go to 10
    # but values below idk, 40? should be 50
    
    if max_size < 40:
        size_multiplier = 50
    else:
        size_multiplier = 10 * (5 - int(((max_size - 40) * 4) / 200))
    
    size_multiplier = min(max(size_multiplier, 10), 50)

    text_multiplier = size_multiplier // 10

    img = img.crop((left, bottom, right + 1, top + 1))
    img = img.resize((img.size[0] * size_multiplier, img.size[1] * size_multiplier), resample=Image.Resampling.NEAREST)

    draw = ImageDraw.Draw(img)
    
    GRID_COLOR = (64, 64, 64)

    if render_grid:
        for x_coordinate in range(right - left):
            draw.line([(x_coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2), 0), (x_coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2), img.size[1])], GRID_COLOR, width=text_multiplier)
        
        for y_coordinate in range(top - bottom):
            draw.line([(0, y_coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2)), (img.size[0], y_coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2))], GRID_COLOR, width=text_multiplier)
            
    ######################################
    # Render text.
    
    TEXT_WIDTH = 5

    offset = (3 * (TEXT_WIDTH + 1) + 1) * text_multiplier

    img_text = Image.new("RGBA", (img.size[0] + offset, img.size[1] + offset), MAP_TEXT_BACKGROUND)
    img_text.paste(img, (offset, offset))
    
    def char_horizontal(xpos, ypos, num):
        for bit in utility.iterate_through_bits(num):
            for x in range(text_multiplier):
                for y in range(text_multiplier):
                    img_text.putpixel((text_multiplier * (4 - bit % 5) + x + xpos, text_multiplier * (7 - bit // 5) + y + ypos), MAP_TEXT_COLOR)

    def draw_horizontal(vertical: int, number: int) -> None:
        skip = 3 - len(str(number))
        for char_index, char in enumerate(str(number)):
            char_horizontal((char_index + skip) * text_multiplier * (TEXT_WIDTH + 1) + 1, vertical * size_multiplier + offset + 1, FULL_MAP_NUMBER_DATA[char])
            
    def char_vertical(xpos, ypos, num):
        for bit in utility.iterate_through_bits(num):
            for x in range(text_multiplier):
                for y in range(text_multiplier):
                    img_text.putpixel((text_multiplier * (7 - bit // 5) + x + xpos, text_multiplier * (bit % 5) + y + ypos), MAP_TEXT_COLOR)

    def draw_vertical(horizontal: int, number: int) -> None:
        for char_index, char in enumerate(str(number)):
            char_vertical(horizontal * size_multiplier + offset + 1, (2 - (char_index)) * text_multiplier * (TEXT_WIDTH + 1) + 1, FULL_MAP_NUMBER_DATA[char])

    for index, ypos in enumerate(range(top - bottom + 1)):
        draw_horizontal(index, ypos + bottom)
        
    for index, xpos in enumerate(range(right - left + 1)):
        draw_vertical(index, xpos + left)
        
    ######################################
    # Render the "you are here" thingy.
    
    draw = ImageDraw.Draw(img_text)
    
    top_x = offset + size_multiplier * (home_x - left)
    top_y = offset + size_multiplier * (home_y - bottom)
    
    base_width = int(size_multiplier // 2.5)
    quarter = base_width // 4
    
    draw.rectangle(
        [
            (top_x - base_width, top_y - base_width),
            (top_x + size_multiplier + base_width - size_multiplier // 10 - 1, top_y + size_multiplier + base_width - size_multiplier // 10 - 1)
        ],
        fill = None,
        outline = GRID_COLOR,
        width = base_width
    )
    
    draw.rectangle(
        [
            (top_x - base_width + quarter, top_y - base_width + quarter),
            (top_x + size_multiplier + base_width - quarter - size_multiplier // 10 - 1, top_y + size_multiplier + base_width - quarter - size_multiplier // 10 - 1)
        ],
        fill = None,
        outline = (255, 0, 0),
        width = base_width // 2
    )
    
    ######################################

    output = io.BytesIO()
    img_text.save(output, "png")
    output.seek(0)
        
    return output

def full_map_system(
        json_interface: bread_cog.JSON_interface,
        ascension: int,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_x: int,
        galaxy_y: int,
        analyze_x: int | None = None,
        analyze_y: int | None = None,
        render_grid: bool = True
    ) -> io.BytesIO:
    coordinate = get_galaxy_coordinate(
        json_interface = json_interface,
        guild = guild,
        galaxy_seed = json_interface.get_ascension_seed(ascension, guild),
        ascension = ascension,
        xpos = galaxy_x,
        ypos = galaxy_y,
        load_data = True
    )
    system_data = coordinate.raw_system_data
    
    if system_data is None:
        system_data = {}

    radius = system_data.get("radius", 15) + 2

    background_shade = 0

    size = radius * 2 + 1
    img = Image.new("RGB", (size, size), (background_shade, background_shade, background_shade, 255))
    
    if coordinate.system:
        ascension_data = json_interface.get_space_ascension(ascension, guild)
    
        # This is all seen Trade Hubs.
        trade_hub_data = ascension_data.get("trade_hubs", {})
        
        in_nebula = in_nebula_database(
            json_interface = json_interface,
            guild = guild,
            ascension = ascension,
            xpos = galaxy_x,
            ypos = galaxy_y
        )
        
        if in_nebula:
            border_color = BORDER_NEBULA
        else:
            border_color = BORDER_REGULAR
    
        for xpos in range(size):
            for ypos in range(size):
                if math.hypot(xpos - radius, ypos - radius) >= radius:
                    img.putpixel((xpos, ypos), border_color)

        # Only include the non-hub colors here.
        img.putpixel((radius, radius), STAR_COLORS_NO_HUB[system_data["star_type"]])

        # Asteroids.
        if system_data.get("asteroid_belt", False):
            asteroid_added = []
            distance = system_data.get("asteroid_belt_distance", 2)

            for angle in range(360):
                asteroid_x = distance * math.cos(math.radians(angle))
                asteroid_y = distance * math.sin(math.radians(angle))

                # Make sure it hasn't added an asteroid at this point yet.
                if (asteroid_x, asteroid_y) in asteroid_added:
                    continue
                
                img.putpixel((int(asteroid_x) + radius, int(asteroid_y) + radius), ASTEROID_COLOR)   

                asteroid_added.append((asteroid_x, asteroid_y))
        elif len(system_data.get("asteroid_belts", [])) > 0:
            for distance in system_data.get("asteroid_belts", []):
                asteroid_added = []

                for angle in range(360):
                    asteroid_x = distance * math.cos(math.radians(angle))
                    asteroid_y = distance * math.sin(math.radians(angle))

                    # Make sure it hasn't added an asteroid at this point yet.
                    if (asteroid_x, asteroid_y) in asteroid_added:
                        continue
                    
                    img.putpixel((int(asteroid_x) + radius, int(asteroid_y) + radius), ASTEROID_COLOR)   

                    asteroid_added.append((asteroid_x, asteroid_y))

        for planet_data in system_data.get("planets", []):
            img.putpixel((round(planet_data.get("xpos", 1)) + radius, round(planet_data.get("ypos", 1)) + radius), PLANET_COLORS[values.get_emote(planet_data.get("type")).name])
            
        if system_data["wormhole"]["exists"]:
            img.putpixel(
                (
                    system_data["wormhole"]["xpos"] + radius,
                    system_data["wormhole"]["ypos"] + radius
                ),
                WORMHOLE_COLOR
            )

        # Trade hub.
        if system_data.get("trade_hub", {}).get("exists", False) or trade_hub_data.get(f"{galaxy_x} {galaxy_y}", {}).get("level", 0) > 0:
            if system_data.get("trade_hub", {}).get("exists", False):
                trade_hub_x = system_data.get("trade_hub", {}).get("xpos", False)
                trade_hub_y = system_data.get("trade_hub", {}).get("ypos", False)
            else:
                trade_hub_x, trade_hub_y = trade_hub_data.get(f"{galaxy_x} {galaxy_y}", {}).get("location", 0)
                
            img.putpixel((trade_hub_x + radius, trade_hub_y + radius), TRADE_HUB_COLOR)

    ##################################################

    size_multiplier = 50
    text_multiplier = size_multiplier // 10

    img = img.resize((img.size[0] * size_multiplier, img.size[1] * size_multiplier), resample=Image.Resampling.NEAREST)

    draw = ImageDraw.Draw(img)

    if render_grid:
        grid_color = (64, 64, 64, 255)
        
        for coordinate in range(size):
            draw.line([(coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2), 0), (coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2), img.size[1])], grid_color, width=text_multiplier)
            draw.line([(0, coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2)), (img.size[0], coordinate * size_multiplier + (size_multiplier - 1) - (text_multiplier // 2))], grid_color, width=text_multiplier)

    ##################################################
    TEXT_WIDTH = 5

    offset = (3 * (TEXT_WIDTH + 1) + 1) * text_multiplier

    img_text = Image.new("RGBA", (img.size[0] + offset, img.size[1] + offset), MAP_TEXT_BACKGROUND)
    img_text.paste(img, (offset, offset))

    def char_horizontal(xpos, ypos, num):
        for bit in utility.iterate_through_bits(num):
            for x in range(text_multiplier):
                for y in range(text_multiplier):
                    img_text.putpixel((text_multiplier * (4 - bit % 5) + x + xpos, text_multiplier * (7 - bit // 5) + y + ypos), MAP_TEXT_COLOR)

    def draw_horizontal(vertical: int, number: int) -> None:
        skip = 3 - len(str(number))
        for char_index, char in enumerate(str(number)):
            char_horizontal((char_index + skip) * text_multiplier * (TEXT_WIDTH + 1) + 1, vertical * size_multiplier + offset + 1, FULL_MAP_NUMBER_DATA[char])
            
    def char_vertical(xpos, ypos, num):
        for bit in utility.iterate_through_bits(num):
            for x in range(text_multiplier):
                for y in range(text_multiplier):
                    img_text.putpixel((text_multiplier * (7 - bit // 5) + x + xpos, text_multiplier * (bit % 5) + y + ypos), MAP_TEXT_COLOR)

    def draw_vertical(horizontal: int, number: int) -> None:
        for char_index, char in enumerate(str(number)):
            char_vertical(horizontal * size_multiplier + offset + 1, (2 - (char_index)) * text_multiplier * (TEXT_WIDTH + 1) + 1, FULL_MAP_NUMBER_DATA[char])

    for index, ypos in enumerate(range(size)):
        draw_horizontal(index, ypos - radius)
        
    for index, xpos in enumerate(range(size)):
        draw_vertical(index, xpos - radius)
    
    # Draw the analysis lines if needed.
    if analyze_x is not None and analyze_y is not None:
        draw = ImageDraw.Draw(img_text)
        
        # Limit where the analysis is.
        analyze_x = min(max(analyze_x, -radius), radius)
        analyze_y = min(max(analyze_y, -radius), radius)
        
        top_left_x = (analyze_x + radius) * size_multiplier + offset
        top_left_y = (analyze_y + radius) * size_multiplier + offset
        
        # White lines.
        draw.rectangle(
            (
                (top_left_x - 20, top_left_y - 20),
                (top_left_x + size_multiplier + 14, top_left_y + size_multiplier + 14),
            ),
            fill = None,
            outline = (255, 255, 255),
            width = 20
        )
        
        draw.line(
            (
                (top_left_x - 5, top_left_y + size_multiplier // 2 - 2),
                (0, top_left_y + size_multiplier // 2 - 2),
            ),
            fill = (255, 255, 255),
            width = 20
        )
        
        draw.line(
            (
                (10, top_left_y + size_multiplier // 2 + 2),
                (10, 0),
            ),
            fill = (255, 255, 255),
            width = 20
        )
        
        # Red lines.
        draw.rectangle(
            (
                (top_left_x - 15, top_left_y - 15),
                (top_left_x + size_multiplier + 9, top_left_y + size_multiplier + 9),
            ),
            fill = None,
            outline = (255, 0, 0),
            width = 10
        )
        
        draw.line(
            (
                (top_left_x - 6, top_left_y + size_multiplier // 2 - 2),
                (5, top_left_y + size_multiplier // 2 - 2),
            ),
            fill = (255, 0, 0),
            width = 10
        )
        
        draw.line(
            (
                (10, top_left_y + size_multiplier // 2 + 2),
                (10, 0),
            ),
            fill = (255, 0, 0),
            width = 10
        )

    output = io.BytesIO()
    img_text.save(output, "png")
    output.seek(0)
        
    return output

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def index_to_coordinate(index: int) -> tuple[int]:
    """Converts an index in a map number to the (x, y) coordinate."""
    return index % MAP_SIZE, index // MAP_SIZE

def generate_trade_hub_bubbles(
        json_interface: bread_cog.JSON_interface,
        ascension: int,
        guild: typing.Union[discord.Guild, int, str],
    ) -> list[int]:
    ascension_data = json_interface.get_space_ascension(ascension, guild)
    
    # This is all seen Trade Hubs.
    trade_hub_data = ascension_data.get("trade_hubs", {})
    
    all_trade_hubs = []
    have_increased_range = 0
    
    for key, data in trade_hub_data.items():
        x, y = key.split(" ")
        all_trade_hubs.append(int(x) + 256 * int(y))
        
        if data.get("upgrades", {}).get("detection_array", {}).get("level", 0) > 0:
            have_increased_range |= 1 << (int(x) + 256 * int(y))
    
    # # Uncomment to use trade hubs that haven't been found yet. 
    # # This shouldn't be enabled in-game but can be fun to look at in a testing environment.
    # map_data = json_interface.get_space_map_data(ascension, guild)
    # for key, data in map_data.get("system_data", {}).items():
    #     if data.get("trade_hub", {}).get("exists", False):
    #         if int(key) not in all_trade_hubs:
    #             all_trade_hubs.append(int(key))
    
    ################################
    
    groups = []

    for key in all_trade_hubs:
        base_x, base_y = index_to_coordinate(key)
        self_range = BASE_COMMUNICATION_RADIUS + (BASE_COMMUNICATION_RADIUS * bool((1 << key) & have_increased_range))
            
        added = []
        for other_index, other_data in enumerate(groups):
            for other_spot in other_data:
                other_x, other_y = index_to_coordinate(other_spot)
                other_range = BASE_COMMUNICATION_RADIUS + (BASE_COMMUNICATION_RADIUS * bool((1 << other_spot) & have_increased_range))
                
                if math.hypot(base_x - other_x, base_y - other_y) <= (self_range + other_range):
                    groups[other_index].append(key)
                    added.append(other_index)
                    
                    # If we've found one we don't need to continue searching this group.
                    break
        
        if len(added) > 1:
            copied = groups.copy()
            fill = []
            for group_id, group in enumerate(groups):
                if group_id in added:
                    fill.extend(group)
            
            # Remove duplicates.
            fill = list(set(fill))
            
            for group_id in added:
                copied.remove(groups[group_id])
            
            copied.append(fill)
            
            groups = copied
        elif len(added) == 0:
            groups.append([key])
        
    ################################

    group_data = [0] * len(groups)

    for key in all_trade_hubs:
        base_x, base_y = index_to_coordinate(key)
        
        group = None
        for gid, g in enumerate(groups):
            if key in g:
                group = gid
                break
        
        if group is None:
            continue
        
        group_data[group] |= make_circle_mask(int(base_x), int(base_y), radius=(BASE_COMMUNICATION_RADIUS + (BASE_COMMUNICATION_RADIUS * bool((1 << key) & have_increased_range))))
    
    return group_data
    
def generate_galaxy_seed() -> str:
    """Generates a random new galaxy seed."""
    return "{:064x}".format(random.randrange(16 ** 64)) # Random 64 digit hexadecimal number.

def has_seen_tile(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        ascension: int,
        xpos: int,
        ypos: int,
        map_data: dict = None
    ) -> bool:
    """Returns a boolean for whether the given tile has been seen yet.

    Args:
        json_interface (bread_cog.JSON_interface): The Bread Cog's JSON interface.
        guild (typing.Union[discord.Guild, int, str]): The guild to get the data for.
        ascension (int): The ascension to get the data for.
        xpos (int): The x position of the tile to check.
        ypos (int): The x position of the tile to check.
        map_data (dict, optional): Already fetched map data, to avoid getting the data from the JSON interface multiple times. Defaults to None.

    Returns:
        bool: Whether the given tile coordinates has been seen before.
    """
    if map_data is None:
        map_data = json_interface.get_space_map_data(
            ascension_id = ascension,
            guild = guild
        )

    seen_data = map_data.get("seen_tiles", [0, 0, 0, 0, 0, 0, 0, 0])

    tile_id = xpos + 256 * ypos

    chunk = tile_id // 8192
    
    # Bitwise AND to get the bit on its own.
    return bool(seen_data[chunk] & 2 ** (tile_id % 8192))

def in_nebula_database(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        ascension: int,
        xpos: int,
        ypos: int,
        map_data: dict = None
    ) -> bool:
    """Returns a boolean for whether the given tile has been marked as in a nebula in the database.
    
    This will not generate anything, only check already generated data. Due to this, it should only be used if `has_seen_tile()` is also True.

    Args:
        json_interface (bread_cog.JSON_interface): The Bread Cog's JSON interface.
        guild (typing.Union[discord.Guild, int, str]): The guild to get the data for.
        ascension (int): The ascension to get the data for.
        xpos (int): The x position of the tile to check.
        ypos (int): The x position of the tile to check.
        map_data (dict, optional): Already fetched map data, to avoid getting the data from the JSON interface multiple times. Defaults to None.

    Returns:
        bool: Whether the given tile coordinates are marked as in a nebula in the database.
    """
    if map_data is None:
        map_data = json_interface.get_space_map_data(
            ascension_id = ascension,
            guild = guild
        )

    seen_data = map_data.get("nebula_tiles", [0, 0, 0, 0, 0, 0, 0, 0])

    tile_id = xpos + 256 * ypos

    chunk = tile_id // 8192
    
    # Bitwise AND to get the bit on its own.
    return bool(seen_data[chunk] & 2 ** (tile_id % 8192))

def generate_trade_hub_mask(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        ascension: int
    ) -> int:
    """Generates an integer mask for every generated tile in the galaxy that has a Trade Hub on it.

    Args:
        json_interface (bread_cog.JSON_interface): The Bread Cog's JSON interface.
        guild (typing.Union[discord.Guild, int, str]): The guild this is taking place in.
        ascension (int): The ascension to get the data for.

    Returns:
        int: The generated mask.
    """
    ascension_data = json_interface.get_space_ascension(ascension, guild)
    
    # This is all seen Trade Hubs.
    trade_hub_data = ascension_data.get("trade_hubs", {})
    
    map_data = json_interface.get_space_map_data(
        ascension_id = ascension,
        guild = guild
    )
    
    out = 0
    
    for hub in trade_hub_data:
        hub_x, hub_y = hub.split(" ")
        
        point = 1 << (int(hub_x) + 256 * int(hub_y))
        out |= point
    
    for system_id, data in map_data.get("system_data", {}).items():
        hub = data.get("trade_hub", {})
        
        if not hub.get("exists", False):
            continue
        
        point = 1 << int(system_id)
        out |= point
        
    return out
        
def get_system_raw_data(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_seed: str,
        ascension: int,
        xpos: int,
        ypos: int,
        load_wormholes: bool = True,
        map_data: dict = None
    ) -> dict:
    """Gets the raw data for a system either from the database if it's there or by generating it.

    Args:
        json_interface (bread_cog.JSON_interface): The JSON interface to use.
        guild (typing.Union[discord.Guild, int, str]): The guild to get the data for.
        galaxy_seed (str): The seed of the galaxy.
        ascension (int): The ascension for the data.
        xpos (int): The galaxy x position of the tile to generate.
        ypos (int): The galaxy y position of the tile to generate.
        load_wormholes (bool, optional): Whether to load the wormholes in the system if there are any. Defaults to True.
        map_data (dict, optional): An already fetched copy of the map data to avoid fetching it multiple times. Defaults to None.

    Returns:
        dict: The raw data for the system.
    """
    if (xpos, ypos) in ALTERNATE_CENTER:
        xpos = MAP_RADIUS
        ypos = MAP_RADIUS

    if map_data is None:
        map_data = json_interface.get_space_map_data(
            ascension_id = ascension,
            guild = guild
        )

    tile_id = xpos + 256 * ypos

    if str(tile_id) in map_data.get("system_data", {}):
        # If it's already in the database, get it from there.
        return map_data.get("system_data", {}).get(str(tile_id))
    else:
        # Generate the data for the system.
        return generation.generate_system(
            galaxy_seed = galaxy_seed,
            galaxy_xpos = xpos,
            galaxy_ypos = ypos,
            get_wormholes = load_wormholes
        )


def get_galaxy_coordinate(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_seed: str,
        ascension: int,
        xpos: int,
        ypos: int,
        load_data: bool = False
    ) -> GalaxyTile:
    """Returns a GalaxyTile object for this location within the galaxy the given account is on.

    Args:
        json (bread_cog.JSON_interface): The JSON interface to use.
        galaxy_seed (str): The galaxy seed to use.
        ascension (int): The ascension of this galaxy.
        xpos (int): The x position of the coordinate to get.
        ypos (int): The y position of the coordinate to get.
        load_data (bool, optional): Whether to load the system data when making the GalaxyTile object. If the tile is not already in
           the database and needs to be generated the data will be loaded no matter what this is. Defaults to False.
    
    Returns:
        GalaxyTile: A GalaxyTile object for the coordinate.
    """
    # If the tile is outside the galaxy, return an empty GalaxyTile.
    if not generation.position_check(xpos - MAP_RADIUS, ypos - MAP_RADIUS):
        return GalaxyTile(
            galaxy_seed = galaxy_seed,
            ascension = ascension,
            guild = guild,
            xpos = xpos,
            ypos = ypos,
            system = False,
            in_nebula = False,
            json_interface = json_interface
        )
    
    # To handle the 2x2 system at the center of the map.
    # The map data only exists at (MAP_RADIUS, MAP_RADIUS),
    # so if the coordinate being called is any of the other
    # three tiles, change it to where the data is.
    old_x = None
    old_y = None
    if (xpos, ypos) in ALTERNATE_CENTER:
        old_x = xpos
        old_y = ypos

        xpos = MAP_RADIUS
        ypos = MAP_RADIUS
    
    map_data = json_interface.get_space_map_data(
        ascension_id = ascension,
        guild = guild
    )

    if has_seen_tile(
            json_interface = json_interface,
            guild = guild,
            ascension = ascension,
            xpos = xpos,
            ypos = ypos,
            map_data = map_data
        ):
        # The tile has been seen, so get the data from storage instead of generating it again.
        
        in_nebula = in_nebula_database(
            json_interface = json_interface,
            guild = guild,
            ascension = ascension,
            xpos = xpos,
            ypos = ypos,
            map_data = map_data
        )

        tile_id = xpos + 256 * ypos

        system = str(tile_id) in map_data.get("system_data", {})

        out = GalaxyTile(
            galaxy_seed = galaxy_seed,
            ascension = ascension,
            guild = guild,
            xpos = xpos,
            ypos = ypos,
            system = system,
            in_nebula = in_nebula,
            json_interface = json_interface
        )

        if load_data:
            out.load_system_data(json_interface, guild, True)
        
        if old_x is not None:
            out.xpos = old_x
            out.ypos = old_y
        
        return out


    #####################################################
    # If it's not in the database, generate it.

    position_data = generation.galaxy_single(
        galaxy_seed = galaxy_seed,
        x = xpos,
        y = ypos
    )

    in_nebula = position_data.get("in_nebula", False)

    is_system = position_data.get("system", False)

    out = GalaxyTile(
        galaxy_seed = galaxy_seed,
        ascension = ascension,
        guild = guild,
        xpos = xpos,
        ypos = ypos,
        system = is_system,
        in_nebula = in_nebula,
        json_interface = json_interface
    )
    
    # Save the new data.
    out.save_to_database(json_interface)

    if not is_system:
        return out

    if load_data:
        out.load_system_data(json_interface=json_interface, guild=guild, get_wormholes=True)
        
    if old_x is not None:
        out.xpos = old_x
        out.ypos = old_y

    return out

def get_system_coordinate(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        galaxy_seed: str,
        ascension: int,
        galaxy_x: int,
        galaxy_y: int,
        system_x: int,
        system_y: int
    ) -> typing.Type[SystemTile]:
    """Returns a SystemTile subclass object for the specified tile within a system in a galaxy.

    Args:
        json (bread_cog.JSON_interface): The JSON interface.
        galaxy_seed (str): The seed of the galaxy the tile is in.
        ascension (int): The ascension of the galaxy this system is in.
        galaxy_x (int): The x position in the galaxy the tile is on.
        galaxy_y (int): The y position in the galaxy the tile is on.
        system_x (int): X position of the tile within the system.
        system_y (int): Y position of the tile within the system.

    Returns:
        typing.Type[SystemTile]: The SystemTile subclass object for the tile.
    """

    galaxy_tile = get_galaxy_coordinate(
        json_interface = json_interface,
        guild = guild,
        galaxy_seed = galaxy_seed,
        ascension = ascension,
        xpos = galaxy_x,
        ypos = galaxy_y
    )

    return galaxy_tile.get_system_coordinate(
        system_x = system_x,
        system_y = system_y
    )

def get_planet_modifiers(
        json_interface: bread_cog.JSON_interface,
        ascension: int,
        guild: typing.Union[discord.Guild, int, str],
        day_seed: str,
        tile: SystemPlanet
    ) -> dict[typing.Type[values.Emote], typing.Union[int, float]]:
    """Generates the item modifiers for the given tile.

    Args:
        tile (SystemPlanet): The tile to generate modifiers for.

    Returns:
        dict[Type[Emote], int | float]: A dictionary of item modifiers.
    """

    # The keys in this need to line up with the possible return values in SystemPlanet.get_priority_item()
    odds = {
        "special_bread": 1,
        "rare_bread": 1,
        "chess_piece": 1,
        "gem_red": 1,
        "gem_blue": 1,
        "gem_purple": 1,
        "gem_green": 1,
        "gem_gold": 1,
        "anarchy_chess": 1,
        "anarchy_piece": 1,
        "space_gem": 1
    }

    # If it isn't a planet, then use the defaults of 1.
    if isinstance(tile, SystemPlanet):
        priority = tile.get_priority_item()

        galaxy_tile = get_galaxy_coordinate(
            json_interface = json_interface,
            galaxy_seed = tile.galaxy_seed,
            guild = guild,
            ascension = ascension,
            xpos = tile.galaxy_xpos,
            ypos = tile.galaxy_ypos,
            load_data = True
        ) # type: GalaxyTile

        if galaxy_tile.in_nebula:
            denominator = 0.2
        else:
            denominator = 1

        if galaxy_tile.star.star_type == "black_hole":
            # If it's a black hole, make it a little crazier by dividing the denominator by 5.
            denominator /= 2.5
        elif galaxy_tile.star.star_type == "supermassive_black_hole":
            # If it's the supermassive black hole at the center of the galaxy, chaos.
            denominator /= 5
        
        raw_seed = tile.tile_seed()

        # Handle the Nebula Refinery, Black Hole Observatory, and some of the Dark Matter Resonance Chamber trade hub upgrades.
        chamber_level = 0
        mod = 0
        if galaxy_tile.trade_hub is not None:
            if galaxy_tile.trade_hub.get_upgrade_level(projects.Nebula_Refinery) > 0:
                mod += abs(random.Random(f"{raw_seed}_nebularefinery").gauss(mu=math.pi / 100, sigma=0.05)) * 2

            if galaxy_tile.trade_hub.get_upgrade_level(projects.Black_Hole_Observatory) > 0:
                mod += abs(random.Random(f"{raw_seed}_blackholeobservatory").gauss(mu=math.pi / 100, sigma=0.05)) * 2

            chamber_level = galaxy_tile.trade_hub.get_upgrade_level(projects.Dark_Matter_Resonance_Chamber)

        deviation = (1 - tile.planet_deviation) / (denominator / 2)

        tile_seed = tile.tile_seed() + day_seed

        phi = (1 + math.sqrt(5)) / 2

        # Get the planet seed for each category.
        # These do not change per day.
        for key in odds.copy():
            key_mod = 0

            if chamber_level > 0 and key == "anarchy_piece":
                key_mod += abs(random.Random(f"{raw_seed}_darkmatterresonancechamber").gauss(mu=math.pi / 100, sigma=0.05)) * 2 * chamber_level

            odds[key] = random.Random(f"{raw_seed}{key}").gauss(mu=1 + mod + key_mod, sigma=deviation)

            if key == priority:
                odds[key] = (abs(odds[key] - 1) + 1) * phi

        # Now to get the actual modifiers.
        # These do change per day, but tend to be around the default seeds calculated above.
        for key, value in odds.copy().items():
            sigma = deviation

            if key == priority:
                sigma = deviation * 1.1

            odds[key] = random.Random(f"{tile_seed}{key}").gauss(mu=value, sigma=sigma)

            # Incredibly unlikely to be an issue, but this forces the priority item to be greater than 1.
            # This prevents the priority item from being less common than normal.
            if key == priority and odds[key] < 1:
                odds[key] = abs(odds[key] - 1) + 1


    result = {}

    for special in values.all_special_breads:
        result[special] = odds.get("special_bread", 1)

    for rare in values.all_rare_breads:
        result[rare] = odds.get("rare_bread", 1)
    
    for bpiece in values.chess_pieces_black:
        result[bpiece] = odds.get("chess_piece", 1)
    
    for wpiece in values.chess_pieces_white:
        result[wpiece] = odds.get("chess_piece", 1)
    
    result[values.gem_red] = odds.get("gem_red", 1)
    result[values.gem_blue] = odds.get("gem_blue", 1)
    result[values.gem_purple] = odds.get("gem_purple", 1)
    result[values.gem_green] = odds.get("gem_green", 1)
    result[values.gem_gold] = odds.get("gem_gold", 1)
    result[values.anarchy_chess] = odds.get("anarchy_chess", 1)
    
    for bpiece in values.anarchy_pieces_black:
        result[bpiece] = odds.get("anarchy_piece", 1)
    
    for wpiece in values.anarchy_pieces_white:
        result[wpiece] = odds.get("anarchy_piece", 1)
    
    for gem in values.all_very_shinies:
        result[gem] = odds.get("space_gem", 1)

    return result
    
def get_trade_hub(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        ascension: int,
        galaxy_xpos: int,
        galaxy_ypos: int
    ) -> typing.Union[SystemTradeHub, None]:
    """Returns a SystemTradeHub object for the trade hub in the given galaxy coordinate.

    Args:
        json (bread_cog.JSON_interface): The JSON interface.
        guild (typing.Union[discord.Guild, int, str]): The guild to get the trade hub for.
        ascension (int): The ascension to use.
        galaxy_xpos (int): The x position in the galaxy to use.
        galaxy_ypos (int): The y position in the galaxy to use.

    Returns:
        typing.Union[SystemTradeHub, None]: The SystemTradeHub object for the trade hub, or None if there is no trade hub.
    """
    if (galaxy_xpos, galaxy_ypos) in ALTERNATE_CENTER:
        galaxy_xpos = MAP_RADIUS
        galaxy_ypos = MAP_RADIUS

    space_data = json_interface.get_custom_file("space", guild=guild)

    ascension_data = space_data.get(f"ascension_{ascension}", dict())

    trade_hub_data = ascension_data.get("trade_hubs", dict())

    galaxy_seed = json_interface.get_ascension_seed(ascension, guild=guild)

    if f"{galaxy_xpos} {galaxy_ypos}" in trade_hub_data.keys():
        trade_hub = trade_hub_data.get(f"{galaxy_xpos} {galaxy_ypos}")

        if "location" in trade_hub:
            xpos = trade_hub["location"][0]
            ypos = trade_hub["location"][1]
        else:
            generated = generation.generate_system(
                galaxy_seed = galaxy_seed,
                galaxy_xpos = galaxy_xpos,
                galaxy_ypos = galaxy_ypos
            )

            xpos = generated["trade_hub"]["xpos"]
            ypos = generated["trade_hub"]["ypos"]
        

        return SystemTradeHub(
            galaxy_seed = galaxy_seed,
            galaxy_xpos = galaxy_xpos,
            galaxy_ypos = galaxy_ypos,
            system_xpos = xpos,
            system_ypos = ypos,
            trade_hub_level = trade_hub.get("level", 1),
            upgrades = trade_hub.get("upgrades", dict()),
            settings = trade_hub.get("settings", dict()),
            color = trade_hub.get("color_id", HUB_RED),
        )
    
    generated = generation.generate_system(
        galaxy_seed = galaxy_seed,
        galaxy_xpos = galaxy_xpos,
        galaxy_ypos = galaxy_ypos
    )

    if generated is None:
        return None
    
    if not generated["trade_hub"].get("exists", False):
        return None
    
    return SystemTradeHub(
        galaxy_seed = galaxy_seed,
        galaxy_xpos = galaxy_xpos,
        galaxy_ypos = galaxy_ypos,
        system_xpos = generated["trade_hub"]["xpos"],
        system_ypos = generated["trade_hub"]["ypos"],
        trade_hub_level = generated["trade_hub"]["level"],
        upgrades = {},
        settings = {},
        color = HUB_RED # Default color is red.
    )

            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def create_trade_hub(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account,
        galaxy_x: int,
        galaxy_y: int,
        system_x: int,
        system_y: int,
        level: int = 1
    ) -> None:
    """Creates a new trade hub in the given system."""
    guild_id = user_account.get("guild_id")

    ascension_data = json_interface.get_space_ascension(ascension_id=user_account.get_prestige_level(), guild=guild_id)

    trade_hub_data = ascension_data.get("trade_hubs", dict())

    trade_hub_data[f"{galaxy_x} {galaxy_y}"] = {
        "location": [system_x, system_y],
        "level": level,
        "project_progress": {
            "project_1": {},
            "project_2": {},
            "project_3": {},
            "project_4": {},
            "project_5": {}
        }
    }

    ascension_data["trade_hubs"] = trade_hub_data

    space_data = json_interface.get_space_data(guild=guild_id)

    space_data[f"ascension_{user_account.get_prestige_level()}"] = ascension_data

    json_interface.set_custom_file("space", space_data, guild=guild_id)

def get_trade_hub_project_categories(
        day_seed: str,
        hub_tile: SystemTradeHub
    ) -> dict[str, list[projects.Project]]:
    category_bindings = {
        values.black_pawn.text: "pawn",
        values.white_pawn.text: "pawn",
        values.anarchy_black_pawn.text: "pawn",
        values.anarchy_white_pawn.text: "pawn",
        values.black_knight.text: "knight",
        values.white_knight.text: "knight",
        values.anarchy_black_knight.text: "knight",
        values.anarchy_white_knight.text: "knight",
        values.black_bishop.text: "bishop",
        values.white_bishop.text: "bishop",
        values.anarchy_black_bishop.text: "bishop",
        values.anarchy_white_bishop.text: "bishop",
        values.black_rook.text: "rook",
        values.white_rook.text: "rook",
        values.anarchy_black_rook.text: "rook",
        values.anarchy_white_rook.text: "rook",
        values.black_queen.text: "queen",
        values.white_queen.text: "queen",
        values.anarchy_black_queen.text: "queen",
        values.anarchy_white_queen.text: "queen",
        values.black_king.text: "king",
        values.white_king.text: "king",
        values.anarchy_black_king.text: "king",
        values.anarchy_white_king.text: "king",
        values.gem_gold.text: "gems",
        values.gem_green.text: "gems",
        values.gem_purple.text: "gems",
        values.gem_blue.text: "gems",
        values.gem_red.text: "gems",
        values.gem_pink.text: "gems",
        values.gem_orange.text: "gems",
        values.gem_cyan.text: "gems",
        values.gem_white.text: "gems",
        # Misc items are not included so new items automatically get added to it.
    }

    categories = {
        "pawn": [],
        "knight": [],
        "bishop": [],
        "rook": [],
        "queen": [],
        "king": [],
        "gems": [],
        "misc": []
    }

    for project in projects.all_projects:
        costs = project.get_reward(
            day_seed = day_seed,
            system_tile = hub_tile
        )

        for item, amount in costs:
            category = category_bindings.get(item)
            if category is None:
                categories["misc"].append(project)
                continue

            if project in categories[category]:
                continue

            categories[category].append(project)
    
    return categories

def get_trade_hub_project_weights(
        day_seed: str,
        hub_tile: SystemTradeHub
    ) -> dict[projects.Project, int]:
    setting = hub_tile.get_setting("shroud_beacon_setting")
    if setting is None:
        return {project: 1 for project in projects.all_projects}
    
    beacon_level = hub_tile.get_upgrade_level(projects.Shroud_Beacon)
    
    categories = get_trade_hub_project_categories(day_seed, hub_tile)

    return {
        project: 1 + (5 * beacon_level * (project in categories[setting]))
        for project in projects.all_projects
    }

def get_trade_hub_projects(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account,
        system_tile: SystemTradeHub
    ) -> list[dict[str, typing.Union[projects.Project, int, str, bool]]]:
    """Returns a list of dictionaries, where each dictionary is a project on the given galaxy tile."""
    prestige_level = user_account.get_prestige_level()
    guild_id = user_account.get("guild_id")
    seed = json_interface.get_ascension_seed(prestige_level, guild_id)
    daily_seed = json_interface.get_day_seed(user_account.get("guild_id"))

    out_projects = []

    galaxy_x = system_tile.galaxy_xpos
    galaxy_y = system_tile.galaxy_ypos

    trade_hub_data = json_interface.get_space_ascension(prestige_level, guild_id)
    trade_hub_data = trade_hub_data.get("trade_hubs", {})
    trade_hub_data = trade_hub_data.get(f"{galaxy_x} {galaxy_y}", {})

    project_data = trade_hub_data.get("project_progress", {})

    used_names = []

    weights = get_trade_hub_project_weights(
        day_seed = daily_seed,
        hub_tile = system_tile
    )

    project_id = -1
    while len(out_projects) < 5:
        project_id += 1

        key = f"project_{len(out_projects) + 1}"
        rng = random.Random(utility.hash_args(seed, daily_seed, galaxy_x, galaxy_y, project_id))
        
        project = None

        if project_data.get(key, {}).get("internal") is not None:
            project = projects.get_project(project_data.get(key, {}).get("internal"))
        
        if project is None:
            project = rng.choices(
                population = list(weights.keys()),
                weights = list(weights.values())
            )[0]
            
            # If it broke out of the while loop then `project` will be a list, in which case we need to skip to the next iteration.
            if isinstance(project, list):
                continue

            # Prevent duplicates.
            if project.internal in used_names:
                continue

        # if project_id == 0: # For testing new projects.
        #     project = projects.Cafeteria_Kerfuffle

        project_progress = project_data.get(key, {}).get("contributions", {})
        completed = project_data.get(key, {}).get("completed", False)

        used_names.append(project.internal)

        out_projects.append(
            {
                "project": project,
                "contributions": project_progress,
                "completed": completed,
                "internal": project.internal
            }
        )
    
    return out_projects

def get_project_credits_usage(
        total_items: int,
        items_contributed: int,
        item_offset: int = 0
    ) -> int:
    """Calculates the amount of credits contributing to a project consumes.

    Args:
        total_items (int): The total number of items the project requires.
        items_contributed (int): The amount of items that have been contributed.
        item_offset (int, optional): The number of items already contributed by the player. Defaults to 0.
    Returns:
        int: The amount of credits to consume, between 0 and 1000.
    """

    total_contributes = items_contributed + item_offset
    amount_done = total_contributes / total_items

    if amount_done == 0:
        return 0

    return max(int(amount_done / ((1 / amount_done) + 1) * 2000), 1)


            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def get_spawn_location(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account
    ) -> tuple[int, int]:
    """Returns a 2D tuple of the spawn location in the galaxy the given player is in."""
    map_data = json_interface.get_space_map_data(
        ascension_id = user_account.get_prestige_level(),
        guild = user_account.get("guild_id")
    )

    if "spawn_point" in map_data:
        return tuple(map_data["spawn_point"])

    seed = json_interface.get_ascension_seed(
        ascension_id = user_account.get_prestige_level(),
        guild = user_account.get("guild_id")
    )

    location = generation.get_galaxy_spawn(galaxy_seed=seed)

    map_data["spawn_point"] = list(location)

    json_interface.set_space_map_data(
        ascension_id = user_account.get_prestige_level(),
        guild = user_account.get("guild_id"),
        new_data = map_data
    )

    return location

def get_move_cost_galaxy(
        json_interface: bread_cog.JSON_interface,
        guild: typing.Union[discord.Guild, int, str],
        ascension: int,
        start_position: tuple[int, int],
        end_position: tuple[int, int]
    ) -> dict:
    """Calculates the fuel cost to move between two points on the galaxy map."""
    points = utility.plot_line(
        start = start_position,
        end = end_position
    )

    # Remove the first item, which is the starting location.
    points.pop(0)

    cost_sum = 0

    through_nebula = False

    map_data = json_interface.get_space_map_data(
        ascension_id = ascension,
        guild = guild
    )
    
    for x, y in points:
        nebula = in_nebula_database(
            json_interface = json_interface,
            guild = guild,
            ascension = ascension,
            xpos = x,
            ypos = y,
            map_data = map_data
        )

        if nebula:
            through_nebula = True
            cost_sum += MOVE_FUEL_GALAXY_NEBULA
        else:
            cost_sum += MOVE_FUEL_GALAXY
    
    return {
        "cost": cost_sum,
        "nebula": through_nebula,
        "points": points
    }


def get_move_cost_system(
        start_position: tuple[int, int],
        end_position: tuple[int, int]
    ) -> dict:
    """Calculates the fuel cost to move between two points on the system map."""
    points = utility.plot_line(
        start = start_position,
        end = end_position
    )

    # Remove the first item, which is the starting location.
    points.pop(0)

    return {
        "cost": len(points) * MOVE_FUEL_SYSTEM
    }


def get_hyperlane_registrar_bonus(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account
    ) -> float:
    """Gets the active multiplier for Hyperlane Registrar for the given player."""
    space_data = json_interface.get_space_data(user_account.get("guild_id"))
    ascension_data = space_data.get(f"ascension_{user_account.get_prestige_level()}", {})
    trade_hub_data = ascension_data.get("trade_hubs", {})

    player_x, player_y = user_account.get_galaxy_location(json_interface)

    max_found = 0

    for key, data in trade_hub_data.items():
        try:
            split = key.split(" ", 1)
            hub_x = int(split[0])
            hub_y = int(split[1])
            level = data.get("level", 1)
        except:
            continue
            
        max_distance = store.trade_hub_squared[level]
        distance = (hub_x - player_x) ** 2 + (hub_y - player_y) ** 2

        if distance <= max_distance:
            upgrades = data.get("upgrades", {})
            registrar = upgrades.get(projects.Hyperlane_Registrar.internal, {}).get("level", 0)
            
            if registrar > max_found:
                max_found = registrar
    
    return projects.Hyperlane_Registrar.cost_multipliers[max_found]
            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def gifting_check_user(
        json_interface: bread_cog.JSON_interface,
        user: account.Bread_Account
    ) -> bool:
    """Determines whether the given user is within distance of a Trade Hub to trade."""
    guild = user.get("guild_id")
    ascension = user.get_prestige_level()

    player_x, player_y = user.get_galaxy_location(json_interface)

    space_data = json_interface.get_space_data(guild)
    ascension_data = space_data.get(f"ascension_{ascension}", {})
    trade_hub_data = ascension_data.get("trade_hubs", {})

    for key in trade_hub_data:
        try:
            split = key.split(" ", 1)
            hub_x = int(split[0])
            hub_y = int(split[1])
            level = trade_hub_data.get(key, {}).get("level", 1)
        except:
            continue
            
        max_distance = store.trade_hub_squared[level]
        distance = (hub_x - player_x) ** 2 + (hub_y - player_y) ** 2

        if distance <= max_distance:
            return True
    
    return False

def allowed_gifting(
        json_interface: bread_cog.JSON_interface,
        player_1: account.Bread_Account,
        player_2: account.Bread_Account
    ) -> bool:
    """Determines whether a gift can be sent between two players."""
    return gifting_check_user(json_interface, player_1) and gifting_check_user(json_interface, player_2)