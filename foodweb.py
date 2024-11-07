import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pyvis.network import Network

#Reads the data in 
foodwebData = pd.read_csv('GulfoMexico.csv')
columns = list(foodwebData.columns)
all_species = []

foodwebArray = foodwebData.to_numpy()

foodwebGraph = nx.DiGraph()
visualizedGraph = nx.DiGraph()
#creates the graph by adding edges
for y in range(1, len(columns)):
    for x in range(len(foodwebArray)):
        if(foodwebArray[x][y] != 0 and foodwebArray[x][0] != columns[y]):
            foodwebGraph.add_edge(foodwebArray[x][0], columns[y], weight=foodwebArray[x][y])
            visualizedGraph.add_edge(foodwebArray[x][0], columns[y], weight=foodwebArray[x][y])

nx.draw_circular(foodwebGraph, with_labels=True)

#idk wtf this is 
editable = Network(directed=True)
editable.from_nx(foodwebGraph)
editable.toggle_physics(False)
editable.save_graph('foodwebgraph.html')

#Finds entries in first column on left
for row in foodwebArray:
    all_species.append(row[0])

#Finds primary producers by seeing which left side species are not in the top row
primary = []
for species in all_species:
    if species not in columns:
        primary.append(species)
        
#For each primary species, create a list of zeroes with a 1 entry at the index location of the primary species
#in the left side column
for species in primary:
    column_values = []
    for i in range(len(all_species)):
        if i == all_species.index(species):
            column_values.append(1)
        else:
            column_values.append(0)
    #Insert this list as a column into the topcolumns of the dataframe at the same index 
    #as the species is on the leftside column of the dataframe. Heading = species. 
    foodwebData.insert(loc = all_species.index(species)+1, column = species,  value = column_values)

for x in foodwebData.index:
    for y in range(1, len(foodwebData.columns)):
        if x + 1 == y and foodwebData.columns[y] not in primary:
            foodwebData.loc[x, foodwebData.columns[y]] -= 1

foodwebData.drop(columns=foodwebData.columns[0], axis=1, inplace=True)
foodwebData = foodwebData.T
transformedArray = foodwebData.to_numpy()

#plt.show()
augment = []
for x in range(len(transformedArray)):
    if all_species[x] in primary:  
        augment.append(1)
    else:
        augment.append(-1)
print(augment)

trophic_levels = np.linalg.solve(transformedArray, augment)