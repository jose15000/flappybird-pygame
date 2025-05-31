import pygame, random, sys
from pygame.locals import *

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800
SPEED = 10
GRAVITY = 1
GAME_SPEED = 10

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 200

game_state = "playing"

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")

font = pygame.font.SysFont("Arial", 40)
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 60)
score = 0

#Efeitos Sonoros por comando e colisão
sound_jump= pygame.mixer.Sound('./venv/sound/jump.wav')
sound_hit= pygame.mixer.Sound('./venv/sound/hitHurt.wav')
sound_point = pygame.mixer.Sound('./venv/sound/SFX： Point - Flappy Bird.mp3')

def draw_restart_button():
    pygame.draw.rect(screen, (0, 200, 0), button_rect)
    text = font.render("Jogar Novamente", True, (255, 255, 255))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [
            pygame.image.load('bluebird-upflap.png').convert_alpha(),
            pygame.image.load('bluebird-midflap.png').convert_alpha(),
            pygame.image.load('bluebird-downflap.png').convert_alpha()
        ]
        self.speed = SPEED
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        super().__init__()
        self.image = pygame.image.load('pipe-red.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.scored = False

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        super().__init__()
        self.image = pygame.image.load('base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -sprite.rect[2]

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return (pipe, pipe_inverted)

def reset_game():
    global bird_group, pipe_group, ground_group, bird, game_state, score
    bird_group.empty()
    pipe_group.empty()
    ground_group.empty()
    score = 0

    bird = Bird()
    bird_group.add(bird)

    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    game_state = "playing"

BACKGROUND = pygame.image.load('background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
ground_group = pygame.sprite.Group()

bird = Bird()
bird_group.add(bird)

for i in range(2):
    ground = Ground(GROUND_WIDTH * i)
    ground_group.add(ground)

for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

clock = pygame.time.Clock()

while True:
    clock.tick(30)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "playing" and event.type == KEYDOWN and event.key == K_SPACE:
            bird.bump()
            sound_jump.play()

        if game_state == "game_over" and event.type == MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                reset_game()

    screen.blit(BACKGROUND, (0, 0))

    if game_state == "playing":
        # Atualiza sprites
        bird_group.update()
        ground_group.update()
        pipe_group.update()

        # Conta pontos ao passar pelos canos
        for pipe in pipe_group:
            if (pipe.rect.right < bird.rect.left) and (not pipe.scored):
                score += 0.5
                pipe.scored = True
                sound_point.play()

        # Gera novo chão
        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        # Gera novos pipes
        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])
            pipes = get_random_pipes(SCREEN_WIDTH * 2)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        # Checa colisão
        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            sound_hit.play()
            game_state = "game_over"

    # Desenha sprites
    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)

    # Desenha pontuação
    score_text = font.render(f"Pontos: {int(score)}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if game_state == "game_over":
        draw_restart_button()

    pygame.display.update()