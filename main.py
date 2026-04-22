"""
Pokemon Mystic Route  –  main.py
States: title → starter → world → battle → switch_select → stats → title
        title → history → title
Controls
  Title         : ENTER=start  H=history
  Starter select: 1 / 2 / 3   ESC=back
  World         : Arrow keys   B at boss gate (team full)
  Battle        : UP/DOWN=select move   SPACE=attack   T=open switch screen
  Switch select : 1-6 = pick slot      ESC=cancel (costs no turn)
  Stats         : ENTER=back to title
  History       : ENTER / ESC = back   UP/DOWN=scroll
"""
import math, random, time
import pygame

from config         import WIDTH, HEIGHT, TILE, FPS, TEAM_LIMIT
from player         import Player
from world          import (generate_maze, draw_world, encounter,
                             is_boss_gate, is_walkable, player_start_pos)
from battle         import attack
from starters       import starters
from wild_pokemon   import random_wild
from bosses         import bosses
from data_manager   import DataManager
from pokemon_sprite import create_mon_sprite, create_boss_sprite

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Mystic Route")
clock  = pygame.time.Clock()

# ── Fonts ──────────────────────────────────────────────────────────────────
FT  = pygame.font.SysFont("arial", 13)
FSM = pygame.font.SysFont("arial", 17)
FMD = pygame.font.SysFont("arial", 22, bold=True)
FLG = pygame.font.SysFont("arial", 34, bold=True)
FXL = pygame.font.SysFont("arial", 52, bold=True)

# ── Palette ────────────────────────────────────────────────────────────────
BG    = (12, 12, 22);    PANEL  = (24, 22, 42);  PANEL2 = (38, 36, 62)
BDR   = (80, 72, 130);   BDR2   = (110,100,170)
WHITE = (245,245,255);   GRAY   = (145,140,165)
YEL   = (255,220, 50);   RED    = (220, 55, 55)
GRN   = ( 55,200, 80);   BLU    = ( 60,140,255)

TYPE_COL = {
    "fire":(230,80,30), "water":(50,130,240), "grass":(50,185,60),
    "electric":(220,190,20), "psychic":(210,80,185),
    "rock":(160,140,95), "ghost":(110,65,170), "normal":(155,150,135),
}

# ── Data / session ─────────────────────────────────────────────────────────
dm   = DataManager()
data = dm.load()
sess = dm.new_session()

# ── Game state ────────────────────────────────────────────────────────────
state          = "title"
tmap           = None      # tile map from maze generator
grass_set      = set()
player         = Player()
party: list    = []
enemy          = None
current_boss   = random.choice(bosses).clone()
active_index   = 0
move_index     = 0
msg_lines: list= []
msg_timer      = 0
starter_name   = ""
run_stats: dict= {}
dmg_popups:list= []
_scache: dict  = {}
history_scroll = 0

# ── Sprite cache helpers ──────────────────────────────────────────────────
def get_spr(mon, size):
    k = (mon.name, size)
    if k not in _scache:
        base = create_mon_sprite(mon.color, mon.type, 32)
        _scache[k] = pygame.transform.scale(base, (size, size))
    return _scache[k]

def get_boss_spr(mon, size):
    k = ("B" + mon.name, size)
    if k not in _scache:
        base = create_boss_sprite(mon.color, 32)
        _scache[k] = pygame.transform.scale(base, (size, size))
    return _scache[k]

# ── Draw helpers ──────────────────────────────────────────────────────────
def panel(rect, col=PANEL, bdr=BDR, r=10):
    pygame.draw.rect(screen, col, rect, border_radius=r)
    pygame.draw.rect(screen, bdr, rect, 2, border_radius=r)

def txt(s, font, color, x, y):
    screen.blit(font.render(s, True, color), (x, y))

