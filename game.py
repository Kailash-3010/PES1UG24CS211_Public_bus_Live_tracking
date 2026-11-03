"""Treasure Hunt: a small Pygame dungeon crawler.

A dungeon of rooms and corridors is generated at random. The player must
walk to the KEY tile and then to the CHEST tile to win. Press R to restart.
"""
import random

import pygame

TILE = 40
COLS, ROWS = 20, 15
WALL, FLOOR, CHEST, KEY = 0, 1, 2, 3
SPEED = 3


def _carve_rooms(grid):
    """Carve up to eight non-overlapping rectangular rooms into the grid."""
    rooms = []
    # Bandit B311: the PRNG only picks room sizes/positions for gameplay.
    # Nothing here is a secret, token or key, so a cryptographic RNG is not
    # needed; the check is skipped for these four lines only.
    for _ in range(8):
        w = random.randint(3, 6)  # nosec B311
        h = random.randint(3, 5)  # nosec B311
        x = random.randint(1, COLS - w - 1)  # nosec B311
        y = random.randint(1, ROWS - h - 1)  # nosec B311
        room = pygame.Rect(x, y, w, h)
        overlap = any(room.inflate(2, 2).colliderect(r) for r in rooms)
        if not overlap:
            rooms.append(room)
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    grid[ry][rx] = FLOOR
    return rooms


def _connect_rooms(grid, rooms):
    """Join each room to the next one with an L-shaped corridor."""
    for i in range(len(rooms) - 1):
        ax, ay = rooms[i].centerx, rooms[i].centery
        bx, by = rooms[i + 1].centerx, rooms[i + 1].centery
        cx = ax
        while cx != bx:
            grid[ay][cx] = FLOOR
            cx += 1 if bx > cx else -1
        cy = ay
        while cy != by:
            grid[cy][bx] = FLOOR
            cy += 1 if by > cy else -1


def generate_world():
    """Build a new dungeon grid.

    Returns:
        A tuple ``(grid, start)`` where ``grid`` is a ROWS x COLS list of
        tile ids and ``start`` is the first room's Rect (or None if no
        room could be placed).
    """
    grid = [[WALL] * COLS for _ in range(ROWS)]
    rooms = _carve_rooms(grid)
    _connect_rooms(grid, rooms)

    if len(rooms) >= 2:
        cr, ck = rooms[-1], rooms[-2]
        grid[cr.centery][cr.centerx] = CHEST
        grid[ck.centery][ck.centerx] = KEY

    start = rooms[0] if rooms else None
    return grid, start


COLORS = {
    WALL: (60, 50, 70),
    FLOOR: (200, 190, 170),
    CHEST: (200, 160, 30),
    KEY: (220, 220, 60),
}


class Player:
    """The player-controlled character and its tile-based collision."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.color = (60, 120, 220)
        self.has_key = False

    def move(self, keys, grid, rows, cols):
        """Move the player according to the pressed arrow/WASD keys."""
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED
        self._try_move(dx, 0, grid, rows, cols)
        self._try_move(0, dy, grid, rows, cols)

    def _try_move(self, dx, dy, grid, rows, cols):
        new = self.rect.move(dx, dy)
        corners = [(new.left, new.top), (new.right - 1, new.top),
                   (new.left, new.bottom - 1),
                   (new.right - 1, new.bottom - 1)]
        for px, py in corners:
            c, r = px // TILE, py // TILE
            if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] == WALL:
                return
        self.rect = new

    def draw(self, screen):
        """Draw the player, with a small key marker once the key is held."""
        pygame.draw.ellipse(screen, self.color, self.rect)
        if self.has_key:
            marker = (self.rect.right - 6, self.rect.top + 6)
            pygame.draw.circle(screen, (220, 220, 60), marker, 5)


WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 50
FPS = 60


class GameEngine:
    """Owns the window, the game state and the main loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Treasure Hunt")
        self.clock = pygame.time.Clock()
        self.fonts = {
            "hud": pygame.font.SysFont("monospace", 24),
            "title": pygame.font.SysFont("monospace", 40, bold=True),
        }
        self.reset()

    def reset(self):
        """Generate a new dungeon and place the player in the first room."""
        self.grid, start = generate_world()
        if start:
            sx = start.x * TILE + 6
            sy = start.y * TILE + 6
        else:
            sx, sy = TILE + 6, TILE + 6
        self.player = Player(sx, sy)
        self.won = False
        self.status = "Find the KEY, then the CHEST!"

    def handle_events(self):
        """Process window events; return False when the game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        """Advance one frame: move the player and handle key/chest pickup."""
        if self.won:
            return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.grid, ROWS, COLS)
        pr = self.player.rect.centery // TILE
        pc = self.player.rect.centerx // TILE
        if 0 <= pr < ROWS and 0 <= pc < COLS:
            cell = self.grid[pr][pc]
            if cell == KEY:
                self.player.has_key = True
                self.grid[pr][pc] = FLOOR
                self.status = "Got the key! Find the CHEST!"
            elif cell == CHEST and self.player.has_key:
                self.won = True
                self.status = "Treasure found!"

    def draw(self):
        """Render the map, player, HUD and (if won) the victory overlay."""
        self.screen.fill((30, 25, 40))
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                rect = pygame.Rect(c * TILE, r * TILE, TILE, TILE)
                pygame.draw.rect(self.screen, COLORS[cell], rect)
                if cell == KEY:
                    center = (c * TILE + TILE // 2, r * TILE + TILE // 2)
                    pygame.draw.circle(self.screen, (255, 240, 60), center, 10)
                elif cell == CHEST:
                    pygame.draw.rect(self.screen, (180, 120, 20),
                                     rect.inflate(-12, -12), border_radius=4)
        self.player.draw(self.screen)
        hud = pygame.Rect(0, ROWS * TILE, WIDTH, 50)
        pygame.draw.rect(self.screen, (20, 20, 35), hud)
        st = self.fonts["hud"].render(self.status + "  |  R=Restart",
                                      True, (200, 200, 200))
        self.screen.blit(st, (8, ROWS * TILE + 13))
        if self.won:
            ov = pygame.Surface((WIDTH, ROWS * TILE), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            self.screen.blit(ov, (0, 0))
            msg = self.fonts["title"].render("TREASURE FOUND!", True,
                                             (220, 180, 30))
            sub = self.fonts["hud"].render("Press R to Play Again", True,
                                           (180, 180, 180))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2,
                                   ROWS * TILE // 2 - 30))
            self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2,
                                   ROWS * TILE // 2 + 20))
        pygame.display.flip()

    def run(self):
        """Run the main loop until the window is closed."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
