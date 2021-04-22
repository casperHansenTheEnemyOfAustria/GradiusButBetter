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
buttons = []
images = []
labels = []
objects = []
keys = set([])
bullets = []
enemies = []
gamestate = Gamestate.MENU
deltaTime = 1
muted = False

#--------------------
#classes, functions, gameobjects and methods

def check_collision(hitbox1, hitbox2):
    return hitbox1.colliderect(hitbox2)


def change_gamestate(new_state):
    global gamestate
    pygame.display.set_caption(str(new_state))
    gamestate = new_state


def quit():
    pygame.quit
    sys.exit()


class MenuManager:
    def __init__(self, buttons, images, labels):
        self._buttons = buttons
        self._images = images
        self._labels = labels

    #player control
    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONUP:
                for button in self._buttons:
                    if button.is_clicked(event.pos):
                        button.click()
                continue

        for buttons in self._buttons:
            buttons.render()

        for image in self._images:
            image.render()
            
        for label in self._labels:
            label.render()


class GameManager:

    def __init__(self, objects):
        self._objects = objects
        self.last_time = pygame.time.get_ticks()


    #player control
    def update(self, events):
    
        for event in events:
            if event.type == KEYDOWN:
                keys.add(event.key)
                continue #SPEED, eller så har man elifs, troligtvist fortfarande snabbare
            if event.type == KEYUP and event.key in keys:
                keys.remove(event.key)
                continue

        for object in self._objects:
            object.update(events)
            
        global deltaTime
        deltaTime = (pygame.time.get_ticks() - self.last_time)
        self.last_time = pygame.time.get_ticks()


class GameObject:

    def __init__(self, position_x, position_y, screen, sprite):
        self.position = pygame.Vector2(position_x, position_y)
        self.velocity = pygame.Vector2(0, 0)
        self.state = 'alive'
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

    def destroy(self):
        objects.remove(self)


class Entity(GameObject):

    def __init__(self, position_x, position_y, maxHP, screen, sprite):

        super().__init__(position_x, position_y, screen, sprite)

        self._maxHP = maxHP
        self.hp = maxHP

        self.hits = 0

        self.last_time = 0


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
        if K_a in keys and self.position.x:
            self.velocity.x = -self.move_speed * 0.8 * deltaTime
        if K_d in keys and self.position.x:
            self.velocity.x = self.move_speed * 0.8 * deltaTime
        if not K_w in keys and not K_s in keys or K_w in keys and K_s in keys:
            self.velocity.y = 0
        if not K_a in keys and not K_d in keys or K_a in keys and K_d in keys:
            self.velocity.x = 0

        #shoot
        if K_SPACE in keys:
            self.bullet_manager.shoot(self.position.x, self.position.y , 1)

        if self.hp < 1:
            change_gamestate(Gamestate.MENU)
            stop_game()

        #render
        super().draw()

class Enemy(Entity):

    def __init__(self, position_x, position_y, maxHP, move_speed, screen, sprite, bullet_sprite, index):

        super().__init__(position_x, position_y, maxHP, screen, sprite)

        self.bullet_manager = BulletManager(screen, bullet_sprite)

        self.move_speed = move_speed

        self.cycle = choice([1, -1])

        self.shoot_speed = randint(500, 2000)

        self.last_shot = 0


    def update(self, events):
        super().update(events)

        #super().check_bullets()

        time = pygame.time.get_ticks()

        if self.position.x > SCREEN_WIDTH*0.8 and self.hp > 0:
            #spawn behaviour
            self.velocity.x = -1 * self.move_speed * deltaTime
            self.velocity.y = self.move_speed * self.cycle / 2 * deltaTime
        elif self.hp > 0:
            #live behaviour
            self.velocity.x = -0.4 * self.move_speed * deltaTime
            self.velocity.y = self.move_speed * self.cycle / 2 * deltaTime
        else:
            #die
            self.velocity = pygame.Vector2(0, 0)
            #Explosion
            if not muted:
                enemy_explode.play()
            
            enemies.remove(self)
            super().destroy()

        if self.position.y > SCREEN_HEIGHT * 0.8:
            self.cycle = -1

        if self.position.y < SCREEN_HEIGHT * 0.2:
            self.cycle = 1
        
        if time - self.last_shot > 500:
            self.bullet_manager.shoot(self.position.x, self.position.y + 55, -1)
            self.last_shot = time

        super().draw()


class EnemyManager:

    def __init__(self, start):

        if start == 'random':
            self.start = randint(1000, 20000)
        else:
            self.start = start

        self.last_time = 0


    def update(self, events):
        global enemies
        time = pygame.time.get_ticks()
        if time - self.last_time > self.start:
            enemies.append(Enemy(SCREEN_WIDTH, SCREEN_HEIGHT * randint(3, 7) / 10, randint(15, 150), randint(1, 4) / 10, screen, pygame.transform.scale(enemy_sprite, (100, 100)), pygame.transform.scale(bullet_sprite, (10, 5)), len(enemies)))
            objects.append(enemies[len(enemies)-1])
            self.last_time = time


