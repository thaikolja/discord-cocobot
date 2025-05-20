# Changelog

## v2.3.0

* **Improved** @cocobot's `/weather` command: You can now toggle between Fahrenheit and Celsius with a simple button underneath the weather card.
* **Fixed** several smaller issues to adhere to Python's best practices.
* Added `on.sh`, `off.sh`, and `deploy.sh` to `.gitignore` since they

## v2.2.1

### General Updates

* **Version Increment:** Upgraded version in `bot.py` from **2.2.0** to **2.2.1**.
* **Header Updates:** Added comprehensive copyright and licensing info in `bot.py`.

### Transliteration Command

* **Prompt Enhancement:** Improved the AI prompt for clearer instructions and better transliteration accuracy.
* **Input Validation:** Added checks for empty or whitespace-only inputs with informative messages.
* **Logging & Error Handling:** Enhanced exception handling and logging in the `transliterate` cog to better track AI service issues.

### Weather Command

* **Asynchronous Requests:** Switched from `requests` to `aiohttp` for non-blocking HTTP calls.
* **Robust Error Management:** Introduced detailed error handling (HTTP errors, timeouts, client errors) with user-friendly messages.
* **Rich Embeds:** Weather details are now presented in Discord embeds with thumbnails, fields (temperature, feels-like, humidity), and timestamps.

### Testing Updates

* **Test Adjustments:** Updated unit tests for the transliteration functionality to match new response formats and error cases.
* **Mock Enhancements:** Refined mocks for Discord interactions and AI responses.

### AI Helper Modifications

* **Model Update:** Changed AI model in `utils/helpers.py` from `gemini-2.0-flash-lite` to `gemini-2.0-flash-exp` for enhanced performance.

## v2.2.0

* **Fixed:** Bug

## v2.0.1

* **Added:** `/learn` command

## v2.0.0

* cocobot v2 is a completely rewritten version of the initial cocobot Discord bot for the Thailand Discord server. At this point, all features from the first, less maintainable version have been reprogrammed in a way that allows other contributors to add functions easily. Already existing functions have been drastically improved; the output quality is at the highest rate so far.

## v1.2.4

* Added trigger that lets @cocobot introduce itself once its username is mentioned
* Added `/assets/cocobot-introduction.md` file for the introduction message
* Added and updated `LICENSE`, `CHANGELOG`, `CONTRIBUTING`, and `README.md` files
* Fixed non-responding `tate` trigger bug
* Changed `/learn` to import the words on bot initialization instead of on every command
* Changed license from `MIT` to `CC BY 4.0` for easier forking and sharing

## v1.2.3

* This version contains the new slash command `/learn`. Read more about this in the `README.md` file.

## v1.2.2

* Added `last_triggered` dictionary to track user trigger times
* Used `time` module alias `std_time` to handle time functions
* Improved error handling for the translation command

## v1.2.1

* Removed API-key exposing error exceptions.
* Changed structure of two environmental variables (!)
* Changed error messages.
* Added `on.sh` script for internal use.
* Added `off.sh` script for internal use.

## v1.2.0

### The new features include:

* `/exchangerate <from_currency> <to_currency> <amount>`: Displays the current exchange rate between two currencies.
* `/weather <location>`: Displays the current weather in a specified location.
* `/time <location>`: Displays the current time in a specified location.

### The code improvements include:

* Added inline code documentation and comments to improve readability and maintainability.
* Improved error handling to provide more informative error messages.
* Improved code organization and structure to make it easier to read and understand.

### Changes:

* Added new features to the Discord bot.
* Improved code quality by adding inline code documentation and comments.
* Improved error handling to provide more informative error messages.
* Improved code organization and structure to make it easier to read and understand.

## v1.1.0

* This version introduces a new function. The slash command \`/weather <location>\` displays the current weather and conditions at a specified location (defaults to Bangkok).

## v1.0.0

* The first working version of **cocobot**, a custom Discord bot for the "Thailand - Official" server. Current functions are limited to `/translate` and `/languages`. Read README.md for instructions.
