import urllib.parse
import openai
import google.generativeai as genai
from config.config import (
	ERROR_MESSAGE,  # Import a predefined error message constant
	GOOGLE_API_KEY,  # Import Google API key from config
	GROQ_API_KEY,  # Import Groq API key from config
	OPENAI_API_KEY  # Import OpenAI API key from config
)


class UseAI:
	# A list of available AI providers
	AVAILABLE_PROVIDERS = ['groq', 'gpt', 'google']

	# Configuration settings specific to Google's AI model generation
	GOOGLE_GENERATION_CONFIG = {
		'temperature':        0.1,
		'top_p':              0.2,
		'top_k':              40,
		'max_output_tokens':  500,
		'response_mime_type': 'text/plain',
	}

	def __init__(self, provider: str):
		# Constructor that initializes the AI provider based on the input
		if provider not in self.AVAILABLE_PROVIDERS:
			raise ValueError(f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}')

		self.provider = provider  # Set the provider based on input

		if provider == 'groq':
			# Configuring OpenAI client for Groq with specific API endpoint and key

			self.client = openai.OpenAI(
				base_url="https://api.groq.com/openai/v1",
				api_key=GROQ_API_KEY
			)

			self.model_name = "llama3-70b-8192"  # Set model name for Groq
		elif provider == 'gpt':
			# Configuring OpenAI client for GPT with the standard API key
			self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
			self.model_name = "gpt-4o-mini"  # Set model name for GPT
		elif provider == 'google':
			# Configure Google's generative AI settings
			genai.configure(api_key=GOOGLE_API_KEY)
			self.model = genai.GenerativeModel(
				model_name="gemini-1.5-flash",
				generation_config=self.GOOGLE_GENERATION_CONFIG,
			)

	def prompt(self, prompt: str, strict: bool = True) -> str:
		# Process a prompt to get a response from the configured AI model
		if strict:
			prompt = f"{prompt}. Only return the result, nothing else."  # Modify prompt if strict condition is True

		if self.provider in ('groq', 'gpt'):
			return self._handle_openai(prompt)  # Handle prompt via OpenAI models
		elif self.provider == 'google':
			return self._handle_google(prompt)  # Handle prompt via Google's AI model

	def _handle_openai(self, prompt: str) -> str:
		# Private method to handle requests to OpenAI models
		content = prompt.strip() if self.provider == 'gpt' else prompt  # Strip prompt for GPT provider
		chat = self.client.chat.completions.create(
			messages=[{
				"role":    "user",
				"content": content
			}],
			model=self.model_name,
		)
		return chat.choices[0].message.content  # Return the content of the response from the model

	def _handle_google(self, prompt: str) -> str:
		# Private method to handle requests to Google's AI model
		chat_session = self.model.start_chat(history=[])  # Start a new chat session
		response = chat_session.send_message(prompt)  # Send the prompt as a message
		return response.text.strip()  # Return the stripped text of the response


def sanitize_url(url: str) -> str:
	"""Sanitize a URL by encoding its components to ensure it's safe for use."""
	parsed = urllib.parse.urlsplit(url)  # Split the URL into components

	return urllib.parse.urlunsplit((
		parsed.scheme,  # Scheme of the URL (e.g., http)
		parsed.netloc,  # Network location part of the URL
		urllib.parse.quote(parsed.path, safe="/"),  # Encode path, preserving slashes
		urllib.parse.quote(parsed.query, safe="=&?"),  # Encode query, preserving '=', '&', and '?'
		urllib.parse.quote(parsed.fragment, safe="")  # Encode fragment part of the URL
	))
