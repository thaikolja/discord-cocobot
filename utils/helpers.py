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

# Split URLs into bits so we can put them back together without inventing new holes
import urllib.parse

# Final maps: Kolja's way of saying "please don't mutate this at 3am"
from typing import Final

# Discord types, because slash commands don't come with a city name tattooed on them
import discord

# Gemini key from the shared config pile
from config.config import GEMINI_API_KEY  # API key for Google Gemini services

# Gemini model name, not a second key despite what the old comment claimed
from config.config import GEMINI_MODEL  # API key for Google Gemini services

# Groq key for the "please be fast" provider
from config.config import GROQ_API_KEY  # API key for Groq services

# Groq model string from env/config
from config.config import GROQ_MODEL  # API key for Groq services

# DeepSeek key for the OpenAI-shaped API
from config.config import DEEPSEEK_API_KEY  # API key for DeepSeek services

# DeepSeek model name
from config.config import DEEPSEEK_MODEL  # Model name for DeepSeek


# Inspector, please ignore that we hand SDKs around like hot potatoes
# noinspection PyTypeChecker
class UseAI:
    """
    A class to handle interactions with various AI providers.

    This class abstracts the complexity of different AI provider APIs,
    allowing for a unified interface to generate responses to prompts.
    """

    # The coconut's approved vendor list — no mystery startups
    AVAILABLE_PROVIDERS = ['groq', 'gemini', 'deepseek']

    # Gemini sampling knobs; temperature is deliberately not here unless a cog asks
    GOOGLE_GENERATION_CONFIG: dict[str, float | str | int] = {
        'top_p': 0.7,
        'top_k': 40,
        'max_output_tokens': 2024,
        'response_mime_type': 'text/plain',
    }

    # Wire up provider, keys, fallback, and the two special-case flags
    def __init__(
        self,
        provider: str,
        api_key: str | None = None,
        model: str | None = None,
        fallback_provider: str | None = None,
        fallback_api_key: str | None = None,
        fallback_model: str | None = None,
        temperature: float | None = None,
        disable_thinking: bool = False,
    ):
        """
        Initializes an instance with a specified provider and sets up the appropriate client
        and model configuration based on the selected provider.

        Args:
            provider (str): The provider to use. Must be one of the available providers
                listed in the class attribute `AVAILABLE_PROVIDERS`.
            api_key (str, optional): Custom API key for the provider.
            model (str, optional): Custom model name for the provider.
            fallback_provider (str, optional): Fallback provider to use in case of failure.
            fallback_api_key (str, optional): Custom API key for the fallback provider.
            fallback_model (str, optional): Custom model name for the fallback provider.

        Raises:
            ValueError: If the provided provider is not in the list of available providers.
        """
        # If someone typed "chatgpt" we politely refuse
        if provider not in self.AVAILABLE_PROVIDERS:
            raise ValueError(
                f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}'
            )

        # Remember which vendor we actually wanted
        self.provider = provider

        # Optional key override so tests don't raid production env
        self.api_key = api_key

        # Optional model override
        self.model_name = model

        # Fallback vendor must also be on the approved list
        if fallback_provider and fallback_provider not in self.AVAILABLE_PROVIDERS:
            raise ValueError(
                f'Invalid fallback provider. Available providers: {self.AVAILABLE_PROVIDERS}'
            )

        # Plan B provider name
        self.fallback_provider = fallback_provider

        # Plan B key
        self.fallback_api_key = fallback_api_key

        # Plan B model
        self.fallback_model = fallback_model

        # Temperature stays None unless transliterate (or a test) pins it
        self.temperature = temperature

        # Thinking-off is the same special-case flag — don't "helpfully" default it on
        self.disable_thinking = disable_thinking

        # Client is lazy so importing this module doesn't phone home
        self.client = None

        # First prompt() pays for SDK setup
        self._client_initialized = False

    # Build an SDK client without touching instance state
    @staticmethod
    def _init_client(provider: str, api_key: str | None = None, model: str | None = None):
        """Create a provider SDK client and resolve the model name.

        Args:
            provider: One of groq, gemini, or deepseek.
            api_key: Optional override for the shared env key.
            model: Optional override for the shared env model.

        Returns:
            Tuple of (client, model_name).

        Raises:
            ValueError: If the provider name is unknown.
        """
        # Groq path: OpenAI-ish but louder
        if provider == 'groq':
            from groq import Groq

            # Key from arg or the global Groq secret
            resolved_key = api_key or GROQ_API_KEY

            # Model from arg or config default
            resolved_model = model or GROQ_MODEL

            # Construct the Groq client
            client = Groq(api_key=resolved_key)

            # Hand both back so callers don't guess
            return client, resolved_model

        # Gemini path: Google's SDK, not the old generativeai package
        elif provider == 'gemini':
            from google import genai

            # Gemini key
            resolved_key = api_key or GEMINI_API_KEY

            # Gemini model id
            resolved_model = model or GEMINI_MODEL

            # Official genai Client
            client = genai.Client(api_key=resolved_key)

            # Same tuple shape as Groq
            return client, resolved_model

        # DeepSeek pretends to be OpenAI with a different base URL
        elif provider == 'deepseek':
            # DeepSeek key
            resolved_key = api_key or DEEPSEEK_API_KEY

            # DeepSeek model
            resolved_model = model or DEEPSEEK_MODEL

            # Local alias so we don't fight the openai package name
            from openai import OpenAI as _OpenAI

            # Point OpenAI SDK at DeepSeek's v1 host
            client = _OpenAI(
                api_key=resolved_key,
                base_url='https://api.deepseek.com/v1',
            )

            # Return the pair
            return client, resolved_model

        # If we got here, someone invented a fourth vendor
        raise ValueError(f"Unknown provider: {provider}")

    # Send a prompt and optionally fall back when the primary vendor ghosts us
    def prompt(self, prompt: str, strict: bool = True) -> str | None:
        """
        Generates and processes a response based on the provided prompt and provider.

        This function modifies the input prompt based on the strict flag and invokes the
        appropriate handler for the configured provider. If the provider is recognized,
        it processes the prompt and returns the response. For unrecognized providers,
        it returns None.

        Args:
            prompt (str): The input string used to generate a response.
            strict (bool, optional): If True, appends additional instructions to the
                prompt for stricter result formatting. Defaults to True.

        Returns:
            str | None: A processed string response from the provider, or None if the
                provider is not supported.
        """
        # Spin up the SDK only when someone actually asks a question
        if not self._client_initialized:
            self.client, self.model_name = self._init_client(self.provider, self.api_key, self.model_name)

            # Don't pay this tax twice
            self._client_initialized = True

        # Strict mode: "only the answer" because models love a preamble
        if strict:
            prompt = f"{prompt}. Only return the result, nothing else."

        # Primary provider first; fallback is for when the cloud has feelings
        try:
            # Groq handler
            if self.provider == 'groq':
                return self._handle_groq(prompt)

            # Gemini handler
            elif self.provider == 'gemini':
                return self._handle_google(prompt)

            # DeepSeek handler
            elif self.provider == 'deepseek':
                return self._handle_deepseek(prompt)

        except Exception as e:
            # Only retry if a fallback vendor was configured
            if self.fallback_provider:
                import logging

                # Discord logger so this shows up next to the rest of the drama
                logger = logging.getLogger('discord')

                # Warn before we swap identities
                logger.warning(
                    f"Primary provider '{self.provider}' failed: {e}. Retrying with fallback '{self.fallback_provider}'."
                )

                # Fallback attempt in its own try so we can log both failures
                try:
                    # Temporary client for the backup vendor
                    fallback_client, fallback_model = self._init_client(
                        self.fallback_provider, self.fallback_api_key, self.fallback_model
                    )

                    # Stash original identity so we can put the costume back
                    orig_provider = self.provider

                    # Stash original client
                    orig_client = self.client

                    # Stash original model
                    orig_model = self.model_name

                    # Pretend we were the fallback all along
                    self.provider = self.fallback_provider

                    # Swap client
                    self.client = fallback_client

                    # Swap model
                    self.model_name = fallback_model

                    # Dispatch using the swapped identity
                    try:
                        # Groq as fallback
                        if self.provider == 'groq':
                            return self._handle_groq(prompt)

                        # Gemini as fallback
                        elif self.provider == 'gemini':
                            return self._handle_google(prompt)

                        # DeepSeek as fallback
                        elif self.provider == 'deepseek':
                            return self._handle_deepseek(prompt)

                    finally:
                        # Restore primary provider name
                        self.provider = orig_provider

                        # Restore primary client
                        self.client = orig_client

                        # Restore primary model
                        self.model_name = orig_model

                except Exception as fallback_err:
                    # Both vendors failed; that's a bad day
                    logger.error(f"Fallback provider '{self.fallback_provider}' also failed: {fallback_err}")

                    # Re-raise the fallback error, not the original
                    raise fallback_err

            else:
                # No safety net: original exception goes out as-is
                raise e

        # Unknown provider after init — shouldn't happen, but None is honest
        return None

    # Groq chat completion
    def _handle_groq(self, prompt: str) -> str:
        """
        Handles communication with the Groq API to generate a chat completion response
        based on the provided prompt.

        Args:
            prompt (str): The input string to be passed to the Groq API for generating
            a response.

        Returns:
            str: The content of the first message choice returned by the Groq API.
        """
        # Minimal chat payload: one user message
        request = {
            'messages': [{"role": "user", "content": prompt}],
            'model': self.model_name,
        }

        # Only pin temperature when a caller asked — transliterate needs this
        if self.temperature is not None:
            request['temperature'] = self.temperature

        # Fire the completion
        chat = self.client.chat.completions.create(**request)

        # First choice text
        return chat.choices[0].message.content

    # DeepSeek is Groq's cousin with a different hostname
    def _handle_deepseek(self, prompt: str) -> str:
        """
        Handles communication with the DeepSeek API (OpenAI-compatible) to generate
        a chat completion response based on the provided prompt.

        Args:
            prompt (str): The input string to be passed to the DeepSeek API.

        Returns:
            str: The content of the first message choice returned by the DeepSeek API.
        """
        # Same shape as Groq so we don't grow a third request dialect
        request = {
            'messages': [{"role": "user", "content": prompt}],
            'model': self.model_name,
        }

        # Same temperature rule as Groq
        if self.temperature is not None:
            request['temperature'] = self.temperature

        # OpenAI-compatible create
        chat = self.client.chat.completions.create(**request)

        # First choice text
        return chat.choices[0].message.content

    # Gemini thinking-off config used only when disable_thinking is True
    def _gemini_thinking_config(self, genai_module):
        """Build ThinkingConfig to disable reasoning for transliterate only."""
        # Model id, lowercased so "2.5" matching isn't a coin flip
        model = (self.model_name or '').lower()

        # Shortcut to ThinkingConfig
        thinking = genai_module.types.ThinkingConfig

        # 2.5 models want a zero budget, not a poetry slam
        if '2.5' in model:
            return thinking(thinking_budget=0)

        # Everyone else: minimal thinking
        return thinking(thinking_level='minimal')

    # Gemini generate_content path
    def _handle_google(self, prompt: str) -> str:
        """
        Handles the generation of content using Google's language model.

        This method utilizes a specified language model and configuration to generate content based on the provided prompt.
        The method interacts with the client to fetch the generated content and returns the processed response.

        Args:
            prompt (str): The input prompt that will be used to generate content.

        Returns:
            str: The stripped text response generated by the model.
        """
        # Need types for GenerateContentConfig
        from google import genai

        # Shared Gemini knobs; temperature stays off this dict unless a cog asked for it
        config_kwargs: dict = {
            'top_p': self.GOOGLE_GENERATION_CONFIG['top_p'],
            'top_k': self.GOOGLE_GENERATION_CONFIG['top_k'],
            'max_output_tokens': self.GOOGLE_GENERATION_CONFIG['max_output_tokens'],
        }

        # Transliterate is the only command that pins temperature (zero, like a monk's dinner)
        if self.temperature is not None:
            config_kwargs['temperature'] = self.temperature

        # Same deal for thinking: only transliterate asks the model not to philosophize
        if self.disable_thinking:
            config_kwargs['thinking_config'] = self._gemini_thinking_config(genai)

        # Actual Gemini call
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(**config_kwargs),
        )

        # Strip whitespace so Discord doesn't get a blank haiku
        return response.text.strip()