def ctr(s, font, color, y):
    img = font.render(s, True, color)
    screen.blit(img, ((WIDTH - img.get_width()) // 2, y))

def hp_bar(x, y, w, h, hp, max_hp):
    r = max(0.0, hp / max_hp)
    bc = GRN if r > 0.5 else YEL if r > 0.25 else RED
    pygame.draw.rect(screen, (40,38,55), (x,y,w,h), border_radius=3)
    if r > 0:
        pygame.draw.rect(screen, bc, (x,y,int(w*r),h), border_radius=3)
    pygame.draw.rect(screen, BDR, (x,y,w,h), 1, border_radius=3)

def type_badge(x, y, ptype):
    col = TYPE_COL.get(ptype, GRAY)
    dk  = tuple(max(0, c-45) for c in col)
    pygame.draw.rect(screen, dk,  (x,y,58,18), border_radius=9)
    pygame.draw.rect(screen, col, (x+1,y+1,56,16), border_radius=8)
    lb = FT.render(ptype.upper(), True, WHITE)
    screen.blit(lb, (x+(58-lb.get_width())//2, y+(18-lb.get_height())//2))

def add_popup(x, y, dmg, mult):
    if   mult >= 2: col=(255,220,50);  pre="★"
    elif mult == 0: col=(160,160,160); pre="✕"
    elif mult <  1: col=(180,180,255); pre="↓"
    else:           col=WHITE;         pre=""
    dmg_popups.append({"x":float(x),"y":float(y),"vy":-2.5,
                        "text":f"{pre}{dmg}","color":col,"life":70,"max_life":70})

def partial_heal(party_list, pct=0.30):
    for mon in party_list:
        mon.hp = min(mon.max_hp, mon.hp + max(1, int(mon.max_hp * pct)))

def starfield(seed=7):
    t  = pygame.time.get_ticks()
    rng = random.Random(seed)
    for _ in range(160):
        sx = rng.randint(0, WIDTH); sy = rng.randint(0, HEIGHT)
        br = int(150 + 80*math.sin(t/900 + sx*0.04))
        pygame.draw.circle(screen, (br, br, min(255,br+40)), (sx,sy), rng.randint(1,2))

# ══════════════════════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════════════════════
def draw_title():
    screen.fill(BG); starfield()
    t = pygame.time.get_ticks()
    for ox,oy,c in [(3,3,(40,25,85)),(0,0,YEL)]:
        img = FXL.render("POKEMON", True, c)
        screen.blit(img, ((WIDTH-img.get_width())//2+ox, 55+oy))
    ctr("MYSTIC  ROUTE", FLG, WHITE, 122)
    for i,(pt,col) in enumerate([("fire",(255,110,50)),("water",(50,140,255)),("grass",(60,220,80))]):
        bob = int(8*math.sin(t/600 + i*2.1))
        spr = pygame.transform.scale(create_mon_sprite(col,pt,32),(72,72))
        screen.blit(spr, (WIDTH//2-110+i*110, 200+bob))
    bw, bh = 260, 52
    for i,(label,col,dk) in enumerate([
        ("  START GAME  ",(50,185,60),(36,140,46)),
        ("  HISTORY  ",(60,100,220),(40,75,175))
    ]):
        bx = WIDTH//2 - bw//2; by = 310 + i*72
        pygame.draw.rect(screen, dk,    (bx,by,bw,bh), border_radius=12)
        pygame.draw.rect(screen, col,   (bx+1,by+1,bw-2,bh-2), border_radius=11)
        pygame.draw.rect(screen, WHITE, (bx,by,bw,bh), 2, border_radius=12)
        lbl = FMD.render(label, True, WHITE)
        screen.blit(lbl, (bx+(bw-lbl.get_width())//2, by+(bh-lbl.get_height())//2))
    hint = FT.render("[ENTER] Start   [H] History", True, GRAY)
    screen.blit(hint, ((WIDTH-hint.get_width())//2, HEIGHT-26))
    txt(f"Runs:{data['runs']}  Wins:{data['wins']}  Losses:{data['losses']}", FT, GRAY, 12, HEIGHT-26)

# ══════════════════════════════════════════════════════════════════════════
# STARTER SELECT
# ══════════════════════════════════════════════════════════════════════════
def draw_starter():
    screen.fill(BG); starfield(8)
    ctr("Choose your Starter!", FLG, WHITE, 50)
    PW, PH = 210, 270; gap = 32; sx0 = (WIDTH - 3*PW - 2*gap)//2
    t = pygame.time.get_ticks()
    for i, st in enumerate(starters):
        px = sx0 + i*(PW+gap); py = 100
        tc = TYPE_COL.get(st.type, GRAY); dark = tuple(max(0,c-60) for c in tc)
        ga = int(35 + 20*math.sin(t/700 + i*1.2))
        gs = pygame.Surface((PW+10,PH+10), pygame.SRCALPHA); gs.fill((*tc,ga))
        screen.blit(gs, (px-5, py-5))
        panel((px,py,PW,PH), col=dark, bdr=tc, r=14)
        img = pygame.transform.scale(create_mon_sprite(st.color,st.type,32),(104,104))
        screen.blit(img, (px+(PW-104)//2, py+14))
        nm = FMD.render(st.name, True, WHITE)
        screen.blit(nm, (px+(PW-nm.get_width())//2, py+126))
        type_badge(px+(PW-58)//2, py+156, st.type)
        txt(f"HP {st.max_hp}", FT, GRAY, px+18, py+184)
        mv = ", ".join(m.name for m in st.moves[:2]) + "…"
        txt(mv, FT, GRAY, px+8, py+202)
        ki = FMD.render(f"[ {i+1} ]", True, YEL)
        screen.blit(ki, (px+(PW-ki.get_width())//2, py+234))
    ctr("[ESC] Back to Title", FT, GRAY, HEIGHT-26)

# ══════════════════════════════════════════════════════════════════════════
# SWITCH SELECT  (shown mid-battle when player presses T)
# ══════════════════════════════════════════════════════════════════════════
def draw_switch_select():
    """Overlay battle background with a party selection panel."""
    draw_battle()   # draw battle scene underneath

    # dim overlay
    dim = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
    dim.fill((0,0,0,160)); screen.blit(dim,(0,0))

    # title
    ctr("Choose a Pokemon to send out!", FMD, WHITE, 60)
    ctr("(ESC = cancel, no turn used)", FT, GRAY, 90)

    # party slots
    slot_w, slot_h = 400, 56
    sx0 = (WIDTH - slot_w) // 2
    for i, mon in enumerate(party):
        sy = 120 + i * (slot_h + 8)
        is_active  = (i == active_index)
        is_fainted = mon.is_fainted()

        bg_col = (40,36,65) if not is_active else (60,55,90)
        bd_col = YEL if is_active else BDR
        if is_fainted: bg_col = (55,22,22); bd_col = RED

        panel((sx0, sy, slot_w, slot_h), col=bg_col, bdr=bd_col, r=8)

        # mini sprite
        mini = pygame.transform.scale(create_mon_sprite(mon.color,mon.type,32),(44,44))
        screen.blit(mini, (sx0+6, sy+6))

        # name + type
        col_name = GRAY if is_fainted else (WHITE if not is_active else YEL)
        txt(mon.name, FMD, col_name, sx0+58, sy+6)
        type_badge(sx0+58, sy+30, mon.type)

        # hp bar
        hp_bar(sx0+160, sy+16, 180, 10, mon.hp, mon.max_hp)
        txt(f"{mon.hp}/{mon.max_hp}", FT, GRAY, sx0+346, sy+12)

        # slot number
        slot_lbl = FMD.render(f"[{i+1}]", True, YEL if not is_fainted else RED)
        screen.blit(slot_lbl, (sx0+slot_w-40, sy+(slot_h-slot_lbl.get_height())//2))

        # current tag
        if is_active:
            cur = FT.render("OUT", True, GRN)
            screen.blit(cur, (sx0+58+FMD.size(mon.name)[0]+6, sy+8))

        # fainted tag
        if is_fainted:
            ft2 = FT.render("FAINTED", True, RED)
            screen.blit(ft2, (sx0+slot_w-90, sy+slot_h//2-ft2.get_height()//2))

# ══════════════════════════════════════════════════════════════════════════
# BATTLE BACKGROUND
# ══════════════════════════════════════════════════════════════════════════
def _draw_battle_bg(is_boss):
    if is_boss: sky_top=(8,4,20);   sky_bot=(30,20,60)
    else:       sky_top=(100,160,220); sky_bot=(170,215,170)
    for y in range(HEIGHT):
        rr = y/HEIGHT
        pygame.draw.line(screen,
            (int(sky_top[0]*(1-rr)+sky_bot[0]*rr),
             int(sky_top[1]*(1-rr)+sky_bot[1]*rr),
             int(sky_top[2]*(1-rr)+sky_bot[2]*rr)), (0,y),(WIDTH,y))
    GLINE = int(HEIGHT*0.65)
    gc  = (72,160,56) if not is_boss else (30,50,30)
    gc2 = (56,140,40) if not is_boss else (20,35,20)
    rng3 = random.Random(12)
    for gx in range(0, WIDTH, TILE):
        col = gc if (gx//TILE)%2==0 else gc2
        pygame.draw.rect(screen, col, (gx,GLINE,TILE,HEIGHT-GLINE))
        bl = tuple(min(255,c+25) for c in col)
        for bx2 in range(gx+2, gx+TILE-2, 5):
            bh = rng3.randint(6,12)
            pygame.draw.line(screen, bl, (bx2,GLINE),(bx2-1,GLINE-bh),1)
    pygame.draw.line(screen, tuple(max(0,c-20) for c in gc),(0,GLINE),(WIDTH,GLINE),2)
    # platforms
    epx=int(WIDTH*0.62); epy=int(HEIGHT*0.42)
    ppx=int(WIDTH*0.25); ppy=int(HEIGHT*0.60)
    for cx,cy,cw,ch in [(epx,epy,180,18),(ppx,ppy,160,16)]:
        pygame.draw.ellipse(screen, tuple(max(0,c-30) for c in gc),(cx-cw//2,cy,cw,ch))
        pygame.draw.ellipse(screen, tuple(max(0,c-10) for c in gc),(cx-cw//2+2,cy+2,cw-4,ch-4))
    # trees
    tc=(32,88,16) if not is_boss else (15,40,10)
    tc2=(24,72,12) if not is_boss else (10,28,8)
    for bx2,by2,br in [(55,200,55),(95,230,45),(22,242,40),
                        (WIDTH-55,210,50),(WIDTH-95,235,42),(WIDTH-22,245,38)]:
        pygame.draw.circle(screen,tc2,(bx2,by2),br+3)
        pygame.draw.circle(screen,tc, (bx2,by2),br)
        pygame.draw.rect(screen,(100,60,18),(bx2-5,by2+br-5,10,20))
    return GLINE, epx, epy, ppx, ppy

# ══════════════════════════════════════════════════════════════════════════
# BATTLE SCREEN
# ══════════════════════════════════════════════════════════════════════════
def draw_battle():
    p = party[active_index]
    t = pygame.time.get_ticks()
    is_boss = (enemy.name == current_boss.name)
    GLINE, epx, epy, ppx, ppy = _draw_battle_bg(is_boss)

    # enemy sprite
    e_size = 148 if is_boss else 116
    e_img  = (get_boss_spr if is_boss else get_spr)(enemy, e_size)
    bob = int(5*math.sin(t/520))
    ex = epx - e_size//2; ey = epy - e_size + 8 + bob
    sh = pygame.Surface((e_size,16),pygame.SRCALPHA)
    pygame.draw.ellipse(sh,(0,0,0,70),(0,0,e_size,16))
    screen.blit(sh,(ex,epy+2)); screen.blit(e_img,(ex,ey))
    if is_boss:
        crown = FMD.render("★  LEGENDARY  ★", True, YEL)
        screen.blit(crown,(ex+(e_size-crown.get_width())//2,ey-28))

    # player sprite
    p_size = 116; p_img = get_spr(p,p_size)
    wobble = int(3*math.sin(t/200)) if msg_timer>60 else 0
    px2=ppx-p_size//2+wobble; py2=ppy-p_size+6
    sh2=pygame.Surface((p_size,14),pygame.SRCALPHA)
    pygame.draw.ellipse(sh2,(0,0,0,70),(0,0,p_size,14))
    screen.blit(sh2,(px2,ppy+2)); screen.blit(p_img,(px2,py2))

    # enemy info card
    ec=pygame.Rect(18,18,290,88); panel(ec,r=10)
    txt(enemy.name,FMD,WHITE,ec.x+12,ec.y+8)
    txt("Lv.?? BOSS" if is_boss else "Lv.15",FT,YEL if is_boss else GRAY,ec.x+185,ec.y+10)
    type_badge(ec.x+12,ec.y+36,enemy.type)
    txt(f"HP {enemy.hp}/{enemy.max_hp}",FT,GRAY,ec.x+12,ec.y+58)
    hp_bar(ec.x+12,ec.y+73,258,10,enemy.hp,enemy.max_hp)

    # player info card
    pc=pygame.Rect(WIDTH-322,HEIGHT-182,300,90); panel(pc,r=10)
    txt(p.name,FMD,WHITE,pc.x+12,pc.y+8)
    txt("Lv.10",FT,GRAY,pc.x+210,pc.y+10)
    type_badge(pc.x+12,pc.y+36,p.type)
    txt(f"HP {p.hp}/{p.max_hp}",FT,GRAY,pc.x+12,pc.y+58)
    hp_bar(pc.x+12,pc.y+73,270,10,p.hp,p.max_hp)

    # move panel
    MP=pygame.Rect(14,HEIGHT-182,342,180); panel(MP,r=10)
    txt("[↑↓]sel  [SPACE]atk  [T]switch",FT,GRAY,MP.x+10,MP.y+6)
    for i,m in enumerate(p.moves):
        my=MP.y+26+i*36; sel=(i==move_index); tc=TYPE_COL.get(m.type,GRAY)
        if sel:
            pygame.draw.rect(screen,PANEL2,(MP.x+5,my-3,MP.width-10,30),border_radius=6)
            pygame.draw.rect(screen,tc,(MP.x+5,my-3,MP.width-10,30),1,border_radius=6)
        txt(("▶ " if sel else "  ")+m.name,FSM,WHITE if sel else GRAY,MP.x+12,my)
        pips=min(m.power//3,8)
        for pi in range(8):
            pygame.draw.rect(screen,tc if pi<pips else (40,38,55),
                             (MP.x+MP.width-96+pi*11,my+8,9,9),border_radius=2)
        type_badge(MP.x+MP.width-64,my-3,m.type)

    # team strip
    tsx=WIDTH-320; tsy=HEIGHT-58
    txt("TEAM:",FT,GRAY,tsx-46,tsy+8)
    for idx,mon in enumerate(party):
        tx=tsx+idx*44
        panel((tx,tsy,40,40),col=YEL if idx==active_index else PANEL,bdr=BDR2,r=6)
        mini=pygame.transform.scale(create_mon_sprite(mon.color,mon.type,32),(30,30))
        screen.blit(mini,(tx+5,tsy+5))
        if mon.is_fainted():
            pygame.draw.line(screen,RED,(tx+2,tsy+2),(tx+37,tsy+37),2)
            pygame.draw.line(screen,RED,(tx+37,tsy+2),(tx+2,tsy+37),2)
        ratio=mon.hp/mon.max_hp
        pygame.draw.circle(screen,GRN if ratio>0.5 else YEL if ratio>0.25 else RED,(tx+36,tsy+6),4)

    # dialogue
    if msg_lines:
        db=pygame.Rect(MP.right+8,HEIGHT-182,WIDTH-MP.right-22,180); panel(db,r=10)
        for li,(lt,lc) in enumerate(msg_lines[-4:]):
            txt(lt,FSM,lc,db.x+12,db.y+14+li*38)

    # damage popups
    for pop in dmg_popups:
        alpha=int(255*(pop["life"]/pop["max_life"]))
        pf=pygame.font.SysFont("arial",int(24*(1.0+0.4*(1-pop["life"]/pop["max_life"]))),bold=True)
        img=pf.render(pop["text"],True,pop["color"]); img.set_alpha(alpha)
        screen.blit(img,(int(pop["x"])-img.get_width()//2,int(pop["y"])))

# ══════════════════════════════════════════════════════════════════════════
# STATS SCREEN
# ══════════════════════════════════════════════════════════════════════════
def draw_stats():
    screen.fill(BG); starfield(13)
    rs = run_stats
    win = rs.get("outcome") == "WIN"
    ctr("VICTORY!" if win else "DEFEATED...", FXL, GRN if win else RED, 55)
    ctr(f"Run #{rs.get('run',0)}  –  Boss: {rs.get('boss','?')}", FMD, YEL, 120)
    sb=pygame.Rect(WIDTH//2-320,155,640,290); panel(sb,r=14)
    rows=[
        ("Starter",       rs.get("starter","?"),         WHITE),
        ("Steps Walked",  str(rs.get("steps",0)),         BLU),
        ("Encounters",    str(rs.get("encounters",0)),    GRN),
        ("Pokemon Caught",str(rs.get("catches",0)),       YEL),
        ("Run Duration",  f"{rs.get('duration',0):.1f}s", GRAY),
        ("Team HP Total", str(rs.get("team_hp",0)),       GRN if win else RED),
    ]
    for i,(label,val,col) in enumerate(rows):
        ry=sb.y+16+i*42
        pygame.draw.rect(screen,PANEL2,(sb.x+12,ry,sb.width-24,36),border_radius=6)
        txt(label,FSM,GRAY,sb.x+24,ry+8)
        vl=FMD.render(val,True,col); screen.blit(vl,(sb.right-24-vl.get_width(),ry+8))
    py2=sb.bottom+18; ctr("Your Party",FSM,GRAY,py2)
    for idx,mon in enumerate(party):
        tx=WIDTH//2-len(party)*44//2+idx*44+2; ty=py2+26
        panel((tx,ty,40,40),col=PANEL2,bdr=BDR2,r=6)
        mini=pygame.transform.scale(create_mon_sprite(mon.color,mon.type,32),(30,30))
        screen.blit(mini,(tx+5,ty+5))
        ratio=mon.hp/mon.max_hp
        pygame.draw.circle(screen,GRN if ratio>0.5 else YEL if ratio>0.25 else RED,(tx+36,ty+6),4)
    ctr("[ENTER] Back to Title",FSM,GRAY,HEIGHT-30)

# ══════════════════════════════════════════════════════════════════════════
# HISTORY SCREEN
# ══════════════════════════════════════════════════════════════════════════
def draw_history():
    screen.fill(BG)
    ctr("RUN  HISTORY", FLG, WHITE, 18)
    txt(f"Total: {data['runs']} runs  •  Wins: {data['wins']}  •  Losses: {data['losses']}",
        FT, GRAY, 20, 58)
    history = data.get("history", [])
    if not history:
        ctr("No runs recorded yet.", FMD, GRAY, HEIGHT//2-20)
        ctr("[ENTER / ESC] Back", FSM, GRAY, HEIGHT-30); return
    hdr_y=80
    cols=[(18,"#"),(55,"Outcome"),(160,"Starter"),(280,"Boss"),
          (430,"Steps"),(530,"Enc."),(610,"Caught"),(700,"Time")]
    for cx,cl in cols: txt(cl,FT,GRAY,cx,hdr_y)
    pygame.draw.line(screen,BDR,(14,hdr_y+18),(WIDTH-14,hdr_y+18),1)
    row_h=30; visible=13
    start=max(0,min(history_scroll,len(history)-visible))
    for i,entry in enumerate(reversed(history[:])):
        if i<start: continue
        if i>=start+visible: break
        ry=hdr_y+22+(i-start)*row_h
        if (i%2)==0: pygame.draw.rect(screen,PANEL,(14,ry-2,WIDTH-28,row_h-2),border_radius=4)
        oc=entry.get("outcome","?"); oc_col=GRN if oc=="WIN" else RED
        for cx,cv,cc in [
            (18,  str(entry.get("run","?")),        WHITE),
            (55,  oc,                               oc_col),
            (160, str(entry.get("starter","?")),    WHITE),
            (280, str(entry.get("boss","?")),        YEL),
            (430, str(entry.get("steps",0)),        BLU),
            (530, str(entry.get("encounters",0)),   GRN),
            (610, str(entry.get("catches",0)),      YEL),
            (700, f"{entry.get('duration',0):.0f}s",GRAY),
        ]: txt(cv,FT,cc,cx,ry)
    if len(history)>visible:
        txt(f"↑↓ scroll  ({start+1}-{min(start+visible,len(history))} of {len(history)})",
            FT,GRAY,14,HEIGHT-46)
    ctr("[ENTER / ESC] Back to Title", FSM, GRAY, HEIGHT-24)

# ══════════════════════════════════════════════════════════════════════════
# WORLD HUD
# ══════════════════════════════════════════════════════════════════════════
def draw_hud():
    pygame.draw.rect(screen,(8,8,14),(0,0,WIDTH,30))
    txt(f"Team {len(party)}/{TEAM_LIMIT}",FT,WHITE,10,8)
    txt(f"Steps: {player.steps_total}",FT,WHITE,110,8)
    txt(f"Encounters: {sess['encounters']}",FT,WHITE,230,8)
    txt(f"Boss: {current_boss.name}",FT,YEL,380,8)
    ready = len(party) >= TEAM_LIMIT
    hint = "→ Right edge + [B] = fight boss!" if ready else "Walk on GREEN tiles to find Pokemon"
    hl = FT.render(hint,True,YEL if ready else GRAY)
    screen.blit(hl,(WIDTH-hl.get_width()-10,8))
    for idx,mon in enumerate(party):
        tx=10+idx*44; ty=HEIGHT-46
        panel((tx,ty,40,40),col=PANEL2,bdr=BDR,r=6)
        mini=pygame.transform.scale(create_mon_sprite(mon.color,mon.type,32),(30,30))
        screen.blit(mini,(tx+5,ty+5))
        ratio=mon.hp/mon.max_hp
        pygame.draw.circle(screen,GRN if ratio>0.5 else YEL if ratio>0.25 else RED,(tx+35,ty+5),4)

# ══════════════════════════════════════════════════════════════════════════
# PLAYER MOVEMENT (maze-aware)
# ══════════════════════════════════════════════════════════════════════════
def try_move(dx, dy):
    """Move player if destination is walkable in the maze."""
    nx, ny = player.x + dx, player.y + dy
    if tmap is not None and is_walkable(tmap, nx, ny):
        player.move(dx, dy)
        return True
    return False

# ══════════════════════════════════════════════════════════════════════════
# END-OF-RUN logic
# ══════════════════════════════════════════════════════════════════════════
def end_run(outcome):
    global state, run_stats
    dm.add_win(data) if outcome=="WIN" else dm.add_loss(data)
    dm.update_best_team(data, len(party))
    dm.finish_run(data, sess, outcome, current_boss.name, len(party), starter_name)
    dm.save(data)
    run_stats = {
        "run":      data["runs"],
        "outcome":  outcome,
        "starter":  starter_name,
        "boss":     current_boss.name,
        "steps":    sess["steps"],
        "encounters": sess["encounters"],
        "catches":  len(party)-1,
        "duration": round(time.time()-sess["start_time"],1),
        "team_hp":  sum(m.hp for m in party),
    }
    state = "stats"


def reset_run():
    global player, tmap, grass_set, current_boss, party
    global active_index, move_index, sess, msg_lines, dmg_popups, starter_name
    tmap, grass_set, _ = generate_maze()
    sx, sy = player_start_pos()
    player = Player()
    player.x, player.y = sx, sy
    current_boss = random.choice(bosses).clone()
    dm.add_run(data); dm.add_boss(data, current_boss.name)
    party=[]; active_index=0; move_index=0
    sess=dm.new_session(); msg_lines=[]; dmg_popups.clear()
    starter_name=""; _scache.clear()


# ══════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════
tmap, grass_set, _ = generate_maze()
sx0, sy0 = player_start_pos()
player.x, player.y = sx0, sy0
dm.add_run(data)
dm.add_boss(data, current_boss.name)

running = True

# ══════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════
while running:
    clock.tick(FPS)

    for pop in dmg_popups[:]:
        pop["y"] += pop["vy"]; pop["vy"] *= 0.92; pop["life"] -= 1
        if pop["life"] <= 0: dmg_popups.remove(pop)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dm.save(data); running = False

        if event.type == pygame.KEYDOWN:

            # ── TITLE ──────────────────────────────────────────────────
            if state == "title":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    state = "starter"
                elif event.key == pygame.K_h:
                    state = "history"

            # ── STARTER ────────────────────────────────────────────────
            elif state == "starter":
                if event.key == pygame.K_ESCAPE:
                    state = "title"
                for i, key in enumerate((pygame.K_1, pygame.K_2, pygame.K_3)):
                    if event.key == key:
                        party = [starters[i].clone()]
                        starter_name = party[0].name
                        active_index = 0; move_index = 0
                        msg_lines = []; dmg_popups.clear()
                        dm.add_starter(data, starter_name)
                        sess = dm.new_session()
                        state = "world"

            # ── WORLD ──────────────────────────────────────────────────
            elif state == "world":
                moved = False
                if event.key == pygame.K_LEFT:  moved = try_move(-1, 0)
                if event.key == pygame.K_RIGHT: moved = try_move( 1, 0)
                if event.key == pygame.K_UP:    moved = try_move( 0,-1)
                if event.key == pygame.K_DOWN:  moved = try_move( 0, 1)
                if moved:
                    dm.record_step(sess)
                    if encounter(player, grass_set):
                        dm.record_encounter(sess)
                        enemy = random_wild()
                        move_index=0; msg_lines=[]; dmg_popups.clear()
                        dm.start_battle_timer(sess)
                        state = "battle"
                if event.key == pygame.K_b and is_boss_gate(player) and len(party) >= TEAM_LIMIT:
                    enemy = current_boss.clone()
                    for mon in party: mon.reset()
                    move_index=0; msg_lines=[]; dmg_popups.clear()
                    dm.start_battle_timer(sess)
                    state = "battle"

            # ── BATTLE ─────────────────────────────────────────────────
            elif state == "battle":
                if event.key == pygame.K_UP:
                    move_index = (move_index-1) % 4
                elif event.key == pygame.K_DOWN:
                    move_index = (move_index+1) % 4

                elif event.key == pygame.K_t:
                    # open switch selection screen (no turn consumed yet)
                    state = "switch_select"

                elif event.key == pygame.K_SPACE:
                    p = party[active_index]
                    move = p.moves[move_index]
                    dmg, mult = attack(p, enemy, move)
                    dm.record_move_use(sess, move.type)

                    eff = ""
                    if mult >= 2:  eff = " Super effective!"
                    elif mult == 0: eff = " No effect."
                    elif mult <  1: eff = " Not very effective…"
                    ec2 = YEL if mult>=2 else GRAY if mult==0 else WHITE

                    e_size2 = 148 if enemy.name==current_boss.name else 116
                    epx2=int(WIDTH*0.62); epy2=int(HEIGHT*0.42)
                    add_popup(epx2, epy2-e_size2//2, dmg, mult)

                    msg_lines=[(f"{p.name} used {move.name}!", WHITE),
                                (f"Dealt {dmg} dmg.{eff}", ec2)]
                    msg_timer = 90

                    if enemy.is_fainted():
                        dm.end_battle_timer(sess, data, enemy.hp)
                        if enemy.name == current_boss.name:
                            end_run("WIN")
                        else:
                            msg_lines.append((f"{enemy.name} fainted!", RED))
                            if len(party) < TEAM_LIMIT:
                                party.append(enemy.clone())
                                dm.add_catch(data, enemy.name)
                                msg_lines.append((f"Got {enemy.name}!", GRN))
                            partial_heal(party, 0.30)
                            state = "world"
                    else:
                        # enemy counter-attack
                        emove = random.choice(enemy.moves)
                        edm, _ = attack(enemy, p, emove)
                        dm.record_move_use(sess, emove.type)
                        msg_lines.append((f"{enemy.name}: {emove.name}! (-{edm}HP)", RED))
                        ppx2=int(WIDTH*0.25); ppy2=int(HEIGHT*0.60)
                        add_popup(ppx2, ppy2-116//2, edm, 1.0)
                        if p.is_fainted():
                            alive = [m for m in party if not m.is_fainted()]
                            if not alive:
                                dm.end_battle_timer(sess, data, 0)
                                end_run("LOSS")
                            else:
                                active_index = next(i for i,m in enumerate(party) if not m.is_fainted())

            # ── SWITCH SELECT ──────────────────────────────────────────
            elif state == "switch_select":
                if event.key == pygame.K_ESCAPE:
                    # cancel – no turn used
                    state = "battle"
                else:
                    for i, key in enumerate((pygame.K_1,pygame.K_2,pygame.K_3,
                                             pygame.K_4,pygame.K_5,pygame.K_6)):
                        if event.key == key and i < len(party):
                            chosen = party[i]
                            if chosen.is_fainted():
                                break   # can't pick fainted
                            if i == active_index:
                                break   # already out, no turn
                            # VALID SWITCH — costs a turn
                            active_index = i
                            move_index = 0
                            state = "battle"
                            # enemy attacks the newly-sent-out pokemon
                            p_new = party[active_index]
                            emove = random.choice(enemy.moves)
                            edm, _ = attack(enemy, p_new, emove)
                            dm.record_move_use(sess, emove.type)
                            msg_lines = [
                                (f"Go, {p_new.name}!", WHITE),
                                (f"{enemy.name}: {emove.name}! (-{edm}HP)", RED),
                            ]
                            ppx2=int(WIDTH*0.25); ppy2=int(HEIGHT*0.60)
                            add_popup(ppx2, ppy2-116//2, edm, 1.0)
                            msg_timer = 90
                            if p_new.is_fainted():
                                alive = [m for m in party if not m.is_fainted()]
                                if not alive:
                                    dm.end_battle_timer(sess, data, 0)
                                    end_run("LOSS")
                            break

            # ── STATS ──────────────────────────────────────────────────
            elif state == "stats":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    reset_run(); state = "title"

            # ── HISTORY ────────────────────────────────────────────────
            elif state == "history":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                    state = "title"
                elif event.key == pygame.K_DOWN:
                    history_scroll = min(history_scroll+1, max(0,len(data.get("history",[]))-13))
                elif event.key == pygame.K_UP:
                    history_scroll = max(0, history_scroll-1)

    if msg_timer > 0:
        msg_timer -= 1

    # ── Render ─────────────────────────────────────────────────────────────
    if   state == "title":         draw_title()
    elif state == "starter":       draw_starter()
    elif state == "world":         draw_world(screen,tmap,grass_set,player); draw_hud()
    elif state == "battle":        draw_battle()
    elif state == "switch_select": draw_switch_select()
    elif state == "stats":         draw_stats()
    elif state == "history":       draw_history()

    pygame.display.flip()

pygame.quit()