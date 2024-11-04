import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

foodwebData = pd.read_csv('GulfoMexico.csv')
foodwebArray = foodwebData.to_numpy()
species = list(foodwebData.iloc[:, 0])
foodwebGraph = nx.Graph()

for x in range(len(foodwebArray)):
    for y in range(1, len(foodwebArray[x])):
        if(foodwebArray[x][y] != 0):
            foodwebGraph.add_edge(x, y-1, weight=foodwebArray[x][y])

nx.draw(foodwebGraph,with_labels=True)
plt.show()
