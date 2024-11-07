import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def center_increasing_sequences(lst):
    sequences = []
    current_sequence = [lst[0]]

    for i in range(1, len(lst)):
        if lst[i] > lst[i - 1]:
            current_sequence.append(lst[i])
        else:
            sequences.append(current_sequence)
            current_sequence = [lst[i]]
    sequences.append(current_sequence)

    centered_sequences = []
    for seq in sequences:
        mean = sum(seq) / len(seq)
        centered_seq = [x - mean for x in seq]
        centered_sequences.extend(centered_seq)

    return centered_sequences


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

augment = []

# for i in range(len(transformedArray)):
#     if transformedArray[0][i] not in all_species:
#         print(transformedArray[0][i])

for x in range(len(transformedArray)):
    if all_species[x] in primary:  
        augment.append(1)
    else:
        augment.append(-1)

trophic_levels = np.linalg.solve(transformedArray, augment)

# Given lists
node_names = all_species
y_positions = trophic_levels

sorted_with_indexes = sorted(enumerate(trophic_levels), key=lambda x: x[1])
xpos=[]
sorted_list = [value for index, value in sorted_with_indexes]
tlevelcounter = 2
xposcounter = 0

for i in range(len(sorted_list)):
    if tlevelcounter>sorted_list[i]:
        xpos.append(xposcounter)
        xposcounter+=0.25
    else:
        tlevelcounter+=0.2
        xposcounter=0
        xpos.append(xposcounter)
        xposcounter+=0.25
        
xpos = center_increasing_sequences(xpos)

for i in range(len(y_positions)):
    if y_positions[i]>1:
        y_positions[i]-=0.7

sorted_indexes = [index for index, value in sorted_with_indexes]
xposreal=[]
for i in range(len(sorted_indexes)):
    xposreal.append(xpos[sorted_indexes.index(i)])

# Make a random set of positions
pos = nx.random_layout(foodwebGraph)
# Update the y-coordinates based on y_positions
for name, y,x in zip(node_names, y_positions,xposreal):
    pos[name] = (x,y*10)  # Set the y-coordinate to the specified value
# Draw the graph with the modified positions
nx.draw(foodwebGraph, pos, with_labels=True, node_color='skyblue', node_size=800, font_size=15)
plt.show()



