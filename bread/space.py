from __future__ import annotations

import discord

import math
import typing
import random
import io

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

MAP_SIZE = 256

MAP_RADIUS = MAP_SIZE // 2
MAP_RADIUS_SQUARED = MAP_RADIUS ** 2

## Fuel requirements:
# This is the amount of fuel required for each jump in their respective areas.
MOVE_FUEL_SYSTEM = 25
MOVE_FUEL_GALAXY = 175
MOVE_FUEL_GALAXY_NEBULA = 350
MOVE_FUEL_WORMHOLE = 325

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
    "wormhole": "images/wormhole.png",
    "trade_hub": "images/trade_hub.png",
    "asteroid": "images/asteroid.png",
    "bread": "images/bread.png",

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

    # Gems.
    "gem_red": "images/gem_red.png",
    "gem_blue": "images/gem_blue.png",
    "gem_purple": "images/gem_purple.png",
    "gem_green": "images/gem_green.png",
    "gem_gold": "images/gem_gold.png",

    # MoaK.
    "anarchy_chess": "images/anarchy_chess.png",
}

print("Bread Space: Loading map images.")

EMOJI_IMAGES = {}

for key, path in EMOJI_PATHS.items():
    EMOJI_IMAGES[key] = Image.open(path).resize((128, 128))

