"""
world.py  –  8-bit randomly-generated maze.
Algorithm : Recursive-backtracker (perfect maze) on a cell grid.
Tiles     : FLOOR (yellow/sand), GRASS (green), WALL (grey rock)
Boss gate : right-centre edge, always reachable.
"""
import random, math, pygame
from config import MAP_W, MAP_H, TILE, WILD_ENCOUNTER_RATE

# ── Cell grid dimensions ───────────────────────────────────────────────────
# Each cell occupies 2×2 tiles; walls = 1 tile wide
CELL_COLS = (MAP_W - 1) // 2
CELL_ROWS = (MAP_H - 1) // 2
BOSS_CELL_ROW = CELL_ROWS // 2
BOSS_CELL_COL = CELL_COLS - 1

WALL = 2
FLOOR = 0
GRASS = 1

# ── 8-bit colours ──────────────────────────────────────────────────────────
CF = {
    "fa": (220, 196,  96), "fb": (200, 178,  78), "fd": (176, 156,  58),
    "ga": ( 56, 148,  40), "gb": ( 44, 128,  28),
    "bl": ( 80, 180,  56), "tp": (120, 220,  80),
    "wa": (110, 108, 116), "wb": ( 88,  86,  94),
    "wh": (148, 146, 158), "ws": ( 56,  54,  62),
    "gbg":( 18,  12,  36), "gbd":(160, 120, 255), "ggl":(200, 160, 255),
}

_TC: dict = {}
_RNG = random.Random(0)

# ── Tile builders ─────────────────────────────────────────────────────────