class Bullet(GameObject):

    def __init__(self, position_x, position_y, direction, screen, sprite): #Add Damage Later
        super().__init__(position_x, position_y, screen, sprite)
        self.direction = direction

        self.last_time = 0


    def update(self, events):
        super().update(events)
        super().draw()
        global enemies
        time = pygame.time.get_ticks()
        self.velocity.x = self.direction * 3 * deltaTime
        if self.direction == 1:
            for enemy in enemies:
                if check_collision(self.hitbox, enemy.hitbox) > 0 :
                    if time - self.last_time > 500:
                        enemy.take_damage()
                        self.last_time = time

                    if self in bullets:
                        bullets.remove(self)
                        super().destroy()
        elif self.direction == -1:
            if check_collision(self.hitbox, objects[0].hitbox) != 0:
                objects[0].take_damage()
                self.last_time = time

                if self in bullets:
                    bullets.remove(self)
                    super().destroy()
        elif self.position.x >= SCREEN_WIDTH:
            bullets.remove(self)
            super().destroy()

class BulletManager:

    def __init__(self, screen, sprite):
        self.last_time = pygame.time.get_ticks()
        self.sprite = sprite
        self.screen = screen


    def shoot(self, origin_x, origin_y, direction):
        if direction == 1:
            if pygame.time.get_ticks() > self.last_time + 150:
                if not muted:    
                    player_shoot.play()
                    
                bullets.append(Bullet(origin_x, origin_y + 30, direction, self.screen, self.sprite))
                objects.append(bullets[len(bullets)-1])
                self.last_time = pygame.time.get_ticks()
        elif pygame.time.get_ticks() > self.last_time + 150:
            bullets.append(Bullet(origin_x, origin_y, direction, self.screen, self.sprite))
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

#enemy sprites
enemy_sprite = pygame.image.load('Sprites/Enemy.png').convert_alpha()
#objects.append(Enemy(SCREEN_WIDTH, SCREEN_HEIGHT * 0.3, 50, 0.1, screen, pygame.transform.scale(enemy_sprite, (100, 100)), pygame.transform.scale(bullet_sprite, (10, 5))))

#explosion stages
explosion_1 = pygame.image.load('Sprites/Exp1.png').convert_alpha()
explosion_2 = pygame.image.load('Sprites/Exp2.png').convert_alpha()
explosion_3 = pygame.image.load('Sprites/Exp3.png').convert_alpha()
explosion_4 = pygame.image.load('Sprites/Exp4.png').convert_alpha()
explosion_5 = pygame.image.load('Sprites/Exp5.png').convert_alpha()

#audio
player_shoot = pygame.mixer.Sound('audio/player_shoot.wav')
enemy_explode = pygame.mixer.Sound('audio/enemy_explosion.wav')
pygame.mixer.music.load('audio/Concert_Of_The_Aerogami.wav')
## menu assets
buttons.append(obj.Button(lambda:change_gamestate(Gamestate.RUNNING),(SCREEN_WIDTH//2)-80,250,screen, ' Start! ', 'impact', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))) # button to start the game
buttons.append(obj.Button(quit,(SCREEN_WIDTH//2)-80,400,screen, ' QUIT ', 'impact', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))) # button to shut down the game

images.append(obj.Image(100,100,screen,10,player_sprite)) # player sprite for the menu
images.append(obj.Image(400,160,screen,10,bullet_sprite)) # 1st bullet sprite for the menu
images.append(obj.Image(600,160,screen,10,bullet_sprite)) # 2nd bullet sprite for the menu
images.append(obj.Image(800,160,screen,10,bullet_sprite)) # 3rd bullet sprite for the menu
images.append(obj.Image(1000,160,screen,10,bullet_sprite)) # 4th bullet sprite for the menu

labels.append(obj.Text(200,50,screen,'The paper plane that could!', 'comicsansms',60,pygame.Color(255,255,255), pygame.Color(0,0,0)))
#game managers


def start_game():
    global game_manager
    global objects
    global keys
    global bullets
    global enemies
    
    objects = []
    keys = set([])
    bullets = []
    enemies = []
    pygame.mixer.music.stop()

    pygame.mixer.music.play(-1,0.0)


    objects.append(Player(600, 300, 50, 0.6, screen, pygame.transform.scale(player_sprite, (70, 35)), pygame.transform.scale(bullet_sprite, (10, 5))))
    
    objects.append(EnemyManager(3000))

    game_manager = GameManager(objects)

    pass

def stop_game():
    global objects
    global keys
    global bullets
    global enemies
    global game_manager
    
    objects = []
    keys = set([])
    bullets = []
    enemies = []
    game_manager = None
    pygame.mixer.music.stop()

    pass

menu_manager = MenuManager(buttons, images, labels)
game_manager = None


#Game Loop
while True:
    #fills the screen with black to clean it
    screen.fill((0, 0, 0))
    events = pygame.event.get()
    
    if gamestate == Gamestate.MENU:
        menu_manager.update(events)

    if gamestate == Gamestate.RUNNING:
        if game_manager:
            game_manager.update(events)
        else:
            start_game()

    #global events
    for event in events:

        #closes the game
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            quit()

        if event.type == KEYDOWN:
            if event.key == K_m:
                muted = not muted

            if event.key == K_r:
                start_game()


    pygame.display.update()