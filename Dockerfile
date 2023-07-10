FROM python:3.10

COPY . /dockermanager/src
WORKDIR /dockermanager/src

ADD requirements.txt /
RUN pip install -r requirements.txt
EXPOSE 5555

CMD [ "python", "main.py" ]