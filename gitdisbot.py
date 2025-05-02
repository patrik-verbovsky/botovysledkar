import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
import json
import os
import matplotlib.pyplot as plt

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SAVE_FILE = "vysledky.json"
KALENDAR_FILE = "kalendar.json"

# ---------------------------- Výsledky ----------------------------------

def load_all_games():
    if not os.path.exists(SAVE_FILE):
        return []
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_game_result(game_data):
    games = load_all_games()
    games.append(game_data)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)

def get_total_scores():
    games = load_all_games()
    scores = {}
    for game in games:
        for p in game["players"]:
            scores[p["jmeno"]] = scores.get(p["jmeno"], 0) + p["body"]
    return scores

# ---------------------------- Kalendář ----------------------------------

def load_events():
    if not os.path.exists(KALENDAR_FILE):
        return []
    with open(KALENDAR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_events(events):
    with open(KALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

@bot.tree.command(name="pridej_udalost", description="Přidá událost do kalendáře")
@app_commands.describe(popis="Popis události", datum="Datum a čas ve formátu dd.mm.yyyy_hh:mm")
async def pridej_udalost(interaction: discord.Interaction, popis: str, datum: str):
    try:
        dt = datetime.strptime(datum, "%d.%m.%Y_%H:%M")
    except ValueError:
        await interaction.response.send_message("❌ Neplatný formát data. Použij `dd.mm.yyyy_hh:mm`.")
        return

    events = load_events()
    event_id = len(events) + 1
    events.append({"id": event_id, "popis": popis, "datetime": dt.strftime("%Y-%m-%d %H:%M")})
    save_events(events)

    await interaction.response.send_message(f"✅ Událost přidána: **{popis}** dne {dt.strftime('%d.%m.%Y %H:%M')}.")

@bot.tree.command(name="udalosti", description="Zobrazí nadcházející události")
async def udalosti(interaction: discord.Interaction):
    events = load_events()
    if not events:
        await interaction.response.send_message("📭 Žádné naplánované události.")
        return

    output = "📅 Nadcházející události\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for e in sorted(events, key=lambda x: x["datetime"]):
        output += f"🆔 {e['id']:>2} │ {e['datetime']} – {e['popis']}\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━"
    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="smaz_udalost", description="Smaže událost podle ID")
@app_commands.describe(udalost_id="ID události k odstranění")
async def smaz_udalost(interaction: discord.Interaction, udalost_id: int):
    events = load_events()
    new_events = [e for e in events if e["id"] != udalost_id]

    if len(new_events) == len(events):
        await interaction.response.send_message("❌ Událost s tímto ID nebyla nalezena.")
        return

    save_events(new_events)
    await interaction.response.send_message(f"🗑️ Událost ID {udalost_id} smazána.")

# ---------------------------- Ankety ----------------------------------

@bot.tree.command(name="anketa", description="Vytvoří jednoduchou anketu")
@app_commands.describe(otazka="Otázka pro anketu", moznosti="Odděl možnosti čárkou (např. Ano,Ne,Možná)")
async def anketa(interaction: discord.Interaction, otazka: str, moznosti: str):
    options = [m.strip() for m in moznosti.split(",") if m.strip()]
    if not 2 <= len(options) <= 10:
        await interaction.response.send_message("❌ Zadej 2–10 možností.")
        return

    emoji_list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    output = f"📊 **{otazka}**\n\n"
    for i, option in enumerate(options):
        output += f"{emoji_list[i]} {option}\n"

    message = await interaction.response.send_message(output)
    for i in range(len(options)):
        await (await message).add_reaction(emoji_list[i])

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SAVE_FILE = "vysledky.json"

def load_all_games():
    if not os.path.exists(SAVE_FILE):
        return []
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            return []

def save_game_result(game_data):
    games = load_all_games()
    games.append(game_data)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)

def get_total_scores():
    games = load_all_games()
    scores = {}
    for game in games:
        for p in game["players"]:
            scores[p["jmeno"]] = scores.get(p["jmeno"], 0) + p["body"]
    return scores

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot je online jako {bot.user}")

