import nextcord
from nextcord.ext import commands
import glob, os
import sqlite3
from os import path
import datetime
from datetime import datetime, date, time, timezone, timedelta
import traceback
import requests, json, random, string
import asyncio
import openai
from time import sleep
import cloudscraper, requests, base64, json, time, os
from websocket import create_connection
import random
import re
from typing import Optional
from nextcord import SlashOption
from nextcord.ext import tasks
white = nextcord.Color.from_rgb(88, 101, 242)
conn = sqlite3.connect('whitelisted.sql')
c = conn.cursor()
cc = nextcord.Client()
scraper = cloudscraper.create_scraper()
auth = None

def create_key_database():
    sqlite3.connect('whitelisted.sql')
    c.execute('CREATE TABLE IF NOT EXISTS key(keys TEXT, duration_start VALUE)')
def create_table_redeemedkeys():
    c.execute('CREATE TABLE IF NOT EXISTS redeemed_keys(discord_id TEXT, key TEXT, duration VALUE)')
create_key_database()
create_table_redeemedkeys()

admin_list = [1052296146778865755]
channel = [1071837222082465844]

async def open_muted(user):
    users = await get_muted_data()
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["mute"] = 1
    with open("whitelisted.json", "w") as f:
        json.dump(users, f)
    return True

async def get_mute(user):
    await open_muted(user)
    users = await get_muted_data()
    wallet_amt = users[str(user.id)]['mute']
    return wallet_amt

async def get_muted_data():
    with open("whitelisted.json") as f:
        users = json.load(f)
    return users

async def add_mute(user):
    await open_muted(user)
    users = await get_muted_data()
    users[str(user.id)]['mute'] += 1
    with open("whitelisted.json", "w") as f:
        json.dump(users, f)

async def remove_mute(user):
    await open_muted(user)
    users = await get_muted_data()
    users[str(user.id)]['mute'] -= 1
    with open("whitelisted.json", "w") as f:
        json.dump(users, f)
        
class CheckMe(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Whitelist Verification",
            custom_id="persistent_modal:feedback",
            timeout=None,
        )
      
        self.rating = nextcord.ui.TextInput(
            label="Purchased Key",
            max_length=30,
            required = True,
            custom_id="persistent_modal:rating",
        )
        self.add_item(self.rating)

    async def callback(self, ctx: nextcord.Interaction):
      c.execute("SELECT * FROM key WHERE keys=?", (self.rating.value,))
      if not c.fetchone():
        embed = nextcord.Embed(title="Purchase Failed",description=(f"Key not found inside the database. You can either purchase one or open a support thread if you believe this is an issue.") , color=white)
        embed.set_footer(text='Thank you for using Pure!')
        await ctx.send(embed=embed, ephemeral=True)
      else:
        c.execute("SELECT * FROM key WHERE keys=?", (self.rating.value,))
        data = c.fetchall()
        subscription_length = data[0][1]
        discord_user = ctx.user.id
        key = data[0][0]
        embed = nextcord.Embed(title="Purchase Completed",description=(f"Thank you for your purchase {ctx.user.name}, your key has been redeemed. ({subscription_length} days)\n> :warning: Check subscription stats using `/stats`."),color=white)
        embed.set_footer(text='Thank you for using Pure!')
        await remove_mute(ctx.user)
        guild = ctx.guild
        role = guild.get_role(1063998344852152391)
        member = ctx.user
        await member.add_roles(role)
        await ctx.send(embed=embed, ephemeral=True)
        c.execute(f'DELETE from key WHERE keys=?', (self.rating.value,))
        conn.commit()
        embed = nextcord.Embed(title="Purchase Completed", description = (f"<:spark:1048283978781704222> Pure is a monthly subscription, you will lose your role every month and will require a renew if you want to keep using Pure.\n<:spark:1048283978781704222> Pure is not responsible for anything you do with this code.\n<:spark:1048283978781704222> Trade or selling Pure code is prohibited, we take this very seriously.\n\n> :warning: Thank you for purchasing Pure {ctx.user.name}, we hope you enjoy the service."), color=white)
        embed.set_footer(text='Thank you for purchasing Pure!')
        await ctx.user.send(f"{key}", embed=embed)
        c.execute(f"INSERT INTO redeemed_keys (discord_id, key, duration) VALUES('{discord_user}','{key}','{subscription_length}')")
        conn.commit()

class FeedbackModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Pure Feedback",
            custom_id="persistent_modal:feedback",
            timeout=None,
        )

        self.discovered = nextcord.ui.TextInput(
            label="How did you discover Pure?",
            placeholder="e.g. Discord server, friend, etc.",
            required=False,
            style=nextcord.TextInputStyle.paragraph,
            custom_id="persistent_modal:discovered",
        )
        self.add_item(self.discovered)

        self.rating = nextcord.ui.TextInput(
            label="What would you rate Pure out of 10?",
            placeholder="10",
            max_length=2,
            custom_id="persistent_modal:rating",
        )
        self.add_item(self.rating)

        self.improve = nextcord.ui.TextInput(
            label="How could we improve Pure?",
            placeholder="e.g. add more features, improve the UI, etc.",
            style=nextcord.TextInputStyle.paragraph,
            required=False,
            custom_id="persistent_modal:improve",
        )
        self.add_item(self.improve)

    async def callback(self, interaction: nextcord.Interaction):
        channel = bot.get_channel(1064246718822096947)
        embed = nextcord.Embed(title="Feedback Received!", description=f"> From {interaction.user.mention}\n> Rating us **{self.rating.value}**\n> Where they discovered the bot: {self.discovered.value}\n> How we could improve the bot: {self.improve.value}", colour=white)
        await channel.send(embed=embed)
        channelreview = bot.get_channel(1063941868552986715)
        embed = nextcord.Embed(title=f"{interaction.user.name} HAS JUST RATED US {self.rating.value}", description=f"> Thank you for the review, we appreciate everyone of you!", colour=white)
        await channelreview.send(embed=embed)

