#Torch is the PyTorch framework
#Torch.nn provides tools for defining neural networks
import torch
import torch.nn as nn

#Defines the NeuralNet class, inheriting from torch.nn.Module
#The constructor initializes the layers based on input_size, hidden_size, and num_classes
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()

        #l1: connects input to the hidden layer
        #l2: hidden layer for better learning.
        #l3: connects hidden layer to output.
        #ReLU: introduces non-linearity to help the model learn complex patterns
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    #Data passes through each layer sequentially
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        #no activation, PyTorch’s CrossEntropyLoss already applies softmax internally
        return out
        