from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
from flask.templating import render_template
import tensorflow as tf
import numpy as np
import os
import csv
import tensorflow
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import sklearn.preprocessing
from sklearn.preprocessing import LabelBinarizer
import re
import pickle
from itertools import product

app = Flask(__name__)
############################################################################################################
CHARS_MAPPING = {
    "a": ("a", "*", "@"),
    "i": ("i", "*", "l", "1", "!"),
    "o": ("o", "*", "0",),
    "u": ("u", "*", "v"),
    "v": ("v", "*", "u"),
    "l": ("1"),
    "h": ("#"),
    "e": ("e", "*"),
    "s": ("s", "$"),
    "t": ("t", "7", "%"),
}

with open('outfile', 'rb') as fp:
    badlist = pickle.load(fp)


for i in range(len(badlist)):
    if len(badlist[i]) < 20:
        combos = [
            (char,
             ) if char not in CHARS_MAPPING else CHARS_MAPPING[char]
            for char in iter(badlist[i])
        ]
        leet = ["".join(pattern) for pattern in product(*combos)]
        for j in range(len(leet)):
            badlist.append(leet[j])


def censor(tweet):
    originaltweet = tweet.split()
    tweet = re.sub(r'[^\w\s]', '', tweet)
    tweet_list = tweet.lower().split()
    for i in range(len(tweet_list)):
        try:
            temp = badlist.index(tweet_list[i])
            originaltweet[i] = '*' * len(originaltweet[i])
        except:
            pass
    censor_string = ' '.join(originaltweet)
    return censor_string
############################################################################################################################################################
def prep_for_model(tweet):
    vocab_size = 10000
    embedding_dim = 16
    max_length = 100
    trunc_type='post'
    padding_type='post'
    oov_tok = "<OOV>"
    training_size = 20000

    with open('train_tweets.txt') as file:
        train_tweets = file.readlines()
        file.close()
    with open('test_tweets.txt') as file:
        test_tweets = file.readlines()
        file.close()
    with open('train_labels.txt') as file:
        train_labels = file.readlines()
        file.close()
    with open('test_labels.txt') as file:
        test_labels = file.readlines()
        file.close()
    print(len(train_tweets))
    tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
    tokenizer.fit_on_texts(train_tweets)

    word_index = tokenizer.word_index

    train_sequences = tokenizer.texts_to_sequences(train_tweets)
    train_padded = pad_sequences(train_sequences, maxlen = max_length, 
                             padding = padding_type, 
                             truncating = trunc_type)


    test_sequences = tokenizer.texts_to_sequences(test_tweets)
    test_padded = pad_sequences(test_sequences, maxlen=max_length,
                            padding=padding_type,
                            truncating=trunc_type)

    train_padded = np.array(train_padded)
    train_labels = np.array(train_labels)
    test_padded = np.array(test_padded)
    test_labels = np.array(test_labels)

    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(24, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
        ])
    tweets = [tweet] 
    sequences = tokenizer.texts_to_sequences(tweets)
    padded = pad_sequences(sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)

    model.load_weights("model.h5")
    prediction = model.predict(padded)
    print(prediction)
    return prediction


###################################################################################################################################################################
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/black-list")
def black_list():
    return render_template("BlackList.html")

@app.route("/real-world")
def real_world():
    return render_template("RealWorld.html")

@app.route("/handling", methods=['POST'])
def handling():
    tweet = request.form['tweet']
    user_name = request.form['user_name']
    censored_string = censor(tweet)
    model_prediction = prep_for_model(tweet)
    threshold = 0.90
    if model_prediction >= threshold:
        cleared = True
    else:
        cleared = False
    return render_template("handling.html", user_name=user_name, censored_string=censored_string, model_prediction  = model_prediction, cleared = cleared)



@app.route("/censored")
def censored():
    return 5

@app.route("/clear")
def clear():
    return 6
if __name__ == "__main__":
    app.run(debug=True)