# ---------------------------------------------------------------------------
# CHANNEL ID → LOCATION MAP  (takes priority over the name-based map below)
# ---------------------------------------------------------------------------
# Format:  <channel_id_as_int>: '<City Name>',
# Example: 1234567890123456789: 'Bangkok',
# ---------------------------------------------------------------------------
# Snowflake IDs beat channel names because people rename channels for fun
CHANNEL_ID_LOCATION_MAP: Final[dict[int, str]] = {
    1148765003005042719: 'Bangkok',
    1148765027873083392: 'Chiang Mai',
    1148765313891041392: 'Chon Buri',
    1148765077797863464: 'Khon Kaen',
    1241487264735821844: 'Krabi',
    1148765044688039986: 'Pattaya',
}

# Name-based fallback map (used when a channel ID is not listed above)
CHANNEL_LOCATION_DEFAULTS: Final[dict[str, str]] = {
    'bangkok': 'Bangkok',
    'chiang-mai': 'Chiang Mai',
    'chon-buri': 'Chon Buri',
    'khon-kaen': 'Khon Kaen',
    'krabi': 'Krabi',
    'pattaya': 'Pattaya',
}


# Guess the city from the Discord channel the slash command landed in
def resolve_channel_location(
    interaction: discord.Interaction, fallback: str = 'Bangkok'
) -> str:
    """Resolve a default city/location from the channel the interaction came from.

    Resolution order:
    1. ``CHANNEL_ID_LOCATION_MAP`` — exact channel ID match (highest priority).
    2. ``CHANNEL_LOCATION_DEFAULTS`` — channel *name* match (fallback).
    3. ``fallback`` — hardcoded default (lowest priority, default: Bangkok).
    """
    # Channel object, which might be a thread, DM, or a fever dream
    channel = interaction.channel

    # Snowflake if Discord gave us one
    channel_id: int | None = getattr(channel, 'id', None)

    # 1. ID-based lookup (priority)
    if channel_id is not None and channel_id in CHANNEL_ID_LOCATION_MAP:
        return CHANNEL_ID_LOCATION_MAP[channel_id]

    # Channel name for the second-best map
    channel_name: str | None = getattr(channel, 'name', None)

    # 2. Name-based lookup (fallback)
    if channel_name is not None and channel_name in CHANNEL_LOCATION_DEFAULTS:
        return CHANNEL_LOCATION_DEFAULTS[channel_name]

    # 3. Final hardcoded default
    return fallback


# Encode URL pieces so Thai city names don't explode query strings
def sanitize_url(url: str) -> str:
    """
    Sanitizes the provided URL by ensuring all parts of the URL are properly encoded.

    This function ensures that any special or reserved characters in the URL's path,
    query, or fragment components are safely encoded to prevent potential issues
    with improper URL formatting or injection vulnerabilities.

    Args:
        url (str): The URL to sanitize.

    Returns:
        str: The sanitized and properly encoded URL.
    """
    # Split into scheme/netloc/path/query/fragment
    parsed = urllib.parse.urlsplit(url)

    # Put it back together with quoted path/query/fragment
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            urllib.parse.quote(parsed.path, safe="/"),
            urllib.parse.quote(parsed.query, safe="=&?"),
            urllib.parse.quote(parsed.fragment, safe=""),
        )
    )
