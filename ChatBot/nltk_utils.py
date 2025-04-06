#nltk is used for tokenization
#numpy helps with numerical operations
#PorterStemmer is a stemming algorithm that reduces words to their root form
import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer
stemmer=PorterStemmer()

#Splits a sentence into words/tokens
def tokenize(sentence):
    return nltk.word_tokenize(sentence)

#Reduces a word to root form and converts to lowercase
def stem(word):
    return stemmer.stem(word.lower())

#Converts a tokenized sentence into a numerical vector
#1. Stems each word in sentence
#2. Creates a zero vector
#3. Sets 1 where words match all_words
def bag_of_words(tokenized_sentence, all_words):
    """
    sentence = ["hello", "how", "are", "you]
    words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
    bog = [   0,      1,     0,    1,     0,      0,       0  ]
    """
    tokenized_sentence = [stem(w) for w in tokenized_sentence]

    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    return bag