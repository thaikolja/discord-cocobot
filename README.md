# cocobot for Discord

A bot for the Discord Thailand-related server **Thailand — Official English-speaking community without trolls or spammers.** Features are added as needed. [Join us](https://discord.gg/DN52SxBpYJ)!

## Features

* `/translate <text> <to> <from>`: Translate a text into another language
  * `<text>`: The text to translate
  * `<to>`: The language as language code or name of the language to translate to, i.e., `de` / `german` for German, or `es` / `spanish` for Spanish
  * `<from>` (optional): If your `<text>` is **not** in English, specify your language here
* ``/languages`: Lists all available language codes

## Installation

**Note:** For installing it on your online server, follow these instructions *after* creating a user and group so that the user directory is created in `/home`

1. `git clone https://gitlab.com/thaikolja/discord-cocobot.git`
2. (Optional) Rename the directory to `cocobot`  using `mv discord-cocobot cocobot`
3. `cd cocobot`[^1]
4. Create a virtual environment via `python -m venv venv` (recommended)
5. Switch to the virtual environment with `source venv/bin/activate`[^2]
6. Install required modules via `pip install -r requirements.txt`
7. `touch .env && nano .env` to open environment file
8. Enter your [private bot token](https://www.writebots.com/discord-bot-token/) as `BOT_TOKEN="..."` and the [guild ID](https://cybrancee.com/learn/knowledge-base/how-to-find-a-discord-guild-id/) as `SERVER_ID=...`

## Usage

Please refer to [Discord's official documentation](https://discord.com/developers/docs/intro) on how to add a bot to your Discord server. This is required to get the `BOT_TOKEN` and the `SERVER_ID` environment variables.

### Locally

1. Follow the "Installation" steps and `cd` into the project's directory

1. Switch into your virtual environment via `source venv/bin/activate`
2. Start the script with `python bot.py`

**Note:** The bot will only be online as long as your process is running. Having it run on a server that is online 24/7 (server-side) is, obviously, the better solution.

### Server-Side

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

## Footnotes

[^1]: For these instructions, the directory will be `cocobot`
[^2]: To exit the virtual environment, run `deactivate`
