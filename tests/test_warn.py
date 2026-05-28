"""Tests for the moderator warning system."""

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

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from cogs.warn import WarnCog
from utils.database import DatabaseManager, WarningEntry, get_db_session, init_db
from utils.security import escape_markdown


@pytest.fixture(autouse=True)
def _init_test_db():
    """Ensure a clean warning table for every test."""
    init_db('sqlite://')
    yield
    with next(get_db_session()) as db:
        db.query(WarningEntry).delete()
        db.commit()


@pytest.fixture
def warn_cog():
    """Create a WarnCog instance with a mocked bot."""
    with patch.dict('os.environ', {'WARNED_ROLE_ID': '1509612090489442396'}):
        bot = MagicMock(spec=commands.Bot)
        bot.user = MagicMock()
        bot.user.id = 4242
        return WarnCog(bot)


@pytest.fixture
def mock_guild():
    """Create a mock guild with a manageable bot member."""
    guild = MagicMock(spec=discord.Guild)
    guild.id = 999
    guild.owner_id = 1
    guild.default_role = MagicMock(spec=discord.Role)
    guild.default_role.id = 1

    bot_member = MagicMock(spec=discord.Member)
    bot_member.guild_permissions.kick_members = True
    bot_member.top_role.position = 100
    guild.me = bot_member

    warned_role = MagicMock(spec=discord.Role)
    warned_role.id = 1509612090489442396
    warned_role.position = 20
    guild.get_role = MagicMock(
        side_effect=lambda rid: warned_role if rid == 1509612090489442396 else None
    )

    return guild


@pytest.fixture
def mock_moderator(mock_guild):
    """Create a moderator member with sufficient permissions."""
    moderator = MagicMock(spec=discord.Member)
    moderator.id = 555
    moderator.mention = '<@555>'
    moderator.display_name = 'Moderator'
    moderator.guild_permissions.administrator = False
    moderator.guild_permissions.moderate_members = True
    moderator.guild_permissions.kick_members = True
    moderator.guild_permissions.ban_members = False
    moderator.guild_permissions.manage_messages = True
    moderator.top_role.position = 50
    moderator.guild = mock_guild
    return moderator


@pytest.fixture
def mock_member(mock_guild):
    """Create a warnable member."""
    member = MagicMock(spec=discord.Member)
    member.id = 12345
    member.mention = '<@12345>'
    member.display_name = 'WarnedUser'
    member.guild = mock_guild
    member.bot = False
    member.guild_permissions.administrator = False
    member.guild_permissions.moderate_members = False
    member.guild_permissions.kick_members = False
    member.guild_permissions.ban_members = False
    member.guild_permissions.manage_messages = False
    member.roles = []
    member.top_role.position = 10
    member.display_avatar.url = 'https://example.com/avatar.png'
    member.send = AsyncMock()
    member.kick = AsyncMock()
    member.add_roles = AsyncMock()
    member.remove_roles = AsyncMock()
    return member


@pytest.fixture
def mock_interaction(mock_guild, mock_moderator):
    """Create a mock interaction for the warn command."""
    interaction = MagicMock(spec=discord.Interaction)
    interaction.guild = mock_guild
    interaction.user = mock_moderator
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


@pytest.mark.asyncio
async def test_warn_first_warning_creates_db_record(warn_cog, mock_interaction, mock_member):
    """The first warning should create an active DB row and send a card."""
    with patch('cogs.warn.init_db'):
        await warn_cog.warn_command.callback(
            warn_cog,
            mock_interaction,
            mock_member,
            reason='Please stop spamming',
        )

    mock_interaction.response.defer.assert_awaited_once()
    mock_interaction.followup.send.assert_awaited_once()
    embed = mock_interaction.followup.send.call_args.kwargs['embed']
    assert embed.title == '⚠️ Warning issued'
    assert '**this is your 1st warning**' in embed.description
    assert embed.footer.text == '© Coconut wisdom since 1875'
    mock_member.add_roles.assert_awaited_once()

    with get_db_session() as db:
        warnings = db.query(WarningEntry).filter(WarningEntry.user_id == str(mock_member.id)).all()
        assert len(warnings) == 1
        assert warnings[0].warning_number == 1
        assert warnings[0].triggered_kick is False
        assert warnings[0].is_active is True
        assert warnings[0].reason == 'Please stop spamming'


