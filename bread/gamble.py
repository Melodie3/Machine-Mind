import random
import bread.values as values

# Brick - 0 and brick 
# Horsey - 0
# Loaf 2 - .25x
# Loaf 3 - .50x
# Special 1 - .25
# Special 2 - .5
# Special 3 - 2x
# Chess piece - 2x
# Chess 2 - 4x
# Chess 3 - 10x
# Anarchy - 10x

# filler_values = [values.horsey, values.horsey, values.horsey, values.horsey, values.horsey,
#                  values.garlic, values.garlic, values.garlic, values.garlic, values.garlic, 
#                  values.cherry, values.cherry, values.cherry, values.cherry, values.cherry,
#                  values.grapes, values.grapes, values.grapes, values.grapes, values.grapes, 
#                  values.apple,  values.apple,  values.apple,  values.apple,  values.apple
# ]

reward_values = [values.brick,
             values.horsey, values.horsey, values.horsey, values.horsey, values.horsey, 
             values.horsey, values.horsey, values.horsey, values.horsey, values.horsey,
             values.cherry, values.cherry, values.cherry, values.cherry, values.cherry, 
             values.cherry, values.cherry, values.cherry, values.cherry, values.cherry,
             values.normal_bread, values.normal_bread, values.normal_bread, values.normal_bread, values.normal_bread, 
             values.normal_bread, values.normal_bread, values.normal_bread, values.normal_bread, values.normal_bread, 
             values.sandwich,   values.croissant,   values.flatbread,   values.french_bread,      values.stuffed_flatbread,
             values.black_pawn, values.black_pawn,  values.black_pawn,  values.black_pawn,  values.black_pawn,
             values.anarchy,
]






def gamble(brick_troll = False) -> dict:
    """Generates a single item for a gamble board, including that item's reward."""

    # filler = filler_values.copy()
    # rewards = reward_values.copy()
    result = None
    found_result = False

    if brick_troll: # 100% brick
        chance_brick = 100
        chance_nothing = 0
        chance_quarter = 0
        chance_half = 0
        chance_double = 0
        chance_quadruple = 0
        chance_ten_times = 0

    else:
        chance_brick = 4
        chance_nothing = 19
        chance_quarter = 26
        chance_half = 25
        chance_double = 15
        chance_quadruple = 10
        chance_ten_times = 1
    
    total_chance = chance_brick + chance_nothing + chance_quarter + chance_half + chance_double + chance_quadruple + chance_ten_times

    rolled_chance = random.randint(1,total_chance)

    rolled_chance -= chance_brick
    if rolled_chance <= 0:
        result = random.choice(values.all_bricks_weighted)
        multiple = 0
        if result.name == "brick_gold":
            multiple = 10
        found_result = True

    rolled_chance -= chance_nothing
    if rolled_chance <= 0 and (found_result is False):
        result = values.horsey
        multiple = 0
        found_result = True
        pass

    rolled_chance -= chance_quarter
    if rolled_chance <= 0 and (found_result is False):
        result = random.choice([values.cherry, values.lemon, values.grapes])
        multiple = .25
        found_result = True
        pass

    rolled_chance -= chance_half
    if rolled_chance <= 0 and (found_result is False):
        result = values.normal_bread
        multiple = .5
        found_result = True
        pass

    rolled_chance -= chance_double
    if rolled_chance <= 0 and (found_result is False):
        result = random.choice(values.all_special_breads)
        multiple = 2
        found_result = True
        pass

    rolled_chance -= chance_quadruple
    if rolled_chance <= 0 and (found_result is False):
        # result = values.black_pawn
        result = random.choice((values.chess_pieces_black_biased)+[values.bcapy])
        multiple = 4
        found_result = True
        pass

    rolled_chance -= chance_ten_times
    if rolled_chance <= 0 and (found_result is False):
        result = random.choice([values.anarchy, values.anarchy_chess, values.holy_hell])
        multiple = 10
        found_result = True

    if  found_result is False: #if we still haven't found it
        print("Error: went out of bounds")
        raise

    output = {}
    output["result"] = result
    output["multiple"] = multiple
    return output
        

def randomize(array: list) -> list:
    """Shuffles a list. `random.shuffle()` is likely faster than this."""
    input = array.copy()
    output = []
    while len(input) != 0:
        index = random.randint(len(input))
        output.append(input.pop(index))
    return output

def gamble_test(iterations: int) -> None:
    """Manual gamble test via running a set number of iterations."""
    bricks = 0
    total_spent = 0
    total_earned = 0
    bet_amount = 40
    for i in range(iterations):
        total_spent += bet_amount

        result = gamble()
        total_earned +=  bet_amount * result["multiple"]

        if result["result"] == values.brick:
            bricks += 1
        pass
    
    print(f"ran for {iterations} iterations")
    print(f"Spent {total_spent} and earned {total_earned}")
    print(f"Leading to a ratio of {total_earned/total_spent}.")
    print(f"Also found {bricks} bricks.")
        
