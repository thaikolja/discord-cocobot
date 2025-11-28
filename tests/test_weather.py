import unittest
import uuid
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import aiohttp
import discord

# Assuming the tests are run from the root directory of the cocobot project,
# or that the PYTHONPATH is set up accordingly.
from cogs.weather import WeatherCog, WeatherView
from config.config import WEATHERAPI_API_KEY  # Import constants


class TestWeatherCog(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = AsyncMock(spec=discord.ext.commands.Bot)
        self.bot.add_view = MagicMock()
        self.weather_cog = WeatherCog(self.bot)

    # The session is created in WeatherCog.__init__
    # We will patch its `get` method in tests.

    async def asyncTearDown(self):
        await self.weather_cog.session.close()

    @patch(
        'cogs.weather.uuid.uuid4',
        return_value=uuid.UUID('12345678-1234-5678-1234-567812345678'),
    )
    @patch('cogs.weather.WeatherView')  # Mock the WeatherView class
    async def test_weather_command_success(self, MockWeatherView, mock_uuid):
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock(spec=discord.InteractionResponse)
        interaction.followup = AsyncMock(spec=discord.Webhook)

        mock_weather_view_instance = MockWeatherView.return_value

        # Mock aiohttp response
        mock_resp = AsyncMock(spec=aiohttp.ClientResponse)
        mock_resp.status = 200
        mock_resp.raise_for_status = MagicMock()
        sample_data = {
            "location": {"name": "TestCity", "country": "TestCountry"},
            "current": {
                "temp_c": 25,
                "feelslike_c": 26,
                "humidity": 60,
                "condition": {
                    "text": "Sunny",
                    "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                },
            },
        }

        async def json_func():
            return sample_data

        mock_resp.json = json_func

        # Patch the session's get method
        with patch.object(self.weather_cog.session, 'get') as mock_get:
            cm = MagicMock()
            cm.__aenter__ = AsyncMock(return_value=mock_resp)
            cm.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = cm

            await self.weather_cog.weather_command.callback(
                self.weather_cog, interaction, location="TestCity", units=None
            )

            interaction.response.defer.assert_called_once_with(ephemeral=False)

            expected_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}&q=TestCity"
            mock_get.assert_called_once_with(expected_url, timeout=10)

            MockWeatherView.assert_called_once_with(
                "TestCity", "metric", self.weather_cog
            )
            self.bot.add_view.assert_called_once_with(mock_weather_view_instance)
            interaction.followup.send.assert_called_once_with(
                embed=ANY, view=mock_weather_view_instance
            )

            sent_embed = interaction.followup.send.call_args.kwargs['embed']
            self.assertIsInstance(sent_embed, discord.Embed)
            self.assertEqual(sent_embed.title, "Weather in TestCity, TestCountry")


class TestWeatherView(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_weather_cog = AsyncMock(spec=WeatherCog)
        self.mock_weather_cog.session = AsyncMock(spec=aiohttp.ClientSession)

        # Mock WEATHERAPI_API_KEY and sanitize_url as they are used directly in the view
        # These are module-level, so patch them where they are looked up ('cogs.weather')
        self.weather_api_key_patch = patch(
            'cogs.weather.WEATHERAPI_API_KEY', "test_api_key"
        )
        self.sanitize_url_patch = patch(
            'cogs.weather.sanitize_url', side_effect=lambda x: x
        )  # simple pass-through

        self.mock_weather_api_key = self.weather_api_key_patch.start()
        self.mock_sanitize_url = self.sanitize_url_patch.start()

        self.location = "Testville"
        self.initial_units = "metric"

        # Patch uuid.uuid4 for predictable custom_id
        self.uuid_patch = patch(
            'cogs.weather.uuid.uuid4',
            return_value=uuid.UUID('abcdef12-abcd-1234-abcd-abcdef123456'),
        )
        self.mock_uuid = self.uuid_patch.start()

        self.view = WeatherView(
            self.location, self.initial_units, self.mock_weather_cog
        )

    async def asyncTearDown(self):
        self.uuid_patch.stop()
        self.weather_api_key_patch.stop()
        self.sanitize_url_patch.stop()

    async def test_on_toggle_units_metric_to_imperial(self):
        interaction = AsyncMock(spec=discord.Interaction)
        interaction.response = AsyncMock(spec=discord.InteractionResponse)
        interaction.message = AsyncMock(spec=discord.Message)
        interaction.followup = AsyncMock(spec=discord.Webhook)  # For error reporting

        # Mock aiohttp response for imperial units
        mock_resp_imperial = AsyncMock(spec=aiohttp.ClientResponse)
        mock_resp_imperial.status = 200
        mock_resp_imperial.raise_for_status = MagicMock()
        imperial_data = {
            "location": {"name": "Testville", "country": "Testland"},
            "current": {
                "temp_f": 77,
                "feelslike_f": 78,
                "humidity": 55,
                "condition": {
                    "text": "Cloudy",
                    "icon": "//cdn.weatherapi.com/weather/64x64/day/119.png",
                },
            },
        }

        async def imperial_json_func():
            return imperial_data

        mock_resp_imperial.json = imperial_json_func

        self.mock_weather_cog.session.get.return_value.__aenter__.return_value = (
            mock_resp_imperial
        )

        await self.view.on_toggle_units(interaction)

        interaction.response.defer.assert_called_once()

        expected_url = f"https://api.weatherapi.com/v1/current.json?key=test_api_key&q={self.location}"
        self.mock_weather_cog.session.get.assert_called_once_with(
            expected_url, timeout=10
        )

        interaction.message.edit.assert_called_once()
        call_kwargs = interaction.message.edit.call_args.kwargs
        self.assertIsInstance(call_kwargs['embed'], discord.Embed)
        self.assertEqual(call_kwargs['view'], self.view)

        self.assertEqual(self.view.current_units, "imperial")
        self.assertEqual(self.view.toggle_button.label, "Show in Civilized Units (°C)")

        edited_embed = call_kwargs['embed']
        self.assertEqual(edited_embed.title, "Weather in Testville, Testland")
        self.assertIn("77°F", edited_embed.fields[0].value)  # Temperature
        self.assertIn("Units: Imperial", edited_embed.footer.text)


if __name__ == '__main__':
    unittest.main()
