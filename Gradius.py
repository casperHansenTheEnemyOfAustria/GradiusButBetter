#imports and constants
import pygame, sys, pickle
from pygame.locals import *
from random import *
from math import *
from gamestates import Gamestate
import objects as obj

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BASE_ATTACK = 5

#Lists for global management
scores = []
player_score = 0
player_HP = 1
objects = []
keys = set([])
bullets = []
enemies = []
power_ups = []
gamestate = Gamestate.MENU
deltaTime = 1
muted = False
stop = False
name = ''
player = None
active_boss = False

#--------------------
#classes, functions, gameobjects and methods

def start_game():
    global player_score
    global game_manager
    global objects
    global keys
    global bullets
    global enemies
    global stop
    global player
    
    player_score = 0
    stop = False
    objects = []
    keys = set([])
    bullets = []
    enemies = []
    pygame.mixer.music.stop()

    if not muted:
        pygame.mixer.music.play(-1,0.0)

    player = Player(600, 300, 50, 0.6, bullet_sprite)

    objects.append(player)
    
    objects.append(EnemyManager(3000))

    game_manager = GameManager(objects)

    #objects.append(EnvironmentManager(60, 30))

    pass


def stop_game():
    """
    resets the game variables and objects
    """
    global objects
    global keys
    global bullets
    global enemies
    global power_ups
    global game_manager
    global stop

    stop = True
    objects = []
    keys = set([])
    bullets = []
    enemies = []
    power_ups = []
    game_manager = None
    pygame.mixer.music.stop()

    pass


def render_scores(da_screen, scores, positions):
    """
    creates an array of renderable text objects
    """
    score_render = []
    for index in range(10):
        score_render.append(obj.Text(positions[index][0], positions[index][1], da_screen, f'{index}. {scores[index]["name"]} - {scores[index]["score"]}', 'comicsansms', 40))

    return score_render


def update_score():
    """
    checks if the player scored higher than any of the current scores and then puts them on the scoreboard
    """
    global scores
    global player_score
    global name
    
    for i, entry in enumerate(scores):
        if player_score >= int(entry['score']):
            scores.insert(i,{'name': name, 'score': player_score})
            scores.pop(len(scores)-1)
            name = ''
            return
        

def load_scores():
    """
    unpacks the scores from the pickle file, if no score has been saved it creates a new scoreboard and a new pickle file
    """
    
    try:
        #checks if the save file is here
        with open('save.pickle', 'rb') as save:
            scores = pickle.load(save)

    except:
        #creates a save file in the case of no save file
        with open('save.pickle', 'wb') as file:

            initial_scores = [{'name': 'ABC', 'score': '0'} for x in range(10)]

            pickle.dump(initial_scores, file)
            scores = initial_scores

    return scores


def save_scores():
    """
    writes the current scores down into the pickle file
    """
    global scores

    with open('save.pickle', 'wb') as file:
        #saves whatever is in the scores into the file
        pickle.dump(scores, file)


def check_collision(hitbox1, hitbox2):
    return hitbox1.colliderect(hitbox2)


def change_gamestate(new_state):
    """
    changes the gamestate
    """
    global gamestate
    pygame.display.set_caption(str(new_state).split('.')[-1])
    gamestate = new_state


def quit():
    """
    shuts down the game and saves the scores
    """
    save_scores()
    pygame.quit
    sys.exit()


class MenuManager:
    """
    manage menu assets and assets, button functions and rendering 
    """
    def __init__(self, buttons, images, labels):
        self._buttons = buttons
        self._images = images
        self.labels = labels

    #player control
    def update(self, events):
        for event in events:
            #checks if the ODD
            if event.type == MOUSEBUTTONUP:
                for button in self._buttons:
                    if button.is_clicked(event.pos):
                        button.click()
                continue

        for buttons in self._buttons:
            buttons.render()

        for image in self._images:
            image.render()
            
        for label in self.labels:
            if gamestate == Gamestate.SCOREBOARD:
                #add position to the text
                label.render()

                pass
            else:
                label.render()


