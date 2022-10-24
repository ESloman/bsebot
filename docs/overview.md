# BSEBot Overview

The aim of this file is to provide a high-level overview of BSEbot's purpose, functionality and how it does all the former. There will be separate documents that provide more in-depth technical information.

## BSEBot Purpose

The primary purpose of BSEBot is to run the 'BSEddies' (eddies) system that the Best Summer Ever (trademark pending) server uses. The eddies system allows users to gain 'eddies' (a fictional currency) and then use those eddies to bet on various things.
Using Discord Slash Commands, users can create bets, place eddies on bets, close bets, etc.

Every day, users will earn eddies through a 'daily salary'; this salary is determined by the user's interactivity in the server. Users who use the server more will naturally gain more eddies passively than others.

The bot does have other functionality - but this is secondary to the primary purpose. This includes the Valorant after-work call-to-arms and also the mute reminder in spoiler threads.

## Technical Overview

The bot is written in Python (`3.9+`) and is deployed via Docker Image to an EC2 AWS instance running in EU West (London). The bot's database is a MongoDB server instance running in a Docker container on the same EC2 instance.

The code relies on the Python library `py-cord` for all of it's interactions with Discord. This framework was chosen due it's ongoing support and it being relatively up to date with the official Discord API.

MongoDB was chosen due it's flexibility - it's a NoSQL DB and it's documents are structured similarly to JSON documents. Document keys can be created dynamically which makes it easy for us to add new keys to tables as needed.

### Discord Slash Commands

The bot heavily relies on Discord Slash Commands for it's core functionality.
- [Discord developer page on slash commands](https://discord.com/developers/docs/interactions/application-commands)
- [Pycord documentation on slash commands](https://guide.pycord.dev/interactions/application-commands/slash-commands/)

Slash commands allow a user to give the bot a command without actually sending the message. The user simply types `/` followed the name of the command (ie, `/<COMMAND>`). Slash commands do allow parameters too and slash commands make it easy to validate the inputs and make sure the user provides all the information they need to. I think they're great and they suit our purposes perfectly.

### Pycord tasks

The bot runs an `asyncio` loop that listens for Discord events and then calls the appropriate bit of code to handle that event. It is therefore not possible for us to natively have some code that says

````python
if datetime.datetime.now() == time_we_want_to_trigger_something:
    do_something()
````

To trigger events that happen at particular times (like, a morning 'good morning message' for example) or at set intervals (like checking who should be King) we must use `pycord`'s tasks (Cogs). We use these extensively for various tasks and we'll go into them in detail at another point. All the tasks are in the `discordbot/tasks` directory.

### Code overview

We will now go through the code - trying to keep the explanation brief and linking to other documents that provide more details.

The code is separated into three primary folders:
- `apis`
- `discordbot`
- `mongo`

The `apis` folder contains API classes for interacting with third party sites or services.  
The `discordbot` folder contains the code python code that runs the bot.  
The `mongo` folder contains DB API classes for interacting with our database.

### Core concepts

The BSEBot works and interacts with Discord by listening for events. Everything that happens in Discord (like a message being sent, someone reacting to something, creating a channel, using a slash command, etc) is an event. We can add 'event listeners' to handle particular events - the `pycord` framework will then invoke our code when it receives an event of that type. The code uses coroutines and an asynchronous framework that allows it to process multiple things (like events) simultaneously.

Similarly, within the code (and using the `pycord` framework), we can register the Slash Commands (and other Application Commands - but on to that later) and then when one of our commands is invoked by a user - the framework will invoke the code that we designated as it's callback.

The [pycord reference on discord events can be found here](https://guide.pycord.dev/interactions/application-commands/slash-commands/). This lists all the supported events in the framework. The events listed are vast and there's lots of 
different things that we can use to trigger code.

An example of an event that we subscribe to is the [`on_ready`](https://guide.pycord.dev/interactions/application-commands/slash-commands/) event. This event is triggered when the bot has logged in and is ready to start to receiving events. This is how we register the event listener:

````python
@self.client.event
async def on_ready():
    """
    Event that handles when we're 'ready'
    :return:
    """
    await self.on_ready.on_ready()
````

We create a function that has a name that's the same as the event we want to register too (in this case `on_ready`) and then decorate it with the `@self.client.event` decorator that tells the framework we want to listen for this event. The code in the function is what gets invoked when Discord sends that event.  
In this case, we call the `on_ready` function on our `on_ready` class. I know, I know, we've said `on_ready` a lot in that code and we'll move on to explaining how this pieces together.

#### BSEBot code principles

The code is separated out to avoid having really large files. This means that I try to separate code out into separate files and classes wherever possible. This is most easily seen when looking at the event listeners. In `main.py`, which is our primary entry point for the bot, we instantiate our our Discord Bot object.

````python
cli = discord.Bot(debug_guilds=IDS, intents=intents, activity=listening_activity)
com = CommandManager(cli, IDS, logger, beta_mode=BETA_MODE, debug_mode=DEBUG_MODE, giphy_token=GIPHY_TOKEN)
````

`discord.Bot` is the `pycord` Bot API class that handles events and interacting with Discord for us. We also instantiate a class called `CommandManager` - and the first parameter we give it is our `discord.Bot` object. This `CommandManager` is defined in `discordbot/commandmanager.py` and 'manages' our commands.  

Every event that we listen for has a corresponding 'Event Class'. These event classes get instantiated by the `CommandManager` and then it references them when it registers all of the event listeners. The event classes allow us to inherit from a base `BaseEvent` class which contains shared methods and variables that all of the events will rely on - typically these are instances of our database or API classes.

For example,

In `discordbot/clienteventclasses.py` (where we define our event classes for client events), we have a `OnReadyEvent` class. It has one method called `on_ready` that contains all of the logic we want to perform when the bot is first started and has successfully connected to Discord.

````python
class OnReadyEvent(BaseEvent):
    """
    Class for handling on_ready event
    """
    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        # init logic here

    async def on_ready(self) -> None:
        """
        Method called for on_ready event.
        :return: None
        """
        # logic here
````

In `CommandManager` we create an instance of it in `__init__`:

````python
self.on_ready = OnReadyEvent(client, guilds, self.logger, self.beta_mode)
````

and then, when we register our event listener for the `on_ready` event (as we saw earlier), we call the `on_ready` method on our `on_ready` event class.

````python
@self.client.event
async def on_ready():
    """
    Event that handles when we're 'ready'
    :return:
    """
    await self.on_ready.on_ready()
````

This is how we handle every event we want to listen to and every event has a corresponding `EventClass`.

'Client' event classes are native Discord events (listed on the reference above). Slash commands are slightly different but each invoked slash commands triggers a 'slash command event' and we also have a corresponding `BSEddies` slash command event class in `slashcommandeventclasses.py`.