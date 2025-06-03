#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the condition that the above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2014-2025
#  Package:   cocobot Discord Bot

# Import the urllib.parse module for URL parsing and handling
import urllib.parse

# Import the openai module for interacting with OpenAI's API
import openai

# Import the google.generativeai module for interacting with Google's Generative AI
import google.generativeai as genai

# Import the GenerationConfig class from google.generativeai for configuring generation parameters
from google.generativeai import GenerationConfig

# Import the GenerationConfig class for configuring generation parameters
from openai.types.chat import ChatCompletionAssistantMessageParam

# Import the necessary API keys from the config module
from config.config import (
	GOOGLE_API_KEY,  # API key for Google services
	GROQ_API_KEY,  # API key for Groq services
	SAMBANOVA_API_KEY  # API key for Sambanova services
)


# Define a class named UseAI to handle interactions with various AI providers
class UseAI:
	"""
	A class to handle interactions with various AI providers.

	This class abstracts the complexity of different AI provider APIs,
	allowing for a unified interface to generate responses to prompts.
	"""

	# Define a list of available AI providers
	AVAILABLE_PROVIDERS = ['groq', 'google', 'sambanova']

	# Define the configuration for Google's generative AI model
	GOOGLE_GENERATION_CONFIG: GenerationConfig | dict[str, float | str | int] = {
		'temperature':        0.1,  # Controls randomness in generation
		'top_p':              0.2,  # Controls diversity of responses
		'top_k':              40,  # Limits the number of tokens considered
		'max_output_tokens':  500,  # Maximum length of the generated response
		'response_mime_type': 'text/plain',  # Format of the response
	}

	# Constructor method to initialize the UseAI instance with the specified provider
	def __init__(self, provider: str):
		"""
		Initialize the UseAI instance with the specified provider.

		Args:
						provider (str): The AI provider to use. Must be one of AVAILABLE_PROVIDERS.

		Raises:
						ValueError: If the provider is not supported.
		"""
		# Check if the provided provider is in the list of available providers
		if provider not in self.AVAILABLE_PROVIDERS:
			raise ValueError(f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}')

		# Assign the provider to the instance variable
		self.provider = provider

		# Initialize the appropriate client based on the provider
		if provider == 'groq':
			# Set up the OpenAI client for Groq with the specified API key and base URL
			self.client = openai.OpenAI(
				api_key=GROQ_API_KEY,
				base_url="https://api.groq.com/openai/v1"
			)
			# Set the model name for Groq
			self.model_name = "llama-3.3-70b-versatile"
		elif provider == 'sambanova':
			# Set up the OpenAI client for Sambanova with the specified API key and base URL
			self.client = openai.OpenAI(
				base_url='https://api.sambanova.ai/v1',
				api_key=SAMBANOVA_API_KEY,
			)
			# Set the model name for Sambanova
			self.model_name = 'Meta-Llama-3.3-70B-Instruct'
			self.temperature = 0.1

		elif provider == 'google':
			# Configure the Google Generative AI with the specified API key
			genai.configure(api_key=GOOGLE_API_KEY)
			# Set up the GenerativeModel for Google with the specified model name and configuration
			self.model = genai.GenerativeModel(
				model_name='gemma-3n-e4b-it',  # Old: "gemini-2.0-flash-exp",
				generation_config=self.GOOGLE_GENERATION_CONFIG,
			)

	# Method to send a prompt to the AI provider and get the response
	def prompt(self, prompt: str, strict: bool = True) -> str | None:
		"""
		Send a prompt to the AI provider and get the response.

		Args:
						prompt (str): The prompt to send to the AI.
						strict (bool): If True, instructs the AI to only return the result.

		Returns:
						str | None: The response from the AI, or None if there's an error.
		"""
		# Append instruction to the prompt if strict mode is enabled
		if strict:
			prompt = f"{prompt}. Only return the result, nothing else."

		# Handle the prompt based on the selected provider
		if self.provider in ('groq', 'gpt', 'sambanova'):
			return self._handle_openai(prompt)
		elif self.provider == 'google':
			return self._handle_google(prompt)

		return None

	# Helper method to handle OpenAI-based providers (Groq, Sambanova)
	def _handle_openai(self, prompt: str) -> str:
		"""
		Handle the prompt using OpenAI's API.

		Args:
						prompt (str): The prompt to send.

		Returns:
						str: The response from OpenAI.
		"""
		# Assign the prompt to the content variable
		content = prompt
		# Create a chat completion request with the specified messages and model
		chat = self.client.chat.completions.create(
			messages=ChatCompletionAssistantMessageParam[{
				"role":    "user",
				"content": content
			}],
			model=self.model_name,
		)
		# Return the content of the first choice's message
		return chat.choices[0].message.content

	# Helper method to handle Google's Generative AI
	def _handle_google(self, prompt: str) -> str:
		"""
		Handle the prompt using Google's Generative AI.

		Args:
						prompt (str): The prompt to send.

		Returns:
						str: The response from Google.
		"""
		# Start a new chat session with an empty history
		chat_session = self.model.start_chat(history=[])
		# Send the prompt message and get the response
		response = chat_session.send_message(prompt)
		# Return the stripped text of the response
		return response.text.strip()


# Function to sanitize a URL by encoding special characters
def sanitize_url(url: str) -> str:
	"""
	Sanitize a URL by encoding special characters.

	Args:
					url (str): The URL to sanitize.

	Returns:
					str: The sanitized URL.
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
			urllib.parse.quote(parsed.fragment, safe="")
		)
	)
