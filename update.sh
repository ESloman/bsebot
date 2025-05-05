#!/usr/bin/bash

docker stop bsebot
docker rm bsebot
docker run -d \
    --pull="always" \
    -v "/home/ubuntu/.env:/home/app/discordbot/.env" \
    -v "/home/ubuntu/bsebotlogs:/root/bsebotlogs" \
    --name bsebot \
    --network="host" \
    --restart="always" \
    esloman/bsebot:latest

# this is safe as it doesn't affect running containers
# data from mongo container isn't stored in a docker volume
docker system prune -af
