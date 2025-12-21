#  Copyright (C) 2025 by Kolja Nolte
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
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Import the logging module for tracking bot activities and errors
import logging

# Import the regular expression module for pattern matching in text
import re

# Import datetime for current time operations
from datetime import datetime, timedelta

# Import the discord.py library for interacting with the Discord API
import discord

# Import the commands extension from discord.py for bot command handling
from discord.ext import commands

# Import configuration constants from the config file
from config.config import COCOBOT_VERSION, DISCORD_SERVER_ID

# Import setup function for logging configuration
from utils.logger import bot_logger, command_logger, error_logger, setup_logging

# Import database functions
from utils.database import init_db, get_db_session, DatabaseManager

# Import SQLAlchemy error for database exception handling
from sqlalchemy.exc import SQLAlchemyError

# Configure advanced logging settings
setup_logging(log_level="INFO")

# List of initial extensions (cogs) to load on startup
INITIAL_EXTENSIONS = [
    # Time-related commands cog
    'cogs.time',
    # Currency exchange functionality cog
    'cogs.exchangerate',
    # Weather information commands cog
    'cogs.weather',
    # Text transliteration commands cog
    'cogs.transliterate',
    # Translation commands cog
    'cogs.translate',
    # Air pollution information cog
    'cogs.pollution',
    # Learning-related commands cog
    'cogs.learn',
    # Administrative commands cog
    'cogs.admin',
]


