"""This houses the galaxy and system generation code.

###############################################################################################
##### CHANGES MADE TO THIS CODE WILL AFFECT EVERYTHING, EVEN IF IT HAS ALREADY BEEN SEEN. #####
##### Due to everything being generated on-demand and not being stored in the database.   #####
###############################################################################################
"""

import random
import math
import typing
import hashlib

import bread.values as values

map_size = 256

map_radius = map_size // 2
map_radius_squared = map_radius ** 2

# This is in `1 in __`, so an 8 means a 1/8 chance.
chance_system = 8 # Chance of any point being a system, assuming it doesn't have a system very close nearby.
chance_trade = 3 # The chance of any generated system having a trading hub by default.

star_weights = {
    "star1": 50,
    "star2": 22,
    "star3": 22,
    "black_hole": 6
}

planet_weights = {
    "normal_bread": 20,
    "special_bread": 20,
    "rare_bread": 50,
    "piece_black": 55,
    "piece_white": 45,
    "gem_red": 20,
    "bem_blue": 48,
    "gem_purple": 24,
    "gem_green": 12,
    "gem_gold": 6,
    "anarchy_chess": 3
}

planet_options = {
    "normal_bread": [values.normal_bread],
    "special_bread": values.all_special_breads,
    "rare_bread": values.all_rare_breads,
    "piece_black": values.chess_pieces_black_biased,
    "piece_white": values.chess_pieces_white_biased,
    "gem_red": [values.gem_red],
    "bem_blue": [values.gem_blue],
    "gem_purple": [values.gem_purple],
    "gem_green": [values.gem_green],
    "gem_gold": [values.gem_gold],
    "anarchy_chess": [values.anarchy_chess]
}

####################################
### GALAXY GENERATION UTILITIES

def gradients_and_nebulae(galaxy_seed: str) -> tuple[list, list]:
    """Generates the gradient and nebulae info for the galaxy.

    Args:
        galaxy_seed (int): The seed of the galaxy.

    Returns:
        tuple[list, list]: The gradient info in one list, and the nebulae info in the other.
    """
    gradient_points = []
    nebulae_points = []

    seeded = random.Random(galaxy_seed)

    previous_angles = []
    for point in range(6): # 4 for gradient points, 2 for nebulae
        dist = map_radius * ((seeded.random() / 2) + 0.25)

        if point > 3:
            dist += map_radius / 16

        try:
            previous = sum(previous_angles) // len(previous_angles) * math.pi
        except ZeroDivisionError:
            previous = 0
        
        angle = (seeded.randrange(0, 360) + previous) % 360
        

        x = round(math.cos(math.radians(angle)) * dist)
        y = round(math.sin(math.radians(angle)) * dist)
        fold = seeded.randint(2, 5)
        rotation = seeded.randrange(0, 360)

        if point <= 3:
            gradient_points.append((x, y, fold, rotation))
        else:
            nebulae_points.append((x, y, 1, rotation))

        previous_angles.append(angle)
    
    return (gradient_points, nebulae_points)

def gradient_modifier(
        gradient_info: list,
        x: int,
        y: int
    ) -> typing.Union[int, float]:
    """Determines the amount that the gradients affect the given point.

    Args:
        gradient_info (list): The gradient information.
        x (int): The x position.
        y (int): The y position.

    Returns:
        typing.Union[int, float]: The amount to add from the gradients.
    """

    for xpoint, ypoint, fold, rotation in gradient_info:
        
        dist = math.dist((x, y), (xpoint, ypoint))

        ydiff = y - ypoint

        try:
            angle = math.asin(ydiff / dist)
        except ZeroDivisionError:
            continue

        if x < xpoint:
            angle = math.pi - angle

        angle += math.radians(rotation)

        mod = math.sin(fold * angle) + math.sin(fold * (1 + 1 / fold) * angle)
        mod = mod * 10

        result = abs((dist - 45 + mod) * (math.pi / 2))
        if result <= 10:
            return result

    return 0

def in_nebula(
        nebulae_info: list,
        x: int,
        y: int
    ) -> bool:
    """Returns a boolean for whether a given point is in a nebula.

    Args:
        nebulae_info (list): The nebulae information.
        x (int): The x position.
        y (int): The y position.

    Returns:
        bool: Whether the point is in a nebula.
    """
    for xpoint, ypoint, fold, rotation in nebulae_info:
        
        dist = math.dist((x, y), (xpoint, ypoint))

        ydiff = y - ypoint

        try:
            angle = math.asin(ydiff / dist)
        except ZeroDivisionError:
            continue

        if x < xpoint:
            angle = math.pi - angle

        angle += math.radians(rotation)

        mod = math.sin(fold * angle) + math.sin(fold * (1 + 1 / fold) * angle)
        mod = mod * 10

        if dist <= (25 + mod) * (math.pi / 2):
            return True

    return False

