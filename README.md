# bsebot [![](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/esloman/bsebot/ci.yml?branch=main) ![GitHub issues](https://img.shields.io/github/issues-raw/esloman/bsebot) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/esloman/bsebot) ![GitHub contributors](https://img.shields.io/github/contributors/esloman/bsebot) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ESloman_bsebot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ESloman_bsebot) [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ESloman_bsebot&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ESloman_bsebot) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ESloman_bsebot&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ESloman_bsebot) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ESloman_bsebot&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ESloman_bsebot)

**`bsebot`** is a Discord bot that provides a user economy and betting system for a server. Users earn `eddies` (points) each day and can also create bets to spend their eddies on. The user with the highest amount of eddies is the **`KING`** of the server - the King gets a special role and earns taxes on other users' earnings.

Bot was originally created for the `BSE` server to fulfill a need to have something similar to _twitch predictions_ for placing bets on the server's games of Valorant. The bot has become a bit more generic and has other functions that are specific for the `BSE` server. The bot is capable of doing a `BSEddies awards` on a monthly or annual basis and also some server statistics.

# Features

- economy system (eddies)
- betting system
- daily wordle
- reminders

# Contributing

Contributions are welcome! See the [Contributing guide](.github/CONTRIBUTING.md). For contribution ideas:
- check the list of GitHub issues
- check the SonarCloud project for outstanding bugs/code smells/vulnerabilities
- additional unit tests to increase coverage (can check the SonarCloud project for weaknesses)
- refactoring/simplifying the code (a lot of functions are too complex and can be broken down)
- reducing duplication
- ensuring type hints are up to date/accurate
- ensuring that comments are accurate and contain the right type hints
- adding new features/functionality
- localisation (tbc)


# Building / running your own version

If you want run your own version of BSEBot - this is easy to do whether you want to containerise the process of run it just as.

## Requirements

You will need to have a version of `MongoDB` running - either another docker container or a local server. The bot expects there to be a
server running on localhost and the standard port that it can access.

I recommend also creating a `.env` file with the needed credentials.

The `.env` looks like this:

```bash
DISCORD_TOKEN="YOUR DISCORD BOT TOKEN"  # this is REQUIRED. Need a bot token to authenticate against Discord
GIPHY_API_KEY="API KEY FOR GIPHY"  # giphy api key if you want gif support
DEBUG_MODE=1  # whether you want to run in DEBUG mode or not
GITHUB_API_KEY="GITHUB API KEY"  # the github api key for doing Github things. Needs to have access to the `bsebot` repo.
```

## Docker

You can build the docker image with:

```bash
docker build -t bsebot:local .
```

This can then be run with:

```bash
docker run -d -v "/path/to/env/.env:/home/app/discordbot/.env" --name bsebot --network="host" --restart="always" bsebot:local
```

(Alternatively, you can change the image to `esloman/bsebot:latest` to pull the latest production image without having to build it yourself.)

Here, we mount the `.env` file to where the bot expects it. If you don't use a `.env` file, you will need to provide the environment variables.

## Docker Compose

Make sure to modify the volume bindings in `docker-compose.yml`.

```bash
docker-compose up -d
```

## Without Docker

I often run the bot locally when testing - but this can be done for production as well.

You will need to add the `bsebot` repo to your `PYTHONPATH` so that the code can find all the imports.
There should also be a `.env` file in `bsebot/discordbot` with the necessary credentials.

But it should be as simple as doing `python main.py` whilst in the `discordbot/` directory.

When I run through VSCode I have the following in my `launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "BSEbot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/discordbot/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "cwd": "${workspaceFolder}/discordbot",
        }
    ]
}
```
