import random
import math
import typing
import discord
import hashlib
import copy
import datetime
from discord.ext import commands

def smart_number(number: int) -> str:
    """Adds commas to the given number, and returns the output."""
    shrink_large_numbers = False
    if shrink_large_numbers is False:
        return f"{number:,}"
    else:
        marker = ""
        fraction = 0
        if number > 1000000000000:
            marker = "T"
            fraction = number / 1000000000000
        elif number > 1000000000:
            marker = "B"
            fraction = number / 1000000000
        elif number > 1000000:
            marker = "M"
            fraction = number / 1000000
        elif number > 10000:
            marker = "K"
            fraction = number / 1000
        else:
            return f"{number:,}"
        
        if fraction > 100:
            return f"{int(fraction):,} {marker}"
        elif fraction > 10:
            return f"{fraction:.1f} {marker}"
        else:
            return f"{fraction:.2f} {marker}"


def write_number_of_times(number: int) -> str:
    """Returns the number of times something has occurred corresponding to the given number. So if 3 is passed it'll return '3 times', but if 1 is passed it will return 'once'."""
    if type(number) is str:
        number = int(number)
    if number == 0:
        return "zero times"
    elif number == 1:
        return "once"
    elif number == 2:
        return "twice"
    else:
        return smart_number(number) + " times"

def write_count(
        number: int,
        word: str,
        delimiter: str = ""
    ) -> str:
    """Writes the count of a number and word, and will pluralize the word if the number is not 1."""
    if number == 1:
        pass
    else:
        word =  word + delimiter + "s"
    output = smart_number(number) + " " + word
    return output

def array_subtract(
        array1: list,
        array2: list
    ) -> list:
    """Subtracts one list from another by returning all the items in array1 that are not in array2."""
    #return [x for x in array1 if x not in array2]
    output = list()
    output.extend(array1)
    #print(f"Array subtract: subtracting {array2} from {array1}")
    #print(f"output: {output}")
    for obj in array2:
    #for i in range(len(array2)):
        
        #object = array2[i]
        #print(f"Object {i} is {object}")
        if obj in output:
            #print(f"Object {i} is in output")
            output.remove(obj)
            #print(f"Removing. Output is now {output}")
            #this is subtly different, but it means that duplicate members are only removed one at a time
    return output

def dict_subtract(
        dict1: dict,
        dict2: dict
    ) -> dict:
    """Subtracts one dictionary from another by returning a dict containing all the keys and values of dict1, subtraced by the same keys in dict2.
    Via this subtraction, if a value goes less than or equal to 0 it will be removed."""
    output = dict()
    output.update(dict1)
    for key in dict2:
        if key in output:
            output[key] -= dict2[key]
            if output[key] <= 0:
                del output[key]
    return output


def increment(
        dictionary: dict,
        key: str,
        amount: int = 1
    ) -> dict:
    """Increments a key in a dictionary by the given amount."""
    if key in dictionary:
        dictionary[key] += amount
    else:
        dictionary[key] = amount
    return dictionary

# returns a random number between 0 and 1, biased towards the edges
def rand_sigmoid(x: typing.Optional[int] = None) -> float:
    """Returns a random number between 0 and 1, but biased towards the edges."""
    if x is None:
        x = random.uniform(-1, 1)
    else:
        x = x * 2 - 1
    sigmoid =  1 / (1 + math.exp(-x*6))
    linear = (.5 + x/2)

    if sigmoid < 0:
        sigmoid = 0
    elif sigmoid > 1:
        sigmoid = 1

    sig_blend = .5

    output =  (sigmoid * sig_blend) + (linear * (1 - sig_blend))

    return output

#returns a random number between 0 and 1, biased towards the middle
def rand_logit(x: typing.Optional[int] = None) -> float:
    """Returns a random number between 0 and 1, but biased towards the middle."""
    if x is None:
        x = random.uniform(0, 1)
    
    if x == 0:
        return 0
    elif x == 1:
        return 1
    
    logit =  math.log(x / (1 - x)) / 6
    linear = x*2 - 1

    if logit < -1:
        logit = -1
    elif logit > 1:
        logit = 1

    logit_blend = .3

    output =  (logit * logit_blend) + (linear * (1 - logit_blend))

    return remap(output, -1, 1, 0, 1)

