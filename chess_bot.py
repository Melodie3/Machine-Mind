import importlib
import random
import typing
from datetime import datetime
import json

import chess

import chess.svg

import cairosvg

# from svglib.svglib import svg2rlg
# from svglib import svglib, utils
# from reportlab.graphics import renderPM
# import io
# import textwrap

from discord.ext import commands
import discord

import verification
import emoji
import bread.utility as utility

#   NOTE: To make RAM DISK, use following command on macos. This will creats a 8MB disk and mount it with the name "RAM_DISK_512MB"
#
#   diskutil erasevolume HFS+ RAM_Disk $(hdiutil attach -nomount ram://16384)
#
# To unmount:
# MAKE SURE THAT YOU'RE UNMOUNTING THE CORRECT DISK NUMBER
#    hdiutil unmount /Volumes/RAM_Disk/
#
#   hdiutil detach /dev/disk2
#

# NOTE: for CAIRO SVG, you need to possibly upgrade brew, then run the following commands:
# 
# pip3 install cairocffi
# brew install cairo
# 
# pip3 install cairosvg
# 
# source: https://stackoverflow.com/questions/37437041/dlopen-failed-to-load-a-library-cairo-cairo-2


example_position = "r1b3nr/p1pp1pkp/2n3p1/1pbQ2B1/4P3/5N2/PpP1KPPP/1R3B1R b - - 1 12"
example_position_2 = "4k1r1/p1ppP3/n4B1p/2p1N1p1/2N1P3/8/P4PPP/R3KB1R w KQ - 2 20" 
example_position_3 = "2r2b1r/pppb1Npp/2np3k/8/4PNnP/1P2P3/PBP1K1P1/R4B1R b - - 8 16" #checkmate
example_position_4 = "rnbq1bnr/ppppkppp/8/4p3/4P3/4K3/PPPP1PPP/RNBQ1BNR b - - 3 3"
example_position_5 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" #starting position
example_position_6 = "rnbqkbnr/ppppppp1/8/4P2p/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2" # en passant next with f5
example_position_7 = "rnbqkbnr/ppppp2p/8/5pp1/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3" #Scholar's mate with Qh5#

# 1. e4 f5 2. d4 g5 3. Qh5#  #probably scholar's mate

emoji_map = {
    "p":"<:Bpawn:961815364436635718>",
    "P":"<:Wpawn:961815364319207516>",
    "r":"<:Brook:961815364377919518>",
    "R":"<:Wrook:961815364482793492>",
    "b":"<:Bbishop:961815364306608228>",
    "B":"<:Wbishop:961815364428263435>",
    "n":"<:Bknight:961815364424048650>",
    "N":"<:Wknight:958746544436310057>",
    "q":"<:Bqueen:961815364470202428>",
    "Q":"<:Wqueen:961815364461809774>",
    "k":"<:Bking:961815364327600178>",
    "K":"<:Wking:961815364411478016>",
}

emoji_map_board_files = {
    0:":regional_indicator_a:",
    1:":regional_indicator_b:",
    2:":regional_indicator_c:",
    3:":regional_indicator_d:",
    4:":regional_indicator_e:",
    5:":regional_indicator_f:",
    6:":regional_indicator_g:",
    7:":regional_indicator_h:",
}

emoji_map_board_ranks = {
    0:":one:",
    1:":two:",
    2:":three:",
    3:":four:",
    4:":five:",
    5:":six:",
    6:":seven:",
    7:":eight:",
}

preface_message = """```\nSend '$move ***' to make a move, such as '$move e4'.
Send '$board setup' for a new game.
Send '$help board' for more information.```"""

board_help_text = """'$board' will show the current board.

'$board setup' will set up a new board, and give the FEN string for the previous one, in case you want to continue the game elsewhere.
'$board setup 960' or '$board setup chess960' will set up a 960 style board.
'$board setup ****' will set up the board based on the FEN string you provide.

'$move ****' will make a move using standard notation, such as '$move e4'
'$move takeback' or '$takeback' will request a takeback for the move you just made.
'$move draw' or '$draw' will offer a draw to the other player.
'$move resign' or '$resign' will resign immediately.

'$board fen' will output the FEN string so you can use it elsewhere.
'$board output' will do the same.
'$board lichess' will give a lichess link to the current setup of the board.
'$board pgn' will give formatted PGN of the game.

Each channel has its own dedicated chess board. If people are not actively playing, feel free to use $board setup to clean the board, as they will always be able to pick up where they left off.
"""

tempfile_path = "/Volumes/RAM_Disk/"

