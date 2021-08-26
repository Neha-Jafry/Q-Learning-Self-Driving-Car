from matplotlib import pyplot as plt 
import csv
import numpy as np


data_inf = ['2021-07-31 20-56-inference-1.csv', '2021-07-31 21-03-inference-2.csv', '2021-07-31 21-09-inference-3.csv', '2021-07-31 21-18-inference-4.csv']

data = ['map-2021-07-30 18-35-30000.csv','map2-2021-07-30 05-51-30000.csv', 'map3-2021-07-29 05-18-30000.csv','map4-2021-07-30 00-57-30000.csv']


for map in range(4):

    with open(data_inf[map]) as file:
        reader = csv.reader(file)
        reward_list =[]
        for row in reader:
            if row!=[]:
                for i in range(len(row)):
                    reward_list.append(float(row[i]))


        plt.figure(figsize=(15, 8))
        plt.plot(range(len(reward_list)+1)[1:], reward_list, color='red', marker='')
        plt.xlabel('Episode', fontsize=26)
        plt.ylabel('Reward', fontsize=26)
        plt.title('Reward per Episode Map ' + str(map+1) + ' Inference', fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.show()

    if data[map]!='':
        with open(data[map]) as file:
            reader = csv.reader(file)
            i = 0
            reward_list = []
            reward_list_5000 = []
            for row in reader:
                if row != []:
                    d = np.array(row)
                    print(type(d[0]))
                    d = d.astype(np.float)
                    if i == 0:
                        x = 0
                        while x < 3000:
                            reward_list.append(d[x:x+10].sum()/10)
                            x+=10
                        i += 1
                    elif i == 1:
                        reward_list_5000 = d
                    # print(len(reward_list), len(reward_list_5000))
        
        plt.figure(figsize=(15, 8))
        plt.plot(range(len(reward_list)+1)[1:], reward_list, color='red', marker='')
        plt.xlabel('Episode (x100)', fontsize=26)
        plt.ylabel('Avg Reward', fontsize=26)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title('Avg Reward per 100 Episode Map ' + str(map+1) + ' Training', fontsize=30)
        plt.show()

        plt.figure(figsize=(15, 8))
        plt.plot(range(len(reward_list_5000)+1)[1:], reward_list_5000, color='red', marker='')
        plt.xlabel('Episode (x1000)', fontsize=26)
        plt.ylabel('Avg Reward', fontsize=26)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title('Avg Reward per 5000 Episodes Map ' + str(map+1) + ' Training', fontsize=30)
        plt.show()