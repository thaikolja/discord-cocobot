# cocobot for Discord

A bot for the Discord Thailand-related server **Thailand — Official English-speaking community without trolls or spammers.** Features are added as needed. [Join us](https://discord.gg/DN52SxBpYJ)!

## Features

* `/translate <text> <language>`: Translate a text into another language
  * `<text>`: The text to translate
  * `<language>`: The language as language code or name of the language to translate to, i.e., `de` / `german` for German, or `es` / `spanish` for Spanish
* `/languages`: Lists all available language codes
* `/weather <location>`: Display the current weather in a city or country.
  * `<location>`  (optional): The specified location. **Default:** Bangkok

* `/time <location>`: Show the current time in a certain location
  * `<location>`: City, country, or both of the location


## Installation

**Note:** For installing it on your **online** server, follow these instructions *after* creating a user and group so that the (example) paths used in this documentation are valid.

1. `git clone https://gitlab.com/thaikolja/discord-cocobot.git`
2. (Optional) Rename the directory to `cocobot`  using `mv discord-cocobot cocobot`
3. `cd cocobot`[^1]
4. Create a virtual environment via `python -m venv venv` (recommended)
5. Switch to the virtual environment with `source venv/bin/activate`[^2]
6. Install required modules via `pip install -r requirements.txt`
7. `touch .env && nano .env` to open environment file
8. Add and replace the values of the following environmental variables:
   1. `BOT_TOKEN=abc`
   2. `SERVER_ID=123`
   3. `LOCALTIME_API_KEY=abc`  ([Sign up to geoapify.com](https://myprojects.geoapify.com/login) for a free API key)
   4. `WEATHERAPI_API_KEY=123abc` ([Register on weatherapi.com](https://www.weatherapi.com/signup.aspx) for free to get an API key) 

## Usage

Please refer to [Discord's official documentation](https://discord.com/developers/docs/intro) on how to add a bot to your Discord server. This is required to get the `BOT_TOKEN` and the `SERVER_ID` environment variables. [Sign up to geoapify.com](https://myprojects.geoapify.com/login) for a free API key required for the `/time` command.

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

[^1]: For these instructions, the directory will be `cocobot`
[^2]: To exit the virtual environment, run `deactivate`
