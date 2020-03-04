import pygame


routes = [
    [
        (735, 50),
        90,
        (500, 50)
    ],
    [
        (735, 50),
        90,
        (400, 50),
        90,
        (400, 150),
        -90,
        (250, 150)
    ]
]


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
        self._current_customer = 0
        self._progress = 0
        self._should_exit = False

    def loop(self):
        self._display.blit(self._background, (0, 0))
        if self._car.rect.y > routes[self._current_customer][self._progress][1]:
            self._car.rect.y -= 0.01
            if self._car.rect.y <= routes[self._current_customer][self._progress][1]:
                self._car.image = pygame.transform.rotate(self._car.image,
                                                          routes[self._current_customer][self._progress + 1])
                self._progress += 2
        elif self._car.rect.x > routes[self._current_customer][self._progress][0]:
            self._car.rect.x -= 0.01
            if self._car.rect.x <= routes[self._current_customer][self._progress][0]:
                self._car.image = pygame.transform.rotate(self._car.image,
                                                          routes[self._current_customer][self._progress + 1])
                self._progress += 2
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