import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

dataset_path_train = os.listdir('dataset/train')

label_types = os.listdir('dataset/train')
print(label_types)

####    PREPARING TRAINING DATA ####

rooms = []

for item in dataset_path_train:
    # Get all the file names
    all_rooms = os.listdir('dataset/train' + '/' + item)

    # Add them to the list rooms
    for room in all_rooms:
        rooms.append((item, str('dataset/train' + '/' + item) + '/' + room))

# Build a dataframe
train_df = pd.DataFrame(data=rooms, columns=['tag', 'video_name'])
print(train_df.head())
print(train_df.tail())

df_train = train_df.loc[:,['video_name', 'tag']]
df_train.to_csv('train.csv')

####  PREPARING TEST DATA ####

dataset_path_test = os.listdir('dataset/test')

room_types = os.listdir('dataset/test')
print('Types of activities found: ', len(dataset_path_test))

rooms = []

for item in dataset_path_test:
    # Get all the file names
    all_rooms = os.listdir('dataset/test' + '/' + item)

    # Add them to the list rooms
    for room in all_rooms:
        rooms.append((item, str('dataset/test' + '/' + item) + '/' + room))

# Build a dataframe
test_df = pd.DataFrame(data=rooms, columns=['tag', 'video_name'])
print(test_df.head())
print(test_df.tail())

df_test = test_df.loc[:,['video_name', 'tag']]
df_test.to_csv('test.csv')

