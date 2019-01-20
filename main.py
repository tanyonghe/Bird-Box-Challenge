from itertools import cycle
import math
import os
import random
import socket
from struct import *
import sys

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *


class DevNull:
    def write(self, msg):
        pass

#sys.stderr = DevNull()  # to squash errors for the time being


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (159, 163, 168)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BG_COLOR = (181, 230, 29)
CAR_COLOR = (181, 230, 29)
TEXT_COLOR = (250, 105, 10)	

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


# Set the width and height of the screen [width, height]
size = (950, 600)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Birdbox Challenge")


# Define images
IMAGES = {}
IMAGES['background'] = pygame.image.load('assets/sprites/background.png').convert_alpha()
IMAGES['title'] = pygame.image.load('assets/sprites/title.png').convert_alpha()
IMAGES['birdbox'] = pygame.image.load('assets/sprites/birdbox.png').convert_alpha()
IMAGES['birdbox_small'] = pygame.image.load('assets/sprites/birdbox_small.png').convert_alpha()
IMAGES['birdbox_blinded'] = pygame.image.load('assets/sprites/birdbox_blinded.png').convert_alpha()
IMAGES['birdbox_blinded_medium'] = pygame.image.load('assets/sprites/birdbox_blinded_medium.png').convert_alpha()
IMAGES['team_name'] = pygame.image.load('assets/sprites/team_name.png').convert_alpha()
IMAGES['score'] = pygame.image.load('assets/sprites/score.png').convert_alpha()
IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )


class Car:
    def __init__(self, x=0, y=0, dx=4, dy=0, width=30, height=30, color=RED):
        self.image = ""
        self.x = x
        self.y = y
        self. dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.color = color

    def load_image(self, img):
        self.image = pygame.image.load(img).convert()
        self.image.set_colorkey(BLACK)

    def draw_image(self):
        screen.blit(self.image, [self.x, self.y])

    def move_x(self):
        self.x += self.dx

    def move_y(self):
        self.y += self.dy

    def draw_rect(self):
        pygame.draw.rect(screen, self.color, [self.x, self.y, self.width, self.height], 0)
		
    def draw_birdbox(self):
        screen.blit(IMAGES['birdbox_small'], (self.x, self.y))

    def check_out_of_screen(self):
        if self.x+self.width > 690 or self.x < 270:
            self.x -= self.dx


def check_collision(player_x, player_y, player_width, player_height, car_x, car_y, car_width, car_height):
    if (player_x+player_width > car_x) and (player_x < car_x+car_width) and (player_y < car_y+car_height) and (player_y+player_height > car_y):
        return True
    else:
        return False
		

def showScore(score):
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (800 - totalWidth) / 2

    screen.blit(IMAGES['score'], (Xoffset - 170, 600 * 0.6))
	
    for digit in scoreDigits:
        screen.blit(IMAGES['numbers'][digit], (Xoffset, 600 * 0.6))
        Xoffset += IMAGES['numbers'][digit].get_width()
	
	
		
def retrieve_UDP_values():
    UDP_IP = socket.gethostbyname(socket.gethostname())
    UDP_IP = "192.168.43.3"
    #UDP_IP = "192.168.13.1"
    UDP_PORT = 5001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(.02)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        data, addr = sock.recvfrom(1024)
        azimuth = "%1.4f" %unpack_from ('!f', data, 36)
        azimuth = int(float(azimuth))
        """
        Left = 1
        Right = 2
        Up = 3
        Down = 4
        Neutral = 0
        """
        return azimuth
        #if azimuth < 177 and azimuth > -80:
            #print("L")
            #return 1
        #elif azimuth > -166 and azimuth < 100:
            #print("R")
            #return 2
        #return 0
			
    except socket.timeout:
        return 400
		

def locate_direction(curr_azimuth, base_azimuth):
    """ Neutral = 0; Left = 1; Right = 2; Up = 3; Down = 4;"""
    diff_azimuth = curr_azimuth - base_azimuth
    if diff_azimuth > 17:
        if diff_azimuth < 160:
            return 2
        else:
            return 1
    elif diff_azimuth < -17:
        if diff_azimuth > -160:
            return 1
        else:
            return 2
    return 0
	

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Create a player car object
player = Car(175, 475, 0, 0, 70, 131, RED)
player.load_image("assets/sprites/player.png")

collision = True

# Store the score
score = 0

# Store base azimuth
base_azimuth = 400

