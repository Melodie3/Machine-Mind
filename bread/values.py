


import typing

############ class

class Emote:
    value = 0
    emoji = None
    text = ""
    attributes = []
    name = None

    def __init__(self, text, value=0, name=None, emoji=None, attributes=[], awards_value=False, alchemy_value=None, giftable=True, alternate_names=[]):
        self.text = text
        self.value = value
        self.name = name
        self.emoji = emoji
        self.attributes = attributes
        self.awards_value = awards_value
        self.giftable = giftable
        if alchemy_value is None:
            self.alchemy_value = value
        self.alternate_names = alternate_names

    def __str__(self):
        if self.name is not None:
            return f"<Emote: {self.name}>"
        elif self.text is not None:
            return f"<Emote: {self.text}>"
        else:
            return "<Emote object>"
    
    def __repr__(self):
        return self.__str__()

    def gives_alchemy_award(self):
        if hasattr (self, "awards_value"):
            return self.awards_value
        else:
            return False

    def get_alchemy_value(self):
        if self.gives_alchemy_award():
            if hasattr (self, "alchemy_value"):
                return self.alchemy_value
            else:
                return self.value
        else:
            return 0

    def get_representation(self, guild_id):
        if self.emoji is not None:
            return self.emoji
        else:
            return self.text

    def can_be_gifted(self):
        if hasattr(self, "giftable"):
            return self.giftable
        else:
            return True

############ regular bread

# normal_bread = { "value" : 1,
#                 "emoji" :  "🍞",
#                 "text" : ":bread:" }

normal_bread =  Emote(
    text=":bread:",
    value=1,
    name="bread",
    emoji= "🍞",
)

############ speacial breads

# flatbread = { "value" : 5,
#              "text" : ":flatbread:",
#              "emoji" : "🫓",
#              "attribute" : "special_bread"}

flatbread =  Emote(
    text=":flatbread:",
    value=5,
    name="flatbread",
    emoji= "🫓",
    attributes=["special_bread"]
)

# stuffed_flatbread = {
#     "value" : 5,
#     "text" : ":stuffed_flatbread:",
#     "emoji" : "🥙",
#     "attribute" : "special_bread"
# }

stuffed_flatbread = Emote(
    text=":stuffed_flatbread:",
    value=5,
    name="stuffed_flatbread",
    emoji= "🥙",
    attributes=["special_bread"]
)

# french_bread = { "value" : 5,
#                         "text" : ":french_bread:",
#                         "emoji" : "🥖",
#                         "attribute" : "special_bread"}

french_bread = Emote(
    text=":french_bread:",
    value=5,
    name="french_bread",
    emoji= "🥖",
    attributes=["special_bread"]
)

# croissant = { "value" : 5,
#                         "text" : ":croissant:",
#                         "emoji" : "🥐",
#                         "attribute" : "special_bread"}

croissant = Emote(
    text=":croissant:",
    value=5,
    name="croissant",
    emoji= "🥐",
    attributes=["special_bread"]
)

# sandwich = { "value" : 5,
#                         "text" : ":sandwich:",
#                         "emoji" : "🥪",
#                         "attribute" : "special_bread"}

sandwich = Emote(
    text=":sandwich:",
    value=5,
    name="sandwich",
    emoji= "🥪",
    attributes=["special_bread"]
)

all_special_breads = [sandwich, croissant, french_bread, stuffed_flatbread, flatbread]

########### rare breads 

class Rare_Bread_Emote(Emote):
    def __init__(self, name, text, emoji):
        self.text = text
        self.name = name
        self.emoji = emoji
        self.value = 10
        self.attributes = ["rare_bread"]
        self.awards_value = False
        self.alchemy_value = 10
        self.alternate_names = []

# doughnut = {
#     "value" : 10,
#     "text" : ":doughnut:",
#     "emoji" : "🍩",
#     "attribute" : "special_bread"
# }

doughnut = Emote(
    text=":doughnut:",
    value=10,
    name="doughnut",
    emoji= "🍩",
    attributes=["rare_bread"]
)

