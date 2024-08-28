import bread.values as values
import typing

#recipes = {}

# wpawn = bpawn + bpawn + 50 specials
# wpawn = bpawn + bpawn + 25 rares
# wpawn = bpawn + bpawn + bpawn
# ":Bpawn:"

"""
New way to store alchemy recipes.
"cost" is the cost of the recipe, in a list of tuples containing the item and the number required.
"requirement" is a list of tuples containing any requirements for the recipe, None can be used for no requirements. None will also be used if "requirement" is excluded.
"result" is the number of output items to create. Will use 1 if it is not included.
"provide_no_dough" is an optional bool for whether to override dough being provided by the item.
Example item:
{
	"cost": [(values.anarchy_chess, 1)],
    "requirement": [("loaf_converter", 128)],
    "provide_no_dough": True,
	"result": 5
}
This would be a recipe that has a cost of 1 MoaK, has a requirement of at least 128 Loaf Converters, will not provide dough when made (if it did in the first place), and will produce 5 of the output item.
"""
recipes = {
    "Wpawn": [
        {
            "cost": [(values.black_pawn, 2), (values.doughnut, 10), (values.bagel, 10), (values.waffle, 10)]
        },
        {
            "cost": [(values.black_pawn, 2), (values.croissant, 10), (values.flatbread, 10), (values.stuffed_flatbread, 10), (values.sandwich, 10), (values.french_bread, 10)]
        },
        {
            "cost": [(values.black_pawn, 3)]
        },
        {
            "cost": [(values.gem_red, 2)]
        }
    ],
    "Wrook": [
        {
            "cost": [(values.black_rook, 1), (values.sandwich, 50), (values.waffle, 25)]
        },
        {
            "cost": [(values.black_rook, 2), (values.sandwich, 50)]
        },
        {
            "cost": [(values.black_rook, 3)]
        },
        {
            "cost": [(values.black_rook, 2), (values.waffle, 75)]
        },
        {
            "cost": [(values.gem_red, 2)]
        }
    ],
        "Wknight": [
        {
			"cost": [(values.black_knight, 1), (values.croissant, 50), (values.bagel, 25)]
		},
        {
			"cost": [(values.black_knight, 2), (values.croissant, 50)]
		},
        {
			"cost": [(values.black_knight, 3)]
		},
        {
			"cost": [(values.black_knight, 2), (values.bagel, 75)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Wbishop": [
        {
			"cost": [(values.black_bishop, 1), (values.french_bread, 50), (values.doughnut, 25)]
		},
        {
			"cost": [(values.black_bishop, 2), (values.french_bread, 50)]
		},
        {
			"cost": [(values.black_bishop, 3)]
		},
        {
			"cost": [(values.black_bishop, 2), (values.doughnut, 75)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Wqueen": [
        {
			"cost": [(values.black_queen, 1), (values.stuffed_flatbread, 50), (values.doughnut, 25)]
		},
        {
			"cost": [(values.black_queen, 2), (values.stuffed_flatbread, 50)]
		},
        {
			"cost": [(values.black_queen, 3)]
		},
        {
			"cost": [(values.black_queen, 2), (values.doughnut, 75)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Wking": [
        {
			"cost": [(values.black_king, 1), (values.flatbread, 50), (values.bagel, 25)]
		},
        {
			"cost": [(values.black_king, 2), (values.flatbread, 50)]
		},
        {
			"cost": [(values.black_king, 3)]
		},
        {
			"cost": [(values.black_king, 2), (values.bagel, 75)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    ######################################################################################

    "Bpawn": [
        {
			"cost": [(values.white_pawn, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Brook": [
        {
			"cost": [(values.white_rook, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Bknight": [
        {
			"cost": [(values.white_knight, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Bbishop": [
        {
			"cost": [(values.white_bishop, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Bqueen": [
        {
			"cost": [(values.white_queen, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    "Bking": [
        {
			"cost": [(values.white_king, 1)]
		},
        {
			"cost": [(values.gem_red, 2)]
		}
    ],

    ######################################################################################


    "gem_gold": [
        {
			"cost": [(values.gem_green, 2), (values.gem_purple, 4), (values.gem_blue, 8), (values.gem_red, 16)]
		},
        {
			"cost": [(values.normal_bread, 10000), 
            (values.croissant, 1000), (values.flatbread, 1000), (values.stuffed_flatbread, 1000), (values.sandwich, 1000), (values.french_bread, 1000),
            (values.doughnut, 500), (values.bagel, 500), (values.waffle, 500)]
		},
        {
            "cost": [(values.anarchy_chess, 1)],
            "requirement": [("loaf_converter", 128)],
            "provide_no_dough": True
        }
    ],

    "gem_green": [
        {
			"cost": [(values.gem_purple, 2)]
		},
        {
			"cost": [(values.gem_gold, 1)],
            "result": 4
		}
    ],

    "gem_purple": [
        {
			"cost": [(values.gem_blue, 2)]
		},
        {
			"cost": [(values.gem_green, 1)]
		}
    ],

    "gem_blue": [
        {
			"cost": [(values.gem_red, 2)]
		},
        {
			"cost": [(values.gem_purple, 1)]
		}
    ],

    "gem_red": [
        {
			"cost": [(values.gem_blue, 1)]
		}
    ],

    ######################################################################################

    "omega_chessatron": [
        {
			"cost": [(values.chessatron, 5), (values.anarchy_chess, 1), 
            (values.gem_gold, 1), (values.gem_green, 1), (values.gem_purple, 1), (values.gem_blue, 1), (values.gem_red, 1),
			]
		}
    ],

    "anarchy_omega_chessatron": [
        {
            "cost": [(values.chessatron, 25), (values.omega_chessatron, 1), (values.anarchy_chessatron, 5)]
        }
    ],

    "fuel": [
        {
            "cost": [(values.gem_red, 2)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.gem_blue, 2)],
            "requirement": [("space_level", 1), ("fuel_research", 1)],
            "result": 3
        },
        {
            "cost": [(values.gem_purple, 2)],
            "requirement": [("space_level", 1), ("fuel_research", 2)],
            "result": 9
        },
        {
            "cost": [(values.gem_green, 2)],
            "requirement": [("space_level", 1), ("fuel_research", 3)],
            "result": 27
        },
        {
            "cost": [(values.gem_gold, 2)],
            "requirement": [("space_level", 1), ("fuel_research", 4)],
            "result": 150
        }
    ],

    ######################################################################################

    "holy_hell": [
        {
			"cost": [ (values.anarchy_chess, 5) ]
		}
    ],

    "anarchy": [
        {
			"cost": [(values.anarchy_chess, 5)]
		}
    ],

    "horsey": [
        {
			"cost": [(values.anarchy_chess, 5)]
		}
    ],

    ######################################################################################

    "bread": [
        {
            "cost": [(values.corrupted_bread, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    ######################################################################################

    "doughnut": [
        {
			"cost": [(values.normal_bread, 25)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.bagel, 2)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.waffle, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 75)],
            "requirement": [("space_level", 1)]
        }
    ],

    "bagel": [
        {
			"cost": [(values.normal_bread, 25)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.doughnut, 2)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.waffle, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 75)],
            "requirement": [("space_level", 1)]
        }
    ],

    "waffle": [
        {
			"cost": [(values.normal_bread, 25)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.doughnut, 2)]
		},
        {
			"cost": [(values.normal_bread, 10), (values.bagel, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 75)],
            "requirement": [("space_level", 1)]
        }
    ],

    ######################################################################################

    "flatbread": [
        {
			"cost": [(values.normal_bread, 10)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.stuffed_flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.sandwich, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.french_bread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.croissant, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 25)],
            "requirement": [("space_level", 1)]
        }
    ],

    "stuffed_flatbread": [
        {
			"cost": [(values.normal_bread, 10)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.sandwich, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.french_bread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.croissant, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 25)],
            "requirement": [("space_level", 1)]
        }
    ],

    "sandwich": [
        {
			"cost": [(values.normal_bread, 10)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.stuffed_flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.french_bread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.croissant, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 25)],
            "requirement": [("space_level", 1)]
        }
    ],

    "french_bread": [
        {
			"cost": [(values.normal_bread, 10)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.stuffed_flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.sandwich, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.croissant, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 25)],
            "requirement": [("space_level", 1)]
        }
    ],

    "croissant": [
        {
			"cost": [(values.normal_bread, 10)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.stuffed_flatbread, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.sandwich, 2)]
		},
        {
			"cost": [(values.normal_bread, 5), (values.french_bread, 2)]
		},
        {
            "cost": [(values.corrupted_bread, 25)],
            "requirement": [("space_level", 1)]
        }
    ],

    ######################################################################################

    "Wpawnanarchy": [
        {
            "cost": [(values.anarchy_black_pawn, 2), (values.white_pawn, 50), (values.doughnut, 100), (values.bagel, 100), (values.waffle, 100), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_pawn, 2), (values.white_pawn, 50), (values.croissant, 100), (values.stuffed_flatbread, 100), (values.flatbread, 100), (values.sandwich, 100), (values.french_bread, 100), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_pawn, 3), (values.white_pawn, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_pawn, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Wknightanarchy": [
        {
            "cost": [(values.anarchy_black_knight, 1), (values.white_knight, 75), (values.croissant, 500), (values.bagel, 250), (values.gem_purple, 5)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_knight, 2), (values.white_knight, 50), (values.croissant, 500), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_knight, 3), (values.white_knight, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_knight, 2), (values.white_knight, 50), (values.bagel, 750), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_knight, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Wbishopanarchy": [
        {
            "cost": [(values.anarchy_black_bishop, 1), (values.white_bishop, 75), (values.french_bread, 500), (values.doughnut, 250), (values.gem_purple, 5)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_bishop, 2), (values.white_bishop, 50), (values.french_bread, 500), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_bishop, 3), (values.white_bishop, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_bishop, 2), (values.white_bishop, 50), (values.doughnut, 750), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_bishop, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Wrookanarchy": [
        {
            "cost": [(values.anarchy_black_rook, 1), (values.white_rook, 75), (values.sandwich, 500), (values.waffle, 250), (values.gem_purple, 5)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_rook, 2), (values.white_rook, 50), (values.sandwich, 500), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_rook, 3), (values.white_rook, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_rook, 2), (values.white_rook, 50), (values.waffle, 750), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_rook, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Wqueenanarchy": [
        {
            "cost": [(values.anarchy_black_queen, 1), (values.white_queen, 75), (values.stuffed_flatbread, 500), (values.doughnut, 250), (values.gem_purple, 5)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_queen, 2), (values.white_queen, 50), (values.stuffed_flatbread, 500), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_queen, 3), (values.white_queen, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_queen, 2), (values.white_queen, 50), (values.doughnut, 750), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_queen, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Wkinganarchy": [
        {
            "cost": [(values.anarchy_black_king, 1), (values.white_king, 75), (values.flatbread, 500), (values.bagel, 250), (values.gem_purple, 5)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_king, 2), (values.white_king, 50), (values.flatbread, 500), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_king, 3), (values.white_king, 25), (values.gem_purple, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.anarchy_black_king, 2), (values.white_king, 50), (values.bagel, 750), (values.gem_purple, 3)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.white_king, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    ######################################################################################

    "Bpawnanarchy": [
        {
            "cost": [(values.anarchy_white_pawn, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_pawn, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Bknightanarchy": [
        {
            "cost": [(values.anarchy_white_knight, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_knight, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Bbishopanarchy": [
        {
            "cost": [(values.anarchy_white_bishop, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_bishop, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Brookanarchy": [
        {
            "cost": [(values.anarchy_white_rook, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_rook, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Bqueenanarchy": [
        {
            "cost": [(values.anarchy_white_queen, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_queen, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    "Bkinganarchy": [
        {
            "cost": [(values.anarchy_white_king, 1)],
            "requirement": [("space_level", 1)]
        },
        {
            "cost": [(values.black_king, 250), (values.gem_green, 10)],
            "requirement": [("space_level", 1)]
        }
    ],

    ######################################################################################
}

# Old recipe storage.
"""
recipes = {
    "Wpawn": [ 
        [(values.black_pawn, 2), (values.doughnut, 10), (values.bagel, 10), (values.waffle, 10)],
        [(values.black_pawn, 2), (values.croissant, 10), (values.flatbread, 10), (values.stuffed_flatbread, 10), (values.sandwich, 10), (values.french_bread, 10)],
        [(values.black_pawn, 3)],
        [(values.gem_red, 1)],
    ],

    "Wrook": [
        [(values.black_rook, 1), (values.sandwich, 50), (values.waffle, 25)],
        [(values.black_rook, 2), (values.sandwich, 50)],
        [(values.black_rook, 3)],
        [(values.black_rook, 2), (values.waffle, 75)],
        [(values.gem_red, 1)],
    ],

    "Wknight": [
        [(values.black_knight, 1), (values.croissant, 50), (values.bagel, 25)],
        [(values.black_knight, 2), (values.croissant, 50)],
        [(values.black_knight, 3)],
        [(values.black_knight, 2), (values.bagel, 75)],
        [(values.gem_red, 1)],
    ],

    "Wbishop": [
        [(values.black_bishop, 1), (values.french_bread, 50), (values.doughnut, 25)],
        [(values.black_bishop, 2), (values.french_bread, 50)],
        [(values.black_bishop, 3)],
        [(values.black_bishop, 2), (values.doughnut, 75)],
        [(values.gem_red, 1)],
    ],

    "Wqueen": [
        [(values.black_queen, 1), (values.stuffed_flatbread, 50), (values.doughnut, 25)],
        [(values.black_queen, 2), (values.stuffed_flatbread, 50)],
        [(values.black_queen, 3)],
        [(values.black_queen, 2), (values.doughnut, 75)],
        [(values.gem_red, 1)],
    ],

    "Wking": [
        [(values.black_king, 1), (values.flatbread, 50), (values.bagel, 25)],
        [(values.black_king, 2), (values.flatbread, 50)],
        [(values.black_king, 3)],
        [(values.black_king, 2), (values.bagel, 75)],
        [(values.gem_red, 1)],
    ],

    "Bpawn": [
        [(values.white_pawn, 1)],
        [(values.gem_red, 1)],
    ],

    "Brook": [
        [(values.white_rook, 1)],
        [(values.gem_red, 1)],
    ],

    "Bknight": [
        [(values.white_knight, 1)],
        [(values.gem_red, 1)],
    ],

    "Bbishop": [
        [(values.white_bishop, 1)],
        [(values.gem_red, 1)],
    ],

    "Bqueen": [
        [(values.white_queen, 1)],
        [(values.gem_red, 1)],
    ],

    "Bking": [
        [(values.white_king, 1)],
        [(values.gem_red, 1)],
    ],


    "gem_gold": [
        [(values.gem_green, 2), (values.gem_purple, 4), (values.gem_blue, 8), (values.gem_red, 16)],

        [(values.normal_bread, 10000), 
            (values.croissant, 1000), (values.flatbread, 1000), (values.stuffed_flatbread, 1000), (values.sandwich, 1000), (values.french_bread, 1000),
            (values.doughnut, 500), (values.bagel, 500), (values.waffle, 500)],
    ],

    "gem_green": [
        [(values.gem_purple, 2)],
        [(values.gem_gold, 1)],
    ],

    "gem_purple": [
        [(values.gem_blue, 2)],
        [(values.gem_green, 1)],
    ],

    "gem_blue": [
        [(values.gem_red, 2)],
        [(values.gem_purple, 1)],
    ],

    "gem_red": [
        [(values.gem_blue, 1)]
    ],

    "omega_chessatron": [
        [(values.chessatron, 5), (values.anarchy_chess, 1), 
            (values.gem_gold, 1), (values.gem_green, 1), (values.gem_purple, 1), (values.gem_blue, 1), (values.gem_red, 1),
        ]
    ],

    "holy_hell": [
        [ (values.anarchy_chess, 5) ],
    ],

    "anarchy": [
        [(values.anarchy_chess, 5)],
    ],

    "horsey": [
        [(values.anarchy_chess, 5)],
    ],

    "doughnut": [
        [(values.normal_bread, 25)],
    ],

    "bagel": [
        [(values.normal_bread, 25)],
    ],

    "waffle": [
        [(values.normal_bread, 25)],
    ],

    "flatbread": [
        [(values.normal_bread, 10)],
    ],

    "stuffed_flatbread": [
        [(values.normal_bread, 10)],
    ],

    "sandwich": [
        [(values.normal_bread, 10)],
    ],

    "french_bread": [
        [(values.normal_bread, 10)],
    ],

    "croissant": [
        [(values.normal_bread, 10)],
    ],

}       
"""

def alchemy(
        target_item: values.Emote,
        item1: typing.Any, # I have no idea what types these were supposed to be.
        item2: typing.Any,
        item3: typing.Any
    ) -> None:
    """Unfinished alchemy function. Does nothing."""
    target_name = target_item.name.lower()
    if target_name in recipes.keys():
        target_recipes = recipes[target_name]
        for recipe in target_recipes:
            if item1 is not None and item2 is not None and item3 is not None:
                pass

    pass

def describe_individual_recipe(recipe: dict) -> str:
    """Describes a recipe, as taken from the full recipes dict."""
    output = ""
    for i in range(len(recipe["cost"])):
    #for pair in recipe:
        pair = recipe["cost"][i]
        item = pair[0]
        amount = pair[1]
        output += f"{amount} {item.text}"
        if i < len(recipe["cost"]) - 1:
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
