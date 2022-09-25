FROM python:3.10.7

ARG DISCORD_TOKEN
ARG GIPHY_TOKEN

RUN echo "Europe/London" | tee /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -vp /home/app

COPY . /home/app/

ENV PYTHONPATH=/home/app/

RUN pip install -r home/app/requirements.txt \
    && touch /home/app/discordbot/.env \
    && echo "DEBUG_MODE=0" >> /home/app/discordbot/.env \
    && echo "DISCORD_TOKEN=${DISCORD_TOKEN}" >> /home/app/discordbot/.env \
    && echo "GIPHY_API_KEY=${GIPHY_TOKEN}" >> /home/app/discordbot/.env

WORKDIR /home/app/discordbot

CMD ["python", "/home/app/discordbot/main.py"]
