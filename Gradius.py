#imports and constants
import pygame, sys
from pygame.locals import *
from random import *
from math import *
from gamestates import Gamestate
import objects as obj

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BASE_ATTACK = 5

#Lists for global management
objects = []
keys = [] 
bullets = []
gamestate = Gamestate.MENU
deltaTime = 1

#--------------------
#classes, gameobjects and methods

def change_gamestate(new_state):
    global gamestate
    pygame.display.set_caption(str(new_state))
    gamestate = new_state


def quit():
    pygame.quit
    sys.exit()


class MenuManager:
    def __init__(self, objects, images):
        self._buttons = buttons
        self._images = images

    #player control
    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONUP:
                for button in self._buttons:
                    print(button.is_clicked(event.pos))
                    if button.is_clicked(event.pos):
                        button.click()
                continue 
           
        for buttons in self._buttons:
            buttons.render()

        for image in self._images:
            image.render()


class GameManager:
    def __init__(self, objects):
        self._objects = objects
        self.last_time = pygame.time.get_ticks()

    #player control
    def update(self, events):
        for event in events:
            if event.type == KEYDOWN:
                keys.append(event.key)
                continue #SPEED, eller så har man elifs, troligtvist fortfarande snabbare
            if event.type == KEYUP:
                keys.remove(event.key)
                continue
                #continue
        for object in self._objects:
            object.update(events)
        global deltaTime
        deltaTime = (pygame.time.get_ticks() - self.last_time)
        self.last_time = pygame.time.get_ticks()
        

class GameObject:
    def __init__(self, position_x, position_y, screen, sprite):
        self.position = pygame.Vector2(position_x, position_y)
        self.velocity = pygame.Vector2(0, 0)
        
        self.sprite = sprite
        self.screen = screen

    @property
    def hitbox(self):
        hitbox = self.sprite.get_rect()
        hitbox.x = self.position.x
        hitbox.y = self.position.y
        return hitbox
    
    # Flyttar objektet
    def update(self, events):
        self.position += self.velocity

    def draw(self):
        self.screen.blit(self.sprite,self.position)


class Entity(GameObject):
    def __init__(self, position_x, position_y, maxHP, screen, sprite):

        super().__init__(position_x, position_y, screen, sprite)

        self._maxHP = maxHP

        self.hp = maxHP

    def take_damage(self):
        self.hp = max(0, self.hp - (randint(1, 10) + BASE_ATTACK))
    
    def heal(self):
        self.hp = min(self._maxHP, self.hp + randint(5, 10))
    

class Player(Entity):
    def __init__(self, position_x, position_y, maxHP, move_speed, screen, sprite, bullet_sprite):
        
        super().__init__(position_x, position_y, maxHP, screen, sprite)

        self.bullet_manager = BulletManager(screen, bullet_sprite)

        self.move_speed = move_speed

    def update(self, events):
        super().update(events)
        
        #movement
        if K_w in keys:
            self.velocity.y = -self.move_speed * deltaTime
        if K_s in keys:
            self.velocity.y = self.move_speed * deltaTime
        if K_a in keys:
            self.velocity.x = -self.move_speed * 0.8 * deltaTime
        if K_d in keys:
            self.velocity.x = self.move_speed * 0.8 * deltaTime
        if not K_w in keys and not K_s in keys:
            self.velocity.y = 0
        if not K_a in keys and not K_d in keys:
            self.velocity.x = 0

        #shoot
        if K_SPACE in keys:
            self.bullet_manager.shoot(self.position.x, self.position.y, 1)

        #render
        super().draw()

class Bullet(GameObject):
    def __init__(self, position_x, position_y, direction, screen, sprite): #Add Damage Later
        super().__init__(position_x, position_y, screen, sprite)
        self.direction = direction

    def update(self, events):
        super().update(events)
        super().draw()
        self.velocity.x = (self.direction > 0) * 3 * deltaTime
        if self.position.x >= SCREEN_WIDTH:
            objects.remove(self)
            bullets.remove(self)

class BulletManager:
    def __init__(self, screen, sprite):
        self.last_time = pygame.time.get_ticks()
        self.sprite = sprite
        self.screen = screen

    def shoot(self, origin_x, origin_y, direction):
        if pygame.time.get_ticks() > self.last_time + 150:
            bullets.append(Bullet(origin_x, origin_y + 5, direction, self.screen, self.sprite))
            objects.append(bullets[len(bullets)-1])
            self.last_time = pygame.time.get_ticks()
            
#--------------------
#gameloops and assembly

    
#Initializing
pygame.init()

#Screen options
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(str(gamestate))

## game assets
#sprite for the bullet
bullet_sprite = pygame.image.load('Sprites/Bullet.png').convert_alpha()

#player sprite and assembly
player_sprite = pygame.image.load('Sprites/Player.png').convert_alpha()
objects.append(Player(600, 300, 3, 0.6, screen, pygame.transform.scale(player_sprite, (70, 35)), pygame.transform.scale(bullet_sprite, (10, 5))))

#enemy sprites
enemy_sprite = pygame.image.load('Sprites/Enemy.png').convert_alpha()

#explosion stages
explosion_1 = pygame.image.load('Sprites/Exp1.png').convert_alpha()
explosion_2 = pygame.image.load('Sprites/Exp2.png').convert_alpha()
explosion_3 = pygame.image.load('Sprites/Exp3.png').convert_alpha()
explosion_4 = pygame.image.load('Sprites/Exp4.png').convert_alpha()
explosion_5 = pygame.image.load('Sprites/Exp5.png').convert_alpha()

## menu assets

start_game = obj.Button(lambda:change_gamestate(Gamestate.RUNNING),(SCREEN_WIDTH//2)-80,200,screen, 'Start!', 'comicsansms', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))
exit_game = obj.Button(quit,(SCREEN_WIDTH//2)-80,320,screen, 'QUIT', 'comicsansms', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))

player_menu_image = obj.Image(100,80,screen,10,player_sprite)
bullet_menu_image1 = obj.Image(400,100,screen,10,bullet_sprite)
bullet_menu_image2 = obj.Image(600,100,screen,10,bullet_sprite)
bullet_menu_image3 = obj.Image(800,100,screen,10,bullet_sprite)
bullet_menu_image4 = obj.Image(1000,100,screen,10,bullet_sprite)


buttons = [start_game,exit_game]
images = [player_menu_image,bullet_menu_image1,bullet_menu_image2,bullet_menu_image3,bullet_menu_image4]

#game manager
menu_manager = MenuManager(buttons,images)
game_manager = GameManager(objects)



#Game Loop
while True:
    #fills the screen with black to clean it
    screen.fill((0, 0, 0))
    events = pygame.event.get()

    if gamestate == Gamestate.MENU:
        menu_manager.update(events)
        pass

    if gamestate == Gamestate.RUNNING:
        game_manager.update(events)
        pass

    #global events
    for event in events:
        #closes the game
        if event.type == QUIT or event.type == pygame.K_ESCAPE:
            quit()
    
    pygame.display.update()