def _floor(v):
    k = f"f{v}"
    if k not in _TC:
        b = CF["fa"] if v == 0 else CF["fb"]
        s = pygame.Surface((TILE, TILE)); s.fill(b)
        alt = tuple(max(0, c - 14) for c in b)
        for ty in range(0, TILE, 8):
            for tx in range(0, TILE, 8):
                if (tx//8 + ty//8) % 2 == 0:
                    pygame.draw.rect(s, alt, (tx, ty, 8, 8))
        dx, dy = _RNG.randint(3,TILE-4), _RNG.randint(3,TILE-4)
        s.set_at((dx, dy), CF["fd"])
        _TC[k] = s
    return _TC[k]


def _grass(v):
    k = f"g{v}"
    if k not in _TC:
        b = CF["ga"] if v == 0 else CF["gb"]
        s = pygame.Surface((TILE, TILE)); s.fill(b)
        for bx in range(2, TILE-2, 5):
            h = _RNG.randint(7, 13); mx = bx + _RNG.randint(-1, 1)
            for by in range(TILE-h, TILE): s.set_at((bx, by), CF["bl"])
            s.set_at((mx, TILE-h-1), CF["tp"]); s.set_at((mx, TILE-h-2), CF["tp"])
        for tx in range(TILE): s.set_at((tx, TILE-1), tuple(max(0,c-18) for c in b))
        _TC[k] = s
    return _TC[k]


def _wall():
    if "w" not in _TC:
        s = pygame.Surface((TILE, TILE)); s.fill(CF["wa"])
        pygame.draw.rect(s, CF["wb"], (2, 2, TILE-4, TILE-4))
        pygame.draw.line(s, CF["wh"], (1,1), (TILE-2,1), 1)
        pygame.draw.line(s, CF["wh"], (1,1), (1,TILE-2), 1)
        pygame.draw.line(s, CF["ws"], (1,TILE-1), (TILE-1,TILE-1), 1)
        pygame.draw.line(s, CF["ws"], (TILE-1,1), (TILE-1,TILE-1), 1)
        for _ in range(4):
            dx,dy = _RNG.randint(3,TILE-4), _RNG.randint(3,TILE-4)
            s.set_at((dx,dy), CF["ws"]); s.set_at((dx+1,dy), CF["wb"])
        _TC["w"] = s
    return _TC["w"]


# ── Maze generation ────────────────────────────────────────────────────────

def generate_maze(seed: int = None):
    """
    Build a perfect maze with recursive backtracker.
    Returns (tmap, grass_set, seed_used).
    tmap[row][col] in {WALL, FLOOR, GRASS}.
    """
    global _TC
    if seed is None:
        seed = random.randint(0, 999999)
    random.seed(seed)
    _RNG.seed(seed + 7)
    _TC.clear()   # rebuild tile surfaces for new run

    visited = [[False]*CELL_COLS for _ in range(CELL_ROWS)]
    tmap    = [[WALL]*MAP_W for _ in range(MAP_H)]

    def c2t(cr, cc):
        return cr*2+1, cc*2+1

    def carve(cr, cc):
        visited[cr][cc] = True
        tr, tc = c2t(cr, cc)
        tmap[tr][tc] = FLOOR
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        random.shuffle(dirs)
        for dr, dc in dirs:
            nr, nc = cr+dr, cc+dc
            if 0 <= nr < CELL_ROWS and 0 <= nc < CELL_COLS and not visited[nr][nc]:
                wr, wc = tr+dr, tc+dc
                tmap[wr][wc] = FLOOR
                carve(nr, nc)

    # start from left-middle
    carve(BOSS_CELL_ROW, 0)

    # ensure boss cell is open
    btr, btc = c2t(BOSS_CELL_ROW, BOSS_CELL_COL)
    tmap[btr][btc] = FLOOR

    # open a 3-tile corridor to the right edge at boss row
    for dc in range(btc, MAP_W):
        tmap[btr][dc] = FLOOR

    # open right edge (boss gate strip)
    for dr in [-1, 0, 1]:
        rr = btr + dr
        if 0 <= rr < MAP_H:
            tmap[rr][MAP_W-1] = FLOOR

    # scatter GRASS on ~38% of inner FLOOR tiles
    for r in range(1, MAP_H-1):
        for c in range(1, MAP_W-2):
            if tmap[r][c] == FLOOR and random.random() < 0.38:
                tmap[r][c] = GRASS

    # keep a FLOOR strip around boss corridor clear
    for dc in range(btc, MAP_W):
        for dr in [-1, 0, 1]:
            rr = btr + dr
            if 0 <= rr < MAP_H:
                tmap[rr][dc] = FLOOR

    grass_set = {(c, r) for r in range(MAP_H) for c in range(MAP_W)
                 if tmap[r][c] == GRASS}
    return tmap, grass_set, seed


def player_start_pos():
    """(x, y) tile for player spawn near left entrance."""
    return 1, BOSS_CELL_ROW * 2 + 1


def is_walkable(tmap, x, y):
    if not (0 <= x < MAP_W and 0 <= y < MAP_H):
        return False
    return tmap[y][x] != WALL


def encounter(player, grass_set):
    if (player.x, player.y) in grass_set:
        return random.randint(1, WILD_ENCOUNTER_RATE) == 1
    return False


def is_boss_gate(player):
    return player.x >= MAP_W - 1


# ── Drawing ───────────────────────────────────────────────────────────────

def draw_world(screen, tmap, grass_set, player):
    t_ms = pygame.time.get_ticks()

    for ty in range(MAP_H):
        for tx in range(MAP_W):
            px, py = tx*TILE, ty*TILE
            cell = tmap[ty][tx]
            if   cell == WALL:  screen.blit(_wall(),       (px, py))
            elif cell == GRASS: screen.blit(_grass((tx+ty)%2), (px, py))
            else:               screen.blit(_floor((tx+ty)%2), (px, py))

    # boss gate glow
    btr = BOSS_CELL_ROW * 2 + 1
    gx = (MAP_W-1)*TILE; gy = (btr-1)*TILE; gw = TILE; gh = 3*TILE
    pygame.draw.rect(screen, CF["gbg"], (gx, gy, gw, gh))
    pygame.draw.rect(screen, CF["gbd"], (gx, gy, gw, gh), 2)
    al = int(90 + 65*math.sin(t_ms/400))
    gl = pygame.Surface((gw, gh), pygame.SRCALPHA)
    gl.fill((*CF["ggl"], al//7)); screen.blit(gl, (gx, gy))
    f = pygame.font.SysFont("arial", 10, bold=True)
    lbl = f.render("BOSS", True, CF["ggl"])
    screen.blit(lbl, (gx+(gw-lbl.get_width())//2, gy+gh//2-lbl.get_height()//2))

    player.draw(screen, TILE)