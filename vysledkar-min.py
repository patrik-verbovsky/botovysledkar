z='Jméno hráče'
y='%d.%m.%Y'
x='━━━━━━━━━━━━━━━━━━━━━━\n'
w='🕒 Datum'
v=print
r='Výsledky'
q='📊 Anketa'
p='%d.%m.%Y_%H:%M'
o='❌ Nezúčastní se'
n='✅ Zúčastní se'
m='%d.%m.%Y %H:%M'
l=max
k=int
j=sum
g='━━━━━━━━━━━━━━━━━━━━━━'
f='❌ Událost nenalezena.'
e='Nikdo'
d='popis'
c='utf-8'
b=open
a='\n'
Z='rsvp'
Y=sorted
X=ValueError
W=str
T='id'
S=len
R=enumerate
P='players'
M='body'
L='%Y-%m-%d %H:%M'
K='Volitelný hráč'
J='jmeno'
I=False
G='datetime'
D=None
B=True
import discord as A
from discord import app_commands as N
from discord.ext import commands as A0
from datetime import datetime as E,timedelta as A1
from typing import Optional
import json as U,os,calendar,matplotlib.pyplot as H,uuid
h=A.Intents.default()
h.message_content=B
h.members=B
C=A0.Bot(command_prefix='!',intents=h)
F='kalendar.json'
A9='ankety.json'
def Q(file):
	if not os.path.exists(file):return[]
	with b(file,'r',encoding=c)as A:return U.load(A)
def V(file,data):
	with b(file,'w',encoding=c)as A:U.dump(data,A,ensure_ascii=I,indent=2)
@C.tree.command(name='kalendar',description='Zobrazí události na dalších 7 dní')
async def AA(interaction):
	J=interaction;K=E.now();M=K.replace(hour=23,minute=59,second=59)+A1(days=7);N=Q(F);D=[]
	for C in N:
		try:H=E.strptime(C[G],L)
		except:continue
		if K<=H<=M:D.append((H,C))
	if not D:await J.response.send_message('📭 Žádné naplánované události v následujících 7 dnech.');return
	D.sort(key=lambda x:x[0]);await J.response.send_message('📌 Zobrazeny nadcházející události:',ephemeral=B)
	for(H,C)in D:O=[f"<@{A}>"for(A,B)in C.get(Z,{}).items()if B.startswith('✅')];P=[f"<@{A}>"for(A,B)in C.get(Z,{}).items()if B.startswith('❌')];I=A.Embed(title=f"📅 Událost – {H.strftime(m)}",description=f"**{C[d]}**\n━━━━━━━━━━━━━━━━━━━━━━",color=3066993);I.add_field(name=n,value=a.join(O)or e,inline=B);I.add_field(name=o,value=a.join(P)or e,inline=B);I.set_footer(text='Klikni na tlačítka níže pro odpověď nebo nastavení.');R=s(C[T],allow_settings=B);await J.channel.send(embed=I,view=R)
class s(A.ui.View):
	def __init__(A,event_id,allow_settings=I):
		B=event_id;super().__init__(timeout=D);A.event_id=B
		if allow_settings:A.add_item(A2(B))
	@A.ui.button(label='✅ Zúčastním se',style=A.ButtonStyle.success,custom_id='rsvp_yes')
	async def yes_button(self,interaction,button):await self._handle_response(interaction,n)
	@A.ui.button(label='❌ Nezúčastním se',style=A.ButtonStyle.danger,custom_id='rsvp_no')
	async def no_button(self,interaction,button):await self._handle_response(interaction,o)
	async def _handle_response(H,interaction,response):
		E=interaction;J=Q(F);K=I
		for C in J:
			if C[T]==H.event_id:C.setdefault(Z,{})[W(E.user.id)]=response;K=B;break
		if K:
			V(F,J);L=[];M=[]
			for(N,O)in C[Z].items():
				if O.startswith('✅'):L.append(f"<@{N}>")
				elif O.startswith('❌'):M.append(f"<@{N}>")
			D=A.Embed(title='📅 Událost',description=C[d],color=5793266);D.add_field(name=w,value=C[G],inline=I);D.add_field(name=n,value=a.join(L)or e,inline=B);D.add_field(name=o,value=a.join(M)or e,inline=B);await E.message.edit(embed=D,view=H)
		else:await E.response.send_message(f,ephemeral=B)
class A2(A.ui.Button):
	def __init__(B,event_id):super().__init__(label='⚙️ Nastavení',style=A.ButtonStyle.secondary);B.event_id=event_id
	async def callback(C,interaction):D=A.Embed(title='⚙️ Nastavení události',description='Zde můžeš upravit událost:\n\n📝 Změnit popis\n🕒 Změnit čas\n🗑️ Smazat událost',color=15844367);await interaction.response.send_message(embed=D,view=A3(C.event_id),ephemeral=B)
