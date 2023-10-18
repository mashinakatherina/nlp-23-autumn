import os
import re
from nltk import WordNetLemmatizer, SnowballStemmer
from pathlib import Path


def split_to_words(sentence):
    words = re.findall(r"(((?<=^)|(?<= )|(?<=\"))(\w+\-?)+\w*\.?)", sentence)
    words = list(map(lambda x: x[0], words))
    return words


def split_to_sentences(lines):
    counter = 0
    headers = {}
    for l in lines:
        l_split = l.split(": ", 1)
        if len(l_split) == 2:
            headers[l_split[0]] = l_split[1].replace("\n", " ")
            counter += 1
        elif l == "\n":
            counter += 1
        else:
            break
    raw = "".join(lines[counter:])
    raw = re.sub(r" {2,}|\t+", " ", raw)
    raw = re.sub(r"^ ", "", raw)
    raw = re.sub("\n{2,}", "\n", raw)
    raw = re.sub("\n ", "\n", raw)
    sentences = re.split(
        r"(((?<!\w\.\w.)(?<!\s\w\.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s(?=[A-Z]))|((?<![\,\-\:])\n(?=[A-Z]|\" )))", raw)[
                ::4]

    return headers, sentences


def process_file(filepath, result_filepath):
    wnl = WordNetLemmatizer()
    sst = SnowballStemmer("english")
    with open(filepath) as f:
        lines = f.readlines()
        headers, sentences = split_to_sentences(lines)
        all_words = []
        for s in sentences:
            all_words += split_to_words(s)
            all_words.append("\n")
        lemmatized = []
        stemmed = []
        original = []
        for w in all_words:
            w_processed = re.sub(r"[.!?,]$", "", w).lower()
            lemmatized.append(wnl.lemmatize(w_processed))
            stemmed.append(sst.stem(w_processed))
            original.append(w_processed)

    with open(result_filepath, "w") as f:
        for i in range(len(all_words)):
            if original[i] == "\n":
                print("", file=f)
            else:
                print(original[i], stemmed[i], lemmatized[i], sep="\t", file=f)


def process_topic(dirname, result_dirname, topic):
    topic_dir = os.path.join(dirname, topic)
    result_dir = os.path.join(result_dirname, topic)

    if not os.path.isdir(result_dir):
        Path(result_dir).mkdir(exist_ok=True, parents=True)

    files = os.listdir(topic_dir)
    for f in files:
        path = os.path.join(topic_dir, f)
        result_path = os.path.join(result_dir, f + ".tsv")
        process_file(path, result_path)
