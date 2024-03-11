"""This houses all the projects that can spawn in Bread Space."""

from __future__ import annotations

import typing
import random
import hashlib
import math

import bread.space as space
import bread.values as values
import bread.account as account
import bread.utility as utility

def hash_args(*args) -> str:
    return hashlib.sha256("".join([str(arg) for arg in args]).encode()).digest()


class Project:
    internal = "project"

    # Optional for subclasses.
    @classmethod
    def display_info(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            completed: bool = False
        ) -> str:
        name = cls.name(day_seed, system_tile)
        description = cls.description(day_seed, system_tile)

        completed_prefix = "~~" if completed else ""
        completed_suffix = "~~    COMPLETED" if completed else ""

        return f"   **{completed_prefix}{name}:{completed_suffix}**\n{description}"

    # Required for subclasses.
    @classmethod
    def name(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        return "Project name"

    # Required for subclasses.
    @classmethod
    def description(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        return "Project description"

    # Required for subclasses.
    @classmethod
    def completion(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        return "Project completion"
    
    # Required for subclasses.
    @classmethod
    def get_cost(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        return [(values.gem_red.text, 100), ("total_dough", 200)]
    
    # Required for subclasses.
    @classmethod
    def get_reward(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        return [(values.gem_red.text, 100), ("total_dough", 200)]

    # Optional for subclasses.
    @classmethod
    def do_purchase(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            user_account: account.Bread_Account
        ) -> None:
        cost = cls.get_cost(day_seed, system_tile)

        for pair in cost:
            user_account.increment(pair[0], -pair[1])

    # Optional for subclasses.
    @classmethod
    def is_affordable_for(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            user_account: account.Bread_Account
        ) -> bool:
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
            system_tile: space.SystemTile
        ) -> str:
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
            system_tile: space.SystemTile
        ) -> str:
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
            system_tile: space.SystemTile
        ) -> int:
        cost = cls.get_cost(day_seed, system_tile)

        return sum([pair[1] for pair in cost])
    
    # Optional for subclasses.
    @classmethod
    def total_items_collected(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> int:
        cost_sum = cls.total_items_required(day_seed, system_tile)

        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        return cost_sum - sum(remaining.values())
    
    # Optional for subclasses.
    @classmethod
    def get_progress_percent(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> float:
        cost_sum = cls.total_items_required(day_seed, system_tile)

        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        progress_sum = cost_sum - sum(remaining.values())

        return progress_sum / cost_sum
    
    # Optional for subclasses.
    @classmethod
    def get_remaining_items(
            cls: typing.Type[typing.Self],
            day_seed: str,
            system_tile: space.SystemTile,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> dict[str, int]:
        """
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
        }"""
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
            system_tile: space.SystemTile,
            progress_data: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> str:
        remaining = cls.get_remaining_items(day_seed, system_tile, progress_data)

        output = []
        for item, amount in remaining.items():
            output.append(f"{utility.smart_number(amount)} {item}")

        return " ,  ".join(output)
        


#######################################################################################################
##### Story projects. #################################################################################
#######################################################################################################

class Essential_Oils(Project):
    internal = "essential_oils"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
        
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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
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
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 50

        return [(values.fuel.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

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


#######################################################################################################
##### Take item projects. #############################################################################
#######################################################################################################

##### Special bread.
    
class Flatbread_Feast(Project):
    internal = "flatbread_feast"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
        
        options = [
            "Flatbread Feast",
            "Crispy Crust",
            "Flat Delight",
        ]

        return rng.choice(options)

    @classmethod
    def description(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        cost = cls.get_price_description(day_seed, system_tile)
        reward = cls.get_reward_description(day_seed, system_tile)
        name = cls.name(day_seed, system_tile)

        part_1 = [
            "Amazing news!",
            "Incredible discovery!",
            "Unbelievable opportunity!"
        ]

        part_2 = [
            "The Trade Hub has just received an exciting proposal!",
            "A tempting offer has arrived for the Trade Hub!",
            "The Trade Hub management is buzzing with news of a lucrative deal!"
        ]

        part_3 = [
            f"\nFor just {cost}, the Trade Hub can become a key supplier for the {name} event!",
            f"\nInvest {cost} now, and the Trade Hub will secure a prominent role in the {name} festival!",
            f"\nBy providing only {cost}, the Trade Hub will be the go-to source for the {name} celebration!"
        ]

        part_4 = [
            "Furthermore, for every event ticket sold, the Trade Hub will earn a percentage of the revenue!",
            "Additionally, you'll receive a share of the profits for every guest attending the festival!",
            "Plus, recruiting vendors for the event will earn the Trade Hub a commission for each sale made!"
        ]

        part_5 = [
            f"{name} guarantees a return of {reward} upon participation!",
            f"{name} promises a profit of {reward} for each flatbread contributed!",
            f"With {name}, you're sure to reap rewards totaling {reward}!"
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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
        reward = cls.get_reward_description(day_seed, system_tile)
        name = cls.name(day_seed, system_tile)

        options = [
            f"Incredible job! You provided all the {values.flatbread.text} required for the {name} and made {reward} from it!",
            f"Very nice! {name} got all the {values.flatbread.text} they needed and you got {reward}!",
            f"Awesome job! The {name} managed to get all the {values.flatbread.text} they needed and you got {reward} from the event!"
        ]

        return rng.choice(options)
    
    @classmethod
    def get_cost(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 100 + 1000

        return [(values.flatbread.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(10, 20) * 50 + 100

        item = rng.choice(values.all_rare_breads)

        return [(item.text, amount)]

##### Rare bread.

##### Black chess pieces.
    
##### White chess pieces.

##### Gems.

class Emergency_Fuel(Project):
    internal = "emergency_fuel"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
        
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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
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
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.gem_red.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 20

        return [(values.gem_blue.text, amount)]

##### Misc items.

class Chessatron_Repair(Project):
    internal = "chessatron_repair"
    
    @classmethod
    def name(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
        
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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

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
            system_tile: space.SystemTile
        ) -> str:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))
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
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 50 + 100

        return [(values.chessatron.text, amount)]
    
    @classmethod
    def get_reward(
            cls,
            day_seed: str,
            system_tile: space.SystemTile
        ) -> list[tuple[str, int]]:
        rng = random.Random(hash_args(day_seed, system_tile.tile_seed()))

        amount = rng.randint(2, 6) * 10

        item = rng.choice(values.anarchy_pieces_black_biased)

        return [(item.text, amount)]


#######################################################################################################
##### Item projects. ##################################################################################
#######################################################################################################

story_projects = [Essential_Oils]

# Chessatron_Repair appears a lot here since it doesn't like it when a list is empty.
# When projects are made for those categories Chessatron_Repair can be removed.
# Except take_misc_item_projects, since it actually goes there lol.
take_special_bread_projects = [Flatbread_Feast]
take_rare_bread_projects = [Chessatron_Repair]
take_black_chess_piece_projects = [Chessatron_Repair]
take_white_chess_piece_projects = [Chessatron_Repair]
take_gem_projects = [Emergency_Fuel]
take_misc_item_projects = [Chessatron_Repair]

take_item_project_lists = [
    take_special_bread_projects,
    take_rare_bread_projects,
    take_black_chess_piece_projects,
    take_white_chess_piece_projects,
    take_gem_projects,
    take_misc_item_projects
]

give_special_bread_projects = [Chessatron_Repair]
give_rare_bread_projects = [Chessatron_Repair]
give_black_chess_piece_projects = [Chessatron_Repair]
give_white_chess_piece_projects = [Chessatron_Repair]
give_gem_projects = [Chessatron_Repair]
give_misc_item_projects = [Chessatron_Repair]

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