class Checkmeagainlol(nextcord.ui.View):
  def __init__(self,):
    super().__init__(timeout=120)
    self.value = None
  @nextcord.ui.button(label="Whitelist", style=nextcord.ButtonStyle.blurple)
  async def phoneverifyagain(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    self.value = True
    button.disabled = True
    await interaction.response.send_modal(CheckMe())

class Bot(commands.Bot):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.persistent_modals_added = False

  async def on_ready(self):
    if not self.persistent_modals_added:
      await bot.change_presence(status=nextcord.Status.dnd, activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=f"VR GirlFriend"))
    print(f"Logged in as {self.user} (ID: {self.user.id})")

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)

@bot.event
async def on_member_join(member):
    await member.send(f':wave: Hey {member.mention}, feel free to check out <#1064198326121152593> to gain access to Pure.')

def get_auth(bot, message):
    with open('tokens.json', 'r') as f:
      auth = json.load(f)
    try:
      return auth[str(message.user.id)]
    except KeyError:
      return 'nope'

@tasks.loop(hours=24)
async def my_loop():
    await asyncio.sleep(7)
    c.execute('UPDATE redeemed_keys SET duration = duration-1 WHERE duration>0')
    conn.commit()

@tasks.loop(minutes=30)
async def check_loop():
    await bot.wait_until_ready()
    await asyncio.sleep(8)
    duration_end = 0
    c.execute("SELECT * FROM redeemed_keys WHERE duration=?", (duration_end,))
    if not c.fetchone():
        print("No user's subscriptions have ended.")
    else:
        try:
            c.execute("SELECT * FROM redeemed_keys WHERE duration=?", (duration_end,))
            data = c.fetchall()
            print(data)
            expired_id = []
            length = (len(data))
            print(f"{length} users have had their license removed.")
            for i in range(length):
                add = data[i][0]
                expired_id.append(add)
            expired_user = len(expired_id)
            for i in range(expired_user):
                try:
                    user = expired_id[i]
                    user_id = (int(user))
                    await add_mute(user_id)
                    guild = bot.get_guild(1002355684769288212)
                    member = guild.get_member(user_id)
                    role = guild.get_role(1063998344852152391)
                    await member.remove_roles(role)
                    embed=nextcord.Embed(title="Subscription Ended",description=f"Hey {user.name}, thank you for purchasing Pure. Sadly your license has now expired and your access has been removed. If you wish to extend your license, please go to our store and [purchase](https://5ky.sellix.io/product/638d179e54980) a new one!",color=white)
                    embed.set_footer(text='Thank you for purchasing Pure!') 
                    await user.send(embed=embed)
                    c.execute("DELETE FROM redeemed_keys WHERE discord_id=?", (user_id,))
                    conn.commit()
                except:
                    print("Error user is no longer in server or cannot message them.")
        except:
            traceback.print_exc()

