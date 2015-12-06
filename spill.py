# -*- coding: utf-8 -*-
"""
Created on Fri Dec 04 20:31:49 2015

@author: Benjamin
"""

import os
import time
import KBHit
import sys
import random
import json
from operator import itemgetter

class Board(object):

    def __init__(self):

        self.layout = "-----------------"
        self.board_length = 50
        self.basic_board = [self.layout for i in range(self.board_length)]

    def pos_update(self,items):

        x = []
        y = []
        symbol = []

        for item in items:
            x.append(item.X)
            y.append(item.Y)
            symbol.append(item.symbol)

        new_board = self.basic_board[:]

        for i, y_pos in enumerate(y):
            cur_line = new_board[y_pos]
            new_board[y_pos] = cur_line[0:x[i]] + symbol[i] + cur_line[x[i]+1:]

        for line in new_board:
            print line

    def check_pos(self,x,y):
    # Returns true if the coordinate is whitin the board
        if 0 <= x <= len(self.layout) - 1 and -1 < y < self.board_length:
            return True
        else:
            return False

    def game_over(self, level):

        print "------------------ "
        print "     GAME OVER     "
        print " You Reached Level:"
        print "        %i         " %level
        print "-------------------"
        time.sleep(2)


    def next_level(self):

        print "------------------------------------"
        print "          CONGRATULATIONS!          "
        print "     YOU REACHED THE NEXT LEVEL!    "
        print "------------------------------------"
        time.sleep(2)
        os.system('cls')

class Player(object):

    def __init__(self, x, y):
        self.symbol = "X"
        self.X = x
        self.Y = y

    def move_increment(self,arrow):

        if arrow == 0:
            return 0, -1
        elif arrow == 1:
            return 1,0
        elif arrow == 2:
            return 0,1
        elif arrow == 3:
            return -1,0

    def move(self, arrow, board):

        xinc, yinc = self.move_increment(arrow)

        if board.check_pos(self.X + xinc, self.Y + yinc):
            self.X += xinc
            self.Y += yinc

class Enemy(object):

    def __init__(self, x, y):

        self.symbol = "O"
        self.X = x
        self.Y = y
        self.move_increment = random.randint(20,40)
        self.move_check = 0

    def move(self, board):

        if self.move_check >= self.move_increment:

            yinc = 1
            
            if random.randint(0,1):
                xinc = 1
            
            else:
                xinc = -1
                
            if board.check_pos(self.X + xinc, self.Y + yinc):
               
                self.Y += yinc
                self.X += xinc
                
                if random.randint(0,10) <= 2:
                    self.increase_speed()
                
            else:
                self.Y = 0
                self.increase_speed()

            self.move_check = 0

        else:
            self.move_check += 1

    def increase_speed(self):
        self.move_increment = self.move_increment*0.80


class Engine(object):

    def __init__(self, board):

        self.tick = 0.05
        self.board = board
        self.kb = KBHit.KBHit()
        self.player = Player(len(board.layout)/2,board.board_length-1)
        
        # Enemy settings
        self.num_init_enemies = 15
        self.spawn_radius = 2
        self.enemies = self.spawn_multiple_enemies(self.num_init_enemies)
        self.enemy_spawn_rate = 10.0
        self.spawn_timer = 0

        self.level = 1
        self.highscore = Highscore()
        self.menu = Menu(self.highscore)
        
    def run(self):
        
        os.system('cls')
        self.menu.show_menu()

        while True:
            os.system('cls')
            
            if self.next_level():
                self.board.next_level()
                self.enemy_spawn_rate = self.enemy_spawn_rate*0.8
                self.level += 1
                self.player.Y = board.board_length-1
                self.num_init_enemies += 2
                self.enemies = self.spawn_multiple_enemies(self.num_init_enemies)
            
            # Game over
            if self.collision(self.player, self.enemies):
                self.board.game_over(self.level)
                self.highscore.check_result(self.level)
                self.reset()

            # Keyboard press
            if self.kb.kbhit():
                self.player.move(self.check_arrow(), self.board)

            for enemy in self.enemies:
                enemy.move(board)

            # Spawn enemies
            if self.spawn_timer >= self.enemy_spawn_rate:

                new_enemy = self.spawn_enemy()
                self.enemies.append(new_enemy)
                self.spawn_timer = 0

            self.spawn_timer += 1

            items = self.enemies[:]
            items.append(self.player)

            self.board.pos_update(items)

            time.sleep(self.tick)

    def spawn_enemy(self):

        collision = True
        
        while collision:
            
            x = random.randrange(0, len(self.board.layout))
            y = random.randrange(0, self.board.board_length)
            new_enemy = Enemy(x,y)
            
            if not self.collision_radius(self.player, [new_enemy], self.spawn_radius):
                collision = False

        return new_enemy

    def spawn_multiple_enemies(self, number):
        
        new_enemies = []        
                
        for i in range(number):
            new_enemies.append(self.spawn_enemy())
            
        return new_enemies            

    def next_level(self):
        if self.player.Y == 0:
            return True

    def collision(self, player, enemies):

        for enemy in enemies:
            if player.X == enemy.X and player.Y == enemy.Y:
                return True
        return False
        
    def collision_radius(self, player, enemies, radius):
        
        p_x = player.X
        p_y = player.Y        
        
        for enemy in enemies:
            
            e_x = enemy.X
            e_y = enemy.Y

            if p_x - radius <= e_x <= p_x + radius and p_y - radius <= e_y <= p_y + radius:
                return True
                   
        return False
        
    def check_arrow(self):
        try:
            arrow = self.kb.getarrow()
            return arrow

        except:
            return False
            
    def reset(self):
        new_board = Board()
        self.__init__(new_board)
        self.run()

