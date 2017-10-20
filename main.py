import discord
import jPoints
import re
import time

client = discord.Client()

bot_admins = ['269959141508775937']

helpmsg = {}

helpmsg['ticket'] = "Syntax:\n" \
                    "`{prefix}ticket add [info about the problem]` or\n" \
                    "`{prefix}ticket [show|close] [ticket number]`\n" \
                    "The info can't be longer than 100 characters.\n" \
                    "A ticket can only be closed by the author or an admin."

helpmsg['tickets'] = "It's to see all tickets of . . .\n" \
                     ". . . every server:\n" \
                     "  `{prefix}tickets all`\n" \
                     ". . . this server:\n" \
                     "  `{prefix}tickets here`\n" \
                     ". . . a specific user:\n" \
                     "  `{prefix}tickets @[user]`"

helpmsg['addinfo'] = "This is to add information to an existing ticket.\n" \
                     "It can only be used by the ticket author.\n" \
                     "Syntax: `{prefix}addinfo [ticket number] [info]`"

helpmsg['channel'] = "This is to set the 'support-channel', where the bot informs the supporters about:\n" \
                     " - new tickets\n" \
                     " - edited tickets\n" \
                     " - closed tickets\n" \
                     "Syntax: `{prefix}channel #[channel name]`\n" \
                     "This command is only usable for admins."

helpmsg['prefix'] = "This is to change the command prefix of the bot.\n" \
                    "The default prefix is `/` and the current is `{prefix}`.\n" \
                    "If the current prefix is in complication with the prefixes of other bots on this server, " \
                    "an **admin** can change it like this:\n" \
                    "`{prefix}prefix [new prefix]`"

helpmsg['help'] = "`{prefix}help` shows this help message.\n" \
                  "Type `help` after any command to see the command-specific help-page!\n" \
                  "For example: `{prefix}ticket help`"

helpmsg['invite'] = "I'll send you an link to invite me to your server.\n" \
                    "Just type `{prefix}invite`!"


