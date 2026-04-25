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
#  Date:      2014-2026
#  Package:   cocobot Discord Bot

# Import the urllib.parse module for URL parsing and handling
import urllib.parse
from typing import Final

import discord

# Import the google.genai module for interacting with Google's Generative AI
from google import genai

# Import the groq module for interacting with Groq's API
from groq import Groq

# Import the necessary API keys from the config module
from config.config import GEMINI_API_KEY  # API key for Google Gemini services
from config.config import GEMINI_MODEL  # API key for Google Gemini services
from config.config import GROQ_API_KEY  # API key for Groq services
from config.config import GROQ_MODEL  # API key for Groq services
from config.config import DEEPSEEK_API_KEY  # API key for DeepSeek services
from config.config import DEEPSEEK_MODEL  # Model name for DeepSeek


# Define a class named UseAI to handle interactions with various AI providers
class UseAI:
    """
    A class to handle interactions with various AI providers.

    This class abstracts the complexity of different AI provider APIs,
    allowing for a unified interface to generate responses to prompts.
    """

    # Define a list of available AI providers
    AVAILABLE_PROVIDERS = ['groq', 'gemini', 'deepseek']

    # Define the configuration for Google's generative AI model
    GOOGLE_GENERATION_CONFIG: dict[str, float | str | int] = {
        'temperature':        0.9,  # Controls randomness in generation
        'top_p':              0.7,  # Controls diversity of responses
        'top_k':              40,   # Limits the number of tokens considered
        'max_output_tokens':  2024,
        'response_mime_type': 'text/plain',  # Format of the response
    }

    # Constructor method to initialize the UseAI instance with the specified provider
    def __init__(self, provider: str):
        """
        Initializes an instance with a specified provider and sets up the appropriate client
        and model configuration based on the selected provider.

        Args:
            provider (str): The provider to use. Must be one of the available providers
                listed in the class attribute `AVAILABLE_PROVIDERS`.

        Raises:
            ValueError: If the provided provider is not in the list of available providers.
        """
        # Check if the provided provider is in the list of available providers
        if provider not in self.AVAILABLE_PROVIDERS:
            raise ValueError(
                f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}'
            )

        # Assign the provider to the instance variable
        self.provider = provider

        # Initialize the appropriate client based on the provider
        if provider == 'groq':
            # Set up the native Groq client with the specified API key
            self.client = Groq(api_key=GROQ_API_KEY)
            # Set the model name for Groq
            self.model_name = GROQ_MODEL
        elif provider == 'gemini':
            # Initialize the Google Generative AI client with the Gemini API key
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            # Set the model name for Google
            self.model_name = GEMINI_MODEL
        elif provider == 'deepseek':
            # DeepSeek uses an OpenAI-compatible API — use the groq SDK pattern via requests
            # We use the groq-compatible interface via the openai-compatible endpoint
            from openai import OpenAI as _OpenAI  # only imported when deepseek is used
            self.client = _OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url='https://api.deepseek.com/v1',
            )
            # Set the model name for DeepSeek
            self.model_name = DEEPSEEK_MODEL

    # Method to send a prompt to the AI provider and get the response
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
        # Append instruction to the prompt if strict mode is enabled
        if strict:
            prompt = f"{prompt}. Only return the result, nothing else."

        # Handle the prompt based on the selected provider
        if self.provider == 'groq':
            return self._handle_groq(prompt)
        elif self.provider == 'google':
            return self._handle_google(prompt)
        elif self.provider == 'deepseek':
            return self._handle_deepseek(prompt)

        return None

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
        # Create a chat completion request with the specified messages and model
        chat = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
        )
        # Return the content of the first choice's message
        return chat.choices[0].message.content

    def _handle_deepseek(self, prompt: str) -> str:
        """
        Handles communication with the DeepSeek API (OpenAI-compatible) to generate
        a chat completion response based on the provided prompt.

        Args:
            prompt (str): The input string to be passed to the DeepSeek API.

        Returns:
            str: The content of the first message choice returned by the DeepSeek API.
        """
        # Create a chat completion request using the OpenAI-compatible interface
        chat = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
        )
        # Return the content of the first choice's message
        return chat.choices[0].message.content

    # Helper method to handle Google's Generative AI
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
        # Generate content using the model with the specified configuration
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=self.GOOGLE_GENERATION_CONFIG['temperature'],
                top_p=self.GOOGLE_GENERATION_CONFIG['top_p'],
                top_k=self.GOOGLE_GENERATION_CONFIG['top_k'],
                max_output_tokens=self.GOOGLE_GENERATION_CONFIG['max_output_tokens'],
            )
        )
        # Return the stripped text of the response
        return response.text.strip()



# ---------------------------------------------------------------------------
# CHANNEL ID → LOCATION MAP  (takes priority over the name-based map below)
# ---------------------------------------------------------------------------
# Format:  <channel_id_as_int>: '<City Name>',
# Example: 1234567890123456789: 'Bangkok',
# ---------------------------------------------------------------------------
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
    'bangkok':          'Bangkok',
    'chiang-mai':       'Chiang Mai',
    'chon-buri':        'Chon Buri',
    'khon-kaen':        'Khon Kaen',
    'krabi':            'Krabi',
    'pattaya':          'Pattaya',
}


def resolve_channel_location(
    interaction: discord.Interaction, fallback: str = 'Bangkok'
) -> str:
    """Resolve a default city/location from the channel the interaction came from.

    Resolution order:
    1. ``CHANNEL_ID_LOCATION_MAP`` — exact channel ID match (highest priority).
    2. ``CHANNEL_LOCATION_DEFAULTS`` — channel *name* match (fallback).
    3. ``fallback`` — hardcoded default (lowest priority, default: Bangkok).
    """
    channel = interaction.channel
    channel_id: int | None = getattr(channel, 'id', None)

    # 1. ID-based lookup (priority)
    if channel_id is not None and channel_id in CHANNEL_ID_LOCATION_MAP:
        return CHANNEL_ID_LOCATION_MAP[channel_id]

    # 2. Name-based lookup (fallback)
    channel_name: str | None = getattr(channel, 'name', None)
    if channel_name is not None and channel_name in CHANNEL_LOCATION_DEFAULTS:
        return CHANNEL_LOCATION_DEFAULTS[channel_name]

    # 3. Final hardcoded default
    return fallback



# Function to sanitize a URL by encoding special characters
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
    # Parse the URL into its components
    parsed = urllib.parse.urlsplit(url)

    # Rebuild the URL with encoded components
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            urllib.parse.quote(parsed.path, safe="/"),
            urllib.parse.quote(parsed.query, safe="=&?"),
            urllib.parse.quote(parsed.fragment, safe=""),
        )
    )
