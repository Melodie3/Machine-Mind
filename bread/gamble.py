from __future__ import annotations

import bread_cog
import discord
import discord.ext.commands as commands
import itertools
import typing
import random
import abc
import time

import bread.account as account
import bread.values as values
import bread.utility as utility
import bread.store as store

EMPTY = ":black_medium_square:"

EMOJI_UP_ARROW = ":arrow_up_small:"
EMOJI_DOWN_ARROW = ":arrow_down_small:"

EMOJI_RIGHT_ARROW = ":arrow_forward:"
EMOJI_LEFT_ARROW = ":arrow_backward:"

EMOJI_BLUE_SQUARE = ":blue_square:"
EMOJI_RED_SQUARE = ":red_square:"

class GameBoard():
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
    
    def __str__(self):
        return f"<GameBoard: {self.board}>"
    
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

class Game(abc.ABC):
    board_size = (4, 4)
    option_data: dict[typing.Any, float | int ] = {
        values.horsey.text: 25,
        values.brick.text: 50,
        values.anarchy.text: 25
    }
    
    def __init__(
            self: typing.Self,
            wager: int | tuple[str | values.Emote, int] | values.Emote | typing.Any,
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
    
    @abc.abstractmethod
    async def run_tick(self: typing.Self) -> None:
        """Run every 1.5 seconds to update the game state."""
        raise NotImplementedError("run_tick() must be implemented in subclasses.")
    
    @abc.abstractmethod
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

            
####################################################################################################################
##### LASERS GAME.

class LasersBoard(GameBoard):
    def format_board(
            self: typing.Self,
            tease_info: tuple[int, int] | None = None,
            laser_info: tuple[int, int] | None = None
        ) -> str:
        """Formats the board.

        Args:
            tease_info (tuple[int, int] | None, optional): Row and column (in that order) of the tiles to tease. Defaults to None.
            laser_info (tuple[int, int] | None, optional): Row and column (in that order) of the tiles to laser. Defaults to None.

        Returns:
            str: The formatted board.
        """
        render_mod = self.board.copy()
        
        # Unpack tease and laser info.
        tease_row, tease_column = tease_info or (None, None)
        laser_row, laser_column = laser_info or (None, None)
            
        for row_index, row in enumerate(render_mod):
            if row_index == laser_row:
                row = [EMOJI_RED_SQUARE] * len(row)
            elif laser_column is not None:
                row[laser_column] = EMOJI_RED_SQUARE
            
            if row_index == tease_row:
                row = [EMOJI_RIGHT_ARROW] + row + [EMOJI_LEFT_ARROW]
            else:
                row = [EMOJI_BLUE_SQUARE] + row + [EMOJI_BLUE_SQUARE]
                
            render_mod[row_index] = row
        
        render_mod.insert(0,
            [EMOJI_DOWN_ARROW if index - 1 == tease_column else EMOJI_BLUE_SQUARE for index in range(self.columns + 2)]
        )
        render_mod.append(
            [EMOJI_UP_ARROW if index - 1 == tease_column else EMOJI_BLUE_SQUARE for index in range(self.columns + 2)]
        )
        
        return "\n".join(["".join(line) for line in render_mod])

class LasersGame(Game):
    board_size = (6, 6)
    
    option_data = {
        values.brick.text: 4,
        values.hotdog.text: 19,
        values.cherry.text: 26,
        values.normal_bread.text: 25,
        values.french_bread.text: 15,
        values.pretzel.text: 10,
        values.birthday.text: 1
    }
    
    async def setup(self: typing.Self) -> None:
        """Run when the game is created, can be used to configure settings and remove the initial wager."""
        self.winning_item = None
        
        self.board = LasersBoard(*self.board_size)
        self.fake_board = LasersBoard(*self.board_size)
        
        
        # Setup the variables used later.
        self.remove_row = None
        self.remove_column = None
        self.shift_chosen = None
        
        self.shift_options = [
            self.board.shift_up,
            self.board.shift_down,
            self.board.shift_left,
            self.board.shift_right
        ]
        self.fake_shift_options = [
            self.fake_board.shift_up,
            self.fake_board.shift_down,
            self.fake_board.shift_left,
            self.fake_board.shift_right
        ]
        self.shift_opposite = {
            self.board.shift_up: self.board.shift_down,
            self.board.shift_down: self.board.shift_up,
            self.board.shift_left: self.board.shift_right,
            self.board.shift_right: self.board.shift_left
        }
        self.fake_shift_opposite = {
            self.fake_board.shift_up: self.fake_board.shift_down,
            self.fake_board.shift_down: self.fake_board.shift_up,
            self.fake_board.shift_left: self.fake_board.shift_right,
            self.fake_board.shift_right: self.fake_board.shift_left
        }
        
        user_account = self.json_interface.get_account(self.ctx.author.id, self.ctx.guild.id) # type: account.Bread_Account
        user_account.increment(self.wager, -1)
        self.json_interface.set_account(self.ctx.author.id, user_account, self.ctx.guild.id)
        
        try:
            self.active_catalyst = user_account.get_active_catalyst().name
        except AttributeError:
            self.active_catalyst = None
        
        self.random_seed = time.time()# * user_account.get("earned_dough")
        self.random_obj = random.Random(self.random_seed)
        
        equal_weight = {i.text: 1 for i in filler_items}
        
        
        ##############################
        
        items = {}
        for key, item_list in salvage_weights.items():
            if self.wager in key:
                items = dict(item_list)
                break
        else:
            raise KeyError(f"Unable to find item {self.wager} in the salvage weights list.")
        
        self.board.populate(equal_weight.keys(), equal_weight.values())
        
        for column in range(self.board_size[0]):
            for row in range(self.board_size[1]):
                self.fake_board.set_cell(row, column, column * self.board_size[0] + row)
                
        ##############################
        
        self.remove_coordinates = [] # type: list[tuple[int, int]]
        self.shifts = [] # type: list[typing.Callable]
        
        # self.winning_item = values.croissant
        
        self.tick_is_real = False
        
        while self.in_progress:
            await self.run_tick()
        
        winning_id = self.fake_board.get_cell(self.fake_board.get_remaining_rows()[0], self.fake_board.get_remaining_columns()[0])
        winning_coordinates = (winning_id % self.board_size[0], winning_id // self.board_size[0])
        
        # Reset all the stuff that's modified while running the initial ticks.
        self.tick = 0
        self.in_progress = True
        self.tick_is_real = True
        self.random_obj = random.Random(self.random_seed)
        
        ##############################
        # Now that we know which tile is going to win, we can finally populate the regular board correctly.
        # The winning tile will *always* be chosen from the wager-specific item list, and a random amount of other tiles will be as well.
        
        if len(items) >= 2:
            amount = round(random.normalvariate(self.board_size[0] * self.board_size[1] / 2, self.board_size[0] * self.board_size[1] / 6))
            
            print(f"[Salvage] Replacing {amount} items on the board.")
            
            # Limit the bounds of the amount to be within a reasonable range.
            amount = min(max(amount, 5), self.board_size[0] * self.board_size[1])
            
            items_add = random.choices(list(items.keys()), weights=list(items.values()), k=amount)
            
            for index, item in enumerate(items_add):
                if self.active_catalyst == store.Aquila.name and item == values.gem_white.text:
                    item = values.ephemeral_token.text
                elif self.active_catalyst == store.Cygnus.name and item == values.ephemeral_token.text:
                    item = values.gem_white.text
                    
                if index == 0:
                    self.board.set_cell(*winning_coordinates, item)
                    continue
                
                column = random.randrange(self.board_size[0])
                row = random.randrange(self.board_size[1])
                
                self.board.set_cell(row, column, item)
        else:
            self.board.populate(items.keys(), items.values())
            
        self.winning_item = values.get_emote(self.board.get_cell(*winning_coordinates))
            
        print(user_account.get("username"), f"is salvaging a {self.wager} and will win a {self.winning_item}.")
        
        ##############################
        
        self.message = await self.ctx.reply(self.board.format_board())
        
    
    async def run_tick(self: typing.Self) -> None:
        action = self.tick % 3
        
        if self.tick_is_real:
            board_use = self.board
            shift_options = self.shift_options
            shift_opposite = self.shift_opposite
        else:
            board_use = self.fake_board
            shift_options = self.fake_shift_options
            shift_opposite = self.fake_shift_opposite
        
        if action == 0:
            # If the action is 0:
            # - Remove anything if there is stuff to remove.
            # - Figure out what we're gonna remove and how we're gonna shift
            # - Tease it.
            if self.tick != 0:
                board_use.remove_row(self.remove_row)
                board_use.remove_column(self.remove_column)
                
                if board_use.get_remaining() <= 1:
                    self.in_progress = False
            
            if self.in_progress:
                if self.tick_is_real:
                    self.shift_chosen = shift_options[self.shifts.pop(0)]
                    self.remove_row, self.remove_column = self.remove_coordinates.pop(0)
                    
                    rendered = board_use.format_board(tease_info=(self.remove_row, self.remove_column))
                else:
                    self.shift_chosen = self.random_obj.choice(shift_options)
                    self.shift_chosen()
                    
                    possible_rows = board_use.get_remaining_rows()
                    possible_columns = board_use.get_remaining_columns()
                    
                    shift_opposite[self.shift_chosen]()
                    
                    if len(possible_rows) > 1:
                        self.remove_row = self.random_obj.choice(possible_rows)
                    else:
                        # If there's only 1 option left, choose something that is not it.
                        self.remove_row = self.random_obj.randrange(self.board_size[1])
                        
                        while self.remove_row == possible_rows[0]:
                            self.remove_row = self.random_obj.randrange(self.board_size[1])
                    
                    if len(possible_columns) > 1:
                        self.remove_column = self.random_obj.choice(possible_columns)
                    else:
                        # If there's only 1 option left, choose something that is not it.
                        self.remove_column = self.random_obj.randrange(self.board_size[0])
                        
                        while self.remove_column == possible_columns[0]:
                            self.remove_column = self.random_obj.randrange(self.board_size[0])
                    
                    self.shifts.append(shift_options.index(self.shift_chosen))
                    self.remove_coordinates.append((self.remove_row, self.remove_column))
            else:
                if self.tick_is_real:
                    rendered = board_use.format_board()

        elif action == 1:
            # If the action is 1, shift the board.
            self.shift_chosen()
            
            if self.tick_is_real:
                rendered = board_use.format_board(tease_info=(self.remove_row, self.remove_column))
            
        else:
            # If the action is 2 (this), show the lasers.
            if self.tick_is_real:
                rendered = board_use.format_board(
                    tease_info=(self.remove_row, self.remove_column),
                    laser_info=(self.remove_row, self.remove_column)
                )
        
        if self.tick_is_real:
            await self.message.edit(content=rendered)
            
        self.tick += 1
    
    async def finish(
            self: typing.Self,
            footer: str = None
        ) -> None:
        if footer is None:
            footer = ""
            
        self.in_progress = False
            
        user_account = self.json_interface.get_account(self.ctx.author.id, self.ctx.guild.id) # type: account.Bread_Account
        
        if self.winning_item is None:
            send_text = f"Hold up, something seems to have gone wrong and the Salvage Machine couldn't be started.\nWell, I suppose I can at least refund you the {self.wager.text} you put into it."
                
            user_account.increment(self.wager.text, 1)
            user_account.increment("salvagez_remaining", 1)
        else:
            out_amount = 1
            
            if self.active_catalyst == store.Gemini.name and random.randint(1, 4) == 1:
                out_amount = 2
                
            send_text = f"The salvage machine has managed to extract {out_amount} {self.winning_item.text} from the {self.wager.text}"
            
            # Little easter egg for certain items.
            if self.winning_item in {values.gem_white, values.ephemeral_token, values.anarchy_omega_chessatron, values.anarchy_chessatron, values.hotdog} \
                or out_amount > 1:
                send_text += "!"
            else:
                send_text += "."
                
            user_account.increment(self.winning_item.text, out_amount)
        
        self.json_interface.set_account(self.ctx.author.id, user_account, self.ctx.guild.id)
        
        await self.ctx.reply(send_text + footer)
        

####################################################################################################################
##### SALVAGE WEIGHTS.

salvage_weights = {
    (values.gem_white,): [(values.gem_white.text, 45), (values.ephemeral_token.text, 25), (values.gem_gold.text, 10), (values.gem_green.text, 5), (values.anarchy_chess.text, 5)] + [(gem.text, 10/3) for gem in values.all_very_shinies],
    (values.ephemeral_token,): [(values.gem_white.text, 50), (values.ephemeral_token.text, 25), (values.anarchy_chessatron.text, 20), (values.anarchy_chess.text, 5)],
    (values.gem_pink,): [(values.gem_white.text, 25), (values.ephemeral_token.text, 15), (values.gem_cyan.text, 30), (values.gem_orange.text, 30)],
    (values.gem_orange,): [(values.gem_white.text, 25), (values.ephemeral_token.text, 15), (values.gem_cyan.text, 30), (values.gem_pink.text, 30)],
    (values.gem_cyan,): [(values.gem_white.text, 25), (values.ephemeral_token.text, 15), (values.gem_orange.text, 30), (values.gem_pink.text, 30)],
    (values.gem_gold,): [(values.gem_white.text, 15), (values.ephemeral_token.text, 10), (values.gem_cyan.text, 10), (values.gem_orange.text, 10), (values.gem_pink.text, 10), (values.gem_green.text, 30), (values.gem_purple.text, 15)],
    (values.gem_green,): [(values.gem_white.text, 10), (values.ephemeral_token.text, 7), (values.gem_gold.text, 30), (values.gem_purple.text, 53)],
    (values.gem_purple,): [(values.gem_white.text, 7), (values.ephemeral_token.text, 5), (values.gem_gold.text, 10), (values.gem_green.text, 20), (values.gem_blue.text, 34)] + [(piece.text, 2) for piece in values.all_anarchy_pieces],
    (values.gem_blue,): [(values.gem_white.text, 5), (values.ephemeral_token.text, 2), (values.gem_gold.text, 5), (values.gem_green.text, 15), (values.gem_purple.text, 30), (values.gem_red.text, 43)],
    (values.gem_red,): [(values.gem_white.text, 2), (values.ephemeral_token.text, 1), (values.gem_gold.text, 2), (values.gem_green.text, 10), (values.gem_purple.text, 15), (values.gem_blue.text, 22)] + [(piece.text, 4) for piece in values.all_chess_pieces],
    tuple(values.anarchy_pieces_white,): [(values.anarchy_chessatron.text, 2.5)] + [(piece.text, 65/6) for piece in values.anarchy_pieces_white] + [(piece.text, 25/6) for piece in values.anarchy_pieces_black] + [(gem.text, 7.5/3) for gem in values.all_very_shinies],
    tuple(values.anarchy_pieces_black,): [(values.anarchy_chessatron.text, 2.5)] + [(piece.text, 65/6) for piece in values.anarchy_pieces_black] + [(piece.text, 25/6) for piece in values.anarchy_pieces_white] + [(gem.text, 7.5/3) for gem in values.all_very_shinies],
    tuple(values.chess_pieces_white,): [(values.chessatron.text, 2.5), (values.gem_red.text, 7.5)] + [(piece.text, 65/6) for piece in values.chess_pieces_white] + [(piece.text, 25/6) for piece in values.chess_pieces_black],
    tuple(values.chess_pieces_black,): [(values.chessatron.text, 2.5), (values.gem_red.text, 7.5)] + [(piece.text, 65/6) for piece in values.chess_pieces_black] + [(piece.text, 25/6) for piece in values.chess_pieces_white],
    tuple(values.all_rare_breads,): [(values.normal_bread.text, 10), (values.corrupted_bread.text, 5)] + [(bread.text, 65/3) for bread in values.all_rare_breads] + [(bread.text, 20/5) for bread in values.all_special_breads],
    tuple(values.all_special_breads,): [(values.normal_bread.text, 10), (values.corrupted_bread.text, 5)] + [(bread.text, 20/3) for bread in values.all_rare_breads] + [(bread.text, 13) for bread in values.all_special_breads],
    (values.normal_bread,): [(values.corrupted_bread.text, 12), (values.gem_white.text, 2), (values.ephemeral_token.text, 1)] + [(bread.text, 5) for bread in values.all_rare_breads] + [(bread.text, 14) for bread in values.all_special_breads],
    (values.corrupted_bread,): [(values.corrupted_bread.text, 75), (values.normal_bread.text, 25)],
    (values.horsey,): [(values.holy_hell.text, 50), (values.anarchy.text, 50)],
    (values.holy_hell,): [(values.anarchy.text, 50), (values.horsey.text, 50)],
    (values.anarchy,): [(values.holy_hell.text, 50), (values.horsey.text, 50)],
    (values.anarchy_chess,): [(values.gem_white.text, 20), (values.ephemeral_token.text, 15), (values.omega_chessatron.text, 30), (values.gem_gold.text, 20), (values.anarchy_chessatron.text, 10), (values.anarchy_omega_chessatron.text, 5)],
    (values.chessatron,): [(values.omega_chessatron.text, 18), (values.anarchy_chessatron.text, 10)] + [(piece.text, 4) for piece in values.chess_pieces_white] + [(piece.text, 12) for piece in values.chess_pieces_black],
    (values.anarchy_chessatron,): [(values.omega_chessatron.text, 18), (values.anarchy_chessatron.text, 10), (values.hotdog.text, 5)] + [(piece.text, 4) for piece in values.anarchy_pieces_white] + [(piece.text, 43/6) for piece in values.anarchy_pieces_black],
    (values.fuel,): [(values.gem_red.text, 50), (values.gem_blue.text, 25), (values.gem_purple.text, 13), (values.gem_green.text, 7), (values.gem_gold.text, 5)],
    (values.cookie,): [(values.cookie.text, 50), (values.pretzel.text, 25), (values.fortune_cookie.text, 15), (values.pancakes.text, 10)],
    (values.pretzel,): [(values.cookie.text, 25), (values.pretzel.text, 50), (values.fortune_cookie.text, 15), (values.pancakes.text, 10)],
    (values.fortune_cookie,): [(values.cookie.text, 10), (values.pretzel.text, 25), (values.fortune_cookie.text, 50), (values.pancakes.text, 15)],
    (values.pancakes,): [(values.cookie.text, 10), (values.pretzel.text, 15), (values.fortune_cookie.text, 25), (values.pancakes.text, 50)],
    (values.omega_chessatron,): [(values.gem_white.text, 15), (values.ephemeral_token.text, 10), (values.anarchy_omega_chessatron.text, 10), (values.anarchy_chess.text, 40), (values.gem_gold.text, 25)],
    (values.anarchy_omega_chessatron,): [(values.gem_white.text, 40), (values.ephemeral_token.text, 30), (values.omega_chessatron.text, 30)],
    (values.hotdog,): [(values.hotdog.text, 95), (values.anarchy_chessatron.text, 5)],
    (values.ascension_token,): [(values.ascension_token.text, 100)],
    (values.middle_finger,): [(values.middle_finger.text, 100)],
    (values.cherry,): [(values.cherry.text, 100)],
    (values.rigged,): [(values.rigged.text, 100)],
}

# Every item that can be salvaged.
salvage_options = list(itertools.chain.from_iterable(salvage_weights.keys()))

# Every item that can show up as filler in a salvage.
filler_items = [values.gem_white, values.ephemeral_token, values.anarchy_chess, values.normal_bread, values.corrupted_bread, values.chessatron, values.anarchy_chessatron, values.omega_chessatron, values.anarchy_omega_chessatron, values.fuel, values.hotdog] \
    + values.all_very_shinies + values.all_shinies + values.all_anarchy_pieces + values.all_chess_pieces + values.all_rare_breads + values.all_special_breads