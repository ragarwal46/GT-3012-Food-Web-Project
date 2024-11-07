import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout


foodwebData = pd.read_csv('GulfoMexico.csv')
columns = list(foodwebData.columns)

foodwebArray = foodwebData.to_numpy()
foodwebGraph = nx.Graph()

for y in range(1, len(columns)):
    for x in range(len(foodwebArray)):
        if(foodwebArray[x][y] != 0):
            foodwebGraph.add_edge(foodwebArray[x][0], columns[y], weight=foodwebArray[x][y])
print(foodwebGraph["Flatfish"])
nx.draw(foodwebGraph, with_labels=True)
plt.show()