# Store counter for birdbox surprise
birdbox_surprise = 0

# Load the fonts
font_40 = pygame.font.SysFont("Bold", 40, True, False)


def draw_main_menu():
    screen.blit(IMAGES['background'], (0, 0))
    screen.blit(IMAGES['title'], (110, 100))
    screen.blit(IMAGES['birdbox'], (500, 220))
    screen.blit(IMAGES['team_name'], (70, 550))	
    showScore(score)
    pygame.display.update()
    pygame.display.flip()


# Setup the enemy cars
cars = []
car_count = 2
for i in range(car_count):
    x = random.randrange(300, 600)
    car = Car(x, random.randrange(-150, -50), 0, random.randint(5, 10), 60, 60, CAR_COLOR)
    cars.append(car)


# Setup the stripes.
stripes = []
stripe_count = 20
stripe_x = 185
stripe_y = -10
stripe_width = 20
stripe_height = 80
space = 20
for i in range(stripe_count):
    stripes.append([470, stripe_y])
    stripe_y += stripe_height + space

# -------- Main Program Loop -----------
while not done:
    birdbox_surprise = (birdbox_surprise + 0.1) % 50
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        # Reset everything when the user starts the game.
        if collision and (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN):
            collision = False
            while base_azimuth == 400:
                base_azimuth = retrieve_UDP_values()
            for i in range(car_count):
                cars[i].y = random.randrange(-150, -50)
                cars[i].x = random.randrange(290, 650)
            player.x = 445
            player.dx = 0
            score = 0
            birdbox_surprise = 0
            pygame.mouse.set_visible(False)

        if not collision:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.dx = 8
                elif event.key == pygame.K_LEFT:
                    player.dx = -8

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.dx = 0
                elif event.key == pygame.K_RIGHT:
                    player.dx = 0
					
    if not collision:
        curr_azimuth = retrieve_UDP_values()
        if curr_azimuth != 400:
            curr_direction = locate_direction(curr_azimuth, base_azimuth)
            if curr_direction == 2:
                player.dx = 8
            elif curr_direction == 1:
                player.dx = -8
            else:
                player.dx = 0
        else:
            player.dx = 0
		

    # --- Drawing code should go here
    if not collision:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, GRAY, [270, 0, 420, 1000])
        pygame.draw.rect(screen, BLACK, [280, 0, 400, 1000])

        # Draw the stripes
        for i in range(stripe_count):
            pygame.draw.rect(screen, YELLOW, [stripes[i][0], stripes[i][1], stripe_width, stripe_height])
        # Move the stripes
        for i in range(stripe_count):
            stripes[i][1] += 3
            if stripes[i][1] > size[1]:
                stripes[i][1] = -40 - stripe_height

        player.draw_image()
        player.move_x()
        player.check_out_of_screen()

        # Check if the enemy cars move out of the screen.
        for i in range(car_count):
            cars[i].draw_birdbox()
            cars[i].y += cars[i].dy
            if cars[i].y > size[1]:
                score += 10
                cars[i].y = random.randrange(-150, -50)
                cars[i].x = random.randrange(290, 600)
                cars[i].dy = random.randint(4, 9)

        if birdbox_surprise < 20:		
            screen.blit(pygame.transform.flip(IMAGES['birdbox_blinded'], True, False), (40 * birdbox_surprise, 200 - 200 * math.fabs(math.cos(birdbox_surprise))))
        elif birdbox_surprise > 28 and birdbox_surprise < 33:
            if math.floor(birdbox_surprise) % 2 == 1:
                screen.blit(pygame.transform.flip(IMAGES['birdbox_blinded_medium'], True, False), (320, 80))
            else:
                screen.blit(IMAGES['birdbox_blinded_medium'], (320, 80))

        pygame.display.update()
		
        # Check the collision of the player with the car
        for i in range(car_count):
            if check_collision(player.x, player.y, player.width, player.height, cars[i].x, cars[i].y, cars[i].width, cars[i].height):
                collision = True
                pygame.mouse.set_visible(True)
                break

        # Draw the score.
        txt_score = font_40.render("Score: "+str(score), True, WHITE)
        screen.blit(txt_score, [15, 15])

        pygame.display.flip()
    else:
        base_azimuth = 400
        draw_main_menu()

    # --- Limit to 60 frames per second
    clock.tick(30)

# Close the window and quit.
pygame.quit()