# bagel = {
#     "value" : 10,
#     "text" : ":bagel:",
#     "emoji" : "🥯",
#     "attribute" : "special_bread"
# }

bagel = Emote(
    text=":bagel:",
    value=10,
    name="bagel",
    emoji= "🥯",
    attributes=["rare_bread"]
)

# waffle = {
#     "value" : 10,
#     "text" : ":waffle:",
#     "emoji" : "🧇",
#     "attribute" : "special_bread"
# }

waffle = Emote(
    text=":waffle:",
    value=10,
    name="waffle",
    emoji= "🧇",
    attributes=["rare_bread"]
)

all_rare_breads = [doughnut, bagel, waffle]

########## lottery win

lottery_win = Emote(
    text=":fingers_crossed:",
    value=1000,
    name="fingers_crossed",
    emoji= "🤞",
    attributes=["lottery_win"]
)

########## uniques

# anarchy = {
#     "value" : 8000,
#     "text" : "<:anarchy:960771114819264533>",
#     "attribute" : "one_of_a_kind"
# }

anarchy = Emote(
    text="<:anarchy:960771114819264533>",
    value=500000,
    name="anarchy",
    attributes=["one_of_a_kind", "unique"],
    awards_value = True
)

# anarchy_chess = {
#     "value" : 8000,
#     "text" : "<:anarchy_chess:960772054746005534>",
#     "attribute" : "one_of_a_kind"
# }

anarchy_chess = Emote(
    text="<:anarchy_chess:960772054746005534>",
    value=2000,
    name="anarchy_chess",
    attributes=["unique", "many_of_a_kind"],
    alternate_names = ["moak"]
)

# horsey = {
#     "value" : 8000,
#     "text" : "<:horsey:960727531592511578>", 
#     "attribute" : "one_of_a_kind"
# }

horsey = Emote(
    text="<:horsey:960727531592511578>",
    value=500000,
    name="horsey",
    attributes=["one_of_a_kind", "unique"],
    awards_value = True
)

# holy_hell  = {
#     "value" : 8000,
#     "text" : "<:holy_hell:961184782253948938>",
#     "attribute" : "one_of_a_kind"
# }

holy_hell = Emote(
    text="<:holy_hell:961184782253948938>",
    value=500000,
    name="holy_hell",
    attributes=["one_of_a_kind", "unique"],
    awards_value = True
)

chessatron = Emote(
    text="<:chessatron:996668260210708491>",
    value=2000,
    name="chessatron",
    attributes=["unique", "full_chess_set"],
    awards_value = True

)

omega_chessatron = Emote(
    text="<:omega_chessatron:1010359685339160637>",
    value=40000,
    name="omega_chessatron",
    attributes=["unique"],
    awards_value = True,
    giftable=False
)

# "<:anarchy_chess:960772054746005534>",
# "<:horsey:960727531592511578>", 
# "<:holy_hell:961184782253948938>"]     
# "<:anarchy:960771114819264533>"

all_one_of_a_kind = [anarchy, anarchy_chess, horsey, holy_hell]
all_uniques =       [anarchy, anarchy_chess, horsey, holy_hell, chessatron, omega_chessatron]

##################### CHESS

class Chess_Emote(Emote):
    def __init__(self, name, text, isWhite, alternate_names=[]):
        self.text = text
        self.name = name
        if isWhite:
            self.value = 80
        else:
            self.value = 40
        self.attributes = ["chess_pieces"]
        self.awards_value = False
        self.alchemy_value = self.value
        self.alternate_names = alternate_names

# white_pawn = { "text" : "<:Wpawn:961815364319207516>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_pawn = Chess_Emote(
    name="Wpawn",
    text = "<:Wpawn:961815364319207516>",
    isWhite=True 
)

# white_rook = { "text" : "<:Wrook:961815364482793492>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_rook = Chess_Emote(
    name="Wrook",
    text = "<:Wrook:961815364482793492>",
    isWhite=True 
)

