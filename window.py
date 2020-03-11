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


def route_length(route):
    length = abs(route[0][0] - 735.0) + abs(route[0][1] - 180.0) + 12
    for i in range(0, len(route) - 2, 2):
        length += abs(route[i + 2][0] - route[i][0]) + abs(route[i + 2][1] - route[i][1]) + 12
    return 2 * length


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

        self.target_reached = True

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
        adjusted_speed = self.speed * (current_time - self._last_time) * time_multiplier
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


time_multiplier = 0.0002


class Window(object):
    def __init__(self):
        pygame.init()
        self._display = pygame.display.set_mode((900, 675), pygame.HWSURFACE)
        self._background = pygame.image.load("background.jpg").convert()
        self._car = Car()
        self._car.target_x = 735.0
        self._car.target_y = 180.0
        self._car.rotate_on_target = 0.0
        self._sprites = pygame.sprite.Group()
        self._sprites.add(self._car)
        self._orders = pygame.sprite.Group()
        self._last_order = None
        self._current_customer = -1
        self._finished_jobs = []
        self._progress = 0
        self._going_back = False
        self._should_exit = False
        self.font = pygame.font.Font('freesansbold.ttf', 32)

    def _update_car(self):
        if self._current_customer != -1:
            if self._car.target_reached and not self._finished_current_job:
                self._car.target_reached = False
                if self._going_back:
                    self._progress -= 2
                    if self._progress < 0:
                        self._car.target_x = self._car.store_x
                        self._car.target_y = self._car.store_y
                        self._car.rotate_on_target = 180
                        self._going_back = False
                        self._finished_jobs.append(self._current_customer)
                        self._finished_current_job = True
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
                        self._orders.remove(self._last_order)
                    else:
                        self._car.target_x = routes[self._current_customer][self._progress][0]
                        self._car.target_y = routes[self._current_customer][self._progress][1]
                        if self._progress + 1 < len(routes[self._current_customer]):
                            self._car.rotate_on_target = routes[self._current_customer][self._progress + 1]
                        else:
                            self._car.rotate_on_target = 180

    def loop(self):
        current_time = pygame.time.get_ticks()
        self.clock += (current_time - self.last_time) * time_multiplier
        for interval in self.schedule.intervals:
            if interval.taskId != 0 and self.schedule.taskSet.tasks[interval.taskId].offset <= self.clock \
                    and interval.taskId - 1 != self._current_customer\
                    and interval.taskId - 1 not in self._finished_jobs:
                i_want_pizza = pygame.sprite.Sprite()
                img = pygame.image.load("thought_bubble.png")
                i_want_pizza.rect = img.get_rect()
                i_want_pizza.rect.x = routes[interval.taskId - 1][-1][0]
                i_want_pizza.rect.y = routes[interval.taskId - 1][-1][1]
                i_want_pizza.image = img
                self._last_order = i_want_pizza
                self._orders.add(i_want_pizza)
            if interval.startTime < self.clock < interval.endTime and interval.taskId - 1 != self._current_customer\
                    and interval.taskId - 1 not in self._finished_jobs and interval.taskId != 0:
                self._current_customer = interval.taskId - 1
                self._progress = 0
                self._car.x = 735.0
                self._car.y = 180.0
                self._car.rect.x = 735.0
                self._car.rect.y = 180.0
                self._car.target_x = routes[self._current_customer][0][0]
                self._car.target_y = routes[self._current_customer][0][1]
                self._car.rotate_on_target = routes[self._current_customer][1]
                self._car.target_reached = False
                self._car.speed = route_length(routes[self._current_customer]) / self.schedule.taskSet.tasks[interval.taskId].wcet
                self._finished_current_job = False
        self.last_time = current_time
        self._update_car()
        self._display.blit(self._background, (0, 0))
        self._car.update()
        self._sprites.draw(self._display)
        self._orders.draw(self._display)
        text = self.font.render("%s" % self.clock, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.x = 10
        text_rect.y = 10
        self._display.blit(text, text_rect)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._should_exit = True

    def execute(self, schedule):
        self.schedule = schedule
        self.clock = 0
        self.last_time = pygame.time.get_ticks()
        while not self._should_exit:
            for event in pygame.event.get():
                self.handle_event(event)
            self.loop()
        self.cleanup()