@bot.tree.command(name="vysledky", description="Zobrazí výsledky hráčů a ukládá je")
@app_commands.describe(
    hrac1="Zadej ve formátu jméno/bodů",
    hrac2="Volitelný hráč", hrac3="Volitelný hráč", hrac4="Volitelný hráč",
    hrac5="Volitelný hráč", hrac6="Volitelný hráč", hrac7="Volitelný hráč",
    hrac8="Volitelný hráč", hrac9="Volitelný hráč", hrac10="Volitelný hráč",
    cas="Volitelné datum a čas ve formátu dd.mm.yyyy_hh:mm"
)
async def vysledky(
    interaction: discord.Interaction,
    hrac1: str,
    hrac2: Optional[str] = None, hrac3: Optional[str] = None,
    hrac4: Optional[str] = None, hrac5: Optional[str] = None,
    hrac6: Optional[str] = None, hrac7: Optional[str] = None,
    hrac8: Optional[str] = None, hrac9: Optional[str] = None,
    hrac10: Optional[str] = None,
    cas: Optional[str] = None
):
    await interaction.response.defer()
    args = [hrac1, hrac2, hrac3, hrac4, hrac5, hrac6, hrac7, hrac8, hrac9, hrac10]
    players = []

    for arg in args:
        if arg:
            try:
                jmeno, body = arg.split('/')
                body = int(body.strip())
                jmeno = jmeno.strip()
                players.append((jmeno, body))
            except:
                await interaction.followup.send(f"❌ Chybný formát u `{arg}`. Použij `jméno/bodů`.")
                return

    if cas:
        try:
            now = datetime.strptime(cas, "%d.%m.%Y_%H:%M")
        except ValueError:
            await interaction.followup.send("❌ Špatný formát času. Použij `dd.mm.yyyy_hh:mm`.")
            return
    else:
        now = datetime.now()

    game_data = {
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
        "players": [{"jmeno": j, "body": b} for j, b in players]
    }
    save_game_result(game_data)

    formatted_time = now.strftime("%d.%m.%Y %H:%M")
    players.sort(key=lambda x: x[1], reverse=True)

    ranks = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "1️⃣0️⃣"]
    max_name_len = max((len(jmeno) for jmeno, _ in players), default=20)

    output = f"📊 Výsledky\n📅 {formatted_time}\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━\n"

    for i, (jmeno, body) in enumerate(players):
        rank = ranks[i] if i < len(ranks) else f"{i+1}"
        output += f"{rank} {jmeno.ljust(max_name_len)} │ {str(body).rjust(3)} b\n"

    output += "━━━━━━━━━━━━━━━━━━━━━━"
    await interaction.followup.send(f"```\n{output}\n```")

@bot.tree.command(name="tabulka", description="Zobrazí celkovou tabulku hráčů")
async def tabulka(interaction: discord.Interaction):
    scores = get_total_scores()
    if not scores:
        await interaction.response.send_message("⚠️ Zatím nejsou uloženy žádné výsledky.")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    max_name_len = max(len(jmeno) for jmeno, _ in sorted_scores)
    output = f"📈 Celkové výsledky\n━━━━━━━━━━━━━━━━━━━━━━\n"

    for i, (jmeno, body) in enumerate(sorted_scores):
        rank = f"{i+1:>2}."
        output += f"{rank} {jmeno.ljust(max_name_len)} │ {str(body).rjust(4)} b\n"

    output += "━━━━━━━━━━━━━━━━━━━━━━"
    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="historie", description="Zobrazí historii her podle data")
@app_commands.describe(
    den="Filtruj podle dne ve formátu dd.mm.yyyy (volitelné)",
    cas="Volitelný časový filtr hh:mm (ukáže pouze hry po tomto čase)"
)
async def historie(interaction: discord.Interaction, den: Optional[str] = None, cas: Optional[str] = None):
    games = load_all_games()
    filtered = []

    try:
        date_filter = datetime.strptime(den, "%d.%m.%Y").date() if den else None
        time_filter = datetime.strptime(cas, "%H:%M").time() if cas else None
    except ValueError:
        await interaction.response.send_message("❌ Neplatný formát filtru. Použij `dd.mm.yyyy` a/nebo `hh:mm`.")
        return

    for game in games:
        dt = datetime.strptime(game["datetime"], "%Y-%m-%d %H:%M")
        if date_filter and dt.date() != date_filter:
            continue
        if time_filter and dt.time() < time_filter:
            continue
        filtered.append(game)

    if not filtered:
        await interaction.response.send_message("🔍 Žádné výsledky pro zadané filtry.")
        return

    output = "🕓 Filtrované hry\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for game in filtered[-5:]:
        output += f"📅 {game['datetime']}\n"
        sorted_players = sorted(game["players"], key=lambda x: x["body"], reverse=True)
        for i, p in enumerate(sorted_players):
            rank = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            output += f"{rank} {p['jmeno']} │ {p['body']} b\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━\n"

    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="statistiky", description="Zobrazí statistiky jednoho hráče")
