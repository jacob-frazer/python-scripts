# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 12:41:38 2020

@author: Jake Frazer
"""
import numpy as np
import matplotlib.pyplot as plt

# blackjack probabilities - without draws
p_win = 0.464
p_lose = 0.536

# blackjack probabilities - with draws
p_win = 0.4243
p_lose = 0.4909
p_draw = 0.0848

# simulating playing one stretch of hands - true if make it to end - false if hit 0 at some point
def knocked_out(min_bet, value_required, cash_stack):
    ''' TODO: Make it carry out the final value too so that we can see the money pulled out in 
    order to calculate EV of strategy
    '''
    # check to catch if doubling phase has already surpassed betting requirements
    if value_required < 0:
        return True, cash_stack
    
    hands_to_play = value_required/min_bet
    ko_count = -(cash_stack/min_bet)
    
    wl_count = 0
    hands = np.random.random(int(hands_to_play))
    for h in hands:
        # you lose the hand
        if h >= p_win + p_draw:
            wl_count -= 1    
        # you draw the hand
        elif h >= p_win:
            continue    
        # you win the hand
        else:
            wl_count += 1
            
        if wl_count == ko_count:
            return False, 0
        
    return True, cash_stack + (wl_count*min_bet)


def doubling_phase(n, start_cash):
    ''' calculates probability of successfully doubling for n hands.
    returns the prob of being alive, cash stack at that ponit, total amount 
    wagered to then
    '''
    end_cash = start_cash
    total_wagered = 0   
    prob = 0.464**n
    
    for i in range(1,n+1):
        total_wagered += end_cash
        end_cash *= 2
        
    return prob, end_cash, total_wagered



def calculate_evs(doubling_hands, start_cash, min_bet, value_required):
    ''' func to work out EV's and probability of getting money
    '''
    
    # simulates doubling phase for n hands
    prob, end_cash, total_wagered = doubling_phase(doubling_hands, start_cash)
    
    # make this as big as poss but computational pain!
    n = 10000

    # gives probability of making it to the end with some amount of money
    # sums[0] = prob,    sums[1] = money
    result = np.array([knocked_out(min_bet, (value_required-total_wagered), end_cash) for x in range(n)],dtype='int64')
    sums = np.sum(result,0)/n
    probability_of_return = prob*sums[0]
    return probability_of_return, sums[1]




# gather some results for different starting values -- EV's
n_range = range(1,40)
results = np.array([calculate_evs(n,10,5,3500) for n in n_range])

x_axis = [x-1 for x in n_range]

evs, prob = [], []
for x in results:
    evs.append(x[0]*x[1])
    prob.append(x[0]*100) 
 
    
# my situation post doubling phase
my_scenario = calculate_evs(0,480,5,3025)

# ev plot
plt.plot(x_axis, evs)
plt.ylabel("Expectation Value £'s")
plt.xlabel("Initial all-in hands")
plt.title("Expectation value of free blackjack credit")
plt.show()

# prob of getting any return plot
plt.plot(x_axis, prob)
plt.ylabel("Probability of ANY return, %")
plt.xlabel("Initial all-in hands")
plt.title("Likelihood of a return from free blackjack credit")
plt.show()





