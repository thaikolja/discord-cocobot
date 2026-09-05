#  Copyright (C) 2026 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2024-2026
#  Package:   cocobot Discord Bot

"""
Logs the bot's readiness and sets up activity status and guild connections upon startup.

This method is an event listener triggered when the bot has successfully connected to Discord.
It performs the following main actions:
1. Logs a readiness message, including the bot's username and ID.
2. Sets the bot's activity status to display a custom message.
3. Logs the name and ID of each guild the bot is connected to.

Raises:
    No explicit errors are raised by this method.
"""

# Regex: because "tate" deserves a word-boundary, not a half-hearted in-string match
import re

# Time math for cooldowns; coconut wisdom since whenever datetime was invented
from datetime import datetime, timedelta

# The actual Discord SDK, not a coconut with a websocket taped on
import discord

# Slash-command error types live here, because of course they do
from discord import app_commands

# Prefix commands still exist; we keep the extension around like a lucky shell
from discord.ext import commands

# SQLAlchemy's "something exploded in the database" exception
from sqlalchemy.exc import SQLAlchemyError

# Version string and the one guild we actually care about
from config.config import COCOBOT_VERSION, DISCORD_SERVER_ID

# Sessions, init, and the manager that pretends visa reminders are a real product
from utils.database import DatabaseManager, get_db_session, init_db

# Loggers: one for the bot, one for commands, one for "oh no"
from utils.logger import bot_logger, command_logger, error_logger, setup_logging

# Spin up logging before anyone asks why the coconut is silent
setup_logging(log_level="INFO")

# Cogs loaded at boot — the whole personality of this nut
INITIAL_EXTENSIONS = [
    # Clock flex for people who forgot Thailand is UTC+7
    'cogs.time',
    # Baht vs. everything else, including regret
    'cogs.exchangerate',
    # Weather, because "it's hot" still needs an API
    'cogs.weather',
    # Romanization for when the Thai keyboard is a suggestion
    'cogs.transliterate',
    # Actual translation, not vibes
    'cogs.translate',
    # AQI so you can blame the air scientifically
    'cogs.pollution',
    # Language drills; the coconut as a tutor
    'cogs.learn',
    # Admin knobs for people with too much power
    'cogs.admin',
    # Warnings: the polite coconut slap
    'cogs.warn',
    # Summarize the chat so nobody has to scroll
    'cogs.summarize',
]