def remap(
        x: typing.Union[int, float],
        in_min: typing.Union[int, float],
        in_max: typing.Union[int, float],
        out_min: typing.Union[int, float],
        out_max: typing.Union[int, float]
    ) -> float:
  """Remaps a number between a min and max to a different min and max."""
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def normalize_array_to_ints(
        array: list,
        target_total: int = 1000
    ) -> list[int]:
    """Normalizes a list to shift the total value to the target total."""
    total = sum(array)
    if total == 0:
        return array
    new_array = [x / total for x in array]
    for x in range(len(new_array)):
        new_array[x] = round(new_array[x] * target_total)
    return new_array


def contains_ping(string: str) -> bool:
    """Returns a boolean for whether a given string contains a ping."""
    if "<@" in string:
        return True
    elif "@everyone" in string:
        return True
    elif "@here" in string:
        return True
    else:
        return False

def sanitize_ping(string: str) -> str:
    """Returns the input string but with invisible characters (U+200B) placed to avoid pings."""
    output = string.replace("@everyone", "@\u200beveryone")
    output = output.replace("@here", "@\u200bhere")
    output = output.replace("<@", "<@\u200b")
    return output

# this will first try a regular reply, and if that fails, it will send it as a plain message with a mention
async def smart_reply(
        ctx: typing.Union[commands.Context, discord.Message],
        message: str,
        ping_reply: bool = True
    ) -> typing.Optional[discord.Message]:
    """Attempts to reply nromally, then if that fails tries to send it as a plain message with a ping.
    
    Will abide by the ping reply parameter."""
    if message == "" or message is None:
        return None
        
    # Try except block to catch errors 
    try:
        message = await ctx.reply(message, mention_author=ping_reply)
    except discord.HTTPException:
        # Sending the message has failed, so the message we're trying to reply to has likely been deleted.
        if ping_reply:
            # Ping reply is on, so send the message normally but with a ping at the start.
            message = await ctx.send(f"{ctx.author.mention}\n\n{message}")
        else:
            # Ping reply is off, so send the message and put the author's display name at the top, so they know it's theirs.
            message = await ctx.send(f"{sanitize_ping(ctx.author.display_name)}:\n\n{message}")
    except:
        # Some other exception has occurred, so reraise it.
        raise
        
    return message

def plot_line(
        start: tuple[int, int],
        end: tuple[int, int]
    ) -> list[tuple[int, int]]:
    """Plots a line between two points. Returns a list of points that make the line, in order."""
    points = []

    x1, y1 = start
    x2, y2 = end

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    error = dx - dy
    x, y = x1, y1

    while True:
        points.append((x, y))

        if x == x2 and y == y2:
            break

        e2 = 2 * error
        if e2 > -dy:
            error -= dy
            x += sx
        if e2 < dx:
            error += dx
            y += sy

    return points

def hash_args(*args, separator: str = "") -> str:
    """Converts a list of args into a string, and then returns the SHA-256 hash of it."""
    return hashlib.sha256(separator.join([str(arg) for arg in args]).encode()).digest()

def get_display_name(member: discord.Member) -> str:
    """Gets the display name of a discord.Member object."""
    return (member.global_name if (member.global_name is not None and member.name == member.display_name) else member.display_name)

def dynamic_circle(radius: int) -> int:
    """Generates a circle bitboard."""
    covered = 1 << (radius + radius * 256)
    
    for angle in range(360):
        for distance in range(1, radius + 1):
            point_x = int(distance * math.cos(math.radians(angle)) + radius + 0.5)
            point_y = int(distance * math.sin(math.radians(angle)) + radius + 0.5)
            
            covered |= 1 << (point_x + 256 * point_y)
    
    return covered
    
def iterate_through_bits(num: int) -> typing.Iterator[int]:
    """Gives an iterator that iterates through the bit locations in an integer.
    
    >>> list(iterate_through_bits(13))
    [0, 2, 3]"""
    while num:
        r = num & -num
        yield r.bit_length() - 1
        num ^= r