@bot.slash_command(name="convert",description="Convert Cookie to Bloxflip Auth.")
async def set(interaction: nextcord.Interaction, cookie: str = SlashOption(description="Roblox Cookie.", required=True)):
    if len(cookie) < 100:
        embed = nextcord.Embed(title="Authorisation Error", description=f"The Roblox cookie is too small and will not work. Use this plugin to get your cookie. ```https://www.editthiscookie.com/```", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    msg = await interaction.send("Processing..", ephemeral=True)
    request = scraper.post("https://rest-bf.blox.land/user/login", json={"cookie": cookie}).json()
    embed = nextcord.Embed(title="Authorisation Generated", description=f"```{request}```", colour=white)
    return await msg.edit(content = "", embed=embed)

@bot.slash_command(name="settings",description="Personal settings for Pure.")
async def set(interaction: nextcord.Interaction, auth: str = SlashOption(description="Bloxflip auth.", required=True)):
    if len(auth) < 50:
        embed = nextcord.Embed(title="Authorisation Error", description=f"This auth token is too small and will not work. We have not tested the token but from recent authorisation updates all tokens are over 50 characters long. [Tutorial Video](https://www.youtube.com/watch?v=BMFbW9giTuw&ab_channel=CodeWithWebDev). ```copy(localStorage.getItem('_DO_NOT_SHARE_BLOXFLIP_TOKEN'))```", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    with open('tokens.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(interaction.user.id)] = auth
    with open('tokens.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    embed = nextcord.Embed(title="Authorisation Set", description=f"This auth token will be used automatically when using any automated prediction. This can be changed at any time by rerunning this command with a new auth token.```{auth[:50]}...```", colour=white)
    return await interaction.send(embed=embed, ephemeral=True)

@bot.slash_command(name="roulette",description="Predict Bloxflip roulette.")
async def roulette(interaction: nextcord.Interaction):
    if interaction.channel.id not in channel:
        return await interaction.send("Wrong channel smart ass!")
    try:
        a = scraper.get('https://rest-bf.blox.land/games/roulette').json()['history'][0]['winningColor']
        b = scraper.get('https://rest-bf.blox.land/games/roulette').json()['history'][1]['winningColor']
        c = scraper.get('https://rest-bf.blox.land/games/roulette').json()['history'][2]['winningColor']
        past_Games = a, b, c
        rCount = past_Games.count("red")
        pCount = past_Games.count("purple")
        rChance = 100 - (rCount * 25)
        pChance = 100 - (pCount * 25)
        if rChance == 100:
            rChance -= 10
        elif pChance == 100:
            pChance -= 10
        if rChance > pChance:
            em = nextcord.Embed(color=white)
            em.set_image(url="https://cdn.discordapp.com/attachments/1055666025208741918/1064258590455627787/image.png")
            await interaction.send(embed=em, ephemeral=True)
        elif pChance > rChance:
            em = nextcord.Embed(color=white)
            em.set_image(url="https://cdn.discordapp.com/attachments/1055666025208741918/1064258590661152840/image.png")
            await interaction.send(embed=em, ephemeral=True)
    except:
        embed = nextcord.Embed(title="Roulette Error", description="Something went wrong with the scraper. Try again later!", colour=white)
        await interaction.send(embed=embed, ephemeral=True)

@bot.slash_command(name="check", description="Gets someones bloxflip player stats.")
async def check(interaction: nextcord.Interaction, username: str = SlashOption(description="Roblox username.", required=True)):
    if await get_mute(interaction.user) != 0:
        view = Checkmeagainlol()
        embed = nextcord.Embed(title="Unauthorized Member", description=f"Hey {interaction.user.name}, you are not whitelisted. Purchase a key [here](https://5ky.sellix.io/product/638d179e54980).", colour=white)
        return await interaction.send(embed=embed, ephemeral=True, view=view)
    try:
        get_userid = requests.get(f"https://api.roblox.com/users/get-by-username?username={username}").json()
        get_userid = str(get_userid["Id"])
        userID = get_userid
    except:
        em = nextcord.Embed(title=f"This user aint even played bloxflip before LOL!!!! L {username}, WE UP THO 💯💯💯!!", color=white)
        return await interaction.response.send_message(embed=em, ephemeral=True)
    headshot = scraper.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userID}&size=720x720&format=Png&isCircular=false").json()['data']
    general_bloxinfo = scraper.get(f"https://rest-bf.blox.land/user/lookup/{userID}").json()
    rank = general_bloxinfo['rank']
    wagered = int(general_bloxinfo['wager'])
    games_played = general_bloxinfo['gamesPlayed']
    rain_winnings = int(general_bloxinfo['rainWinnings'])
    trivia_Winnings = int(general_bloxinfo['triviaWinnings'])
    em = nextcord.Embed(color=white)
    em.set_thumbnail(url=headshot[0]['imageUrl'])
    em.add_field(name="**User ID**", value=f"```{userID}```")
    em.add_field(name="**Username**", value=f"```{username}```")
    em.add_field(name="**Rank**", value=f"```{rank}```")
    em.add_field(name="**Total Wagered**", value=f"```{wagered}```" + "\n")
    em.add_field(name="**Games Played**", value=f"```{games_played}```")
    em.add_field(name="**Rain Winnings**",value=f"```{str(rain_winnings)}```")
    em.add_field(name="**Trivia Winnings**",value=f"```{str(trivia_Winnings)}```")
    await interaction.response.send_message(embed=em, ephemeral=True)

key = ""
openai.api_key = key

@bot.slash_command(name="write", description="Use AI to generate text or something cool lol")
async def write(interaction, prompt: str = SlashOption(description="What should we generate?", required=True)):
    if await get_mute(interaction.user) != 0:
        view = Checkmeagainlol()
        embed = nextcord.Embed(title="Unauthorized Member", description=f"Hey {interaction.user.name}, you are not whitelisted. Purchase a key [here](https://5ky.sellix.io/product/638d179e54980).", colour=white)
        return await interaction.send(embed=embed, ephemeral=True, view=view)
    msg = await interaction.send("Thinking..", ephemeral=True)
    response = openai.Completion.create(engine='text-davinci-003', prompt=prompt, temperature=0.1, top_p=1, max_tokens=1000)
    try:
        await msg.edit(content='', embed=nextcord.Embed(title=f'AI response to {prompt}!', description="```" + response['choices'][0]['text'] + "```", color=white))
    except:
        await msg.edit(content=f'Failed to answer {prompt}.')

class Verification(nextcord.ui.View):
  def __init__(self):
    super().__init__()
    self.value = None
  @nextcord.ui.button(label="Verify", style=nextcord.ButtonStyle.green)
  async def endgame(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    guild = interaction.guild
    role = guild.get_role(1048290020353642606)
    member = interaction.user
    await member.add_roles(role)
    await interaction.send("Successfully Verified!", ephemeral=True)

class Change(nextcord.ui.View):
  def __init__(self):
    super().__init__()
    self.value = None
  @nextcord.ui.button(label="End Game", style=nextcord.ButtonStyle.green)
  async def endgame(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    self.value = True
    self.stop()

class Currency:
	def __init__(self):
		pass

	def Balance(auth):
		request = scraper.get("https://rest-bf.blox.land/user", headers={
						"x-auth-token": auth
				}).json()
		if not "user" in list(request):
			raise KeyError("Invalid authorization provided.")
		return request["user"]["wallet"]

	def Affiliate(auth):
		request = scraper.get("https://rest-bf.blox.land/user/affiliates", headers={
				"x-auth-token": auth
			}).json()
		if not "affiliateMoneyAvailable" in list(request):
			raise KeyError("Invalid authorization provided.")
		return request["affiliateMoneyAvailable"]

	def ClaimAfiliate(auth, amount):
		response = scraper.post("https://rest-bf.blox.land/user/affiliates/claim", headers={
									"x-auth-token": auth
								}, json={
									"amount": str(amount)
								})

		if response.status_code == 200:
			return True

		elif response.status_code == 429:
			raise Exception("Network error: Ratelimited, too many requests.")

		elif Currency.Affiliate(auth) < 100:
			raise Exception("Not enough funds to withdraw")

		else:
			raise KeyError("Invalid authorization provided.")

	def Withdraw(auth, amount):
		response = scraper.post("https://rest-bf.blox.land/user/withdrawTarget", headers={
								"x-auth-token": auth
							}, json={
								"amount": str(int(amount))
							})

		if not response.status_code == 200:
			raise Exception("Either you're withdrawing more than your balance or your auth is not connected to a valid cookie.")

class Mines:
	def __init__(self):
		pass

	def Create(betamount, mines, auth=None):
		response = scraper.post("https://rest-bf.blox.land/games/mines/create", 
								headers={
									"x-auth-token": auth
								}, 
								json={
									"betAmount": betamount,
									"mines": mines
								}
						)

		if betamount < 5:
			raise Exception("Bet amount must be greater than 5")


		if response.status_code == 429:
			raise KeyError("Ratelimited: Too many requests")

		if not response.status_code == 200:
			try:
				response.json()
			except:
				raise Exception("Network error.", "error")
			if response.json()["msg"] == "You already have an active mines game!":
				raise Exception("You already have an active mines game. End it then try again.")

		return response

	def Choose(choice, auth=None):
		response = scraper.post("https://rest-bf.blox.land/games/mines/action", 
								headers={
									"x-auth-token": auth
								},
								json={
									"cashout": False,
									"mine": choice
								}
						)
				

		if response.status_code == 429:
			raise KeyError("Ratelimited: Too many requests")

		if not response.status_code == 200:
			if response.json()["msg"] == "You do not have an active mines game!":
				raise Exception("There is currently no active mines game")
		return not response.json()["exploded"]

	def Cashout(auth):
		response = scraper.post("https://rest-bf.blox.land/games/mines/action", 
							headers={
								"x-auth-token": auth
							},
							json={
								"cashout": True,

							}
					)

		if not response.status_code == 200:
			if not "msg" in list(response.json()):
				raise KeyError("Invalid authorization provided.")

			elif response.json()["msg"] == "You do not have an active mines game!":
				raise Exception("You do not have an active mines game.")

			elif response.json()["msg"] == "You cannot cash out yet! You must uncover at least one tile!":
				raise Exception("You cannot cash out yet! You must uncover at least one tile!")

			return False

		return response

owner_list = [1052296146778865755]

@bot.command()
async def verify(interaction: nextcord.Interaction):
    if interaction.author.id in owner_list:
        await interaction.message.delete()
        embed = nextcord.Embed(title="Verification", description=f"> React to the button below to get verified!", colour=white)
        return await interaction.send(embed=embed, view=Verification())

@bot.slash_command(name = 'predict', description='Predict Bloxflip mines.')
async def predict(interaction: nextcord.Interaction):
    if interaction.channel.id not in channel:
        return await interaction.send("Wrong channel smart ass!")
    if get_auth(bot, interaction) == "nope":
        embed = nextcord.Embed(title="Missing Authorisation", description=f"Hey {interaction.user.name}, you have not set an auth token yet. No worries, you can do so by using the settings command. ```/settings```", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    auth = get_auth(bot, interaction)
    try:
        r = scraper.get('https://rest-bf.blox.land/games/mines/history', headers={"x-auth-token": auth}, params={ 'size': '1','page': '0',}  ) 
        mines_location = (r.json()['data'][0]['mineLocations'])
    except:
        letters = ["A","B","C","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        letter1 = random.choice(letters)
        letter2 = random.choice(letters)
        letter3 = random.choice(letters)
        letter4 = random.choice(letters)
        letter5 = random.choice(letters)
        error = (letter1+letter2+letter3+letter4+letter5)
        embed = nextcord.Embed(title=f"API Error {error}", description=f"Try starting a mines game without the predictor first. You may not have any past history.", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    grid = ['💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣']
    for x in mines_location:
        grid[x] = '🟩'
    em = nextcord.Embed(color=white)
    em.add_field(name='💸 Grid', value="\n" + "```"+grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+grid[12]+grid[13]+grid[14]+"\n"+grid[15]+grid[16]+grid[17] \
            +grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + "```\n", inline=False)
    await interaction.send(embed=em, ephemeral=True)

@bot.slash_command(name = 'premiumpredict', description='Predict Bloxflip mines.')
async def premiumpredict(interaction: nextcord.Interaction):
    if interaction.channel.id not in channel:
        return await interaction.send("Wrong channel smart ass!")
    if await get_mute(interaction.user) != 0:
        view = Checkmeagainlol()
        embed = nextcord.Embed(title="Unauthorized Member", description=f"Hey {interaction.user.name}, you are not whitelisted. Purchase a key [here](https://5ky.sellix.io/product/638d179e54980).", colour=white)
        return await interaction.send(embed=embed, ephemeral=True, view=view)
    if get_auth(bot, interaction) == "nope":
        embed = nextcord.Embed(title="Missing Authorisation", description=f"Hey {interaction.user.name}, you have not set an auth token yet. No worries, you can do so by using the settings command. ```/settings```", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    auth = get_auth(bot, interaction)
    try:
        r = scraper.get('https://rest-bf.blox.land/games/mines/history', headers={"x-auth-token": auth}, params={ 'size': '1','page': '0',}  ) 
        uuid = (r.json()['data'][0]['uuid'])
        mines_location = (r.json()['data'][0]['mineLocations']) 
        clicked_spots = (r.json()['data'][0]['uncoveredLocations'])
    except:
        letters = ["A","B","C","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        letter1 = random.choice(letters)
        letter2 = random.choice(letters)
        letter3 = random.choice(letters)
        letter4 = random.choice(letters)
        letter5 = random.choice(letters)
        error = (letter1+letter2+letter3+letter4+letter5)
        embed = nextcord.Embed(title=f"API Error {error}", description=f"Try starting a mines game without the predictor first. You may not have any past history.", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    grid = ['🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥']
    for x in mines_location:
        grid[x] = '💣'
    for x in clicked_spots:
        grid[x] = '🟩'
    em = nextcord.Embed(color=white)
    em.add_field(name='<a:loading:1055292996381331507> Previous Game', value="\n" + "```"+grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+grid[12]+grid[13]+grid[14]+"\n"+grid[15]+grid[16]+grid[17] \
            +grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + "```\n", inline=False)
    msg = await interaction.send(embed=em, ephemeral=True)
    await asyncio.sleep(3)
    grid = ['💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣','💣']
    roundId = int(''.join(filter(str.isdigit, uuid))) 
    roundNum = int(str(roundId)[:2])
    grid[int(roundNum / 4)] = '🟩'
    grid[int(roundNum / 5)] = '🟩'
    grid[int(roundNum / 7)] = '🟩'
    em = nextcord.Embed(color=white)
    em.add_field(name='💸 Grid', value="\n" + "```"+grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+grid[12]+grid[13]+grid[14]+"\n"+grid[15]+grid[16]+grid[17] \
            +grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + "```\n", inline=False)
    return await msg.edit("<#1063941868552986715>", embed=em)

def crashPoint(num):
    info = scraper.get('https://rest-bf.blox.land/games/crash').json()['history'][num]['crashPoint']
    return info

@bot.slash_command(name = 'crash', description='Predict Bloxflip crash.')
async def crash(interaction: nextcord.Interaction):
    if interaction.channel.id not in channel:
        return await interaction.send("Wrong channel smart ass!")
    one = crashPoint(0)
    two = crashPoint(1)
    three = crashPoint(2)
    pst3 = [one, two, three]
    average = sum(pst3) / len(pst3)
    prediction = (1 / (average - 2) / 1)
    if prediction < 1:
        prediction = 1. + prediction
    safe = ''
    if prediction > 3:
        safe = '2x'
    elif prediction < 3:
        safe = "1.5x"
    elif prediction > 4:
        safe = '4x'
    prediction = "{:.2f}".format(prediction)
    em = nextcord.Embed(color=white)
    em.add_field(name="<:spark:1048283978781704222> Prediction", value=f"> {prediction}x", inline=False)
    em.add_field(name="<:spark:1048283978781704222> Average", value=f"> {int(average)}x", inline=False)
    em.add_field(name="<:spark:1048283978781704222> Safe Bet", value=f"> {safe}", inline=False)
    await interaction.send(embed=em, ephemeral=True)

@bot.slash_command(name = 'feedback', description='Give us what we need.')
async def feedback(interaction: nextcord.Interaction):
    if await get_mute(interaction.user) != 0:
        view = Checkmeagainlol()
        embed = nextcord.Embed(title="Unauthorized Member", description=f"Hey {interaction.user.name}, you are not whitelisted. Purchase a key [here](https://5ky.sellix.io/product/638d179e54980).", colour=white)
        return await interaction.send(embed=embed, ephemeral=True, view=view)
    await interaction.response.send_modal(FeedbackModal())
    return await interaction.followup.send("Thank you for the review.", ephemeral=True)

@bot.slash_command(name = 'mines', description='Auto predict and play Bloxflip mines.')
async def mines(interaction: nextcord.Interaction, bet : int = SlashOption(description="How much should we bet?", required=True)):
    if interaction.channel.id not in channel:
        return await interaction.send("Wrong channel smart ass!")
    if await get_mute(interaction.user) != 0:
        view = Checkmeagainlol()
        embed = nextcord.Embed(title="Unauthorized Member", description=f"Hey {interaction.user.name}, you are not whitelisted. Purchase a key [here](https://5ky.sellix.io/product/638d179e54980).", colour=white)
        return await interaction.send(embed=embed, ephemeral=True, view=view)
    if get_auth(bot, interaction) == "nope":
        embed = nextcord.Embed(title="Missing Authorisation", description=f"Hey {interaction.user.name}, you have not set an auth token yet. No worries, you can do so by using the settings command. ```/settings```", colour=white)
        return await interaction.send(embed=embed, ephemeral=True)
    auth = get_auth(bot, interaction)
    if bet < 5:
        embed = nextcord.Embed(color=0xff0000)
        embed.add_field(name='🔎 Bet amount too low.', value="> Bet amount must be higher than 5!")
        return await interaction.send(embed=embed, ephemeral=True)
    try:
        balancebefore = Currency.Balance(auth=auth)
        start_game = Mines.Create(betamount=bet, mines=3, auth=auth)
        if start_game.status_code == 400:
            embed = nextcord.Embed(color=0xff0000)
            embed.add_field(name='🔎 Bet amount higher than balance.', value="> You do not have another balance to make that bet, or youre using more than 24 tokens.")
            return await interaction.send(embed=embed, ephemeral=True)
        if start_game.status_code == 429:
            embed = nextcord.Embed(color=0xff0000)
            embed.add_field(name='🔎 Ratelimited', value="> Youre using too many requests, try ease on the command usage.")
            return await interaction.send(embed=embed, ephemeral=True)
        if not start_game.status_code == 200:
            if start_game.json()["msg"] == "You already have an active mines game!":
                return await interaction.send("You already have an active mines game. End it then try again.")
    except:
        embed = nextcord.Embed(color=0xff0000)
        embed.add_field(name='🔎 Invalid Auth Token.', value="> We need your bloxflip auth token to start the mines game. Get it by pasting this into your [browser console](https://www.youtube.com/watch?v=BMFbW9giTuw&ab_channel=CodeWithWebDev). ```copy(localStorage.getItem('_DO_NOT_SHARE_BLOXFLIP_TOKEN'))```")
        return await interaction.send(embed=embed, ephemeral=True)
    embed = nextcord.Embed(title="🔎 Requesting APIs", description="> <a:loading:1055292996381331507> Please be patient.")
    start = await interaction.send(embed=embed, ephemeral=True)
    grid = ['🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥','🟥']
    tokens = 3
    r = scraper.get('https://rest-bf.blox.land/games/mines/history', headers={"x-auth-token": auth}, params={ 'size': '1','page': '0',}  ) 
    uuid = (r.json()['data'][0]['uuid'])
    roundId = int(''.join(filter(str.isdigit, uuid))) 
    roundNum = int(str(roundId)[:2])
    grid[int(roundNum / 4)] = '🟩'
    grid[int(roundNum / 5)] = '🟩'
    grid[int(roundNum / 7)] = '🟩'
    chance = random.randint(45,95)
    if tokens < 4:
        chance = chance - 15
    times = range(tokens)
    try:
        for x in times:
            try:
                a = int(roundNum / 4)
                b = int(roundNum / 5)
                c = int(roundNum / 7)
                Mines.Choose(choice=int(a), auth=auth)
                Mines.Choose(choice=int(b), auth=auth)
                Mines.Choose(choice=int(c), auth=auth)
            except:
                continue
    except:
        view = Change()
        embed = nextcord.Embed(color=0xff0000)
        embed.add_field(name='🔎 Failed to click mines.', value='> Click the button below to end the mines game and continue using Pure normally.')
        await start.edit(embed=embed, view=view)
        await view.wait()
        if view.value:
            Mines.Cashout(auth=auth)
            return await start.delete()
    try:
        Mines.Cashout(auth=auth)
        balance = Currency.Balance(auth=auth)
        difference = balance - balancebefore
        em = nextcord.Embed(color=white)
        em.add_field(name='🔎 You Won!', value=f'> <:spark:1048283978781704222> Before: **{round(balancebefore)}**\n> <:spark:1048283978781704222> After: **{round(balance)}** (+{round(difference)})', inline=False)
        em.add_field(name='💰 Profit', value=f'> {round(difference)}')
        em.add_field(name='💸 Grid', value="\n" + "```"+grid[0]+grid[1]+grid[2]+grid[3]+grid[4]+"\n"+grid[5]+grid[6]+grid[7]+grid[8]+grid[9]+"\n"+grid[10]+grid[11]+grid[12]+grid[13]+grid[14]+"\n"+grid[15]+grid[16]+grid[17] \
            +grid[18]+grid[19]+"\n"+grid[20]+grid[21]+grid[22]+grid[23]+grid[24] + "```\n", inline=False)
        await start.edit(embed=em)
    except:
        balance = Currency.Balance(auth=auth)
        difference = balancebefore - balance
        embed = nextcord.Embed(color=0xff0000)
        embed.add_field(name='🔎 You Lost!', value=f'> <:spark:1048283978781704222> Before: **{round(balancebefore)}**\n> <:spark:1048283978781704222> After: **{round(balance)}** (-{round(difference)})', inline=False)
        await start.edit(content="", embed=embed)

@bot.slash_command(name="subrem", description="Remove a users subscription.")
async def removesubscription(ctx, member: nextcord.Member = SlashOption(description="Buyer?", required=True), reason: str = SlashOption(description="Why is this user getting their subscription removed?", required=True)):
    if ctx.user.id in admin_list:
        discord_id = member.id
        c.execute("SELECT * FROM redeemed_keys WHERE discord_id=?", (discord_id,))
        if not c.fetchone():
            embed=nextcord.Embed(title="Subscription Error",description="User does not have a subscription.", color=white)
            embed.set_footer(text='Hello staff members!')
            await ctx.send(embed=embed, ephemeral=True)
        else:
            c.execute("DELETE FROM redeemed_keys WHERE discord_id=?", (discord_id,))
            conn.commit()
            embed=nextcord.Embed(title="Subscription Configuration Successful",description=f"Not having a valid reason for this removal can get you demoted.\n> <:spark:1048283978781704222> Successfully removed {member.name}'s subscription.",color=white)
            embed.set_footer(text='I will message them privately!') 
            await ctx.send(embed=embed, ephemeral=True)
            await add_mute(member)
            guild = ctx.guild
            role = guild.get_role(1063998344852152391)
            await member.remove_roles(role)
            embed=nextcord.Embed(title="System Notification",description=f"<:spark:1048283978781704222> Hey {member.name}, your subscription has been removed by **{ctx.user.name}**.\n> :warning: Reason: **{reason}**",color=white)
            embed.set_footer(text='This is appealable.') 
            await member.send(embed=embed)
    else:
      await ctx.send("Bro 🐒💩💀", ephemeral=True)

@bot.slash_command(name="sublif", description="Add a number of days to everyones subscription.")
async def sublif(ctx, amount: str = SlashOption(description="Why is this user getting their subscription removed?", required=True)):
    if ctx.user.id in admin_list:
        c.execute(f'UPDATE redeemed_keys SET duration = duration+{amount} WHERE duration>0')
        conn.commit()
        embed=nextcord.Embed(title="Subscription Configuration Successful",description=f"If this is not used suitably, you will be demoted.\n> <:spark:1048283978781704222> Successfully added **{amount}** days to everyone's license.",color=white)
        embed.set_footer(text=f'Wow, how kind of you {ctx.user.name}!')
        await ctx.send(embed=embed, ephemeral=True)
    else:
      await ctx.send("Bro 🐒💩💀", ephemeral=True)


@bot.slash_command(name="stats", description="Check your subscription.")
async def stats(ctx):
  if await get_mute(ctx.user) != 0:
    await ctx.send("Maybe [purchase](https://5ky.sellix.io/product/638d179e54980) Pure first.", ephemeral=True)
  else:
    id = ctx.user.id
    c.execute("SELECT * FROM redeemed_keys WHERE discord_id=?", (id,))
    data = c.fetchall()
    subscription_length = data[0][2]
    if subscription_length > 1:
      ohno = "good news!"
    else:
      ohno = "bad news!"
    timestamp = datetime.now()
    result = timestamp + timedelta(days=subscription_length)
    result = result.strftime('%d/%m/%Y')
    embed=nextcord.Embed(title=f"Subscription Successfully Fetched", description=f"Hey {ctx.user.name}, {ohno}\n> <:spark:1048283978781704222> You currently have **{subscription_length}** days remaining on your license. (**{result}**)", color=white)
    embed.set_footer(text='Thank you for purchasing Pure!')
    await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="subadd", description="Add days to a users subscription.")
async def addday(ctx, member: nextcord.Member = SlashOption(description="Buyer?", required=True), amount: int = SlashOption(description="How many days should I add?", required=True)):
    if ctx.user.id in admin_list:
        member_id = member.id
        c.execute("SELECT * FROM redeemed_keys WHERE discord_id=?", (member_id,))
        data = c.fetchall()
        current_amount_of_days = (data[0][2])
        c.execute(f'DELETE from redeemed_keys WHERE discord_id=?', (member_id,))
        conn.commit()
        new_days = (current_amount_of_days+amount)
        key = "updated amount"
        c.execute(f"INSERT INTO redeemed_keys (discord_id, key, duration) VALUES('{member_id}','{key}','{new_days}')")
        conn.commit()
        embed=nextcord.Embed(title="Subscription Configuration Successful",description=f"> <:spark:1048283978781704222> Successfully Added **{amount}** days to **{member.name}**'s subscription.", color=white)
        await member.send(f"**{ctx.user.name}** has added **{amount}** days to your subscription, say thank you!\n> :warning: Check how many days you have left using `/stats`.")
        embed.set_footer(text='What a lucky user!')
        await ctx.send(embed=embed, ephemeral=True)
    else:
      await ctx.send("Bro 🐒💩💀", ephemeral=True)   

@bot.slash_command(name="keycheck", description="Check if a key is valid.")
async def keycheck(ctx, key: str = SlashOption(description="Premium key.", required=True)):
    if ctx.user.id in admin_list:
        c.execute("SELECT * FROM key WHERE keys=?", (key,))
        if not c.fetchone():
            embed = nextcord.Embed(title="Key Invalid",description=(f"Key not found inside the database. That key does not exist!") , color=white)
            embed.set_footer(text='Staff are on top!')
            await ctx.send(embed=embed, ephemeral=True)
        else:
            c.execute("SELECT * FROM key WHERE keys=?", (key,))
            data = c.fetchall()
            subscription_length = data[0][1]
            key = data[0][0]
            embed = nextcord.Embed(title="Key Found",description=(f"That key is valid. ({subscription_length} days)\n> :warning: Do not leak keys or give them out unnecessary or it will result in a demote."),color=white)
            embed.set_footer(text='Staff are on top!')
            await ctx.send(embed=embed, ephemeral=True)

@bot.slash_command(name="redeem", description="Redeem a whitelist key for Pure.")
async def redeem(ctx, key: str = SlashOption(description="Purchased key.", required=True)):
  if await get_mute(ctx.user) == 0:
    await ctx.send("You already have an active subscription.", ephemeral=True)
    return
  c.execute("SELECT * FROM key WHERE keys=?", (key,))
  if not c.fetchone():
      embed = nextcord.Embed(title="Purchase Failed",description=(f"Key not found inside the database. You can either purchase one or open a support thread if you believe this is an issue.") , color=white)
      embed.set_footer(text='Thank you for using Pure!')
      await ctx.send(embed=embed, ephemeral=True)
  else:
    c.execute("SELECT * FROM key WHERE keys=?", (key,))
    data = c.fetchall()
    subscription_length = data[0][1]
    discord_user = ctx.user.id
    key = data[0][0]
    guild = ctx.guild
    role = guild.get_role(1063998344852152391)
    member = ctx.user
    await member.add_roles(role)
    embed = nextcord.Embed(title="Purchase Completed",description=(f"Thank you for your purchase {ctx.user.name}, your key has been redeemed. ({subscription_length} days)\n> :warning: Check subscription stats using `/stats`."),color=white)
    embed.set_footer(text='Thank you for using Pure!')
    await remove_mute(ctx.user)
    await ctx.send(embed=embed, ephemeral=True)
    c.execute(f'DELETE from key WHERE keys=?', (key,))
    conn.commit()
    embed = nextcord.Embed(title="Purchase Completed", description = (f"<:spark:1048283978781704222> Pure is a monthly subscription, you will lose your role every month and will require a renew if you want to keep using Pure.\n<:spark:1048283978781704222> Pure is not responsible for anything you do with this code.\n<:spark:1048283978781704222> Trade or selling Pure code is prohibited, we take this very seriously.\n\n> :warning: Thank you for purchasing Pure {ctx.user.name}, we hope you enjoy the service."), color=white)
    embed.set_footer(text='Thank you for purchasing Pure!')
    await ctx.user.send(f"{key}", embed=embed)
    c.execute(f"INSERT INTO redeemed_keys (discord_id, key, duration) VALUES('{discord_user}','{key}','{subscription_length}')")
    conn.commit()

@bot.slash_command(name="generatekey", description="Generate a whitelist key for Pure.")
async def generatekey(ctx, length: int = SlashOption(description="How many days?", required=True), custom: str = SlashOption(description="Custom Key.", required=False), member: nextcord.Member = SlashOption(description="Discord member to send the key.", required=False)):
    if ctx.user.id in admin_list:
      if custom == None:
        letters = ["A","B","C","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        letter1 = "P"
        letter2 = "R"
        letter3 = "E"
        letter4 = "D"
        letter5 = "I"
        letter6 = "C"
        letter7 = "T"
        letter8 = "O"
        letterR = "R"
        lettersep = "-"
        letter9 = random.choice(letters)
        letter10 = random.choice(letters)
        letter11 = random.choice(letters)
        letter12 = random.choice(letters)
        letter13 = random.choice(letters)
        letter14 = random.choice(letters)
        letter15 = random.choice(letters)
        letter16 = random.choice(letters)
        letter17 = random.choice(letters)
        letter18 = random.choice(letters)
        letter19 = random.choice(letters)
        letter20 = random.choice(letters)
        letter21 = random.choice(letters)
        letter22 = "P"
        letter23 = "U"
        letter24 = "R"
        letter25 = "E"
        code = (letter1+letter2+letter3+letter4+letter5+letter6+letter7+letter8+letterR+lettersep+letter9+letter10+letter11+letter12+letter13+letter14+letter15+letter16+letter17+letter18+letter19+letter20+letter21+lettersep+letter22+letter23+letter24+letter25)
        duration_start = length
        c.execute(f"INSERT INTO key (keys,duration_start) VALUES('{code}', {duration_start})")
        conn.commit()
        if member:
            try:
                embed = nextcord.Embed(title="Pure Key Generation", description=(f"<:spark:1048283978781704222> Days: **{duration_start}**\n<:spark:1048283978781704222> Key: **{code}**\n<:spark:1048283978781704222> Usage: **/redeem <key>**"), colour=white)
                await member.send(f"{code}", embed=embed)
                await member.send(f"{ctx.user.mention} has gifted you a {duration_start} day key!")
                await ctx.send("I have sent the key to the user!", ephemeral=True)
            except:
                await ctx.send("User does not have DMs open!", ephemeral=True)
        else:
            embed = nextcord.Embed(title="Pure Key Generation",description=(f"<:spark:1048283978781704222> Days: **{duration_start}**\n<:spark:1048283978781704222> Key: **{code}**\n<:spark:1048283978781704222> Usage: **/redeem <key>**"), colour=white)
            await ctx.send(f"{code}", embed=embed, ephemeral=True)
      else:
        duration_start = length
        c.execute(f"INSERT INTO key (keys,duration_start) VALUES('{custom}', {duration_start})")
        conn.commit()
        if member:
            try:
                embed = nextcord.Embed(title="Pure Key Generation", description=(f"<:spark:1048283978781704222> Days: **{duration_start}**\n<:spark:1048283978781704222> Key: **{custom}**\n<:spark:1048283978781704222> Usage: **/redeem <key>**"), colour=white)
                await member.send(f"{custom}", embed=embed)
                await member.send(f"{ctx.user.mention} has gifted you a {duration_start} day key!")
                await ctx.send("I have sent the key to the user!", ephemeral=True)
            except:
                await ctx.send("User does not have DMs open!", ephemeral=True)
        else:
            embed = nextcord.Embed(title="Pure Key Generation",description=(f"<:spark:1048283978781704222> Days: **{duration_start}**\n<:spark:1048283978781704222> Key: **{custom}**\n<:spark:1048283978781704222> Usage: **/redeem <key>**"), colour=white)
            await ctx.send(f"{custom}", embed=embed, ephemeral=True)
    else:
      await ctx.send("Bro 🐒💩💀", ephemeral=True)

bot.run("")
