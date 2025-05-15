# Botový výsledkář
Tento bot byl vyroben pro jeden Discord server, na kterém se ale už nepoužívá, tak ho tedy zveřejňuji i s návodem zde.
<br>Bot umí: 
- kalendář s nastavením, účastí
- výsledky s grafy, tabulkami, historií, podrobnými statistikami
- ankety pomocí tlačítek
- a další...

## Nastavení
### 1. Stáhnutí souboru
Nejprve si soubor musíte stáhnout buď přes ```git clone```, stáhnutí ZIPu zde na GH, nebo stáhnutí daného souboru.
Pro ušetření místa na disku doporučuji stáhnout minifikovanou verzi. Je třeba mít nainstalovaný Python 3.12, matplotlib (pip příkaz: ```pip3 install matplotlib```) a pro uživatele macOS také certifikáty pro HTTPS.

### 2. Získání tokenu + vytvoření aplikace na DC dev portalu
Pro použití bota potřebujete token, ten zjistíte tak, že po přidání nové aplikace na ni kliknete, půjdete do sekce Bot a stisknete tlačítko ```Reset token```. Token si zkopírujte a vložte do souboru na poslední řádek, tedy to bude vypadat následovně: <br> ```bot.run('your bot token here/váš token k botovi zde')``` => ```bot.run('MihgJJfdsjoiFEHI8473743......')```

### 3. Permissions a invite do serveru
Na Discord Developer portálu v sekci Bot zapnete ```Message Content Intent```, pro odkaz přejděte do sekce OAuth2 a vyberte následující možnosti: ```bot```, ```applications.commands```, ```Send Messages```, ```Read Message History```. (Pokud by vám tento postup nefungoval, zkuste označit všechny možnosti v Text Permissions, popřípadě i možnost Administrator - tu ale nedoporučuji)

### 4. Spuštění bota
Pomocí příkazu ```python3 (váš název souboru)``` spustíte bota. To je vše!
