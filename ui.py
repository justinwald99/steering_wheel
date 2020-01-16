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
<<<<<<< HEAD
=======
    
def makeGuage(surface, coordinates, label, min, max, ) {
    GUAGE_WIDTH = 40
    GUAGE_HEIGHT = 100
    outline = pygame.Rect(coordinates, (GUAGE_WIDTH, GUAGE_HEIGHT))
    pygame.draw.rect(surface, coordinates)
}
>>>>>>> 1cf6711506f11c1ba73ac1425256fb954ad07178
