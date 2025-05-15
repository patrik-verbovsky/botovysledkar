import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional
import json
import os
import calendar
import matplotlib.pyplot as plt
import uuid

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

KALENDAR_FILE = "kalendar.json"
ANKETY_FILE = "ankety.json"


def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@bot.tree.command(name="kalendar", description="Zobrazí události na dalších 7 dní")
async def kalendar(interaction: discord.Interaction):
    today = datetime.now()
    upcoming_limit = today.replace(hour=23, minute=59, second=59) + timedelta(days=7)

    events = load_json(KALENDAR_FILE)
    upcoming_events = []

    for e in events:
        try:
            dt = datetime.strptime(e["datetime"], "%Y-%m-%d %H:%M")
        except:
            continue
        if today <= dt <= upcoming_limit:
            upcoming_events.append((dt, e))

    if not upcoming_events:
        await interaction.response.send_message("📭 Žádné naplánované události v následujících 7 dnech.")
        return

    upcoming_events.sort(key=lambda x: x[0])

    await interaction.response.send_message("📌 Zobrazeny nadcházející události:", ephemeral=True)

    for dt, e in upcoming_events:
        attending = [f"<@{uid}>" for uid, v in e.get("rsvp", {}).items() if v.startswith("✅")]
        not_attending = [f"<@{uid}>" for uid, v in e.get("rsvp", {}).items() if v.startswith("❌")]

        embed = discord.Embed(
            title=f"📅 Událost – {dt.strftime('%d.%m.%Y %H:%M')}",
            description=f"**{e['popis']}**\n━━━━━━━━━━━━━━━━━━━━━━",
            color=0x2ecc71
        )
        embed.add_field(name="✅ Zúčastní se", value="\n".join(attending) or "Nikdo", inline=True)
        embed.add_field(name="❌ Nezúčastní se", value="\n".join(not_attending) or "Nikdo", inline=True)
        embed.set_footer(text="Klikni na tlačítka níže pro odpověď nebo nastavení.")

        view = RSVPView(e["id"], allow_settings=True)
        await interaction.channel.send(embed=embed, view=view)



class RSVPView(discord.ui.View):
    def __init__(self, event_id, allow_settings=False):
        super().__init__(timeout=None)
        self.event_id = event_id
        if allow_settings:
            self.add_item(SettingsButton(event_id))

    @discord.ui.button(label="✅ Zúčastním se", style=discord.ButtonStyle.success, custom_id="rsvp_yes")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_response(interaction, "✅ Zúčastní se")

    @discord.ui.button(label="❌ Nezúčastním se", style=discord.ButtonStyle.danger, custom_id="rsvp_no")
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_response(interaction, "❌ Nezúčastní se")

    async def _handle_response(self, interaction, response):
        events = load_json(KALENDAR_FILE)
        updated = False
        for e in events:
            if e["id"] == self.event_id:
                e.setdefault("rsvp", {})[str(interaction.user.id)] = response
                updated = True
                break
        if updated:
            save_json(KALENDAR_FILE, events)

            attending = []
            not_attending = []
            for user_id, status in e["rsvp"].items():
                if status.startswith("✅"):
                    attending.append(f"<@{user_id}>")
                elif status.startswith("❌"):
                    not_attending.append(f"<@{user_id}>")

            embed = discord.Embed(title="📅 Událost", description=e["popis"], color=0x5865f2)
            embed.add_field(name="🕒 Datum", value=e["datetime"], inline=False)
            embed.add_field(name="✅ Zúčastní se", value="\n".join(attending) or "Nikdo", inline=True)
            embed.add_field(name="❌ Nezúčastní se", value="\n".join(not_attending) or "Nikdo", inline=True)

            await interaction.message.edit(embed=embed, view=self)
        else:
            await interaction.response.send_message("❌ Událost nenalezena.", ephemeral=True)


class SettingsButton(discord.ui.Button):
    def __init__(self, event_id):
        super().__init__(label="⚙️ Nastavení", style=discord.ButtonStyle.secondary)
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ Nastavení události",
            description="Zde můžeš upravit událost:\n\n📝 Změnit popis\n🕒 Změnit čas\n🗑️ Smazat událost",
            color=0xf1c40f
        )
        await interaction.response.send_message(embed=embed, view=SettingsView(self.event_id), ephemeral=True)


class SettingsView(discord.ui.View):
    def __init__(self, event_id):
        super().__init__(timeout=180)
        self.event_id = event_id

    @discord.ui.button(label="📝 Změnit popis", style=discord.ButtonStyle.primary)
    async def change_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeDescriptionModal(self.event_id))

    @discord.ui.button(label="🕒 Změnit čas", style=discord.ButtonStyle.secondary)
    async def change_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeTimeModal(self.event_id))

    @discord.ui.button(label="🗑️ Smazat událost", style=discord.ButtonStyle.danger)
    async def delete_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        events = load_json(KALENDAR_FILE)
        for i, e in enumerate(events):
            if e["id"] == self.event_id:
                events.pop(i)
                save_json(KALENDAR_FILE, events)
                await interaction.response.send_message("🗑️ Událost byla smazána.", ephemeral=True)
                return
        await interaction.response.send_message("❌ Událost nenalezena.", ephemeral=True)

class ChangeDescriptionModal(discord.ui.Modal, title="Změnit popis události"):
    novy_popis = discord.ui.TextInput(label="Nový popis", max_length=200)

    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id

    async def on_submit(self, interaction: discord.Interaction):
        events = load_json(KALENDAR_FILE)
        for e in events:
            if e["id"] == self.event_id:
                e["popis"] = self.novy_popis.value
                save_json(KALENDAR_FILE, events)
                await interaction.response.send_message("✅ Popis události byl změněn.", ephemeral=True)
                return
        await interaction.response.send_message("❌ Událost nenalezena.", ephemeral=True)


