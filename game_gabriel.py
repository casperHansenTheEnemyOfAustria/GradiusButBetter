#constants and imports
import pygame
import random
import math
import sys
# import objects_gabriel as objg

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

#------------------------------
#objects and functions
def p_banana():
    print('banana')

def close_game():
    pygame.quit()
    sys.exit()
    


#------------------------------
#gameloop
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# title_card  = objg.Text(100,100,screen,'Hello there!', 'comicsansms', 60)
# bottom_text  = objg.Text(100,200,screen,'BEANING TIME!', 'comicsansms', 20)
# banana = objg.Button(p_banana,100,300,screen, 'banana', 'arial', 20, pygame.Color(255,255,0))

# texts = [title_card,bottom_text]
# buttons = [banana]


while True:

    events = pygame.event.get()
    
    #game events
    for event in events:
        print(event)
        if event.type == pygame.QUIT:
            close_game()

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     if button.is_clicked(event.pos):
        #         button.click()
        pass


    #rendering
    # for text in texts:
    #     text.render()
    # for button in buttons:
    #     button.render()

    pygame.display.update()