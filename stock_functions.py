# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 17:29:50 2016

@author: Ben
"""

import numpy as np
import random
from copy import copy
from copy import deepcopy

def backtest_func(actions,data,starting_capital):
    '''Backtests a list of actions produced by a trading algorithm.
    inputs: 
        actions: list of strings, either 'buy', 'sell', or 'hold', indicating what to do on that day
        data: list representing stock prices on each day
        starting_capital
    outputs:
        frac_returns: fractional increase from starting capital
        frac_returns_per_day: frac_returns/(# of days stock was held)'''
    days_held=0 
    
    capital=starting_capital

    for n in range(len(data)):

        #if action is to buy, calculate # of stocks bought by int(capital/data[n]), then decrese capital by num_stocks*price of stocks
        #also, increment days held... we'll consider the day the stock is bought the first day it is held        
        if actions[n]=='buy':
            num_stocks=int(capital/data[n])

            capital-=num_stocks*data[n]

            days_held+=1
        #if action is to sell, increase capital by (#of stocks)*(price of stock)
        #Set #stocks=0
        elif actions[n]=='sell':
            capital+=num_stocks*data[n]
            num_stocks=0

        #if action is to hold, just increment days_held
        elif actions[n]=='hold':
            days_held+=1
            
    frac_returns=float(capital-starting_capital)/starting_capital
    frac_returns_per_day=float(frac_returns)/days_held
    
    return frac_returns,frac_returns_per_day
        
        
actions=['buy','hold','sell','buy','hold','sell']
#actions=['sell']
def mwa_mwslope_func(data,window):
    '''Given list of data, returns the moving window avg over last window number of data points, and slope of line fit to last window # of data points'''
    #TODO: figure out how to fit slopes to these windows of data
    mwa=[]
    for n in range(len(data)):
        if n>=window-1:
            l=data[(n-window+1):(n+1)]
            mwa.append(np.mean(l))
        elif n==0:
            mwa.append(data[n])
        else:
            l=data[:n+1]
            mwa.append(np.mean(l))
            
    return mwa



def multivar_lin_strategy(classifiers,params):
    # I didn't understand why "actions" was defined outside of the program. 
    # np.dot does not do matrix multiplication, instead it takes the dot
    # product of the vector--so this was fixed for elementwise multiplication
    # it did not make sense to me why you took the len() of a scalar
    # Where is actions supposed to be defined? 
    #actions=['buy','hold','sell','buy','hold','sell']
    #matrix multiply classifier matrix by param vector in column form
    # I ignored this and defined actions as an empty list at the start of this 
    # function
    actions=[]

    Vlist=[]
    for ind in range(classifiers.shape[1]):

        V=np.dot(float(classifiers[0,ind]),float(params[ind,0]))

        Vlist.append(copy(V)) 

    last_action='sell'

    for n in range(len(Vlist)):

        if Vlist[n]>1 and last_action=='sell':

            actions.append('buy')
            last_action='buy'
            
            # What is the point of last_ind?
            last_ind=n
        elif Vlist[n]<-1 and last_action=='buy':

            actions.append('sell')
            last_action='sell'
            
            # What is the point of last_ind?
            last_ind=n
        else:

            actions.append('hold')

    #we don't want to finish buying a stock, so if we do replace it with hold.
    if last_action=='buy':
        
        # this previously did nothing since you had "==" which just checked 
        # equality and I don't know why the last element wasn't used and you 
        # had the last_ind thing. So I'm not sure if I actually changed this
        # for the better
        actions[-1]='hold'
    return actions
    
def evaluate_individual_fitness(algorithm,data_segments,params,classifier_segments,a1,a2,a3):
    '''Runs a backtest on algorithm (a function that takes classifiers and params) for each segment of data in data_segments.
    Returns fitness score given by a1*(average frac_returns per segment)+a2*(stand dev in frac returns)+a3*avg(frac_returns_per_day)'''
    
    starting_capital=10**6    

    frac_returns_list=[]

    frac_returns_per_day_list=[]

    for n in range(len(data_segments)):

        classifiers=classifier_segments[n]

        data=data_segments[n]

        #decide actions

        actions=algorithm(classifiers,params)

        #backtest
        # this function should use the 'actions' calculated in the previous
        # step not the one externally defined. 
        (frac_returns,frac_returns_per_day)=backtest_func(actions,data,starting_capital)
        frac_returns_list.append(frac_returns)
        frac_returns_per_day_list.append(frac_returns_per_day)
        
    fitness_score=a1*np.mean(frac_returns_list)+a2*np.std(frac_returns_list)+a3*np.mean(frac_returns_per_day)
    
    return fitness_score
    
def rank_individuals(indv_params,fit_alg,dseg,cseg,a1,a2,a3):
    """ Ranks the individuals based on their fitness according to the fitness
    algorithm, and returns a list of the fitnesses in order of largest fitness
    as well as a list of the original parameters with the same order as the
    respective fitnesses. 
    """

    fitness_list=[]

    new_param_list=[]

    fappend=fitness_list.append
    pappend=new_param_list.append
    finsert=fitness_list.insert
    pinsert=new_param_list.insert
    
    # iterate through all indviduals
    for i in range(len(indv_params)):
        par=indv_params[i]

        fitcheck=lambda fit_alg,par: evaluate_individual_fitness(fit_alg,dseg,
                                                                 par,cseg,a1,
                                                                 a2,a3)
        pfit=fitcheck(fit_alg,par)

        # insert pfit into appropriate index of fitness list
        if len(fitness_list)==0:

            fappend(copy(pfit))
            pappend(copy(par))

        elif pfit>max(fitness_list):
            fappend(pfit)
            pappend(par)

        elif pfit<min(fitness_list):
            finsert(0,copy(pfit))
            pinsert(0,copy(par))
            
        else:
            for f in fitness_list:
                if pfit<f:

                    finsert(fitness_list.index(f),copy(pfit))
                    pinsert(fitness_list.index(f),copy(par))

                    break
    return (fitness_list,new_param_list)
        
def produce_offspring(params_list_ordered,num_reproduce,num_offspring,mutation_rate):
    '''Takes a list of parameters (list of lists) representing individuals, 
        number of individuals to allow to reproduce (num_reproduce), number of offspring to create (num_offspring),
        and mutation_rate (stand dev of noise added=norm(offspring)*mutation_rate )
        Returns offspring_list, list of lists of params representing offspring''' 
        
    parents=params_list_ordered[0:num_reproduce]   #select num_reproduce best individuals to be parents
    
    offspring_list=[]
    
    for n in range(num_offspring):
        #select two random parents
        parent1=random.choice(parents)
        parent2=random.choice(parents)
        #select two random weighs
        weight1=random.random()
        weight2=1-weight1
        
        #create offspring by doing weighted avg of parents params
        offspring=[weight1*parent1[n]+weight2*parent2[n] for n in range(len(parent1))]
        
        #create noise vector with stand dev=norm(offspring)*mutation_rate
        noise=np.random.normal(0,np.linalg.norm(offspring)*mutation_rate,len(offspring))
        #add noise
        offspring+=noise
        #append newely created offspring to list of offspring
        offspring_list.append(offspring)
        
    return offspring_list
        
    

#data=[1,2,3,.5,-100,2]
#starting_capital=1000



#return_frac=backtest_func(actions,data,starting_capital)

data=[1,2,1,4,5,6,1,7,1]
mwa=mwa_mwslope_func(data,3)