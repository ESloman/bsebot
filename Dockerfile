FROM python:3.11.5

ARG DISCORD_TOKEN
ARG GIPHY_TOKEN
ARG GIT_USER
ARG GIT_PASS
ARG GITHUB_API_KEY

SHELL ["/bin/bash", "-c"]

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -yq tzdata nano unzip google-chrome-stable\
    && ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get autoremove  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && FULL_VERSION=`google-chrome --version` \
    && CHROME_VERSION=`echo ${FULL_VERSION:14}` \
    && wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && mkdir -vp /opt/chromedriver \
    && unzip chromedriver-linux64.zip -d /opt/chromedriver \
    && rm -rf chromedriver-linux64.zip

RUN mkdir -vp /home/app

COPY . /home/app/

RUN cd /home/app \
    && mkdir -vp /home/gitwork \
    && cd /home/gitwork \
    && git clone https://${GIT_USER}:${GIT_PASS}@github.com/ESloman/bsebot.git

ENV PYTHONPATH=/home/app/

RUN pip install -r home/app/requirements.txt \
    && touch /home/app/discordbot/.env \
    && echo "DEBUG_MODE=0" >> /home/app/discordbot/.env \
    && echo "DISCORD_TOKEN=${DISCORD_TOKEN}" >> /home/app/discordbot/.env \
    && echo "GIPHY_API_KEY=${GIPHY_TOKEN}" >> /home/app/discordbot/.env \
    && echo "GITHUB_API_KEY=${GITHUB_API_KEY}" >> /home/app/discordbot/.env

WORKDIR /home/app/discordbot

CMD ["python", "/home/app/discordbot/main.py"]
