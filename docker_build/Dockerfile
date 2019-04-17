FROM python:3.7

RUN mkdir /home/app
WORKDIR /home/app

ADD requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT python main.py

