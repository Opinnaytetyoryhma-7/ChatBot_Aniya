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
from datetime import datetime

#Defined the chatbot's name
#Enables timestamp
#Uses GPU if available
bot_name = 'Aniya'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#Loads intents.json, which contains chatbot responses
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)


def load_model():
    #Loads the trained model from data.pth
    FILE = "data.pth"
    data = torch.load(FILE, map_location=device)

    #Recreates the Neural Network model using the stored parameters
    #Loads trained weights, model_state, into the model
    #Sets the model to evaluation mode, eval(), disabling training behaviors
    #Extracts metadata from the saved data.pth
    #These values are used to rebuild the model
    model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
    model.load_state_dict(data["model_state"])
    model.eval()

    return model, data["all_words"], data["tags"]

model, all_words, tags = load_model()

def get_response(raw_sentence):

    #Tokenizes the input
    #Converts it into a bag-of-words vector
    #Reshapes it into a format suitable for the model
    #Converts it into a PyTorch tensor for processing
    #Save original input
    sentence = tokenize(raw_sentence)
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

    return tag, prob.item()

# Track user messages
# Save to log only if it's "unknown"
def log_unknown_input(sentence):
    with open("chat_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] USER: {sentence.strip()} | INTENT: unknown\n")

#creating a ticket
def handle_ticket(sentence):
    print(f"{bot_name}: Voisitko kuvailla ongelmasi ja jättää yhteystietosi, kiitos!")
    ticket = input("Sinä: ")

    with open("tickets.txt", "a", encoding="utf-8") as ticket_file:
        ticket_file.write(f"[{timestamp}]\nCONTACT REQUEST:\nMessage: {sentence.strip()}\nUser Info: {ticket.strip()}\n---\n")

    print(f"{bot_name}: Kiitos! Olemme tallentaneet tietosi. Palaamme asiaan heti kun pystymme!")

def chat_loop():

    #Starts an infinite loop that waits for user input
    #Exits when the user types quit
    print("Hei! Miten voin olla avuksi? :) Jos haluat lopettaa keskustelun, kirjoita stop.")

    while True:
        raw_sentence = input('Sinä: ')
        if raw_sentence == "stop":
            break

        tag, prob = get_response(raw_sentence)

        #If the probability is above 75%, the bot picks a response from intents.json
        #Otherwise, it responds with Pahoittelut, nyt en ymmärtänyt. Haluatko jättää yhteydenottopyynnön?
        if prob > 0.75:
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    print(f"{bot_name}: {random.choice(intent['responses'])}")
                    if tag == "goodbye":
                        return
                    elif tag == "problem":
                        if tag == "ticket_asking":
                            handle_ticket(raw_sentence)
                            return
                        if tag == "goodbye":
                            return
                    break
        else:
            print(f"{bot_name}: Pahoittelut, nyt en ymmärtänyt. Haluatko jättää yhteydenottopyynnön?")
            log_unknown_input(raw_sentence)

            follow = input("Sinä: ").lower()
            if follow in ["kyllä", "joo", "haluan", "ok", "juu"]:
                handle_ticket(raw_sentence)
            else:
                print(f"{bot_name}: Selvä juttu! Hyvää päivänjatkoa!")
            return
        
if __name__ == "__main__":
    chat_loop()