# Main bot class: commands.Bot with extra coconut
class Cocobot(commands.Bot):
    """
    Represents a Discord bot with specific functionalities such as command handling,
    custom events, interaction tracking, and cooldown management.

    This class is designed to act as a custom Discord bot by extending the
    `commands.Bot` class and adding additional features. It enables tracking of
    command usages, manages reminders, synchronizes commands with a specific server,
    and handles bot-related events such as startup and incoming messages. The bot
    is designed with modularity and testability in mind, incorporating database
    interactions and logging functionalities.

    Attributes:
        version (str): The version identifier for the bot.
        tate_cooldowns (dict): Tracks cooldowns for the 'tate' command on a per-user basis. Keys are
            user identifiers, and values store cooldown-related data for managing the command's usage.
        reminded_users (set): Keeps track of users who have received reminders in the visa channel. This
            is maintained mainly for compatibility with existing tests, even though reminders are now
            handled through database interactions.
    """

    # Pin the advertised version so `/cocobot` doesn't invent a number
    version: str = COCOBOT_VERSION

    # Constructor: intents, cooldowns, and a set tests still poke
    def __init__(self):
        """
        Initializes a Discord bot with custom intents and attributes for tracking user actions
        and reminders. Sets up default functionality for command handling and manages specific
        features like 'tate' command cooldowns and user reminders.

        Attributes:
            tate_cooldowns (dict): A dictionary to track cooldowns for the 'tate' command on a
                per-user basis. Keys are identifiers for users, and values store cooldown-related
                data.
            reminded_users (set): A set to track users who have been reminded in the visa channel.
                This is kept for compatibility with tests, although reminder logic has transitioned
                to using a database.
        """
        # Start from Discord's default intents, then turn on the spicy ones
        intents = discord.Intents.default()

        # Members: so we can tell who is who, not just a snowflake
        intents.members = True

        # Message content: privileged, required, and Discord's favorite lecture
        intents.message_content = True

        # Prefix '!' because slash commands weren't enough for nostalgia
        super().__init__(command_prefix='!', intents=intents)

        # Per-user cooldown map for the tate easter egg
        self.tate_cooldowns = {}

        # In-memory visa reminders; tests still check this even after we grew a DB
        self.reminded_users = set()

    # Load cogs, init DB, shove commands onto the guild
    async def setup_hook(self):
        """
        Performs setup operations for the application, including database initialization,
        extension loading, and command tree synchronization.

        This method initializes the database, loads predefined extensions, and synchronizes
        application commands with a specific Discord server. It manages errors during the
        extension loading process and logs the corresponding outcomes.

        Raises:
            ImportError: If an import operation fails while loading an extension.
            ModuleNotFoundError: If an extension module cannot be found.
            AttributeError: If an attribute required for loading an extension is missing.
        """
        # Create tables before anyone tries to remind a visa applicant
        init_db()

        # Walk the cog list like a packing list for a beach trip
        for extension in INITIAL_EXTENSIONS:
            # One cog at a time so a bad import doesn't nuke the whole fruit
            try:
                # discord.py logs this; we just await and hope
                await self.load_extension(extension)

            # Missing module, bad import, or someone renamed a class
            except (ImportError, ModuleNotFoundError, AttributeError) as e:
                # Log it loud; a silent failed cog is how you ship a dummy
                bot_logger.error(
                    f'Failed to load extension {extension}. {type(e).__name__}: {e}',
                    exc_info=True
                )

        # Target guild object from the configured server ID
        guild = discord.Object(id=DISCORD_SERVER_ID)

        # Copy globals onto the guild so slash commands show up this century
        self.tree.copy_global_to(guild=guild)

        # Sync; Discord will pretend this is instant
        await self.tree.sync(guild=guild)

        # Confirm the tree actually landed
        bot_logger.info('Commands loaded...')

    # Fired when Discord finally admits we exist
    async def on_ready(self):
        """
        Logs the bot's readiness and sets up activity status and guild connections upon startup.

        This method is an event listener triggered when the bot has successfully connected to Discord.
        It performs the following main actions:
        1. Logs a readiness message, including the bot's username and ID.
        2. Sets the bot's activity status to display a custom message.
        3. Logs the name and ID of each guild the bot is connected to.

        Raises:
            No explicit errors are raised by this method.

        """
        # Username + ID so logs can prove which coconut woke up
        bot_logger.info(f'🥥 {self.user} is ready! (ID: {self.user.id})')

        # Playing "Waiting for a coconut to fall" — accurate job description
        await self.change_presence(
            activity=discord.Game(name="Waiting for a coconut to fall")
        )

        # List every guild so we notice if we joined the wrong island
        for guild in self.guilds:
            # Name and ID; "unknown" guilds are how incidents start
            bot_logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')

    # Every message walks through this gauntlet
    async def on_message(self, message):
        """
        Handles incoming messages sent in Discord channels and performs various actions
        based on message content or channel context. This method checks for specific
        keywords, commands, and user interactions to send contextual messages, reminders,
        or embeds, while also managing cooldowns and ensuring database consistency.

        Args:
            message (discord.Message): The message object containing information such as
                the sender, channel, and content.

        Raises:
            SQLAlchemyError: If an error occurs while interacting with the database during
                user reminder checks or updates.

        """
        # Ignore our own messages; infinite coconut loops are not a feature
        if message.author == self.user:
            # Leave immediately, pride intact
            return

        # Visa channel + the word "visa" = nationality nag, once
        if (
            message.channel.name == "visa"
            and "visa" in message.content.lower()  # Case-insensitive matching
        ):
            # Default: we have not nagged this human yet
            user_already_reminded = False

            # DB first; tests and outages fall back to a set
            try:
                # Harmless if already initialized
                init_db()  # Safe to call multiple times

                # Ask the database if this Discord ID already got the speech
                with get_db_session() as db:
                    # Persistent reminder flag, not vibes
                    user_already_reminded = DatabaseManager.has_been_reminded_about_visa(db, str(message.author.id))

            # Database sulking: log it and use RAM like it's 2019
            except SQLAlchemyError as e:
                # Don't hide SQL failures behind a coconut emoji
                error_logger.error(f"Database error checking visa reminder: {e}")

                # In-memory fallback the tests still love
                user_already_reminded = message.author.id in self.reminded_users

            # First-time visa chatter: send the nationality reminder
            if not user_already_reminded:
                # Silent ping so we don't wake the whole island
                await message.channel.send(
                    f"🥥 **Friendly reminder to {message.author.mention}**: Don't forget "
                    f"to **mention your nationality** when asking questions in this "
                    f"channel. Visa rules can vary "
                    "significantly based on your nationality.",
                    silent=True,
                )

                # Persist the nag so we don't become that bot
                try:
                    # Init again in case the first call never ran
                    init_db()  # Ensure database is initialized

                    # Write the reminder row
                    with get_db_session() as db:
                        # Mark this user as already reminded
                        DatabaseManager.mark_user_as_reminded_about_visa(db, str(message.author.id))

                # DB write failed; we still remember in RAM
                except SQLAlchemyError as e:
                    # Log it; silent failure is how duplicates happen
                    error_logger.error(f"Database error marking user as reminded: {e}")

                # Tests inspect this set; keep it honest
                self.reminded_users.add(message.author.id)

                # Stop here; no tate GIFs in visa support
                return

        # Flag for the "who is this coconut" embed
        send_cocobot_info_embed = False

        # Trim so "!cocobot " still counts as a hello
        normalized_message_content_stripped = message.content.strip()

        # Exact !cocobot, case-insensitive because thumbs exist
        is_cocobot_command = normalized_message_content_stripped.lower() == '!cocobot'

        # Mention-only ping: no extra text, just @cocobot
        is_cocobot_mention_alone = False

        # Did they actually ping us, or just talk about coconuts?
        if any(mention.id == self.user.id for mention in message.mentions):
            # Start with the stripped text, then peel mentions off
            text_without_mentions = normalized_message_content_stripped

            # Strip every mention form Discord might have used
            for mention in message.mentions:
                # Both <@id> and the nick form <@!id>
                text_without_mentions = text_without_mentions.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')

            # If nothing but whitespace remains, they pinged us alone
            if text_without_mentions.strip() == '':
                # That's a hello, not a conversation
                is_cocobot_mention_alone = True

        # Humans only; bots pinging bots is a crime against CPU
        if not message.author.bot and (is_cocobot_command or is_cocobot_mention_alone):
            # Flip the flag so we send the intro embed
            send_cocobot_info_embed = True

        # Intro embed path
        if send_cocobot_info_embed:
            # Re-import so tests can patch the version without restarting the universe
            from config.config import COCOBOT_VERSION as CURRENT_VERSION

            # Green embed: service announcement with a Gitlab invite
            embed = discord.Embed(
                timestamp=datetime.now(),
                title="🥥 Cocobot at your service!",
                description=f"Hi, I'm **@cocobot** `v{CURRENT_VERSION}`, the *actual* "
                            f"useful brother of our dearest August Engelhardt. Type "
                            f"`/cocobot` to see what I can do for you. I "
                            f"promise on the holy coconut, I'm here to help. "
                            f"Cocovores are invited to [contribute](https://gitlab.com/thailand-discord/bots/cocobot) to my code.",
                color=discord.Color.green(),
            )

            # Thumbnail if Discord gave us a face
            if self.user.display_avatar:
                # Use the current avatar URL, not a fossil
                embed.set_thumbnail(url=self.user.display_avatar.url)

            # Footer older than most of the server
            embed.set_footer(text="© Coconut wisdom since 1875")

            # Drop the embed in-channel
            await message.channel.send(embed=embed)

            # Don't also process this as a prefix command
            return

        # Word-boundary tate; "estate" is not a meme
        tate_pattern = r'(?<!\w)tate(?!\w)'

        # Case-insensitive hunt for the Bottom G
        if re.search(tate_pattern, message.content, re.IGNORECASE):
            # Clock for the 3-minute nap
            now = datetime.now()

            # Who summoned this
            user = message.author

            # Already on cooldown?
            if user.id in self.tate_cooldowns:
                # Last GIF timestamp
                last_used = self.tate_cooldowns[user.id]

                # How long since we last indulged
                time_since = now - last_used

                # Three minutes of peace for the GIF CDN
                if time_since < timedelta(minutes=3):
                    # Tell them the Bottom G is napping
                    await message.channel.send(
                        f"🥥 Sorry, {user.mention}, the Bottom G is tired from all "
                        f"the Bottom G'ing and needs a 3-minute break."
                    )

                    # No GIF, no further processing
                    return

            # Stamp the cooldown, new user or post-nap
            self.tate_cooldowns[user.id] = now

            # Empty embed, image does the talking
            embed = discord.Embed()

            # Tenor URL that has survived longer than it should
            embed.set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif')

            # Send the GIF
            await message.channel.send(embed=embed)

        # Tribute path for @Nal / nal_9345
        elif '@Nal' in message.content or any(
            mention.name == 'nal_9345' for mention in message.mentions
        ):
            # Another image-only embed
            embed = discord.Embed()

            # Hosted tribute image
            embed.set_image(url='https://smmallcdn.net/kolja/1749743431468/nal.avif')

            # Send it
            await message.channel.send(embed=embed)

        # Always let prefix commands have a turn
        await self.process_commands(message)

    # Prefix-command error dump
    async def on_command_error(self, ctx, error):
        """
        Handles errors triggered by command execution in the bot.

        This handler processes various types of errors encountered during the execution of
        commands and provides user-friendly feedback. Additionally, it logs significant
        information regarding the error events for further analysis.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            error (commands.CommandError): The error object containing details about the
                encountered issue.

        """
        # Unknown command: point at /help instead of gaslighting
        if isinstance(error, commands.CommandNotFound):
            # User-facing miss
            await ctx.send(
                f"❌ Command '{ctx.command}' not found. Use `/help` to see available "
                f"commands."
            )

            # Log who asked for a ghost command
            command_logger.warning(f"Command not found: {ctx.command} by {ctx.author}")

            # Done with this error
            return

        # Missing args: name the param, don't shrug
        elif isinstance(error, commands.MissingRequiredArgument):
            # Tell them which knob they skipped
            await ctx.send(f"❌ Missing required argument: {error.param.name}")

            # Log for the "users never read usage" archive
            command_logger.warning(
                f"Missing required argument in {ctx.command}: {error.param.name}"
            )

            # Stop here
            return

        # Bad types / parse failures
        elif isinstance(error, commands.BadArgument):
            # Echo the converter's complaint
            await ctx.send(f"❌ Invalid argument provided: {error}")

            # Log it
            command_logger.warning(f"Bad argument in {ctx.command}: {error}")

            # Stop
            return

        # Rate limit: show seconds, not a lecture
        elif isinstance(error, commands.CommandOnCooldown):
            # retry_after, two decimals, coconut-adjacent hourglass
            await ctx.send(
                f"⏳ This command is on cooldown. Try again in {error.retry_after:.2f}s"
            )

            # Info, not a crime
            command_logger.info(f"Command on cooldown: {ctx.command} by {ctx.author}")

            # Stop
            return

        # Everything else: generic coconut crack
        else:
            # Don't dump tracebacks into the channel
            await ctx.send(
                "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                "developers have been notified."
            )

            # Developers were, in fact, notified via this log
            error_logger.error(
                f"Error in command {ctx.command}: {error}", exc_info=True
            )

    # Slash-command errors: ephemeral, slightly ruder
    @staticmethod
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handles and logs errors encountered during application command execution.

        This method attempts to handle and respond to errors raised while processing
        application commands. If the response to the interaction has already been sent,
        a follow-up message will be sent instead. If no response has been sent yet,
        an error message will be sent as the initial response. Any issues with sending
        the error message due to Discord API limitations are logged for debugging.

        Parameters:
            interaction (discord.Interaction): The interaction object representing the command's context.
            error (app_commands.AppCommandError): The exception raised during command execution.

        Raises:
            discord.HTTPException: If there is an HTTP issue when interacting with the Discord API.
            discord.NotFound: If the interaction or channel is no longer available.
            discord.InteractionResponded: If an attempt is made to respond to an already-responded interaction.
        """
        # Respond or follow up; Discord is picky about which
        try:
            # Already answered? Follow-up only
            if interaction.response.is_done():
                # Ephemeral so the channel doesn't become a graveyard
                await interaction.followup.send(
                    "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                    "developers have been notified. Just kidding, nobody cares.",
                    ephemeral=True,
                )

            # First response still available
            else:
                # Same joke, as the initial reply
                await interaction.response.send_message(
                    "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                    "developers have been notified. Just kidding, nobody cares.",
                    ephemeral=True,
                )

        # HTTP / already-responded / gone interaction: log, don't crash
        except (discord.HTTPException, discord.InteractionResponded, discord.NotFound) as followup_error:
            # Error handler that throws is a special kind of failure
            error_logger.error(
                f"Failed to send error message to user: {followup_error}", exc_info=True
            )

        # Always log the original slash error
        error_logger.error(f"Error in app command: {error}", exc_info=True)

    # Test/admin helper: wipe one user's visa nag
    @staticmethod
    async def reset_visa_reminder_for_user(user_id: str):
        """
        Resets the visa reminder for a specified user by deleting the existing reminder from the database,
        if present. This method ensures that only one active reminder exists per user.

        Args:
            user_id (str): The Discord ID of the user whose visa reminder is to be reset.

        Returns:
            bool: True if a visa reminder was deleted, False if no reminder was found.

        """
        # Session scoped to this reset
        with get_db_session() as db:
            # Model import kept local; circular imports are a lifestyle
            from utils.database import VisaReminder

            # One row per user, if we're lucky
            reminder = db.query(VisaReminder).filter(VisaReminder.user_discord_id == user_id).first()

            # Found it: delete and commit
            if reminder:
                # Remove the row
                db.delete(reminder)

                # Persist
                db.commit()

                # Caller can celebrate
                return True

            # Nothing to reset
            return False

    # Custom run: token from the module so tests can patch it
    def run(self, **kwargs):
        """
        Fetches the Discord bot token and starts the bot.

        This method retrieves the token from the 'bot' module if available. If the token
        is not found in the module (e.g., during standard operations), it falls back to
        reading the token from a configuration file. The token is then passed to the
        parent class's `run` method to initialize and start the bot.

        Args:
            **kwargs: Arbitrary keyword arguments, typically passed during initialization
                and execution of the bot's runtime context.
        """
        # sys.modules is how pytest pretends to be production
        import sys

        # Grab the loaded bot module, if any
        bot_module = sys.modules.get('bot')

        # Patched token lives as a module attribute in tests
        if bot_module:
            # getattr so a missing name isn't a crash
            token = getattr(bot_module, 'DISCORD_BOT_TOKEN', None)

        # Module not loaded (weird, but possible)
        else:
            # Force the config fallback
            token = None

        # No module token: read config the grown-up way
        if token is None:
            # Import here so tests can patch config too
            from config.config import DISCORD_BOT_TOKEN

            # Real token, hopefully
            token = DISCORD_BOT_TOKEN

        # Hand off to discord.py; kwargs unused but kept for signature
        super().run(token)


# CLI entry: construct and run
def main():
    """
    The main entry point of the application. This function initializes and starts a bot instance.

    This function is responsible for creating an instance of the `Cocobot` class and executing its
    custom `run` method to start the bot using the necessary configuration details.

    Raises:
        Any exception related to bot initialization or runtime errors.
    """
    # One Cocobot to rule the Thailand Discord
    bot = Cocobot()

    # Token is fetched inside run(); we just press go
    bot.run()  # Use the custom run method that gets the token internally


# Script entry, not import-time fireworks
if __name__ == "__main__":
    # Start the coconut
    main()
