# bsebot [![](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/esloman/bsebot) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/esloman/bsebot/docker-image.yml) ![GitHub issues](https://img.shields.io/github/issues-raw/esloman/bsebot) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/esloman/bsebot) ![GitHub contributors](https://img.shields.io/github/contributors/esloman/bsebot)

**`bsebot`** is a Discord bot that provides a user economy and betting system for a server. Users again `eddies` (points), each day and can also create bets to spend their eddies on. The user with the highest amount of eddies is the **`KING`** of the server - the King gets a special role and earns taxes on other users' earnings.

Bot was originally created for the `BSE` server to fulfill a need to have something similar to _twitch predictions_ for placing bets on the server's games of Valorant. The bot has become a bit more generic and has other functions that are specific for the `BSE` server. The bot is capable of doing a `BSEddies awards` on a monthly or annual basis and also some server statistics.

**NOTE**: The aim is to make the code more server agnostic so that it can be invited to other servers. Will add an invite link here once that's been completed. Issue #79 captures that work.

# Features
- # Eddies

    ## view your eddies
    Use `/view` to see how many eddies you have

    ![view example](/docs/readme_images/readme_view.png)

    ## check the leaderboard
    See how you stack up against other users in the server using `/leaderboard`

    ![leaderboard example](docs/readme_images/readme_leaderboard.png)

    ## earn eddies
    Earn eddies daily through interacting with the server.

    ![eddies salary example](docs/readme_images/readme_salary.PNG)

    ## become the **King**
    Whoever has the most eddies - is the King! They get a special named role and will earn taxes on everyone's salaries.

    ![king message](docs/readme_images/readme_king.PNG)

    ## `R E O V L U T I O N`
    Will the peasants overthrow the KING? Will the KING consolidate further power?

    ![revolution message](docs/readme_images/readme_revolution.png)

- # Betting system

    Create bets and spend your eddies to lose it all or win **big**.

    ## Create bets

    Using `/create`

    ![modal creating a bet](docs/images/../readme_images/readme_create_creating.png)

    ![bet created](docs/readme_images/readme_create_created.png)

    ## Place eddies on those bets

    Using `/place` users can easily put their eddies onto bets. Users can also use the `place` button on the bet to invoke the same UI.

    ![using /place command](docs/readme_images/readme_place.gif)

    ## Close bets

    Use `/close` or the use the bet buttons to invoke the close dialog and give users their payouts.

    ![close dialog](docs/readme_images/readme_close_initial.png)

    Bet message gets updated with who won what.

    ![bet edit screen](docs/readme_images/readme_close_closed.png)

- # Awards and statistics

    Get monthly and annual stats and awards.

    ## Statistics
    Get stats updates on the first of month and year.

    ![stats message](docs/readme_images/readme_stats.png)

    ## Awards
    Win monthly/annual awards and win some extra eddies.

    ![awards message](docs/readme_images/readme_awards.png)
