# Discord Docker Manager Bot

A mouth full, aye? Well, this simple python bot is made to run _as_ a docker container, to manage said docker containers
in the same environment.

___
## Functionality
The currently supported actions are:

- Retrieving a list of all containers, running or not
- Restarting containers by name or id
- Stopping containers by name or id
- A help menu that basically says what I'm writing here

## Environments (.env)
This app relies on a couple of environment variables:

- **DISCORD_TOKEN** ~ this is the token of your discord bot, as created in the [discord developer portal](https://discord.com/developers)
- **ADMINS** ~ A list of user id's that are allowed to use the bot. It is comma seperated.

See the example.env for.. well, examples.

___
### Reasoning
So, as you can see this is all fairly easy to perform by using direct docker commands or using the docker desktop app.
Why did I create this then? I am running most of my (docker container) services on my Raspberry Pi, and I don't 
want to open up a port to the internet. I still want to manage my services however, so what better way to do that then
using a discord bot? Shhh. There is no better way. This is it.
