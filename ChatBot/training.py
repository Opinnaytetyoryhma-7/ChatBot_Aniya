#Loads required libraries for NLP and machine learning
#Opens and reads intents.json, which contains training data
#Nltk_utils.py contains helper functions for text processing
import json
from nltk_utils import tokenize, stem, bag_of_words
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from nltk_utils import bag_of_words, tokenize, stem
from model import NeuralNet

with open('intents.json', 'r') as f:
    intents = json.load(f)

#Loops through each intent in intents.json
#Tokenizes (splits words) each sentence
#Collects all words into all_words
#Pairs words with their respective tag in xy
all_words = []
tags = []
xy = []
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

#Ignores punctuation
#Stems words
#Removes deplicates and sorts words alphabetically
ignore_words = ['?', '!', '.', ',']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

#Converts each sentence into a "bag of words" representation "Hello, how are you?" → [0, 1, 0, 1, 1, 0, 0, ...]
#Maps each tag to a numerical label, which is needed for training
X_train = []
y_train = []
for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)

    label = tags.index(tag)
    y_train.append(label) #CrossEntropyLoss

X_train = np.array(X_train)
y_train = np.array(y_train)

#Converts X_train and y_train into PyTorch dataset for training
#Allows easy batch loading of data using DataLoader
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]
    
    def __len__(self):
        return self.n_samples
    
#Hyperparameters, defines key parameters like batch size, learning rate, and number of training epochs
batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(X_train [0])
learning_rate = 0.001
num_epochs = 1000

#Uses DataLoader to shuffle & load data in batches for training
#Moves the model to GPU if available for faster training
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

#Uses CrossEntropyLoss for classification
#Uses Adam optimizer, which is a popular optimization method for deep learning
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)

#Loops through num_epochs to train the model
#Computes loss: measures how well the model is predicting
#Optimizer Step: updates weights to minimize loss
#Prints loss every 100 epochs for monitoring training progress
for epoch in range(num_epochs) :
    for(words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(device, dtype=torch.long)

        #Forward Pass: feeds data into the model
        outputs = model(words)
        loss = criterion(outputs, labels)

        #Backward Pass: Adjusts model weights using gradient descent
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch +1) % 100 == 0:
        print(f'epoch {epoch+1}/{num_epochs}, loss={loss.item():.4f}')

print(f'final loss, loss={loss.item():.4f}')

#Saves the trained model parameters to data.pth file
#Stores all_words and tags for later use during prediction
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "all_words": all_words,
    "tags": tags

}

FILE = "data.pth"
torch.save(data, FILE)

print(f'Training complete. File saved to {FILE}')