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

"""
Tests for the AI Jail cog (cogs/jail.py).
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from cogs.jail import JailCog
from utils.database import JailedUser, get_db_session, init_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _init_test_db():
    """Ensure a clean jailed_users table for every test."""
    init_db('sqlite://')  # in-memory database
    yield
    with next(get_db_session()) as db:
        db.query(JailedUser).delete()
        db.commit()


@pytest.fixture
def jail_cog():
    """Create a JailCog instance with mocked bot and env vars."""
    with patch.dict('os.environ', {
        'JAIL_ROLE_ID': '999',
        'AUGUST_INTERNAL_PORT': '17432',
        'AUGUST_INTERNAL_SECRET': 'test-secret',
    }):
        bot = MagicMock(spec=commands.Bot)
        cog = JailCog(bot)
        return cog


@pytest.fixture
def mock_guild():
    """Create a mock guild with a default role and a jail role."""
    guild = MagicMock(spec=discord.Guild)

    default_role = MagicMock(spec=discord.Role)
    default_role.id = 1
    guild.default_role = default_role

    jail_role = MagicMock(spec=discord.Role)
    jail_role.id = 999
    guild.get_role = MagicMock(side_effect=lambda rid: jail_role if rid == 999 else None)

    return guild, default_role, jail_role


@pytest.fixture
def mock_member(mock_guild):
    """Create a mock member with two roles."""
    guild, default_role, _ = mock_guild
    member = MagicMock(spec=discord.Member)
    member.id = 12345
    member.display_name = 'TestUser'
    member.mention = '<@12345>'
    member.guild = guild

    role_a = MagicMock(spec=discord.Role)
    role_a.id = 100
    role_b = MagicMock(spec=discord.Role)
    role_b.id = 200

    member.roles = [default_role, role_a, role_b]
    member.remove_roles = AsyncMock()
    member.add_roles = AsyncMock()
    member.send = AsyncMock()

    return member


@pytest.fixture
def mock_interaction(mock_guild, mock_member):
    """Create a mock interaction for slash commands."""
    guild, _, _ = mock_guild
    interaction = MagicMock(spec=discord.Interaction)
    interaction.guild = guild
    interaction.user = MagicMock(spec=discord.Member)
    interaction.user.id = 99999
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    return interaction


# ---------------------------------------------------------------------------
# /jail tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_jail_already_jailed(jail_cog, mock_interaction, mock_member):
    """Jailing an already-jailed user should return an ephemeral abort."""
    # Pre-insert a jail record
    with next(get_db_session()) as db:
        db.add(JailedUser(
            user_id=str(mock_member.id),
            username='TestUser',
            jailed_by='99999',
            roles_snapshot='[]',
        ))
        db.commit()

    with patch('cogs.jail.init_db'):
        await jail_cog.jail_command.callback(jail_cog, mock_interaction, mock_member)

    mock_interaction.response.send_message.assert_awaited_once()
    call_kwargs = mock_interaction.response.send_message.call_args
    assert 'already in jail' in call_kwargs[0][0]
    assert call_kwargs[1]['ephemeral'] is True


@pytest.mark.asyncio
async def test_jail_success(jail_cog, mock_interaction, mock_member):
    """Happy path: roles stripped, Jailed role assigned, DB record created, August notified."""
    with patch('cogs.jail.init_db'), \
         patch.object(jail_cog, '_call_august', new_callable=AsyncMock, return_value=True) as mock_august:
        await jail_cog.jail_command.callback(
            jail_cog, mock_interaction, mock_member, reason='test reason'
        )

    # Roles should have been stripped
    mock_member.remove_roles.assert_awaited_once()

    # Jailed role should have been assigned
    mock_member.add_roles.assert_awaited_once()

    # August should have been called
    mock_august.assert_awaited_once_with('/start-jail', {
        'user_id': str(mock_member.id),
        'username': mock_member.display_name,
    })

    # DB record should exist
    with next(get_db_session()) as db:
        record = db.query(JailedUser).filter(
            JailedUser.user_id == str(mock_member.id)
        ).first()
        assert record is not None
        assert record.reason == 'test reason'
        assert json.loads(record.roles_snapshot) == ['100', '200']

    # Ephemeral success message
    call_kwargs = mock_interaction.response.send_message.call_args
    assert 'has been jailed' in call_kwargs[0][0]


# ---------------------------------------------------------------------------
# /unjail tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unjail_not_jailed(jail_cog, mock_interaction, mock_member):
    """Unjailing a user who is not jailed should return an ephemeral abort."""
    with patch('cogs.jail.init_db'):
        await jail_cog.unjail_command.callback(jail_cog, mock_interaction, mock_member)

    mock_interaction.response.send_message.assert_awaited_once()
    call_kwargs = mock_interaction.response.send_message.call_args
    assert 'not currently jailed' in call_kwargs[0][0]
    assert call_kwargs[1]['ephemeral'] is True


@pytest.mark.asyncio
async def test_unjail_success(jail_cog, mock_interaction, mock_member, mock_guild):
    """Happy path: August stopped, roles restored, DB record deleted."""
    guild, _, jail_role = mock_guild

    # Pre-insert a jail record with role snapshot
    with next(get_db_session()) as db:
        db.add(JailedUser(
            user_id=str(mock_member.id),
            username='TestUser',
            jailed_by='99999',
            roles_snapshot=json.dumps(['100', '200']),
        ))
        db.commit()

    # Make jail role appear in the member's current roles
    mock_member.roles = [guild.default_role, jail_role]

    # Mock guild.get_role to return mock roles for restoration
    role_100 = MagicMock(spec=discord.Role)
    role_100.id = 100
    role_200 = MagicMock(spec=discord.Role)
    role_200.id = 200

    def get_role_side_effect(rid):
        mapping = {999: jail_role, 100: role_100, 200: role_200}
        return mapping.get(rid)

    guild.get_role = MagicMock(side_effect=get_role_side_effect)

    with patch('cogs.jail.init_db'), \
         patch.object(jail_cog, '_call_august', new_callable=AsyncMock, return_value=True) as mock_august:
        await jail_cog.unjail_command.callback(jail_cog, mock_interaction, mock_member)

    # August should have been told to stop
    mock_august.assert_awaited_once_with('/stop-jail', {'user_id': str(mock_member.id)})

    # Jail role should have been removed
    mock_member.remove_roles.assert_awaited_once()

    # Roles should have been restored
    mock_member.add_roles.assert_awaited_once()
    restored = mock_member.add_roles.call_args[0]
    restored_ids = {r.id for r in restored}
    assert restored_ids == {100, 200}

    # DB record should be gone
    with next(get_db_session()) as db:
        record = db.query(JailedUser).filter(
            JailedUser.user_id == str(mock_member.id)
        ).first()
        assert record is None

    # Success message
    call_kwargs = mock_interaction.response.send_message.call_args
    assert 'unjailed' in call_kwargs[0][0]


# ---------------------------------------------------------------------------
# on_member_remove tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_on_member_remove_jailed(jail_cog):
    """When a jailed member leaves, the DB record should be deleted and August notified."""
    # Pre-insert a jail record
    with next(get_db_session()) as db:
        db.add(JailedUser(
            user_id='55555',
            username='LeavingUser',
            jailed_by='99999',
            roles_snapshot='[]',
        ))
        db.commit()

    member = MagicMock(spec=discord.Member)
    member.id = 55555

    with patch('cogs.jail.init_db'), \
         patch.object(jail_cog, '_call_august', new_callable=AsyncMock, return_value=True) as mock_august:
        await jail_cog.on_member_remove(member)

    mock_august.assert_awaited_once_with('/stop-jail', {'user_id': '55555'})

    with next(get_db_session()) as db:
        assert db.query(JailedUser).filter(JailedUser.user_id == '55555').first() is None


@pytest.mark.asyncio
async def test_on_member_remove_not_jailed(jail_cog):
    """When a non-jailed member leaves, nothing should happen."""
    member = MagicMock(spec=discord.Member)
    member.id = 77777

    with patch('cogs.jail.init_db'), \
         patch.object(jail_cog, '_call_august', new_callable=AsyncMock) as mock_august:
        await jail_cog.on_member_remove(member)

    mock_august.assert_not_awaited()