def gen_embed(
        title: str, title_link: str = None,
        color: str | tuple[int, int, int] = "#8790ff", # 8884479
        description: str = None,
        author_name: str = None, author_link: str = None, author_icon: str = None,
        footer_text: str = None, footer_icon: str = None,
        image_link: str = None,
        thumbnail_link: str = None,
        fields: list[tuple[str, str, bool]] = None,
        timestamp: datetime.datetime = None
    ) -> discord.Embed:
    """Function for easy creation of embeds. The color can be provided as a hex code (with or without the hash symbol) or as RGB values.
    # Fields:
    Each field is a 3 item tuple as follows:
    1. Field name (256 characters)
    2. Field text (1024 characters)
    3. Whether the field should be inline (bool)
    The fields should be provided in the order you want to display them.
    # For adding images:
    https://discordpy.readthedocs.io/en/stable/faq.html#local-image"""

    if isinstance(color, str):
        color = int(color.replace("#", ""), 16)
    elif isinstance(color, tuple):
        color = int(f"{color[0]:02x}{color[1]:02x}{color[2]:02x}", 16)
    else:
        raise TypeError("Provided color must be a hex code or set of RBG values in a tuple.")
    
    embed = discord.Embed(
        color = color,
        title = title,
        url = title_link,
        description = description,
        timestamp = timestamp
    )

    if author_name is not None:
        embed.set_author(
            name = author_name,
            url = author_link,
            icon_url = author_icon
        )
    
    if footer_text is not None:
        embed.set_footer(
            text = footer_text,
            icon_url = footer_icon
        )
    
    if image_link is not None:
        embed.set_image(
            url = image_link
        )
    
    if thumbnail_link is not None:
        embed.set_thumbnail(
            url = thumbnail_link
        )
    
    if fields is not None:
        for field_title, field_text, field_inline in fields:
            embed.add_field(
                name = field_title,
                value = field_text,
                inline = field_inline
            )
    
    return embed

def name_amount(amount: int) -> str:
    """Takes in a number and generates a stat name for that many breads in a roll."""
    if amount > 99:
        return f"{amount}_breads"
    
    single = ["", "_one", "_two", "_three", "_four", "_five", "_six", "_seven", "_eight", "_nine"]
    ten = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    return f"{ten[amount // 10]}{single[amount % 10]}_breads"

#################################################################################################################
#################################################################################################################
#################################################################################################################

everyone_prevention = discord.AllowedMentions(everyone=False, roles=False)

