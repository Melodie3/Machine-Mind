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

PATTERNS = ['SVS', 'VSV', 'SVVS', 'VSVS', 'SVSV']

SYLLABLES = [
    'Vah', 'Nab', 'Or', 'Is', 'Ter', 'Pho', 'Qua', 'Cos', 'Tek', 'Glo', 'Zor', 'Yul', 'Kor', 'Vex', 'Dra', 'Plu', 'Fyr', 
    'Bla', 'Grav', 'Hyp', 'Jex', 'Klyn', 'Morph', 'Nyx', 'Plex', 'Rhyn', 'Spect', 'Vex', 'Zyph', 'Grim', 'Slyth',
    'Xen', 'Chro', 'Drex', 'Kryp', 'Ryze', 'Shrym', 'Trex', 'Vex', 'Wrym', 'Xylo', 'Zygo', 'Myth', 'Glo', 'Vra', 'Zar'
]

VOWELS = ['a', 'e', 'i', 'o', 'u']

MAP_SIZE = 256

MAP_RADIUS = MAP_SIZE // 2
HALF_RADIUS = MAP_RADIUS // 2
MAP_RADIUS_SQUARED = MAP_RADIUS ** 2

# This is in `1 in __`, so an 8 means a 1/8 chance.
CHANCE_SYSTEM = 8 # Chance of any point being a system, assuming it doesn't have a system very close nearby.
CHANCE_TRADE = 3 # The chance of any generated system having a trading hub by default.

STAR_WEIGHTS = {
    "star1": 50,
    "star2": 22,
    "star3": 22,
    "black_hole": 6
}

