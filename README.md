# bsebot [![](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

![Discord](https://img.shields.io/badge/Discord-%237289DA.svg?style=for-the-badge&logo=discord&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) 


## Intro

The code repository for Best Summer Ever's Discord Server bot. This bot manages the 'BSEddies' (eddies) system of the server - a fictional system of 'points' that users can use to bet on different predictions. The system allows easy creation of these "bets".

## Eddies overview

Users earn `eddies` daily whilst interacting with the server. The users can use slash commands to create bets and then place bets on those bets with eddies. The user with the highest amount of eddies is the 'KING'! This means that they get a shiny gold name and a special role. The KING also taxes the working-class users and gains eddies off of bets and daily salaries. Every week, a 'revolution' event to overthrow the KING is triggered and users can chose to support or overthrow them.

## Bot Overview
The BSEBot is written in **Python** and is deployed via a Docker container that runs on an AWS EC2 instance.
The code can be run locally by running `discordbot/main.py` - assuming that a `.env` also exists in the the same directory. The `.env` file must have a `DISCORD_TOKEN` env and a `DEBUG_MODE=1` env.

When the bot is invited to a server, users can interact with it using slash commands. These commands allow users to view how many eddies they have, create bets, place eddies on bets, etc.