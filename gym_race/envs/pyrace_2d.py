import pygame
import math

from pygame.constants import FULLSCREEN

screen_width = 1920
screen_height = 1080
# check_point = ((1200, 660), (1250, 120), (190, 200), (1030, 270), (250, 475), (850, 910))
check_point1 = ((1276,943), (1609,825), (1711,453), (1590,243), (925,118), (345,217), (209,500), (295,741),(760, 935)) # map 1
check_point2 = ((1223, 825),(1461,995),(1591, 497),(1155,445),(1205,215),(273,95),(310,430),(695,480),(365,740),(760, 935)) # map 2
check_point4 = ((1540,730),(885,715),(920,600),(1690,615),(1760,890),(1720,90),(1540,415),(1385,125),(1200,415),(995,111),(840,350),(270,125),(480,340),(300,540),(730,533),(310,745),(360,915),(653,885),(760, 935)) # map4
check_point3 = ((1703,890), (1707, 150), (1370,430), (1110, 567), (1577, 785), (901,777), (697,109), (285,760), (103,129), (145,780), (673, 373), (617,911),(760, 935)) # map 3
# chk_idx = 0
CAR_SIZE_X = 40
CAR_SIZE_Y = 40
MAP = 'map'

check_point = ()

if MAP == 'map':
    check_point = check_point1
elif MAP == 'map2':
    check_point = check_point2
elif MAP == 'map3':
    check_point = check_point3
elif MAP == 'map4':
    check_point = check_point4

class Car:
    def __init__(self, car_file, map_file, pos):
        self.surface = pygame.image.load(car_file)
        self.map = pygame.image.load(map_file)
        self.surface = pygame.transform.scale(self.surface, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotate_surface = self.surface
        self.pos = pos
        self.angle = 0
        self.speed = 0
        self.speedInit = False
        self.center = [self.pos[0] + CAR_SIZE_X /2, self.pos[1] + CAR_SIZE_Y / 2]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.current_check = 0
        self.visited = []
        self.prev_distance = 0
        self.cur_distance = 0
        self.goal = False
        self.check_flag = False
        self.distance = 0
        self.time_spent = 0
        self.l_goal = False


    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    def draw_collision(self, screen):
        for i in range(4):
            x = int(self.four_points[i][0])
            y = int(self.four_points[i][1])
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)

    def draw_radar(self, screen):
        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def check_collision(self):
        self.is_alive = True
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])


    def check_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == (255, 255, 255, 255) and len < 2000:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars_for_draw.append([(x, y), dist])

    def check_checkpoint(self):
        p = check_point[self.current_check]
        self.prev_distance = self.cur_distance
        dist = get_distance(p, self.center)
        if dist < 70:
            self.current_check += 1
            self.prev_distance = 9999
            self.check_flag = True
            if self.current_check >= len(check_point):
                self.current_check = 0
                self.visited = []
                self.l_goal = True
            self.goal = True
            
        self.cur_distance = dist

    def update(self):
        #check speed
        self.speed -= 0.5
        if self.speed > 10:
            self.speed = 10
        if self.speed < 1:
            self.speed = 1

        #check position
        self.rotate_surface = rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + CAR_SIZE_X/2, int(self.pos[1]) + CAR_SIZE_Y/2]
        len =  0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

class PyRace2D:
    def __init__(self, is_render = True):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.car = Car('car.png', MAP +'.png', [830, 920])
        self.game_speed = 60
        self.is_render = is_render
        self.mode = 0
        

    def action(self, action):
        if action == 0:
            self.car.speed += 2
        if action == 1:
            self.car.angle += 15
        elif action == 2:
            self.car.angle -= 15
        elif action == 3:
            if self.car.speed -2 >= 10:
                self.car.speed -= 2

        self.car.update()
        self.car.check_collision()
        self.car.check_checkpoint()

        self.car.radars.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar(d)

    def evaluate(self, reward):
        if not self.car.is_alive:
            reward += -1000 + self.car.distance//10
        elif self.car.goal:
            if self.car.l_goal:
                reward += 50
            else:
                if self.car.current_check not in self.car.visited:
                    reward += self.car.distance//10
                    self.car.visited.append(self.car.current_check)
                else:
                    self.car.goal = False
        return reward, self.car.distance

    def is_done(self):
        if not self.car.is_alive:
            self.car.current_check = 0
            self.car.distance = 0
            return True
        return False

    def observe(self):
        # return state
        radars = self.car.radars
        ret = [0, 0, 0, 0, 0]
        i = 0
        for r in radars:
            ret[i] = int(r[1] / 20)
            i += 1

        return ret

    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.mode += 1
                    self.mode = self.mode % 3

        self.screen.blit(self.car.map, (0, 0))


        if self.mode == 1:
            self.screen.fill((0, 0, 0))

        self.car.radars_for_draw.clear()
        for d in range(-90, 105, 15):
            self.car.check_radar_for_draw(d)
        pygame.draw.circle(self.screen, (255, 255, 0), check_point[self.car.current_check], 50, 1)
        self.car.draw_collision(self.screen)
        self.car.draw_radar(self.screen)
        self.car.draw(self.screen)



        pygame.display.flip()
        self.clock.tick(self.game_speed)


def get_distance(p1, p2):
	return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
