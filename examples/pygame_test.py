from time import sleep
import pygame


class Application:
    def __init__(self):
        pygame.init()
        self.display = pygame.display
        self.display.set_caption("Martin was here")
        self.screen = pygame.display.set_mode((1400, 800))
        self.screen.fill((84, 84, 84))
        self.display.update()

    def run(self):
        running = True
        while running is True:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case _:
                        ...
            sleep(0.02)
        pygame.quit()


if __name__ == "__main__":
    Application().run()