# Define the main bot class inheriting from commands.Bot
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

    # Version identifier for the bot
    version: str = COCOBOT_VERSION

    # Constructor method to initialize the bot
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
        # Initialize default Discord intents
        intents = discord.Intents.default()

        # Enable member-related intents for tracking member information
        intents.members = True

        # Enable message content intent to read message content
        intents.message_content = True

        # Call the parent class constructor with command prefix and intents
        super().__init__(command_prefix='!', intents=intents)

        # Dictionary to track cooldowns for the 'tate' command per user
        self.tate_cooldowns = {}

        # Set to track users reminded in the visa channel (for backward compatibility)
        # The actual logic now uses database, but this is kept for tests
        self.reminded_users = set()

    # Setup hook to load extensions and sync commands
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
        # Initialize database
        init_db()

        # Iterate through the list of initial extensions
        for extension in INITIAL_EXTENSIONS:
            # Try to load the current extension
            try:
                # Asynchronously load the extension (discord.py will log this automatically)
                await self.load_extension(extension)
            # Catch extension loading errors (ImportError, ModuleNotFoundError, etc.)
            except (ImportError, ModuleNotFoundError, AttributeError) as e:
                # Log the failure to load the extension along with the error details
                bot_logger.error(
                    f'Failed to load extension {extension}. {type(e).__name__}: {e}',
                    exc_info=True
                )

        # Create a discord.Object representing the target guild using its ID
        guild = discord.Object(id=DISCORD_SERVER_ID)

        # Copy global application commands to the specified guild
        self.tree.copy_global_to(guild=guild)

        # Synchronize the application command tree with the specified guild
        await self.tree.sync(guild=guild)

        # Log that the command tree synchronization is complete
        bot_logger.info('Command tree synced.')

    # Event that triggers when the bot is ready and online
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
        # Log an informational message indicating the bot is ready, including its
        # username
        bot_logger.info(f'🥥 {self.user} is ready! (ID: {self.user.id})')

        # Set the bot's activity status
        await self.change_presence(
            activity=discord.Game(name="Waiting for a coconut to fall")
        )

        # Log guild information where the bot is present
        for guild in self.guilds:
            bot_logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')

    # Event that triggers for every message received
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
        # Check if the message author is the bot itself to prevent self-responses
        if message.author == self.user:
            # Exit the handler if the message is from the bot
            return

        # Check for visa channel nationality reminder condition
        # Only remind the user if they haven't been reminded before and their message contains "visa"
        if (
            message.channel.name == "visa"
            and "visa" in message.content.lower()  # Case-insensitive matching
        ):
            # Try to check database, but allow graceful fallback for test environments
            user_already_reminded = False
            try:
                # Initialize database if not already done
                init_db()  # Safe to call multiple times

                # Check database if user has already been reminded
                with get_db_session() as db:
                    user_already_reminded = DatabaseManager.has_been_reminded_about_visa(db, str(message.author.id))
            except SQLAlchemyError as e:
                # Log the exception and fall back to in-memory check
                error_logger.error(f"Database error checking visa reminder: {e}")
                user_already_reminded = message.author.id in self.reminded_users

            if not user_already_reminded:
                # Send a reminder to mention nationality in the visa channel
                await message.channel.send(
                    f"🥥 **Friendly reminder to {message.author.mention}**: Don't forget "
                    f"to **mention your nationality** when asking questions in this "
                    f"channel. Visa rules can vary "
                    "significantly based on your nationality.",
                    silent=True,
                )
                # Mark user as reminded in the database if available, otherwise in-memory
                try:
                    init_db()  # Ensure database is initialized

                    with get_db_session() as db:
                        DatabaseManager.mark_user_as_reminded_about_visa(db, str(message.author.id))
                except SQLAlchemyError as e:
                    # Log the exception instead of failing silently
                    error_logger.error(f"Database error marking user as reminded: {e}")

                # Always add to in-memory set for backward compatibility with tests
                self.reminded_users.add(message.author.id)
                # Prevent further processing for this message
                return

        # Flag for sending Cocobot info embed
        send_cocobot_info_embed = False

        # Strip whitespace from message content
        normalized_message_content_stripped = message.content.strip()

        # Check if message is exactly '!cocobot'
        is_cocobot_command = normalized_message_content_stripped.lower() == '!cocobot'

        # Check if Cocobot is mentioned in the message
        is_cocobot_mention = any(
            mention.id == self.user.id for mention in message.mentions
        )

        # Set flag if command or mention detected
        if is_cocobot_command or is_cocobot_mention:
            send_cocobot_info_embed = True

        # Send Cocobot info embed if flag is set
        if send_cocobot_info_embed:
            # Import version again to get the mocked value during tests
            from config.config import COCOBOT_VERSION as CURRENT_VERSION
            # Create embed for Cocobot info
            embed = discord.Embed(
                timestamp=datetime.now(),
                title="🥥 Cocobot at your service!",
                url="https://gitlab.com/thailand-discord/bots/cocobot",
                description=f"Hi, I'm **@cocobot** `v{CURRENT_VERSION}`, the *actual* "
                            f"useful brother of our dearest August Engelhardt. Type "
                            f"`/coco` to see what I can do for you. I "
                            "promise on the holy coconut, I'm here to help.",
                color=discord.Color.green(),
            )
            # Add bot avatar as thumbnail if available
            if self.user.display_avatar:
                embed.set_thumbnail(url=self.user.display_avatar.url)
            # Set footer text
            embed.set_footer(text="© Coconut wisdom since 1875")
            # Send the embed to the channel
            await message.channel.send(embed=embed)
            # Prevent further processing for this message
            return

        # Regular expression pattern to detect the word 'tate'
        tate_pattern = r'(?<!\w)tate(?!\w)'

        # Search for 'tate' in message content
        if re.search(tate_pattern, message.content, re.IGNORECASE):
            # Get current time
            now = datetime.now()

            # Get message author
            user = message.author

            # Check if user is in cooldown dictionary
            if user.id in self.tate_cooldowns:
                # Get last used timestamp
                last_used = self.tate_cooldowns[user.id]

                # Calculate time since last use
                time_since = now - last_used

                # Check if cooldown period has not passed
                if time_since < timedelta(minutes=3):
                    # Inform user about cooldown
                    await message.channel.send(
                        f"🥥 Sorry, {user.mention}, the Bottom G is tired from all "
                        f"the Bottom G'ing and needs a 3-minute break."
                    )

                    # Prevent further processing for this message
                    return

            # Update last used timestamp (either for new user or after cooldown has
            # passed)
            self.tate_cooldowns[user.id] = now

            # Create embed for 'tate' GIF
            embed = discord.Embed()
            embed.set_image(url='https://c.tenor.com/fyrqnSBR4gcAAAAd/tenor.gif')

            # Send the embed to the channel
            await message.channel.send(embed=embed)
        # Check for tribute to @Nal
        elif '@Nal' in message.content or any(
            mention.name == 'nal_9345' for mention in message.mentions
        ):
            # Create embed for Nal tribute
            embed = discord.Embed()
            embed.set_image(url='https://smmallcdn.net/kolja/1749743431468/nal.avif')
            # Send the embed to the channel
            await message.channel.send(embed=embed)

        # Process any commands contained in the message
        await self.process_commands(message)

    # Global error handler for commands
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
        # Handle command not found errors
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                f"❌ Command '{ctx.command}' not found. Use `/help` to see available "
                f"commands."
            )
            command_logger.warning(f"Command not found: {ctx.command} by {ctx.author}")
            return

        # Handle missing required arguments
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
            command_logger.warning(
                f"Missing required argument in {ctx.command}: {error.param.name}"
            )
            return

        # Handle bad argument errors
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided: {error}")
            command_logger.warning(f"Bad argument in {ctx.command}: {error}")
            return

        # Handle command on cooldown errors
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ This command is on cooldown. Try again in {error.retry_after:.2f}s"
            )
            command_logger.info(f"Command on cooldown: {ctx.command} by {ctx.author}")
            return

        # Log other errors
        else:
            await ctx.send(
                "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                "developers have been notified."
            )
            error_logger.error(
                f"Error in command {ctx.command}: {error}", exc_info=True
            )

    # Global error handler for application commands (slash commands)
    @staticmethod
    async def on_app_command_error(interaction, error):
        """
        Global error handler for application command errors.

        Args:
                interaction: Discord interaction object
                error: The exception that occurred
        """
        try:
            if interaction.response.is_done():
                # If response is already done, follow up instead
                await interaction.followup.send(
                    "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                    "developers have been notified.",
                    ephemeral=True,
                )
            else:
                # If no response yet, send response
                await interaction.response.send_message(
                    "🥥 Oops, something's cracked, and it's **not** the coconut! The "
                    "developers have been notified.",
                    ephemeral=True,
                )
        except (discord.HTTPException, discord.InteractionResponded, discord.NotFound) as followup_error:
            # If we can't send an error message to the user due to Discord API issues,
            # log it for debugging but don't crash the error handler
            error_logger.error(
                f"Failed to send error message to user: {followup_error}", exc_info=True
            )

        error_logger.error(f"Error in app command: {error}", exc_info=True)

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
        with get_db_session() as db:
            # Find and delete any existing visa reminder for the user
            from utils.database import VisaReminder
            reminder = db.query(VisaReminder).filter(VisaReminder.user_discord_id == user_id).first()
            if reminder:
                db.delete(reminder)
                db.commit()
                return True
            return False

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
        # Access the token variable from the current module context
        # The module globals will have the patched value during tests
        import sys

        # Get the 'bot' module to access potentially patched variables
        bot_module = sys.modules.get('bot')
        if bot_module:
            token = getattr(bot_module, 'DISCORD_BOT_TOKEN', None)
        else:
            token = None

        if token is None:
            # Fallback to config if not found in module (shouldn't happen in normal use)
            from config.config import DISCORD_BOT_TOKEN

            token = DISCORD_BOT_TOKEN

        super().run(token)


def main():
    """
    The main entry point of the application. This function initializes and starts a bot instance.

    This function is responsible for creating an instance of the `Cocobot` class and executing its
    custom `run` method to start the bot using the necessary configuration details.

    Raises:
        Any exception related to bot initialization or runtime errors.
    """
    # Initialize an instance of the Cocobot class
    bot = Cocobot()

    # Run the bot using the token retrieved from the configuration
    bot.run()  # Use the custom run method that gets the token internally


if __name__ == "__main__":
    main()
