# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 19:14:29 2016

@author: Ben
"""
#import numpy as np
#import random
#from copy import copy
#from copy import deepcopy

import numpy as np
import stock_functions
import parsetxt

pop_size=1000
num_reproduce=100
original_pop_std=10
mutation_rate=.01
maxIters=100
trials=6
weights=[0,0,0,0,1]
p_goto0=0
p_becomenon0=0

random.seed(0)
data=parsetxt.parsetxt('Close','ford_5Y.txt')

data_train=data[0:4*len(data)/5]
data_test=data[4*len(data)/5:]

(mwa3,mwslope3)=stock_functions.mwa_mwslope_func(data,3)
(mwa5,mwslope5)=stock_functions.mwa_mwslope_func(data,5)
(mwa10,mwslope10)=stock_functions.mwa_mwslope_func(data,10)
(mwa30,mwslope30)=stock_functions.mwa_mwslope_func(data,30)

classifiers=np.transpose(np.array([len(mwa3)*[1],data,mwa3,mwa5,mwa10,mwa30,mwslope3,mwslope5,mwslope10,mwslope30]))
#classifiers=np.transpose(np.array([len(mwa3)*[1],data,mwa3,mwa10,mwslope3,mwslope10]))
classifiers_train=classifiers[0:len(data_train),:]
classifiers_test=classifiers[len(data_train):,:]

num_classifiers=classifiers.shape [1]


#[data_segments,classifier_segments]=parsetxt.chunks(data_train,classifiers_train,30,10)
original_pop=[]
for n in range(pop_size):
    indv=list(np.random.normal(0,original_pop_std,num_classifiers))
    original_pop.append(indv)
    
population=original_pop    

for n in range(maxIters):
    #Generate evaluation data for this generaiton
    [data_segments,classifier_segments]=parsetxt.chunks(data_train,classifiers_train,100,2)
    #rank 
    (population_ordered,fitness_list)=stock_functions.rank_individuals(population,stock_functions.multivar_lin_strategy,stock_functions.evaluate_individual_fitness,weights,data_segments,classifier_segments)
    (fitness_score,frac_returns_list)=stock_functions.evaluate_individual_fitness(stock_functions.multivar_lin_strategy,data_segments,population_ordered[0],classifier_segments,weights)
    print 'iter #: ' + str(n)    
    print 'max fitness: '+str(max(fitness_list))
    #print 'frac_returns_list: '+str(frac_returns_list)
    
    #test on training data just so we can have an idea if we're actually makeing progress
    actions=stock_functions.multivar_lin_strategy(classifiers_test,population_ordered[0])
    (frac_returns,frac_returns_per_day)=stock_functions.backtest_func(actions,data_test,10**6)
    print 'frac_returns on test data: '+str(frac_returns)
     
    
    #offspring=stock_functions.produce_offspring(population_ordered,num_reproduce,pop_size,mutation_rate)
    offspring=stock_functions.produce_offspring_with_param_elim(population_ordered,num_reproduce,pop_size,mutation_rate,p_goto0,p_becomenon0)
    population=offspring

#for n in range(maxIters):
#    #Generate evaluation data for this generaiton
#    [data_segments,classifier_segments]=parsetxt.chunks(data_train,classifiers_train,30,30)
#    for j in range(trials):
#        data=data_segments[j]
#        classifiers=classifier_segments[j]
#        (population_ordered,fitness_list)=stock_functions.rank_individuals(population,stock_functions.multivar_lin_strategy,stock_functions.evaluate_individual_fitness,[1,0,0],[data],[classifiers])
#        #eliminate worst half
#        population=population_ordered[0:len(population_ordered)/2]
#    print 'iter #: ' + str(n)    
#    print 'max fitness: '+str(max(fitness_list))
#    #test on training data just so we can have an idea if we're actually makeing progress
#    actions=stock_functions.multivar_lin_strategy(classifiers_test,population[0])
#    (frac_returns,frac_returns_per_day)=stock_functions.backtest_func(actions,data_test,10**6)
#    print 'frac_returns on test data: '+str(frac_returns)
#     
#    
#    offspring=stock_functions.produce_offspring(population,len(population),pop_size,mutation_rate)
#    population=offspring