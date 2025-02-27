from __future__ import annotations

import bread_cog
import discord
import discord.ext.commands as commands
import itertools
import typing
import random

import bread.account as account
import bread.values as values
import bread.utility as utility

EMPTY = ":black_medium_square:"

EMOJI_UP_ARROW = ":arrow_up_small:"
EMOJI_DOWN_ARROW = ":arrow_down_small:"

EMOJI_RIGHT_ARROW = ":arrow_forward:"
EMOJI_LEFT_ARROW = ":arrow_backward:"

EMOJI_BLUE_SQUARE = ":blue_square:"
EMOJI_RED_SQUARE = ":red_square:"

class GameBoard:
    """Represents a rectangular game board with a set number of rows and columns."""
    
    def __init__(
            self: typing.Self,
            columns: int,
            rows: int,
            filler: typing.Any = EMPTY
        ) -> None:
        self.rows = rows
        self.columns = columns
        self.board = [[filler for _ in range(columns)] for _ in range(rows)]
    
    ############################################
    # Getters.
    
    def get_row(
            self: typing.Self,
            row: int
        ) -> typing.List[typing.Any]:
        """Gets a row of the board."""
        return self.board[row]
    
    def get_column(
            self: typing.Self,
            column: int
        ) -> typing.List[typing.Any]:
        """Gets a column of the board."""
        return [self.board[row][column] for row in range(self.rows)]
    
    def get_cell(
            self: typing.Self,
            row: int,
            column: int
        ) -> typing.Any:
        """Gets a specific cell of the board."""
        return self.board[row][column]
    
    def get_non_empty(self: typing.Self) -> typing.List[typing.Tuple[typing.Any, typing.Tuple[int, int]]]:
        """Returns a list of the remaining tiles on the board in a tuple.
        The first tuple element is item itself, and the second is its location as a tuple."""
        return [
            (self.get_cell(row, column), (row, column))
            for row in range(self.rows)
            for column in range(self.columns)
            if self.board[row][column] != EMPTY
        ]
    
    def count(
            self: typing.Self,
            value: typing.Any
        ) -> int:
        """Counts the number of a given item on the board."""
        # Flatten the board list and then use list.count().
        return list(itertools.chain(*self.board)).count(value)
    
    def get_remaining(self: typing.Self) -> int:
        """Returns the number of non-empty cells in the board."""
        return self.rows * self.columns - self.count(EMPTY)

    def get_remaining_rows(self: typing.Self) -> list[int]:
        return list(set([item[1][0] for item in self.get_non_empty()]))

    def get_remaining_columns(self: typing.Self) -> list[int]:
        return list(set([item[1][1] for item in self.get_non_empty()]))
    
    ############################################
    # Setters.
    
    def set_cell(
            self: typing.Self,
            row: int,
            column: int,
            value: typing.Any
        ) -> None:
        self.board[row][column] = value
    
    def set_whole_row(
            self: typing.Self,
            row: int,
            value: typing.Any
        ) -> None:
        self.board[row] = [value for _ in range(self.columns)]
    
    def set_whole_column(
            self: typing.Self,
            column: int,
            value: typing.Any
        ) -> None:
        for row in range(self.rows):
            self.board[row][column] = value
    
    def format_board(self: typing.Self) -> str:
        return "\n".join(" ".join(i.text if isinstance(i, values.Emote) else i for i in row) for row in self.board)
    
    def populate(
            self: typing.Self,
            options: typing.List[typing.Any],
            weights: typing.List[int]
        ) -> None:
        """Populates the board with the given options and weights."""
        # Generate a list of options based on the weights.
        flattened = random.choices(list(options), weights=list(weights), k=self.rows * self.columns)
        
        # If any options are lists choose a random item from them.
        # If any options are an Emote get the text representation.
        for index, item in enumerate(flattened):
            if isinstance(item, (list, tuple)):
                flattened[index] = random.choice(item)
            elif isinstance(item, values.Emote):
                flattened[index] = item.text
        
        # Unflatten the list and set the cells.
        self.board = [flattened[i:i + self.columns] for i in range(0, len(flattened), self.columns)]
    
    ############################################
    # Remove cells.
    # Removing just sets it to empty.
    
    def remove_row(
            self: typing.Self,
            row: int
        ) -> None:
        self.set_whole_row(row, EMPTY)
    
    def remove_column(
            self: typing.Self,
            column: int
        ) -> None:
        self.set_whole_column(column, EMPTY)
    
    def remove_cell(
            self: typing.Self,
            row: int,
            column: int
        ) -> None:
        self.set_cell(row, column, EMPTY)
    
    ############################################
    # Shifts.
    
    def shift_up(self: typing.Self) -> None:
        self.board = self.board[1:] + [self.board[0]]

    def shift_down(self: typing.Self) -> None:
        self.board = [self.board[-1]] + self.board[:-1]

    def shift_left(self: typing.Self) -> None:
        self.board = [
            i[1:] + [i[0]]
            for i in self.board
        ]

    def shift_right(self: typing.Self) -> None:
        self.board = [
            [i[-1]] + i[:-1]
            for i in self.board
        ]

