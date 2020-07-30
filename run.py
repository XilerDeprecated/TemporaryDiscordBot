#   ©Xiler - Arthurdw
#   Xiler is under a CC0-1.0 License (View the license here: https://legal.xiler.net/license)
#   By proceeding to this site you agree with our ToS. (View the tos here: https://legal.xiler.net/tos)

from configparser import ConfigParser
from datetime import datetime
from os import name, system

import discord
from BeatPy.discord import formatter
from discord.ext import commands

# Windows and Linux compatibility
clear, back_slash = "clear", "/"
if name == "nt":
    clear, back_slash = "cls", "\\"

# Reading our config.cfg file
cfg = ConfigParser()
cfg.read("config.cfg")

# Setup BeatPy
setup = formatter.Embed(footer=True, footer_message=f"©Xiler | {datetime.now().year}")
em = setup.create


# Our general logger:
class Logger:
    def __init__(self):
        self.bold = "\033[1m"
        self.normal = "\033[8m"
        self.default = "\033[39m"
        self.green = "\033[92m"
        self.yellow = "\033[93m"
        self.cyan = "\033[96m"
        self.red = "\033[91m"
        self.magenta = "\033[95m"
        self.blue = "\033[94m"

    def generate_timestamp(self) -> str:
        """Generates a usable timestamp for the logger."""
        return f"[{self.green + datetime.now().strftime('%H:%M:%S %d/%m/%y') + self.default}]"

    def log(self, message: str) -> None:
        """Sends a popper formatted log message"""
        print(f"{self.generate_timestamp()} {message}")

    def warn(self, message: str) -> None:
        """Logs a popper formatted warning/important message"""
        print(f"[{self.magenta + self.bold}WARN{self.default + self.normal}]{self.generate_timestamp()} "
              f"{self.magenta + message + self.default}")

    def error(self, message: str) -> None:
        """Logs a popper formatted error message"""
        print(f"[{self.red + self.bold}ERROR{self.default + self.normal}]{self.generate_timestamp()} "
              f"{self.red + message + self.default}")

    def command_executed(self, ctx: commands.Context) -> None:
        """Logs it when a command got executed!"""
        self.log(f"{self.bold + self.cyan + ctx.command.name + self.normal + self.default} "
                 f"got executed by {self.yellow + ctx.author.name}#{ctx.author.discriminator + self.default} "
                 f"({self.blue + str(ctx.author.id) + self.default})")

    def guild_join_leave(self, member: discord.Member, join: bool = False) -> None:
        """Logs it when a member leaves or joins."""
        self.log(f"{self.yellow + member.name}#{member.discriminator + self.default} "
                 f"({self.blue + str(member.id) + self.default}) "
                 f"{self.bold + self.cyan + ('joined' if join else 'left') + self.normal + self.default} "
                 f"the Xiler discord!")


# Generate our usable logger object:
logger = Logger()


# Handles all events:
class EventListener(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.roles = [699699284022526024, 699698377046229072]  # Early bird, Member

    # Fetch our role objects
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(696758091768791080)
        self.roles = map(lambda _id: guild.get_role(_id), self.roles)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 696758091768791080:  # Because this script is temporary we'll only allow this in our guild
            await member.add_roles(*self.roles, reason="Welcoming roles!")
            logger.guild_join_leave(member, True)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id == 696758091768791080:  # Because this script is temporary we'll only allow this in our guild
            logger.guild_join_leave(member)


# The class for all other commands:
class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = 696758091768791080
        self.suggestions = 703192340998651909  # 703192340998651909
        # self.cogs = self.bot.cogs

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.guild)
        self.suggestions = self.guild.get_channel(self.suggestions)

    @commands.command(name="reload", aliases=["rl"])
    @commands.has_role(699699122432639117)
    async def reload(self, ctx):
        msg = await ctx.send("Started reloading")
        for cog in self.bot.cogs:
            self.bot.remove_cog(cog.__name__)
            self.bot.add_cog(cog(self.bot))
        await msg.delete()
        await ctx.send(f"~~{msg.content}~~\nFinished!")

    @commands.command(name="suggest", aliases=["sug"])
    async def suggest(self, ctx, *, suggestion: str):
        if ctx.guild == self.guild:
            if isinstance(self.suggestions, int):
                await self.on_ready()
            msg = await self.suggestions.send(**em(suggestion,
                                                   footer_message=f"Submitted by {ctx.author} ({ctx.author.id})",
                                                   footer_icon=ctx.author.avatar_url))
            for emoji in ["👍", "😐", "👎"]:
                await msg.add_reaction(emoji)
            await ctx.send(
                **em(f"Successfully send your suggestion in {self.suggestions.mention}!\n``` {suggestion} ```",
                     color=0xff0016, timestamp=False))


# Setting up our bot object:
class TempBot(commands.Bot):
    cogs = [EventListener, GeneralCommands]

    def __init__(self):
        system(clear)
        logger.warn("Initializing system...")
        super().__init__(command_prefix=commands.when_mentioned_or(cfg["GENERAL"].get("prefix")),
                         description="The temporary bot for Xiler",
                         case_insensitive=True,
                         help_attrs=dict(hidden=True))

        # Add the COG's
        print("\n")
        for cog in self.cogs:
            logger.log(
                f"{logger.cyan}Started{logger.default} loading {logger.yellow + cog.__name__ + logger.default}...")
            self.add_cog(cog(self))
            logger.log(
                f"{logger.cyan}Successfully{logger.default} loaded {logger.yellow + cog.__name__ + logger.default}!")
        print("\n")

    # Start the bot
    def run(self):
        super().run(cfg["GENERAL"].get("token"), reconnect=True)

    # Our introduction message
    async def on_ready(self):
        logger.log(f"Successfully initialized on {self.user.name}!")
        print(f"\n\n{logger.red + logger.bold}LEGAL NOTICE:\n"
              f"This bot is official property of Xiler (https://www.xiler.net) and any of its ToS or Privacy policies "
              f"apply to this application!{logger.default + logger.normal}\n\n")

    # Handle messages properly (prevent bot response, log, process)
    async def on_message(self, message):
        if message.author.bot:
            return
        ctx = await self.get_context(message)
        if ctx.valid:
            logger.command_executed(ctx)
        await self.process_commands(message)

    # Prevent unknown exception errors
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, (commands.errors.CommandNotFound,)):
            return
        else:
            message = f"{type(exception).__name__}: {exception}".capitalize()
            logger.error(message)
            await ctx.send(**em(message, title="Oops...", color=0x0000ff))


if __name__ == "__main__":
    TempBot().run()
