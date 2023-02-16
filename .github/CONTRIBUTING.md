# Contributing to BSEBot

Contributors are welcome!

BSEBot was first created as a bot for the **BSE** Discord server and as an excuse to play around with Discord and Python code. It's best to dive in and have a play with the codebase - there are some setup requirements below.

# Getting started

There's a form of documenation and an overview in the `docs/` directory but it is far from complete. It's written in mind for those new to this repository and with a bit but not loads of Python experience. [Start with the overview here](../docs/overview.md).

## Want to ask questions?
- Drop me a message on Discord: _ESloman#6969_
- [Join my bot testing server](https://discord.gg/R39Kw7gXSa)
- To see the BSEBot in action: [join the BSE server.](https://discord.gg/dGMPswqf49)


### Starting requirements
These are starting requirements that I assume you have met.
1. python 3.10+ installed (ideally *3.11* )
2. git installed
3. some kind of IDE installed
4. discord installed (and a discord account)
5. discord developer account (https://discord.com/developers)

### Setup
1. Clone the repo
2. Install the python requirements `pip install -r requirements.txt`
3. Create a `.env` file in the `discordbot` directory
4. Add the `DEBUG_MODE=1` line to `.env` file
5. Getting a bot token
   1. Go to https://discord.com/developers/applications
   2. Create a new application (name it whatever)
   3. Create a bot user for the application (name is something like BSEBot - %NAME%)
   4. Copy the token into the `.env` file `DISCORD_TOKEN=%YOUR_TOKEN_HERE%`
6. Install MongoDB (needs to be installed locally for testing)
7. Invite the bot you created to a discord server for testing - or invite to the [Sloman Server](https://discord.gg/R39Kw7gXSa).
8. Try to run 'main.py'!

You may need to add the `bsebot` repo to your pythonpath.

### Starting to contribute
- Make yourself a new branch - you won't have permissions to commit to `main` directly.
- Pick an issue from the list of issues (or create one if you have another idea of something you want to work on)
- Start work!