class A3(A.ui.View):
	def __init__(A,event_id):super().__init__(timeout=180);A.event_id=event_id
	@A.ui.button(label='📝 Změnit popis',style=A.ButtonStyle.primary)
	async def change_description(self,interaction,button):await interaction.response.send_modal(A4(self.event_id))
	@A.ui.button(label='🕒 Změnit čas',style=A.ButtonStyle.secondary)
	async def change_time(self,interaction,button):await interaction.response.send_modal(A5(self.event_id))
	@A.ui.button(label='🗑️ Smazat událost',style=A.ButtonStyle.danger)
	async def delete_event(self,interaction,button):
		C=interaction;A=Q(F)
		for(D,E)in R(A):
			if E[T]==self.event_id:A.pop(D);V(F,A);await C.response.send_message('🗑️ Událost byla smazána.',ephemeral=B);return
		await C.response.send_message(f,ephemeral=B)
class A4(A.ui.Modal,title='Změnit popis události'):
	novy_popis=A.ui.TextInput(label='Nový popis',max_length=200)
	def __init__(A,event_id):super().__init__();A.event_id=event_id
	async def on_submit(A,interaction):
		C=interaction;D=Q(F)
		for E in D:
			if E[T]==A.event_id:E[d]=A.novy_popis.value;V(F,D);await C.response.send_message('✅ Popis události byl změněn.',ephemeral=B);return
		await C.response.send_message(f,ephemeral=B)
class A5(A.ui.Modal,title='Změnit čas události'):
	novy_cas=A.ui.TextInput(label='Nový čas (dd.mm.yyyy_hh:mm)')
	def __init__(A,event_id):super().__init__();A.event_id=event_id
	async def on_submit(C,interaction):
		A=interaction
		try:I=E.strptime(C.novy_cas.value,p)
		except X:await A.response.send_message('❌ Špatný formát času.',ephemeral=B);return
		D=Q(F)
		for H in D:
			if H[T]==C.event_id:H[G]=I.strftime(L);V(F,D);await A.response.send_message('✅ Čas události byl změněn.',ephemeral=B);return
		await A.response.send_message(f,ephemeral=B)
@C.tree.command(name='pridat_udalost',description='Přidá novou událost do kalendáře')
@N.describe(popis='Popis události',termin='Datum a čas ve formátu dd.mm.yyyy_hh:mm')
async def AB(interaction,popis,termin):
	J=popis;C=interaction
	try:D=E.strptime(termin,p)
	except X:await C.response.send_message('❌ Nesprávný formát data. Použij `dd.mm.yyyy_hh:mm`.');return
	H=Q(F)
	for N in H:
		O=E.strptime(N[G],L)
		if O==D:await C.response.send_message('⚠️ V tomto termínu už existuje jiná událost.');return
	K=W(uuid.uuid4());P={T:K,d:J,G:D.strftime(L),Z:{}};H.append(P);V(F,H);M=A.Embed(title='📅 Nová událost',description=J,color=45300);M.add_field(name=w,value=D.strftime(m),inline=I);R=s(K,allow_settings=B);await C.response.send_message('✅ Událost byla přidána:');await C.channel.send(embed=M,view=R)
class t(A.ui.View):
	def __init__(A,otazka,moznosti,interaction):
		B=moznosti;super().__init__(timeout=D);A.otazka=otazka;A.moznosti=B;A.hlasovani={};A.interaction=interaction
		for C in B:A.add_item(u(C,A))
	async def update_embed(B):
		C={A:0 for A in B.moznosti}
		for K in B.hlasovani.values():C[K]+=1
		D=j(C.values());E=[]
		for F in B.moznosti:G=C[F];H=G/D*100 if D>0 else 0;L='█'*k(H/10);E.append(f"**{F}**: {G} hlasů | {L} {H:.1f}%")
		J=A.Embed(title=q,description=B.otazka,color=3447003);J.add_field(name=r,value=a.join(E),inline=I);await B.interaction.edit_original_response(embed=J,view=B)
class u(A.ui.Button):
	def __init__(B,moznost,view):C=moznost;super().__init__(label=C,style=A.ButtonStyle.secondary);B.moznost=C;B.view_ref=view
	async def callback(A,interaction):C=interaction;A.view_ref.hlasovani[W(C.user.id)]=A.moznost;await C.response.send_message(f"Hlasovali jste pro: **{A.moznost}**",ephemeral=B);await A.view_ref.update_embed()
