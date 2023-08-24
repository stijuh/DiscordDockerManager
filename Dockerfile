# Use an official Python runtime as a parent image
FROM python:3.10

# Install the Docker client
RUN apt-get update && apt-get install -y docker.io
RUN DOCKER_BUILDKIT=0 docker compose -f docker-compose-dev.yml up -d --build

COPY . /dockermanager/src
WORKDIR /dockermanager/src

# Install Python dependencies
ADD requirements.txt /
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]