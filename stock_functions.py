# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 17:29:50 2016

@author: Ben
"""

import numpy as np
import random
from copy import copy
#from copy import deepcopy

#from random import randint

#import parsetxt

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
            #print 'price at buy: '+str(data[n])
            num_stocks=int(capital/data[n])
            #print 'num_stocks: '+str(num_stocks)
            capital-=num_stocks*data[n]
            #print 'capital: '+str(capital)
            days_held+=1
        #if action is to sell, increase capital by (#of stocks)*(price of stock)
        #Set #stocks=0
        elif actions[n]=='sell':
            #print 'price at sell: '+str(data[n])
            capital+=num_stocks*data[n]
            num_stocks=0
            #print 'num_stocks: '+str(num_stocks)
            #print 'capital: '+str(capital)
        #if action is to hold, just increment days_held
        elif actions[n]=='hold':
            days_held+=1
            
    frac_returns=float(capital-starting_capital)/starting_capital
    frac_returns_per_day=float(frac_returns)/days_held
    
    return frac_returns,frac_returns_per_day
        
        
#actions=['buy','hold','sell','buy','hold','sell']

def mwa_mwslope_func(data,window):
    '''Given list of data, returns the moving window avg over last window number of data points, and slope of line fit to last window # of data points'''
    
    mwa=[]
    mwslope=[]
    for n in range(len(data)):
        if n>=window-1:
            l=data[(n-window+1):(n+1)]
            P=np.polyfit(range(len(l)),l,1)
            mwa.append(np.mean(l))
            mwslope.append(P[0])
        elif n==0:
            mwa.append(data[n])
            mwslope.append(0)
        else:
            l=data[:n+1]
            mwa.append(np.mean(l))
            P=np.polyfit(range(len(l)),l,1)
            mwslope.append(P[0])
            
    return mwa,mwslope
    
def multivar_lin_strategy(classifiers,params):
    
    #matrix multiply classifier matrix by param vector in column form
#    print('params')
#    print params
#    print('classifiers shape')
#    print classifiers.shape
    V=np.dot(classifiers,params)
#    print 'V: '
#    print list(V)
    #print V
    last_action='sell'
    actions=[]
    for n in range(len(V)):
        #print n
        if V[n]>1 and last_action=='sell':
            #print 'buying'
            actions.append('buy')
            last_action='buy'
            last_ind=n
            #print 'actions: '
            #print actions
        elif V[n]<-1 and last_action=='buy':
            #print 'selling'
            actions.append('sell')
            last_action='sell'
            last_ind=n
            #print 'actions: '
            #print actions
        else:
            actions.append('hold')
            #print 'actions: '
            #print actions
            
    #we don't want to finish buying a stock, so if we do replace it with hold.
    #print 'last ind:'
    #print last_ind
    if last_action=='buy':
        #print 'here'
        actions[last_ind]='hold'
        #print 'actions'
        #print actions
    #print actions   
    return actions
    
def evaluate_individual_fitness(algorithm,data_segments,params,classifier_segments,weights):
    '''Runs a backtest on algorithm (a function that takes classifiers and params) for each segment of data in data_segments.
    Returns fitness score given by a1*(average frac_returns per segment)+a2*(stand dev in frac returns)+a3*avg(frac_returns_per_day)'''
    
    
    a1=weights[0]
    a2=weights[1]
    a3=weights[2]
    a4=weights[3]
    a5=weights[4]
    starting_capital=10**6    
    frac_returns_list=[]
    frac_returns_per_day_list=[]
    for n in range(len(data_segments)):
        classifiers=classifier_segments[n]
        data=data_segments[n]
        #decide actions
        actions=algorithm(classifiers,params)
        #backtest
        (frac_returns,frac_returns_per_day)=backtest_func(actions,data,starting_capital)
        #print 'frac returns: '+str(frac_returns)
        frac_returns_list.append(frac_returns)
        frac_returns_per_day_list.append(frac_returns_per_day)
        
    fitness_score=a1*np.mean(frac_returns_list)+a2*np.std(frac_returns_list)+a3*np.mean(frac_returns_per_day)+a4*np.count_nonzero(params)+a5*min(frac_returns_list)
    
    return fitness_score,frac_returns_list


    
def rank_individuals(params_list,trading_strategy,fitness_function,weights,data_segments,classifier_segments):
    
    """ Ranks the individuals based on their fitness according to the fitness
    algorithm, and returns a list of the fitnesses in order of largest fitness
    as well as a list of the original parameters with the same order as the
    respective fitnesses. 
    """

    fitness_list=[]

    param_list_ordered=[]

    fappend=fitness_list.append
    pappend=param_list_ordered.append
    finsert=fitness_list.insert
    pinsert=param_list_ordered.insert
    
    # iterate through all indviduals
    for i in range(len(params_list)):
        #Select params for ith individual
        indv=params_list[i]
        #print 'individual'
        #print indv
        #evaluate individual's fitness
        (indv_fitness,frac_returns_list)=evaluate_individual_fitness(trading_strategy,data_segments,indv,classifier_segments,weights)

        # insert pfit into appropriate index of fitness list
        if len(fitness_list)==0:

            fappend(copy(indv_fitness))
            pappend(copy(indv))

        elif indv_fitness>max(fitness_list):
            finsert(0,copy(indv_fitness))
            pinsert(0,copy(indv))            
            

        elif indv_fitness<min(fitness_list):
            fappend(indv_fitness)
            pappend(indv)
            
            
        else:
            for f in fitness_list:
                if indv_fitness>=f:

                    finsert(fitness_list.index(f),copy(indv_fitness))
                    pinsert(fitness_list.index(f),copy(indv))

                    break
    return param_list_ordered,fitness_list
        
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
        offspring=list(offspring)
        #append newely created offspring to list of offspring
        offspring_list.append(offspring)
        
    return offspring_list
    
def produce_offspring_with_param_elim(params_list_ordered,num_reproduce,num_offspring,mutation_rate,param_elim_prob,param_reint_prob):
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
        
                
        for i in range(len(offspring)):
            if offspring[i]!=0:
                if random.random()<param_elim_prob:
                    offspring[i]=0
                else:
                    offspring[i]=offspring[i]+float(np.random.normal(0,np.linalg.norm(offspring)*mutation_rate,1))
            else:
                if random.random()<param_reint_prob:
                    try:
                        offspring[i]=float(np.random.normal(0,np.linalg.norm(offspring)*mutation_rate,1))
                    except:
                        offspring[i]=0
                    
        offspring=list(offspring)
        #append newely created offspring to list of offspring
        offspring_list.append(offspring)
        
    return offspring_list
        
    
#def produce_offspring(params_list_ordered,num_reproduce,num_offspring,mutation_rate):
#    '''Takes a list of parameters (list of lists) representing individuals, 
#        number of individuals to allow to reproduce (num_reproduce), number of offspring to create (num_offspring),
#        and mutation_rate (stand dev of noise added=norm(offspring)*mutation_rate )
#        Returns offspring_list, list of lists of params representing offspring''' 
#        
#    parents=params_list_ordered[0:num_reproduce]   #select num_reproduce best individuals to be parents
#    
#    offspring_list=[]
#    
#    for n in range(num_offspring):
#        #select two random parents
#        parent1=random.choice(parents)
#        parent2=random.choice(parents)
#        #select two random weighs
#        weight1=random.random()
#        weight2=1-weight1
#        
#        #create offspring by doing weighted avg of parents params
#        offspring=[weight1*parent1[n]+weight2*parent2[n] for n in range(len(parent1))]
#        
#        #create noise vector with stand dev=norm(offspring)*mutation_rate
#        noise=np.random.normal(0,np.linalg.norm(offspring)*mutation_rate,len(offspring))
#        #add noise
#        offspring+=noise
#        #append newely created offspring to list of offspring
#        offspring_list.append(offspring)
#        
#    return offspring_list
        
    

#data=[1,2,3,.5,-100,2]
#starting_capital=1000



#return_frac=backtest_func(actions,data,starting_capital)


#data_segments=[[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9],[1,2,3,4,5,6,7,8,9]]
#
#classifier_segments=[np.array([[1,2,3],[1,-2,-3],[1,2,3],[1,2,3],[-1,2,-3],[1,2,3],[-1,-2,-3],[1,2,3],[1,2,-3]]),np.array([[1,2,3],[1,-2,-3],[1,2,3],[1,2,3],[-1,2,-3],[1,2,3],[-1,-2,-3],[1,2,3],[1,2,-3]]),np.array([[1,2,3],[1,-2,-3],[1,2,3],[1,2,3],[-1,2,-3],[1,2,3],[-1,-2,-3],[1,2,3],[1,2,-3]]),np.array([[1,2,3],[1,-2,-3],[1,2,3],[1,2,3],[-1,2,-3],[1,2,3],[-1,-2,-3],[1,2,3],[1,2,-3]])]
#
#params=[1,2,3]
#
##actions=multivar_lin_strategy(classifiers,params)
#
#
#fitness=evaluate_individual_fitness(multivar_lin_strategy,data_segments,params,classifier_segments,[1,0,0])
#
##Create 2 individuals, try to get it to order them
#idv1=[1,2,3]  #this one has fitness of 3.37
#idv2=[1,2,-3] #this one has fitness of 1.06

##put individuals together as a list
#params_list=[idv1,idv2]
#weights=[1,0,0]

#(param_list_ordered,fitness_list)=rank_individuals(params_list,multivar_lin_strategy,evaluate_individual_fitness,weights,data_segments,classifier_segments)

















