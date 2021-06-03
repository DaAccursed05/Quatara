import discord
from discord.ext import commands
from discord.ext import tasks
import json

from discord.ext.commands.core import command

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #Here, I loop the task of cleaning the spam file every 20 seconds
        @tasks.loop(seconds = 15)
        async def clean_spam(seconds = 15):
            with open("spam_detect.txt", "w+") as file:
                file.truncate(0)

    #This listener detects spam in the channels except those marked for spam
    @commands.Cog.listener()
    async def on_message(self, message):
        spamchannels = []
        Spambool = False
        with open("server_configs.json", "r") as f:
            data = json.load(f)
            spamchannels = data[str(message.guild.id)]["Spam Ignore"]
            Spambool = data[str(message.guild.id)]["Spam"]

        if Spambool and (not spamchannels or message.channel.id not in spamchannels):
            counter = 0
            with open ("spam_detect.txt", "r+") as file:
                for lines in file:
                    if lines.strip("\n") == str(message.author.id) + str(message.channel.id) + message.content:
                        counter += 1

                #If messages sent by the user and the channel + the content of the message is the same for 5 times, we ping the mods
                file.writelines(f"{str(message.author.id) + str(message.channel.id) + message.content}\n")
                if counter > 5:
                    file.truncate(0)
                    id = 0
                    with open("role_configs.json", "r") as f:
                        data = json.load(f)
                        id = data[str(message.guild.id)]["Moderator"]
                    await message.channel.send(f"You are spamming. Proceeding to ping <@&{id}> to take action.")

    #This is the kick command, pretty self explanatory imo
    @commands.command(description = "Kicks members, supa simple lil command all of ya folks should know right?", aliases = ["yeet"])
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, reason = "No reason provided"):
        await member.kick(reason= reason)
        await ctx.send(f"{member.name} has been kicked for {reason}. All hail Da YEETs!!!")
        await member.send(f"Thou hast been kicked, pestilence, for {reason}.")

    #If the user doesn't have the permission, we display this message
    @kick.error
    async def kickerror(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Hey mods! We have an imposter tryna kick someone without thy permissions. Do with him as thou wisheth.")
        else:
            print(error)

    #Repeat the same thing for ban command
    @commands.command(description = "Bans pesky motherlovers from the server once and for all for greater good of the server.", aliases = ["superyeet"])
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member : discord.Member, *, reason = "No reason provided."):
        await ctx.guild.ban(member, reason= reason)
        await ctx.send("The pestilence has been Banned. All hail YEET GOD.")
        await member.send(f"Hey punk, by the grace of the Yeet GOD, you have been banned for {reason}.")

    @ban.error
    async def kickerror(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Hey mods! We have an imposter tryna ban someone without thy permissions. Do with him as thou wisheth.")

    #repeat the same thing for clean command as well so yep
    @commands.command(description = "Clears the given set of commands so you don't have to dirty your hands.", aliases = ["clean", "tidy", "purge"])
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amt):
        await ctx.channel.purge(limit = int(amt) + 1)

    @clear.error
    async def clearError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Sorry but it seems you do not have the permissions to use this command. Thanks with the goodwill for cleannup though! :thumbsup:.")

    @commands.command(description = "Voids the pestilence into your void! After all, there's no sound in space.", aliases = ["void"])
    @commands.has_permissions(kick_members = True)
    async def mute(self, ctx, user : discord.Member, *, reason= "No reason provided."):
        role = None
        MuteRole = None
        with open("role_configs.json", "r") as f:
            data = json.load(f)
            role = data[str(ctx.guild.id)]["Member"]
            MuteRole = data[str(ctx.guild.id)]["Mute"]
        if MuteRole is not None and role is not None:
            Role = ctx.guild.get_role(role)
            muteRole = ctx.guild.get_role(MuteRole)
            await user.remove_roles(Role, reason= reason)
            await user.add_roles(muteRole, reason= reason)
            await ctx.send(f"{user.name} has been muted for {reason}!!! All hail {ctx.guild.name}!!!")
        else:
            await ctx.send("You have not configured either the member or the muted role. Configure both to be able to mute members.")

    @mute.error
    async def muteError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You tried to mute someone but can't! Hah! Why shut others' mouths when you can't zip it up yourself?")

    @commands.command(description = "Gives the disabled peasants their ability to talk back. There should be a reward for bad boys when they turn good, right?", aliases = ["unvoid"])
    @commands.has_permissions(kick_members = True)
    async def unmute(self, ctx, user : discord.Member, *, reason= "No reason provided."):
        role = None
        MuteRole = None
        with open("role_configs.json", "r") as f:
            data = json.load(f)
            role = data[str(ctx.guild.id)]["Member"]
            MuteRole = data[str(ctx.guild.id)]["Mute"]
        if MuteRole is not None and role is not None:
            Role = ctx.guild.get_role(role)
            muteRole = ctx.guild.get_role(MuteRole)
            await user.remove_roles(muteRole, reason= reason)
            await user.add_roles(Role, reason= reason)
            await ctx.send(f"{user.name} has been unmuted for {reason}!!! All hail {ctx.guild.name}!!!")
        else:
            await ctx.send("You have not configured either the member or the muted role. Configure both to be able to mute members.")

    @mute.error
    async def muteError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You tried to unmute someone but can't! Hah! You shouldn't try to be a god by giving other their speech back, mortal.")

