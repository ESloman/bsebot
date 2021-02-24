# bsebot

## Intro

The code repository for Best Summer Ever's Discord Server bot. This bot manages the 'BSEddies' system of the server - a fictional system of 'points' that users can use to bet on different predictions. The system allows easy creation of these "bets"

As this repository is private and the code within it only intended to be used for the BSEBot - the people reading this document are highly likely to be members of the BSE Discord Server and are either interested in how it works or interested in collaborating on the project. This document will be written with that in mind.



## Overview
The BSEBot is written in **Python** and uses Python 3.9. The bot runs on a AWS EC2 instance in the *cloud* :cloud:.



### Dependencies

The bot relies on a few third party dependencies:

```
discord.py==1.6.0
requests
python-dotenv~=0.15.0
pymongo~=3.11.3
discord-py-slash-command==1.0.9.5
```

1. `discord.py` is the library we use for interacting with the Discord API
2. `discord-py-slash-command` is an additional library that we use for interacting with Discord's Slash Command API
3. `requests` is the library we use for sending HTTP requests
4. `python-dotenv` is a simple library for interacting with `.env` files
5. `pymongo` is a library we use for interacting with MongoDB



### MongoDB

The database that we use is MongoDB. This is a NoSQL database that stores entries as BSON documents. The structure is as following:

- MongoDB Server (the actual instance running everything - there can be only one instance)
- MongoDB Database (a database within the instance - an instance can have X Databases)
- MongoDB Collection (think 'table' - Collections exist within Databases and a Database can have X Collections)
- MongoDB Documents (think 'rows' - BSON documents within a Collection. A Collection can have X Documents)

The AWS instance is running a MongoDB server and the third party library `pymongo` is officially developed by MongoDB.


All the code for interacting with our MongoDB instance is within the `mongo` folder. We use the database to store all information about each user and all the bets that have been created on the server.



### discordbot

The rest of the code can be found in the `discordbot` folder. This contains the code that interacts with Discord and actually does all the fancy stuff we want it to do.

### Bets
Here we'll discuss how bets work and how they're structured.

#### Bet Creation
A bet is created using the `/bseddies bet create` slash command. This will create a unique ID and put the bet into the database. The user can specify up to four "outcomes" to a bet. THe user can also specify a "timeout" for the bet - this timeout denotes when the bet will be "closed" for any new bets.

Once created, a message will be sent to the channel the user sent the slash command in with all bet information. Users can then react, or use `/bseddies bet place` command, to the corresponding emoji to place eddies on a particular outcome. Users can only bet on ONE outcome per bet. They can place as many eddies as they want on a bet.

#### Bet Closing

Once a bet exceeds it's "timeout" - the bet will be "closed" by the system. This means no more new bets can be placed on it.

Only the user who created the bet can give the "result" by using the `/bseddies bet close` command. This will close the bet formally and distribute the winnings to the winners. This command can be used before a bet "times out" and will also "close" it for new bets.


### Glossary - A note on terminology

This is just to explain some of the terminology that's used throughout the code and might not be _100%_ consistent. 

**GUILD**\
Discord calls servers "Guilds". The API uses "guild" throughout. To remain consistent with that - we also use the term "guild" in the code rather than "server". 

**Points**\
When this was being developed, I wasn't 100% sure what it would be called. So I use the term "points" a lot in the code. Some of the comments refer to "bseddies" or "eddies" though. The actual DB database is called "bestsummereverpoints" and the Collection for users is called "userpoints". I'd like to remain consistent with using the term "points" in code but we can freely use "bseddies" or "points" within comments.



## How it actually works

The Discord API works on "events". Basically, we register a series of events to listen to and when one of those events happens on the server we trigger the function that we registered for that event. We can only register one function for each event. The Slash Commands work in a similar manner but we register the Slash Commands with the server and when someone executes a command we run the function that we registered for that command.

We use Discord's Slash Commands API to register commands and these commands provide a way for users to manage bets and their BSEddies. Slash Commands are a relatively new feature for Discord and they're still officially in "beta". One big advantage is that user's don't have to send a message to use a command (meaning less notifications for everyone). Another is that users can see what parameters they need to give for a given command - for both OPTIONAL and REQUIRED commands. Discord will also do some basic validation on these inputs to make sure that the data provided is correct.

