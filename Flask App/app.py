from flask import Flask
import os
from os.path import isfile, join
import re
import string
from nltk.stem.porter import *
from flask import Flask, render_template, request, redirect, url_for
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


##########################

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def my_form_post():
    keyword_original = request.form['keywords']
    all_pairs = []
    data_path = r"C:/Users/Emad/Desktop/HillaryEmails/"
    for file in list_all_files(data_path)[23:26]:
       all_text = read_file(file)
       all_pairs.extend(tokenize(all_text, file))

    inv_index = create_posting(sort_tokens(linguistic_clean(all_pairs)))
    keyword = preprocess_keywords([keyword_original])[0]
    result = inv_index[keyword]
    result = [i.replace(data_path, "") for i in result]
    sent_result = f"{keyword_original} became --> {keyword} <br /> it appeared in the following text files: <br />"
    result = "<br />".join(result)
    sent_result += result
    # processed_text = text.upper()
    # return processed_text
    return render_template('index.html', result=sent_result)
    # return redirect(url_for('my_form_post'))

if __name__ == "__main__":
    app.run(port=8050)