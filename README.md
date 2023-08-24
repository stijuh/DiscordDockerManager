# Discord Docker Manager Bot

A mouth full, aye? Well, this simple python bot is made to run _as_ a docker container, to manage said docker containers
in the same environment.

___

## 1. Functionality

The currently supported actions are:

- Retrieving a list of all containers, optionally filtered by status and name
- Stopping, (re)starting, renaming or removing containers by name or id
- Retrieve logs of a container in txt format
- Run an image from [Docker Hub](https://hub.docker.com/) with commands to execute
- Run your own or publicly available code hosted on [Github](https://github.com/) as a container (cannot contain env variables, see [Limitations](#4-limitations).)
- A help menu that basically says what I'm writing here

___

## 2. How to use

The application is supposed to run as a docker container within the same environment as the containers you want to
manage.

### 2.1 For running locally:

1. Clone this project and make sure docker is running or available.
2. Set up the .env file with the variables laid out in [Environments](#22-environments-env).
3. Execute `docker compose up` in the terminal.

You can also use this in tools like [portainer](https://docs.portainer.io/).

### 2.2 Environments (.env)

This app relies on a couple of environment variables:

- **DISCORD_TOKEN** ~ this is the token of your discord bot, as created in
  the [discord developer portal](https://discord.com/developers)
- **ADMINS** ~ A list of user id's that are allowed to use the bot. It is comma seperated.
- **GUILDS** ~ A list of guild (also known as a server) id's that the commands will be usable in. It is comma seperated.

See the example.env for.. well, examples.

___

## 3 Reasoning

So, as you can see this is all fairly easy to perform by using direct docker commands or using the docker desktop app.
Why did I create this then? I am running most of my (docker container) services on my Raspberry Pi, and I don't
want to open up a port to the internet. I still want to manage my services however, so what better way to do that then
using a discord bot? Shhh. There is no better way. This is it.

___

## 4 Limitations

As of the time of writing (AUG 2023), this bot can be used to manage already existing containers, 
pull images from dockerhub and from you own/public coding projects on github with a `docker-compose.yml` file.

However, there is one big limitation. Because of Discord's security practises, users should not transmit any sensitive
data like passwords, or _environment variables_. So, if your app needs environment variables to function, this bot cannot
deploy it for you. You can of course still do this manually, and then manage the container through this bot.

If Discord changes their security practises (End-to-End Encryption for example), then this might change. 

___
[2023 Studio Stoy](https://studiostoy.nl)