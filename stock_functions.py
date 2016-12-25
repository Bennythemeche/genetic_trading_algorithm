# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 17:29:50 2016

@author: Ben
"""

import numpy as np

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
            print 'num_stocks: '+str(num_stocks)
            capital-=num_stocks*data[n]
            print 'capital: '+str(capital)
            days_held+=1
        #if action is to sell, increase capital by (#of stocks)*(price of stock)
        #Set #stocks=0
        elif actions[n]=='sell':
            capital+=num_stocks*data[n]
            num_stocks=0
            print 'num_stocks: '+str(num_stocks)
            print 'capital: '+str(capital)
        #if action is to hold, just increment days_held
        elif actions[n]=='hold':
            days_held+=1
            
    frac_returns=float(capital-starting_capital)/starting_capital
    frac_returns_per_day=float(frac_returns)/days_held
    
    return frac_returns,frac_returns_per_day
        
        
actions=['buy','hold','sell','buy','hold','sell']

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
    
    #matrix multiply classifier matrix by param vector in column form
    V=
    last_action=='sell'
    for n in range(len(V)):
        if V[n]>1 and last_action=='sell':
            actions.append('buy')
            last_action='buy'
            last_ind=n
        elif V[n]<-1 and last_action=='buy':
            actions.append('sell')
            last_action='sell'
            last_ind=n
        else:
            actions.append('hold')
            
    #we don't want to finish buying a stock, so if we do replace it with hold.
    if last_action=='buy':
        actions[last_ind]=='hold'
        
    return actions
    
def evaluate_individual_fitness(algorithm,data_segments,params,classifier_segments,a1,a2,a3):
    '''Runs a backtest on algorithm (a function that takes classifiers and params) for each segment of data in data_segments.
    Returns fitness score given by a1*(average frac_returns per segment)+a2*(stand dev in frac returns)+a3*avg(frac_returns_per_day)'''
    
    frac_returns_list=[]
    frac_returns_per_day_list=[]
    for n in range(len(data_segments)):
        classifiers=classifier_segments[n]
        data=data_segments[n]
        #decide actions
        actions=algorithm(classifiers,params)
        #backtest
        (frac_returns,frac_returns_per_day)=backtest_func(actions,data,starting_capital)
        frac_returns_list.append(frac_returns)
        frac_returns_per_day_list.append(frac_returns_per_day)
        
    fitness_score=a1*np.mean(frac_returns_list)+a2*np.std(frac_returns_list)+a3*np.mean(frac_returns_per_day)
    
    return fitness_score
        
        


#data=[1,2,3,.5,-100,2]
#starting_capital=1000



#return_frac=backtest_func(actions,data,starting_capital)

data=[1,2,1,4,5,6,1,7,1]
mwa=mwa_mwslope_func(data,3)







