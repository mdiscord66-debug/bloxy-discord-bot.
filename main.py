import os
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("DISCORD_TOKEN")
URL = "https://bloxy.trade"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def parse_number(text):
    text = text.lower().replace(",", "").replace("$", "").strip()
    if "k" in text:
        return float(text.replace("k", "")) * 1000
    if "m" in text:
        return float(text.replace("m", "")) * 1_000_000
    return float(text)


def get_best_rate():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    deals = []

    # ⚠️ You may need to adjust selectors later
    listings = soup.find_all("div")

    for item in listings:
        text = item.get_text(" ", strip=True)

        if "$" in text and "k" in text.lower():
            parts = text.split()

            try:
                price = parse_number([p for p in parts if "$" in p][0])
                value = parse_number([p for p in parts if "k" in p.lower() or "m" in p.lower()][0])

                rate = (price / value) * 1000
                deals.append((price, value, rate))
            except:
                continue

    deals.sort(key=lambda x: x[2])
    return deals[:5]


@bot.command()
async def rate(ctx):
    await ctx.send("🔎 Checking best $ per 1K...")

    deals = get_best_rate()

    if not deals:
        await ctx.send("No deals found.")
        return

    embed = discord.Embed(title="💰 Best $ per 1K Rates", color=0x00ff99)

    for price, value, rate in deals:
        embed.add_field(
            name=f"${price} for {int(value)}",
            value=f"Rate: ${rate:.4f} per 1K",
            inline=False
        )

    await ctx.send(embed=embed)


bot.run(TOKEN)
