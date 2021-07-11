
from os import stat
import sys
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import time
import datetime

import gym
import gym_race
import csv

MAP = 'map'

def load_data(file):
    np_load_old = np.load
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)
    data = np.load(file)
    data = data['m']
    np.load = np_load_old
    return data

def makeBucket(state):
    biList = []
    for i in range(len(state)):
        if state[i] <= stateBounds[i][0]:
            bi= 0
        elif state[i] >= stateBounds[i][1]:
            bi= buckets[i] - 1
        else:
            # Mapping the state bounds to the bucket array
            bound_width = stateBounds[i][1] - stateBounds[i][0]
            offset = (buckets[i]-1)*stateBounds[i][0]/bound_width
            scaling = (buckets[i]-1)/bound_width
            bi= int(round(scaling*state[i] - offset))
        biList.append(bi)
    return tuple(biList)


def chooseAction(state, epsilon):
    #either chose randomly or optimal step
    if random.random() < epsilon:
        action = env.action_space.sample()
    else:                                  
        action = int(np.argmax(qTable[state]))
    return action



def learn(decayFactor, simulate = True ,  epsilonMin = 0.001,
         lrMin= 0.4 , EPISODES = 9999999, maxSteps = 2000 , lr_ =  0.8 , epsilon = 0.8 ):

    lr = lr_
    epsilon = epsilon
    print(epsilon)
    gamma = 0.99
    reward = 0
    rewardList = []
    avgList = []
    avg_c = 0
    meanBuffer = np.zeros(100)
    done = False
    env.set_view(simulate)
    threshold = 1000
    tReward =0
    savetime = "-".join(str(datetime.datetime.fromtimestamp(time.time()))[:-10].split(":"))
    filename = MAP + '-' + savetime + str(EPISODES)

    for e in range(EPISODES):

        meanBuffer[avg_c] = tReward
        avg_c += 1

        if (e+1) % 100 ==0 and e != 0:
            rewardList.append(np.mean(meanBuffer))
            meanBuffer = np.zeros(100)
            avg_c = 0
            
        if (e+1) % 5000 ==0 and e !=0:
            savetime = "-".join(str(datetime.datetime.fromtimestamp(time.time()))
                        [:-10].split(":"))
            filename = MAP + '-' + savetime
            ep = e+1
            env.save_memory(filename+'-%d' %ep)
        
        if (e+1) % 1000 == 0 and e!=0:
            avgList.append(np.mean(rewardList[int((e+1)/100-10):]))

        if (e+1) % 5000==0 and e !=0:
            ep = e+1
            with open(filename+'-%d.csv' %ep, 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(rewardList)
                writer.writerow(avgList)
        
        observation = env.reset()
        state0 = makeBucket(observation)
        tReward= 0

        if e >= threshold:
            epsilon = 0.01
        
        for steps in range(maxSteps):
            action = chooseAction(state0, epsilon)
            observation, reward, done, _ = env.step(action)
            state = makeBucket(observation)
            env.remember(state0, action, reward, state, done)
            tReward += reward
            bestQ  = np.amax(qTable[state])
            qTable[state0 + (action,)] += lr *(reward+ gamma*(bestQ) - qTable[state0 + (action,)])


            state0 = state 
            env.render()

            if  done or steps >= maxSteps-1:
                print("Episode %d : steps taken: %i total reward = %f."
                      % (e, steps, tReward))
                break

        #updating epsilon and lr
        epsilon = max(epsilonMin, min(0.8, 1.0 - math.log10((e+1)/decayFactor)))
        lr = max(lrMin, min(0.8, 1.0 - math.log10((e+1)/decayFactor)))

def get_learning_rate(t):
    return max(0.001, min(0.8, 1.0 - math.log10((t+1)/decayFactor)))
    
def test_model(file, maxSteps=2000):
    print("Loading model...")
    model = [file]

    #load qTable  values from the model 
    print("Start setting up the model...")
    gamma = 0.99 
    for list in model:
        mod = load_data(list)
        lr = get_learning_rate(0)
        i = 0
        for data in mod:
            state0 , action, reward, state, done = data
            bestQ = np.amax(qTable[state])
            qTable[state0 + (action,)] += lr* (reward + gamma* bestQ - qTable[state0 + (action,)])
            if done == True:
                i +=1
                lr = get_learning_rate(i)
    print("Model Setup Completed")

     # play game
    env.set_view(True)
    rewardCount = 0   

    for e in range(9999999):
        observation = env.reset()
        state0 = makeBucket(observation)
        totalReward = 0 
        for steps in range(maxSteps):
            action =chooseAction(state0 ,0.01)
            observation, reward, done, _  = env.step(action)
            state = makeBucket(observation)
            totalReward += reward
            bestQ  = np.amax(qTable[state])
            qTable[state0 + (action , )] += lr * (reward + gamma* (bestQ) - qTable[state0 + (action,)])
            state0 = state

            env.render()
            if done or steps >= maxSteps -1:
                print("Episode %d finished after %i time steps with total reward = %f."
                      % (e, steps, totalReward))            
                break
        
        if totalReward >=  1000:
            rewardCount +=1
        else:
            rewardCount = 0
    
    lr = get_learning_rate(i + e)












# setting up a simulated environment
env = gym.make("Pyrace-v0")

#setting up the dimensions for the q table and the q tablr
buckets = tuple((env.observation_space.high + np.ones(env.observation_space.shape)).astype(int))
actions = env.action_space.n
stateBounds = list(zip(env.observation_space.low, env.observation_space.high))
qTable = np.zeros(buckets + (actions,), dtype=float)

decayFactor = np.prod(buckets, dtype=float) / 10.0

print(decayFactor)
#start the learning process

#To train a new model un comment the next line
learn(decayFactor=decayFactor, simulate=False, EPISODES=15000, maxSteps=2000)

#To test a pretrained model
# test_model('map-2021-07-08 13-12-5000.npz', maxSteps=5000)
# test_model('map4-2021-07-04 04-36-5000.npy', maxSteps=5000)