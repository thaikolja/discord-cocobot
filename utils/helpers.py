#  Copyright (C) 2025 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thaikolja/discord-cocobot
#
#  This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
#  You are free to use, share, and adapt this work for non-commercial purposes, provided that you:
#  - Give appropriate credit to the original author.
#  - Provide a link to the license.
#  - Distribute your contributions under the same license.
#
#  For more information, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   CC BY-NC-SA 4.0
#  Date:      2014-2025
#  Package:   Thailand Discord

# Import the urllib.parse module for URL manipulation and parsing
import urllib.parse

# Import the openai module for interacting with OpenAI's API
import openai

# Import Google's generative AI module with a custom alias 'genai'
import google.generativeai as genai

# Import configuration constants from config.config module
from config.config import (
	GOOGLE_API_KEY,  # Google API key for authentication
	GROQ_API_KEY,  # Groq API key for authentication
	SAMBANOVA_API_KEY  # Sambanova API key for authentication
)

# Import urllib.parse module again (this is redundant as it was already imported)
import urllib.parse


# Define a class UseAI that handles different AI providers
class UseAI:
	# List of available AI providers that this class can work with
	AVAILABLE_PROVIDERS = ['groq', 'google', 'sambanova']

	# Configuration settings for Google's generative AI model
	GOOGLE_GENERATION_CONFIG: dict[str, float | str | int] = {
		'temperature':        0.1,  # Controls randomness in responses
		'top_p':              0.2,  # Controls diversity of responses
		'top_k':              40,  # Limits number of tokens considered
		'max_output_tokens':  500,  # Maximum length of generated response
		'response_mime_type': 'text/plain',  # Format of the response
	}

	# Constructor method that initializes the AI provider
	def __init__(self, provider: str):
		# Check if the provider is in the list of available providers
		if provider not in self.AVAILABLE_PROVIDERS:
			# Raise ValueError if provider is invalid
			raise ValueError(f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}')

		# Set the provider property based on input
		self.provider = provider

		if provider == 'groq':
			self.client = openai.OpenAI(
				api_key=GROQ_API_KEY,
				base_url="https://api.groq.com/openai/v1"
			)
			self.model_name = "llama-3.3-70b-versatile"
		# Configure client for GPT provider
		elif provider == 'sambanova':
			self.client = openai.OpenAI(
				base_url='https://api.sambanova.ai/v1/chat/completions',
				api_key=SAMBANOVA_API_KEY,
			)
			self.model_name = "Meta-Llama-3.1-8B-Instruct"
		# Configure client for Google provider
		elif provider == 'google':
			# Configure Google's generative AI with API key
			genai.configure(api_key=GOOGLE_API_KEY)
			# Initialize Google's generative model with specific configuration
			self.model = genai.GenerativeModel(
				model_name="gemini-2.0-flash-exp",
				generation_config=self.GOOGLE_GENERATION_CONFIG,
			)

	# Method to process a prompt and get response from AI model
	def prompt(self, prompt: str, strict: bool = True) -> str | None:
		# If strict mode is enabled, modify prompt to request only the result
		if strict:
			prompt = f"{prompt}. Only return the result, nothing else."

		# Handle the prompt based on the provider
		if self.provider in ('groq', 'gpt', 'sambanova'):
			# Use OpenAI's API handling for Groq and GPT providers
			return self._handle_openai(prompt)
		elif self.provider == 'google':
			# Use Google's API handling for Google provider
			return self._handle_google(prompt)

	# Private method to handle OpenAI API requests
	def _handle_openai(self, prompt: str) -> str:
		# For GPT provider, strip whitespace from prompt
		content = prompt
		# Create a chat completion request with the given prompt
		chat = self.client.chat.completions.create(
			messages=[{
				"role":    "user",
				"content": content
			}],
			model=self.model_name,
		)
		# Return the content of the first response from the model
		return chat.choices[0].message.content

	# Private method to handle Google's generative AI requests
	def _handle_google(self, prompt: str) -> str:
		# Start a new chat session with empty history
		chat_session = self.model.start_chat(history=[])
		# Send the prompt as a message in the chat session
		response = chat_session.send_message(prompt)
		# Return the stripped text response from Google's model
		return response.text.strip()


# Function to sanitize and normalize a URL
def sanitize_url(url: str) -> str:
	# Parse the input URL into its components
	parsed = urllib.parse.urlsplit(url)
	# Rebuild the URL with properly encoded components
	return urllib.parse.urlunsplit((
		parsed.scheme,  # URL scheme (e.g., http, https)
		parsed.netloc,  # Network location (e.g., www.example.com)
		urllib.parse.quote(parsed.path, safe="/"),  # Encoded path
		urllib.parse.quote(parsed.query, safe="=&?"),  # Encoded query string
		urllib.parse.quote(parsed.fragment, safe="")  # Encoded fragment
	))
