FROM python:3.11.0

ARG DISCORD_TOKEN
ARG GIPHY_TOKEN
ARG GIT_USER
ARG GIT_PASS

RUN apt-get update \
    && apt-get install -yq tzdata nano \
    && ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

RUN mkdir -vp /home/app

COPY . /home/app/

RUN cd /home/app \
    && mkdir -vp /home/gitwork \
    && cd /home/gitwork \
    && git clone https://${GIT_USER}:${GIT_PASS}@github.com/ESloman/bsebot.git

ENV PYTHONPATH=/home/app/

RUN pip install cython \
    && pip install cchardet \
    && git clone https://github.com/Pycord-Development/pycord \
    && cd pycord \
    && pip install -U .[speed] \
    && cd .. \
    && pip install -r home/app/requirements.txt \
    && touch /home/app/discordbot/.env \
    && echo "DEBUG_MODE=0" >> /home/app/discordbot/.env \
    && echo "DISCORD_TOKEN=${DISCORD_TOKEN}" >> /home/app/discordbot/.env \
    && echo "GIPHY_API_KEY=${GIPHY_TOKEN}" >> /home/app/discordbot/.env

WORKDIR /home/app/discordbot

CMD ["python", "/home/app/discordbot/main.py"]
