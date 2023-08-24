# Use an official Python runtime as a parent image
FROM python:3.10

# Install the Docker client
RUN apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

COPY . /dockermanager/src
WORKDIR /dockermanager/src

# Install Python dependencies
ADD requirements.txt /
RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]