# class to track a chess game happening on a channel
class Chess_game():

    def initialize_variables(self):
        # self.channel = None

        self.game_board = chess.Board()

        self.game_details = ""
        self.starting_fen = None

        self.last_message_header = None
        self.last_message_body = None
        self.last_message_footer = None

        self.last_message_embed = None

        self.last_message_full_embed = None
        self.last_full_embed_info = None
        self.last_full_embed_commentary = None

        self.players_white = set() #empty set
        self.players_black = set()

        self.black_offers_draw = False
        self.white_offers_draw = False

        self.black_requests_takeback = False
        self.white_requests_takeback = False

        self.last_player_move_messages = list()

        self.moves = list() #empty list

    def __init__(self, starting_channel, starting_board = chess.Board()):
        self.initialize_variables()
        print ("New chess game object initialized for channel "+str(starting_channel))
        self.channel = starting_channel
        self.game_board = starting_board
        self.clean_slate()
        #game_board = chess.Board()
        pass

    def clean_slate(self):
        self.initialize_variables()
        self.last_message_header = None
        self.last_message_body  = None
        self.last_message_footer = None
        self.last_message_embed = None
        #game_board.reset()
        self.players_white = set()
        self.players_black = set()
        self.moves = list()
        self.game_details = ""
        self.black_offers_draw = False
        self.white_offers_draw = False
        self.black_requests_takeback = False
        self.white_requests_takeback = False
        self.starting_fen = None
        self.last_player_move_messages = list()

    

    def set_board(self, new_board):
        self.game_board = new_board

    def bake_fen(self):
        self.starting_fen = self.game_board.board_fen()

    #### IMPORT / EXPORT ####

    def imex_test(self):
        string = json.dumps(self.to_dict())
        self.from_dict(json.loads(string))

    def to_dict(self):
        output = dict()
        output["channel_name"] = self.channel.name
        output["moves"] = self.moves
        if self.starting_fen is not None:
            output["starting_fen"] = self.starting_fen
        output["channel_id"] = self.channel.id
        
        output["player_ids_white"] = list()
        output["player_ids_black"] = list()
        for player in self.players_white:
            output["player_ids_white"].append(player.id)
        for player in self.players_black:
            output["player_ids_black"].append(player.id)
        output["game_details"] = self.game_details

        output["guild_id"] = self.channel.guild.id

        return output
        # json_str = json.dumps(output, indent=4)
        # print("JSON String is \n"+json_str)
        # return json_str

    def from_dict(input: dict):
        print ("Restoring game from dict")
        restored_game = Chess_game(input["channel_id"])
        restored_game.clean_slate()

        # restored_game.channel = input["channel_id"]

        restored_game.game_board.reset()

        guild = bot_ref.get_guild(int(input["guild_id"]))

        restored_game.channel = guild.get_channel(input["channel_id"])

        if "starting_fen" in input.keys():
            print (f"game had FEN {input['starting_fen']}")
            restored_game.starting_fen = input["starting_fen"]
            restored_game.game_board = chess.Board(restored_game.starting_fen)
        
        for move in input["moves"]:
            print (f"Pushing move {move}")
            try:
                restored_game.moves.append(move)
                restored_game.game_board.push_san(move)
            except:
                print("Error pushing move "+move)
                pass

        if "player_ids_white" in input.keys():
            player_var = input["player_ids_white"]
            if type(player_var) is int:
                user = guild.get_member(player_var)
                restored_game.players_white.add(user)
            else: # is list
                for player_id in input["player_ids_white"]:
                    user = guild.get_member(player_id)
                    restored_game.players_white.add(user)
        
        if "player_ids_black" in input.keys():
            player_var = input["player_ids_black"]
            if type(player_var) is int:
                user = guild.get_member(player_var)
                restored_game.players_black.add(user)
            else: # is list
                for player_id in input["player_ids_black"]:
                    user = guild.get_member(player_id)
                    restored_game.players_black.add(user)

        restored_game.game_details = input["game_details"]

        return restored_game


            
    #### RENDERING ####

    def get_rendered_board(self):
        svg_code = None
        last_move = None
        num_moves = len(self.game_board.move_stack)
        #output_path = tempfile_path + f"board_{str(self.channel)}_{num_moves}.png"
        output_path = tempfile_path + f"board_{str(self.channel)}.png"
        if num_moves != 0:
            last_move = self.game_board.peek()
        
        svg_code = chess.svg.board(self.game_board, lastmove=last_move, size=600)

        cairosvg.svg2png(bytestring=svg_code,write_to=output_path) #uses not working cairosvg

        #drawing = svglib.svg2rlg(io.StringIO(textwrap.dedent(svg_code)))
        #drawing = svglib.svg2rlg(io.StringIO(textwrap.dedent(svg_code)))
        # drawing = svg2rlg("home.svg")
        # renderPM.drawToFile(drawing, output_path, fmt="PNG")
        # print (f"Done rendering board file to {output_path}")
        return output_path
        pass

    #### MESSAGING ######

    async def send_header(self, text):
        #print ("chess_game channel is "+str(self.channel))
        if self.last_message_header is not None:
            await self.last_message_header.delete()
        self.last_message_header = await self.channel.send(text)
    
    async def send_body(self, text):
        if self.last_message_body is not None:
            await self.last_message_body.delete()
        self.last_message_body = await self.channel.send(text)

    async def send_footer(self, text):
        if self.last_message_footer is not None:
            await self.last_message_footer.delete()
        self.last_message_footer = await self.channel.send(text)

    async def send_full_message(self, header, body, footer):
        temp_header = await self.channel.send(header)
        temp_body   = await self.channel.send(body)
        temp_footer = await self.channel.send(footer)
        try: # perhaps messages were deleted
            if self.last_message_header is not None:
                await self.last_message_header.delete()
            if self.last_message_body is not None:
                await self.last_message_body.delete()
            if self.last_message_footer is not None:
                await self.last_message_footer.delete()
        except:
            pass 
        self.last_message_header = temp_header
        self.last_message_body   = temp_body
        self.last_message_footer = temp_footer

        #self.last_message_header = await self.channel.send(header)
        #self.last_message_body   = await self.channel.send(body)
        #self.last_message_footer = await self.channel.send(footer)

    async def send_full_message_with_embed(self, header, embed, file, footer):
        temp_header = await self.channel.send(header)
        temp_embed   = await self.channel.send(file=file, embed=embed)
        temp_footer = await self.channel.send(footer)
        try: # perhaps messages were deleted
            if self.last_message_header is not None:
                await self.last_message_header.delete()
            if self.last_message_embed is not None:
                await self.last_message_embed.delete()
            if self.last_message_footer is not None:
                await self.last_message_footer.delete()
        except:
            pass 
        self.last_message_header = temp_header
        self.last_message_embed   = temp_embed
        self.last_message_footer = temp_footer

    async def send_embed(self, embed, file=None):
        #await ctx.send(file=file, embed=embed)
        
        if self.last_message_embed is not None:
            await self.last_message_embed.delete()
        self.last_message_embed = await self.channel.send(file=file, embed=embed)
        pass

    async def send_full_embed(self, info, commentary, image_path):
        embed = discord.Embed() #creates embed
        embed.title="Chessboard"
        #embed.description="Desc"
        file = discord.File(image_path, filename="board.png")
        embed.set_image(url="attachment://board.png")
        #embed.set_image(image)
        embed.color = discord.Color(0x8790ff) # 8790ff

        embed.add_field(name="Commentary", value=commentary, inline=False)
        #embed.add_field( value=commentary, inline=False)
        embed.add_field(name="Info", value=info, inline=False)
        
        # embed.set_footer(text=preface_message)

        # await self.channel.send(file=image, embed=embed)
        new_embed = await self.channel.send(file=file, embed=embed)
        new_footer = await self.channel.send(commentary)
        if self.last_message_embed is not None:
            await self.last_message_embed.delete()
        if self.last_message_footer is not None:
            await self.last_message_footer.delete()
        self.last_message_embed = new_embed
        self.last_message_footer = new_footer
        pass

    ######################
    #### GAME STUFF ######
    ######################

    def add_move(self, player: discord.Member, move_text):
        #if a move is made, a draw offer is no longer valid
        self.black_offers_draw = False
        self.white_offers_draw = False
        self.black_requests_takeback = False
        self.white_requests_takeback = False

        player_name = player.display_name
        if utility.contains_ping(player.display_name):
            player_name = player.name
        print("move added for "+player_name+" in channel "+str(self.channel))
        
        #add player names to roster
        if (self.game_board.turn is chess.WHITE):
            # NOTE: THIS IS BACKWARDS ON PURPOSE,
            # the move is already made by the time we're adding it
            self.players_black.add(player)
        else:
            self.players_white.add(player)

        #add move text to list
        self.moves.append(move_text)
        
        #print ("full move list is "+str(self.moves))
        #print ("move list id is "+str(id(self.moves)))

    async def end_game(self, reason=None):
        if not (self.is_starting_position()):
            
            # append new text to previous footer
            new_text = self.last_message_footer.content + "\n\n"
            #new_text = ""

            if (self.game_board.is_game_over()):
                new_text += "Good game."
                pass
            else:
                new_text += "This game has been ended"
                if reason is not None:
                    new_text += ", because " + reason
                else:
                    new_text += "."

                new_text += "\n\nIf you'd like to continue this game later, use the following FEN:\n"\
                    + "`" + self.game_board.fen() + "`\n" \
                    +"Here is a lichess link:\n"+Chess_bot.get_lichess_link(self.game_board)

            if self.last_message_footer is not None:
                try: #message may have been deleted
                    await self.last_message_footer.edit(content=new_text)
                except:
                    pass

            #now we do header
            new_header = "```\n" +Chess_bot.get_pgn(self) + "\n```"
            if self.last_message_header is not None:
                try: #message may have been deleted
                    await self.last_message_header.edit(content=new_header)
                except:
                    pass
        
        #clear all
        
        self.game_board.reset()
        self.clean_slate()

    def is_starting_position(self):
        #print("checking if starting position")
        #print("move stack is "+str(self.game_board.move_stack))
        #if (self.game_board.fen() == chess.STARTING_FEN):
            #print("looks like starting position to me")
        if len(self.game_board.move_stack) == 0: #if no moves
            return True
        #print ("doesn't look like it")
        return False





