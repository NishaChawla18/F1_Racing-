import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()
pygame.font.init()
pygame.mixer.init()
from playsound import playsound
#playsound("C:\\Users\\hp\\Music\\ Ikk Kudi - Full Video _ Udta Punjab _ Shahid Mallya _ Alia Bhatt & Shahid Kapoor _ Amit Trivedi.mp3")
GRASS = scale_image(pygame.image.load("grass.jpeg"), 2.5)
TRACK = scale_image(pygame.image.load("track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_image(pygame.image.load("finish.png"),1)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130 , 330)

BLUE_BIKE = scale_image(pygame.image.load("1-1.png"), 0.5)
RED_BIKE = scale_image(pygame.image.load("2-2.png"), 0.5)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = [(175, 100), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

pygame.mixer.music.load('powerful-gym-rock-121485-[AudioTrimmer.com].mp3')
pygame.mixer.music.play(-1)
class GameInfo:
    LEVELS = 10
    # pygame.mixer.music.play(-1)
    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractBike:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.vel=3
        self.move()

    def move_backward(self):
        
        self.vel = max(self.vel - self.acceleration, self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal
        

    def collide(self, mask, x=0, y=0):
        bike_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(bike_mask, offset)
        print(poi)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerBike():
    IMG = BLUE_BIKE
    START_POS = (170, 280)
    
    
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = 4
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        
        self.vel = max(self.vel - self.acceleration, self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        
        print(radians/3.14,vertical,horizontal,self.vel)
        
        self.y -= math.cos(radians) * self.vel
        self.x -= math.sin(radians) * self.vel
        

    def collide(self, mask, x=0, y=0):
        bike_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(bike_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
    
    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class ComputerBike(AbstractBike):
    IMG = RED_BIKE
    START_POS = (150, 280)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


def draw(win, images, player_bike, computer_bike, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(
        f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(
        f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(
        f"Vel: {round(player_bike.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_bike.draw(win)
    computer_bike.draw(win)
    pygame.display.update()


def move_player(player_bike):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_bike.rotate(left=True)
    if keys[pygame.K_d]:
        player_bike.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_bike.move_forward()
        #player_car.move(5)
    if keys[pygame.K_s]:
        moved = True
        player_bike.move_backward()
        #player_car.move(-5)
'''
    if not moved:
        player_car.reduce_speed()'''


def handle_collision(player_bike, computer_bike, game_info):
    if player_bike.collide(TRACK_BORDER_MASK) != None:
        player_bike.bounce()

    computer_finish_poi_collide = computer_bike.collide(
        FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:

        blit_text_center(WIN, MAIN_FONT, "You lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_bike.reset()
        computer_bike.reset()

    player_finish_poi_collide = player_bike.collide(
        FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_bike.bounce()
        else:
            game_info.next_level()
            player_bike.reset()
            computer_bike.next_level(game_info.level)


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_bike = PlayerBike(4, 4)
computer_bike = ComputerBike(2, 4, PATH)
game_info = GameInfo()

#playsound("C:\\Users\\hp\\Music\\ Ikk Kudi - Full Video _ Udta Punjab _ Shahid Mallya _ Alia Bhatt & Shahid Kapoor _ Amit Trivedi.mp3")

while run:
    #playsound("C:\\Users\\hp\\Music\\ Ikk Kudi - Full Video _ Udta Punjab _ Shahid Mallya _ Alia Bhatt & Shahid Kapoor _ Amit Trivedi.mp3")
    # pygame.mixer.music.play(-1)
    clock.tick(FPS)

    draw(WIN, images, player_bike, computer_bike, game_info)
    #playsound("C:\\Users\\hp\\Music\\ Ikk Kudi - Full Video _ Udta Punjab _ Shahid Mallya _ Alia Bhatt & Shahid Kapoor _ Amit Trivedi.mp3")
    # bgm= pygame.mixer.music.load('bgm.mp3')
    # pygame.mixer.music.play(-1)
    while not game_info.started:
        blit_text_center(
            WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()
                pygame.mixer.music.play(-1)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_bike)
    computer_bike.move()

    handle_collision(player_bike, computer_bike, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        player_bike.reset()
        computer_bike.reset()


pygame.quit()
