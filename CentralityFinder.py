# Trophic Centrality

import networkx as nx
import pandas as pd
import numpy as np

foodwebData = pd.read_csv('GulfoMexico.csv')
columns = list(foodwebData.columns)
all_species = []

foodwebArray = foodwebData.to_numpy()
foodwebGraph = nx.DiGraph()

for y in range(1, len(columns)):
    for x in range(len(foodwebArray)):
        if foodwebArray[x][y] != 0 and foodwebArray[x][0] != columns[y]:
            foodwebGraph.add_edge(foodwebArray[x][0], columns[y], weight=foodwebArray[x][y])

reversedfoodWeb = foodwebGraph.reverse()

for row in foodwebArray:
    all_species.append(row[0])

primary = []
for species in all_species:
    if species not in columns:
        primary.append(species)

for species in primary:
    column_values = []
    for i in range(len(all_species)):
        if i == all_species.index(species):
            column_values.append(1)
        else:
            column_values.append(0)
    foodwebData.insert(loc=all_species.index(species) + 1, column=species, value=column_values)

for x in foodwebData.index:
    for y in range(1, len(foodwebData.columns)):
        if x + 1 == y and foodwebData.columns[y] not in primary:
            foodwebData.loc[x, foodwebData.columns[y]] -= 1

foodwebData.drop(columns=foodwebData.columns[0], axis=1, inplace=True)
foodwebData = foodwebData.T
transformedArray = foodwebData.to_numpy()

augment = []


for x in range(len(transformedArray)):
    if all_species[x] in primary:  
        augment.append(1)
    else:
        augment.append(-1)

trophic_levels = np.linalg.solve(transformedArray, augment)

# Dictionary for trophic levels
trophic_level_dict = {species: level for species, level in zip(all_species, trophic_levels)}

# Dictionary for centrality measure
centrality_measure = {species: 0 for species in all_species}

for prey in reversedfoodWeb.nodes:
    predators = list(reversedfoodWeb.predecessors(prey))
    
    if not predators:
        continue  
    

    total_weight = sum(reversedfoodWeb[predator][prey]['weight'] for predator in predators)
    
    max_trophic_predator = max(predators, key=lambda predator: trophic_level_dict[predator])
    max_trophic_level = trophic_level_dict[max_trophic_predator]


    prey_centrality = 0
    for predator in predators:
        original_weight = reversedfoodWeb[predator][prey]['weight']
        trophic_difference = max_trophic_level - trophic_level_dict[predator]
        adjusted_weight = original_weight * (10 ** trophic_difference)
        
        normalized_weight = adjusted_weight / total_weight
        prey_centrality += normalized_weight
    

    for predator in predators:
        centrality_measure[predator] += prey_centrality

keystone_species = max(centrality_measure, key=centrality_measure.get)
print("Keystone species:", keystone_species)
#print("Trophic centrality scores:", centrality_measure)
