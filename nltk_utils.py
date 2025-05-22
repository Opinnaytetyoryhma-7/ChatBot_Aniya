import nltk
import stanza
import numpy as np
from nltk.stem.snowball import SnowballStemmer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Initialize the stanza pipeline for Finnish
nlp = stanza.Pipeline('fi', processors='tokenize')

stemmer = SnowballStemmer("english")

# Replace nltk.word_tokenize with stanza tokenization
def tokenize(sentence):
    doc = nlp(sentence)
    return [word.text for sent in doc.sentences for word in sent.words]

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]

    bag = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx] = 1.0

    return bag