@pytest.mark.asyncio
async def test_warn_third_warning_kicks_and_clears_active_cycle(
    warn_cog,
    mock_interaction,
    mock_member,
):
    """The third warning should kick the member and archive the active cycle."""
    mock_member.roles = [mock_interaction.guild.get_role(1509612090489442396)]

    with get_db_session() as db:
        db.add(
            WarningEntry(
                guild_id=str(mock_interaction.guild.id),
                user_id=str(mock_member.id),
                username=mock_member.display_name,
                moderator_id='555',
                moderator_name='Moderator',
                reason='First warning',
                warning_number=1,
                is_active=True,
            )
        )
        db.add(
            WarningEntry(
                guild_id=str(mock_interaction.guild.id),
                user_id=str(mock_member.id),
                username=mock_member.display_name,
                moderator_id='555',
                moderator_name='Moderator',
                reason='Second warning',
                warning_number=2,
                is_active=True,
            )
        )
        db.commit()

    with patch('cogs.warn.init_db'):
        await warn_cog.warn_command.callback(
            warn_cog,
            mock_interaction,
            mock_member,
            reason='Third warning',
        )

    mock_member.kick.assert_awaited_once_with(
        reason='User has been warned too many times.'
    )
    mock_member.remove_roles.assert_awaited_once()
    embed = mock_interaction.followup.send.call_args.kwargs['embed']
    assert embed.title == '🛑 Warning limit reached'
    assert '**this is your 3rd warning**' in embed.description

    with get_db_session() as db:
        active_warnings = DatabaseManager.get_active_warnings(
            db,
            str(mock_interaction.guild.id),
            str(mock_member.id),
        )
        assert active_warnings == []

        all_warnings = (
            db.query(WarningEntry)
            .filter(WarningEntry.user_id == str(mock_member.id))
            .order_by(WarningEntry.id.asc())
            .all()
        )
        assert len(all_warnings) == 3
        assert all_warnings[-1].triggered_kick is True
        assert all(warning.is_active is False for warning in all_warnings)


@pytest.mark.asyncio
async def test_warn_rejects_non_moderators(warn_cog, mock_interaction, mock_member):
    """Non-moderators should receive an ephemeral rejection."""
    mock_interaction.user.guild_permissions.moderate_members = False
    mock_interaction.user.guild_permissions.kick_members = False
    mock_interaction.user.guild_permissions.manage_messages = False

    await warn_cog.warn_command.callback(
        warn_cog,
        mock_interaction,
        mock_member,
        reason='No permission',
    )

    mock_interaction.response.send_message.assert_awaited_once()
    assert 'Only moderators and above' in mock_interaction.response.send_message.call_args.args[0]
    assert mock_interaction.response.send_message.call_args.kwargs['ephemeral'] is True


@pytest.mark.asyncio
async def test_warn_rejects_moderator_targets(warn_cog, mock_interaction, mock_member):
    """Moderators and above should not be warnable targets."""
    mock_member.guild_permissions.administrator = False
    mock_member.guild_permissions.moderate_members = True
    mock_member.guild_permissions.kick_members = False
    mock_member.guild_permissions.ban_members = False
    mock_member.guild_permissions.manage_messages = False

    await warn_cog.warn_command.callback(
        warn_cog,
        mock_interaction,
        mock_member,
        reason='Should fail',
    )

    mock_interaction.response.send_message.assert_awaited_once()
    assert 'cannot be warned' in mock_interaction.response.send_message.call_args.args[0]
    mock_interaction.response.defer.assert_not_awaited()


@pytest.mark.asyncio
async def test_warn_uses_default_reason_when_omitted(
    warn_cog,
    mock_interaction,
    mock_member,
):
    """Warnings without a reason should use the configured default reason."""
    with patch('cogs.warn.init_db'):
        await warn_cog.warn_command.callback(
            warn_cog,
            mock_interaction,
            mock_member,
        )

    embed = mock_interaction.followup.send.call_args.kwargs['embed']
    reason_field = next(field for field in embed.fields if field.name == 'Reason')
    assert reason_field.value == escape_markdown(WarnCog.DEFAULT_REASON)

    with get_db_session() as db:
        warning = db.query(WarningEntry).filter(WarningEntry.user_id == str(mock_member.id)).one()
        assert warning.reason == WarnCog.DEFAULT_REASON


@pytest.mark.asyncio
async def test_resetwarnings_clears_active_warning_cycle(
    warn_cog,
    mock_interaction,
    mock_member,
):
    """Resetting warnings should archive active warnings without deleting history."""
    mock_member.roles = [mock_interaction.guild.get_role(1509612090489442396)]

    with get_db_session() as db:
        db.add(
            WarningEntry(
                guild_id=str(mock_interaction.guild.id),
                user_id=str(mock_member.id),
                username=mock_member.display_name,
                moderator_id='555',
                moderator_name='Moderator',
                reason='First warning',
                warning_number=1,
                is_active=True,
            )
        )
        db.add(
            WarningEntry(
                guild_id=str(mock_interaction.guild.id),
                user_id=str(mock_member.id),
                username=mock_member.display_name,
                moderator_id='555',
                moderator_name='Moderator',
                reason='Second warning',
                warning_number=2,
                is_active=True,
            )
        )
        db.commit()

    with patch('cogs.warn.init_db'):
        await warn_cog.resetwarnings_command.callback(
            warn_cog,
            mock_interaction,
            mock_member,
        )

    mock_interaction.response.send_message.assert_awaited_once()
    assert 'Reset 2 active warning(s)' in mock_interaction.response.send_message.call_args.args[0]
    mock_member.remove_roles.assert_awaited_once()

    with get_db_session() as db:
        active_warnings = DatabaseManager.get_active_warnings(
            db,
            str(mock_interaction.guild.id),
            str(mock_member.id),
        )
        assert active_warnings == []
        historical_warnings = db.query(WarningEntry).filter(
            WarningEntry.user_id == str(mock_member.id)
        ).all()
        assert len(historical_warnings) == 2
        assert all(warning.is_active is False for warning in historical_warnings)


