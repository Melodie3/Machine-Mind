# emoji.py

golden_brick = "<:brick_gold:971239215968944168>"


# CHESS

white_pawn = "<:Wpawn:961815364319207516>"
white_rook = "<:Wrook:961815364482793492>"
white_bishop = "<:Wbishop:961815364428263435>"
white_knight = "<:Wknight:958746544436310057>"
white_queen = "<:Wqueen:961815364461809774>"
white_king = "<:Wking:961815364411478016>"

black_pawn = "<:Bpawn:961815364436635718>"
black_rook = "<:Brook:961815364377919518>"
black_bishop = "<:Bbishop:961815364306608228>"
black_knight = "<:Bknight:961815364424048650>"
black_queen = "<:Bqueen:961815364470202428>"
black_king = "<:Bking:961815364327600178>"

chessboard_reference = {
    "p":black_pawn,
    "P":white_pawn,
    "r":black_rook,
    "R":white_rook,
    "b":black_bishop,
    "B":white_bishop,
    "n":black_knight,
    "N":white_knight,
    "q":black_queen,
    "Q":white_queen,
    "k":black_king,
    "K":white_king,
    "light square":":white_medium_square:",
    "dark square":":black_medium_square:"
}


white_pawn_anarchy = "<:wP:971046978349858936>"
white_rook_anarchy = "<:wR:971047003402403862>"
white_bishop_anarchy = "<:wB:971046928395665448>"
white_knight_anarchy = "<:wN:971046961811714158>"
white_queen_anarchy = "<:wQ:971046990312013844>"
white_king_anarchy = "<:wK:971046942144602172>"

black_pawn_anarchy = "<:bP:971046900038004736>"
black_rook_anarchy = "<:bR:971046920166457364>"
black_bishop_anarchy = "<:bB:971046862134050887>"
black_knight_anarchy = "<:bN:971046888486891642>"
black_queen_anarchy = "<:bQ:971046911551356948>"
black_king_anarchy = "<:bK:971046879540445275>"

chessboard_reference_anarchy = {
    "p":black_pawn_anarchy,
    "P":white_pawn_anarchy,
    "r":black_rook_anarchy,
    "R":white_rook_anarchy,
    "b":black_bishop_anarchy,
    "B":white_bishop_anarchy,
    "n":black_knight_anarchy,
    "N":white_knight_anarchy,
    "q":black_queen_anarchy,
    "Q":white_queen_anarchy,
    "k":black_king_anarchy,
    "K":white_king_anarchy,
    "light square":":yellow_circle:",
    "dark square":":purple_circle:"
}

chessboard_files = {
    0:":regional_indicator_a:",
    1:":regional_indicator_b:",
    2:":regional_indicator_c:",
    3:":regional_indicator_d:",
    4:":regional_indicator_e:",
    5:":regional_indicator_f:",
    6:":regional_indicator_g:",
    7:":regional_indicator_h:",
}

chessboard_ranks = {
    0:":one:",
    1:":two:",
    2:":three:",
    3:":four:",
    4:":five:",
    5:":six:",
    6:":seven:",
    7:":eight:",
}

##
#   BREAD
#

all_breads = [":bread:",
                ":french_bread:",
                ":croissant:",
                ":flatbread:",
                ":sandwich:",
                ":stuffed_flatbread:"]

rare_breads = [":doughnut:",
                ":bagel:",
                ":waffle:"]

emoji_conversions = { "🍞" : ":bread:",
                       "🥖" : ":french_bread:",
                       "🥐" : ":croissant:",
                       "🫓" : ":flatbread:",
                       "🥪" : ":sandwich:",
                       "🥙" : ":stuffed_flatbread:",
                       "🍩" : ":doughnut:",
                       "🥯" : ":bagel:" ,
                       "🧇" : ":waffle:",
                       "🖕" : ":middle_finger:"}

            

one_of_a_kind = ["<:anarchy_chess:960772054746005534>",     
                 "<:anarchy:960771114819264533>"]



# 8 pawns of each color
all_chess_pieces_black = [black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn, black_pawn,
                            black_rook, black_rook,
                            black_bishop, black_bishop,
                            black_knight, black_knight,
                            black_queen,
                            black_king]

                    
all_chess_pieces_white = [white_pawn,white_pawn, white_pawn, white_pawn, white_pawn, white_pawn,white_pawn, white_pawn, 
                            white_rook,  white_rook,
                            white_bishop, white_bishop,
                            white_knight, white_knight,
                            white_queen,
                            white_king]

# other

amogus = "<:sus:961517169424883722>"

#### Indexing

all_default_emoji = all_breads + rare_breads 


def get_named_emoji(name: str):

    #check for an emoji conversion
    #we do this first because a single char emoji isn't long enough for later checks
    if name in emoji_conversions.keys():
        return emoji_conversions[name]
    
    #print (f"All default emoji are: {all_default_emoji}")
    for default_emoji in all_default_emoji:

        #first check for direct match
        if name == default_emoji:
            return default_emoji

        #print(f"checking emoji {default_emoji}: length is {len(default_emoji)}, len-1 is {(len(default_emoji))-1}")
        #print(f"substring is {default_emoji[1:2]}")

        #then check for name w/o colons
        if name == default_emoji[1:(len(default_emoji))-1]:
            return default_emoji
    

    return None