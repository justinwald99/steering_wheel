import sys, pygame
pygame.init()

gearPos = "2"

screen = pygame.display.set_mode()
gearFont = pygame.font.Font('freesansbold.ttf', 128)

gearText = gearFont.render(gearPos, False, (255,255,255))
gearTextRect = gearText.get_rect()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    screen.fill((0,0,0))
    screen.blit(gearText, (screen.get_width() / 2, screen.get_height() / 2))
    pygame.display.flip()
