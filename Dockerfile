FROM python:3.10.7-slim

ARG DISCORD_TOKEN
ARG GIPHY_TOKEN

RUN mkdir -vp /home/app

COPY ./* /home/app/

ENV PYTHONPATH=/home/app/

RUN python install -f home/app/requirements.txt

RUN touch /home/app/discordbot/.env \
    && echo "DEBUG_MODE=1" >> /home/app/discordbot/.env \
    && echo "DISCORD_TOKEN=${DISCORD_TOKEN}" >> /home/app/discordbot/.env \
    && echo "GIPHY_TOKEN=${GIPHY_TOKEN}" >> /home/app/discordbot/.env

CMD ["python", "/home/app/discordbot.main.py"]