class t(A.ui.View):
	def __init__(A,otazka,moznosti,interaction):
		B=moznosti;super().__init__(timeout=D);A.otazka=otazka;A.moznosti=B;A.hlasovani={};A.interaction=interaction
		for C in B:A.add_item(u(C,A))
	async def update_embed(B):
		C={A:0 for A in B.moznosti}
		for K in B.hlasovani.values():C[K]+=1
		E=j(C.values());F=[]
		for D in B.moznosti:G=C[D];H=G/E*100 if E>0 else 0;L='█'*k(H/10);M=[f"<@{A}>"for(A,B)in B.hlasovani.items()if B==D];F.append(f"**{D}**: {G} hlasů | {L} {H:.1f}%\n{", ".join(M)}")
		J=A.Embed(title=q,description=B.otazka,color=3447003);J.add_field(name=r,value='\n\n'.join(F),inline=I);await B.interaction.edit_original_response(embed=J,view=B)
@C.tree.command(name='anketa',description='Vytvoří anketu s tlačítky')
@N.describe(otazka='Otázka pro anketu',moznosti='Možnosti oddělené čárkou (např. Ano,Ne,Možná)')
async def AC(interaction,otazka,moznosti):
	C=otazka;B=interaction;D=[A.strip()for A in moznosti.split(',')if A.strip()]
	if not 2<=S(D)<=5:await B.response.send_message('❌ Zadej 2–5 možností.');return
	F=t(C,D,B);E=A.Embed(title=q,description=C,color=3447003);E.add_field(name=r,value='Zatím nikdo nehlasoval.',inline=I);await B.response.send_message(embed=E,view=F)
@C.event
async def A6():await C.tree.sync();v(f"✅ Bot je online jako {C.user}")
i='vysledky.json'
def O():
	if not os.path.exists(i):return[]
	with b(i,'r',encoding=c)as B:
		try:
			A=U.load(B)
			if isinstance(A,list):return A
			else:return[]
		except U.JSONDecodeError:return[]
def A7(game_data):
	A=O();A.append(game_data)
	with b(i,'w',encoding=c)as B:U.dump(A,B,ensure_ascii=I,indent=2)
def A8():
	C=O();A={}
	for D in C:
		for B in D[P]:A[B[J]]=A.get(B[J],0)+B[M]
	return A
@C.event
async def A6():await C.tree.sync();v(f"✅ Bot je online jako {C.user}")
@C.tree.command(name='vysledky',description='Zobrazí výsledky hráčů a ukládá je')
@N.describe(hrac1='Zadej ve formátu jméno/bodů',hrac2=K,hrac3=K,hrac4=K,hrac5=K,hrac6=K,hrac7=K,hrac8=K,hrac9=K,hrac10=K,cas='Volitelné datum a čas ve formátu dd.mm.yyyy_hh:mm')
async def AD(interaction,hrac1,hrac2=D,hrac3=D,hrac4=D,hrac5=D,hrac6=D,hrac7=D,hrac8=D,hrac9=D,hrac10=D,cas=D):
	F=interaction;await F.response.defer();Q=[hrac1,hrac2,hrac3,hrac4,hrac5,hrac6,hrac7,hrac8,hrac9,hrac10];A=[]
	for I in Q:
		if I:
			try:C,D=I.split('/');D=k(D.strip());C=C.strip();A.append((C,D))
			except:await F.followup.send(f"❌ Chybný formát u `{I}`. Použij `jméno/bodů`.");return
	if cas:
		try:K=E.strptime(cas,p)
		except X:await F.followup.send('❌ Špatný formát času. Použij `dd.mm.yyyy_hh:mm`.');return
	else:K=E.now()
	T={G:K.strftime(L),P:[{J:A,M:B}for(A,B)in A]};A7(T);U=K.strftime(m);A.sort(key=lambda x:x[1],reverse=B);O=['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','1️⃣0️⃣'];V=l((S(A)for(A,B)in A),default=20);H=f"📊 Výsledky\n📅 {U}\n";H+=x
	for(N,(C,D))in R(A):Y=O[N]if N<S(O)else f"{N+1}";H+=f"{Y} {C.ljust(V)} │ {W(D).rjust(3)} b\n"
	H+=g;await F.followup.send(f"```\n{H}\n```")
@C.tree.command(name='tabulka',description='Zobrazí celkovou tabulku hráčů')
async def AE(interaction):
	C=interaction;D=A8()
	if not D:await C.response.send_message('⚠️ Zatím nejsou uloženy žádné výsledky.');return
	E=Y(D.items(),key=lambda x:x[1],reverse=B);F=l(S(A)for(A,B)in E);A=f"📈 Celkové výsledky\n━━━━━━━━━━━━━━━━━━━━━━\n"
	for(G,(H,I))in R(E):J=f"{G+1:>2}.";A+=f"{J} {H.ljust(F)} │ {W(I).rjust(4)} b\n"
	A+=g;await C.response.send_message(f"```\n{A}\n```")
