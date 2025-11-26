# 🥥 cocobot

![GitLab Release](https://img.shields.io/gitlab/v/release/thaikolja%2Fdiscord-cocobot?style=flat&label=version&color=%23d87630&link=https%3A%2F%2Fgitlab.com%2Fthaikolja%2Fdiscord-cocobot) [![pipeline status](https://gitlab.com/thailand-discord/bots/cocobot/badges/main/pipeline.svg)](https://gitlab.com/thailand-discord/bots/cocobot/-/commits/main) ![GitLab License](https://img.shields.io/gitlab/license/thailand-discord%2Fbots%2Fcocobot?style=flat) [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**@cocobot** is your friendly, feature-rich **Discord bot** designed for the [**Discord Thailand** server](https://discord.gg/6JXCqVdmTZ), bringing a tropical twist to your server with useful utilities and fun interactions. Built with **Python** and the `discord.py` library, cocobot offers **a variety of commands** for practical tasks like weather checking, translation, and currency conversion, all wrapped in a coconut-themed package.

![GitHub Repository Banner](https://p.ipic.vip/7kz50a.jpg)

## 📖 Documentation

For detailed information about installation, configuration, and usage, please check our comprehensive documentation in the [`docs/`](docs/) directory:

- **[Getting Started](docs/README.md)** - Complete setup guide and feature overview
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development setup and contribution guide
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Technical API reference
- **[Deployment Guides](docs/)**
  - [Development](docs/DEPLOYMENT_DEVELOPMENT.md)
  - [Production](docs/DEPLOYMENT_PRODUCTION.md)
  - [Docker](docs/DEPLOYMENT_DOCKER.md)
- **[Architecture](docs/ARCHITECTURE.md)** - System design and technical architecture
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Security](docs/SECURITY.md)** - Security policy and best practices
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## 🌟 Features

- **🌤️ Weather** - Get current weather conditions for any location
- **🕓 Time** - Check the local time in any city or country  
- **💱 Exchange Rates** - Convert between currencies with up-to-date rates
- **🌫️ Pollution** - Check the air quality index (AQI) for any city
- **🔤 Transliteration** - Convert Thai text to Latin script
- **💡 Learn** - Shows Thai words with translations and transliterations
- **🌐 Translation** - Translate text between languages using AI

## 🚀 CI/CD Pipeline

cocobot features an automated CI/CD pipeline that:
- Runs tests on every push
- Automatically deploys to production when changes are merged to the `main` branch
- Stops previous containers, rebuilds with new code, and starts the updated version
- Includes health checks and status reporting

For setup instructions, see the [Production Deployment Guide](docs/DEPLOYMENT_PRODUCTION.md).

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://gitlab.com/thailand-discord/bots/cocobot.git
   cd cocobot
   ```

2. **Set up the environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token and API keys
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

For detailed installation instructions, see the [full documentation](docs/README.md).

## 🧑‍💻 Authors and Contributors

* **Kolja Nolte** (kolja.nolte@gmail.com)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

**cocobot** is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

**cocobot** was created by Kolja Nolte and is maintained by the Thailand Discord community. Special thanks to:

- The `discord.py` team for their excellent library
- All API and AI providers for their services
- [August Engelhardt](https://en.wikipedia.org/wiki/August_Engelhardt) for inspiration

---

For complete documentation, visit the [`docs/`](docs/) directory. 🥥