#    #A warm command to give members warnings before voiding them :kekw:
#    @commands.command(description = "Warns members that might commit wrongdoings. I mean you have to be merciful since our Satan isn't. [Note: A reason is compulsory for using this command.")
#    @commands.has_permissions(kick_members = True)
#    async def warn(self, ctx, user : discord.Member, *, reason):
#        #Check if the user has warns from the file
#        warns = {}
#        data = {}
#        with open("warns.json", "r") as f:
#            data = json.load(f)
#            warns = data[str(ctx.guild.id)]["Warns"]
#        if str(user.id) in warns:
#            if warns[str(user.id)] == 3:
#                #we use the same code we used with mute
#                role = None
#                MuteRole = None
#                with open("role_configs.json", "r") as f:
#                    data = json.load(f)
#                    role = data[str(ctx.guild.id)]["Member"]
#                    MuteRole = data[str(ctx.guild.id)]["Mute"]
#                if MuteRole is not None and role is not None:
#                    Role = ctx.guild.get_role(role)
#                    muteRole = ctx.guild.get_role(MuteRole)
#                    await user.remove_roles(Role, reason= reason)
#                    await user.add_roles(muteRole, reason= reason)
#                    warns.pop(str(user.id))
#                    await ctx.send(f"{user.name} has been muted over accumulation of 3 warnings. The current reason for warning was {reason}!!! All hail Da YEET GOD!!!")
#                else:
#                    await ctx.send("Cannot warn further, muted role has not been set up. What kind of moderation do you think I'd do if you don't give me the roles, dummy.")
#                data[str(ctx.guild.id)]["Warns"] = warns
#            else:
#                warnnum = warns[str(user.id)]
#                warnnum += 1
#                warns.pop(str(user.id))
#                warns[str(user.id)] = warnnum
#                data[str(ctx.guild.id)]["Warns"] = warns
#                await ctx.send(f"{user.name} has been warned for {reason}. Behave yourself or I'm getting the spaceship. Warnings remaining = {3 - warns[user.id]}.")
#        else:
#            warns[str(user.id)] = 1
#            data[str(ctx.guild.id)]["Warns"] = warns
#            await ctx.send(f"{user.name} has been warned for {reason}. Behave yourself or I'm getting the spaceship. Warnings remaining = {3 - warns[user.id]}.")
#        with open("warns.json", "w") as f:
#            json.dump(data, f)
#
#
#    @warn.error
#    async def warnError(self, ctx, error):
#        if isinstance(error, commands.MissingPermissions):
#            await ctx.send("You can't even handle your own habit of stealing the job of Mods, why try to warn others?")
#
#    #A superwarn commands for more serious stuff
#    @commands.command(description = "Warns pestilence for more serious stuff. These get YEETed instantly on 3 warns instead of being muted")
#    @commands.has_permissions(kick_members = True)
#    async def superwarn(self, ctx, user : discord.Member, *, reason):
#        superwarns = {}
#        data = {}
#        with open("warns.json", "r") as f:
#            data = json.load(f)
#            superwarns = data[str(ctx.guild.id)]["Superwarns"]
#        if superwarns:
#            if str(user.id) in superwarns:
#                if superwarns[str(user.id)] == 3:
#                    await user.kick(reason= reason)
#                    await ctx.send(f"{user.name} has been kicked after the accumulation of 3 superwarnings. The reason for the last superwarning was {reason}. All hail Da YEETs!!!")
#                    await user.send(f"Thou hast been kicked, pestilence, after 3 superwarnings. The reason for thy last warning was {reason}.")
#                    superwarns.pop(str(user.id))
#                    data[str(ctx.guild.id)]["Superwarns"] = superwarns
#                    with open("warns.json", "w") as f:
#                        json.dump(data, f)
#                else:
#                    superwarns[str(user.id)] += 1
#                    data[str(ctx.guild.id)]["Superwarns"] = superwarns
#                    await ctx.send(f"{user.name} has been superwarned for {reason}. Behave yourself or face the wrath of Quatara!! Superwarnings remaining = {3 - self.bot.superwarns[user]}.")
#                    with open("warns.json", "w") as f:
#                        json.dump(data, f)
#            else:
#                superwarns[str(user.id)] = 1
#                data[str(ctx.guild.id)]["Superwarns"] = superwarns
#                await ctx.send(f"{user.name} has been superwarned for {reason}. Behave yourself or face the wrath of Quatara!! Superwarnings remaining = {3 - superwarns[user.id]}.")
#                with open("warns.json", "w") as f:
#                    json.dump(data, f)
#        else:
#            superwarns[str(user.id)] = 1
#            data[str(ctx.guild.id)]["Superwarns"] = superwarns
#            await ctx.send(f"{user.name} has been superwarned for {reason}. Behave yourself or face the wrath of Quatara!! Superwarnings remaining = {3 - superwarns[user.id]}.")
#            with open("warns.json", "w") as f:
#                json.dump(data, f)
#            
#    @superwarn.error
#    async def superwarnError(self, ctx, error):
#        if isinstance(error, commands.MissingPermissions):
#            await ctx.send("You tried to superwarn without permissions. Satan surely has a separate role reserved for you in hell.")
#
#    #A forgive command in case someone did a lot of good work and you are like, okay let's pardon this guy's warnings
#    @commands.command(description = "Clears the warnings from a redeemed soul. Good work, boi!")
#    @commands.has_permissions(kick_members = True)
#    async def forgive(self, ctx, user : discord.Member):
#        warns = {}
#        superwarns = {}
#        data = {}
#        with open("warns.json", "r") as f:
#            data = json.load(f)
#            warns = data[str(ctx.guild.id)]["Warn"]
#            superwarns = data[str(ctx.guild.id)]["Superwarns"]
#        if warns and superwarns:
#            if user.id in warns and superwarns:
#                warns.pop(user.id)
#                superwarns.pop(user.id)
#                await ctx.send(f"{user.name}, you have been forgiven for your good deeds from the sins of your pasts. You live as a free man now. Just remember: Try not to repeat the mistakes you made. Have a good day.")
#                data[str(ctx.guild.id)]["Warns"] = warns
#                data[str(ctx.guild.id)]["Superwarns"] = superwarns
#                with open("warns.json", "w") as f:
#                    json.dump(data,f)
#            elif user.id in warns:
#                warns.pop(user.id)
#                await ctx.send(f"{user.name}, you have been forgiven for your good deeds from the sins of your pasts. You live as a free man now. Just remember: Try not to repeat the mistakes you made. Have a good day.")
#                data[str(ctx.guild.id)]["Warns"] = warns
#                with open("warns.json", "w") as f:
#                    json.dump(data, f)
#            elif user.id in superwarns:
#                superwarns.pop(user.id)
#                await ctx.send(f"{user.name}, you have been forgiven for your good deeds from the sins of your pasts. You live as a free man now. Just remember: Try not to repeat the mistakes you made. Have a good day.")
#                data[str(ctx.guild.id)]["Superwarns"]
#                with open("warns.json", "w") as f:
#                    json.dump(data,f)
#            else:
#                await ctx.send("We can't find any warns for our good boi. I don't think he's sinned before, mind checking your records?")
#        else:
#            await ctx.send("We can't find any warns for our good boi. I don't think he's sinned before, mind checking your records?")
#
#    @forgive.error
#    async def forgiveError(self, ctx, error):
#        if isinstance(error, commands.MissingPermissions):
#            await ctx.send("You can't forgive when you don't have the power to. So don't try to act smart, it's scummy. And sus.")

    #A command to add spam channels.
    @commands.command(description = "Adds spam channels where spamming is allowed.")
    @commands.has_permissions(administrator = True)
    async def addspam(self, ctx, channel : discord.TextChannel):
        spam_channels = []
        with open("server_configs.json", "r") as f:
            data = json.load(f)
            spam_channels =data[str(ctx.guild.id)]["Spam Ignore"]
        if channel in spam_channels:
            await ctx.send("This channel already exists in our spam list.")
        else:
            data = {}
            with open("server_configs.json", "r") as f:
                data = json.load(f)

            data[str(ctx.guild.id)]["Spam Ignore"].append(channel.id)
            with open("server_configs.json", "w") as f:
                json.dump(data, f)
            
            await ctx.send(f"Spam channel has been added to our list. We shall ping the moderators on spams in {channel.name} from now on.")

    @addspam.error
    async def addspamError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not decide which channels I do not detect spam in! Begone thot!")

    #Aaaaaand another command to remove them
    @commands.command(description = "Removes a channel from spam channels where spamming is allowed.")
    @commands.has_permissions(administrator = True)
    async def rmspam(self, ctx, channel : discord.TextChannel):
        spam_channels =  []
        with open("server_configs.json", "r") as f:
            data = json.load(f)
            spam_channels = data[str(ctx.guild.id)]["Spam Ignore"]
        await ctx.send(spam_channels)
        if channel.id in spam_channels:
            data = {}
            with open("server_configs.json", "r") as f:
                data = json.load(f)
            data[str(ctx.guild.id)]["Spam Ignore"].remove(channel.id)
            with open("server_configs.json", "w") as f:
                json.dump(data, f)
            await ctx.send("Spam channel removed!!!")
        else:
            await ctx.send("The channel isn't in the list of channels where spamming is allowed. Look again, maybe?")

    @rmspam.error
    async def rmspamError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not decide which channels I detect spam in! Begone thot!")

    #Flips the spam on or off
    @commands.command(description = "Toggles the spam to on or off on your server. Gotta keep spammers at bay!")
    @commands.has_permissions(administrator = True)
    async def togglespam(self, ctx):
        data = {}
        with open("server_configs.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["Spam"] = not(data[str(ctx.guild.id)]["Spam"])
        truth = data[str(ctx.guild.id)]["Spam"]
        with open("server_configs.json", "w") as f:
            json.dump(data, f)
        await ctx.send(f"Spam detection has been set to {truth} on your server.")
    
    @togglespam.error
    async def tserror(self, ctx, error):
      if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the authorisation to decide to toggle the spam for this server! Next time, consult your superiors.")

    #Sets the Moderator role to be pinged when Spam occurs on your server
    @commands.command(description = "Sets the role to be mentioned when spam is detected on your server to start the spicy drama.")
    @commands.has_permissions(administrator = True)
    async def setMod(self, ctx, role : discord.Role):
        data = {}
        with open("role_configs.json", "r") as f:
            data = json.load(f)
        data[str(ctx.guild.id)]["Moderator"] = role.id

        with open("role_configs.json", "w") as f:
            json.dump(data, f)
        await ctx.send(f"Moderator role is now set to {role.mention}. This role will now be pinged when spam is detected.")

    @setMod.error
    async def sMerror(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Begone mortal! You cannot set the moderator role for this server! Have an admin try to use the command!")

    @commands.command(description = "Sets the Member role which is to logged to members when they join and removed when they are muted.")
    @commands.has_permissions(kick_members = True)
    async def setMember(self, ctx, role : discord.Role):
        data = {}
        with open("role_configs.json", "r") as f:
            data = json.load(f)
            data[str(ctx.guild.id)]["Member"] = role.id
        with open("role_configs.json", "w") as f:
            json.dump(data, f)
        await ctx.send(f"The Member role is now set to {role.mention}. This role will now be given to members when they join the server and will be taken away when muted.")

    @setMember.error
    async def sMembError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You cannot set the member role when your own role in the server is negligible. Begone!")

    @commands.command(description = "Sets the mute role to be given to members whence they are muted. Have to make a specification of disability to cause it, after all.")
    @commands.has_permissions(kick_members = True)
    async def setMute(self, ctx, role : discord.Role):
        data = {}
        with open("role_configs.json", "r") as f:
            data = json.load(f)
            data[str(ctx.guild.id)]["Mute"] = role.id
        with open("role_configs.json", "w") as f:
            json.dump(data, f)
        await ctx.send(f"The Muted role is now set to {role.mention}. This role will now be given to members when they are muted in replacement of the general Member role.")

    @setMute.error
    async def setMuteError(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You cannot set the muted role when your own role in the server is negligible. Begone!")

def setup(bot):
    bot.add_cog(Moderation(bot))