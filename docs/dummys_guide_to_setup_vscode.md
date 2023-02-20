# A dummy's guide to setting up with VSCode

This is a step by step walkthrough for setting up everything you need for local bot development with Visual Studio Code.

## Step One: Installing VS Code

[Visual studio code can be downloaded from here](https://code.visualstudio.com/).

## Step Two: Install git 

[Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Step Three: Install python

Most of the code is written in `Python`. It will need to be installed if you want to run anything. `Python 3.10` is the minimum requirement; there's some [pattern matching](https://peps.python.org/pep-0636/) in parts and that only became available in `Python 3.10`. `3.11` is recommended, as it comes with various performance enhancements and it's what the application Docker image is built with.

- [Article on installing python on different devices](https://realpython.com/installing-python/)
- [Python downloads](https://www.python.org/downloads/)

## Step Four: Cloning the repo

You _can_ clone the repo via the CLI or via a git GUI tool. But you can also do it via VS Code if you already installed git.

To do the latter;

We need to install an extension first though:
- Open the Extensions tab on the left (**Control**, **Shift**, and **X**.)
- Search "github"
- Install `Github Pull Requests and Issues` extension

- Press **Control**, **Shift**, and **P**.
- Enter "git clone" and select the **Git: Clone** command.
- Select **Clone from GitHub**.
- This _should_ take you through a workflow to authorise VSCode with GitHub.
- Once you're back in VSCode, you should see a list of repos that you have access to and you can search.
- Search/select `ESloman/bsebot` and then select where you want to clone it.
- Open the repo when prompted.

You now have the repo installed locally!

## Step Five: Resolving autocomplete paths

Sometimes, VSCode autocomplete struggles with working out Python paths and other things so we can help it with a couple of simple files. Make sure to also select an interpreter; press **Control**, **Shift**, and **P**. Search `python select` and click `Python: Select Interpreter` and select the Python version.


In the root of the repo, create a folder called `.vscode`. And then create three new files:
- `.env`
- `launch.json`
- `settings.json`

### .env

`.env` should look something like this:

```
PYTHONPATH=PATH\TO\THE\REPO\bsebot
```

Should simply contains the PYTHONPATH env with the value being the path to the repo root.

### launch.json

This file contains the VSCode launch configuration for running/testing the bot.

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "BSEBot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/discordbot/main.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "cwd": "${workspaceFolder}/discordbot"
        }
    ]
}
```

### settings.json

This is your settings file for repo settings. Here we're telling VSCode where to find our Python `.env` file. We can also add in `python.autoComplete.extraPaths` and `python.analysis.extraPaths` to give VSCode extra hints for autocomplete. The latter two are optional, but if you have issues then add those in.

```json
{
    "python.autoComplete.extraPaths": [
        "PATH\\TO\\PYTHON\\INSTALL\\LOCATION",
        "\\PATH\\TO\\PYTHON\\PACKAGES"
    ],
    "python.analysis.extraPaths": [
        "PATH\\TO\\PYTHON\\INSTALL\\LOCATION",
        "\\PATH\\TO\\PYTHON\\PACKAGES"
    ],
    "python.envFile": "${workspaceFolder}/.vscode/.env"
}
```

## Step Six: Installing Python requirementts

Open up a terminal and navigate to the bsebot repo. Run `pip install -r requirements.txt`. This will install all the dependencies that the bot requires.

# 

_If you're not interested in **running** the bot then you can stop here_. This is enough to peruse the code with all the dependencies installed.

#

## Step Seven: First attempt at running

Head over to the "Run and Debug" tab. You _should_, if you did above, have a "BSEBot" configuration you can run simply by clicking play. (If you don't, go back and do **Step Five**.)

When you click play, if everything is setup okay, you should get some messages that keys weren't found in a `.env` file and then the program should exit. This is normal and a good sign!

## Step Eight: Discord Bot token

In order to run/debug/test the bot locally; we'll need a bot token so we can actually login to Discord. Naturally, I'm not going to give out BSEBot's _actual_ token; so you'll need to create a new application and a new bot.

Head over to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application. And then create a new bot and copy the token.

IF you're in the **BSEBot Team** Discord Developer team then there's a couple of applications with bots in that can be "claimed" by adding your name to it. They've already been invited to the BSEBot Test Server. Simply click on one of them, go to "Bot" and then reset the token. Then **copy** the token.

## Step Eight: The `.env` file

We need a `.env` file for our own Discord bot token so the bot can auth correctly.

Create a `.env` file in the `discordbot/` directory. It should have two lines:

```bash
DISCORD_TOKEN="MTAzHjkbFAkeHTA69FakeODtrMA.GK6969Z.tGww69s1kSox69FAkEJGb_P4DrWu69696969K6969BO69s"
DEBUG_MODE=1
```

This tells the application what our bot token is and that we're in debug mode. Replace the token (it's a fake token) with the one for your application.

#

**Note**: This is also how you make your own BSEBot to be run elsewhere.

#


## Step Nine: Attempting to run again

If we go back to our "Run and Debug" tab and attempt to run the bot again; we'll get a different error: `pymongo.errors.ServerSelectionTimeoutError`. This is complaining that there isn't a valid MongoDB server to connect to. We'll have to install it if we want to run the bot.

## Step Ten: Install MongoDB

MongoDB is the database service we use. Install the community edition.

[Install MongoDB](https://www.mongodb.com/docs/manual/installation/)

I typically just leave the service running as I'm often jumping in and out of development. You can disable it and re-enable it as you see fit.

**Optional**: I use `Studio3T` as a GUI client for MongoDB; it has a free community edition that's a bit more fully featured that the one Mongo offers by default. Most people won't require this though.

## Step Eleven: Attempt to run again!

When we go back to our "Run and Debug" tab and run the bot this time; it _should_ actually be operational now. If you used one of the Team Application's bots then it should already be in the [test server](https://discord.com/invite/R39Kw7gXSa) - you can play around with the commands there. Else, you will need to invite your bot to a server to be able to play around with it. I recommend the [test server](https://discord.com/invite/R39Kw7gXSa).

#

# Need Help?

Join the [Test Server](https://discord.com/invite/R39Kw7gXSa) and come and ask me questions.
