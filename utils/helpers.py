# Import the urllib.parse module to work with URLs
import urllib.parse


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