def close_invalids(tickets):
    for ticket_nr in tickets:
        ticket = tickets[ticket_nr]
        
        if ticket['closed']:
            continue

        server = client.get_server(ticket['Server'])
        
        if server is None:
            tickets[ticket_nr]['closed'] = True
            jPoints.ticket.set(ticket_nr, tickets[ticket_nr])
        
    return tickets


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
    if message.channel.is_private:
        if message.author != client.user:
            await client.send_message(message.channel, "Sorry, I can't help you in a private chat.")
        return 0

    client_member = message.server.get_member(client.user.id)
    if not client_member.permissions_in(message.channel).send_messages:
        return 0

    prefix = jPoints.prefix.get(message.server.id)

    commands = ['tickets', 'ticket', 'addinfo', 'channel', 'help', 'prefix', 'invite']

    if message.content.lower().startswith(tuple(map(lambda com: prefix + com, commands))):
        await client.send_typing(message.channel)
    else:
        return 0  # Attention to this when adding new commands.

    if message.content.lower().startswith(prefix + 'tickets'):
        content = message.content[9:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Tickets',
                description=helpmsg['tickets'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        tickets = close_invalids(jPoints.ticket.get_dict())

        if content.lower().startswith('all'):
            tickets_embed = discord.Embed(
                title="All active tickets.",
                description="Every ticket of every server.",
                color=0x37ceb2
            )

            for ticket_nr in tickets:
                ticket = tickets[ticket_nr]

                if ticket['closed']:
                    continue

                author = await client.get_user_info(ticket['Author'])

                server = client.get_server(ticket['Server'])

                tickets_embed.add_field(
                    name="#" + ticket_nr,
                    value="**Author:** {0}\n"
                          "**Info:** {1}\n"
                          "**Server:** *{2}*".format(author.mention, ticket['Info'], server.name),
                    inline=False
                )

        elif content.lower().startswith('here'):
            tickets_embed = discord.Embed(
                title="Active tickets.",
                description="Every ticket of this server.",
                color=0x37ceb2
            )

            for ticket_nr in tickets:
                ticket = tickets[ticket_nr]

                if ticket['closed'] or ticket['Server'] != message.server.id:
                    continue

                author = await client.get_user_info(ticket['Author'])

                tickets_embed.add_field(
                    name="#" + ticket_nr,
                    value="**Author:** {0}\n"
                          "**Info:** {1}".format(author.mention, ticket['Info']),
                    inline=False
                )

        elif len(content) == 0:
            await client.send_message(message.channel, "Which tickets?\n"
                                                       "Type `{0}tickets help` to see how it works.".format(prefix))
            return 0

        else:
            member = message.mentions[0]

            tickets_embed = discord.Embed(
                title="User tickets.",
                description="Every active ticket of {0}.".format(member.mention),
                color=0x37ceb2
            )

            for ticket_nr in tickets:
                ticket = tickets[ticket_nr]

                if ticket['closed'] or ticket['Author'] != member.id:
                    continue

                server = client.get_server(ticket['Server'])

                tickets_embed.add_field(
                    name="#" + ticket_nr,
                    value="**Info:** {0}\n"
                          "**Server:** *{1}*".format(ticket['Info'], server.name),
                    inline=False
                )

        if len(tickets_embed.fields) == 0:
            await client.send_message(message.channel, "There are no active tickets.")
            return 0

        tickets_embed.set_footer(
            text="To see also the added info of an ticket use the 'ticket show' command."
        )

        await client.send_message(message.channel, embed=tickets_embed)

    elif message.content.lower().startswith(prefix + "ticket"):
        content = message.content[8:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Ticket',
                description=helpmsg['ticket'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        try:
            channel_id = str(jPoints.channel.get(message.server.id))
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
            content = content[4:].replace('\n', ' ')

            if len(content) > 100:
                await client.send_message(message.channel, "Too many characters, no ticket has been created.\n"
                                                           "Please don't make the info-text longer than 100 chars!")
                return 0

            elif len(content) == 0:
                await client.send_message(message.channel, "Whats your problem? "
                                                           "If you don't tell it, nobody can help you.")
                return 0

            ticket_nr = len(jPoints.ticket.get_dict())+1
            jPoints.ticket.set(ticket_nr, {'Author': message.author.id,
                                           'Info': content,
                                           'closed': False,
                                           'Server': message.server.id})

            ticket_embed = discord.Embed(
                title="New ticket",
                color=0x37ceb2
            )
            ticket_embed.add_field(
                name="Ticket number:",
                value=str(ticket_nr),
            )
            ticket_embed.add_field(
                name="Author:",
                value=message.author.mention
            )
            ticket_embed.add_field(
                name="Info:",
                value=content
            )

            await client.send_message(channel, embed=ticket_embed)
            await client.send_message(message.channel, "Ticket created :white_check_mark: \n"
                                                       "Your ticket has the number {0}.".format(ticket_nr))

        if content.lower().startswith("show"):
            content = content[5:]
            close_invalids(jPoints.ticket.get_dict())

            try:
                ticket = jPoints.ticket.get(content)
            except KeyError:
                await client.send_message(message.channel, "Given ticket can't be found.")
                return 0

            if ticket['closed']:
                await client.send_message(message.channel, "This ticket is closed.")
                return 0

            ticket_embed = discord.Embed(
                title="Support ticket #{0}".format(content),
                color=0x37ceb2
            )
            for info in ticket:
                if info == 'closed':
                    continue

                if info == 'Author':
                    author = await client.get_user_info(ticket[info])
                    ticket[info] = author.mention

                if info == 'Server':
                    server = client.get_server(ticket[info])
                    ticket[info] = server.name

                ticket_embed.add_field(
                    name=info,
                    value=ticket[info]
                )

            await client.send_message(message.channel, embed=ticket_embed)

        if content.lower().startswith("close"):
            content = content[6:]

            try:
                ticket = jPoints.ticket.get(content)
            except KeyError:
                await client.send_message(message.channel, "Given ticket can't be found.")
                return 0

            if ticket['Author'] != message.author:
                if (not message.author.server_permissions.administrator) and (message.author.id not in bot_admins):
                    await client.send_message(message.channel, "You have to be admin or ticket author for that.")
                    return 0

                elif ticket['Server'] != message.server.id and message.author.id not in bot_admins:
                    await client.send_message(message.channel, "This ticket is from an other server.")
                    return 0

            if ticket['closed']:
                await client.send_message(message.channel, "Ticket is already closed.")
                return 0

            ticket['closed'] = True
            jPoints.ticket.set(content, ticket)
            await client.send_message(message.channel, "Ticket closed.")
            await client.send_message(channel, "{0} just closed ticket #{1}".format(message.author.mention, content))

    if message.content.lower().startswith(prefix + 'addinfo'):
        content = message.content[9:]

        if content == 'help':
            help_embed = discord.Embed(
                title='AddInfo',
                description=helpmsg['addinfo'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        try:
            ticket_nr = content.split(' ')[0]
            ticket = jPoints.ticket.get(ticket_nr)
        except KeyError:
            await client.send_message(message.channel, "Given ticket can't be found.")
            return 0

        if ticket['closed']:
            await client.send_message(message.channel, "This ticket is closed.")
            return 0

        if ticket['Author'] != message.author.id:
            await client.send_message(message.channel, "You have to be ticket author for that.")
            return 0

        content = content.replace(ticket_nr, '')

        title = time.strftime('%d.%m.%y %H:%M')
        ticket[title] = content
        jPoints.ticket.set(ticket_nr, ticket)

        await client.send_message(message.channel, "Info added.")

        channel_id = str(jPoints.channel.get(message.server.id))
        channel = client.get_channel(channel_id)

        ticket_embed = discord.Embed(
            title="New information:",
            color=0x37ceb2
        )
        ticket_embed.add_field(
            name=title,
            value=content
        )

        await client.send_message(
            channel,
            "{0} just added info to ticket #{1}".format(message.author.mention, ticket_nr),
            embed=ticket_embed
        )

    if message.content.lower().startswith(prefix + "channel"):
        content = message.content.split(" ")[1]

        if content == 'help':
            help_embed = discord.Embed(
                title='Channel',
                description=helpmsg['channel'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        if (not message.author.server_permissions.administrator) and (message.author.id not in bot_admins):
            await client.send_message(message.channel, "You have to be admin for that.")
            return 0

        channel_id = re.sub(r"<#(\d+)>", r"\1", content)

        if client.get_channel(channel_id) is None:
            await client.send_message(message.channel, "You have to mention the channel.")
            return 0

        jPoints.channel.set(message.server.id, channel_id)

        try:
            await client.add_reaction(message, "✅")
        except discord.errors.Forbidden:
            pass

    if message.content.lower().startswith(prefix + 'help'):
        content = message.content[6:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Help',
                description=helpmsg['help'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        help_embed = discord.Embed(
            title="Help",
            description="All commands and how to use them.",
            color=0x37ceb2
        )

        for cmd in helpmsg:
            help_embed.add_field(
                name=cmd,
                value=helpmsg[cmd].format(prefix=prefix)
            )

        if message.author.server_permissions.administrator or message.author.id in bot_admins:
            destination = message.channel
        else:
            destination = message.author
            try:
                await client.add_reaction(message, "✅")
            except discord.errors.Forbidden:
                pass

        await client.send_message(destination, embed=help_embed)

    if message.content.lower().startswith(prefix + 'prefix'):
        content = message.content[8:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Prefix',
                description=helpmsg['prefix'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        if (not message.author.server_permissions.administrator) and (message.author.id not in bot_admins):
            await client.send_message(message.channel, "You have to be admin for that.")
            return 0

        if len(content) != 1:
            await client.send_message(message.channel, "The prefix has to be **one** character.")
            return 0

        jPoints.prefix.set(message.server.id, content)

        await client.send_message(message.channel, "Okay, new prefix is `{0}`.".format(content))

    if message.content.lower().startswith(prefix + 'invite'):
        content = message.content[8:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Invite',
                description=helpmsg['invite'].format(prefix=prefix),
                color=0x37ceb2
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        await client.send_message(
            message.channel,
            "Okay, invite me to your Server:\n"
            "https://discordapp.com/oauth2/authorize?client_id=360801859461447700&scope=bot&permissions=19456"
        )


@client.event
async def on_server_join(server):
    jPoints.prefix.set(server.id, '/')
    try:
        await client.send_message(server.owner, "Hey, you or an admin on your server invited me to '{0}'. :smiley:\n"
                                                "The default prefix is `/`, so type `/help` into a text channel "
                                                "on the server to see what you "
                                                "(or rather I) can do.".format(server.name))

        await client.send_message(server.default_channel, "Hey, I'm glad to be here. "
                                                          "Hopefully I'll be helpful :smiley:.\n"
                                                          "Type `/help` to see all available commands.")
    except discord.errors.Forbidden:
        pass


client.run('BOT-TOKEN')  # TODO: insert token
