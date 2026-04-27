import discord

TOKEN = "MTQ5ODI0Njg0MzcxNTI4OTEyOA.G2GnhJ.9l7C6cSQ_OrTNwJ_u2vFrXMzVrGl7CkduSdteA"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Přihlášen jako {client.user}")

    channel = client.get_channel(1498249205385269489)  
    await channel.send("Bot spuštěn ✅")

client.run(TOKEN)