print("Bread Space: Map image loading complete.")


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
        self.galaxy_seed = galaxy_seed

        self.galaxy_xpos = galaxy_xpos
        self.galaxy_ypos = galaxy_ypos
        self.system_xpos = round(system_xpos)
        self.system_ypos = round(system_ypos)
    
    # Optional for subclasses.
    def __str__(self: typing.Self):
        return f"<SystemTile | system_x: {self.system_xpos} | system_y: {self.system_ypos} | galaxy_x: {self.galaxy_xpos} | galaxy_y: {self.galaxy_ypos}>"
    
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
        
        

    ###############################################################################
    ##### Analysis methods.

    # Should be overwitten by subclasses.
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
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
            detailed: bool = False
        ) -> list[str]:
        return ["There seems to be nothing here."]
    
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
            detailed: bool = False
        ) -> list[str]:
        return [
                "Object type: Star",
                f"Star type: {self.star_type.title()}"
            ]
    
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

            trade_hub_level: int = None
        ) -> None:
        super().__init__(galaxy_seed, galaxy_xpos, galaxy_ypos, system_xpos, system_ypos)

        self.trade_hub_level = trade_hub_level
        self.type = "trade_hub"
    
    def get_emoji(self: typing.Self) -> str:
        return "trade_hub"
    
    def get_analysis(
            self: typing.Self,
            guild: typing.Union[discord.Guild, int, str],
            json_interface: bread_cog.JSON_interface,
            detailed: bool = False
        ) -> list[str]:
        return [
                "Object type: Trade Hub",
                f"Trade Hub level: {self.trade_hub_level}",
                "Use '$bread space hub' while over the trade hub to interact with it."
            ]
    
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
            "Anarchy Piece": values.anarchy_black_pawn
        }

        if not detailed:
            deviation = self.planet_deviation

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
            
            result = next(
                text for lower, upper, text in ranges
                if (lower < deviation <= upper and upper > 1) or \
                   (lower <= deviation < upper and upper < 1) or \
                   (lower <= deviation <= upper and (upper > 1 and lower < 1))
            )

            result = [
                "Object type: Planet",
                f"Planet type: {self.planet_type.text}",
                f"Stability: {result}",
                "",
                "Distance too far to determine more information."
            ]

            return result

        result = [
            "Object type: Planet",
            f"Planet type: {self.planet_type.text}",
            f"Distance: {round(self.planet_distance, 3)}",
            f"Angle: {self.planet_angle}",
            f"Deviation: {round(self.planet_deviation, 3)}",
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
            detailed: bool = False
        ) -> list[str]:
        return [
                "Object type: Wormhole",
                "Use '$bread space move wormhole' when above.",
                "Futher information: Unavailable."
            ]
    
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
            in_nebula: bool = False,

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

        self.xpos = xpos
        self.ypos = ypos
        self.in_nebula = in_nebula

        self.system = system

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
        
        # Get the data for the system.
        raw_data = generation.generate_system(
            galaxy_seed = self.galaxy_seed,
            galaxy_xpos = self.xpos,
            galaxy_ypos = self.ypos,
            get_wormholes = get_wormholes
        )

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
        
        if raw_data.get("wormhole", {}).get("exists", False):
            wormhole_data = raw_data.get("wormhole", {})

            self.wormhole = SystemWormhole(
                galaxy_seed = self.galaxy_seed,

                galaxy_xpos = self.xpos,
                galaxy_ypos = self.ypos,
                system_xpos = wormhole_data.get("xpos", None),
                system_ypos = wormhole_data.get("ypos", None),

                wormhole_link_location = wormhole_data.get("link_galaxy", None)
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

                planet_type = planet_data.get("type"),
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
        
        # If nothing else triggers, then this tile is empty.
        return self._empty_system_tile(
            system_x = system_x,
            system_y = system_y
        )

def get_corruption_chance(
        xpos: int,
        ypos: int,
    ) -> float:
    """Returns the chance of a loaf becoming corrupted for any point in the galaxy. Between 0 and 1."""
    dist = math.hypot(xpos, ypos)

    # The band where the chance is 0 is between ~80 and ~87.774.
    if 80 <= dist <= 87.774:
        return 0.0

    # `\frac{d^{2.15703654359}}{1000}+118e^{-0.232232152965\left(\frac{d}{22.5}\right)^{2}}-19`
    # where `d` is the distance to (0, 0).
    return ((dist ** 2.15703654359 / 1000) + 118 * math.e ** (-0.232232152965 * (dist / 22.5) ** 2) - 19) / 100

            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def space_map(
        account: account.Bread_Account,
        json_interface: bread_cog.JSON_interface,
        mode: typing.Union[str, None] = None,
        analyze_position: str = None
    ) -> io.BytesIO:
    """Generates the map of a system or galaxy that can be sent in Discord.

    Args:
        account (account.Bread_Account): The account of the player calling the map.
        json_interface: (bread_cog.JSON_interface): The JSON interface.
        mode (typing.Union[str, None], optional): The mode to use. 'galaxy' for the galaxy map. Defaults to the system map for anything else. Defaults to None.
        analyze_position (str, optional): The location to hover the analysis on. Example: `a1` and `e5`. If None is passed it will not add the analysis. Only works on the system map. Defaults to None.

    Returns:
        io.BytesIO: BytesIO object corresponding to the generated image.
    """
    galaxy_seed = json_interface.get_ascension_seed(account.get_prestige_level(), guild=account.get("guild_id"))

    guild = account.get("guild_id")

    sensor_level = account.get("telescope_level")

    # Position in the galaxy.
    x_galaxy, y_galaxy = account.get_galaxy_location(json_interface=json_interface)

    radius = sensor_level + 2

    ascension = account.get_prestige_level()

    if mode == "galaxy":
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

    letters = "abcdefghijk"

    corners = [
        (0, 0), (0, 1), (1, 0),
        (0, y_size + 3), (1, y_size + 3), (0, y_size + 2),
        (x_size + 3, 0), (x_size + 2, 0), (x_size + 3, 1),
        (x_size + 3, y_size + 3), (x_size + 3, y_size + 2), (x_size + 2, y_size + 3),
    ]
    
    size_check = x_size - round(2 * ((telescope_level + 1) ** 0.5)) # https://www.desmos.com/calculator/jbtcaxcbl6
    
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
            if abs(xpos - 2 - radius) + abs(ypos - 2 - radius) > size_check:
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

    letters = "abcdefghijk"

    corners = [
        (0, 0), (0, 1), (1, 0),
        (0, y_size + 3), (1, y_size + 3), (0, y_size + 2),
        (x_size + 3, 0), (x_size + 2, 0), (x_size + 3, 1),
        (x_size + 3, y_size + 3), (x_size + 3, y_size + 2), (x_size + 2, y_size + 3),
    ]

    size_check = x_size - round(2 * ((telescope_level + 1) ** 0.5)) # https://www.desmos.com/calculator/jbtcaxcbl6

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
        if abs(grid_x - 2 - radius) + abs(grid_y - 2 - radius) <= size_check:
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
        xpos = "abcdefghijk".index(analyze_position[0])
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

            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################
    
def generate_galaxy_seed() -> str:
    """Generates a random new galaxy seed."""
    return "{:064x}".format(random.randrange(16 ** 64)) # Random 64 digit hexadecimal number.

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
        load_data (bool, optional): Whether to load the system data when making the GalaxyTile object. Defaults to False.
    
    Returns:
        GalaxyTile: A GalaxyTile object for the coordinate.
    """
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
        in_nebula = in_nebula
    )

    if not is_system:
        return out

    if load_data:
        out.load_system_data(json_interface=json_interface, guild=guild, get_wormholes=True)

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
        "anarchy_piece": 1
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
            denominator = 2.5
        else:
            denominator = math.tau

        if galaxy_tile.star.star_type == "black_hole":
            # If it's a black hole, make it a little crazier by dividing the denominator by 2.
            denominator /= 2

        deviation = (1 - tile.planet_deviation) / denominator

        raw_seed = tile.tile_seed()
        tile_seed = tile.tile_seed() + day_seed

        sqrt_phi = math.sqrt((1 + math.sqrt(5)) / 2)

        # Get the planet seed for each category.
        # These do not change per day.
        for key in odds.copy():
            odds[key] = random.Random(f"{raw_seed}{key}").gauss(mu=1, sigma=deviation)

            if key == priority:
                odds[key] = (abs(odds[key] - 1) + 1) * sqrt_phi

        # Now to get the actual modifiers.
        # These do change per day, but tend to be around the default seeds calculated above.
        for key, value in odds.copy().items():
            sigma = deviation / 2.5

            if key == priority:
                sigma = deviation / 1.5

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
            trade_hub_level = trade_hub.get("level", 1)
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
        trade_hub_level = generated["trade_hub"]["level"]
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
        system_y: int
    ) -> None:
    """Creates a new trade hub in the given system."""
    guild_id = user_account.get("guild_id")

    ascension_data = json_interface.get_space_ascension(ascension_id=user_account.get_prestige_level(), guild=guild_id)

    trade_hub_data = ascension_data.get("trade_hubs", dict())

    trade_hub_data[f"{galaxy_x} {galaxy_y}"] = {
        "location": [system_x, system_y],
        "level": 1,
        "project_progress": {
            "project_1": {},
            "project_2": {},
            "project_3": {}
        }
    }

    ascension_data["trade_hubs"] = trade_hub_data

    space_data = json_interface.get_space_data(guild=guild_id)

    space_data[f"ascension_{user_account.get_prestige_level()}"] = ascension_data

    json_interface.set_custom_file("space", space_data, guild=guild_id)

def get_trade_hub_projects(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account,
        galaxy_x: int,
        galaxy_y: int
    ) -> list[dict[str, typing.Union[projects.Project, int, str, bool]]]:
    """Returns a list of dictionaries, where each dictionary is a project on the given galaxy tile."""
    prestige_level = user_account.get_prestige_level()
    guild_id = user_account.get("guild_id")
    seed = json_interface.get_ascension_seed(prestige_level, guild_id)
    daily_seed = json_interface.get_day_seed(user_account.get("guild_id"))

    out_projects = []

    trade_hub_data = json_interface.get_space_ascension(prestige_level, guild_id)
    trade_hub_data = trade_hub_data.get("trade_hubs", {})
    trade_hub_data = trade_hub_data.get(f"{galaxy_x} {galaxy_y}", {})

    project_data = trade_hub_data.get("project_progress", {})

    used_names = []

    project_id = -1
    while len(out_projects) < 3:
        project_id += 1

        key = f"project_{len(out_projects) + 1}"
        rng = random.Random(utility.hash_args(seed, daily_seed, galaxy_x, galaxy_y, project_id))
        
        # project = projects.all_projects.copy()
        project = projects.item_project_lists

        while isinstance(project, list):
            if isinstance(project, list):
                if len(project) == 0:
                    break
            
            project = rng.choice(project)
        
        # If it broke out of the while loop then `project` will be a list, in which case we need to skip to the next iteration.
        if isinstance(project, list):
            continue

        # Prevent duplicates.
        if project.internal in used_names:
            continue

        project_progress = project_data.get(key, {}).get("contributions", {})
        completed = project_data.get(key, {}).get("completed", False)

        used_names.append(project.internal)

        out_projects.append(
            {
                "project": project,
                "contributions": project_progress,
                "completed": completed
            }
        )
    
    return out_projects


            

        




###################################################################################################################################
###################################################################################################################################
###################################################################################################################################

def get_spawn_location(
        json_interface: bread_cog.JSON_interface,
        user_account: account.Bread_Account
    ) -> tuple[int, int]:
    """Returns a 2D tuple of the spawn location in the galaxy the given player is in."""
    seed = json_interface.get_ascension_seed(
        ascension_id = user_account.get_prestige_level(),
        guild = user_account.get("guild_id")
    )

    return generation.get_galaxy_spawn(galaxy_seed=seed)

def get_move_cost_galaxy(
        galaxy_seed: str,
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

    for x, y in points:
        tile_data = generation.galaxy_single(
            galaxy_seed = galaxy_seed,
            x = x,
            y = y
        )

        if tile_data.get("in_nebula", False):
            through_nebula = True
            cost_sum += MOVE_FUEL_GALAXY_NEBULA
        else:
            cost_sum += MOVE_FUEL_GALAXY
    
    return {
        "cost": cost_sum,
        "nebula": through_nebula
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