PLANET_WEIGHTS = {
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

PLANET_OPTIONS = {
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

def generate_gradients(galaxy_seed: str) -> list:
    """Generates the gradient and nebulae info for the galaxy.

    Args:
        galaxy_seed (int): The seed of the galaxy.

    Returns:
        list: The gradient info in a list.
    """
    gradient_points = []

    seeded = random.Random(galaxy_seed)

    previous_angles = []
    for point in range(4): # 4 for gradient points, 2 for nebulae
        dist = MAP_RADIUS * ((seeded.random() / 2) + 0.25)

        if point > 3:
            dist += MAP_RADIUS / 16

        try:
            previous = sum(previous_angles) // len(previous_angles) * math.pi
        except ZeroDivisionError:
            previous = math.tau
        
        angle = (seeded.randrange(0, 360) + previous) % 360
        

        x = round(math.cos(math.radians(angle)) * dist)
        y = round(math.sin(math.radians(angle)) * dist)
        fold = seeded.randint(2, 5)
        rotation = seeded.randrange(0, 360)

        gradient_points.append((x, y, fold, rotation))

        previous_angles.append(angle)
    
    return gradient_points

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

def generate_nebulae(galaxy_seed: str) -> list[dict]:
    out = []
    previous_angle = 1

    nebula_count = max(round(random.Random(galaxy_seed).normalvariate(5, 1)), 1)
    for i in range(nebula_count):
        rng = random.Random(f"{galaxy_seed}_nebula_{i}")

        theta = rng.uniform(0, math.tau) # τ!! :3

        size_average = 32

        blob_x_size = max(min(rng.normalvariate(size_average, 20), size_average * 1.25), size_average * 0.75)
        blob_y_size = max(min(rng.normalvariate(blob_x_size, 20), blob_x_size * 1.25), blob_x_size * 0.75)

        blob_angle = rng.uniform(0, math.tau) - previous_angle
        previous_angle = blob_angle

        dist_range = int(max(blob_x_size, blob_y_size))
        blob_distance = rng.uniform(dist_range * 1.2, dist_range * 2.5)

        blob_location = [
            math.cos(blob_angle) * blob_distance,
            math.sin(blob_angle) * blob_distance
        ]

        exponent_modifier = rng.uniform(1, 3)
        max_depth = min(max(int(rng.normalvariate(5, 1)), 3), 7)

        out.append({
            "location": blob_location,
            "theta": theta,
            "size_x": blob_x_size,
            "size_y": blob_y_size,
            "modifier": exponent_modifier,
            "max_depth": max_depth
        })
        
    return out

def in_nebula(
        nebulae_info: list[dict],
        x: int,
        y: int
    ) -> bool:
    for data in nebulae_info:
        location = data["location"]
        size_x = data["size_x"]
        size_y = data["size_y"]
        modifier = data["modifier"]
        max_depth = data["max_depth"]
        theta = data["theta"]

        use = (
            (x - location[0]) / HALF_RADIUS / (size_x / HALF_RADIUS),
            (y - location[1]) / HALF_RADIUS / (size_y / HALF_RADIUS)
        )

        use = (
            use[0] * math.cos(theta) - use[1] * math.sin(theta),
            use[0] * math.sin(theta) + use[1] * math.cos(theta)
        )

        if use[0] ** 2 + use[1] ** 2 > 4:
            continue
        
        exponent = use[1] + modifier

        depth = mandelbrot(use, max_depth, exponent)

        if depth != max_depth:
            continue

        return True
    
    return False

def mandelbrot(
        coord: tuple[float, float],
        depth: int,
        exponent: float
    ) -> int:
    """Runs the Mandelbrot Set equation on the given coordinate up to the given depth, with the given exponent.
    
    Args:
        coord (tuple[float, float]): The coordinate to run the equation on.
        depth (int): The maximum depth to check.
        exponent (float): The exponent to use. It would be `d` in `z = z^d + c`.
    
    Returns:
        int: The last depth value at which it was within the radius 2 circle."""
    coord = complex(*coord)

    g = 0
    try:
        z = coord
        
        for g in range(depth):
            if z.imag ** 2 + z.real ** 2 > 4:
                return g + 1
            z = z ** exponent + coord

        return depth
    except (OverflowError, ZeroDivisionError):
        return g

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

    return rng.randint(1, int(CHANCE_SYSTEM + mod + gradient_mod) * CHANCE_TRADE)

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
    
    if (x ** 2 + y ** 2) > MAP_RADIUS_SQUARED:
        return 0

    rng = core_spot(
        galaxy_seed = galaxy_seed,
        x = x,
        y = y,
        rng = random.Random(),
        gradient_info = gradient_info
    )

    if rng > CHANCE_TRADE:
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
                ) <= CHANCE_TRADE:
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
    if gradient_info is None:
        gradient_info = generate_gradients(galaxy_seed)
    if nebulae_info is None:
        nebulae_info = generate_nebulae(galaxy_seed)
    
    point_info = get_spot(
        galaxy_seed = galaxy_seed,
        x = x - MAP_RADIUS,
        y = y - MAP_RADIUS,
        gradient_info = gradient_info
    )

    out = {
        "x": x,
        "y": y,
        "in_nebula": in_nebula(nebulae_info, x - MAP_RADIUS, y - MAP_RADIUS),
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

    gradient_info = generate_gradients(galaxy_seed)
    nebulae_info = generate_nebulae(galaxy_seed)

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

def get_all_wormholes(
        galaxy_seed: str,
        gradient_data: list = None,
        nebula_data: list = None
    ) -> list[tuple[dict[str, int, float], ...]]:
    """Generates all wormholes in a galaxy.

    Args:
        galaxy_seed (str): The seed of the galaxy this point is in.
        gradient_data (list, optional): Gradient data, will make this if nothing is passed. Defaults to None.
        nebula_data (list, optional): Nebula data, will make this if nothing is passed. Defaults to None.

    Returns:
        list[tuple[dict[str, int, float], ...]]: The list of points, as a list of tuples of 2 dicts.
    """
    raw_locations = []
    full_point_data = []

    wormhole_count = random.Random(galaxy_seed).gauss(mu=25, sigma=5)

    if wormhole_count < 1:
        wormhole_count = 1 - wormhole_count
    if wormhole_count > 49:
        wormhole_count = 49 - (wormhole_count - 49)

    wormhole_count = round(wormhole_count)

    for wormhole_id in range(wormhole_count):
        point_data = get_wormhole_points(
            galaxy_seed = galaxy_seed,
            existing_points = raw_locations,
            gradient_data = gradient_data,
            nebula_data = nebula_data
        )

        full_point_data.append(tuple(point_data))
        
        for data in point_data:
            raw_locations.append(data["location"])
    
    return full_point_data

    

def get_wormhole_points(
        galaxy_seed: str,
        existing_points: list[tuple[tuple[int, int], tuple[int, int]]],
        gradient_data: list = None,
        nebula_data: list = None
    ) -> list[dict[str, int, float]]:
    """Generates a single set of wormhole points.

    Args:
        galaxy_seed (str): The galaxy seed.
        existing_points (list[tuple[tuple[int, int], tuple[int, int]]]): Already generated wormholes, so it knows what to avoid.
        gradient_data (list, optional): Gradient data, will make this if nothing is passed. Defaults to None.
        nebula_data (list, optional): Nebula data, will make this if nothing is passed. Defaults to None.

    Returns:
        list[dict[str, int, float]]: The list of wormhole point data.
    """
    wormhole_id = len(existing_points) + 1
    
    if gradient_data is None:
        gradient_data = generate_gradients(galaxy_seed)
    if nebula_data is None:
        nebula_data = generate_nebulae(galaxy_seed)

    points = []
    out_data = []

    for point_id in range(2):
        seeded = random.Random(f"{galaxy_seed} wormhole {wormhole_id} point {point_id}")

        point_angle = seeded.randrange(0, 360)
        point_distance = seeded.randint(42, 128)

        check_x = round(math.cos(math.radians(point_angle)) * point_distance) + MAP_RADIUS
        check_y = round(math.sin(math.radians(point_angle)) * point_distance) + MAP_RADIUS

        check_data = galaxy_single(
            galaxy_seed = galaxy_seed,
            x = check_x,
            y = check_y,
            gradient_info = gradient_data,
            nebulae_info = nebula_data
        )

        initial_angle = point_angle
        initial_distance = point_distance
        if not check_data.get("system", False):
            while True:
                point_angle += 1
                
                if point_angle >= 360:
                    point_angle = 0
                
                if point_angle == initial_angle:
                    if initial_distance > 85:
                        point_distance -= 1
                    else:
                        point_distance += 1

                check_x = round(math.cos(math.radians(point_angle)) * point_distance) + MAP_RADIUS
                check_y = round(math.sin(math.radians(point_angle)) * point_distance) + MAP_RADIUS

                check_data = galaxy_single(
                    galaxy_seed = galaxy_seed,
                    x = check_x,
                    y = check_y,
                    gradient_info = gradient_data,
                    nebulae_info = nebula_data
                )
                if check_data.get("system", False):
                    point = (check_x, check_y)

                    if not (point in points) and not (point in existing_points):
                        break
        else:
            point = (check_x, check_y)

        data = {
            "location": point,
            "distance": (initial_distance + 50) / 180,
            "angle": initial_angle
        }
        out_data.append(data)

        points.append(point)
        
    return out_data



###############################
#### SYSTEM GENERATION FUNCTIONS

def generate_system(
        galaxy_seed: str,
        galaxy_xpos: int,
        galaxy_ypos: int,
        get_wormholes: bool = True,
        all_wormholes: typing.Optional[list[dict]] = None
    ) -> typing.Union[dict, None]:
    """Generates the data for a system.

    Args:
        galaxy_seed (str): The seed of the galaxy this system is in.
        galaxy_xpos (int): The x position of the system within the galaxy.
        galaxy_ypos (int): The y position of the system within the galaxy.
        get_wormholes (bool, optional): Whether to determine whether there are wormholes in this system. Defaults to True.
        all_wormholes (typing.Optional[list[dict]], optional): The list of wormholes in this galaxy. If None is passed it will generate them. Defaults to None.

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

    gradient_info = generate_gradients(galaxy_seed)
    nebula_info = generate_nebulae(galaxy_seed)

    system_position = (galaxy_xpos, galaxy_ypos)

    system_type = get_spot(
        galaxy_seed = galaxy_seed,
        x = galaxy_xpos - MAP_RADIUS,
        y = galaxy_ypos - MAP_RADIUS,
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

    merchant_xpos = trade_hub_xpos * -1
    merchant_ypos = trade_hub_ypos * -1

    star_type = rng.choices(
        population = list(STAR_WEIGHTS.keys()),
        weights = list(STAR_WEIGHTS.values())
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
        planet_rng = random.Random(hashlib.sha256(str(galaxy_seed + str(galaxy_ypos) + str(galaxy_xpos) + "planet" + str(planet_id)).encode()).digest())

        planet_type = planet_rng.choices(
            population = list(PLANET_WEIGHTS.keys()),
            weights = list(PLANET_WEIGHTS.values())
        )[0]

        planet_type = planet_rng.choice(PLANET_OPTIONS[planet_type])

        deviation = planet_rng.normalvariate(
            mu = 1,
            sigma = 0.1
        )

        modified_id = planet_id + (1 if planet_id - 1 >= asteroid_belt_distance else 0)

        planet_distance = 2 + (modified_id + 1.5)# ** 1.712 # dont ask why that number lol

        distance_mod = planet_rng.normalvariate(mu = 1, sigma = 0.1)

        planet_angle = planet_rng.randrange(0, 360) # Orbiting code here?

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
    
    ###############################################################
    #### One quick thing in the middle.
        
    largest_distance = max(planets, key=lambda x: x["distance"])["distance"]
    
    ###############################################################
    #### Wormholes.
    wormhole_data = {
        "exists": False,
        "xpos": None,
        "ypos": None,
        "link_galaxy": None
    }
    
    if get_wormholes:
        if all_wormholes is None:
            all_wormholes = get_all_wormholes(
                galaxy_seed = galaxy_seed,
                gradient_data = gradient_info,
                nebula_data = nebula_info
            )
        
        pair_data = None
        angle = None
        distance = None
        for point1, point2 in all_wormholes:
            if point1.get("location") == system_position:
                angle = point1.get("angle")
                distance = point1.get("distance")
                pair_data = point2
                break
            elif point2.get("location") == system_position:
                angle = point2.get("angle")
                distance = point2.get("distance")
                pair_data = point1
                break
        
        if pair_data is not None:
            final_distance = largest_distance * distance

            wormhole_x = round(math.cos(math.radians(angle)) * final_distance)
            wormhole_y = round(math.sin(math.radians(angle)) * final_distance)

            wormhole_position = (wormhole_x, wormhole_y)

            trade_hub_pos = (trade_hub_xpos, trade_hub_ypos)
            planet_positions = [(planet.get("xpos"), planet.get("ypos")) for planet in planets]

            # If this tile is already taken up, then move the wormhole.
            # Asteroids are ignored here, since other things can overwrite them.
            if wormhole_position == trade_hub_pos or \
            wormhole_position in planet_positions or \
            wormhole_position == (0, 0):
                attempt_number = 0
                
                while True:
                    attempt_number += 1

                    wormhole_rng = random.Random(hashlib.sha256(str(galaxy_seed + str(galaxy_ypos) + str(galaxy_xpos) + "wormhole" + str(attempt_number)).encode()).digest())

                    distance = wormhole_rng.uniform(178 / 180, 92 / 180)
                    angle = wormhole_rng.randrange(0, 360)

                    wormhole_x = round(math.cos(math.radians(angle)) * final_distance)
                    wormhole_y = round(math.sin(math.radians(angle)) * final_distance)

                    wormhole_position = (wormhole_x, wormhole_y)
                    if not(wormhole_position == trade_hub_pos or \
                    wormhole_position in planet_positions or \
                    wormhole_position == (0, 0)):
                        break
            
            wormhole_data = {
                "exists": True,
                "xpos": wormhole_x,
                "ypos": wormhole_y,
                "link_galaxy": pair_data.get("location")
            }


    
    
    
    ###############################################################
    
    return {
        "trade_hub": {
            "exists": has_trade_hub,
            "xpos": trade_hub_xpos,
            "ypos": trade_hub_ypos,
            "level": int(has_trade_hub)
        },
        "merchant": {
            "xpos": merchant_xpos,
            "ypos": merchant_ypos
        },
        "wormhole": wormhole_data,
        "radius": math.ceil(largest_distance) + 1,
        "star_type": star_type,
        "asteroid_belt": asteroid_belt,
        "asteroid_belt_distance": asteroid_belt_distance,
        "planets": planets
    }

def get_trade_hub_name(
        galaxy_seed: str,
        galaxy_x: int,
        galaxy_y: int
    ) -> str:
    """Generates a name for the trade hub at a given location.

    Args:
        galaxy_seed (str): The seed of the galaxy this trade hub is in.
        galaxy_x (int): The x position within the galaxy.
        galaxy_y (int): The y position within the galaxy.

    Returns:
        str: The generated name.
    """
    rng = random.Random(hashlib.sha256(str(galaxy_seed + str(galaxy_x) + str(galaxy_y) + "trade_hub").encode()).digest())
    pattern = rng.choice(PATTERNS)
    name_parts = []
    for char in pattern:
        if char == 'S':
            name_parts.append(rng.choice(SYLLABLES))
        elif char == 'V':
            name_parts.append(rng.choice(VOWELS))
    
    if rng.random() < 0.3:
        num_words = rng.randint(2, 3)
        for i in range(num_words - 1):
            name_parts.insert(rng.randrange(len(name_parts)), " ")
    
    result = ''.join(name_parts).lower().title()
    
    result = result.replace("  ", " ").strip()
    
    return result

def get_galaxy_spawn(galaxy_seed: str) -> tuple[int, int]:
    """Returns the spawn location of a galaxy.

    Args:
        galaxy_seed (str): The seed of the galaxy.

    Returns:
        tuple[int, int]: The x and y positions of the spawn point.
    """

    rng = random.Random(galaxy_seed)

    # Get a random angle from the galaxy seed.
    angle = rng.randrange(0, 360)

    # Calculate the exact location from the angle via sine and cosine.
    spawn_x = math.cos(math.radians(angle)) * 83
    spawn_y = math.sin(math.radians(angle)) * 83

    spawn_data = galaxy_single(galaxy_seed, round(spawn_x + MAP_RADIUS), round(spawn_y + MAP_RADIUS))

    # If the initially chosen point is in a nebula, then move it to not be in a nebula.
    if spawn_data.get("in_nebula", False):
        for attempts in range(25):
            # Make 25 attempts to move it. If this doesn't work, oh well.
            rng = random.Random(f"{galaxy_seed} attempt {attempts}")
            angle = rng.randrange(0, 360)

            spawn_x = math.cos(math.radians(angle)) * 83
            spawn_y = math.sin(math.radians(angle)) * 83

            spawn_data = galaxy_single(galaxy_seed, round(spawn_x + MAP_RADIUS), round(spawn_y + MAP_RADIUS))
            if not spawn_data.get("in_nebula", False):
                # If this new point is not in a nebula, break out of the loop.
                break
    
    # We have found an open point, now to try and find a nearby system.
    if not spawn_data.get("system", False):
        # The initially chosen point was not a system, big surprise.
        for angle_mod_amount in range(359):
            angle_mod = (angle_mod_amount + 1) // 2 * (1 if angle_mod_amount % 2 == 0 else -1)

            for mod_amount in range(6):
                check_distance = 83 + ((mod_amount + 2) // 2 * (1 if mod_amount % 2 == 0 else -1))

                spawn_x = math.cos(math.radians(angle + angle_mod)) * check_distance
                spawn_y = math.sin(math.radians(angle + angle_mod)) * check_distance

                spawn_data = galaxy_single(galaxy_seed, round(spawn_x + MAP_RADIUS), round(spawn_y + MAP_RADIUS))

                if spawn_data.get("system", False):
                    # We found a system!!
                    break
            else: # If it did not break out of the loop, so if it did not find a system.
                continue
            
            # If the `else` did not run, then it means it did break out of the inner loop, and thus it found a system.
            break
    
    return (round(spawn_x + MAP_RADIUS), round(spawn_y + MAP_RADIUS))