class CustomContext(commands.Context):    
    async def safe_reply(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message:        
        kwargs["allowed_mentions"] = everyone_prevention

        return await super().reply(content, **kwargs)
    
    async def send(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message:
        kwargs["allowed_mentions"] = everyone_prevention

        return await super().send(content, **kwargs)
    
    async def reply(
            self: typing.Self,
            content: str = "",
            **kwargs
        ) -> discord.Message | None:
        if (content is None or len(str(content)) == 0) and kwargs.get("embed", None) is None and kwargs.get("file", None) is None:
            return None
        
        try:
            ping_data = self.bot.json_cog.get_filing_cabinet("ping_settings", guild=self.guild, create_if_nonexistent=True)
            
            if str(self.author.id) in ping_data:
                kwargs["mention_author"] = ping_data.get(str(self.author.id), True)
        except: # oh well
            pass
        
        try:
            return await self.safe_reply(content, **copy.deepcopy(kwargs))
        except discord.HTTPException:
            # If something went wrong replying.
            if kwargs.get("mention_author", True):
                return await self.send(f"{self.author.mention},\n\n{content}", **kwargs)
            else:
                return await self.send(f"{sanitize_ping(self.author.display_name)},\n\n{content}", **kwargs)
    
    async def send_help(
            self: typing.Self,
            *args: typing.Any
        ) -> typing.Any:
        """Slightly modified version of base Context send_help to pass ctx to the send_group_help method."""
        bot = self.bot
        cmd = bot.help_command

        if cmd is None:
            return None

        cmd = cmd.copy()
        cmd.context = self

        if len(args) == 0:
            await cmd.prepare_help_command(self, None)
            mapping = cmd.get_bot_mapping()
            injected = commands.core.wrap_callback(cmd.send_bot_help)
            try:
                return await injected(mapping)
            except commands.errors.CommandError as e:
                await cmd.on_help_command_error(self, e)
                return None

        entity = args[0]
        if isinstance(entity, str):
            entity = bot.get_cog(entity) or bot.get_command(entity)

        if entity is None:
            return None

        try:
            entity.qualified_name
        except AttributeError:
            # if we're here then it's not a cog, group, or command.
            return None

        await cmd.prepare_help_command(self, entity.qualified_name)

        try:
            if commands.context.is_cog(entity):
                injected = commands.core.wrap_callback(cmd.send_cog_help)
                return await injected(entity)
            elif isinstance(entity, commands.Group):
                injected = commands.core.wrap_callback(cmd.send_group_help)
                return await injected(entity, self)
            elif isinstance(entity, commands.Command):
                injected = commands.core.wrap_callback(cmd.send_command_help)
                return await injected(entity)
            else:
                return None
        except commands.errors.CommandError as e:
            await cmd.on_help_command_error(self, e)

class CustomBot(commands.Bot):
    # THIS CAN ONLY BE RELOADED BY RESTARTING THE ENTIRE BOT.
    
    async def get_context(
            self: typing.Self,
            message: discord.Message,
            *,
            cls=CustomContext):
        return await super().get_context(message, cls=cls)

class CustomHelpCommand(commands.DefaultHelpCommand):
    # THIS CAN ONLY BE RELOADED BY RESTARTING THE ENTIRE BOT.

    def get_ending_note(self: typing.Self) -> str:
        command_name = self.invoked_with

        return f'Type `{self.context.clean_prefix}{command_name} <command>` for more info on a command.\nYou can also type `{self.context.clean_prefix}{command_name} <category>` for more info on a category.'

    def get_opening_note(self: typing.Self) -> str:
        return self.get_ending_note()

    async def command_not_found(
            self: typing.Self,
            string: str
        ) -> None:
        embed_send = gen_embed(
            title = "Machine-Mind help",
            description = f"Command `{string}` not found."
        )
        return await self.context.reply(embed=embed_send)
    
    async def subcommand_not_found(
            self: typing.Self,
            command: commands.Command,
            string: str
        ) -> None:
        embed_send = gen_embed(
            title = "Machine-Mind help",
            description = f"Command `{command.qualified_name}` has no subcommand called `{string}`."
        )
        return await self.context.reply(embed=embed_send)

    async def send_cog_help(
            self: typing.Self,
            cog: commands.Cog | CustomBot
        ) -> None:
            
        command_lines = []
        all_commands = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)

        for command in all_commands:
            try:

                command_description = command.brief

                if command_description is None:
                    command_description = command.help
                    if command_description is None:
                        command_description = ""

                if len(command_description) > 120:
                    command_description = f"{command_description[:120]}..."
                
                command_lines.append(f"- `{command.name}` -- {command_description}")
            except commands.CommandError:
                continue
        
        if len(command_lines) == 0:
            command_lines.append("*Nothing to list.*")
        
        embed = gen_embed(
            title = "Machine-Mind help",
            description = "{}\n\n**Commands:**\n{}\n\n{}".format(
                cog.description,
                "\n".join(command_lines),
                self.get_opening_note()
            )
        )
        await self.context.reply(embed=embed)
    
    async def send_bot_help(self: typing.Self) -> None:
        all_commands = await self.filter_commands(self.context.bot.commands, sort=self.sort_commands)
        all_commands = [(c.name, c) for c in all_commands]
        all_commands: dict[str, commands.Command] = dict(sorted(all_commands, key=lambda c: c[0]))

        command_data = {}
        listed = []
        for name, command in all_commands.items():
            try:
                if len(command.parents) != 0:
                    continue

                if command in listed:
                    continue

                listed.append(command)

                if command.cog not in command_data:
                    command_data[command.cog] = []

                brief = command.short_doc
                
                if len(brief) > 120:
                    brief = f"{brief[120]}..."

                command_data[command.cog].append(f"- `{name}` -- {brief}")

            except commands.CommandError:
                continue
        
        command_data = dict(sorted(command_data.items(), key=lambda c: "No Category" if c[0] is None else c[0].qualified_name))

        lines = []

        if self.context.bot.description is not None:
            lines.append(f"{self.context.bot.description}\n")
        
        for cog, command_list in command_data.items():
            if cog is None:
                lines.append(f"**No Category:**")
            else:
                lines.append(f"**{cog.qualified_name}:**")
            for cmd in command_list:
                lines.append(cmd)
        
        lines.append("")
        lines.append(self.get_ending_note())
        
        embed = gen_embed(
            title = "Machine-Mind help",
            description = "\n".join(lines)
        )
        await self.context.reply(embed=embed)

    async def send_command_help(
            self: typing.Self,
            command: commands.Command
        ) -> None:
        command_lines = []

        breadcrumbs = []
        for parent in reversed(command.parents):
            breadcrumbs.append(parent.name)
        
        if len(breadcrumbs) != 0:
            breadcrumbs.append(command.name)

            command_lines.append("*{}*".format(" -> ".join(breadcrumbs)))

        ####

        command_name = f"{command.full_parent_name} {command.name}".strip()
        command_lines.append(f"## **{self.context.clean_prefix}{command_name}**")
        command_lines.append(command.description)
        command_lines.append("")

        usage = f"{self.context.clean_prefix}{command_name} {command.signature}".strip()
        command_lines.append(f"Syntax: `{usage}`")
        if len(command.aliases) > 0:
            command_lines.append("Aliases: {}".format(', '.join([f"`{a}`" for a in command.aliases])))

        
        arguments = command.clean_params.values()
        if len(arguments) > 0:
            command_lines.append("\n**Arguments:**")
            for argument in arguments:
                name = argument.displayed_name or argument.name
                description = argument.description or self.default_argument_description
                command_lines.append(f"- `{name}`-- {description}")

        ####
        
        command_lines.append("")
        command_lines.append(self.get_ending_note())
        
        embed = gen_embed(
            title = "Machine-Mind help",
            description = "\n".join(command_lines)
        )
        await self.context.reply(embed=embed)
        
    async def send_group_help(
            self: typing.Self,
            command: commands.Group,
            ctx: commands.Context | CustomContext
        ) -> None:
        command_lines = []

        breadcrumbs = []
        for parent in reversed(command.parents):
            breadcrumbs.append(parent.name)
        
        if len(breadcrumbs) != 0:
            breadcrumbs.append(command.name)

            command_lines.append("*{}*".format(" -> ".join(breadcrumbs)))

        ####

        command_name = f"{command.full_parent_name} {command.name}".strip()
        command_lines.append(f"## **{self.context.clean_prefix}{command_name}**")
        command_lines.append(command.description)
        command_lines.append("")

        usage = f"{self.context.clean_prefix}{command_name} {command.signature}".strip()
        command_lines.append(f"Syntax: `{usage}`")
        if len(command.aliases) > 0:
            command_lines.append("Aliases: {}".format(', '.join([f"`{a}`" for a in command.aliases])))

        
        arguments = command.clean_params.values()
        if len(arguments) > 0:
            command_lines.append("\n**Arguments:**")
            for argument in arguments:
                name = argument.displayed_name or argument.name
                description = argument.description or self.default_argument_description
                command_lines.append(f"- `{name}` -- {description}")

        subcommands = command.commands
        if len(subcommands) > 0:
            command_lines.append("\n**Subcommands:**")

            # Probably a bad way of doing this, but it does prevent the toggle
            # check from sending a message if a subcommand here is disabled.
            old_invoked = ctx.invoked_with
            ctx.invoked_with = "help"
            
            for subcommand in sorted(subcommands, key=lambda c: c.name):
                try:
                    if not await subcommand.can_run(ctx):
                        continue
                except commands.CommandError:
                    continue

                name = subcommand.name
                description = subcommand.short_doc
                command_lines.append(f"- `{name}` -- {description}")

            ctx.invoked_with = old_invoked
        ####
        
        command_lines.append("")
        command_lines.append(self.get_ending_note())
        
        embed = gen_embed(
            title = "Machine-Mind help",
            description = "\n".join(command_lines)
        )
        await self.context.reply(embed=embed)

    async def command_callback(
            self: typing.Self,
            ctx: commands.Context | CustomContext,
            /, *,
            command: typing.Optional[str] = None
        ) -> None:

        bot = ctx.bot

        if command is None:
            return await self.send_bot_help()

        # Check if it's a cog
        cog = bot.get_cog(command)
        if cog is not None:
            return await self.send_cog_help(cog)

        keys = command.split(' ')
        cmd = bot.all_commands.get(keys[0])
        if cmd is None:
            return await self.command_not_found(keys[0])
            

        for key in keys[1:]:
            try:
                found = cmd.all_commands.get(key)  # type: ignore
            except AttributeError:
                return await self.subcommand_not_found(cmd, self.remove_mentions(key))
            else:
                if found is None:
                    return await self.subcommand_not_found(cmd, self.remove_mentions(key))
                cmd = found

        if isinstance(cmd, commands.Group):
            return await self.send_group_help(cmd, ctx)
        else:
            return await self.send_command_help(cmd)
    
    async def on_help_command_error(
            self: typing.Self,
            ctx: commands.Context | CustomContext,
            error: Exception, /
        ) -> None:
        raise error