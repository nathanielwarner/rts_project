import pygame


class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("car.png")

        self.rect = img.get_rect()
        self.image = img

        self.rect.x = 735
        self.rect.y = 180

        self.image = pygame.transform.rotate(self.image, 90)


class Window(object):
    def __init__(self):
        self._display = pygame.display.set_mode((900, 675), pygame.HWSURFACE)
        self._background = pygame.image.load("background.jpg").convert()
        self._car = Car()
        self._sprites = pygame.sprite.Group()
        self._sprites.add(self._car)
        self._should_exit = False

    def loop(self):
        self._display.blit(self._background, (0, 0))
        self._car.update()
        self._sprites.draw(self._display)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._should_exit = True

    def execute(self):
        while not self._should_exit:
            for event in pygame.event.get():
                self.handle_event(event)
            self.loop()
        self.cleanup()


def main():
    window = Window()
    window.execute()


if __name__ == "__main__":
    main()