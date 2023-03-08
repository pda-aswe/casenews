FROM python:3.9.16

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENV DOCKER_CONTAINER Yes

COPY . .

CMD [ "python3", "-u", "src/main.py"]