class Chess_bot(commands.Cog, name="Chess"):

    games = {}

    def __init__(self, bot):
        #print("chess __init__ called")
        self.bot = bot

        self.boards = {} #empty dictionary
        self.previous_board_messages = {} # so we can delete the last one once we get a new one
        #print("boards is: "+str(self.boards)+", bot is "+str(self.bot))
        #print("chess module is: "+ str(chess))
        #print(chess.Board)
        #print("signature of get_board is "+signature(get_board))

    @commands.command( hidden=True )
    @commands.is_owner()
    async def test_render(self, ctx):
        current_game = self.get_game(ctx.channel)
        

        # image_path = current_game.get_rendered_board()
        # await ctx.send("Board rendered.")

        # # color for MM is 8790ff
        # embed = discord.Embed() #creates embed
        # embed.title="Title"
        # embed.description="Desc"
        # file = discord.File(image_path, filename="board.png")
        # embed.set_image(url="attachment://board.png")
        
        # embed.color = discord.Color(0x8790ff) # 8790ff

        # await ctx.send(file=file, embed=embed)

    ###################
    #  Board Command  #
    ###################

    @commands.command(
        brief="Set up or view the channel's chess board",
        help=board_help_text
    )
    async def board(self, ctx, *args):
        print ("$board called, "+str(len(args))+" args which are "+str(args))

        current_game = self.get_game(ctx.channel)
        work_board = await self.get_board(ctx)

        #no args, just print board
        if (len(args) == 0):
            
            #await self.print_board(ctx, work_board)
            await self.print_game(current_game)

            return #there is only one possible zero-arg command
        
        # setup subcommand
        if (args[0].lower() == "setup"):
            # plain setup command
            if (len(args) == 1):
                print("resetting board")
                #await ctx.send("The board has been reset.\n"+
                #                "If you would like to continue the previous game, the FEN string is "+
                #                work_board.fen())

                #await self.end_previous_board(ctx, work_board, reason = "A new game has been started.")

                await current_game.end_game(reason = "a new game has been started.")

                #work_board.reset()
                #await self.print_board(ctx, work_board, delete_last=False)
                await self.print_game(current_game)
                return

            #chess960
            elif (len(args) >= 2) and \
                (args[1].lower() == "chess960" or \
                 args[1] == "960"):
                
                index960 = -1
                if len(args) == 3:
                    try:
                        index960 = int(args[2])
                    except:
                        print("Failed to parse 960 index number")
                        pass
                
                if index960 < 0 or index960 > 959:
                    index960 = random.randint(0, 959)
                
                await current_game.end_game(reason = "a new game has been started.")
                new_board = chess.Board.from_chess960_pos(index960)
                print( "new board is 960, index "+str(index960))
                print (new_board)
                current_game.set_board(new_board)
                current_game.bake_fen() # indicate that it is a nonstandard FEN
                current_game.game_details = "Chess960, starting postition #" + str(index960)
                await self.print_game(current_game)
                pass
                return

            # setup with FEN
            else:
                print("assuming fen string for setup")
                #more commands, assume it's a FEN string, take the rest and convert to string
                fen_array = args[1 : len(args)]
                fen_string = ' '.join(fen_array)
                print("read potential fen string as "+fen_string)
                try:
                    print ("trying to make a new board")
                    new_board = chess.Board(fen_string)
                    print ("new board made, is "+str(new_board))
                    print ("ending current game")
                    await current_game.end_game(reason = "a new board was set up.")
                    print ("ended")
                    current_game.set_board(new_board)
                    current_game.bake_fen() # put in the FEN to remember
                    print ("game set with new pieces")
                    #old_board = work_board.copy()
                    #work_board.set_fen(fen_string)
                    #await self.end_previous_board(ctx, old_board, reason = "A new board has been set up.")
                except:
                    await ctx.send("I tried to interpret that as a FEN string, but it didn't seem to work.")
                    return
                await ctx.send("The board has been setup as per your instructions.")
                #await self.print_board(ctx, work_board, delete_last=False)
                await self.print_game(current_game)
                return

        if (args[0].lower() == "fen") or (args[0].lower() == "output"):
            #output = work_board.fen()
            output = current_game.game_board.fen()
            print("outputting board: " + output)
            await ctx.send("Board position in FEN notation: "+output)

        if (args[0].lower() == "lichess"):
            #output = self.get_lichess_link(work_board)
            output = Chess_bot.get_lichess_link(current_game.game_board)
            await ctx.send("Here is a lichess link for the current board:\n"+output)

        if (args[0].lower() == "pgn"):
            output = Chess_bot.get_pgn(current_game)
            await ctx.send("Here is the PGN for the current board:\n```\n"+output+"\n```")

        if (args[0].lower() == "help"):
            output = "```\n" + board_help_text + "```"
            await ctx.send(output)


    ###############################
    #######  MOVE COMMAND  ########
    ###############################

    # todo
    # add draw function?
    # add detection for en passant

    @commands.command(
        brief="Makes a chess move.",
        help="Takes Standard Algabraic Notation, such as 'e4'. Also accepts 'draw' and 'resign'."
    )
    async def move(self, ctx, arg):
        #work_board = await self.get_board(ctx)
        current_game = self.get_game(ctx.channel)
        work_board = current_game.game_board

        turn = work_board.turn
        brick = False

        if (arg.lower() == "resign"):
            await self.resign(ctx)
            return
        elif (arg == "draw"):
            await self.draw(ctx)
            return
        elif (arg == "takeback"):
            await self.takeback(ctx)
            return

        try:
            # (I don't know if this is a fully necessary way to do it but it should work)

            #gets the representation of the move
            move = work_board.parse_san(arg)

            if work_board.has_legal_en_passant():
                if work_board.is_en_passant(move):
                    pass #acceptable
                else: #en passant declined ??
                    brick = True
                    pass 
            #turns it back into a string for our recording
            move_string = work_board.san(move)
            # then makes the move
            work_board.push_san(move_string)
            pass
        except ValueError:
            await ctx.reply("It seems that is not a legal move, or is not properly specified.\nApologies, but I am not currently capable of performing that.")
        else:
            current_game.add_move(ctx.message.author, move_string) #adds the move to the list
            #await self.print_board(ctx, work_board)
            await self.print_game(current_game)


            current_game.last_player_move_messages.append(ctx.message)
            # if len(current_game.last_player_move_messages) > 4:
            #     old_message = current_game.last_player_move_messages.pop(0)
            #     await old_message.delete()
            # await ctx.message.delete()


            if work_board.is_game_over():
                await current_game.end_game()
        pass
        if brick:
            await ctx.reply("You declined en passant. Tsk, tsk.")
            #JSON_cog = bot_ref.get_cog("JSON")
            #bot_ref.brick(ctx, ctx.author)
            await ctx.invoke(self.bot.get_command('brick'), member=ctx.author, duration=None)
        

    ##############################################################################################################################################################
    #########   DRAW

    @commands.command(
        brief="Offers a draw.",
        help="Must be made by a person who has already moved for that team."
    )
    async def draw(self, ctx):
        print("Draw offered")
        current_game = self.get_game(ctx.channel)
        work_board = current_game.game_board

        turn = work_board.turn
        # 4 variations:
        # white's turn, white offers
        # white's turn, black accepts
        # black's turn, black offers
        # black's turn, white accepts

        # is white the one who started the offer
        if (turn == chess.WHITE): 
            
            # if white is in the process of starting the offer
            if (current_game.white_offers_draw is False):
                # if the person offering is actually the white player
                if (ctx.author in current_game.players_white):
                    current_game.white_offers_draw = True
                    await ctx.send("White has offered a draw. Does Black accept?\n\nReply $draw to accept, or ignore this message to reject.")
                    return
                elif (ctx.author in current_game.players_black):
                    await ctx.send("You must wait until your turn to offer a draw.")
                    return
                else:
                    await ctx.reply("You aren't authorized to offer a draw from White.")
                    return
            # if white has already started the offer and it is black's job to respond
            elif (current_game.white_offers_draw is True):
                # if black is responding with acceptance
                if (ctx.author in current_game.players_black):
                    await ctx.reply("The game has been drawn.")
                    await current_game.end_game(reason = "both players agreed to a draw.")
                    return
                else:
                    await ctx.reply("You aren't authorized to offer a draw from Black.")
                    return

        else: # turn is BLACK
            # if black is in the process of starting the offer
            if (current_game.black_offers_draw is False):
                # if the person offering is actually the black player
                if (ctx.author in current_game.players_black):
                    current_game.black_offers_draw = True
                    await ctx.send("Black has offered a draw. Does White accept?\n\nReply $draw to accept, or ignore this message to reject.")
                    return
                elif (ctx.author in current_game.players_white):
                    await ctx.send("You must wait until your turn to offer a draw.")
                    return
                else:
                    await ctx.reply("You aren't authorized to offer a draw from Black.")
                    return
            # if black has already started the offer and it is white's job to respond
            elif (current_game.black_offers_draw is True):
                # if white is responding with acceptance
                if (ctx.author in current_game.players_white):
                    await ctx.reply("The game has been drawn.")
                    await current_game.end_game(reason = "both players agreed to a draw.")
                    return
                else:
                    await ctx.reply("You aren't authorized to offer a draw from White.")
                    return

    ##############################################################################################################################################################
    #########   TAKEBACK (IN PROGRESS)

    @commands.command(
        brief="Requests a takeback.",
        help="Must be made by the team who most recently moved."
    )
    async def takeback(self, ctx):
        print("takeback requested")
        current_game = self.get_game(ctx.channel)
        work_board = current_game.game_board

        turn = work_board.turn
        # 4 variations:
        # white's turn, black offers
        # white's turn, white accepts
        # black's turn, white offers
        # black's turn, black accepts

        #black_requests_takeback = False
        #white_requests_takeback = False

        if len(current_game.moves) == 0:
            await ctx.reply("There are not enough moves to take back.")
            return
        
        # is black who messed up and is requesting the takeback
        if (turn == chess.WHITE): 
            
            # if black is in the process of starting the offer
            if (current_game.black_requests_takeback is False):
                # if the person requesting is actually the black player
                if (ctx.author in current_game.players_black):
                    current_game.black_requests_takeback = True
                    await ctx.send("*Takeback Requested*\n(from Black)\n\nReply $takeback to accept, or ignore this message to reject.")
                    return
                elif (ctx.author in current_game.players_white):
                    await ctx.send("You cannot request a takeback on your own turn.")
                    return
                else:
                    await ctx.reply("You aren't authorized to request a takeback.")
                    return
            # if black has already started the offer and it is black's job to respond
            elif (current_game.black_requests_takeback is True):
                # if white is responding with acceptance
                if (ctx.author in current_game.players_white):
                    #await ctx.reply("The game has been drawn.")
                    #await current_game.end_game(reason = "both players agreed to a draw.")
                    work_board.pop() #pops the move from the board itself
                    current_game.moves.pop() #pops the move from the internal move list
                    await ctx.send("Takeback has been accepted.")
                    await self.print_game(current_game)
                    return
                else:
                    await ctx.reply("You aren't authorized to accept that takeback.")
                    return

        else: # turn is BLACK
            # if white is in the process of starting the offer
            if (current_game.white_requests_takeback is False):
                # if the person offering is actually the white player
                if (ctx.author in current_game.players_white):
                    current_game.white_requests_takeback = True
                    await ctx.send("*Takeback Requested*\n(from White)\n\nReply $takeback to accept, or ignore this message to reject.")
                    return
                elif (ctx.author in current_game.players_black):
                    await ctx.send("You cannot request a takeback on your own turn.")
                    return
                else:
                    await ctx.reply("You aren't authorized to request a takeback.")
                    return
            # if white has already started the request and it is black's job to respond
            elif (current_game.white_requests_takeback is True):
                # if black is responding with acceptance
                if (ctx.author in current_game.players_black):
                    #await ctx.reply("The game has been drawn.")
                    #await current_game.end_game(reason = "both players agreed to a draw.")
                    work_board.pop() #pops the move from the board itself
                    current_game.moves.pop() #pops the move from the internal move list
                    await ctx.send("Takeback has been accepted.")
                    await self.print_game(current_game)
                    return
                else:
                    await ctx.reply("You aren't authorized to accept that takeback.")
                    return

    ##############################################################################################################################################################
    #########   RESIGN

    @commands.command(
        brief="Resigns.",
        help="Must be made by a person who has already moved for that team."
    )
    async def resign(self, ctx):
        current_game = self.get_game(ctx.channel)
        work_board = current_game.game_board

        turn = work_board.turn

        if (turn == chess.WHITE and ctx.author in current_game.players_white):
            await current_game.end_game(reason = "White resigned.")
            await ctx.reply("White resigned.")
        elif (turn == chess.BLACK and ctx.author in current_game.players_black):
            await current_game.end_game(reason = "Black resigned.")
            await ctx.reply("Black resigned.")

        #second batch, for not the person's turn
        elif (ctx.author in current_game.players_white):
            await current_game.end_game(reason = "White resigned.")
            await ctx.reply("White resigned.")
        elif (ctx.author in current_game.players_black):
            await current_game.end_game(reason = "Black resigned.")
            await ctx.reply("Black resigned.")
        else:
            await ctx.reply("Only a player in the game may resign.")

    ###############################
    ########    GAME    ###########
    ###############################

    @commands.group( hidden = True)
    async def chess(self, ctx, *args):
        #setup
        #960
        #variant ****
        #end

        #resign
        #draw
        #end
        #new(?)
        #notify
        #three-check
        #board = chess.variant.find_variant("name: str") 
        pass
        await ctx.reply("This command doesn't do anything yet.")

    # takes 960, or a name, or both
    @chess.command( hidden = True)
    async def variant(self, ctx, *args):
        if len(args) == 0:
            return
        
        #first check for 960
        chess960 = False
        if ("960" in args):
            chess960 = True
            args.remove("960")
        elif "chess960" in args:
            chess960 = True
            args.remove("chess960")
        
        if chess960 == True:
            if len(args) == 0:
                #create 960 board and return
                pass
                return
            else:
                #create 960 board and continue, I guess
                pass

        variant_name = " ".join(args)

        board = chess.variant.find_variant(variant_name) 
        #TODO : actually do something with this lol
        pass


    ###############################
    #########  UTILITY  ###########
    ###############################
    
    ##############################
    ######## GAME

    def get_game(self, channel):
        #print ("getting game")
        if channel in self.games:
            #print("game already exists")
            return self.games[channel]
        else:
            #print("making new game")
            self.games[channel] = Chess_game(channel, chess.Board())
            return self.games[channel]

    ##############################
    ######## BOARD 

    #gets board for current channel, or creates it if it doesn't exist yet
    async def get_board(self, ctx):
        print("getting board:")
        work_board = None
        if ctx.channel in self.boards:
            print("board already exists")
            work_board = self.boards[ctx.channel] #get board from dict
        else:
            print("making new board for "+str(ctx.channel))
            work_board = chess.Board() # set up a new board
            #board = "a"
            self.boards[ctx.channel] = work_board # add to dict
        return work_board

    # finds the previous board posted in the channel so we can delete it when we make a new one
    def get_previous_board_message(self, ctx):
        print("getting previous board message")
        message = None
        if ctx.channel in self.previous_board_messages:
            print("found it.")
            message = self.previous_board_messages[ctx.channel]
        return message

    def set_previous_board_message(self, ctx, message):
        print("setting new previous board message")
        self.previous_board_messages[ctx.channel] = message

    async def end_previous_board(self, ctx, work_board, reason = None):
        prev_message = self.get_previous_board_message(ctx)
        if prev_message is not None:
            #new_text = prev_message.content + "\n\n"
            new_text = ""
            if reason is not None:
                new_text += reason
            else:
                new_text += "The game has been ended."
            # check if there's a game in progress

            if not (work_board.is_game_over() or self.is_starting_position(work_board)):
                new_text += "\nIf you'd like to continue it later, use the following FEN:\n"\
                    +work_board.fen() \
                    +"\nHere is a lichess link: "+Chess_bot.get_lichess_link(work_board)
           
            
            print("Ending message is:"+new_text)
            await prev_message.reply(new_text)
            self.boards.pop(ctx.channel)

    def get_lichess_link(work_board):
        output = work_board.fen()
        output = output.replace(" ","_") #convert to be URL safe
        output = "https://lichess.org/editor/" + output #append to lichess
        return output

    def is_starting_position(self, work_board):
        if self.board.fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
            return True
        else:
            return False

    ###############################
    ########   OUTPUT   ###########
    ###############################

    def render_board_emoji(self, work_board):
        output = ""

        #add files labels
        for i in range(0,8):
            output += emoji_map_board_files[i] + " " #no spacing
        output += "\n"

        whiteSquare = True #top left square is white

        for index_rank in range(7,-1,-1):
            for index_file in range(0,8):
                piece = work_board.piece_at(index_rank*8+index_file)
                square_label = ""

                if piece is None:
                    if whiteSquare:
                        #square_label += ":white_medium_square:"

                        square_label += ":white_large_square:"

                        #square_label += ":white_circle:"
                        #square_label += ":white_small_square:"
                        #square_label += "<:brick_fide:961517570396135494>"
                    else:
                        #square_label += ":black_medium_square:"
                        square_label += ":black_large_square:"

                        #square_label += ":blue_square:"
                        #square_label += ":white_circle:"
                        #square_label += ":black_small_square:"
                        #square_label += "<:brick_fide:961517570396135494>"

                #other piece, look it up
                else:
                    square_label += emoji_map[piece.symbol()]

                square_label += " " #add spacing
                output += square_label #add piece
                whiteSquare = not whiteSquare #alternate white and black

            output += emoji_map_board_ranks[index_rank]
            #letter_rank += 1
            output += "\n" #newline every 8 spaces
            whiteSquare = not whiteSquare # it flips again when going back do

        return output

        
    async def print_game(self, current_game):
        work_board = current_game.game_board

        #await current_game.send_header(preface_message)
        #await current_game.send_body(self.render_board_emoji(work_board))
        #await current_game.send_footer(Chess_bot.get_commentary(work_board))

        header = preface_message + "\n" + Chess_bot.get_ingame_notation(current_game)
        
        embed = discord.Embed() #creates embed
        # embed.title="Discord Chess"
        # embed.description=header

        embed.color = discord.Color(0x8790ff) #light blue

        try:
            image_path = current_game.get_rendered_board()
            file = discord.File(image_path, filename="board.png")
            embed.set_image(url="attachment://board.png")
        except:
            file = None
            embed.description = "An error occurred while rendering the board. The board cache might not exist."

        
        

        # await current_game.send_full_embed(info=header, 
        #                                     commentary= Chess_bot.get_commentary(current_game),
        #                                     image_path=image_path)

        await current_game.send_full_message_with_embed(header=header,
                                                    embed=embed,
                                                    file=file,
                                                    footer = Chess_bot.get_commentary(current_game))
        
        # await ctx.send(file=file, embed=embed)
        # await current_game.send_full_message(header, 
        #                                      self.render_board_emoji(work_board), 
        #                                      Chess_bot.get_commentary(current_game))

    #commentary
    def get_commentary(current_game: Chess_game):
        if type(current_game) is Chess_game:
            work_board = current_game.game_board
        else:
            raise ValueError("We don't take game board anymore")
        output = ""
        if work_board.is_game_over():
            outcome = work_board.outcome()
            if work_board.is_checkmate():
                output += "Checkmate.\n"
            elif work_board.is_stalemate():
                output += "Stalemate."
            else:            
                output += str(outcome.termination) + "\n"

            if outcome.winner is chess.WHITE:
                output += "White wins!"
            elif outcome.winner is chess.BLACK:
                output += "Black wins!"
            pass
            
            return output
        
        if work_board.is_check():
            output += "Check.\n"

        if work_board.has_legal_en_passant():
            output += "En passant is available. **You'd better take it.**\n\n"

        if work_board.turn is chess.WHITE:
            
            output += "White to move."
            for player in current_game.players_white:
                output += " " + player.mention
        else:
            output += "Black to move."
            for player in current_game.players_black:
                output += " " + player.mention
        
        return output

    def get_pgn(current_game):
        output = ""
        if (current_game.game_details != ""):
            output += f'[Variant "{current_game.game_details}"]\n'
        if (current_game.starting_fen is not None):
            output += f'[FEN "{current_game.starting_fen}"]\n'
        output += '[Site "AnarchyChess Official Discord"]\n'
        output += datetime.now().strftime('[Date "%Y.%-m.%-d"]\n')
        output += f'[White "{Chess_bot.get_printed_player_list(current_game.players_white)}"]\n'
        output += f'[Black "{Chess_bot.get_printed_player_list(current_game.players_black)}"]\n'

        output += Chess_bot.get_moves_notation(current_game)
        return output
        

    def get_ingame_notation(current_game):
        output = "```\n"

        output += current_game.game_details
        if current_game.game_details != "":
            output += "\n"

        output += "White: " + Chess_bot.get_printed_player_list(current_game.players_white)
        #for name in current_game.players_white:
        #    output += " " + name 
        output += "\nBlack: " + Chess_bot.get_printed_player_list(current_game.players_black)
        #for name in current_game.players_black:
        #    output += " " + name

        output += "\n"

        output += Chess_bot.get_moves_notation(current_game)
        #move_num = 1
        #move_stack = current_game.moves
        #for i in range(len(move_stack)):
        #    if ((i) % 2 is 0): #every 2 moves
        #        output += str(int(i/2)+1) + ". "
        #    output += move_stack[i] + " "

        output += "```"
        return output

    def get_moves_notation(current_game):
        output = ""
        move_num = 1
        move_stack = current_game.moves
        for i in range(len(move_stack)):
            if ((i) % 2 == 0): #every 2 moves
                output += str(int(i/2)+1) + ". "
            output += move_stack[i] + " "
        return output
        


    def get_printed_player_list(player_list: typing.Set[discord.Member]):
        length = len(player_list)
        output = ""
        player_num = 1

        for player in player_list:
            # first add the name to the list
            if player.display_name in ["@everyone", "@here"]:
                output += player.name
            else:
                output += player.display_name

            #if there's at least 2 people, AND we're not at the end
            if length >= 2 and player_num < length: 
                output += ", "
            player_num += 1
        
        return output

    #############################################
    ########   STARTUP  /  SHUTDOWN   ###########
    #############################################

    @commands.command( hidden = True )
    @commands.is_owner()
    async def chess_data_save(self, ctx):
        self.internal_save()
        await ctx.send("Done.")

    def internal_save(self):
        JSON_cog = bot_ref.get_cog("JSON")
        #JSON_cog.load_all_data() 
        #cabinet = JSON_cog.get_filing_cabinet("chess", create_if_nonexistent=True)
        outfile = dict()

        for channel in self.games:
            game = self.games[channel]
            id = str(channel.id)
            saved_game = game.to_dict()
            outfile[id] = saved_game

        JSON_cog.set_filing_cabinet("chess", outfile)
        JSON_cog.save_all_data()

    def capture_data(self, json_store):
        outfile = dict()

        for channel in self.games:
            game = self.games[channel]
            id = str(channel.id)
            saved_game = game.to_dict()
            outfile[id] = saved_game

        json_store.set_filing_cabinet("chess", outfile)
        json_store.save_all_data()

    @commands.command( hidden = True )
    @commands.is_owner()
    async def chess_data_load(self, ctx):
        self.internal_load()
        await ctx.send("Done.")

    def internal_load(self):
        JSON_cog = bot_ref.get_cog("JSON")
        JSON_cog.load_all_data() 
        cabinet = JSON_cog.get_filing_cabinet("chess", create_if_nonexistent=True)

        for id in cabinet.keys():
            print (f"loading game {id}")
            # try:
            saved_game = cabinet[id]
            restored_game = Chess_game.from_dict(saved_game)
            self.games[restored_game.channel] = restored_game # restored_game
            # except:
            #     print(f"failed to load game {id}")
        

    @commands.command(
        hidden = True
    )
    @commands.is_owner()
    async def graceful_shutdown(self, ctx):
        print("graceful shutdown called")
        for channel in self.games:
            game = self.games[channel]
            await game.end_game(reason="the bot was taken offline temporarily for maintenance.")
        await ctx.send("Done.")

    @commands.command(
        hidden=True
    )
    @commands.is_owner()
    async def chess_imex_test(self, ctx):
        print("outputting all games to JSON")
        for channel in self.games:
            game = self.games[channel]
            # game.to_dict()
            game.imex_test()
        await ctx.send("Done.")

bot_ref = None
cog_ref = None

async def setup(bot):

    global bot_ref
    global cog_ref

    bot_ref = bot
    cog_ref = Chess_bot(bot)
    #return bot.add_cog(Chess_bot(bot))
    importlib.reload(verification)
    importlib.reload(emoji)
    importlib.reload(utility)

    await bot.add_cog(cog_ref)

    cog_ref.internal_load()
    #bot.add_cog(Chess_game(bot)) #do we want to actually have this be a *cog*, or just a helper class?

#seems mostly useless since we can't call anything async
def teardown(bot):
    print('chess bot is being unloaded, saving data.')
    try:
        cog_ref.internal_save()
        print("Done saving data.")
    except:
        print("An error occurred  trying to save data.")
    #await bot.graceful_shutdown()
    #Chess_bot.graceful_shutdown(bot)