def core_spot(
        galaxy_seed: str,
        x: int,
        y: int,
        rng: random.Random,
        gradient_info: int
    ) -> int:
    """The core randomness for a point in the galaxy. This disregards nearby systems.

    Args:
        galaxy_seed (str): The seed of the galaxy.
        x (int): The x coordinate.
        y (int): The y coordinate.
        rng (random.Random): The random.Random object for randomness.

    Returns:
        int: The generated random number greater than or equal to 1.
    """
    rng.seed(hashlib.sha256(str(galaxy_seed + str(x) + str(y)).encode()).digest())
    try:
        mod = ((x ** 2 + y ** 2) / 131072) ** -1
    except:
        mod = 2 ** 16

    gradient_mod = gradient_modifier(gradient_info, x, y) * 128

    return rng.randint(1, int(chance_system + mod + gradient_mod) * chance_trade)

def get_spot(
        galaxy_seed: str,
        x: int,
        y: int,
        gradient_info: list
    ) -> int:
    """The main logic for a point in the galaxy.

    Args:
        galaxy_seed (str): The galaxy seed.
        x (int): The x coordinate.
        y (int): The y coordinate.

    Returns:
        int: What is on the given point. 0 is nothing, 1 is a system without a trade hub, 2 is a system with a trade hub.
    """
    
    if (x ** 2 + y ** 2) > map_radius_squared:
        return 0

    rng = core_spot(
        galaxy_seed = galaxy_seed,
        x = x,
        y = y,
        rng = random.Random(),
        gradient_info = gradient_info
    )

    if rng > chance_trade:
        return 0 # nothing
    
    for x_mod in range(-1, 2):
        for y_mod in range(-1, 2):
            if x_mod == 0 and y_mod == 0:
                continue
            if core_spot(
                    galaxy_seed = galaxy_seed,
                    x = x + x_mod,
                    y = y + y_mod,
                    rng = random.Random(),
                    gradient_info = gradient_info
                ) <= chance_trade:
                return 0
    
    if rng == 1:
        return 2 # system with trade hub
    
    return 1 # system without trade hub



###############################
#### GALAXY GENERATION FUNCTIONS

def galaxy_single(
        galaxy_seed: str,
        x: int,
        y: int,
        gradient_info: list = None,
        nebulae_info: list = None
    ) -> dict:
    """Generates a single point in the galaxy.
    
    Note that this does NOT include player-made modifications, like trade hubs.

    Args:
        galaxy_seed (int): The seed of the galaxy.
        x (int): The x coordinate to generate.
        y (int): The y coordinate to generate.
        gradient_info (list, optional): The gradient info. If None is provided it will be generated. Defaults to None.
        nebulae_info (list, optional): The nebulae info. If None is provided it will be generated. Defaults to None.
    
    Returns:
        dict: The information for the generated point.
    """
    if gradient_info is None or nebulae_info is None:
        gradient_info, nebulae_info = gradients_and_nebulae(galaxy_seed)
    
    point_info = get_spot(
        galaxy_seed = galaxy_seed,
        x = x - map_radius,
        y = y - map_radius,
        gradient_info = gradient_info
    )

    out = {
        "x": x,
        "y": y,
        "in_nebula": in_nebula(nebulae_info, x - map_radius, y - map_radius),
        "system": False,
    }

    if point_info != 0:
        out["system"] = True
        out["trade_hub"] = point_info == 2

    return out
    

def galaxy_bulk(
        galaxy_seed: str,
        top_right: tuple[int, int],
        bottom_left: tuple[int, int]
    ) -> dict[tuple[int, int], dict]:
    """Generates a set of spaces in bulk.

    Args:
        galaxy_seed (int): The seed of the galaxy.
        top_left (tuple[int, int]): The x y coordinate of the top left space to generate.
        bottom_right (tuple[int, int]): The x y coordinate of the bottom right space to generate.

    Returns:
        dict[tuple[int, int], dict]: Dictionary for the generated spaces. Keys are the x y coordinates, and the values are the space information.
    """
    out = {}

    gradient_info, nebulae_info = gradients_and_nebulae(galaxy_seed)

    x_size = max(top_right[0], bottom_left[0]) - min(top_right[0], bottom_left[0]) + 1
    y_size = max(top_right[1], bottom_left[1]) - min(top_right[1], bottom_left[1]) + 1

    for y_pos in range(y_size):
        for x_pos in range(x_size):
            out[(x_pos + min(top_right[0], bottom_left[0]), y_pos + min(top_right[1], bottom_left[1]))] = galaxy_single(
                galaxy_seed = galaxy_seed,
                x = x_pos + min(top_right[0], bottom_left[0]),
                y = y_pos + min(top_right[1], bottom_left[1]),
                gradient_info = gradient_info,
                nebulae_info = nebulae_info
            )
    
    return out