@app_commands.describe(jmeno="Jméno hráče")
async def statistiky(interaction: discord.Interaction, jmeno: str):
    games = load_all_games()
    stats = [p["body"] for g in games for p in g["players"] if p["jmeno"].lower() == jmeno.lower()]

    if not stats:
        await interaction.response.send_message(f"❌ Hráč `{jmeno}` nebyl nalezen v žádné hře.")
        return

    total = sum(stats)
    average = total / len(stats)
    best = max(stats)

    output = (
        f"📊 Statistiky pro **{jmeno}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕹️ Počet her: {len(stats)}\n"
        f"📈 Celkem bodů: {total}\n"
        f"📊 Průměr: {average:.2f} b\n"
        f"🏆 Nejvyšší skóre: {best} b\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="mvp", description="Zobrazí hráče s nejvíce výhrami")
async def mvp(interaction: discord.Interaction):
    games = load_all_games()
    wins = {}

    for game in games:
        sorted_players = sorted(game["players"], key=lambda x: x["body"], reverse=True)
        winner = sorted_players[0]["jmeno"]
        wins[winner] = wins.get(winner, 0) + 1

    if not wins:
        await interaction.response.send_message("❌ Zatím nejsou žádné výhry.")
        return

    sorted_winners = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    output = "🏅 MVP (počet 1. míst)\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, (jmeno, pocet) in enumerate(sorted_winners):
        output += f"{i+1:>2}. {jmeno} │ {pocet} výher\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━"
    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="topza", description="Zobrazí tabulku hráčů za konkrétní den")
@app_commands.describe(den="Datum ve formátu dd.mm.yyyy")
async def topza(interaction: discord.Interaction, den: str):
    try:
        target_date = datetime.strptime(den, "%d.%m.%Y").date()
    except ValueError:
        await interaction.response.send_message("❌ Neplatný formát data. Použij `dd.mm.yyyy`.")
        return

    games = load_all_games()
    scores = {}

    for g in games:
        dt = datetime.strptime(g["datetime"], "%Y-%m-%d %H:%M")
        if dt.date() == target_date:
            for p in g["players"]:
                scores[p["jmeno"]] = scores.get(p["jmeno"], 0) + p["body"]

    if not scores:
        await interaction.response.send_message("❌ Žádné výsledky pro tento den.")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    output = f"📆 Výsledky za {den}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, (jmeno, body) in enumerate(sorted_scores):
        output += f"{i+1:>2}. {jmeno} │ {body} b\n"
    output += "━━━━━━━━━━━━━━━━━━━━━━"
    await interaction.response.send_message(f"```\n{output}\n```")

@bot.tree.command(name="graf", description="Vygeneruje graf skóre hráče v čase")
@app_commands.describe(jmeno="Jméno hráče")
async def graf(interaction: discord.Interaction, jmeno: str):
    await interaction.response.defer()
    games = load_all_games()
    data = []

    for g in games:
        dt = datetime.strptime(g["datetime"], "%Y-%m-%d %H:%M")
        for p in g["players"]:
            if p["jmeno"].lower() == jmeno.lower():
                data.append((dt, p["body"]))

    if not data:
        await interaction.followup.send(f"❌ Žádná data pro hráče `{jmeno}`.")
        return

    data.sort(key=lambda x: x[0])
    x = [d[0] for d in data]
    y = [d[1] for d in data]

    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title(f"Vývoj skóre: {jmeno}")
    plt.xlabel("Datum")
    plt.ylabel("Skóre")
    plt.xticks(rotation=45)
    plt.tight_layout()

    filepath = f"/tmp/{jmeno}_graf.png"
    plt.savefig(filepath)
    plt.close()

    await interaction.followup.send(file=discord.File(filepath))

bot.run('váš klíč/your token')