# white_bishop = { "text" : "<:Wbishop:961815364428263435>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_bishop = Chess_Emote(
    name="Wbishop",
    text = "<:Wbishop:961815364428263435>",
    isWhite=True 
)

# white_knight = { "text" : "<:Wknight:958746544436310057>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_knight = Chess_Emote(
    name="Wknight",
    text = "<:Wknight:958746544436310057>",
    isWhite=True 
)

# white_queen = { "text" : "<:Wqueen:961815364461809774>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_queen = Chess_Emote(
    name="Wqueen",
    text = "<:Wqueen:961815364461809774>",
    isWhite=True 
)

# white_king = { "text" : "<:Wking:961815364411478016>",
#     "value" : 80,
#     "attribute" : "chess_pieces" 
# }
white_king = Chess_Emote(
    name="Wking",
    text = "<:Wking:961815364411478016>",
    isWhite=True 
)


# black_pawn = { "text" : "<:Bpawn:961815364436635718>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_pawn = Chess_Emote(
    name="Bpawn",
    text = "<:Bpawn:961815364436635718>",
    isWhite=False 
)

# black_rook = { "text" : "<:Brook:961815364377919518>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_rook = Chess_Emote(
    name="Brook",
    text = "<:Brook:961815364377919518>",
    isWhite=False 
)

# black_bishop = { "text" : "<:Bbishop:961815364306608228>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_bishop = Chess_Emote(
    name="Bbishop",
    text = "<:Bbishop:961815364306608228>",
    isWhite=False 
)

# black_knight = { "text" : "<:Bknight:961815364424048650>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_knight = Chess_Emote(
    name="Bknight",
    text =  "<:Bknight:961815364424048650>",
    isWhite=False 
)

# black_queen = { "text" : "<:Bqueen:961815364470202428>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_queen = Chess_Emote(
    name="Bqueen",
    text =  "<:Bqueen:961815364470202428>",
    isWhite=False 
)

# black_king = { "text" : "<:Bking:961815364327600178>",
#     "value" : 40,
#     "attribute" : "chess_pieces" 
# }
black_king = Chess_Emote(
    name="Bking",
    text =  "<:Bking:961815364327600178>",
    isWhite=False 
)

all_chess_pieces = [black_king, black_queen, black_knight, black_bishop, black_rook, black_pawn, white_pawn, white_rook, white_bishop, white_knight, white_queen, white_king]
chess_pieces_black_biased = [black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,black_pawn,
                             black_rook, black_rook,
                             black_bishop, black_bishop,
                             black_knight, black_knight,
                             black_queen, 
                             black_king]
chess_pieces_white_biased = [white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,white_pawn,
                             white_rook, white_rook,
                             white_bishop, white_bishop,
                             white_knight, white_knight,
                             white_queen,
                             white_king]

##################### CHESS END

##################### SHINIES

class Shiny_Emote(Emote):
    def __init__(self, name, text, value, awards_value=False, alchemy_value=None, alternate_names=[]):
        self.text = text
        self.name = name
        self.attributes = ["shiny"]
        self.value = value
        self.awards_value = awards_value
        if alchemy_value is None:
            self.alchemy_value = value
        else:
            self.alchemy_value = alchemy_value
        self.alternate_names = alternate_names
        

# <:gem_red:1006498544892526612> <:gem_blue:1006498655508889671> <:gem_gold:1006498746718244944> <:gem_green:1006498803295211520> <:gem_purple:1006498607861604392>

gem_red = Shiny_Emote(
    name="gem_red",
    text = "<:gem_red:1006498544892526612>",
    value = 150,
    alternate_names = ["red_gem"]
)

gem_blue = Shiny_Emote(
    name="gem_blue",
    text = "<:gem_blue:1006498655508889671>",
    value = 250,
    alternate_names = ["blue_gem"]
)

gem_purple = Shiny_Emote(
    name="gem_purple",
    text = "<:gem_purple:1006498607861604392>",
    value = 500,
    alternate_names = ["purple_gem"]
)

