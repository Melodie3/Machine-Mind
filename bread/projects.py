"""This houses all the projects that can spawn in Bread Space."""

from __future__ import annotations

import typing
import random
import math

import bread.space as space
import bread.values as values
import bread.account as account
import bread.utility as utility
import bread.store as store

class Project:
    internal = "project"

    # Optional for subclasses.
    @classmethod
    def display_info(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            compress_description: bool = False,
            completed: bool = False
        ) -> str:
        """Returns a string that represents this project, it includes the name and description, as well as some text if the project has been completed."""
        name = cls.name(day_seed, system_tile)
        description = cls.description(day_seed, system_tile)

        if compress_description:
            description_use = description[:250]
            if not description_use.endswith(" "):
                description_use += description[250:].split(" ")[0]
            
            description_use = description_use.strip()

            if description_use.endswith("."):
                description_use += ".."
            else:
                description_use += "..."
        else:
            description_use = description

        completed_prefix = "~~" if completed else ""
        completed_suffix = "~~    COMPLETED" if completed else ""

        return f"   **{completed_prefix}{name}:{completed_suffix}**\n{description_use}"

    # Required for subclasses.
    @classmethod
    def name(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        """The project's name, this should be based on the day seed, and return the same thing with the same day seed and system tile."""
        return "Project name"

    # Required for subclasses.
    @classmethod
    def description(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        """The project's description, this should be based on the day seed, and return the same thing with the same day seed and system tile."""
        return "Project description"

    # Required for subclasses.
    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        """The project's completion text, this is sent when the project is completed. This should be based on the day seed, and return the same thing with the same day seed and system tile."""
        return "Project completion"
    
    # Required for subclasses.
    @classmethod
    def get_cost(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        """The cost of this project, this should be based on the day seed, and return the same thing with the same day seed and system tile."""
        return [(values.gem_red.text, 100), ("total_dough", 200)]
    
    # Required for subclasses.
    @classmethod
    def get_reward(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        """The reward for completing this project, this should be based on the day seed, and return the same thing with the same day seed and system tile."""
        return [(values.gem_red.text, 100), ("total_dough", 200)]

    # Optional for subclasses.
    @classmethod
    def do_purchase(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            user_account: account.Bread_Account
        ) -> None:
        """This subtracts all the cost items from a single user account."""
        cost = cls.get_cost(day_seed, system_tile)

        for pair in cost:
            user_account.increment(pair[0], -pair[1])

    # Optional for subclasses.
    @classmethod
    def is_affordable_for(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            user_account: account.Bread_Account
        ) -> bool:
        """Returns a boolean for whether a single user account has all the items required for the cost."""
        cost = cls.get_cost(day_seed, system_tile)

        for pair in cost:
            if user_account.get(pair[0]) < pair[1]:
                return False
        
        return True
    
    # Optional for subclasses.
    @classmethod
    def get_price_description(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        """Formatted version of the cost in a string."""
        cost = cls.get_cost(day_seed, system_tile)

        output = ""
        for i in range(len(cost)):
            pair = cost[i]

            output += f"{utility.smart_number(pair[1])} {pair[0]}"
            if i != len(cost) - 1:
                output += " ,  "

        return output
    
    # Optional for subclasses.
    @classmethod
    def get_reward_description(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        """Formatted version of the reward in a string."""
        reward = cls.get_reward(day_seed, system_tile)

        output = ""
        for i in range(len(reward)):
            pair = reward[i]

            output += f"{utility.smart_number(pair[1])} {pair[0]}"
            if i != len(reward) - 1:
                output += " ,  "

        return output
    
    # Optional for subclasses.
    @classmethod
    def total_items_required(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> int:
        """Sums up all the required items into a single number."""
        cost = cls.get_cost(day_seed, system_tile)

        return sum([pair[1] for pair in cost])
    
    # Optional for subclasses.
    @classmethod
    def total_items_collected(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> int:
        """Uses the given project data to determine the number of items collected."""
        cost_sum = cls.total_items_required(day_seed, system_tile)

        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        return cost_sum - sum(remaining.values())
    
    # Optional for subclasses.
    @classmethod
    def get_progress_percent(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> float:
        """Returns a float representing this the percentage of items contributed to this project. Will be between 0 and 1."""
        cost_sum = cls.total_items_required(day_seed, system_tile)

        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        progress_sum = cost_sum - sum(remaining.values())

        return progress_sum / cost_sum
    
    # Optional for subclasses.
    @classmethod
    def get_remaining_items(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> dict[str, int]:
        """Returns a dict containing the amount of each item remaining.
        ```
        {
            "completed": False,
            "contributions": { # This dict is what's passed to the progress_data parameter.
                "user_id": {
                    "items": {
                        item1: amount,
                        item2: amount,
                        item3: amount
                    }
                }
            }
        }```"""
        remaining = dict(cls.get_cost(day_seed, system_tile))

        for data in progress_data.values():
            contributions = data.get("items", {})
            for item, amount in contributions.items():
                remaining[item] -= amount

                if remaining[item] <= 0:
                    remaining.pop(item)
        
        return remaining
    
    # Optional for subclasses.
    @classmethod
    def get_remaining_description(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> str:
        """Formatted version of the remaining items in a string."""
        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        output = []
        for item, amount in remaining.items():
            output.append(f"{utility.smart_number(amount)} {item}")

        return " ,  ".join(output)
        


#######################################################################################################
##### Trade hub levelling. ############################################################################
#######################################################################################################
    
class Trade_Hub(Project):
    internal = "trade_hub"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        return f"Trade Hub Level {system_tile.trade_hub_level + 1}"

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        distance = store.trade_hub_distances[system_tile.trade_hub_level]
        return f"A better Trade Hub that allows trading with those {distance} tiles away."

    @classmethod
    def all_costs(cls) -> list[tuple[str, int]]:
        return [
            # Level 1:
            [
                (values.anarchy_chess.text, 1), (values.chessatron.text, 20),
                (values.gem_gold.text, 100), (values.gem_green.text, 200), (values.gem_purple.text, 400), (values.gem_blue.text, 800), (values.gem_red.text, 1600),
                (values.doughnut.text, 10000), (values.waffle.text, 10000), (values.bagel.text, 10000),
                (values.croissant.text, 20000), (values.french_bread.text, 20000), (values.sandwich.text, 20000), (values.stuffed_flatbread.text, 20000), (values.flatbread.text, 20000)
            ],
            # Level 2:
            [
                (values.anarchy_chess.text, 5), (values.chessatron.text, 40),
                (values.gem_gold.text, 200), (values.gem_green.text, 400), (values.gem_purple.text, 800), (values.gem_blue.text, 1600), (values.gem_red.text, 3200),
                (values.doughnut.text, 20000), (values.waffle.text, 20000), (values.bagel.text, 20000),
                (values.croissant.text, 40000), (values.french_bread.text, 40000), (values.sandwich.text, 40000), (values.stuffed_flatbread.text, 40000), (values.flatbread.text, 40000)
            ],
            # Level 3:
            [
                (values.anarchy_chess.text, 10), (values.chessatron.text, 80),
                (values.gem_gold.text, 400), (values.gem_green.text, 800), (values.gem_purple.text, 1600), (values.gem_blue.text, 3200), (values.gem_red.text, 6400),
                (values.doughnut.text, 40000), (values.waffle.text, 40000), (values.bagel.text, 40000),
                (values.croissant.text, 80000), (values.french_bread.text, 80000), (values.sandwich.text, 80000), (values.stuffed_flatbread.text, 80000), (values.flatbread.text, 80000)
            ],
            # Level 4:
            [
                (values.anarchy_chess.text, 20), (values.chessatron.text, 160), (values.anarchy_chessatron.text, 1),
                (values.gem_gold.text, 800), (values.gem_green.text, 1600), (values.gem_purple.text, 3200), (values.gem_blue.text, 6400), (values.gem_red.text, 12800),
                (values.doughnut.text, 80000), (values.waffle.text, 80000), (values.bagel.text, 80000),
                (values.croissant.text, 160000), (values.french_bread.text, 160000), (values.sandwich.text, 160000), (values.stuffed_flatbread.text, 160000), (values.flatbread.text, 160000)
            ],
            # Level 5:
            [
                (values.anarchy_chess.text, 40), (values.chessatron.text, 320), (values.anarchy_chessatron.text, 4),
                (values.gem_gold.text, 1600), (values.gem_green.text, 3200), (values.gem_purple.text, 6400), (values.gem_blue.text, 12800), (values.gem_red.text, 25600),
                (values.doughnut.text, 160000), (values.waffle.text, 160000), (values.bagel.text, 160000),
                (values.croissant.text, 320000), (values.french_bread.text, 320000), (values.sandwich.text, 320000), (values.stuffed_flatbread.text, 320000), (values.flatbread.text, 320000)
            ],
        ]
    
    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        if random.randint(1, 32) != 1:
            return ""
        
        messages = [
            "The new Trade Hub employees are a little confused by the weird 'Spleen Room' in the yellow quadrant, but they'll get used to it.",
            "The existance of multiple Blåhaj in the green quadrant is slightly concerning, but it's probably fine."
        ]

        out = "\n"
        out += random.choice(messages)
        
        return out
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        if system_tile is None:
            level = 0
        else:
            level = system_tile.trade_hub_level
        return cls.all_costs()[level]
    
    @classmethod
    def get_reward(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        return [("total_dough", 2000000)] # Award 2 million dough on completion.
        
#######################################################################################################
##### Base project. ###################################################################################
#######################################################################################################

class Base_Project(Project):
    """Written by ???."""
    internal = "base_project"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = []

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = []

        part_2 = []

        part_3 = []

        part_4 = []
        
        part_5 = []

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = []

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        return []
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        return []


#######################################################################################################
##### Story projects. #################################################################################
#######################################################################################################

class Essential_Oils(Project):
    """Written by Duck."""
    internal = "essential_oils"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Essential Oils",
            "Bread Living",
            "Oil Offer",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "This is incredible!",
            "Woah!",
            "Oh, look!"
        ]

        part_2 = [
            "The officials at the Trade Hub have recieved an incredible offer!",
            "The higher-ups here have recieved an awesome invitation!",
            "The Trade Hub managers have gotten an interesting message!"
        ]

        part_3 = [
            f"\nFor the low low price of {cost}, the Trade Hub will be a part of the Bread Living company!",
            f"\nWith a cost of only {cost}, the Trade Hub will get to join the Bread Living!",
            f"\nBy paying just {cost}, you and the entire Trade Hub will join Bread Living!"
        ]

        part_4 = [
            "\nIf you get other people to join Bread Living, you will get a commission of every sale they make!",
            "\nWhen people you recruit sell anything you will get some money!"
        ]
        
        part_5 = [
            f"Bread Living guarantees you will make {reward} after signing up!",
            f"Bread Living advertises a profit of {reward}, and there's no way that's wrong!",
            f"As Bread Living claims, you will be making a profit of {reward}!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Great work, team! You've managed to join Bread Living and made a profit of {reward}!",
            f"Incredible work! You landed the job at Bread Living and made that {reward} profit just as promised!",
            f"Nice job! You provided all the resources required and made a profit of {reward} from joining Bread Living!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 50

        return [(values.fuel.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 50

        options = [
            values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, values.gem_red, 
            values.gem_blue, values.gem_blue, values.gem_blue, values.gem_blue, values.gem_blue, values.gem_blue, values.gem_blue, values.gem_blue, 
            values.gem_purple, values.gem_purple, values.gem_purple, values.gem_purple,
            values.gem_green, values.gem_green,
            values.gem_gold
        ]
        amounts = {
            values.gem_red: amount / 1 * 0.75,
            values.gem_blue: amount / 3 * 0.75,
            values.gem_purple: amount / 9 * 0.75,
            values.gem_green: amount / 27 * 0.75,
            values.gem_gold: amount / 150 * 0.75
        }

        item = rng.choice(options)

        return [(item.text, math.ceil(amounts[item]))]

class Bingobango(Project):
    """Written by Kapola."""
    internal = "bingobango"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Bingobango"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "bingo"
        ]

        part_2 = [
            "bango"
        ]

        part_3 = [
            f"bingobango {cost}..."
        ]

        part_4 = [
            f"bingobango {reward}"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            "bingobango!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        return [(values.anarchy_chess.text, 1)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 2000

        return [(values.normal_bread.text, amount)]


#######################################################################################################
##### Take item projects. #############################################################################
#######################################################################################################

##### Special bread.

class Beach_Disappearance(Project):
    """Concept by Duck, written by Kapola."""
    internal = "beach_disappearance"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Beach Disappearance",
            "Ecosystem Problem 2",
            "Sand Witches",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "So, the Trade Hub has an animal ecosystem on board.",
            "The Trade Hub design contains an on-board animal ecosystem.",
            "The current Trade Hub model has its own animal ecosystem."
        ]

        part_2 = [
            "Unfortunately, all the beaches on the ecosystem have mysteriously disappeared.",
            "However, it has been struck with a problem; all the beaches are suspiciously gone.",
            "There has been an issue with it recently though: the beaches are somehow all gone."
        ]

        part_3 = [
            "We don't know exactly how they all disappeared;",
            "The Trade Hub does not know the circumstances of the disappearance;",
            "It is unknown how all these beacues have disappeared;"
        ]

        part_4 = [
            "some think that they were washed away by the ocean,",
            "experts believe the sand washed away into the water,",
            "some believe the sand was gobbled up by the waters,"
        ]

        part_5 = [
            "while others think it was the work of a sand-eating demon.",
            "but others believe an ancient time spell is responsible.",
            "while some believe it was the result of a devastating burrito."
        ]

        part_6 = [
            "\nRegardless, we think we have found a solution;",
            "\nAnyways, the Trade Hub believes they have a solution;",
            "\nFortunately, a solution has most likely been found;"
        ]
        
        part_7 = [
            "it would involve summoning the sand back with some sandwitches.",
            "the sand would be summoned by sandwitches.",
            "sand could be brought back by the magical powers of sandwitches."
        ]

        part_8 = [
            "However, the Trade Hub doesn't have quite enough for the project;",
            "Unfortunately, the Hub doesn't keep enough of them on hand;",
            "However, we do not have enough for something at a scale this big;"
        ]

        part_9 = [
            "after all, the Hub is worried they might turn against us with their magical powers.",
            "the Trade Hub never knows when those unstable creatures might ally with the French for a revolution.",
            "we do not know what these unpredictable people will do if they discover we have been keeping their wands in secret."
        ]

        part_10 = [
            f"We'd be willing to offer you {reward} if you found {cost} willing to help!",
            f"You could get a huge {reward} from the Trade Hub if you found some {cost} for bringing the beaches back!",
            f"If you provided {cost} that were willing to help, the Trade Hub would reward you with {reward}!"
        ]


        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            f"Woo! Thanks to you, all the beaches are back and the animals have returned to their usual life!",
            f"Wow! All the beaches are back! I sure hope this drastic and radical environmental action won't cause any more problems in the future!",
            f"Well, we succeeded, but at what cost?? The sandwitches are storming the Hub! Uprising! We must warn the... *gets dumped on by a huge pile of sand*"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1280

        return [(values.sandwich.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 20

        item = rng.choice(values.chess_pieces_black_biased)

        return [(item.text, amount)]

class Croissant_Cravings(Project):
    """Written by Kapola"""
    internal = "croissant_cravings"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Croissant Cravings",
            "Alien Invasion",
            "Appease the Overlords",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "We have received a most peculiar visit!",
            "The Trade Hub is now the victim of an interesting arrival!",
            "Some strange entities have come to the Trade Hub!"
        ]

        part_2 = [
            "These alien overlords from a far away galaxy",
            "Some extraterrestrials",
            "A small group of aliens from outside our reach"
        ]

        part_3 = [
            "have come as a delegation to talk to our species!",
            "have arrived to this Trade Hub for negociations!",
            "are now here, and they are not happy!"
        ]

        part_4 = [
            "They threaten to destroy our entire galaxy,",
            "This Trade Hub, planet, and even indeed the whole galaxy,",
            "Their threats are most worrying; to destroy the galaxy,"
        ]

        part_5 = [
            "if their requests are not completely fulfilled!",
            "unless we can provide them with a huge offering!",
            "unless they are given a huge compensation!"
        ]

        part_6 = [
            "The overlords' power system is entirely powered by croissants,",
            "The aliens feed exclusively on the most excellent croissants,",
            "They are working on an artificial planet made entirely of croissants,"
        ]
        
        part_7 = [
            f"and they ask for {cost} for not making our galaxy implode!",
            f"and if {cost} are not provided, they will declare war on our galaxy!",
            f"and they require {cost} if we do not want to get blown to bits!"
        ]

        part_8 = [
            f"The Trade Hub offers {reward} in the name of the galaxy to anyone who can provide this!",
            f"We are ready to provide {reward} for anyone who can help us save the world!",
            f"Anyone who can give this will be rewarded with {reward} in the name of our galaxy!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Hooray! The offering of {cost} was provided and the aliens have left! Here is your reward!",
            f"It worked! The aliens have left! Thank you for your help and here are your {reward}!",
            f"You will be remembered here as the one who saved the galaxy from certain doom! And of course, your {reward} are here!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1920

        return [(values.croissant.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 30

        item = rng.choice(values.chess_pieces_black_biased)

        return [(item.text, amount)]

class Appease_The_French(Project):
    """Written by Lilly."""
    internal = "appease_the_french"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Appease the French",
            "Feed the French",
            "Pacify the French"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Revolution!",
            "Rebellion!",
            "An uprising is upon us!"
        ]

        part_2 = [
            "The local French population have begun rioting!",
            "The French employees on this trade hub have unionized and begun to riot!",
            "The French are up in arms!"
        ]

        part_3 = [
            "We told them they could have some cake, but that just made them angrier!",
            "Luckily, we can hide in our state-of-the-art armory for now!",
            "They seem really hungry, so we offered them some cake, but it didn't seem to help."
        ]

        part_4 = [
            "If we want to keep our heads, we'd better appease them.",
            "It's in our best interest to appease them to keep everything peaceful.",
            "We'd better find a peaceful solution before anyone loses their head."
        ]

        part_5 = [
            "As everyone knows, the best way to reason with a French person is to give them a baguette.",
            "Luckily, data from the cafeteria shows that each and every one of the protestors love baguettes.",
            "However, we know that French people love their baguettes!"
        ]

        part_6 = [
            f"According to our top analysts, we'd need {cost} to ensure a peaceful solution to this problem.",
            f"Our estimates suggest we need at least {cost} to end this conflict.",
            f"If we were to get {cost}, we could give them out to the protestors, ending the conflict swiftly."
        ]

        part_7 = [
            f"The management at this Trade Hub is offering a {reward} reward to anyone who can supply the baguettes necessary.",
            f"We at the Trade Hub are generously offering {reward} to any person who can supply the baguettes we need.",
            f"Our compensation fund is allowing {reward} to anyone who is willing to help end this revolution through yeasty means."
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Thank goodness! We got all the baguettes we needed to stop the revolution, and as compensation, you will recieve {reward}!",
            f"Just in time! The French were all given baguettes to appease them, and they've stopped revolting! As a thank you, please take {reward}!",
            f"That was close! The revolutionaries have successfully been appeased by giving them baguettes! As a thanks for helping, take {reward}!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1920

        return [(values.stuffed_flatbread.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 15

        return [(values.gem_red.text, amount)]

class Flatbread_Shortage(Project):
    """Concept by Lilly, written by Kapola."""
    internal = "flatbread_shortage"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Flatbread Shortage",
            "Not Enough Flatbreads",
            "Quick Destuffing",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "So, we just ran out of flatbreads.",
            "Well, the Trade Hub cafeteria just ran into a flatbread shortage.",
            "Unfortunately, the cafeteria here is short on flatbread today."
        ]

        part_2 = [
            "Moreover, tomorrow is NATIONAL FLATBREAD DAY! We CAN'T let this happen!",
            "And to make matters worse, tomorrow we have a delegation of... important people, who have heard about our famous flatbreads!",
            "We need some now, or else our flatbread-eating demon will destroy us for failing to provide our daily offering!"
        ]

        part_3 = [
            "We asked all around the Trade Hub for any spare flatbreads,",
            "We went everywhere to see if anyone had some flatbreads,",
            "The Trade Hub asked just about everyone here if anyone had anything,"
        ]

        part_4 = [
            "but we haven't been successful!",
            "but the Hub hasn't found a single seller!",
            "unfortunately there is no one ready to give anything!"
        ]

        part_5 = [
            "Plus, our next flatbread shipping is in a month's time!",
            "We won't get a cargo of flatbread for weeks either!",
            "The Trade Hub's next incoming flatbread shipping is in several weeks, so we can't count on that."
        ]

        part_6 = [
            "Thankfully, something might save us:",
            "An unlikely savior might be upon us, however:",
            "There are at least some good news:"
        ]
        
        part_7 = [
            "if we could just get some stuffed flatbreads instead,",
            "if the Hub got its hands on some stuffed flatbreads,",
            "if someone would just offer stuffed flatbreads instead,"
        ]

        part_8 = [
            "it would just be a matter of removing the stuffing to use the flatbreads,",
            "we would simply need to remove the stuffing,",
            "we could just remove the stuffing to get the flatbreads,"
        ]

        part_9 = [
            "and then store that for a later date!",
            "and then the stuffing could just be stored to use later!",
            "we have space to store that to use some other time!"
        ]

        part_10 = [
            f"The Trade Hub's analysts estimate they would need around {cost} to fill the demands,",
            f"The Trade Hub thinks a total of {cost} would be required for all flatbread requirements,",
            f"It is estimated that {cost} would be needed to have enough flatbreads;"
        ]

        part_11 = [
            f"moreover the Hub would be willing to give {reward} as thanks to anyone who would provide such a gift!",
            f"and {reward} could be given if you helped us in our task!",
            f"if you just helped us get there, these {reward} would be all yours!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
            rng.choice(part_11)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Okay, it was enough! Ah, right, your reward, here.",
            f"Thanks for your help! Here is your {reward}.",
            f"Ah, thankfully everything worked out in the end! Wondering when that extra stuffing will come in handy. By the way, here's your {reward}."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 960

        return [(values.stuffed_flatbread.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 10

        item = rng.choice(values.chess_pieces_white_biased)

        return [(item.text, amount)]

class Too_Much_Stuffing(Project):
    """Concept by Lilly, written by Kapola."""
    internal = "flatbread_shortage"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Too Much Stuffing",
            "Stuffed Flatbread Shortage",
            "Quick Restuffing",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "So, we just ran out of stuffed flatbreads.",
            "Well, the Trade Hub cafeteria just ran into a stuffed flatbread shortage.",
            "Unfortunately, the cafeteria here is short on stuffed flatbread today."
        ]

        part_2 = [
            "Moreover, tomorrow is NATIONAL STUFFED FLATBREAD DAY! We CAN'T let this happen!",
            "And to make matters worse, tomorrow we have a delegation of... important people, who have heard about our famous stuffed flatbreads!",
            "We need some now, or else our stuffed flatbread-eating god will destroy us for failing to provide our daily offering!"
        ]

        part_3 = [
            "We asked all around the Trade Hub for any spare stuffed flatbreads,",
            "We went everywhere to see if anyone had some stuffed flatbreads,",
            "The Trade Hub asked just about everyone here if anyone had anything,"
        ]

        part_4 = [
            "but we haven't been successful!",
            "but the Hub hasn't found a single seller!",
            "unfortunately there is no one ready to give anything!"
        ]

        part_5 = [
            "Plus, our next stuffed flatbread shipping is in a month's time!",
            "We won't get a cargo of stuffed flatbread for weeks either!",
            "The Trade Hub's next incoming stuffed flatbread shipping is in several weeks, so we can't count on that."
        ]

        part_6 = [
            "Thankfully, something might save us:",
            "An unlikely savior might be upon us, however:",
            "There are at least some good news:"
        ]
        
        part_7 = [
            "a lot of stuffing is just laying around in the Hub's food storage!",
            "loads of stuffing alone is in our storage!",
            "we have a bunch of leftover stuffing in the pantries!"
        ]

        part_8 = [
            "We don't exactly know where it came from,",
            "No one's sure why it's there,",
            "The Trade Hub has no record of its existence,"
        ]

        part_9 = [
            "but if we could just get some regular flatbreads,",
            "however if the Hub got its hands on some normal flatbreads,",
            "thankfully if someone would just offer flatbreads,"
        ]

        part_10 = [
            "the stuffing could just be put right in!",
            "it would just be a matter of filling them with the stuffing!",
            "we'd just need to put the stuffing back in!"
        ]

        part_11 = [
            f"The Trade Hub's analysts estimate they would need around {cost} to fill the demands,",
            f"The Trade Hub thinks a total of {cost} would be required for all stuffed flatbread requirements,",
            f"It is estimated that {cost} would be needed to have enough stuffed flatbreads;"
        ]

        part_12 = [
            f"moreover the Hub would be willing to give {reward} as thanks to anyone who would provide such a gift!",
            f"and {reward} could be given if you helped us in our task!",
            f"if you just helped us get there, these {reward} would be all yours!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
            rng.choice(part_11),
            rng.choice(part_12)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Okay, it was enough! Ah, right, your reward, here.",
            f"Thanks for your help! Here is your {reward}.",
            f"Ah, thankfully everything worked out in the end! Still wondering where that extra stuffing came from. What a strange thing, eh? By the way, here's your {reward}."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1440

        return [(values.flatbread.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 15

        item = rng.choice(values.chess_pieces_white_biased)

        return [(item.text, amount)]

##### Rare bread.

class Waffle_Machine(Project):
    """Concept by Emily, written by Duck."""
    internal = "waffle_machine"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Waffle Machine",
            "The Broken Machine",
            "Cafeteria Conflict",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Oh no!",
            "Oh no...",
            "Welp."
        ]

        part_2 = [
            "The officials at the Trade Hub have some unfortunate news.",
            "The Trade Hub's cafeteria staff have some bad news.",
            "The Trade Hub's staff have made a sad announcement."
        ]

        part_3 = [
            "\nThe waffle machine in the cafeteria is broken!",
            "\nThe cafeteria's waffle machine stopped working!",
            "\nThe Trade Hub's waffle machine is no longer functional!"
        ]

        part_4 = [
            "\nThis is very unfortunate,",
            "\nThis is not good,",
            "\nThis is bad,"
        ]

        part_5 = [
            "due to the fact that the next time another machine can be ordered is in a few days!",
            "because the Trade Hub can only get a replacement in a few days!",
            "because the Trade Hub doesn't have same-day delivery on waffle machines!"
        ]

        part_6 = [
            "In the time until a replacement can be acquired,",
            "In that time,",
            "Before another waffle machine arrives,"
        ]
        
        part_7 = [
            "nobody can have any waffles!",
            "no waffles can be made!",
            "the Trade Hub will have no waffles!"
        ]

        part_8 = [
            f"\nWith a supply of just {cost},",
            f"\nFor only {cost},",
            f"\nIf someone were able to provide {cost},"
        ]

        part_9 = [
            "the cafeteria would be able to have waffles until the replacement machine arrives!",
            "there would be enough waffles to go around for the few days required!",
            "everyone on the Trade Hub would be able to have waffles!"
        ]

        part_10 = [
            "But worry not, good deeds do not go without a reward!",
            "Don't worry, there is a reward for anyone who provides the needed waffles!",
            "The cafeteria staff will compensate someone who gives the waffles!"
        ]

        part_11 = [
            f"The reward for providing the waffles is {reward}!",
            f"The staff have announced a reward of {reward}!",
            f"The posted reward is {reward}!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
            rng.choice(part_11)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            f"Phew! That was close to a waffle-pocalypse! But luckily the waffles were provided! The Trade Hub has put in an order for a replacement waffle machine, but until that arrives everyone will have all the waffles they want!",
            f"Waffles! Congratulations! You provided all the needed waffles! The folks on the Trade Hub will have plenty of waffles to eat until the new waffle machine arrives!",
            f"Yay! You did it! The Trade Hub cafeteria staff have confirmed that they have more than enough waffles to supply the hungry Trade Hub staff!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1280

        return [(values.waffle.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 20

        return [(values.gem_red.text, amount)]

class Stolen_Donuts(Project):
    """Written by Kapola."""
    internal = "Stolen_Donuts"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Stolen Donuts",
            "Missing Donuts",
            "Duck Donuts"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "In the Trade Hub's cafeteria there are many shops,",
            "The Trade Hub's cafeteria has an abundance of stores,",
            "The cafeteria in the Trade Hub has a lot of stores,"
        ]

        part_2 = [
            "some of these stores sell useful items when traversing space, but some are restaurants.",
            "a portion of the stores sell things like gems, and a portion are restaurants.",
            "while a big chunk of the stores sell things useful to an adventurer, there are a few restaurants at the cafeteria."
        ]

        part_3 = [
            "Most of the time these restaurants run without problems,",
            "The majority of the time the restaurants serve customers perfectly fine,",
            "A lot of the time everything runs as expected at these restaurants,"
        ]

        part_4 = [
            "but not always...",
            "but Murphy's Law will always come true...",
            "but things are bound to go wrong..."
        ]

        part_5 = [
            "You see, the Duck Donuts location at this Trade Hub has run into a slight issue.",
            "As expected to happen eventually, the restaurant called Duck Donuts has found a problem.",
            "Around last Sunday, the Duck Donuts restaurant reported some troubling news."
        ]

        part_6 = [
            "All of their donut ingredients were stolen!",
            "Every single ingredient they had to make donuts was taken by a thief!",
            "The donut ingredients were robbed!"
        ]

        part_7 = [
            "Until the new ingredients can arrive from corporate",
            "Before new ingredients arrive",
            "Prior to new ingredients arriving"
        ]

        part_8 = [
            "Duck Donuts cannot serve anybody!",
            "nobody can get any donuts!",
            "no donuts can be served!"
        ]

        part_9 = [
            "A estimation from Duck Donuts",
            "A quick calculation",
            "The current DonutModel™️ "
        ]

        part_10 = [
            f"states that {cost} would be required to fill the gap.",
            f"says just {cost} would be sufficient to keep customers happy.",
            f"describes a scenario that would fix the issue, and it would only require {cost}!"
        ]

        part_11 = [
            f"If somebody is able to provide the donuts required, Duck Donuts says they will be rewarded with {reward}!",
            f"Duck Donuts has placed a bounty of {reward} to the first person able to provide the donuts required!",
            f"A reward of {reward} has been posted by Duck Donuts to be claimed by whoever helps them in their time of need!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
            rng.choice(part_11)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        cost = cls.get_price_description(day_seed, system_tile)

        options = [
            f"Yippee! The predictions were correct and exactly {cost} was sold!",
            f"It worked! Exactly {cost} was sold at Duck Donuts and everybody was happy!",
            "Very well done! All the donuts required were given and were all sold, every single one!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1280

        return [(values.doughnut.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 10

        return [(values.gem_blue.text, amount)]

class Ecosystem_Problem(Project):
    """Written by Duck."""
    internal = "ecosystem_problem"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Ecosystem Problem",
            "Stop it now!",
            "Nefarious Birds"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "So, the Trade Hub has an animal ecosystem on board.",
            "The Trade Hub design contains an on-board animal ecosystem.",
            "The current Trade Hub model has its own animal ecosystem."
        ]

        part_2 = [
            "Typically this ecosystem runs fine without human intervention,",
            "Normally the ecosystem runs without a hitch,",
            "Most of the time the ecosystem is self-sustaining and runs smoothly,"
        ]

        part_3 = [
            "but things have gone awry recently.",
            "but recently an issue has been spotted.",
            "but in the past few days the ecosystem overseers have noticed a problem."
        ]

        part_4 = [
            "Some birds have been seen recently doing something abnormal.",
            "More and more birds as of late have been spotted doing something weird.",
            "Most of the birds residing in a specific area have started doing something odd."
        ]

        part_5 = [
            "Instead of flying around their typical area, they have started flying over the sea instead.",
            "They've begun flying over the sea instead of their regular area.",
            "The birds have been flying above the sea instead of where they typically reside."
        ]

        part_6 = [
            "This is a big issue as they're no longer keeping the animal populations in check.",
            "This is a problem because the birds have stopped making sure the animal population is normal.",
            "By doing this the animal population is increasing to problematic amounts due to the absense of birds, which is a slight issue."
        ]

        part_7 = [
            f"The wildlife experts on board the Trade Hub have concluded that by releasing {cost} into the wild it would solve the problem.",
            f"The Trade Hub's wildlife experts think that adding {cost} to the ecosystem would result in things returning to normal.",
            f"Onboard wildlife experts have predicted that introducing {cost} to the environment would be sufficient and fix the issues."
        ]

        part_8 = [
            f"They are also offering {reward} to whoever is able to provide the needed items.",
            f"A reward of {reward} has been announced by the wildlife experts.",
            f"The wildlife experts have proposed {reward} to the first person to provide the required items."
        ]

        part_9 = [
            "They found it under a tree one day, are slightly concerned it's magical, and want to get rid of it.",
            "It was found in a cave on the west side of the ecosystem and the wildlife experts have their doubts as to whether it is actually from 1834 as Jeff keeps saying.",
            "The wildlife experts are concerned it is releasing Blåhaj into the atmosphere. While this is not necessarily bad they're concerned it may affect the trout population."
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            "It worked! The animal population has returned to normal!",
            "Success! The population of animals returned to what is considered normal by the wildlife experts.",
            "Yippee! Everything went as expected and the ecosystem has returned to how it was prior to this unfortunate event."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 1280

        return [(values.bagel.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 5

        return [(values.gem_purple.text, amount)]

##### Black chess pieces.

class Board_Game_Festival(Project):
    """Written by Kapola."""
    internal = "board_game_festival"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Board Game Festival",
            "GameFest",
            "Missing Pawns"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_cost(day_seed, system_tile)[0][1]
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Okay, so you see, this Hub here holds an annual board game festival.",
            "It is an annual occurence in this Trade Hub to hold a board game festival.",
            "The GameFest is an annual board game festival that takes place in this Trade Hub and many others."
        ]

        part_2 = [
            "In the festival there are lots of board games;",
            "Many games are available at the festival;",
            "There are a large amount of games to play at the festival;"
        ]

        part_3 = [
            "checkers, The Minion, Katan, Capitalism Game, Crabble, and of course, Chess, are only some of the games you can play.",
            "Detective, Le Monopole, The Minion, COVID-19 But There's 4 Of Them, and obviously, Chess, among many others."
        ]

        part_4 = [
            "Now, you see, many of these games require some kind of playing pawns,",
            "Many of those games require pawns to play,",
            "A lot of board games among those are played with some sort of pawns,"
        ]

        part_5 = [
            "however, every year, the same tragedy strikes: the Pawn Thief!",
            "unfortunately, there is always one slight hiccup with that, every single year: the Pawn Thief!",
            "however, in every instance of the festival, there was one issue with this: the Pawn Thief!"
        ]

        part_6 = [
            "Every year, they come and steal all our pawns,",
            "Every festival, all our pawns are stolen by this mysterious individual,",
            "There is not a single time where the pawns were not taken by this masked figure,"
        ]

        part_7 = [
            "and despite our best protection efforts, this year was no exception!",
            "and well, even though we tried to prevent it, we again didn't succeed!",
            "and unfortunately, they were again successful!"
        ]

        part_8 = [
            "So as with every year, we are left asking our customers for help!",
            "That means you will have to provide us with pawns if you wish for this event to happen!",
            "Our only option is therefore to source our pawns from the future players!"
        ]

        part_9 = [
            f"As with every year, we have a {reward} reward prepared in advance for exactly this event,",
            f"Just like usual, we have a reward ({reward}) prepared specifically for this occasion,",
            f"We have {reward} prepared for precisely this eventuality,"
        ]

        part_10 = [
            f"that we will give to anyone who can provide us {cost} for the festival!",
            f"and it will be given to any generous soul who can provide us {cost} for the festival!",
            f"and anyone who can provide {cost} will find themself winner of this reward for saving the festival!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Well, that was enough! You earned yourself... a free spot in the next chess tournament! What, you were promised a *reward*? {reward}? Ugh, they weren't fooled again! Ah, just take it already! ",
            f"Woo! The Festival is saved! Exactly like every other year! Here's your {reward}!",
            f"You did it! Congratulations! The Board Game festival is up and running! Here's your {reward} as promised!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 1024

        return [(values.black_pawn.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 8

        return [(values.anarchy_black_pawn.text, amount)]
    
class Electrical_Issue(Project):
    """Written by Duck."""
    internal = "electrical_issue"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Electrical Issue",
            "Ecosystem Electronics",
            "Lighting Problem",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_cost(day_seed, system_tile)[0][1]
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Onboard the Trade Hub there's an ecosystem.",
            "There is an ecosystem on the Trade Hub.",
            "In this Trade Hub there's an ecosystem.",
        ]

        part_2 = [
            "Normally this ecosystem has a time cycle.",
            "Typically there is a time cycle in the ecosystem.",
            "There exists a time cycle in the ecosystem, at least, there is normally.",
        ]

        part_3 = [
            "But things have gone wrong.",
            "However this cycle has broken.",
            "The time cycle has stopped working, though.",
        ]

        part_4 = [
            "Some Trade Hub workers have determined that it's an electrical issue is",
            "Electricians on board have concluded that an electrical issue is",
            "Onboard experts figured out that an electrical issue is",
        ]

        part_5 = [
            "causing the time cycle to break.",
            "the source of the broken time cycle.",
            "the crux of the problem.",
        ]

        part_6 = [
            "Before replacement devices can arrive and the time cycle can be fixed time will not pass in the ecosystem, and will be stuck during the day!",
            "Prior to replacement decives arriving via HubMail™️the time cycle won't work and the lights will stay on all the time!",
            "Before the issue can be fixed time will not progress and the day will be eternal in the ecosystem!",
        ]

        part_7 = [
            f"The engineers have thought of a solution, they'll give {reward} for anyone that's able to buy them time by providing {cost}!",
            f"The Trade Hub workers have come up with an idea, they'll award {reward} to the first person able to provide {cost}!",
            f"The ecosystem overseers have thought of a solution, they'll reward anyone with {reward} if that person is able to give them {cost}!",
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Success! The Black Knights were able to keep the ecosystem dark and let evolution continue! As promised, your {reward} is on the way!",
            f"Yoggers! The ecosystem was kept dark at times due to the Black Knights! Your {reward} is on the way!",
            f"Wow! It seems like the ecosystem is working when it isn't! Thanks to the Black Knights you provided it is keeping things in order! Of course, the {reward} are on their way!",
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 256

        return [(values.black_knight.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2

        return [(values.anarchy_black_knight.text, amount)]
    
class Chess_Tournament(Project):
    """Written by Kapola."""
    internal = "chess_tournament"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Chess Tournament",
            "Bishops Missing",
            "Tournament Problem"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_cost(day_seed, system_tile)[0][1]
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "5 minutes until signups end for the Trade Hub Chess Tournament!",
            "There are only 10 minutes left to enter the Chess Tourney!",
            "To all visitors! Only 15 minutes until the Chess Tournament starts!"
        ]

        part_2 = [
            "If you want to sign up, please head to the...",
            "Prize for winning! Signups are at the...",
            "We highly recommend you enter! You can find the inscriptions at..."
        ]

        part_3 = [
            "wait, what's that?",
            "what do I hear?",
            "what is this news?"
        ]

        part_4 = [
            "Oh no!",
            "That's not good!",
            "We have a problem here!"
        ]

        part_5 = [
            "We ordered all the chess pieces for the tournament in bulk,",
            "The pieces were supposed to come sorted by type,",
            "We meant to have a bulk order of each piece,"
        ]

        part_6 = [
            "but somehow the black bishops didn't get delivered!",
            "but we did not receive any black bishops!",
            "however the order of black bishops didn't get through!"
        ]

        part_7 = [
            "Is there anyone who has some spares for us?",
            "Would any generous soul be able to help the tourney?",
            "Anyone with a donation to help?"
        ]

        part_8 = [
            "We're in need of... um, let me check...",
            "We need... yes? Ah...",
            "What do we need? Let me see..."
        ]

        part_9 = [
            f"{cost}!",
            f"it looks like we need {cost}!",
            f"that's a lot! We still need {cost}!"
        ]

        part_10 = [
            f"The Trade Hub would offer {reward} in exchange for those pieces!",
            f"We're offering a reward of {reward} for all those bishops!",
            f"We have some {reward} to offer to someone who could help!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Let the tournament begin! Oh, right, your reward! Here it is, your precious {reward}!",
            f"And here is your {reward}, as promised! The Trade Hub never lets down, huh? Well make sure to come back here in the future!",
            f"There's your {reward}... wait, you're not participating in the tournament???"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2,6) * 256

        return [(values.black_bishop.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2

        return [(values.anarchy_black_bishop.text, amount)]
    
class Diorama_Issue(Project):
    """Written by Duck."""
    internal = "diorama_issue"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Diorama Issue",
            "Missing Prop",
            "Diorama Problems",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Everyone in the Trade Hub is always excited when the diorama extraordinaire Apeace Avart comes through to show off his incredible dioramas.",
            "There is always excitement in the Trade Hub when Apeace Avart visits, showing off his incredible diorama-making abilities.",
            "It's always incredible when Apeace Avart stops at the Trade Hub to display the amazing dioramas he makes.",
        ]

        part_2 = [
            "Due to this, everybody was expecting some incredible scenes this time.",
            "When it was announced that he would be making a stop in a few days, there was much anticipation.",
            "Everybody is always very impressed by the dioramas, especially the Blåhaj spleen diorama. As you can imagine, when it was announced that he would be visiting the Trade Hub all the employees were very excited.",
        ]

        part_3 = [
            "But before the show arrived, the Trade Hub recieved sad news.",
            "But just a few days before Apeace Avart was scheduled to arrive some unfortunate news was sent to the Trade Hub.",
            "But some sad news has reached the Trade Hub...",
        ]

        part_4 = [
            "Apeace Avart's latest diorama was of a castle, but the props used to make the towers have gone missing!",
            "The latest diorama Apeace Avart was making was of a castle, but he's unable to find the props for the towers!",
            "Crucial props used to make the towers in a castle diorama have disappeared from Apeace Avart's studio!",
        ]

        part_5 = [
            "The tour was supposed to start soon, but it can't start until the diorama has been finished!",
            "The diorama tour can start until replacement tower props have been found!",
            "Apeace Avart can't visit the Trade Hub unless new tower props have been located!",
        ]

        part_6 = [
            f"Luckily, Apeace Avart has stated that if anybody is able to provide {cost} he would be able to paint them gray and use them!",
            f"But, Apeace Avart said that {cost} would be sufficient replacements.",
            f"Apeace Avart did say, however, that with {cost} he would be able to finish the legendary diorama!",
        ]

        part_7 = [
            f"But don't worry, a reward of {reward} has been stated for whoever is able to provide the new props.",
            f"Apiece Avart is willing to give away some unused old props, {reward}, as a reward.",
            f"Some old props that were never used, {reward}, have been posted by Apiece Avart as a reward.",
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Yay! The new props fit so well, the diorama turned out amazing! The reward of {reward} is on its way...",
            f"The diorama looks great! The new props worked really well, and may have made it look better! The reward of {reward} has been given!",
            f"Yippee! The new diorama is incredible, the new props fit in very well! Like Apiece Avart said, the reward of {reward} will be given!",
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2,6) * 256
        return [(values.black_rook.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2
        return [(values.anarchy_black_rook.text, amount)]

##### White chess pieces.

class Round_Table(Project):
    """Concept by Emily, written by ChatGPT."""
    internal = "round_table"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "The Round Table",
            "King Arthur",
            "The Holy Knight"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_cost(day_seed, system_tile)[0][1]
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Hark!",
            "Behold!",
            "Alas!"
        ]

        part_2 = [
            "The noble knight King Arthur seeks aid!",
            "King Arthur, the valiant defender of the realm, calls for assistance!",
            "The gallant King Arthur requires your help!"
        ]

        part_3 = [
            "The quest for assembling the legendary Round Table is at hand!",
            "A mission to gather the bravest knights for King Arthur's Round Table has commenced!",
            "The Holy Knight's sacred endeavor to unite the realm's finest knights under one banner has begun!"
        ]

        part_4 = [
            "This is a dire hour,",
            "Troubling times have fallen upon us,",
            "A dark cloud looms over the kingdom,"
        ]
        
        part_5 = [
            "as the Round Table remains incomplete!",
            "for King Arthur's Round Table lacks members!",
            "with the Holy Knight's assembly yet unfinished!"
        ]

        part_6 = [
            "Before the realm can achieve unity,",
            "Until the noble Round Table is fully assembled,",
            "Until the fellowship of knights is whole,"
        ]

        part_7 = [
            "additional knights are required to join the cause!",
            "more valiant souls must answer the call!",
            "brave warriors must step forward to join the noble quest!"
        ]

        part_8 = [
            f"With {cost} knights needed to complete the Round Table!",
            f"Seeking {cost} honorable knights to fill the ranks!",
            f"A total of {cost} gallant warriors are required for the Round Table's completion!"
        ]

        part_9 = [
            "Fear not, for valor shall be rewarded!",
            "But fret not, for those who aid shall be duly compensated!",
            "Take heart, for those who answer the call shall be duly recognized!"
        ]

        part_10 = [
            f"The reward for aiding in the assembly of the Round Table is {reward}!",
            f"Those who join the noble cause shall be granted {reward} in recognition of their bravery!",
            f"A bounty of {reward} awaits those who pledge their swords to the cause!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_cost(day_seed, system_tile)[0][1]
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Rejoice! The Round Table stands complete, thanks to the valorous souls who answered the call! With {cost} knights now sworn to the cause, the realm is one step closer to unity and peace. The Holy Knight extends heartfelt gratitude to all who contributed, and the promised {reward} shall soon find their way to the deserving hands of those who helped forge this legacy of valor and camaraderie. Onward, noble knights, for the realm awaits the dawn of a new era, united under the banner of King Arthur's Round Table!",
            f"The Round Table, now complete with {cost} valiant knights, stands as a beacon of unity and honor in the realm. Let the heralds sing of the bravery of those who answered the call, for their names shall be forever etched in the annals of history. As a token of gratitude, {reward} shall be bestowed upon the gallant souls who helped realize this noble vision. May the fellowship forged around the Round Table endure through the ages, a testament to the strength of camaraderie and the triumph of valor!",
            f"Victory! With {cost} noble knights now gathered around the Round Table, the realm's unity is assured and King Arthur's legacy preserved. Let the banners fly high and the trumpets sound in celebration of this momentous achievement! To those who heeded the call and joined the ranks of the Round Table, {reward} shall serve as a symbol of appreciation and honor. Together, we stand as guardians of peace and justice, bound by oath and valor, forever remembered in the songs and tales of old."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2,6) * 256

        return [(values.white_knight.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2

        return [(values.anarchy_white_knight.text, amount)]
    
class Fortress_Building(Project):
    """Written by Kapola."""
    internal = "fortress_building"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Fortress Building",
            "New Defences",
            "Materials Missing for Fortress"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "The Trade Hub's building a fortress right now,",
            "We're getting equipped with a brand new fortress,",
            "This construction space is for building a defense fortress,"
        ]

        part_2 = [
            "which will help the Trade Hub defend against invaders!",
            "in order to defend against an increasing number of bandits.",
            "which is to protect the Trade Hub from rival spaceships!"
        ]

        part_3 = [
            "It is one of the largest projects overseen here to date,",
            "This huge project makes us all proud of this Hub,",
            "The project is one of the biggest undertaken here,"
        ]

        part_4 = [
            "but we just ran out of towers for it!",
            "unfortunately while the walls are done, towers are lacking!",
            "sadly we're missing materials for some towers."
        ]
        
        part_5 = [
            "What's that? They're called *rooks*? Why? Well, *rooks* then.",
            "What, *rooks*? Why did we call them that? Ah well.",
            "Wait, why are they *rooks*? Who chose that stupid name? Anyway."
        ]
        
        part_6 = [
            "If you could provide us with some... *rooks* to build the fortress,",
            "If you just donated a couple \"rooks\" for the construction,",
            "Please just help us get enough \"rooks\" for the building,"
        ]
        
        part_7 = [
            f"we could give you {reward}!",
            f"and we could give you some... ah, yes, {reward}!",
            f"and these {reward} would be all yours!"
        ]
        
        part_8 = [
            f"We just need {cost}, by the way.",
            f"We need a full {cost}, and quick! We hear an invasion's on the way.",
            f"{cost} is what you should give us, before the next raid arrives!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Look, here they come! And... ouch, destroyed! Well, thanks for the towers, I mean rooks, and take these {reward}!",
            f"Well, the building is completed, hope it fares well! Here's your {reward}!",
            f"Did you hear! The towers... I mean, rooks, were instrumental in defeating the latest raid! Ah, yes the {reward}, right, here it is!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2,6) * 256
        return [(values.white_rook.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2
        return [(values.anarchy_white_rook.text, amount)]

class Offering_Ritual(Project):
    """Written by Kapola."""
    internal = "offering_ritual"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Offering Ritual",
            "Chess Piece Offering",
            "Chess Offering Ritual"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Attention attention!",
            "Announcement to all Trade Hub customers!",
            "Important announcement!"
        ]

        part_2 = [
            "As you may already know,",
            "You may already be aware of this, but",
            "As you should know by now,"
        ]

        part_3 = [
            "this Trade Hub holds a daily offering ritual to appease our gods.",
            "this Trade Hub has a long-standing tradition of holding daily offerings burned by fire.",
            "here there are daily rituals that we believe are required to keep the Trade Hub running."
        ]

        part_4 = [
            "The sacrifice varies each day,",
            "What it is that we offer depends on a complicated calendar,",
            "The offered item is chosen by a complex process to make our overlords happy,"
        ]
        
        part_5 = [
            "and this day, the item chosen is a chess piece,",
            "and today, our calendars dictate a chess piece should be offered,",
            "and our system specifies that today it is a chess piece that is needed for sacrifice,"
        ]
        
        part_6 = [
            "more specifically a white queen used for standard tournament play!",
            "particularly a type of white queen piece!",
            "specifically a standard white queen chess piece!"
        ]
        
        part_7 = [
            "However, it appears the Trade Hub is all out of stock!",
            "Unfortunately, the Trade Hub sold all the stock it had left a few days ago!",
            "Sadly, all these have been sold out, and the shipment that was supposed to arrive 2 days ago is still stuck in Albuquerque."
        ]
        
        part_8 = [
            "We will therefore need to source our offerings from the populace!",
            "Our only option is then to find the missing pieces from the people!",
            "This is why we must ask you, dear customers, to provide us with our needs!"
        ]
        
        part_9 = [
            f"There is a {reward} reward put up to anyone who can provide {cost} to help our cause!",
            f"There are still a whopping {cost} needed for the offering; the Trade Hub offers {reward} to anyone who can provide this!",
            f"Anyone who can provide the missing {cost} will be rewarded with {reward}!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"{reward} are now yours! And don't question what we did to those pieces.",
            f"The whole thing went absolutely perfectly, and the offering was successfully sent to the endless flames of hell and despair! Here are your totally legally obtained {reward}.",
            f"YES, THANKS TO YOU WE WERE ABLE TO CONTINUE OUR CHESS PIECE TRAFFICKI- uh I mean, yes, the ritual went very well! Just take these {reward}!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2,6) * 128
        return [(values.white_queen.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6)
        return [(values.anarchy_white_queen.text, amount)]

class Royal_Summit(Project):
    """Concept by Emily, written by ChatGPT."""
    internal = "royal_summit"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Royal Summit",
            "Diplomatic Assembly",
            "Regal Conference"
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Hail, esteemed denizens!",
            "Greetings, noble attendants!",
            "Salutations, honored guests!"
        ]

        part_2 = [
            "The esteemed visitors from a distant land have made a request.",
            "Royalty from afar seeks counsel from the Trade Hub's finest minds.",
            "A diplomatic entourage has arrived."
        ]

        part_3 = [
            "Their arrival brings both opportunity and challenge.",
            "The presence of visiting dignitaries prompts reflection on our shared responsibilities.",
            "With the arrival of distinguished guests, the Trade Hub faces a momentous occasion."
        ]

        part_4 = [
            "This occasion demands careful consideration.",
            "The Trade Hub must rise to the occasion.",
            "We are presented with a unique challenge."
        ]
        
        part_5 = [
            "The council is called upon to convene promptly.",
            "A meeting of minds is essential to address the needs of our honored guests.",
            "Swift action is required to accommodate the visiting royalty's request."
        ]
        
        part_6 = [
            "In the halls of deliberation,",
            "Amidst the discussions,",
            "During the council's session,"
        ]
        
        part_7 = [
            "strategies for diplomacy will be devised.",
            "plans for hospitality will be formulated.",
            "decisions regarding protocol will be made."
        ]
        
        part_8 = [
            f"With the resources of {cost},",
            f"For the provision of {cost},",
            f"Should someone supply {cost},"
        ]
        
        part_9 = [
            "the Trade Hub can offer a display of hospitality befitting royalty.",
            "we can extend a warm welcome to our distinguished guests.",
            "our esteemed visitors will be honored with the utmost respect and care."
        ]
        
        part_10 = [
            "And fear not, for generosity shall be duly rewarded!",
            "Rest assured, there shall be recompense for acts of kindness!",
            "Those who assist shall not go unrecognized!"
        ]
        
        part_11 = [
            f"The reward for extending hospitality is {reward}!",
            f"Those who contribute shall receive a token of appreciation in the form of {reward}!",
            f"A gesture of gratitude awaits those who lend their aid, in the form of {reward}!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10),
            rng.choice(part_11)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            "Bravo! The Trade Hub's council has successfully orchestrated a grand reception for the visiting royalty! Through your collective efforts, the diplomatic mission has flourished, and bonds of friendship have been strengthened between distant realms!",
            "Splendid work! The Trade Hub's hospitality has left a lasting impression on the visiting royalty! Your contributions have ensured that the diplomatic exchange has been a resounding success, fostering goodwill and understanding across borders!",
            "Magnificent! The Trade Hub's council has navigated the complexities of diplomacy with finesse, earning accolades from the visiting dignitaries! Thanks to your dedication, the bonds of camaraderie between nations have been reaffirmed, promising a brighter future of cooperation and harmony!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(1, 4) * 100
        return [(values.white_king.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(1, 4)
        return [(values.anarchy_white_king.text, amount)]

##### Gems.

class Emergency_Fuel(Project):
    """Concept by Emily, written by Duck."""
    internal = "emergency_fuel"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Emergency Fuel",
            "Fuel Emergency",
            "Needed Fuel",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Oh no!",
            "Oh dear!",
            "We need your help!"
        ]

        part_2 = [
            "A ship recently flew into this Trade Hub,",
            "We recently had a new space ship arrive here,",
            "Recently a space ship came into this Trade Hub,"
        ]

        part_3 = [
            "but it doesn't have the fuel required to continue the journey!",
            "but it's lacking the required fuel to make it safely to the next spot on its route!",
            "but the ship lacks the needed fuel to traverse the emptiness of space!"
        ]

        part_4 = [
            f"The ship operators are willing to pay {reward}",
            f"The ship operators have put up a reward of {reward}",
            f"The owners of the ship are paying {reward}"
        ]

        part_5 = [
            f"to anyone that can give them {cost}!",
            f"to any person willing to sell {cost} to them!",
            f"to anybody selling {cost} to help them adventure through space!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Phew! You managed to get just enough {values.gem_red.text} for the ship operators to take off! As part of the deal, you got {reward}!",
            f"Away they go! You got all the {values.gem_red.text} required for departure and you made {reward} from it!",
            f"Bye, bye! The ship operators were able to depart because you got all the {values.gem_red.text} required! Incredible job! As expected, you did get the reward of {reward}!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.gem_red.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 20

        return [(values.gem_blue.text, amount)]

class Gem_Mining(Project):
    """Written by Duck."""
    internal = "gem_mining"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Gem Mining",
            "Mining World",
            "Mining Request",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Of all the things in the reaches of space",
            "Throughout the wonders in the depths of space",
            "Of all the marvels in the depths of space"
        ]

        part_2 = [
            "\nNothing compares to this nice little place",
            "\nNothing can match this solitary place",
            "\nNothing compares to this quaint little place"
        ]

        part_3 = [
            "\nA good mining planet crunching out gems",
            "\nA mining planet, producing nice gems",
            "\nPlanets for mining are making the gems"
        ]

        part_4 = [
            "\nThe things were the source and also the stems",
            "\nNot only the heart but also the stems",
            "\nThey're the lifeblood, the roots, and also the stems"
        ]

        part_5 = [
            "\nThe tools broke down, they're in need of repair",
            "\nThe tools are broken, they need some repair,",
            "\nThe tools have failed, they need urgent repair,"
        ]

        part_6 = [
            "\nThey're asking folks for whatever they spare",
            "\nThey're in need of help, for all you can spare",
            "\nThey are seeking aid, for all you can spare."
        ]

        part_7 = [
            "\nSupplies of blue are very sufficient",
            "\nSupplies of blue, abundant, sufficient",
            "\nProviding blue gems would be sufficient"
        ]

        part_8 = [
            "\nReturning to calls of \"very efficient\"",
            "\nHeeding the calls of \"work done proficient\"",
            "\nResponding to calls for work quite proficient."
        ]

        part_9 = [
            f"\n\n{reward} has been stated by the mining world for providing {cost}.",
            f"\n\nA reward of {reward} has been posted for a cost of {cost}.",
            f"\n\nThe mining world has offered {reward} for anyone able to provide {cost}."
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        options = [
            "The gems were enough and the mining planet has returned to full efficiency!",
            "Yay! The gems you gave were sufficient to bring the mining planet to maximum efficiency!",
            "You did it! Congratulations! The mining planet is back up and running! I will now take your spleen."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.gem_blue.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 45

        return [(values.gem_purple.text, amount)]

class Jewelry_Store(Project):
    """Written by Kapola."""
    internal = "jewelry_store"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Jewelry Store",
            "New Jewelry Shop",
            "Jewelry Shop Opening",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Announcement! Looking for volunteers to sell gems!",
            "Hello there, you! It looks like you may be able to help us!",
            "The Trade Hub is in need of gems, looking for any help!"
        ]

        part_2 = [
            "The brand new jewelry store is about to open,",
            "We're preparing for the grand opening of our new jewelry shop,",
            "Our new shop for jewelry is almost ready,"
        ]

        part_3 = [
            "but we're missing a type of gem, the purple ones.",
            "however purple gems are lacking.",
            "sadly our last purple gems were just shipped yesterday."
        ]

        part_4 = [
            "The Trade Hub is looking for people to sell their gems,",
            "We're taking any donations that we can get,",
            "The Trade Hub would greatly appreciate any donations,"
        ]

        part_5 = [
            "and a generous reward will be offered in exchange for it!",
            "and we have a reward on the table!",
            "and you could be the winner of a large prize!"
        ]

        part_6 = [
            f"All you need is to give us the required {cost},",
            f"We just need {cost} from you,",
            f"We're only asking for {cost},"
        ]

        part_7 = [
            f"and you would get {reward} in exchange.",
            f"and the {reward} we're offering definitely seems worth that!",
            f"and you'll obtain a generous {reward}."
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Aaaaaaand... the jewelry store is opening... now! Special thanks for the help, and here are your {reward}!",
            f"The grand opening was successful and in time! You shall receive your {reward} in the next 5 business seconds.",
            f"Well, that was a success! Your {reward} are right here!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.gem_purple.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 45

        return [(values.gem_green.text, amount)]

class Generator_Breakdown(Project):
    """Written by Kapola."""
    internal = "generator_breakdown"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Generator Breakdown",
            "Backup Generator Fuel",
            "Generator Repair",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Hey, you! Yes, you!",
            "Announcement! Help required!",
            "We need help with something please!"
        ]

        part_2 = [
            "The Trade Hub's main generator just broke!",
            "Our power source has suffered a catastrophic failure!",
            "The generator keeping the Trade Hub running broke down!"
        ]

        part_3 = [
            "It will take a good while to fix the generator.",
            "Unfortunately, our engineers are all on vacation!",
            "It'll be weeks before a new one can be installed."
        ]

        part_4 = [
            "We do have a green-gem-powered backup generator,",
            "The Trade Hub has a backup power source running on green gems,",
            "The backup generator using green gems could be activated,"
        ]

        part_5 = [
            "but the Hub is lacking the fuel to run it.",
            "however the gem supply here is running dry!",
            "sadly all our remaining green gems were just sold."
        ]

        part_6 = [
            f"The Trade Hub estimates it will need {cost} to run the backup generator while the main one is fixed.",
            f"A total of {cost} are required to power the Trade Hub before the main generator is back.",
            f"{cost} are needed to keep the Trade Hub running in the meantime."
        ]

        part_7 = [
            "We are looking for people to volunteers their green gems,",
            "A green gem donation would be greatly appreciated,",
            "The gems can only come from the Hub's customers,"
        ]

        part_8 = [
            f"and anyone who can provide enough will receive {reward} as compensation!",
            f"and worry not for if you are the one to return power, you will be given {reward}!",
            f"and you will be rewarded with {reward} as compensation if you can supply us with fuel!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Thanks to you the Trade Hub can keep running while the generator is fixed! Here are your {reward}!",
            f"The Trade Hub can keep running now with your contribution! Your {reward} are here as promised.",
            f"It was a close call, but nothing went wrong while the power was out and it is now restored! You can take your {reward}."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.gem_green.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 12

        return [(values.gem_gold.text, amount)]

class Gem_Salesman(Project):
    """Written by Kapola."""
    internal = "gem_salesman"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Gem Salesman",
            "Travelling Merchant",
            "Gold Gem Restock",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Hey there!",
            "Oh, dear friend!",
            "'ello!"
        ]

        part_2 = [
            "Back to this good ol' Trade Hub today",
            "I've come back 'ere in these great times",
            "Returned to this place"
        ]

        part_3 = [
            "for a little restockin' on gold gems!",
            "'cause my gold gem supply was getting empty!",
            "'cause I was missin' some gems to sell!"
        ]

        part_4 = [
            "If ya don't know me, I'm just the ol' gem merchant!",
            "I ain't seen you before... Boris' my name, the gem salesman!",
            "I'm a regular around these parts. I'm a gem salesman!"
        ]

        part_5 = [
            "I come always to this place 'cause the vibes 'ere are good...",
            "One of the best Trade Hubs to go around, this place, ya know?",
            "This place is very nice, eh? That's why I spend my time here when I'm around."
        ]

        part_6 = [
            "Usually they always have some gems to stock me on...",
            "Never fails to sell a good price here, stocks always full...",
            "I always trust this place to restock my stuffs..."
        ]

        part_7 = [
            "looks like they ran out this time though, haha!",
            "bound to run out eventually though, am I right?",
            "had to break that streak at some point though!"
        ]

        part_8 = [
            "Hey, if ya could just sell me what I need, I'd be real pleased!",
            "Lookin' like you might have what I need though. Could buy ye stuffs!",
            "Think you could help a pal here?"
        ]

        part_9 = [
            f"I only need {cost} anyway...",
            f"Buyin' some {cost}...",
            f"All it would require is {cost}..."
        ]

        part_10 = [
            f"think {reward}'s a good price for that?",
            f"for {reward}, would ya be ready to sell?",
            f"I have some {reward} to pay with too!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7),
            rng.choice(part_8),
            rng.choice(part_9),
            rng.choice(part_10)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Aight, thanks for helpin' you pal here! Hope to see ya around these parts soon, and take these {reward}!",
            f"Ay, thank you for ye help! Have these {reward}. And ya can take this too, don't'ya want? Been tryin' to get rid of it since someone gave it to me at random on the street... told me it was a spleen o' some kind.",
            f"Well, I sure do 'preciate ya lendin' a hand to your ol' buddy here! Hope to see ya 'round this area again, and don't forget to grab these here {reward}!",
            f"Oi, I do 'preciate your kindness to an ol' man like me! Like promised the {reward} is now yours for the takin'. If you like I could throw in this ol' Blåhaj emitting rock I found in a random trash can at another trade hub once.",
            f"Well, slap my knee and shuck my corn! Ain’t you just a blessin’ sent straight from heaven, helpin’ out your ol’ pal like that! I reckon I’ll be seein’ ya 'round these parts quicker than a jackrabbit on a hot griddle. Now, don’t y’all dare forget to take these here {reward} with ya, ya hear me, sugar?"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 25 + 100

        return [(values.gem_gold.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 2

        item_1 = rng.choice(values.anarchy_pieces_black_biased)
        item_2 = rng.choice(values.anarchy_pieces_white_biased)


        return [(item_1.text, amount), (item_2.text, amount)]

##### Misc items.

class Omega_Order(Project):
    """Written by Kapola."""
    internal = "omega_order"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Omega Order",
            "Omega Chessatron Shipping",
            "Omega Trons Missing",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "How unfortunate!",
            "Uh oh...",
            "Hey, you! We need your help!"
        ]

        part_2 = [
            "Someone ordered a huge order of omega chessatrons,",
            "The Trade Hub has an enormous shipping of omegas to send,",
            "The Trade Hub needs to ship a lot of omegas to a customer,"
        ]

        part_3 = [
            "but we're missing half the MoaKs needed for them!",
            "sadly our Many of a Kinds are not sufficient!",
            "howver we are missing a crucial part of the order!"
        ]

        part_4 = [
            "All nearby supply sources are exhausted as well.",
            "Unfortunately, we have no way of obtaining more in time.",
            "We have asked many for help, but no one had enough."
        ]

        part_5 = [
            "If you have enough to complete the order,",
            "If you possess the MoaKs needed to finish alchemizing,",
            "If you can help us obtain the required resources,"
        ]

        part_6 = [
            "the Trade Hub is willing to offer you a large compensation!",
            "you would be rewarded with much riches!",
            "we could give you a huge reward!"
        ]

        part_7 = [
            f"The Hub is offering {reward} for {cost}!",
            f"You would be given {reward} if you provided us with {cost}!",
            f"If you can provide {cost}, we would give you {reward}!"
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6),
            rng.choice(part_7)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"Amazing! Thanks to you and the {values.anarchy_chess.text} you provided, we were able to finish up and ship the entire order. Here are your {reward}!",
            f"Many thanks for your generous donation of {values.anarchy_chess.text}! We managed to send the fuull shipping of omegas; here are your {reward}!",
            f"Incredible! You've really saved the day on this one; the order made it on time! Here is the {reward} you were promised."
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6)

        return [(values.anarchy_chess.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6)

        return [(values.omega_chessatron.text, amount)]

class Chessatron_Repair(Project):
    """Written by Duck."""
    internal = "chessatron_repair"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Chessatron Repair",
            "Leak Repair",
            "Chessatron Fix",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)

        part_1 = [
            "Oh no!",
            "Oh dear!",
            "Uh oh!"
        ]

        part_2 = [
            "There appears to be a leak on the side of the Trade Hub!",
            "There's a leak on the hull of the Trade Hub!",
            "The crew has spotted a leak on the side of the Trade Hub!",
            "A leak has been identified on the side of the Trade Hub!",
            "There has been a leak on the exterior of the Trade Hub!"
        ]

        part_3 = [
            "\nThe Trade Hub's engineers have been hard at work trying to resolve this,",
            "\nThe workers on the Trade Hub have found a fix for the leak,",
            "\nThe team assigned to fixing it have managed to find a fix,"
        ]

        part_4 = [
            "but they're in need of a few resources!",
            "but the Trade Hub lacks the resources required!",
            "but they don't have what's required to fix it!",
            "but the team doesn't have the items to patch the leak!",
            "but the workers are running low on resources!"
        ]

        part_5 = [
            f"The engineers need {cost} to fix the Trade Hub!",
            f"The team are in need of {cost} in order to fix the leak!",
            f"The workers require {cost} to fix the issue!"
        ]

        part_6 = [
            f"\nIn compensation, they have decided to give you {reward} as a reward.",
            f"\nFor payment, the team has decided to reward you with {reward} if the needed items are given."
        ]

        return " ".join([
            rng.choice(part_1),
            rng.choice(part_2),
            rng.choice(part_3),
            rng.choice(part_4),
            rng.choice(part_5),
            rng.choice(part_6)
        ])

    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> str:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)

        options = [
            f"It's fixed! Incredible job out there! You managed to get all the {values.chessatron.text} needed to patch the leak. You also made {reward} from it!",
            f"Here come the engineers! They have good news! They managed to fix the leak! They were only able to due this due to the {values.chessatron.text} you contributed! Nice job! As their part of the deal, the engineers gave you {reward} as a reward!",
            f"That was a close one! The Trade Hub almost got very damaged, but because of the {values.chessatron.text} you contributed everything is fine! You made {reward} as a reward from the engineers!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.chessatron.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTradeHub
        ) -> list[tuple[str, int]]:
        rng = random.Random(utility.hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 10

        item = rng.choice(values.anarchy_pieces_black_biased)

        return [(item.text, amount)]


#######################################################################################################
##### Item projects. ##################################################################################
#######################################################################################################

story_projects = [Essential_Oils, Bingobango]

take_special_bread_projects = [Too_Much_Stuffing, Flatbread_Shortage, Appease_The_French, Croissant_Cravings, Beach_Disappearance]
take_rare_bread_projects = [Ecosystem_Problem, Stolen_Donuts, Waffle_Machine]
take_black_chess_piece_projects = [Board_Game_Festival, Electrical_Issue, Chess_Tournament, Diorama_Issue]
take_white_chess_piece_projects = [Royal_Summit, Offering_Ritual, Fortress_Building, Round_Table]
take_gem_projects = [Gem_Salesman, Generator_Breakdown, Jewelry_Store, Gem_Mining, Emergency_Fuel]
take_misc_item_projects = [Chessatron_Repair, Omega_Order]

take_item_project_lists = [
    take_special_bread_projects,
    take_rare_bread_projects,
    take_black_chess_piece_projects,
    take_white_chess_piece_projects,
    take_gem_projects,
    take_misc_item_projects
]

give_special_bread_projects = []
give_rare_bread_projects = []
give_black_chess_piece_projects = []
give_white_chess_piece_projects = []
give_gem_projects = []
give_misc_item_projects = []

give_item_project_lists = [
    give_special_bread_projects,
    give_rare_bread_projects,
    give_black_chess_piece_projects,
    give_white_chess_piece_projects,
    give_gem_projects,
    give_misc_item_projects
]

item_project_lists = [take_item_project_lists, give_item_project_lists]


all_projects = story_projects + \
            take_special_bread_projects + take_rare_bread_projects + take_black_chess_piece_projects + take_white_chess_piece_projects + take_gem_projects + take_misc_item_projects + \
            give_special_bread_projects + give_rare_bread_projects + give_black_chess_piece_projects + give_white_chess_piece_projects + give_gem_projects + give_misc_item_projects