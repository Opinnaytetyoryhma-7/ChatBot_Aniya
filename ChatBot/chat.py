#Random: selects random responses for variety
#Json: loads the chatbot’s predefined questions and responses
#Torch: loads and runs the trained Neural Network model
#NeuralNet: imports the chatbot’s model from model.py
#bag_of_words, tokenize: preprocess user input
import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

#Uses GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#Loads intents.json, which contains chatbot responses
with open('intents.json', 'r') as f:
    intents = json.load(f)

#Loads the trained model from data.pth
FILE = "data.pth"
data = torch.load(FILE, map_location=device)

#Extracts metadata from the saved data.pth
#These values are used to rebuild the model
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

#Recreates the Neural Network model using the stored parameters
#Loads trained weights, model_state, into the model
#Sets the model to evaluation mode, eval(), disabling training behaviors
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

#Defined the chatbot's name
#Starts an infinite loop that waits for user input
#Exits when the user types quit
bot_name = 'Aniya'
print("Hei! Miten voin olla avuksi? :) Jos haluat lopettaa keskustelun, kirjoita stop.")
while True:
    sentence = input('You: ')
    if sentence == "stop":
        break

    #Tokenizes the input
    #Converts it into a bag-of-words vector
    #Reshapes it into a format suitable for the model
    #Converts it into a PyTorch tensor for processing
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    #Passes input through the model to get predictions
    #Finds the intent with the highest probability
    #Retrieves the corresponding tag from the tags list
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    #Applies softmax to convert model output into probabilities
    #Retrieves the probability of the predicted intent
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    #If the probability is above 75%, the bot picks a response from intents.json
    #Otherwise, it responds with Pahoittelut, nyt en ymmärtänyt. Haluatko jättää yhteydenottopyynnön?
    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                print(f"{bot_name}: {random.choice(intent['responses'])}")
    else:
        print(f"{bot_name}: Pahoittelut, nyt en ymmärtänyt. Haluatko jättää yhteydenottopyynnön?")