@C.tree.command(name='historie',description='Zobrazí historii her podle data')
@N.describe(den='Filtruj podle dne ve formátu dd.mm.yyyy (volitelné)',cas='Volitelný časový filtr hh:mm (ukáže pouze hry po tomto čase)')
async def AF(interaction,den=D,cas=D):
	F=interaction;T=O();H=[]
	try:K=E.strptime(den,y).date()if den else D;N=E.strptime(cas,'%H:%M').time()if cas else D
	except X:await F.response.send_message('❌ Neplatný formát filtru. Použij `dd.mm.yyyy` a/nebo `hh:mm`.');return
	for A in T:
		Q=E.strptime(A[G],L)
		if K and Q.date()!=K:continue
		if N and Q.time()<N:continue
		H.append(A)
	if not H:await F.response.send_message('🔍 Žádné výsledky pro zadané filtry.');return
	C='🕓 Filtrované hry\n━━━━━━━━━━━━━━━━━━━━━━\n'
	for A in H[-5:]:
		C+=f"📅 {A[G]}\n";U=Y(A[P],key=lambda x:x[M],reverse=B)
		for(I,S)in R(U):V=['🥇','🥈','🥉'][I]if I<3 else f"{I+1}.";C+=f"{V} {S[J]} │ {S[M]} b\n"
		C+=x
	await F.response.send_message(f"```\n{C}\n```")
@C.tree.command(name='statistiky',description='Zobrazí statistiky jednoho hráče')
@N.describe(jmeno=z)
async def AG(interaction,jmeno):
	C=interaction;B=jmeno;E=O();A=[A[M]for C in E for A in C[P]if A[J].lower()==B.lower()]
	if not A:await C.response.send_message(f"❌ Hráč `{B}` nebyl nalezen v žádné hře.");return
	D=j(A);F=D/S(A);G=l(A);H=f"""📊 Statistiky pro **{B}**
━━━━━━━━━━━━━━━━━━━━━━
🕹️ Počet her: {S(A)}
📈 Celkem bodů: {D}
📊 Průměr: {F:.2f} b
🏆 Nejvyšší skóre: {G} b
━━━━━━━━━━━━━━━━━━━━━━""";await C.response.send_message(f"```\n{H}\n```")
@C.tree.command(name='mvp',description='Zobrazí hráče s nejvíce výhrami')
async def AH(interaction):
	D=interaction;F=O();A={}
	for G in F:H=Y(G[P],key=lambda x:x[M],reverse=B);E=H[0][J];A[E]=A.get(E,0)+1
	if not A:await D.response.send_message('❌ Zatím nejsou žádné výhry.');return
	I=Y(A.items(),key=lambda x:x[1],reverse=B);C='🏅 MVP (počet 1. míst)\n━━━━━━━━━━━━━━━━━━━━━━\n'
	for(K,(L,N))in R(I):C+=f"{K+1:>2}. {L} │ {N} výher\n"
	C+=g;await D.response.send_message(f"```\n{C}\n```")
@C.tree.command(name='topza',description='Zobrazí tabulku hráčů za konkrétní den')
@N.describe(den='Datum ve formátu dd.mm.yyyy')
async def AI(interaction,den):
	C=interaction
	try:I=E.strptime(den,y).date()
	except X:await C.response.send_message('❌ Neplatný formát data. Použij `dd.mm.yyyy`.');return
	K=O();A={}
	for H in K:
		N=E.strptime(H[G],L)
		if N.date()==I:
			for D in H[P]:A[D[J]]=A.get(D[J],0)+D[M]
	if not A:await C.response.send_message('❌ Žádné výsledky pro tento den.');return
	Q=Y(A.items(),key=lambda x:x[1],reverse=B);F=f"📆 Výsledky za {den}\n━━━━━━━━━━━━━━━━━━━━━━\n"
	for(S,(T,U))in R(Q):F+=f"{S+1:>2}. {T} │ {U} b\n"
	F+=g;await C.response.send_message(f"```\n{F}\n```")
@C.tree.command(name='graf',description='Vygeneruje graf skóre hráče v čase')
@N.describe(jmeno=z)
async def AJ(interaction,jmeno):
	D=interaction;C=jmeno;await D.response.defer();N=O();B=[]
	for F in N:
		Q=E.strptime(F[G],L)
		for I in F[P]:
			if I[J].lower()==C.lower():B.append((Q,I[M]))
	if not B:await D.followup.send(f"❌ Žádná data pro hráče `{C}`.");return
	B.sort(key=lambda x:x[0]);R=[A[0]for A in B];S=[A[1]for A in B];H.figure();H.plot(R,S,marker='o');H.title(f"Vývoj skóre: {C}");H.xlabel('Datum');H.ylabel('Skóre');H.xticks(rotation=45);H.tight_layout();K=f"/tmp/{C}_graf.png";H.savefig(K);H.close();await D.followup.send(file=A.File(K))
C.run('your bot token here/váš token k botovi zde')