class Menu(object):

    def __init__(self, highscore):

        self.highscore = highscore

    def show_menu(self):

        print "---------------"
        print "1. Play"
        print "2. Show Highscores"
        print "3. Quit"
        print "---------------"

        choice = raw_input("> ")

        if choice == "1":
            return

        elif choice == "2":
            self.highscore.print_highscore()
            self.show_menu()

        elif choice == "3":
            sys.exit()

        else:
            print "Option not recognized."
            time.sleep(2)
            self.show_menu()

class Highscore(object):

    def __init__(self,highscore_file = "highscore.json"):
        
        self.highscore_file = highscore_file
        
        # Creating empyt highscore list if not present
        if not os.path.isfile(highscore_file):
            self.clear_highscores()

        self.scores = self.load_highscores(self.highscore_file)

    def print_highscore(self):
        
        sorted_highscores = sorted(self.scores, key = lambda tup: tup[1], reverse = True)
        
        print "---------------"
        print "  HIGHSCORES:  "
        print " Nr.\t Initials\tLevel"
        
        for i, user in enumerate(sorted_highscores):
            print "%i.\t\%s\t\%s" %(i+1, user[0], user[1])

        print "Press C to clear highscores:"        
        clear = raw_input("> ")
        
        if clear.lower() == "c":
            if self.confirm_clear():
                self.clear_highscores()
                
        
        return
    
    def check_result(self, level):
        
        scores = self.scores
        scores = sorted(scores, key = lambda tup: tup[1], reverse = True)
        
        for i, score in enumerate(scores):
            
            if level > score[1]:
                initials = self.new_highscore()
                scores = scores[:i] + [(initials, level)] + scores[i:]
                scores.pop()
                self.scores = scores
                self.save_highscores()
                return

            
    def save_highscores(self):
        with open(self.highscore_file, "w") as fp:
            json.dump(self.scores, fp)

    def new_highscore(self):
        print "Congratulations you made a Highscore!"
        print "Enter initials:"
        
        while True:
            initials = raw_input("> ")
            if len(initials) == 3:
                return initials
            else:
                print "Initals must be 3 characters."
                time.slee(2)
        
    def load_highscores(self, score_file):
        
        fp = open(score_file)
        scores = json.load(fp)
        fp.close()
        
        return scores

    def clear_highscores(self):
        
        default_highscore = [("NN1" , 0),
                             ("NN2" , 0),
                             ("NN3" , 0),
                             ("NN4" , 0),
                             ("NN5" , 0),
                             ("NN6" , 0),
                             ("NN7" , 0),
                             ("NN8" , 0),
                             ("NN9" , 0),
                             ("NN0" , 0),
                         ]
        print "Clearing Highscores"
        time.sleep(1)
        with open(self.highscore_file,"w") as fp:            
            json.dump(default_highscore, fp)
        

    def confirm_clear(self):
        
        print "Are you sure you want to clear highscores Y/N ?"
        confirm = raw_input(">  ")  
        
        if confirm.lower() == "y":
            return True
        else:
            return False

board = Board()
game = Engine(board)
game.run()