class ChangeTimeModal(discord.ui.Modal, title="Změnit čas události"):
    novy_cas = discord.ui.TextInput(label="Nový čas (dd.mm.yyyy_hh:mm)")

    def __init__(self, event_id):
        super().__init__()
        self.event_id = event_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            dt = datetime.strptime(self.novy_cas.value, "%d.%m.%Y_%H:%M")
        except ValueError:
            await interaction.response.send_message("❌ Špatný formát času.", ephemeral=True)
            return

        events = load_json(KALENDAR_FILE)
        for e in events:
            if e["id"] == self.event_id:
                e["datetime"] = dt.strftime("%Y-%m-%d %H:%M")
                save_json(KALENDAR_FILE, events)
                await interaction.response.send_message("✅ Čas události byl změněn.", ephemeral=True)
                return
        await interaction.response.send_message("❌ Událost nenalezena.", ephemeral=True)


@bot.tree.command(name="pridat_udalost", description="Přidá novou událost do kalendáře")
@app_commands.describe(
    popis="Popis události",
    termin="Datum a čas ve formátu dd.mm.yyyy_hh:mm"
)
async def pridat_udalost(interaction: discord.Interaction, popis: str, termin: str):
    try:
        dt = datetime.strptime(termin, "%d.%m.%Y_%H:%M")
    except ValueError:
        await interaction.response.send_message("❌ Nesprávný formát data. Použij `dd.mm.yyyy_hh:mm`.")
        return

    events = load_json(KALENDAR_FILE)
    for e in events:
        existing_dt = datetime.strptime(e["datetime"], "%Y-%m-%d %H:%M")
        if existing_dt == dt:
            await interaction.response.send_message("⚠️ V tomto termínu už existuje jiná událost.")
            return

    event_id = str(uuid.uuid4())
    new_event = {
        "id": event_id,
        "popis": popis,
        "datetime": dt.strftime("%Y-%m-%d %H:%M"),
        "rsvp": {}
    }

    events.append(new_event)
    save_json(KALENDAR_FILE, events)

    embed = discord.Embed(title="📅 Nová událost", description=popis, color=0x00b0f4)
    embed.add_field(name="🕒 Datum", value=dt.strftime("%d.%m.%Y %H:%M"), inline=False)

    view = RSVPView(event_id, allow_settings=True)
    await interaction.response.send_message("✅ Událost byla přidána:")
    await interaction.channel.send(embed=embed, view=view)
class AnketaView(discord.ui.View):
    def __init__(self, otazka, moznosti, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.otazka = otazka
        self.moznosti = moznosti
        self.hlasovani = {}  # user_id -> moznost
        self.interaction = interaction
        for moznost in moznosti:
            self.add_item(AnketaButton(moznost, self))

    async def update_embed(self):
        counts = {m: 0 for m in self.moznosti}
        for hlas in self.hlasovani.values():
            counts[hlas] += 1
        total = sum(counts.values())
        lines = []
        for moznost in self.moznosti:
            count = counts[moznost]
            percent = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percent / 10)
            lines.append(f"**{moznost}**: {count} hlasů | {bar} {percent:.1f}%")
        embed = discord.Embed(title="📊 Anketa", description=self.otazka, color=0x3498db)
        embed.add_field(name="Výsledky", value="\n".join(lines), inline=False)
        await self.interaction.edit_original_response(embed=embed, view=self)
class AnketaButton(discord.ui.Button):
    def __init__(self, moznost, view: AnketaView):
        super().__init__(label=moznost, style=discord.ButtonStyle.secondary)
        self.moznost = moznost
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.hlasovani[str(interaction.user.id)] = self.moznost
        await interaction.response.send_message(f"Hlasovali jste pro: **{self.moznost}**", ephemeral=True)
        await self.view_ref.update_embed()


class AnketaView(discord.ui.View):
    def __init__(self, otazka, moznosti, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.otazka = otazka
        self.moznosti = moznosti
        self.hlasovani = {}  # user_id -> moznost
        self.interaction = interaction
        for moznost in moznosti:
            self.add_item(AnketaButton(moznost, self))

    async def update_embed(self):
        counts = {m: 0 for m in self.moznosti}
        for hlas in self.hlasovani.values():
            counts[hlas] += 1
        total = sum(counts.values())
        lines = []
        for moznost in self.moznosti:
            count = counts[moznost]
            percent = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percent / 10)
            hlasujici = [f"<@{uid}>" for uid, v in self.hlasovani.items() if v == moznost]
            lines.append(f"**{moznost}**: {count} hlasů | {bar} {percent:.1f}%\n{', '.join(hlasujici)}")
        embed = discord.Embed(title="📊 Anketa", description=self.otazka, color=0x3498db)
        embed.add_field(name="Výsledky", value="\n\n".join(lines), inline=False)
        await self.interaction.edit_original_response(embed=embed, view=self)

@bot.tree.command(name="anketa", description="Vytvoří anketu s tlačítky")
@app_commands.describe(otazka="Otázka pro anketu", moznosti="Možnosti oddělené čárkou (např. Ano,Ne,Možná)")
async def anketa(interaction: discord.Interaction, otazka: str, moznosti: str):
    options = [m.strip() for m in moznosti.split(",") if m.strip()]
    if not 2 <= len(options) <= 5:
        await interaction.response.send_message("❌ Zadej 2–5 možností.")
        return

    view = AnketaView(otazka, options, interaction)
    embed = discord.Embed(title="📊 Anketa", description=otazka, color=0x3498db)
    embed.add_field(name="Výsledky", value="Zatím nikdo nehlasoval.", inline=False)
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot je online jako {bot.user}")


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

bot.run('your bot token here/váš token k botovi zde')
