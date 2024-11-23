# 🥥 `@cocobot` for Discord

![GitLab Release](https://img.shields.io/gitlab/v/release/thaikolja%2Fdiscord-cocobot) ![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/thaikolja%2Fdiscord-cocobot) ![GitLab Last Commit](https://img.shields.io/gitlab/last-commit/thaikolja%2Fdiscord-cocobot)

A custom written in Python for the Thailand-related Discord server **Thailand Discord - The English-speaking Thailand community without trolls or spammers.** Features are added as needed. Feel free to [join us](https://discord.gg/DN52SxBpYJ) or help make `@cocobot` even better!

**Table of Contents**

[TOC]

## Features

`@cocobot` is being continuously being developed. Here is an overview of what it can do. Any contribution by [forking the code](https://gitlab.com/thaikolja/discord-cocobot/-/forks/new) and creating pull requests is highly welcome. Scroll down to the "Contribute" section to learn how—it's easy, don't worry!

### Functions

* `/learn`: Helps you extend your Thai vocabulary by randomly displaying one of the 150 most commonly used words in the English language and translating them into Thai, in Thai script, and [transliterated](https://simple.wikipedia.org/wiki/Transliteration).
* `/translate <text> <language>`: Translate a text into another language
  * `<text>`: The text to translate
  * `<language>`: The language as language code or name of the language to translate to, i.e., `de` / `german` for German, or `es` / `spanish` for Spanish
* `/languages`: Lists all available language codes
* `/weather <location>`: Display the current weather in a city or country.
  * `<location>`  (optional): The specified location. **Default:** Bangkok
* `/time <location>`: Show the current time in a certain location
  * `<location>`: City, country, or both of the location
* `/exchangerate <from_currency> <to_currency> <amount>`: Display the up-to-date exchange rate of two currencies.
  * `<from_currency>` (optional): Three-character abbreviation for a currency according to [ISO 4217 standards](https://www.iban.com/currency-codes). **Default:** `USD`
  * `<to_currency>` (optional): Three-character abbreviation for a currency according to [ISO 4217 standards](https://www.iban.com/currency-codes). **Default:** `THB`
  * `<amount>` (optional): The amount used to convert the currencies. **Default:** `1`  

### Automation

* `@cocobot`: Mentioning this bot by its user name will display an introduction message and ask users to [contribute to `@cocobot` via GitLab](https://gitlab.com/thaikolja/discord-cocobot)
* `tate`: Displays [a .gif of Bottom G dancing](https://media1.tenor.com/m/fyrqnSBR4gcAAAAd/bottom-g-andrew-tate.gif) whenever the standalone word "Tate" for Andrew Tate is typed (case-insensitive), with a cool-off time of `30` minutes.

## Installation

**Note:** To install it on your **online** server, follow these instructions *after* creating a user and group so that the (example) paths used in this documentation are valid.

1. `git clone https://gitlab.com/thaikolja/discord-cocobot.git`
2. (Optional) Rename the directory to `cocobot`  using `mv discord-cocobot cocobot`
3. `cd cocobot`[^1]
4. Duplicate and rename the file `.env.example` to `.env` and fill out the required variables (e.g., `cp .env.example .env && nano .env`)
5. Create a virtual environment via `python -m venv venv` (recommended)
6. Switch to the virtual environment with `source venv/bin/activate`[^2]
7. Install required modules via `pip install -r requirements.txt`
8. `touch .env && nano .env` to open environment file
9. Add and replace the values of the following environmental variables:
   1. `BOT_TOKEN`
   2. `SERVER_ID`
   3. `LOCALTIME_API_KEY`  ([Sign up to geoapify.com](https://myprojects.geoapify.com/login) for a free API key)
   4. `WEATHERAPI_API_KEY` ([Register on weatherapi.com](https://www.weatherapi.com/signup.aspx) for free to get an API key) 
   5. `CURRENCYAPI_API_KEY` ([Register on currencyapi.com](https://app.currencyapi.com/register) to get a free API key for 300 calls/month)

## Usage

Please refer to [Discord's official documentation](https://discord.com/developers/docs/intro) on how to add a bot to your Discord server. This is required to get the `BOT_TOKEN` and the `SERVER_ID` environment variables. Register on other websites specified in installation step #8 to obtain a free API key.

### Locally

1. Follow the "Installation" steps and `cd` into the project's directory

1. Switch into your virtual environment via `source venv/bin/activate`
2. Start the script with `python bot.py`

**Note:** The bot will only be online as long as your process is running. Having it run on a server that is online 24/7 (server-side) is, obviously, the better solution.

### Server-Side

Again, make sure to **skip** the installation section until you've arrived at **step 3**, otherwise the paths in this documentation will be invalid.

1. Create a user and group the bot will be run as, for example:

   ```bash
   sudo useradd -M bots # You'll be asked for a password after this
   sudo groupadd bot
   ```

2. Assign the user to the group via `sudo usermod -a -G bots bot`

3. Follow the "Installation" instructions above

4. To run the bot in the background, [create it as a service](https://medium.com/@swinarah/create-background-service-in-linux-ed29583a5b9d) inside `/etc/systemd/system/`, for example, `cocobot.service`

5. Make sure your service file looks similar to this, depending on the directories, user, and group name:

   `````bash
   # /etc/systemd/system/cocobot.service
   
   [Unit]
   Description=Discord Cocobot
   After=network.target
   
   [Service]
   ExecStart=/home/bots/cocobot/venv/bin/python /home/bots/cocobot/bot.py
   WorkingDirectory=/home/bots/cocobot
   Restart=no # Change this to "always" if you want it to restart on failure
   User=bots
   Group=bot
   EnvironmentFile=/home/bots/cocobot/.env # Important
   
   [Install]
   WantedBy=multi-user.target
   `````

6. Reload the services registry via `systemctl daemon-reload`

7. Finally, start your bot using the actual service name file:

   ```````bash
   sudo systemctl start cocobot.service
   sudo systemctl enable cocobot.service

7. (Optional) To check the status, run `sudo systemctl status cocobot.service`

## Authors

* **Kolja Nolte** / [thaikolja](https://gitlab.com/thaikolja/) \<kolja.nolte@gmail.com\>

## Contribute

**We welcome contributions of any kind to enhance our Discord server!**

To get involved and make `@cocobot` even better, you can either [browse existing tickets](https://gitlab.com/thaikolja/discord-cocobot/-/issues) or contribute [actual code](https://gitlab.com/thaikolja/discord-cocobot) with features you find useful and match our server profile. *DigitalOcean* has [a very thorough article](https://www.digitalocean.com/resources/articles/how-to-contribute-to-open-source#the-process-for-submitting-your-open-source-contributions) on how this works on the technical side in case you're new to open-source software.

For a detailed guide on how to contribute, please see the [CONTRIBUTING.md](./) file.

## License

Our Discord server's content is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license. This allows you to share, copy, and adapt the material for any purpose, provided you give appropriate credit. For full details on usage rights and obligations, please refer to the [LICENSE](https://gitlab.com/thaikolja/discord-cocobot/-/blob/main/LICENSE?ref_type=heads) file.

[^1]: For these instructions, the directory will be `cocobot`
[^2]: To exit the virtual environment, run `deactivate`