class GameManager:
    """
    manages game assets such as the player and the enemies 
    """
    def __init__(self, objects):
        global stop

        self._objects = objects
        self._last_time = pygame.time.get_ticks()


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
            if stop:
                return True
            
        global deltaTime
        deltaTime = (pygame.time.get_ticks() - self._last_time)
        self._last_time = pygame.time.get_ticks()


class GameObject:
    
    def __init__(self, position_x, position_y, sprite):
        self.position = pygame.Vector2(position_x, position_y)
        self.velocity = pygame.Vector2(0, 0)
        self.sprite = sprite
        #self.screen = screen
        self.do_draw = True


    @property
    def hitbox(self):
        hitbox = self.sprite.get_rect()
        hitbox.x = self.position.x
        hitbox.y = self.position.y
        return hitbox

    def set_sprite(self, new_sprite):
        self.sprite = new_sprite

    # Flyttar objektet
    def update(self, events):
        self.position += self.velocity

    def draw(self):
        global screen
        screen.blit(self.sprite,self.position)

    def destroy(self):
        objects.remove(self)


class Entity(GameObject):

    def __init__(self, position_x, position_y, maxHP, sprite):

        super().__init__(position_x, position_y, sprite)

        self._maxHP = maxHP
        self._hp = maxHP

        self.hits = 0

        self._last_time = 0

        self.last_damage = 0


    def take_damage(self, damage):
        self._hp = max(0, self._hp - (randint(1, 10) + BASE_ATTACK) * damage)
        self.last_damage = pygame.time.get_ticks()
        self.do_draw = False


    def heal(self):
        self._hp = min(self._maxHP, self._hp + randint(5, 10))


class Player(Entity):

    def __init__(self, position_x, position_y, maxHP, move_speed, bullet_sprite):

        super().__init__(position_x, position_y, maxHP, pygame.transform.scale(player_sprite, (70, 35)))

        self._bullet_manager = BulletManager(bullet_sprite)

        self.move_speed = move_speed

        self._last_time = 0

        self._start_shooting_time = None

        self.power = 1

        self._shooting = False


    def update(self, events):
        super().update(events)

        self._shooting = False

        global player_HP
        player_HP = self._hp/50

        time = pygame.time.get_ticks()

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
        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                self._start_shooting_time = time
                self._bullet_manager.tap_shoot(self.position.x, self.position.y, self.power)
                self._shooting = True
            if event.type == KEYUP:
                if event.key == K_SPACE and self._start_shooting_time:
                    if time - self._start_shooting_time > 1000:
                        self._bullet_manager.big_shoot(self.position.x, self.position.y, self.power)
                        self._shooting = True
                    self._start_shooting_time = None

        if K_SPACE in keys and not self._shooting:
            self._bullet_manager.shoot(self.position.x, self.position.y, 1, self.power)
            self._shooting = True


        if self._start_shooting_time != None and time - self._start_shooting_time > 1000:
            self.sprite = pygame.transform.scale(red_player_sprite, (70, 35))
        else:
            self.sprite = pygame.transform.scale(player_sprite, (70, 35))


        for enemy in enemies:
            if check_collision(self.hitbox, enemy.hitbox) > 0:
                if time - self._last_time > 500:
                    self.take_damage(1)
                    self._last_time = time
        
        for power in power_ups:
            if check_collision(self.hitbox, power.hitbox) > 0:
                if power.type == "Speed":
                    self.move_speed += 0.1
                if power.type == "Power":
                    self.power += 0.2
                player_power.play()
                power.destroy()
                power_ups.remove(power)
                self.heal()
        #player die
        if self._hp < 1:
            change_gamestate(Gamestate.GAME_OVER)            
            stop_game()
            return True

        #render
        if self.do_draw:
            super().draw()
        elif time - self.last_damage > 50:
            self.do_draw = True