####################################################################################################################
####################################################################################################################
####################################################################################################################

class Game:
    board_size = (4, 4)
    option_data: dict[typing.Any, float | int ] = {
        values.horsey.text: 25,
        values.brick.text: 50,
        values.anarchy.text: 25
    }
    
    def __init__(
            self: typing.Self,
            wager: int | tuple[str | values.Emote, int] | typing.Any,
            json_interface: bread_cog.JSON_interface,
            ctx: commands.Context
        ) -> None:
        """Base gambling game that can be subclassed. Not intended to be used directly.

        Args:
            wager (int | tuple[str  |  values.Emote, int] | typing.Any): Information about the given wager. Different games will handle this differently.
            json_interface (bread_cog.JSON_interface): The Bread Cog's JSON interface.
            ctx (commands.Context): The context of the command that started the game.
        """
        
        # This is kind of ugly, but unfortunately it is how you provide documentation to variables in Python.
        
        self.message: discord.Message = None
        """The initial board state message. Will be edited as the game progresses."""
        
        self.ctx = ctx
        """The context of the command that started the game."""
        
        self.json_interface = json_interface
        """The Bread Cog's JSON interface."""
        
        self.wager = wager
        """The wager as given to `__init__`. Different games will handle this differently."""
        
        self.tick = 0
        """The number of times the game has ticked, can be used to coordinate certain things, like alternating movements."""
        
        self.in_progress = True
    
    async def setup(self: typing.Self) -> None:
        """Run when the game is created, can be used to configure settings and remove the initial wager."""
        self.board = GameBoard(*self.board_size)
        self.board.populate(self.option_data.keys(), self.option_data.values())
        
        # Now that things have been setup, send and store the initial message.
        self.message = await self.ctx.reply(self.board.format_board())
    
    async def run_tick(self: typing.Self) -> None:
        """Run every 1.5 seconds to update the game state."""
        pass
    
    async def finish(
            self: typing.Self,
            footer: str = None
        ) -> None:
        """Run when the game is finished, can be used to clean up and save user data.
        Gets passed a footer to append to the end of a result message.
        Typically this will be a message saying when the Extra Gamble shop item is unlocked."""
        
        if footer is None:
            footer = ""
        
        await self.ctx.reply("Gambling finished.")

####################################################################################################################
####################################################################################################################
####################################################################################################################
##### BASE GAME.

