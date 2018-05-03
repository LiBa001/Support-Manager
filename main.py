import discord
import sqlib
import time
import json
import urllib.request
import asyncio

client = discord.AutoShardedClient()

bot_admins = ['269959141508775937']

spam_protector = {}

helpmsg = {}

helpmsg['ticket'] = "Syntax:\n" \
                    "`{prefix}ticket add [info about the problem]` or\n" \
                    "`{prefix}ticket show [ticket number]`\n" \
                    "`{prefix}ticket close [ticket number]; [reason]`\n" \
                    "The info can't be longer than 100 characters and not shorter than 10.\n" \
                    "A ticket can only be closed by the author or an admin.\n" \
                    "**Please __don't__ abuse tickets for normal communication or to offend.\n" \
                    "It's allowed to create one or two test tickets, " \
                    "but you have to __delete them__ after one day at the latest.**\n" \
                    "Generally, __think of closing tickets__, when the problem is solved."

helpmsg['tickets'] = "It's to see all tickets of . . .\n" \
                     "~~. . . every guild:~~ *(no longer available)*\n" \
                     "  ~~`{prefix}tickets all`~~\n" \
                     ". . . this guild:\n" \
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

helpmsg['supprole'] = "Admins should set a support-role like this:\n" \
                      "`{prefix}supprole @[support-role]`\n" \
                      "This role will be mentioned on ticket events.\n" \
                      "To remove it type: `{prefix}supprole remove`." \
                      "**Note:** You have to set the role to be mentionable."

helpmsg['prefix'] = "This is to change the command prefix of the bot.\n" \
                    "The default prefix is `/` and the current is `{prefix}`.\n" \
                    "If the current prefix is in complication with the prefixes of other bots on this guild, " \
                    "an **admin** can change it like this:\n" \
                    "`{prefix}prefix [new prefix]`"

helpmsg['info'] = "Shows information about the bot and more.\n" \
                  "Just type: `{prefix}info` or `{prefix}about`!"

helpmsg['help'] = "`{prefix}help` shows this help message.\n" \
                  "Type `help` after any command to see the command-specific help-page!\n" \
                  "For example: `{prefix}ticket help`"

helpmsg['invite'] = "I'll send you an link to invite me to your guild.\n" \
                    "Just type `{prefix}invite`!"


def close_invalids():
    for ticket in sqlib.tickets.get_all():
        ticket_nr = ticket[0]
        
        if ticket[5] == 1:
            continue

        guild = client.get_guild(int(ticket[2]))
        
        if guild is None:
            sqlib.tickets.update(ticket_nr, {'closed': 1})
        
    return sqlib.tickets.get_all()


def post_to_apis():
    domains = {
        'discordbots.org': 'API-TOKEN',
        'bots.discord.pw': 'API-TOKEN'
    }
    for domain in domains:
        count_json = json.dumps({
            "server_count": len(client.guilds),
            "shard_count": client.shard_count,
            "shard_id": client.shard_id
        })

        # Resolve HTTP redirects
        api_redirect_url = "https://{0}/api/bots/{1}/stats".format(domain, client.user.id)

        # Construct request and post guild count
        api_req = urllib.request.Request(api_redirect_url)

        api_req.add_header(
            "Content-Type",
            "application/json"
        )

        api_req.add_header(
            "Authorization",
            domains[domain]
        )

        urllib.request.urlopen(api_req, count_json.encode("ascii"))