class Enemy(Entity):

    def __init__(self, position_x, position_y, maxHP, move_speed, sprite, bullet_sprite, points):

        super().__init__(position_x, position_y, maxHP, sprite)

        self._bullet_manager = BulletManager(bullet_sprite)

        self._move_speed = move_speed

        self._cycle = choice([1, -1])

        self.points = points

        self._last_shot = 0

        self._death_time = None

        self._time = 0

        self._exp = [explosion_1, explosion_2, explosion_3, explosion_4, explosion_5]


    def update(self, events):
        super().update(events)

        #super().check_bullets()

        self._time = pygame.time.get_ticks()

        if self.position.x > SCREEN_WIDTH*0.8 and self._hp > 0:
            #spawn behaviour
            self.velocity.x = -1 * self._move_speed * deltaTime
            self.velocity.y = self._move_speed * self._cycle / 2 * deltaTime
        elif self._hp > 0:
            #live behaviour
            self.velocity.x = -0.4 * self._move_speed * deltaTime
            self.velocity.y = self._move_speed * self._cycle / 2 * deltaTime
        else:
            #die
            self.velocity = pygame.Vector2(0, 0)
            #Explosion
            global player_score
            player_score += self.points
            if self._death_time == None:
                self._death_time = self._time
                if not muted:
                    enemy_explode.play()
                enemies.remove(self)
            self.die()

        if self.position.y > SCREEN_HEIGHT * 0.8:
            self._cycle = -1

        if self.position.y < SCREEN_HEIGHT * 0.2:
            self._cycle = 1

        if self.position.x < -100:
            enemies.remove(self)
            self.destroy()
        
        if self._time - self._last_shot > 800:
            self._bullet_manager.shoot(self.position.x, self.position.y + 55, -0.5, 1)
            self._last_shot =self._time

        if self.do_draw:
            super().draw()
        elif self._time - self.last_damage > 50:
            self.do_draw = True

    def die(self):
        stage = min((self._time - self._death_time) // 100, 4)
        if self._time - self._death_time < 600:
            self.sprite = self._exp[stage]
        else:
            if randint(1, 100) > 85:
                temp = PowerUp(self.position.x, self.position.y)
                objects.append(temp)
                power_ups.append(temp)
            super().destroy()

class Boss(Entity):
    def __init__(self, position_x, position_y, maxHP, move_speed, sprite, bullet_sprite, points):
        super().__init__(position_x, position_y, maxHP, sprite)

        self._move_speed = move_speed

        self.bullet_sprite = bullet_sprite

        self.points = points

        self._bullet_manager = BulletManager(bullet_sprite)

        self._last_shot = 0

        self._death_time = None

        self._time = 0

        self._exp = [explosion_1, explosion_2, explosion_3, explosion_4, explosion_5]

    def update(self, events):
        super().update(events)

        self._time = pygame.time.get_ticks()

        if self.position.x > SCREEN_WIDTH*0.8 and self._hp > 0:
            #spawn behaviour
            self.velocity.x = -1 * self._move_speed * deltaTime
            self.velocity.y = self._move_speed * deltaTime
        elif self._hp > 0:
            #live behaviour
            self.velocity.x = 0
            self.velocity.y = self._move_speed * (player.position.y - 40 - self.position.y) / 150 * deltaTime
        else:
            #die
            self.velocity = pygame.Vector2(0, 0)
            #Explosion
            global player_score
            player_score += self.points
            if self._death_time == None:
                self._death_time = self._time
                if not muted:
                    enemy_explode.play()
                enemies.remove(self)
            self.die()
        
        if self._time - self._last_shot > 800:
            self._bullet_manager.shoot(self.position.x, self.position.y + 55, -0.5, 1)
            self._last_shot =self._time

        if self.do_draw:
            super().draw()
        elif self._time - self.last_damage > 50:
            self.do_draw = True
    
    def die(self):
        stage = min((self._time - self._death_time) // 100, 4)
        if self._time - self._death_time < 600:
            self.sprite = self._exp[stage]
        else:
            if randint(1, 100) > 85:
                temp = PowerUp(self.position.x, self.position.y)
                objects.append(temp)
                power_ups.append(temp)
            global active_boss
            active_boss = False
            super().destroy()



class EnemyManager:

    def __init__(self, start):

        if start == 'random':
            self._start = randint(1000, 20000)
        else:
            self._start = start

        self._last_time = 0

        self._count = 0


    def update(self, events):
        global enemies
        global active_boss
        time = pygame.time.get_ticks()
        if not active_boss:    
            if time - self._last_time > self._start:
                if self._count % 10 != 0 or self._count == 0:
                    new_enemy = Enemy(SCREEN_WIDTH, SCREEN_HEIGHT * randint(3, 7) / 10, randint(50, 200), randint(1, 4) / 10, pygame.transform.scale(enemy_sprite, (100, 100)), pygame.transform.scale(bullet_sprite, (10, 5)), 5)
                    enemies.append(new_enemy)
                    objects.append(new_enemy)
                    self._last_time = time
                    self._count += 1
                elif enemies == []:
                    new_enemy = Boss(SCREEN_WIDTH, SCREEN_HEIGHT * randint(3, 7) / 10, randint(400, 800), randint(1, 2) / 10, pygame.transform.scale(boss_sprite, (40 * 5, 40 * 5)), pygame.transform.scale(bullet_sprite, (10, 5)), 10)
                    enemies.append(new_enemy)
                    objects.append(new_enemy)
                    self._last_time = time
                    active_boss = True
                    self._count += 1


class Bullet(GameObject):

    def __init__(self, position_x, position_y, direction, sprite, damage): #Add Damage Later
        super().__init__(position_x, position_y, sprite)
        self._direction = direction
        self._damage = damage

        self._last_time = 0


    def update(self, events):
        super().update(events)
        super().draw()
        global enemies
        time = pygame.time.get_ticks()
        self.velocity.x = self._direction * 3 * deltaTime
        if self._direction == 1:
            for enemy in enemies:
                if check_collision(self.hitbox, enemy.hitbox) > 0 :
                    if time - self._last_time > 500:
                        enemy.take_damage(self._damage)
                        self._last_time = time

                    if self in bullets:
                        bullets.remove(self)
                        super().destroy()
        elif self._direction < 0:
            if check_collision(self.hitbox, player.hitbox) != 0:
                player.take_damage(1)
                self._last_time = time

                if self in bullets:
                    bullets.remove(self)
                    super().destroy()
        try:
            if self.position.x >= SCREEN_WIDTH:
                bullets.remove(self)
                super().destroy()
        except ValueError:
            pass
        if self.position.x < -100:
            bullets.remove(self)
            super().destroy()
        

class BulletManager:
    
    def __init__(self, sprite):
        self._last_time = pygame.time.get_ticks()
        self.sprite = sprite

    def shoot(self, origin_x, origin_y, direction, multiplier):
        time = pygame.time.get_ticks()
        if direction == 1:
            if time > self._last_time + 150:
                if not muted:    
                    player_shoot.play()

                sprite = pygame.transform.scale(self.sprite, (10, 5))
                damage = multiplier
                    
                temp = Bullet(origin_x + 60, origin_y + 30, direction, sprite, damage)

                bullets.append(temp)
                objects.append(temp)
                self._last_time = time
        elif time > self._last_time + 150:
            if not muted:
                player_shoot.play()
            new_bullet = Bullet(origin_x, origin_y, direction, self.sprite, 1)
            bullets.append(new_bullet)
            objects.append(new_bullet)
            self._last_time = time
    
    def tap_shoot(self, origin_x, origin_y, multiplier):
        time = pygame.time.get_ticks()
        if time > self._last_time + 150:
                if not muted:    
                    player_shoot.play()

                sprite = pygame.transform.scale(self.sprite, (20, 10))
                damage = 2 * multiplier
                    
                temp = Bullet(origin_x + 60, origin_y + 30, 1, sprite, damage)

                bullets.append(temp)
                objects.append(temp)
                self._last_time = time

    def big_shoot(self, origin_x, origin_y, multiplier):
        if not muted:    
            player_shoot.play()

        sprite = pygame.transform.scale(self.sprite, (50, 25))
        damage = 5 * multiplier
            
        temp = Bullet(origin_x, origin_y + 30, 1, sprite, damage)

        bullets.append(temp)
        objects.append(temp)


class PowerUp(GameObject):
    def __init__(self, origin_x, origin_y):
        self.type = choice(["Speed", "Power"])
        if self.type == "Power":
            super().__init__(origin_x, origin_y, pygame.transform.scale(power_up_sprite, (18 * 5, 9 * 5)))
        elif self.type == "Speed":
            super().__init__(origin_x, origin_y, pygame.transform.scale(speed_up_sprite, (18 * 5, 9 * 5)))
    
    def update(self, events):
        self.draw()

#--------------------
#gameloops and assembly

#Initializing
pygame.init()

#Screen options
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(str(gamestate).split('.')[-1])

## game assets
#sprite for the bullet
try:
    bullet_sprite = pygame.image.load('Sprites/Bullet.png').convert_alpha()

    #player sprite and assembly
    player_sprite = pygame.image.load('Sprites/Player.png').convert_alpha()
    red_player_sprite = pygame.image.load('Sprites/Red_Player.png').convert_alpha()

    power_up_sprite = pygame.image.load('Sprites/PowerUp.png').convert_alpha()
    speed_up_sprite = pygame.image.load('Sprites/SpeedUp.png').convert_alpha()

    #enemy sprites
    enemy_sprite = pygame.image.load('Sprites/Enemy.png').convert_alpha()
    boss_sprite = pygame.image.load('Sprites/Boss.png').convert_alpha()

    #explosion stages
    explosion_1 = pygame.transform.scale(pygame.image.load('Sprites/Exp1.png').convert_alpha(), (4 * 5, 3 * 5))
    explosion_2 = pygame.transform.scale(pygame.image.load('Sprites/Exp2.png').convert_alpha(), (6 * 5, 5 * 5))
    explosion_3 = pygame.transform.scale(pygame.image.load('Sprites/Exp3.png').convert_alpha(), (8 * 5, 7 * 5))
    explosion_4 = pygame.transform.scale(pygame.image.load('Sprites/Exp4.png').convert_alpha(), (20 * 5, 20 * 5))
    explosion_5 = pygame.transform.scale(pygame.image.load('Sprites/Exp5.png').convert_alpha(), (20 * 5, 20 * 5))

    #audio
    player_shoot = pygame.mixer.Sound('audio/player_shoot.wav')
    player_power = pygame.mixer.Sound('audio/power.wav')
    enemy_explode = pygame.mixer.Sound('audio/enemy_explosion.wav')
    pygame.mixer.music.load('audio/Concert_Of_The_Aerogami.wav')

except Exception as e:
    print('Not all assets could be loaded: ' + str(e) + ' at line ' + str(e.__traceback__.tb_lineno))


## menu assets
menu_buttons = []
menu_buttons.append(obj.Button(lambda:change_gamestate(Gamestate.RUNNING),(SCREEN_WIDTH//2)-100,250,screen, ' Start! ', 'impact', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))) # button to start the game
menu_buttons.append(obj.Button(quit,(SCREEN_WIDTH//2)-80,470,screen, ' QUIT ', 'impact', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))) # button to shut down the game
menu_buttons.append(obj.Button(lambda:change_gamestate(Gamestate.SCOREBOARD),(SCREEN_WIDTH//2)-100,360,screen, ' Score ', 'impact', 80, pygame.Color(255,255,255), pygame.Color(120,120,120))) # button to shut down the game
menu_images = []
menu_images.append(obj.Image(100, 100, screen, 10, player_sprite)) # player sprite for the menu
for x in range(4):
    menu_images.append(obj.Image(400+200*x, 160, screen, 10, bullet_sprite)) # 1st bullet sprite for the menu
menu_labels = []
menu_labels.append(obj.Text(200,50,screen,'The paper plane that could!', 'comicsansms',60,pygame.Color(255,255,255)))

##scoreboard assets
scoreboard_buttons = []
scoreboard_buttons.append(obj.Button(lambda:change_gamestate(Gamestate.MENU), 380, 500, screen, ' Menu ', 'impact', 80, pygame.Color(255,255,255),pygame.Color(120,120,120)))
scoreboard_buttons.append(obj.Button(lambda:change_gamestate(Gamestate.RUNNING), 680, 500, screen, ' Play ', 'impact', 80, pygame.Color(255,255,255),pygame.Color(120,120,120)))

scoreboard_images = []
#no images :(

scoreboard_label_positions = [(300,100), (300,150), (300,200), (300,250), (300,300), (650,100), (650,150), (650,200), (650,250), (650,300)]
scores = load_scores()
scoreboard_labels = render_scores(screen, scores, scoreboard_label_positions)

#managers
main_menu = MenuManager(menu_buttons, menu_images, menu_labels)
scoreboard_menu = MenuManager(scoreboard_buttons, scoreboard_images, scoreboard_labels)
game_manager = None


#Game Loop
while True:
    #fills the screen with black to clean it
    screen.fill((0, 0, 0))
    events = pygame.event.get()

    if gamestate == Gamestate.MENU:
        main_menu.update(events)

    elif gamestate == Gamestate.GAME_OVER:
        #display name on the screen
        obj.Text(500,300,screen,f'Name:{name}', 'impact', 50, pygame.Color(255,255,255)).render()
        obj.Text(400, 80, screen, f'FINAL SCORE:{player_score}', 'impact', 80, pygame.Color(255,255,255)).render()

    elif gamestate == Gamestate.SCOREBOARD:

        scoreboard_menu.labels = render_scores(screen, scores, scoreboard_label_positions)

        scoreboard_menu.update(events)
    
    elif gamestate == Gamestate.RUNNING:
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(25, 100, 100 * player_HP, 25))
        if game_manager:
            game_manager.update(events)
            obj.Text(20, 20, screen, f'Score:{player_score}', 'comicsansms', 30, pygame.Color(255,255,255)).render()

        else:
            start_game()


    #global events
    for event in events:

        #closes the game
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE and gamestate == Gamestate.MENU):
            quit()

        if event.type == KEYDOWN:

            if gamestate == Gamestate.MENU :
                #get into the game from the menu
                if event.key == pygame.K_RETURN:
                    change_gamestate(Gamestate.RUNNING)


            elif gamestate == Gamestate.RUNNING:

                if event.type == KEYDOWN:

                    #restart game when playing
                    if  event.key == K_r:
                        start_game()
                    
                    #quit game mid game
                    if event.key == K_ESCAPE:
                        stop_game()
                        change_gamestate(Gamestate.MENU)

                    elif event.key == K_m:
                        muted = not muted
                        if muted:
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.play(-1,0.0)


            elif gamestate == Gamestate.SCOREBOARD:
                #go to menu from scoreboard
                if event.key == pygame.K_ESCAPE:
                    change_gamestate(Gamestate.MENU)
                
                if event.key == pygame.K_RETURN:
                    change_gamestate(Gamestate.RUNNING)
            

            elif gamestate == Gamestate.GAME_OVER:
                #accept the name and go to scoreboard
                if event.key == pygame.K_RETURN and len(name) > 2:
                    change_gamestate(Gamestate.SCOREBOARD)
                    update_score()
                    
                #backspace function
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                    
                #add key to name
                elif len(name) < 6:
                    name += event.unicode
            

            
                    
                                
    pygame.display.update()