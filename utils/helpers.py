# Import the urllib.parse module to work with URLs
import os
import urllib.parse
import openai
import google.generativeai as genai

from config.config import ERROR_MESSAGE
from config.config import GOOGLE_API_KEY
from config.config import GROQ_API_KEY
from config.config import OPENAI_API_KEY


class UseAI:
	AVAILABLE_PROVIDERS = ['groq', 'gpt', 'google']

	provider = str

	def __init__(self, provider: str):
		if provider not in self.AVAILABLE_PROVIDERS:
			raise ValueError(f'Invalid provider. Available providers: {self.AVAILABLE_PROVIDERS}')

		self.provider = provider

	def prompt(self, prompt: str, strict: bool = True):
		if strict:
			prompt = f"{prompt}. Only return the result, nothing else."

		if self.provider == 'groq':
			print(prompt)

			client = openai.OpenAI(
				base_url="https://api.groq.com/openai/v1",
				api_key=GROQ_API_KEY
			)

			chat = client.chat.completions.create(
				messages=[
					{
						"role":    "user",
						"content": prompt
					}
				],
				model="llama-3.3-70b-versatile",
			)

			return chat.choices[0].message.content

		elif self.provider == 'gpt':
			client = openai.OpenAI(
				api_key=OPENAI_API_KEY
			)

			chat = client.chat.completions.create(
				messages=[
					{
						"role":    "user",
						"content": prompt.strip()
					}
				],
				model="gpt-4o-mini",
			)

			return chat.choices[0].message.content
		elif self.provider == 'google':
			genai.configure(api_key=GOOGLE_API_KEY)

			generation_config: dict = {
				'temperature':        0.1,
				'top_p':              0.2,
				'top_k':              40,
				'max_output_tokens':  500,
				'response_mime_type': 'text/plain',
			}

			model = genai.GenerativeModel(
				model_name="gemini-2.0-flash-exp",
				generation_config=generation_config,
			)

			chat_session = model.start_chat(history=[])

			return chat_session.send_message(prompt).text.strip()
		else:
			return f"{ERROR_MESSAGE} Something's up with the API."


# Define a function to sanitize a URL
def sanitize_url(url):
	"""
	Sanitize a URL by encoding its components to ensure it is safe for use.

	Args:
			url (str): The URL to be sanitized.

	Returns:
			str: The sanitized URL with its components properly encoded.
	"""
	# Split the URL into its components (scheme, netloc, path, query, fragment)
	parsed = urllib.parse.urlsplit(url)

	# Encode each component of the URL to ensure it's safe
	sanitized = urllib.parse.urlunsplit((
		# The URL scheme (e.g., 'http', 'https')
		parsed.scheme,

		# The network location part (e.g., 'www.example.com')
		parsed.netloc,

		# Encode the path, allowing '/'
		urllib.parse.quote(parsed.path, safe="/"),

		# Encode the query string, allowing '=', '&', '?'
		urllib.parse.quote(parsed.query, safe="=&?"),

		# Encode the fragment identifier without any safe characters
		urllib.parse.quote(parsed.fragment, safe="")
	))

	# Return the sanitized URL
	return sanitized