gem_gold = Shiny_Emote(
    name="gem_gold",
    text = "<:gem_gold:1006498746718244944>",
    value = 5000,
    awards_value = True,
    alternate_names = ["gold_gem"]
)

gem_green = Shiny_Emote(
    name="gem_green",
    text = "<:gem_green:1006498803295211520>",
    value = 750,
    alternate_names = ["green_gem"]
)

all_shinies = [gem_red, gem_blue, gem_purple, gem_gold, gem_green]


                            
##################### MISC BREADS

# subset: stonks
pretzel = Emote(
    text=":pretzel:",
    name="pretzel",
    emoji="🥨",
    attributes=["misc_bread", "stonks"]
)

fortune_cookie = Emote(
    text=":fortune_cookie:",
    name="fortune_cookie",
    emoji="🥠",
    attributes=["misc_bread", "stonks"],
    alternate_names=["fortune"]
)

cookie = Emote(
    text=":cookie:",
    name="cookie",
    emoji="🍪",
    attributes=["misc_bread", "stonks"]
)

# rest of the misc breads
birthday = Emote(
    text=":birthday:",
    name="birthday",
    emoji="🎂",
    attributes=["misc_bread"]
)

cake = Emote(
    text=":cake:",
    name="cake",
    emoji="🍰",
    attributes=["misc_bread"]
)

pancakes = Emote(
    text=":pancakes:",
    name="pancakes",
    emoji="🥞",
    attributes=["misc_bread"]
)

hamburger = Emote(
    text=":hamburger:",
    name="hamburger",
    emoji="🍔",
    attributes=["misc_bread"]
)

pizza = Emote(
    text=":pizza:",
    name="pizza",
    emoji="🍕",
    attributes=["misc_bread"]
)

dumpling = Emote(
    text=":dumpling:",
    name="dumpling",
    emoji="🥟",
    attributes=["misc_bread"]
)



pie = Emote(
    text=":pie:",
    name="pie",
    emoji="🥧",
    attributes=["misc_bread"]
)

hotdog = Emote(
    text=":hotdog:",
    name="hotdog",
    emoji="🌭",
    attributes=["misc_bread"]
)

taco = Emote(
    text=":taco:",
    name="taco",
    emoji="🌮",
    attributes=["misc_bread"]
)

burrito = Emote(
    text=":burrito:",
    name="burrito",
    emoji="🌯",
    attributes=["misc_bread"]
)

cupcake = Emote(
    text=":cupcake:",
    name="cupcake",
    emoji="🧁",
    attributes=["misc_bread"]
)



misc_bread_emotes = [pretzel, birthday, cake, pancakes, hamburger, pizza, dumpling, fortune_cookie, pie, hotdog, taco, burrito, cupcake, cookie]

##################### SHADOW

shadow_gem_gold = Emote(
    text="<:shadow_gem_gold:1025975043907399711>",
    name="shadow_gem_gold",
    attributes=["shadow"],
    giftable = False
)

shadow_moak = Emote(
    text="<:shadow_moak:1025974976093884537>",
    name="shadow_moak",
    attributes=["shadow"],
    giftable = False
)

shadowmega_chessatron = Emote(
    text="<:shadowmega_chessatron:1025974897639432262>",
    name="shadowmega_chessatron",
    attributes=["shadow"],
    giftable = False
)

shadow_emotes = [shadow_gem_gold, shadow_moak, shadowmega_chessatron]

##################### MISC

middle_finger = Emote(
    text=":middle_finger:",
    name="middle_finger",
    emoji="🖕",
    attributes=["misc"]
)

cherry = Emote(
    text=":cherries:",
    name="cherries",
    emoji="🍒",
    attributes=["misc"]
)

lemon = Emote(
    text=":lemon:",
    name="lemon",
    emoji="🍋",
    attributes=["misc"]
)

grapes = Emote(
    text=":grapes:",
    name="grapes",
    emoji="🍇",
    attributes=["misc"]
)