The bulk of the code is reacting to Slash Commands that the user sends. We do listen to a few events (mainly reaction type events as we do quite a bit with user reactions).


### Code structure

#### discordbot

##### Events and Commands

The entry point to the bot is within `main.py`. This file sets up the basic variables that we need, instantiates the classes that do all the heavy lifting and then begins the asyncio loop that listens for events from Discord.

There are two main classes that are instantiated in `main.py` that are worth noting:

```python
cli = commands.Bot(command_prefix="!", intents=intents)
com = CommandManager(cli, IDS, logger, beta_mode=BETA_MODE, debug_mode=DEBUG_MODE)
```

- `cli` is the Discord API class that handles event listening.
- `com` is an instance of `CommandManager`. This class adds all the event listeners and registers all of the Slash Commands.

The `CommandManager` class can be found in `commandmanager.py`.

Every event we listen to and every Slash Command we register actually has a corresponding Class that handles all the logic for that particular event. These classes can be found in `clienteventclasses.py` for Discord events and `slashcommandeventclasses.py` for Slash Command events. The `CommandManager` instance that we instantiate will instantiate it's own instances of all these classes and register the corresponding class methods for each event and Slash Command.

For example:

commandmanager.py L82-84

```python
# client event classes
self.on_ready = OnReadyEvent(client, guilds, self.logger, self.beta_mode)
self.on_reaction_add = OnReactionAdd(client, guilds, self.logger, self.beta_mode)
```

Here we're instantiating classes that correspond to the "on_ready" event and "on_reaction_add" events.

Down in the `register_client_events` method we register the `on_reaction_add` event:

commandmanager.py L182-200

```python
@self.client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    """
    This event is triggered when anyone 'reacts' to a message in a guild that the bot is in - even it's own
    reactions. However, this only triggers for messages that the bot has in it's cache - reactions to older
    messages will only trigger a 'on_raw_reaction_add' event.

    Here, we simply hand it off to another class to deal with.
    :param reaction:
    :param user:
    :return:
    """
    await self.on_reaction_add.handle_reaction_event(
        reaction.message,
        reaction.message.guild,
        reaction.message.channel,
        reaction.emoji,
        user
    )
```

The function name (`on_reaction_add`) corresponds to the event name. The `@self.client.event` decorator is what registers this function to the event (taken from the function name - so `on_reaction_add`). The function parameters will be provided by the Discord client when the event happens. When someone reacts to something in the server, this function will be called. Now, this function doesn't actually do much - it just calls the `handle_reaction_event` method on our `OnReactionAdd` instance called `self.on_reaction_add`.

That `OnReactionAdd.on_reaction_add` method handles the bulk of the logic for when a user reacts to something.

Every single event and slash command event is structured in a similar manner - with an event being registered in `CommandManager` and the function calling a specific event class.

##### Tasks

We also have a series of 'Tasks'. These are COG classes that execute a function at a set interval. The tasks are all instantiated our `CommandManager` instance and will execute their functions periodically. The tasks are:

- Bet Closer task (`betcloser.py`). This checks all "active" bets and closes them if they've timed out
- The KING check task (`eddiekingtask.py`). This checks who's the KING and makes sure the role is assigned to ONLY them

**Daily Allowance**
Let's talk allowance. Every day, every user will receive a certain amout of eddies. This amount will vary with how much the user has interacted with the server recently. The file that handles this calculation every day is in `eddiemanager.py`. This file actually runs as a cronjob on the AWS instance and not as a task (as we can't trigger tasks and exact times of day...). It runs every morning at 6am.

Now, as this file isn't running with any direct connection to the Discord API, we need a way to send messages to users. In order to do so, we write out a simple JSON file with the user's allowance in. To actually send the allowance messages to users we have a task running called 'Eddie Gain Message Task' (`eddiegainmessageclass.py`) - this checks every few minutes for that JSON file and sends the messages as described. It then deletes the file.

##### Other files

- `bot_enums.py`: File that contains enums for us to use.
- `constants.py`: A load of useful static variables
- `embedmanager.py`: contains a class that will create a Discord Embed object based on given data

## End
Now, this is a FAR from complete explanation. But hopefully this is a good starting point for helping people understand at least the concepts.
