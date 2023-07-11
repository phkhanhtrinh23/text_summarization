"""main.py: This script summarizes text provided in a PDF file."""

import os
import nltk
import pytesseract
import re
from pdf2image import convert_from_path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer
from PIL import Image
from transformers import pipeline
import textwrap
nltk.download("stopwords")
nltk.download("punkt")


def extractOCR(file):
    pages = convert_from_path(file, 500)

    image_counter = 1
    for page in pages:
        filename = "page_" + str(image_counter) + ".jpg"
        page.save(filename, "JPEG")
        image_counter = image_counter + 1

    limit = image_counter-1
    text = ""
    for i in range(1, limit + 1):
        filename = "page_" + str(i) + ".jpg"
        page = str(((pytesseract.image_to_string(Image.open(filename)))))
        page = page.replace("-\n", "")
        text += page
        os.remove(filename)
    return text


def summarize_custom(text):
    # Process text by removing numbers and unrecognized punctuation
    processedText = re.sub("’", "'", text)
    processedText = re.sub("[^a-zA-Z' ]+", " ", processedText)
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(processedText)

    # Normalize words with Porter stemming and build word frequency table
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        elif stemmer.stem(word) in freqTable:
            freqTable[stemmer.stem(word)] += 1
        else:
            freqTable[stemmer.stem(word)] = 1

    # Normalize every sentence in the text
    sentences = sent_tokenize(text)
    stemmedSentences = []
    sentenceValue = dict()
    for sentence in sentences:
        stemmedSentence = []
        for word in sentence.lower().split():
            stemmedSentence.append(stemmer.stem(word))
        stemmedSentences.append(stemmedSentence)

    # Calculate value of every normalized sentence based on word frequency table
    # [:12] helps to save space
    for num in range(len(stemmedSentences)):
        for wordValue in freqTable:
            if wordValue in stemmedSentences[num]:
                if sentences[num][:12] in sentenceValue:
                    sentenceValue[sentences[num][:12]] += freqTable.get(wordValue)
                else:
                    sentenceValue[sentences[num][:12]] = freqTable.get(wordValue)

    # Determine average value of a sentence in the text
    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue.get(sentence)

    average = int(sumValues / len(sentenceValue))

    # Create summary of text using sentences that exceed the average value by some factor
    # This factor can be adjusted to reduce/expand the length of the summary
    summary = ""
    for sentence in sentences:
            if sentence[:12] in sentenceValue and sentenceValue[sentence[:12]] > (3.0 * average):
                summary += " " + " ".join(sentence.split())

    # Process the text in summary and write it to a new file
    summary = re.sub("’", "'", summary)
    summary = re.sub("[^a-zA-Z0-9'\"():;,.!?— ]+", " ", summary)
    summaryText = open(fileName + "Summary.txt", "w")
    summaryText.write(summary)
    summaryText.close()

def summarize_model(text, summarizer):
    # Process text by removing numbers and unrecognized punctuation
    processedText = re.sub("’", "'", text)
    processedText = re.sub("[^a-zA-Z' ]+", " ", processedText)
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(processedText)
    temp = []

    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        else:
            temp += [word]

    # Split text into chunks
    n = 500
    chunks = [temp[i:i+n] for i in range(0, len(temp), n)]
    summary = ""

    for chunk in chunks:
        text = " ".join(chunk)
        res = summarizer(text, max_length=140, min_length=40, do_sample=False)
        res = str(res[0]["summary_text"])
        if len(summary) == 0:
            summary += res.capitalize() 
        elif res[-1] == ".":
            summary += " " + res.capitalize()
        else:
            summary += ". " + res.capitalize()

    # Process the text in summary and write it to a new file
    summary = re.sub("’", "'", summary)
    summary = re.sub("[^a-zA-Z0-9'\"():;,.!?— ]+", " ", summary)
    summaryText = open(fileName + "Summary.txt", "w")
    summaryText.write(summary)
    summaryText.close()

# Scan user input for PDF file name
print("What is the name of the PDF?")
fileName = input("(Without .pdf file extension)\n")
pdfFileName = fileName + ".pdf"
option = input("Custom extraction or Model extraction? (custom / model)\n")

if option == "custom":
    text = extractOCR(pdfFileName)
    summarize_custom(text)
elif option == "model":
    text = extractOCR(pdfFileName)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summarize_model(text, summarizer)
else:
    print("Not a valid option!")
