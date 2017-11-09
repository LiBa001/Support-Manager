# Support-Manager wiki

A small overview about the bot's commands.
The default [prefix](#prefix) may differ from the prefix used on your server.

* [/tickets](#tickets)
* [/ticket](#ticket)
* [/addinfo](#addinfo)
* [/channel](#channel)
* [/supprole](#supprole)
* [/prefix](#prefix)
* [/invite](#invite)
* [/help](#help)
* [/info](#info)

***

### `/tickets`
It's to see all open tickets of:
* this server:
  > /tickets here
* or a specific user:
  > /tickets @[user]

***

### `/ticket`
Syntax:
> /ticket add [info about the problem]

> /ticket show [ticket number]

> /ticket close [ticket number]; [reason]

The info can't be longer than 100 characters and not shorter than 10.
A ticket can only be closed by the author or an admin.

**Please don't abuse tickets for normal communication or to offend.**  
**It's allowed to create one or two test tickets, but you have to delete them after one day at the latest.**  
**Generally, think of closing tickets, when the problem is solved.**  

***Example:***  
> User's perspective.  
![ticket add/show](https://liba001.github.io/Support-Manager/pictures/ticket_add_show.PNG)  
> Supporter's perspective.  
![ticket close](https://liba001.github.io/Support-Manager/pictures/ticket_close.PNG)  

***

### `/addinfo`
This is to add information to an existing ticket.
It can only be used by the ticket author.  

Syntax:
> /addinfo [ticket number] [info]

***

### `/channel`
This is to set the 'support-channel', where the bot informs the [supporters](#supprole) about:
* new tickets
* edited tickets
* closed tickets

Syntax:
> /channel #[channel name]

This command is only usable for admins.

***

### `/supprole`
Admins should set a support-role like this:
> /supprole @[support-role]

**This role will be mentioned on ticket events in the [support-channel](#channel).**

To remove it type:
> /supprole remove.

**Note**: You have to set the role to be mentionable!

***

### `/prefix`
This is to change the command prefix of the bot.  
The default prefix is `/`.  
If the current prefix is in complication with the prefixes of other bots on your server, an admin can change it like this:
> /prefix [new prefix]

***

### `/invite`
The bot will send you an link for inviting it to a server.  
Just type `/invite`!

***

### `/help`
/help shows a help message with the command list and a short description how to use them (slightly reduced version of this page).  
Type `help` after any command to see the command-specific help-page!

For example: 
> /ticket help

***

### `/info`
Shows information about:
* the bot
  * server count
  * member count
  * uptime
* the developer(s)
  * name, discord username
  * Pages: [GitHub](https://github.com/LiBa001), [Discordbots.org](https://discordbots.org/user/269959141508775937), [Patreon](https://www.patreon.com/user?u=8320690)
* programming language, library

Just type: `/info` or `/about`!
