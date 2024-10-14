FROM python:3.13.0-slim

RUN apt-get update && apt-get -y --no-install-recommends install curl git gnupg2 \
    && curl -q https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -yq jq tzdata nano unzip google-chrome-stable \
    && ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get autoremove  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && CHROME_VERSION=$(curl https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r .channels.Stable.version) \
    && curl -q -o chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && mkdir -vp /opt/chromedriver \
    && unzip chromedriver-linux64.zip -d /opt/chromedriver \
    && rm -rf chromedriver-linux64.zip

RUN mkdir -vp /home/app

COPY . /home/app/

ENV PYTHONPATH=/home/app/

RUN pip install -r home/app/requirements.txt

WORKDIR /home/app/discordbot

CMD ["python", "/home/app/discordbot/main.py"]