class BaseGame(Game):
    board_size = (4, 4)
    option_data: dict[tuple[values.Emote] | values.Emote, float | int ] = {
        tuple(values.all_bricks_weighted): 4,
        values.horsey: 19,
        (values.cherry, values.lemon, values.grapes): 26,
        values.normal_bread: 25,
        tuple(values.all_special_breads): 15,
        tuple(values.chess_pieces_black_biased + [values.bcapy]): 10,
        (values.anarchy, values.anarchy_chess, values.holy_hell): 1
    }
    
    multipliers = {
        values.brick_gold: 10,
        (values.brick, values.fide_brick, values.brick_fide): 0,
        values.horsey: 0,
        (values.cherry, values.lemon, values.grapes): 0.25,
        values.normal_bread: 0.5,
        tuple(values.all_special_breads): 2,
        tuple(values.chess_pieces_black_biased + [values.bcapy]): 4,
        (values.anarchy, values.anarchy_chess, values.holy_hell): 10
    }
    
    async def setup(self: typing.Self) -> None:
        """Run when the game is created, can be used to configure settings and remove the initial wager."""
        self.board = GameBoard(*self.board_size)
        
        user_account = self.json_interface.get_account(self.ctx.author.id, self.ctx.guild.id) # type: account.Bread_Account
        user_account.increment("total_dough", -self.wager)
        self.json_interface.set_account(self.ctx.author.id, user_account, self.ctx.guild.id)
        
        brick_troll = user_account.get("brick_troll_percentage") >= random.randint(1,100)
        
        if brick_troll:
            self.board.populate([values.all_bricks_weighted], [100])
        else:
            self.board.populate(self.option_data.keys(), self.option_data.values())
            
        self.winning_x = random.randrange(self.board_size[0])
        self.winning_y = random.randrange(self.board_size[1])
        self.winning_item = values.get_emote(self.board.get_cell(self.winning_y, self.winning_x))
        
        self.column_remove = [(False, i) for i in range(self.board_size[0]) if i != self.winning_x]
        self.row_remove = [(True, i) for i in range(self.board_size[1]) if i != self.winning_y]
        
        self.remove = self.column_remove + self.row_remove
        random.shuffle(self.remove)
        
        # Now that things have been setup, send and store the initial message.
        self.message = await self.ctx.reply(self.board.format_board())
    
    async def run_tick(self: typing.Self) -> None:
        remove = self.remove.pop(0)
        
        if remove[0]:
            self.board.remove_row(remove[1])
        else:
            self.board.remove_column(remove[1])
        
        if len(self.remove) == 0:
            self.in_progress = False
            
        await self.message.edit(content=self.board.format_board())
        
        self.tick += 1
    
    async def finish(
            self: typing.Self,
            footer: str = None
        ) -> None:
        if footer is None:
            footer = ""
            
        wager = self.wager
        
        for option, multiplier in self.multipliers.items():
            if (isinstance(option, values.Emote) and self.winning_item == option) or \
                (isinstance(option, (tuple, list)) and self.winning_item in option):
                winnings = int(wager * multiplier)
                break
        else:
            # If nothing is found return the wager dough.
            winnings = wager
            
        do_brick = False
        
        if self.winning_item in values.all_bricks:
            do_brick = True
            
            send_text = "You found a brick. Please hold, delivering reward at high speed."
            
            if self.winning_item == values.brick_gold:
                # ooh
                send_text += f" Looks like you'll be able to sell this one for {utility.smart_number(winnings)} dough."
        elif self.winning_item == values.horsey:
            send_text = "Sorry, you didn't win anything. Better luck next time."
        else:
            send_text = f"With a {self.winning_item.text}, you won {utility.smart_number(winnings)} dough."
            
        # Get the user account now to avoid overwriting data.
        user_account = self.json_interface.get_account(self.ctx.author.id, self.ctx.guild.id) # type: account.Bread_Account
        user_account.increment("gamble_winnings", winnings - wager)
        user_account.increment("total_dough", winnings)
        self.json_interface.set_account(self.ctx.author.id, user_account, self.ctx.guild.id)
        
        await self.ctx.reply(send_text + footer)
        
        if do_brick:
            # insert trol emoji here
            await self.ctx.invoke(self.ctx.bot.get_command('brick'), member=self.ctx.author)