brick = Emote(
    text=":bricks:",
    name="brick",
    emoji="🧱",
    attributes=["misc"]
)

brick_gold = Emote(
    text="<:brick_gold:971239215968944168>",
    name="brick_gold",
    attributes = ["misc"]
)

fide_brick = Emote( # hires one
    text = "<:fide_brick:961811237296037957>",
    name = "fide_brick",
    attributes = ["misc"]
)

brick_fide = Emote( # this is the pixel one
    text = "<:brick_fide:961517570396135494>",
    name = "brick_fide",
    attributes = ["misc"]
)

bcapy = Emote(
    text = "<:Bcapy:1003061938684711092>",
    name = "bcapy",
    attributes = ["misc"]
)

wcapy = Emote(
    text = "<:Wcapy:1003061948964946010>",
    name = "wcapy",
    attributes = ["misc"]
)

rigged = Emote(
    text = "<:RIGGED1:1016075464525234347>", # was"<:RIGGED:1016075464525234347>",
    name = "rigged1",
    attributes = ["misc"]
)

ascension_token = Emote(
    text = "<:ascension_token:1023695148380602430>" ,
    name = "ascension_token",
    attributes = ["misc"],
    giftable = False
)

all_bricks = [brick, brick_gold, fide_brick, brick_fide]
all_bricks_weighted = [brick] * 10 + [brick_gold] * 1 + [fide_brick] * 5 + [brick_fide] * 5
misc_emotes = [ascension_token, middle_finger, cherry, brick, brick_gold, fide_brick, brick_fide, lemon, grapes, rigged, bcapy, wcapy]

##################### CODE

all_emotes = [normal_bread, 
    flatbread, stuffed_flatbread, french_bread, croissant, sandwich, 
    doughnut, bagel, waffle, 
    lottery_win,
    ] + all_chess_pieces + misc_emotes + misc_bread_emotes + all_uniques + all_shinies + shadow_emotes

def get_emote(text: str) -> typing.Optional[Emote]:
    # return None

    text = text.lower()
    for emote in all_emotes:
        if (emote.emoji is not None) and (emote.emoji == text):
            return emote
        if text == emote.text.lower():
            return emote
        if text == emote.name.lower():
            return emote
        for alternate_name in emote.alternate_names:
            if text == alternate_name.lower():
                return emote
    # now we check for the last character being an s
    if text[-1] == "s":
        text_minus_last_char = text[:-1]
        for emote in all_emotes:
            if (emote.emoji is not None) and (emote.emoji == text_minus_last_char):
                return emote
            if text_minus_last_char == emote.text.lower():
                return emote
            if text_minus_last_char == emote.name.lower():
                return emote
            for alternate_name in emote.alternate_names:
                if text_minus_last_char == alternate_name.lower():
                    return emote
    return None


def get_emote_text(text: str):
    emote = get_emote(text)
    if emote is not None:
        return emote.text
    else:
        return None

def extract_emote_from_text(text: str) -> typing.Optional[Emote]:
    text = text.lower()
    for emote in all_emotes:
        if (emote.emoji is not None):
            if emote.emoji in text:
                return emote
        if emote.text.lower() in text:
            return emote
        if emote.name.lower() in text:
            return emote
        for alternate_name in emote.alternate_names:
            if alternate_name.lower() in text:
                return emote
    return None

########################################################################################

all_breads = [":bread:",
                ":french_bread:",
                ":croissant:",
                ":flatbread:",
                ":sandwich:",
                ":stuffed_flatbread:"]

rare_breads = [":doughnut:",
                ":bagel:",
                ":waffle:"]

emoji_conversions = {  "🍞" : ":bread:",
                       "🥖" : ":french_bread:",
                       "🥐" : ":croissant:",
                       "🫓" : ":flatbread:",
                       "🥪" : ":sandwich:",
                       "🥙" : ":stuffed_flatbread:",
                       "🍩" : ":doughnut:",
                       "🥯" : ":bagel:" }