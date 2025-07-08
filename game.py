import pgzrun
from platformer import *

TILE_SIZE = 18
ROWS = 30
COLS = 20
WIDTH = TILE_SIZE * ROWS
HEIGHT = TILE_SIZE * COLS
TITLE = "2D GAME"

game_state = "menu"
menu_index = 0
config_index = 0
music_enabled = True
sfx_enabled = True

platforms = build("platformer_platforms.csv", TILE_SIZE)
obstacles = build("platformer_obstacles.csv", TILE_SIZE)
mushrooms = build("platformer_mushrooms.csv", TILE_SIZE)

color_key = (0, 0, 0)
fox_stand = Sprite("fox.png", (0,0,32,32), 5, color_key, 30)
fox_walk = Sprite("fox.png", (0, 64,32,32), 8, color_key, 5)

player = SpriteActor(fox_stand)
player.bottomleft = (0, HEIGHT - TILE_SIZE)
player.velocity_x = 3
player.velocity_y = 0
player.jumping = False
player.alive = True

slime_walk = Sprite("slime_fire_walk_a.png", (0, 0, 128, 128), 1, color_key, 10)
slime_walk.images.append(Sprite("slime_fire_walk_b.png", (0, 0, 128, 128), 1, color_key, 10).images[0])

slime_jump = Sprite("slime_normal_walk_a.png", (0, 0, 128, 128), 1, color_key, 10)
slime_jump.images.append(Sprite("slime_normal_walk_b.png", (0, 0, 128, 128), 1, color_key, 10).images[0])

slime = SpriteActor(slime_walk)
slime.scale = 0.15
slime.pos = (200, HEIGHT - TILE_SIZE - 9 )
slime.velocity = 0.5
slime.left_limit = 180
slime.right_limit = 270

slimej = SpriteActor(slime_jump)
slimej.scale = 0.15
slimej.pos = (200, HEIGHT - TILE_SIZE * 7 - 8 )
slimej.velocity = 0.5
slimej.left_limit = 190
slimej.right_limit = 260

gravity = 1
jump_velocity = -10
over = False
win = False

def draw():
    screen.clear()
    screen.fill("skyblue")

    if game_state == "menu":
        draw_menu()
    elif game_state == "config":
        draw_config()
    elif game_state == "jogo":
        slime.draw()
        slimej.draw()
        for platform in platforms:
            platform.draw()
        for obstacle in obstacles:
            obstacle.draw()
        for mushroom in mushrooms:
            mushroom.draw()
        if player.alive:
            player.draw()
        if over:
            screen.draw.text("Game Over", center=(WIDTH/2, HEIGHT/2))
        if win:
            screen.draw.text("You Win", center=(WIDTH/2, HEIGHT/2))

def update():
    if game_state != "jogo": return
    global over, win

    if (keyboard.LEFT and player.midleft[0] > 0) and player.alive:
        player.x -= player.velocity_x
        player.sprite = fox_walk
        player.flip_x = True
        if player.collidelist(platforms) != -1:
            object = platforms[player.collidelist(platforms)]
            player.x = object.x + (object.width / 2 + player.width / 2)

    elif (keyboard.RIGHT and player.midright[0] < WIDTH) and player.alive:
        player.x += player.velocity_x
        player.sprite = fox_walk
        player.flip_x = False
        if player.collidelist(platforms) != -1:
            object = platforms[player.collidelist(platforms)]
            player.x = object.x - (object.width / 2 + player.width / 2)

    player.y += player.velocity_y
    player.velocity_y += gravity

    if player.collidelist(platforms) != -1:
        object = platforms[player.collidelist(platforms)]
        if player.velocity_y >= 0:
            player.y = object.y - (object.height / 2 + player.height / 2)
            player.jumping = False
        else:
            player.y = object.y + (object.height / 2 + player.height / 2)
        player.velocity_y = 0

    if player.collidelist(obstacles) != -1:
        player.alive = False
        over = True

    for mushroom in mushrooms:
        if player.colliderect(mushroom):
            mushrooms.remove(mushroom)
            if sfx_enabled:
                sounds.sfx_coin.play()

    if len(mushrooms) == 0:
        win = True

    if player.colliderect(slime) or player.colliderect(slimej):
        player.alive = False
        over = True

    slime.x -= slime.velocity
    if slime.x < slime.left_limit or slime.x > slime.right_limit:
        slime.velocity *= -1
        slime.flip_x = not slime.flip_x

    slimej.x -= slimej.velocity
    if slimej.x < slimej.left_limit or slimej.x > slimej.right_limit:
        slimej.velocity *= -1
        slimej.flip_x = not slimej.flip_x

def on_key_down(key):
    global menu_index, config_index, game_state, music_enabled, sfx_enabled

    if game_state == "menu":
        if key == keys.UP:
            menu_index = (menu_index - 1) % 3
        elif key == keys.DOWN:
            menu_index = (menu_index + 1) % 3
        elif key == keys.RETURN:
            if menu_index == 0:
                game_state = "jogo"
                if music_enabled:
                    music.play("theme")
            elif menu_index == 1:
                game_state = "config"
            elif menu_index == 2:
                exit()

    elif game_state == "config":
        if key == keys.UP:
            config_index = (config_index - 1) % 3
        elif key == keys.DOWN:
            config_index = (config_index + 1) % 3
        elif key == keys.RETURN:
            if config_index == 0:
                music_enabled = not music_enabled
                if music_enabled:
                    music.play("theme")
                else:
                    music.stop()
            elif config_index == 1:
                sfx_enabled = not sfx_enabled
            elif config_index == 2:
                game_state = "menu"

    elif game_state == "jogo":
        if (key == keys.UP and not player.jumping) and player.alive:
            player.velocity_y = jump_velocity
            player.jumping = True
            if sfx_enabled:
                sounds.sfx_jump.play()

def on_key_up(key):
    if game_state == "jogo" and (key == keys.LEFT or key == keys.RIGHT) and player.alive:
        player.sprite = fox_stand
        player.sprite.i = 0
        player.sprite.frame_num = player.sprite.frames

def draw_menu():
    options = ["Play", "Options", "Exit"]
    screen.draw.text("Fox 2D", center=(WIDTH // 2, 50), fontsize=60, color="black")
    screen.draw.text("Take all Mushrooms", center=(WIDTH // 2, 80), fontsize=20, color="black")
    for i, text in enumerate(options):
        y = 200 + i * 70
        color = "yellow" if i == menu_index else "white"
        screen.draw.text(text, center=(WIDTH // 2, y), fontsize=40, color=color)

def draw_config():
    options = [
        f"Music: {'ON' if music_enabled else 'OFF'}",
        f"Effect: {'ON' if sfx_enabled else 'OFF'}",
        "Back"
    ]
    screen.draw.text("Options", center=(WIDTH // 2, 100), fontsize=50, color="black")
    for i, text in enumerate(options):
        y = 200 + i * 70
        color = "yellow" if i == config_index else "white"
        screen.draw.text(text, center=(WIDTH // 2, y), fontsize=36, color=color)

pgzrun.go()