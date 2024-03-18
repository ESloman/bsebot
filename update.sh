#!/usr/bin/bash

# this is safe as it doesn't affect running containers
# data from mongo container isn't stored in a docker volume
docker system prune -af
docker stop bsebot
docker rm bsebot
docker run --pull="always" -d -v "/home/ubuntu/.env:/home/app/discordbot/.env" -v "/home/ubuntu/bsebotlogs:/root/bsebotlogs" --name bsebot --network="host" --restart="always" elliotsloman/bsebot:latest
