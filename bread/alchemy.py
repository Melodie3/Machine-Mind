import bread.values as values

#recipes = {}

# wpawn = bpawn + bpawn + 50 specials
# wpawn = bpawn + bpawn + 25 rares
# wpawn = bpawn + bpawn + bpawn
# ":Bpawn:"

recipes = {
    "Wpawn" : [ 
        [(values.black_pawn, 2), (values.doughnut, 10), (values.bagel, 10), (values.waffle, 10)],
        [(values.black_pawn, 2), (values.croissant, 10), (values.flatbread, 10), (values.stuffed_flatbread, 10), (values.sandwich, 10), (values.french_bread, 10)],
        [(values.black_pawn, 3)],
        [(values.gem_red, 1)],
    ],

    "Wrook" : [
        [(values.black_rook, 1), (values.sandwich, 50), (values.waffle, 25)],
        [(values.black_rook, 2), (values.sandwich, 50)],
        [(values.black_rook, 3)],
        [(values.black_rook, 2), (values.waffle, 75)],
        [(values.gem_red, 1)],
    ],

    "Wknight" : [
        [(values.black_knight, 1), (values.croissant, 50), (values.bagel, 25)],
        [(values.black_knight, 2), (values.croissant, 50)],
        [(values.black_knight, 3)],
        [(values.black_knight, 2), (values.bagel, 75)],
        [(values.gem_red, 1)],
    ],

    "Wbishop" : [
        [(values.black_bishop, 1), (values.french_bread, 50), (values.doughnut, 25)],
        [(values.black_bishop, 2), (values.french_bread, 50)],
        [(values.black_bishop, 3)],
        [(values.black_bishop, 2), (values.doughnut, 75)],
        [(values.gem_red, 1)],
    ],

    "Wqueen" : [
        [(values.black_queen, 1), (values.stuffed_flatbread, 50), (values.doughnut, 25)],
        [(values.black_queen, 2), (values.stuffed_flatbread, 50)],
        [(values.black_queen, 3)],
        [(values.black_queen, 2), (values.doughnut, 75)],
        [(values.gem_red, 1)],
    ],

    "Wking" : [
        [(values.black_king, 1), (values.flatbread, 50), (values.bagel, 25)],
        [(values.black_king, 2), (values.flatbread, 50)],
        [(values.black_king, 3)],
        [(values.black_king, 2), (values.bagel, 75)],
        [(values.gem_red, 1)],
    ],

    "Bpawn" : [
        [(values.white_pawn, 1)],
        [(values.gem_red, 1)],
    ],

    "Brook" : [
        [(values.white_rook, 1)],
        [(values.gem_red, 1)],
    ],

    "Bknight" : [
        [(values.white_knight, 1)],
        [(values.gem_red, 1)],
    ],

    "Bbishop" : [
        [(values.white_bishop, 1)],
        [(values.gem_red, 1)],
    ],

    "Bqueen" : [
        [(values.white_queen, 1)],
        [(values.gem_red, 1)],
    ],

    "Bking" : [
        [(values.white_king, 1)],
        [(values.gem_red, 1)],
    ],


    "gem_gold" : [
        [(values.gem_green, 2), (values.gem_purple, 4), (values.gem_blue, 8), (values.gem_red, 16)],

        [(values.normal_bread, 10000), 
            (values.croissant, 1000), (values.flatbread, 1000), (values.stuffed_flatbread, 1000), (values.sandwich, 1000), (values.french_bread, 1000),
            (values.doughnut, 500), (values.bagel, 500), (values.waffle, 500)],
    ],

    "gem_green" : [
        [(values.gem_purple, 2)],
        [(values.gem_gold, 1)],
    ],

    "gem_purple" : [
        [(values.gem_blue, 2)],
        [(values.gem_green, 1)],
    ],

    "gem_blue" : [
        [(values.gem_red, 2)],
        [(values.gem_purple, 1)],
    ],

    "gem_red" : [
        [(values.gem_blue, 1)]
    ],

    "omega_chessatron" : [
        [(values.chessatron, 5), (values.anarchy_chess, 1), 
            (values.gem_gold, 1), (values.gem_green, 1), (values.gem_purple, 1), (values.gem_blue, 1), (values.gem_red, 1),
        ]
    ],

    "holy_hell" : [
        [ (values.anarchy_chess, 5) ],
    ],

    "anarchy" : [
        [(values.anarchy_chess, 5)],
    ],

    "horsey" : [
        [(values.anarchy_chess, 5)],
    ],

    "doughnut" : [
        [(values.normal_bread, 25)],
    ],

    "bagel" : [
        [(values.normal_bread, 25)],
    ],

    "waffle" : [
        [(values.normal_bread, 25)],
    ],

    "flatbread" : [
        [(values.normal_bread, 10)],
    ],

    "stuffed_flatbread" : [
        [(values.normal_bread, 10)],
    ],

    "sandwich" : [
        [(values.normal_bread, 10)],
    ],

    "french_bread" : [
        [(values.normal_bread, 10)],
    ],

    "croissant" : [
        [(values.normal_bread, 10)],
    ],

}       

def alchemy(target_item, item1, item2, item3):
    target_name = target_item.name.lower()
    if target_name in recipes.keys():
        target_recipes = recipes[target_name]
        for recipe in target_recipes:
            if item1 is not None and item2 is not None and item3 is not None:
                pass

    pass

def describe_individual_recipe(recipe):
    output = ""
    for i in range(len(recipe)):
    #for pair in recipe:
        pair = recipe[i]
        item = pair[0]
        amount = pair[1]
        output += f"{amount} {item.text}"
        if i < len(recipe) - 1:
            output += ",  "
    return output

# wrook = { wrook : { cost: 2, item: brook}}}

# bread alchemize wrook
# "You wish to create a Wrook. What is your first offering? Respond only with the name of the item you wish to use, or the word 'nothing.'"
# "$offer 1"
# "You wish to create a Wrook. What is your second offering?"
# "$offer 2"
# "You wish to create a Wrook. What is your third offering?"
# "$offer 3"
# "Sorry, but those offerings do not seem to have worked. Please try again."
# alternately "This will cost you $cost. Do you wish to continue?"
# "$continue"