# Trophic Centrality
import networkx as nx
import pandas as pd
import numpy as np


#This code below reads from the file and finds trophic levels for our creatures. 

#Format of the file is as follows: Look at a specific column. The topmost entry of the column is species X. For every numerical entry below that, the number represents what percent 
#the row species comprises of the column species diet
foodwebData = pd.read_csv('GulfoMexico.csv') #Saved as a pandas Dataframe

columns = list(foodwebData.columns)
all_species = []

foodwebArray = foodwebData.to_numpy()
foodwebGraph = nx.DiGraph()

#Adds all edges from the dataframe, with specified weights.   
for y in range(1, len(columns)):
    for x in range(len(foodwebArray)):
        if foodwebArray[x][y] != 0 and foodwebArray[x][0] != columns[y]:
            foodwebGraph.add_edge(foodwebArray[x][0], columns[y], weight=foodwebArray[x][y])

#Defines a reversed food web, useful for calculating the prey species of a given species X, since a directed graph was created.
reversedfoodWeb = foodwebGraph.reverse()

#Since some species, such as Detritus or primary producers eat nothing, these columns are not included. 
#These columns must be found and the manually added. 
#Finds all species
for row in foodwebArray:
    all_species.append(row[0])

#Finds all species that are in rows but not in columns. These are our primary producers, or trophic level 1. 
primary = []
for species in all_species:
    if species not in columns:
        primary.append(species)

#For every s
for species in primary:
    column_values = []
    for i in range(len(all_species)):
        if i == all_species.index(species):
            column_values.append(1)
        else:
            column_values.append(0)
    foodwebData.insert(loc=all_species.index(species) + 1, column=species, value=column_values)

#This manipulates the existing dataframe that we have and turns it into a matrix that can be row reduced
for x in foodwebData.index:
    for y in range(1, len(foodwebData.columns)):
        if x + 1 == y and foodwebData.columns[y] not in primary:
            #We subtract one to convert each column into an expression of trophic level relations
            #More detail in our paper
            foodwebData.loc[x, foodwebData.columns[y]] -= 1

#Drops the first column of names, so we have only numbers, and transposes the matrix. 
foodwebData.drop(columns=foodwebData.columns[0], axis=1, inplace=True)
foodwebData = foodwebData.T
transformedArray = foodwebData.to_numpy()

augment = []

#Because of the way each equation works out, for primary producers, their trophic level is one. 
#For all other species, their linear expression modelled by matrix coefficients in their rows will sum to -1
for x in range(len(transformedArray)):
    if all_species[x] in primary:  
        augment.append(1)
    else:
        augment.append(-1)

#Row reduce and solve the matrix. This is a list that holds every trophic level for each species. 
trophic_levels = np.linalg.solve(transformedArray, augment)



### Beginning of Centrality Calculations

#Here we initialize a dictionary for trophic levels
trophic_level_dict = {species: level for species, level in zip(all_species, trophic_levels)}

#Here we initalize a dictionary where I'll store all the centrality scores for later.
centrality_measure = {species: 0 for species in all_species}

for prey in reversedfoodWeb.nodes:

    #Creates a list of all the species that eat the one we are iterating over
    predators = list(reversedfoodWeb.predecessors(prey))

    #If it doesn't have any predators, we can skip it
    if not predators:
        continue  
    
    #For all the predators of the animal we are iterating over, we are summing the weights of the predator-prey interaction for our
    #running total
    total_weight = sum(reversedfoodWeb[predator][prey]['weight'] for predator in predators)
    


    prey_centrality = 0
    for predator in predators:
        original_weight = reversedfoodWeb[predator][prey]['weight']

        trophic_difference = trophic_level_dict[prey] - trophic_level_dict[predator]

        #Adjust the weight using the 10% rule due to trophic differences

        adjusted_weight = original_weight * (10 ** trophic_difference)

        #To normalize the weight in order to scale the contributions accordingly, we divide the adjusted weight by the total weight.
        
        normalized_weight = adjusted_weight / total_weight
        prey_centrality += normalized_weight
    

    for predator in predators:
        centrality_measure[predator] += prey_centrality

#Now we do the same thing for the predators

for predator in foodwebGraph.nodes:

    #We use foodwebgraph instead of the reversed version, that way we can get the prey from the predators

    preys = list(foodwebGraph.predecessors(predator))

    #If the animal has no prey, we can skip this step.

    if not preys:
        continue

    for prey in preys:
        total_predation = sum(foodwebGraph[prey][pred]['weight'] for pred in foodwebGraph.successors(prey))
        if total_predation == 0:
            continue

        #Adjust prey's contribution based on the trophic level difference
        #Same idea as above with the predators

        trophic_difference = trophic_level_dict[predator] - trophic_level_dict[prey]

        adjusted_weight = (foodwebGraph[prey][predator]['weight'] / total_predation) * (10 ** (-trophic_difference))

        centrality_measure[predator] += adjusted_weight

#Sort the values so we can get the most important species, and keep 3 of the most important as our contenders

keystone_species = sorted(centrality_measure, key=centrality_measure.get, reverse=True)[:3]

print("Keystone species:", keystone_species)
#print("Trophic centrality scores:", centrality_measure)