@client.event
async def on_ready():
    print(client.user.name)
    print("--------------")

    for guild in client.guilds:
        if sqlib.servers.get(guild.id) is None:
            sqlib.servers.add_element(guild.id, {'prefix': '/'})

    # print(list(map(lambda s: s.name, client.guilds)))
    post_to_apis()


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        if message.author != client.user:
            await message.channel.send("Sorry, I can't help you in a private chat.")
        return 0

    client_member = message.guild.get_member(client.user.id)
    if not client_member.permissions_in(message.channel).send_messages:
        return 0

    prefix = sqlib.servers.get(message.guild.id, 'prefix')[0]

    commands = ['tickets', 'ticket', 'addinfo', 'channel', 'supprole', 'help', 'prefix', 'invite', 'info', 'about']

    if message.content.lower().startswith(tuple(map(lambda com: prefix + com, commands))):
        await message.channel.trigger_typing()
        remove_message = True
    else:
        remove_message = False
        if client.user in message.mentions:
            await message.channel.send("Type `{0}help` to see available commands.".format(prefix))
        return 0  # Attention to this when adding new commands.

    if message.content.lower().startswith(prefix + 'tickets'):
        content = message.content[9:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Tickets',
                description=helpmsg['tickets'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        tickets = close_invalids()
        tickets = list(filter(lambda t: t[5] == 0, tickets))

        if content.lower().startswith('here'):
            tickets_embed = discord.Embed(
                title="Active tickets.",
                description="Every ticket of this guild.",
                color=0x37ceb2
            )

            guild_id = message.guild.id
            tickets = list(filter(lambda t: t[2] == guild_id, tickets))

            for ticket in tickets:
                ticket_nr = ticket[0]

                author = await client.get_user_info(ticket[1])

                tickets_embed.add_field(
                    name="#" + ticket_nr,
                    value="**Author:** {0}\n"
                          "**Info:** {1}".format(author.mention, ticket[3]),
                    inline=False
                )

        elif len(content) == 0 or len(message.mentions) == 0:
            await message.channel.send("Which tickets?\nType `{0}tickets help` to see how it works.".format(prefix))
            return 0

        else:
            member = message.mentions[0]

            tickets_embed = discord.Embed(
                title="User tickets.",
                description="Every active ticket of {0}.".format(member.mention),
                color=0x37ceb2
            )

            for ticket in tickets:
                ticket_nr = ticket[0]

                if ticket[5] == 1 or ticket[1] != member.id:
                    continue

                guild = client.get_guild(ticket[2])

                tickets_embed.add_field(
                    name="#" + ticket_nr,
                    value="**Info:** {0}\n"
                          "**Server:** *{1}*".format(ticket[3], guild.name),
                    inline=False
                )

        if len(tickets_embed.fields) == 0:
            await message.channel.send("There are no active tickets.")
            return 0

        tickets_embed.set_footer(
            text="To see also the added info of an ticket use the 'ticket show' command."
        )

        await message.channel.send(embed=tickets_embed)

    elif message.content.lower().startswith(prefix + "ticket"):
        content = message.content[8:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Ticket',
                description=helpmsg['ticket'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        channel_id = str(sqlib.servers.get(message.guild.id, 'channel')[0])
        channel = message.guild.get_channel(int(channel_id))
        if channel_id == '0':
            await message.channel.send(
                "It seems there is no support channel configured. :confused:\n"
                "Ask an admin to set one up!"
            )
            return 0

        if channel is None:
            await message.channel.send("The configured support channel doesn't exist anymore.\n"
                                       "Ask an admin to set up a new one.")
            return 0

        if content.lower().startswith("add"):
            last_executed = spam_protector.get(message.author.id, time.time() - 60)
            if last_executed > time.time() - 60:
                await message.channel.send(
                    ":cool: :arrow_down: "
                    "You can add your next ticket in {0} seconds. :timer:".format(60 - int(time.time() - last_executed))
                )
                return None

            content = content[4:].replace('\n', ' ')

            if len(content) > 200:
                await message.channel.send("Too many characters, no ticket has been created.\n"
                                           "Please don't make the info-text longer than 200 chars!")
                return 0

            elif len(content) < 10:
                await message.channel.send("Whats your problem? "
                                           "If you don't tell it, nobody can help you.\n"
                                           "Try to describe it! *`(min. 10 chars)`*")
                return 0

            ticket_nr = str(len(sqlib.tickets.get_all())+1)
            sqlib.tickets.add_element(ticket_nr, {'author': message.author.id,
                                                  'server': message.guild.id,
                                                  'info': content,
                                                  'added': "{}",
                                                  'closed': 0})

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

            supprole_id = int(sqlib.servers.get(str(message.guild.id), 'role')[0])
            if supprole_id != 0:
                supprole = discord.utils.find(lambda r: r.id == supprole_id, message.guild.roles)

                if supprole is None:
                    await message.channel.send("It seems like the support-role doesn't exist anymore. "
                                               ":confused:")
                    return 0
                await channel.send(supprole.mention, embed=ticket_embed)

            else:
                await channel.send(embed=ticket_embed)
            await message.channel.send("Ticket created :white_check_mark: \n"
                                       "Your ticket has the number {0}.".format(ticket_nr))
            spam_protector[message.author.id] = time.time()

        if content.lower().startswith("show"):
            content = content[5:]
            close_invalids()

            ticket = sqlib.tickets.get(content)

            if ticket is None:
                await message.channel.send("Given ticket can't be found.")
                return 0
            else:
                ticket = list(ticket)  # change tuple to list, to change the values

            if ticket[5] == 1:
                await message.channel.send("This ticket is closed.")
                return 0

            ticket_embed = discord.Embed(
                title="Support ticket #{0}".format(content),
                color=0x37ceb2
            )

            author = await client.get_user_info(ticket[1])
            ticket[1] = author.mention

            guild = client.get_guild(ticket[2])
            ticket[2] = guild.name

            added_dict = json.loads(ticket[4].replace("'", '"'))
            ticket[4] = ""
            for date in added_dict:
                ticket[4] += "**{date}:** {info}\n".format(date=date, info=added_dict[date])

            if len(ticket[4]) == 0:
                ticket[4] = "*Nothing added.*"

            column_names = ['Ticket number', 'Author', 'Server', 'Info', 'Added', 'closed']

            counter = 0
            for info in ticket:
                if counter == 5:
                    continue

                ticket_embed.add_field(
                    name=column_names[counter],
                    value=info
                )
                counter += 1

            await message.channel.send(embed=ticket_embed)

        if content.lower().startswith("close"):
            content = content[6:]
            splited = content.split(';')
            if len(splited) > 1:
                closemsg = splited[1]
                content = splited[0]
            else:
                closemsg = ""
            
            errormsg = ""

            ticket = sqlib.tickets.get(content)

            if ticket is None:
                await message.channel.send("Given ticket can't be found.")
                return 0

            if ticket[5] == 1:
                await message.channel.send("Ticket is already closed.")
                return 0

            if ticket[1] != message.author.id:
                if (not message.author.guild_permissions.administrator) and (message.author.id not in bot_admins):

                    is_supporter = False
                    for role in message.author.roles:
                        if role.id == sqlib.servers.get(message.guild.id, 'role')[0]:
                            is_supporter = True
                            break

                    if not is_supporter:
                        await message.channel.send("You have to be admin, supporter or "
                                                   "ticket author for that.")
                        return 0

                elif ticket[2] != message.guild.id and message.author.id not in bot_admins:
                    await message.channel.send("This ticket is from an other guild.")
                    return 0

                msg_to_user = "**Hey, {0} just closed your ticket #{1}:** \n{2}".format(message.author.mention,
                                                                                        ticket[0],
                                                                                        closemsg)
                ticketauthor = await client.get_user_info(ticket[1])
                try:
                    await ticketauthor.send(msg_to_user)
                except discord.Forbidden:
                    errormsg = ", but user disabled direct messages"

            sqlib.tickets.update(content, {'closed': 1})
            await message.channel.send(f"Ticket closed{errormsg}.")

            channel_id = int(sqlib.servers.get(sqlib.tickets.get(content, 'server')[0], 'channel')[0])
            channel = client.get_channel(channel_id)

            if channel is None:
                await message.channel.send("There is no support channel on the guild.")
                return 0

            suppmsg = "**{0} just closed ticket #{1}**: \n{2}".format(message.author.mention, content, closemsg)

            supprole_id = int(sqlib.servers.get(str(message.guild.id), 'role')[0])
            if supprole_id != 0:
                supprole = discord.utils.find(lambda r: r.id == supprole_id, message.guild.roles)

                if supprole is None:
                    await message.channel.send("It seems like the support-role doesn't exist anymore. "
                                               ":confused:")
                    return 0
                await channel.send(supprole.mention + '\n' + suppmsg)

            else:
                await channel.send(suppmsg)

    elif message.content.lower().startswith(prefix + 'addinfo'):
        content = message.content[9:]

        if content == 'help':
            help_embed = discord.Embed(
                title='AddInfo',
                description=helpmsg['addinfo'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        ticket_nr = content.split(' ')[0]
        ticket = sqlib.tickets.get(ticket_nr)

        if ticket is None:
            await message.channel.send("Given ticket can't be found.")
            return 0

        if ticket[5] == 1:
            await message.channel.send("This ticket is closed.")
            return 0

        if ticket[1] != message.author.id:
            await message.channel.send("You have to be ticket author for that.")
            return 0

        content = content.replace(ticket_nr, '')

        title = time.strftime('%d.%m.%y %H:%M')
        added_dict = json.loads(ticket[4].replace("'", '"'))
        added_dict[title] = content

        channel_id = int(sqlib.servers.get(message.guild.id, 'channel')[0])
        channel = client.get_channel(channel_id)

        if channel is None:
            await message.channel.send(":hushed: I can't find the support-channel anymore.")
            return 0

        ticket_embed = discord.Embed(
            title="New information:",
            color=0x37ceb2
        )
        ticket_embed.add_field(
            name=title,
            value=content
        )

        suppmsg = "{0} just added info to ticket #{1}".format(message.author.mention, ticket_nr)

        supprole_id = sqlib.servers.get(message.guild.id, 'role')
        if supprole_id is not None:
            if supprole_id[0] != '0':
                supprole = discord.utils.find(lambda r: r.id == supprole_id[0], message.guild.roles)

                if supprole is None:
                    await message.channel.send("It seems like the support-role doesn't exist anymore. "
                                               ":confused:")
                    return 0
                suppmsg += ', ' + supprole.mention

        await channel.send(suppmsg, embed=ticket_embed)

        sqlib.tickets.update(ticket_nr, {'added': str(added_dict)})
        await message.channel.send("Info added.")

    elif message.content.lower().startswith(prefix + "channel"):
        content = message.content[9:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Channel',
                description=helpmsg['channel'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        if (not message.author.guild_permissions.administrator) and (message.author.id not in bot_admins):
            await message.channel.send("You have to be admin for that.")
            return 0

        if len(message.channel_mentions) == 0:
            await message.channel.send("You have to mention the channel.")
            return 0

        else:
            channel_id = message.channel_mentions[0].id

        sqlib.servers.update(message.guild.id, {'channel': int(channel_id)})

        try:
            await message.add_reaction("✅")
        except discord.errors.Forbidden:
            pass
        remove_message = False

    elif message.content.lower().startswith(prefix + 'supprole'):
        content = message.content[10:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Support role',
                description=helpmsg['supprole'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        if (not message.author.guild_permissions.administrator) and (message.author.id not in bot_admins):
            await message.channel.send("You have to be admin for that.")
            return 0

        if content.startswith('remove'):
            sqlib.servers.update(message.guild.id, {'role': '0'})

        else:
            roles = message.role_mentions

            if len(roles) == 0:
                await message.channel.send("You have to mention the role.")
                return 0

            else:
                sqlib.servers.update(message.guild.id, {'role': roles[0].id})

        try:
            await message.add_reaction("✅")
        except discord.errors.Forbidden:
            pass
        remove_message = False

    elif message.content.lower().startswith(prefix + 'help'):
        content = message.content[6:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Help',
                description=helpmsg['help'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        help_embed = discord.Embed(
            title="Help",
            description="All commands and how to use them.",
            color=0x37ceb2
        )

        for cmd in helpmsg:
            help_embed.add_field(
                name=cmd,
                value=helpmsg[cmd].format(prefix=prefix),
                inline=False
            )

        if message.author.guild_permissions.administrator or message.author.id in bot_admins:
            destination = message.channel
        else:
            destination = message.author
            try:
                await message.add_reaction("✅")
            except discord.errors.Forbidden:
                pass
            remove_message = False

        await destination.send(embed=help_embed)

    elif message.content.lower().startswith(prefix + 'prefix'):
        content = message.content[8:].lower()

        if content == 'help':
            help_embed = discord.Embed(
                title='Prefix',
                description=helpmsg['prefix'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        if (not message.author.guild_permissions.administrator) and (message.author.id not in bot_admins):
            await message.channel.send("You have to be admin for that.")
            return 0

        if len(content) != 1:
            await message.channel.send("The prefix has to be **one** character.")
            return 0

        sqlib.servers.update(message.guild.id, {'prefix': content})

        await message.channel.send("Okay, new prefix is `{0}`.".format(content))

    elif message.content.lower().startswith(prefix + 'invite'):
        content = message.content[8:]

        if content == 'help':
            help_embed = discord.Embed(
                title='Invite',
                description=helpmsg['invite'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        await message.channel.send(
            "Okay, invite me to your Server:\n"
            "https://discordapp.com/oauth2/authorize?client_id=360801859461447700&scope=bot&permissions=19456"
        )

    elif message.content.lower().startswith((prefix + 'info', prefix + 'about')):
        if message.content[6:] == "help" or message.content[7:] == "help":
            help_embed = discord.Embed(
                title="Info/About",
                description=helpmsg['info'].format(prefix=prefix),
                color=0x37ceb2
            )
            await message.channel.send(embed=help_embed)
            return 0

        infotext = discord.Embed(
            title="Support-Manager",
            description="About the bot.",
            color=0x37ceb2,
            url="https://liba001.github.io/Support-Manager/"
        )
        infotext.set_author(
            name="Linus Bartsch | LiBa01#8817",
            url="https://liba001.github.io/",
            icon_url="https://avatars0.githubusercontent.com/u/30984789?s=460&v=4"
        )
        infotext.set_thumbnail(
            url="https://images.discordapp.net/avatars/360801859461447700/695877fa3289fae03ff5770e7067e8c6.png?size=512"
        )
        infotext.add_field(
            name="Developer",
            value="Name: **Linus Bartsch**\n"
                  "Discord: **LiBa01#8817**\n"
                  "GitHub: [LiBa001](https://github.com/LiBa001)\n"
                  "I'm also at [Discordbots.org](https://discordbots.org/user/269959141508775937).\n"
                  "I'd be very happy if you'd support me on "
                  "[**Patreon**](https://www.patreon.com/user?u=8320690). :heart:\n"
                  "*Concept idea by **MrBlack#8359***",
            inline=True
        )
        infotext.add_field(
            name="Developed in:",
            value="Language: **Python3.6**\n"
                  "Library: **discord.py** (0.16.8)\n"
        )
        infotext.add_field(
            name="Commands",
            value="Type `{0}help` to get all commands.\n"
                  "Join the [Official Support Server](https://discord.gg/z3X3uN4) "
                  "if you have any questions or suggestions.".format(prefix)
        )
        infotext.add_field(
            name="Stats",
            value="Server count: **{0}**\n"
                  "Uptime: **{1}** hours, **{2}** minutes\n"
                  "Member count: **{3}**".format(len(client.guilds), up_hours, up_minutes, len(list(client.get_all_members())))
        )
        infotext.set_footer(
            text="Special thanks to MaxiHuHe04#8905 who supported me a few times."
        )

        await message.channel.send(embed=infotext)

    elif client.user in message.mentions:
        await message.channel.send("Type `{0}help` to see available commands.".format(prefix))

    client_member = message.guild.get_member(client.user.id)
    if client_member.permissions_in(message.channel).manage_messages and remove_message:
        await message.delete()


@client.event
async def on_guild_join(guild):
    post_to_apis()
    if sqlib.servers.get(guild.id) is None:
        sqlib.servers.add_element(guild.id, {'prefix': '/'})
    try:
        await guild.owner.send("Hey, you or an admin on your guild invited me to '{0}'. :smiley:\n"
                               "The default prefix is `/`, so type `/help` into a text channel "
                               "on the guild to see what you "
                               "(or rather I) can do.".format(guild.name))

        if guild.default_channel is not None:
            await guild.default_channel.send("Hey, I'm glad to be here. "
                                             "Hopefully I'll be helpful :smiley:.\n"
                                             "Type `/help` to see all available commands.")
    except discord.errors.Forbidden:
        pass


@client.event
async def on_guild_remove(guild):
    post_to_apis()


async def uptime_count():
    await client.wait_until_ready()
    global up_hours
    global up_minutes
    up_hours = 0
    up_minutes = 0

    while not client.is_closed:
        await asyncio.sleep(60)
        up_minutes += 1
        if up_minutes == 60:
            up_minutes = 0
            up_hours += 1


client.loop.create_task(uptime_count())
client.run('BOT_TOKEN')  # TODO: insert token
