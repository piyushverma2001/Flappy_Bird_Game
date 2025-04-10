import random
import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_UP, K_SPACE, K_ESCAPE

FPS = 60
SCREEN_HEIGHT, SCREEN_WIDTH = 511, 289
GROUNDY = SCREEN_HEIGHT * 0.8

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

ASSET_DIR = "gallery/sprites/"
PLAYER = ASSET_DIR + "bird.png"
BACKGROUND = ASSET_DIR + "background.png"
PIPE = ASSET_DIR + "pipe.png"

GAME_SPRITES = {}
GAME_SOUNDS = {}

def welcomeScreen():
    player_x = SCREEN_WIDTH // 5
    player_y = (SCREEN_HEIGHT - GAME_SPRITES['player'].get_height()) // 2
    message_x = (SCREEN_WIDTH - GAME_SPRITES['message'].get_width()) // 2
    message_y = int(SCREEN_HEIGHT * 0.13)
    base_x = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_SPACE or event.key == pygame.K_UP
            ):
                return

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        SCREEN.blit(GAME_SPRITES['message'], (message_x, message_y))
        SCREEN.blit(GAME_SPRITES['base'], (base_x, GROUNDY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame():
    score = 0
    playerx = SCREEN_WIDTH // 5
    playery = SCREEN_WIDTH // 2
    basex = 0

    pipe1 = getRandomPipe()
    pipe2 = getRandomPipe()

    upperPipes = [
        {'x': SCREEN_WIDTH+200, 'y':pipe1[0]['y']},
        {'x': SCREEN_WIDTH+200+(SCREEN_WIDTH/2), 'y':pipe2[0]['y']},
    ]

    lowerPipes = [
        {'x': SCREEN_WIDTH+200, 'y':pipe1[1]['y']},
        {'x': SCREEN_WIDTH+200+(SCREEN_WIDTH/2), 'y':pipe2[1]['y']},
    ]

    pipe_velocity_x = -4
    player_velocity_y = -9
    player_max_velocity = 10
    player_min_velocity = -8
    gravity = 1
    flap_velocity = -8
    flapped = False


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_SPACE or event.key == pygame.K_UP
            ):
                if playery > 0:
                    player_velocity_y = flap_velocity
                    flapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        
        if crashTest:
            return

        player_mid = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipe_mid = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipe_mid <= player_mid < pipe_mid + 4:
                score += 1
                print(f"Score: {score}")
                GAME_SOUNDS['point'].play()

        if player_velocity_y <player_max_velocity and not flapped:
            player_velocity_y += gravity

        if flapped:
            flapped = False        
        
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(player_velocity_y, GROUNDY - playery - playerHeight)

        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipe_velocity_x
            lowerPipe['x'] += pipe_velocity_x

        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        digits = [int(d) for d in str(score)]
        total_width = sum(GAME_SPRITES['numbers'][d].get_width() for d in digits)
        Xoffset = (SCREEN_WIDTH - total_width) // 2

        for d in digits:
            SCREEN.blit(GAME_SPRITES['numbers'][d], (Xoffset, SCREEN_HEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][d].get_width()
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    player_h = GAME_SPRITES['player'].get_height()
    pipe_w = GAME_SPRITES['pipe'][0].get_width()

    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipe_h = GAME_SPRITES['pipe'][0].get_height()
        if playery < pipe['y'] + pipe_h and abs(playerx - pipe['x']) < pipe_w:
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if playery + player_h > pipe['y'] and abs(playerx - pipe['x']) < pipe_w:
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    pipe_height = GAME_SPRITES['pipe'][0].get_height()
    base_height = GAME_SPRITES['base'].get_height()
    offset = SCREEN_HEIGHT // 3

    min_y = offset
    max_y = SCREEN_HEIGHT - base_height - int(1.2 * offset)
    pipe_y = random.randint(min_y, max_y)

    pipe_x = SCREEN_WIDTH + 10
    top_pipe_y = pipe_y - pipe_height - offset

    return [
        {'x': pipe_x, 'y': top_pipe_y},
        {'x': pipe_x, 'y': pipe_y}
    ]

def load_sprites():
    GAME_SPRITES['numbers'] = tuple(
        pygame.image.load(f'gallery/sprites/{i}.png').convert_alpha() for i in range(10)
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

def load_sounds():
    sound_names = ['die', 'hit', 'point', 'swoosh', 'wing']
    for name in sound_names:
        GAME_SOUNDS[name] = pygame.mixer.Sound(f'gallery/audio/{name}.wav')

if __name__ == "__main__":
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')

    load_sprites()
    load_sounds()

    while True:
        welcomeScreen()
        mainGame()