import os
import sys

import pygame

def load_image(name):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Area(pygame.sprite.Sprite):
    image = load_image(r"gamedata\img\TestArea.jpg")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Area.image
        self.rect = Area.image.get_rect()

    def move_up(self): # тоже не забыть сделать масштабирование
        global speedw
        a = speedw
        self.rect = self.rect.move(0, int(a))
        if speedw < 10:
            speedw += 0.2

    def move_down(self): # тоже не забыть сделать масштабирование
        global speeds
        a = speeds
        self.rect = self.rect.move(0, -int(a))
        if speeds < 10:
            speeds += 0.2

    def move_right(self): # тоже не забыть сделать масштабирование
        global speedd
        a = speedd
        self.rect = self.rect.move(-int(a), 0)
        if speedd < 10:
            speedd += 0.2

    def move_left(self): # тоже не забыть сделать масштабирование
        global speeda
        a = speeda
        self.rect = self.rect.move(int(a), 0)
        if speeda < 10:
            speeda += 0.2

if __name__ == '__main__':
    pygame.init()
    SCREENRES = pygame.display.Info()
    screen = pygame.display.set_mode((SCREENRES.current_w, SCREENRES.current_h))
    size = SCREENRES.current_w, SCREENRES.current_h
    screen = pygame.display.set_mode(size)

    areas = pygame.sprite.Group()
    ar = Area(areas)

    heroes = pygame.sprite.Group()  # отрисовка героя
    hero = pygame.sprite.Sprite(heroes)
    hero_image = load_image(r"gamedata\img\hero.png").convert_alpha()
    hero.image = hero_image
    hero.rect = hero.image.get_rect()
    hero.rect.x = SCREENRES.current_w // 2 - hero.rect[2] // 2 # чтоб он в центре спавнился
    hero.rect.y = SCREENRES.current_h // 2 - hero.rect[3] // 2  # не забыть сделать увеличение/уменьшение размеров героя

    fps = 60
    clock = pygame.time.Clock()

    running = True
    speedw = 0.6
    speeda = 0.6
    speeds = 0.6
    speedd = 0.6
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                print('ага')
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


        areas.draw(screen)
        heroes.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
