import os
import sys

import pygame

speedw = 0.6
speeda = 0.6
speeds = 0.6
speedd = 0.6

def load_image(name):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Area(pygame.sprite.Sprite):
    image = load_image(r"gamedata\img\game\scene\1-335as.jpg")
    image = pygame.transform.scale(image, (image.get_width() * 2.5, image.get_height() * 2.5))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Area.image
        self.rect = Area.image.get_rect()

    def move_up(self):  # тоже не забыть сделать масштабирование
        global speedw
        a = speedw
        self.rect = self.rect.move(0, a)
        if speedw < 6.25:
            speedw += 0.4

    def move_down(self):  # тоже не забыть сделать масштабирование
        global speeds
        a = speeds
        self.rect = self.rect.move(0, -int(a))
        if speeds < 6.25:
            speeds += 0.4

    def move_right(self):  # тоже не забыть сделать масштабирование
        global speedd
        a = speedd
        self.rect = self.rect.move(-int(a), 0)
        if speedd < 6.25:
            speedd += 0.4

    def move_left(self):  # тоже не забыть сделать масштабирование
        global speeda
        a = speeda
        self.rect = self.rect.move(int(a), 0)
        if speeda < 6.25:
            speeda += 0.4

    def inertion_up(self):
        global speedw
        if speedw >= 0.6:
            a = speedw
            self.rect = self.rect.move(0, a)
            speedw -= 0.4

    def inertion_down(self):
        global speeds
        if speeds >= 0.6:
            a = speeds
            self.rect = self.rect.move(0, -int(a))
            speeds -= 0.4

    def inertion_left(self):
        global speeda
        if speeda >= 0.6:
            a = speeda
            self.rect = self.rect.move(int(a), 0)
            speeda -= 0.4

    def inertion_right(self):
        global speedd
        if speedd >= 0.6:
            a = speedd
            self.rect = self.rect.move(-int(a), 0)
            speedd -= 0.4


def play():
    pygame.init()
    SCREENRES = pygame.display.Info()
    screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
    size = SCREENRES.current_w, SCREENRES.current_h
    screen = pygame.display.set_mode(size)

    areas = pygame.sprite.Group()
    ar = Area(areas)

    heroes = pygame.sprite.Group()  # отрисовка героя
    hero = pygame.sprite.Sprite(heroes)
    hero_image = load_image(r"gamedata\img\game\char\cla_char_sprite_0_b.png").convert_alpha()
    hero.image = pygame.transform.scale(hero_image, (hero_image.get_width() * 2.5, hero_image.get_width() * 2.5))

    hero.rect = hero.image.get_rect()
    hero.rect.x = SCREENRES.current_w // 2 - hero.rect[2] // 2  # чтоб он в центре спавнился
    hero.rect.y = SCREENRES.current_h // 2 - hero.rect[3] // 2  # не забыть сделать увеличение/уменьшение размеров героя

    fps = 60
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    ar.inertion_up()
                if event.key == pygame.K_a:
                    ar.inertion_left()
                if event.key == pygame.K_s:
                    ar.inertion_down()
                if event.key == pygame.K_d:
                    ar.inertion_right()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    speedw = 0.6
                if event.key == pygame.K_a:
                    speeda = 0.6
                if event.key == pygame.K_s:
                    speeds = 0.6
                if event.key == pygame.K_d:
                    speedd = 0.6
        keys = pygame.key.get_pressed()
        # движение по зажатию
        if keys[pygame.K_w]:
            ar.move_up()
        if keys[pygame.K_d]:
            ar.move_right()
        if keys[pygame.K_a]:
            ar.move_left()
        if keys[pygame.K_s]:
            ar.move_down()
        # инерция
        if not keys[pygame.K_w]:
            ar.inertion_up()
        if not keys[pygame.K_d]:
            ar.inertion_right()
        if not keys[pygame.K_a]:
            ar.inertion_left()
        if not keys[pygame.K_s]:
            ar.inertion_down()

        areas.draw(screen)
        heroes.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()