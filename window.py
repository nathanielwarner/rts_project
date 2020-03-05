import pygame


routes = [
    [
        (735, 150),
        90,
        (535, 150),
        90,
        (535, 355),
        -90,
        (0, 355)
    ],
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
    ],
    [
        (735, 150),
        90,
        (535, 150),
        90,
        (535, 425)
    ]
]


class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("car.png")

        self.rect = img.get_rect()
        self.image = img

        self.store_x = 735.0
        self.store_y = 180.0

        self.x = self.store_x
        self.y = self.store_y

        self.rect.x = self.x
        self.rect.y = self.y

        self.target_x = None
        self.target_y = None
        self.rotate_on_target = None

        self.target_reached = False

        self.speed = 0.2
        self._last_time = pygame.time.get_ticks()

        self.image = pygame.transform.rotate(self.image, 90)

    def _rotate_and_complete(self):
        self.image = pygame.transform.rotate(self.image, self.rotate_on_target)
        self.target_reached = True
        self.x = self.target_x
        self.y = self.target_y

    def update(self, *args):
        current_time = pygame.time.get_ticks()
        adjusted_speed = self.speed * (current_time - self._last_time)
        self._last_time = current_time
        if not self.target_reached:
            if self.x > self.target_x:
                self.x -= adjusted_speed
                if self.x <= self.target_x:
                    self._rotate_and_complete()
            elif self.x < self.target_x:
                self.x += adjusted_speed
                if self.x >= self.target_x:
                    self._rotate_and_complete()
            elif self.y > self.target_y:
                self.y -= adjusted_speed
                if self.y <= self.target_y:
                    self._rotate_and_complete()
            elif self.y < self.target_y:
                self.y += adjusted_speed
                if self.y >= self.target_y:
                    self._rotate_and_complete()
        self.rect.x = self.x
        self.rect.y = self.y


class Window(object):
    def __init__(self):
        pygame.init()
        self._display = pygame.display.set_mode((900, 675), pygame.HWSURFACE)
        self._background = pygame.image.load("background.jpg").convert()
        self._car = Car()
        self._car.target_x = routes[0][0][0]
        self._car.target_y = routes[0][0][1]
        self._car.rotate_on_target = routes[0][1]
        self._sprites = pygame.sprite.Group()
        self._sprites.add(self._car)
        self._current_customer = 0
        self._progress = 0
        self._going_back = False
        self._should_exit = False

    def _update_car(self):
        if self._current_customer < len(routes):
            if self._car.target_reached:
                self._car.target_reached = False
                if self._going_back:
                    self._progress -= 2
                    if self._progress < 0:
                        self._car.target_x = self._car.store_x
                        self._car.target_y = self._car.store_y
                        self._car.rotate_on_target = 180
                        self._going_back = False
                        self._current_customer += 1
                    else:
                        self._car.target_x = routes[self._current_customer][self._progress][0]
                        self._car.target_y = routes[self._current_customer][self._progress][1]
                        self._car.rotate_on_target = - routes[self._current_customer][self._progress + 1]
                else:
                    self._progress += 2
                    if self._progress >= len(routes[self._current_customer]):
                        self._progress -= 4
                        self._going_back = True
                        self._car.target_x = routes[self._current_customer][self._progress][0]
                        self._car.target_y = routes[self._current_customer][self._progress][1]
                        self._car.rotate_on_target = - routes[self._current_customer][self._progress + 1]
                    else:
                        self._car.target_x = routes[self._current_customer][self._progress][0]
                        self._car.target_y = routes[self._current_customer][self._progress][1]
                        if self._progress + 1 < len(routes[self._current_customer]):
                            self._car.rotate_on_target = routes[self._current_customer][self._progress + 1]
                        else:
                            self._car.rotate_on_target = 180

    def loop(self):
        self._update_car()
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