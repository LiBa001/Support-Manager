import discord
import jPoints
import re

client = discord.Client()

@client.event
async def on_ready():
    print(client.user.name)
    print("--------------")

    for server in client.servers:
        try:
            jPoints.prefix.get(server.id)
        except KeyError:
            jPoints.prefix.set(server.id, '/')


@client.event
async def on_message(message):
    prefix = jPoints.prefix.get(message.server.id)

    if message.content.lower().startswith(prefix + "ticket"):
        content = message.content.split(" ")[1]

        try:
            channel_id = jPoints.channel.get(message.server.id)
            print(channel_id == "360807429073534999")
            print(channel_id)
            print("360807429073534999")
            channel = client.get_channel(channel_id)
        except KeyError:
            await client.send_message(
                message.channel,
                "It seems there is no support channel configured. :confused:\n"
                "Ask an admin to set one up!"
            )
            return 0

        if channel is None:
            await client.send_message(message.channel, "The configured support channel doesn't exist anymore.\n"
                                                       "Ask an admin to set up a new one.")
            return 0

        if content.lower().startswith("add"):
            content = message.content.split(" ")[1]

            await client.send_message(channel, "{0} needs help: {1}".format(message.author, content))

    if message.content.lower().startswith(prefix + "channel"):
        if not message.author.server_permissions.administrator:
            await client.send_message(message.channel, "You have to be admin for that.")
            return 0

        channel_id = message.content.split(" ")[1]
        channel_id = re.sub(r"<#(\d+)>", r"\1", channel_id)

        if client.get_channel(channel_id) is None:
            await client.send_message(message.channel, "You have to mention the channel.")
            return 0

        jPoints.channel.set(message.server.id, channel_id)


client.run('[BOT-TOKEN]')
