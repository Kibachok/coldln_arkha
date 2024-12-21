import pygame


def cla_mainmenu_draw(screen, xoffset=0, yoffset=0):
    doomerochek = pygame.image.load(r'doomkisser_V2_s.png').convert()
    doomerochek = pygame.transform.scale(doomerochek, (510, 510))
    screen.blit(doomerochek, (-xoffset, -yoffset))
    font = pygame.font.Font(None, 35)
    text = font.render("Cold Line :: Arkhangelsk (Dev-alpha)", False, '#CACAEF')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) // 2 - xoffset * 2, 50 - yoffset * 3))
    font = pygame.font.Font(None, 20)
    text = font.render("imagine good working main menu here", False, '#DDDDDD')
    screen.blit(text, (500 - text.get_width() - (500 - text.get_width()) // 2, 75))
    pygame.display.flip()


pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("ColdLine Arkhangelsk")
cla_mainmenu_draw(screen)
game_isactive = True
while game_isactive:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_isactive = False
        if event.type == pygame.MOUSEMOTION:
            cla_mainmenu_draw(screen, xoffset=event.pos[0] // 50, yoffset=event.pos[1] // 50)