###############################
#### SYSTEM GENERATION FUNCTIONS

def generate_system(
        galaxy_seed: str,
        galaxy_xpos: int,
        galaxy_ypos: int
    ) -> typing.Union[dict, None]:
    """Generates the data for a system.

    Args:
        galaxy_seed (str): The seed of the galaxy this system is in.
        galaxy_xpos (int): The x position of the system within the galaxy.
        galaxy_ypos (int): The y position of the system within the galaxy.

    Returns:
        typing.Union[dict, None]: The data for the system in a dict if the tile has a system on it, otherwise None.
    """

    ######################################################################################
    ##### CHANGES MADE TO THIS WILL AFFECT EVERY SYSTEM, INCLUDING ONES ALREADY SEEN #####
    ##### This is because the contents of systems are generated on-demand, and are   #####
    ##### not stored in the database anywhere. Natural trade hubs that haven't been  #####
    ##### levelled up should stay, however they may not spawn in the same location   #####
    ##### before changes are made. Trade hubs that have been levelled up will stay.  #####
    ##### Depending on where the change is made asteroid belts & planets may change. #####
    ######################################################################################

    gradient_info = gradients_and_nebulae(galaxy_seed)[0]

    system_type = get_spot(
        galaxy_seed=galaxy_seed,
        x = galaxy_xpos - map_radius,
        y = galaxy_ypos - map_radius,
        gradient_info = gradient_info
    )

    if system_type == 0:
        return None
    
    rng = random.Random(hashlib.sha256(str(galaxy_seed + str(galaxy_ypos) + str(galaxy_xpos)).encode()).digest())

    has_trade_hub = system_type == 2

    trade_hub_xpos = rng.randint(-1, 1)
    trade_hub_ypos = rng.randint(-1, 1)

    if not(trade_hub_xpos or trade_hub_ypos):
        trade_hub_ypos = rng.randint(0, 1) * -2 + 1

    star_type = rng.choices(
        population = list(star_weights.keys()),
        weights = list(star_weights.values())
    )[0]

    planet_count = round(rng.normalvariate(
        mu = 7,
        sigma = 2
    ))

    ###############################################################
    #### Planet & Asteroid belt generation.

    planets = []

    planet_count = max(min(planet_count, 12), 2)

    asteroid_belt = rng.randint(1, 3) == 1 # 1 in 3 chance of an asteroid belt.

    if asteroid_belt:
        asteroid_belt_distance = rng.randint(2, math.ceil(planet_count ** 0.85) + 1)
    else:
        asteroid_belt_distance = planet_count + 2

    for planet_id in range(planet_count):
        planet_type = rng.choices(
            population = list(planet_weights.keys()),
            weights = list(planet_weights.values())
        )[0]

        planet_type = rng.choice(planet_options[planet_type])

        deviation = rng.normalvariate(
            mu = 1,
            sigma = 0.1
        )

        modified_id = planet_id + (1 if planet_id - 1 >= asteroid_belt_distance else 0)

        planet_distance = 2 + (modified_id + 1.5)# ** 1.712 # dont ask why that number lol

        distance_mod = rng.normalvariate(mu = 1, sigma = 0.1)

        planet_angle = rng.randrange(0, 360) # Orbiting code here?

        planet_distance = planet_distance * distance_mod

        planet_x = math.cos(math.radians(planet_angle)) * planet_distance
        planet_y = math.sin(math.radians(planet_angle)) * planet_distance

        planets.append({
            "xpos": planet_x,
            "ypos": planet_y,
            "distance": planet_distance,
            "angle": planet_angle,
            "type": planet_type, # what type of item is prioritized
            "deviation": deviation # how much variation there is in the roll multipliers
        })
    
    largest_distance = max(planets, key=lambda x: x["distance"])["distance"]
    
    return {
        "trade_hub": {
            "exists": has_trade_hub,
            "xpos": trade_hub_xpos,
            "ypos": trade_hub_ypos,
            "level": int(has_trade_hub)
        },
        "radius": math.ceil(largest_distance) + 1,
        "star_type": star_type,
        "asteroid_belt": asteroid_belt,
        "asteroid_belt_distance": asteroid_belt_distance,
        "planets": planets
    }