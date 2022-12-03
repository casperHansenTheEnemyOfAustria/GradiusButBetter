#imports and constants
import pygame, sys, pickle
from pygame.locals import *
from random import *
from math import *

from pygame.time import Clock
from gamestates import Gamestate
import objects as obj


class Gradius_model():
    #Lists for global management
    __scores = [] #the text elements for the scoreboard
    __player_score = 0 #the current score the player has achieved 
    __player_HP = 1 
    __objects = [] #All active objects. Everything that gets updated each frame
    __keys = set([]) #a set for the input keys, stops duplicate entries
    __bullets = [] #active bullets
    __enemies = [] #active enemies
    __power_ups = [] #power-up hitboxes
    __gamestate = Gamestate.MENU #gamestate, defaults to the start menu
    __delta_time = 1 #default delta
    __frame_limit = Clock()
    __muted = False
    __stop = False
    __name = ''
    __player = None #the current player so that it is accessible globally 
    __active_boss = False
    __player_dead = False #stops the game as the player dies

    @classmethod
    def start_game(cls):
        """
        initiates the elements needed for the game to launch and then changes the gamestate into running
        also resets the elements for a clean run
        """

        cls.__player_dead = False
        cls.__active_boss = False
        cls.__player_score = 0
        cls.__stop = False
        cls.__objects = []
        cls.__keys = set([])
        cls.__bullets = []
        cls.__enemies = []

    @classmethod
    def load_scores(cls):
        """
        unpacks the scores from the pickle file, if no score has been saved it creates a new scoreboard and a new pickle file with that scoreboard
        """
        
        try:
            #checks if the save file is here
            with open('save.pickle', 'rb') as save:
                scores = pickle.load(save)

        except:
            #creates a save file in the case of no save file
            with open('save.pickle', 'wb') as file:

                #creates 10 of the scoreboard values 
                initial_scores = [{'name': 'ABC', 'score': '0'} for x in range(10)]

                pickle.dump(initial_scores, file)
                scores = initial_scores

        return scores


    @classmethod
    def if_highscore(cls):
        """
        checks if the score achieved is worth displaying or not
        """
    

        for i, entry in enumerate(cls.__scores):
            if cls.__player_score >= int(entry['score']):
                return True

        return False
    @classmethod
    def update_score(cls):
        """
        checks if the player scored higher than any of the current scores and then puts them on the scoreboard
        """
        
        for i, entry in enumerate(cls.__scores):
            #if current achieved score is larger than a stored score
            if cls.__player_score >= int(entry['score']):
                #insert the current score in front of the score as it is larger or equal
                cls.__scores.insert(i,{'name': name, 'score': cls.__player_score})
                cls.__scores.pop(len(cls.__scores)-1)
                name = ''
                return

    @classmethod
    def __save_scores(cls):
        """
        writes the current scores down into the pickle file
        """

        with open('save.pickle', 'wb') as file:
            #saves whatever is in the scores into the file
            pickle.dump(cls.__scores, file)

    @classmethod
    def stop_game(cls):
        """
        resets the game variables and objects
        """

        cls.__stop = True
        cls.__objects = []
        cls.__keys = set([])
        cls.__bullets = []
        cls.__enemies = []
        cls.__power_ups = []
        cls.__game_manager = None

        pass

    @classmethod
    def get_scores(cls) -> list:
        return cls.__scores
    
    @classmethod
    def get_player_score(cls) -> int:
        return cls.__player_score

    @classmethod
    def quit(cls):
        """
        shuts down the game and saves the scores
        """
        cls.__save_scores()
        pygame.quit
        sys.exit()




