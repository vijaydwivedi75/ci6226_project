from flask import Flask
import os
from os.path import isfile, join
import re
import string
from nltk.stem.porter import *
from flask import Flask, render_template, request, redirect, url_for
import time
import pickle
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

app = Flask(__name__)


##########################
def preprocess_keywords(keywords):
    modified_list = []
    for keyword in keywords:
        # Removing punctuations
        punctuations = '''!@#$%^&*()-_=+'`~ ":;|/.,?[]{}<>'''
        for char in keyword.lower():
            if char in punctuations:
                keyword = keyword.replace(char, "")

        # Lowercasing the token
        keyword = keyword.lower()

        # Stemming
        stemmer = PorterStemmer()
        keyword = stemmer.stem(keyword)

        modified_list.append(keyword)
    return modified_list


def list_all_files(path='HillaryEmails'):
    root = join(os.getcwd(), path)
    file_paths = [join(root, file) for file in os.listdir(path) if isfile(join(path, file))]
    return file_paths


def read_file(file_path):
    with open(file_path, 'r', encoding="utf8") as file:
        content = file.read()
        content = content.replace("\n", " ")  # removing \n and replacing with space
        content = content.replace("\t", " ")  # removing \t and replacing with space
        return content


def tokenize(file_content, file_path):
    return [(x, file_path) for x in re.split(r"([.,!?]+)?\s+", file_content) if x]


def linguistic_clean(token_file_path_pairs):
    modified_list = []
    for pair in token_file_path_pairs:

        token, file_path = pair

        # Removing punctuations
        punctuations = '''!@#$%^&*()-_=+'`~ ":;|/.,?[]{}<>'''
        for char in token.lower():
            if char in punctuations:
                token = token.replace(char, "")

                # Lowercasing the token
        token = token.lower()

        # Stemming
        stemmer = PorterStemmer()
        token = stemmer.stem(token)

        modified_list.append((token, file_path))

    return modified_list


def sort_tokens(token_file_path_pairs):
    token_file_path_pairs.sort(key=lambda tup: tup[1])  # then by doc id (file paths)
    token_file_path_pairs.sort(key=lambda tup: tup[0])  # sorting first by token
    return token_file_path_pairs


def create_posting(sorted_token_file_path_pairs):
    inv_index, token_frequency = {}, {}
    for pair in sorted_token_file_path_pairs:
        token, file_path = pair
        if not token in inv_index:
            token_frequency[token] = 1
            inv_index[token] = [file_path]
        else:
            if file_path != inv_index[token][-1]:
                inv_index[token].append(file_path)
                token_frequency[token] += 1
    inv_index['__freq__'] = token_frequency
    return inv_index

def get_inv_index(data_path):
    all_pairs = []
    for file in list_all_files(data_path):
       all_text = read_file(file)
       all_pairs.extend(tokenize(all_text, file))

    inv_index = create_posting(sort_tokens(linguistic_clean(all_pairs)))
    return inv_index

##########################

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    data_path = r"C:/Users/emade/Downloads/ci6226_project-master/HillaryEmails/"
    stop_words = set(stopwords.words('english'))  # list of stop words from NLTK

    keyword_original = request.form['keywords']
    start_time = time.time()
    keyword_original = re.sub(' +', ' ', keyword_original)  # Removes unncessarcy spaces

    keywords = keyword_original.split(" ")
    # remove stop words
    keywords = [w for w in keywords if not w in stop_words]
    keywords = list(set(keywords))  # Remove repeated words.
    if '' in keywords:
        keywords.remove('')


    ## Checking and saving inverted index as oickle files ####
    inv_idx_pkl_name = "inv_index.pkl"
    if os.path.exists(inv_idx_pkl_name):
        pickle_in = open(inv_idx_pkl_name, "rb")
        inv_index = pickle.load(pickle_in)
    else:
        inv_index = get_inv_index(data_path)
        pickle_out = open(inv_idx_pkl_name, 'wb')
        pickle.dump(inv_index, pickle_out)
    # inv_idx_time = time.time() - start_time
    #print(f"Creating inverted indexes required: {inv_idx_time}")
    ###########################################################

    # Applying the same transformations on keywords,
    keywords = preprocess_keywords(keywords)
    preprocessed_keywords = " ".join(keywords)

    results = []
    try:
        # start_time = time.time()
        for i in range(len(keywords)):
            # getting the inverted index of keyword
            kwd_inv_idx = inv_index[keywords[i]]
            #print(f"Getting inverted index of {keywords[i]} required {time.time() - start_time}s")
            results.append([i.replace(data_path, "") for i in kwd_inv_idx])
            # start_time = time.time()

        # Applying intersection to get the ANDed results of keywords
        if len(results) > 1:
            result.sort(key=len)  # to sort according to the lengths of the lists inside
            result = set(results[0]).intersection(*results[1:])
            #print(f"Getting intersection required: {time.time() - start_time}")
        else:
            result = results[0]

        durtion = time.time() - start_time
        sent_result = f"Keyword(s):  {keyword_original}<br />"
        sent_result += f"Time required: {round(durtion,2)}s<br /> ***********************************<br /> "
        # sent_result +=f"{keyword_original} became --> {preprocessed_keywords} <br />"
        sent_result +=f"Keyword(s) appeared in the following text files: <br />"
        result = "<br />".join(result)
        sent_result += result
    except:
        sent_result = f"Sorry!! .. Keyowrd(s) not found in any of the documents!!"

    return render_template('index.html', result=sent_result)


if __name__ == "__main__":
    app.run(port=8050)
