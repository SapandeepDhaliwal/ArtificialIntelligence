# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 12:23:41 2018

@author: Sapandeep Dhaliwal
"""

import copy
import numpy as np
import math
import random
import time

class square(object):
    def __init__(self):
        self.score = 0
        self.policeman_present = False

    def get_score(self):
        return self.score

    def set_policeman_present(self):
        self.policeman_present = True

    def reset_policeman_present(self):
        self.policeman_present = False

    def is_policeman_present(self):
        return self.policeman_present

    def increment_score(self, inc):
        self.score += inc

    def __repr__(self):
        s = '({},{})'.format(self.score,self.policeman_present)
        return s

class city(object):
    def __init__(self):
        self.matrix = []
        self.size_of_city = 0
        self.police_num = 0
        self.scooter_num =0
        self.total_score = 0
        self.feasible_squares = set()
        self.count_of_police =0
        self.list_of_policemen_loc = set()
        self.id = 0
        self.all_squares = set()
        self.read_file()
        self.start_time = time.clock()

        self.max_prob = 0
        self.min_prob = 1
        self.max_temp = 0
        self.min_temp = 100000

        #For analysis
        self.temp_hist = []
        self.prob_hist = []
        self.error_hist = []
        self.jump_hist = []
        self.zero_prob_step = 0

    def get_list_of_policemen_loc(self):
        return self.list_of_policemen_loc

    def get_feasible_squares(self):
        return self.feasible_squares

    def __eq__(self, other):
        if self.list_of_policemen_loc == other.list_of_policemen_loc:
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def read_file(self):
        """
        Read input file input.txt and store results
        :return:
        """

        with open('input.txt') as text_file:
            self.size_of_city = int(text_file.readline())
            self.police_num = int(text_file.readline())
            self.scooter_num = int(text_file.readline())

            for i in range(self.size_of_city):
                self.matrix.append([])
                for j in range(self.size_of_city):
                    self.matrix[i].append([])

            for i in range(self.size_of_city):
                for j in range(self.size_of_city):
                    self.matrix[i][j] = square()
                    self.feasible_squares.add((i,j))
                    self.all_squares.add((i,j))

            self.numpy_mat = np.zeros((self.size_of_city,self.size_of_city))

            for line in text_file:
                loc_of_scooter = line.split(',')
                row = int(loc_of_scooter[0])
                col = int(loc_of_scooter[1])
                self.matrix[row][col].increment_score(1)
                self.numpy_mat[row][col] += 1

        text_file.close()


    def place_policeman(self,row,col):
        self.matrix[row][col].set_policeman_present()
        self.list_of_policemen_loc.add((row,col))
        self.count_of_police += 1
        self.id += 2**(row*self.size_of_city + col)
        self.total_score += self.matrix[row][col].get_score()
        for x,y in self.feasible_squares.copy():
            if self.matrix[x][y].is_policeman_present():
                for i in range(self.size_of_city):
                    if (x,i) in self.feasible_squares:
                        self.feasible_squares.remove((x,i))
                for j in range(self.size_of_city):
                    if (j,y) in self.feasible_squares:
                        self.feasible_squares.remove((j,y))

                for i in range(self.size_of_city):
                    if(x+i,y+i) in self.feasible_squares:
                        self.feasible_squares.remove((x+i,y+i))
                    if(x-i,y-i) in self.feasible_squares:
                        self.feasible_squares.remove((x-i,y-i))
                    if(x-i,y+i) in self.feasible_squares:
                        self.feasible_squares.remove((x-i,y+i))
                    if(x+i,y-i) in self.feasible_squares:
                        self.feasible_squares.remove((x+i,y-i))


    def get_total_score(self,loc_police = None):
        if loc_police == None:
            return self.total_score
        else:
            score = 0
            for x,y in loc_police:
                score += self.matrix[x][y].get_score()
            return score

    """Simulated annealing"""
    def initialize_state(self):
        self.total_score = 0
        self.count_of_police =0
        for x,y in self.list_of_policemen_loc:
            self.matrix[x][y].reset_policeman_present()
        self.list_of_policemen_loc = set()
        self.feasible_squares = set(self.all_squares)
        self.id = 0

    def get_next_random_state(self, large_jump = False):
        if self.count_policemen() == self.police_num and large_jump == False:
            old_policeman_location = list(self.get_list_of_policemen_loc())
            self.initialize_state()
            index = random.randint(0, len(old_policeman_location)-1)
            old_policeman_location.pop(index)
            for x,y in old_policeman_location:
                self.place_policeman(x,y)
            if len(self.feasible_squares) > 0:
                x,y = random.sample(self.feasible_squares,1)[0]
                self.place_policeman(x,y)
            else:
                return False
            return True
        else:
            self.initialize_state()
            for police_man in range(self.police_num):
                if len(self.feasible_squares) > 0:
                    x,y = random.sample(self.feasible_squares,1)[0]
                    self.place_policeman(x,y)
                else:
                    return False
            return True

    def get_new_temp(self, prev_temp, step):
        temp = 5.0/(1.0 + math.exp(float(step)/float(3000.0)))
        self.temp_hist.append(temp)
        if self.max_temp < temp:
            self.max_temp = temp
        if self.min_temp > temp:
            self.min_temp = temp
        return temp

    def should_accept_next_state(self, step, temp, error):
        prob = math.exp(float(error)/float(temp))
        self.prob_hist.append(prob)
        self.error_hist.append(error)

        if self.max_prob < prob:
            self.max_prob = prob
        if self.min_prob > prob:
            self.min_prob = prob

        if prob == 0.0 and self.zero_prob_step == 0:
            self.zero_prob_step = step
        draw = random.uniform(0,1)
        if draw < prob:
            return True
        return False

    def get_best_score_SA(self, initial_state, temp_step = 5.0, init_temp = 2.5, max_steps = 10000):
        max_score = 0
        stayed_with_good_state = 0
        switched_state = 0
        count_next_current_same = 0
        next_state_large_jump = False
        count_large_jump = 1
        no_improve_count = 0
        improve_count_threshold = 1000
        stopping_temp = 0.0001

        Current_state = initial_state
        best_state = copy.deepcopy(initial_state)
        score = Current_state.get_total_score()
        intial_score = score
        max_score = score
        same_initial_state_count = 0
        temp = init_temp
        i = 1
        time_elapsed = False
        last_state_update_step = 0
        while(1):
            i += 1
            next_state = copy.deepcopy(Current_state)
            while next_state.get_next_random_state(large_jump = next_state_large_jump) != True:
                pass
            new_score = next_state.get_total_score()

            if next_state_large_jump == True:
                count_large_jump += 1
                next_state_large_jump = False
                no_improve_count = 0
                if intial_score == new_score:
                    same_initial_state_count += 1
                self.jump_hist.append(1)
            else:
                self.jump_hist.append(0)

            """if stuck in same state for some time when matrix is dense, restart search"""
            if Current_state.get_list_of_policemen_loc() == next_state.get_list_of_policemen_loc():
                count_next_current_same += 1
                if count_next_current_same > next_state.police_num:
                    next_state_large_jump = True
                    count_next_current_same = 0
            else:
                count_next_current_same = 0

            if new_score > max_score:
                max_score = new_score
                best_state = copy.deepcopy(next_state)

            temp = self.get_new_temp(temp, i*temp_step)

            if new_score >= score and Current_state.get_list_of_policemen_loc() != next_state.get_list_of_policemen_loc():
                score = new_score
                Current_state = copy.deepcopy(next_state)
                last_state_update_step = i
            elif new_score < score:
                if self.should_accept_next_state(i, float(temp), new_score-score):
                    Current_state = copy.deepcopy(next_state)
                    score = new_score
                    switched_state += 1
                    last_state_update_step = i
                else:
                    stayed_with_good_state += 1

            if new_score <= score or score <= max_score:
                no_improve_count += 1
            else:
                no_improve_count = 0

            """if no improvement for some time, then take large step"""
            if no_improve_count > improve_count_threshold and next_state_large_jump == False:
                next_state_large_jump = True
                no_improve_count = 0

            current_time = time.clock()
            if(int(current_time - self.start_time) > 150):
                time_elapsed = True
                break

            if i > max_steps:
                break

            if temp < stopping_temp:
                break

        return (best_state, time_elapsed)

    def count_policemen(self):
        return self.count_of_police

    def get_matrix_val(self, row, col):
        return self.numpy_mat[row][col]




class Homework1b(object):

    def __init__(self):
        self.matrix = []
        self.size_of_city = 0
        self.police_num = 0
        self.scooter_num =0


        City = city()
        City2 = city()
        score = []
        while City2.get_next_random_state() != True:
            pass
        time_elapsed = False
        for i in range(20):
            if time_elapsed == False:
                (City2, time_elapsed) = City.get_best_score_SA(initial_state = City2)
                score.append(City2.get_total_score())
            else:
                break
        max_score = max(score)
        with open("output.txt",'w') as out_file:
            out_file.write(str(max_score) + "\n")
        out_file.close()


if __name__== "__main__":
    solution = Homework1b()
