import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer
from transformers import pipeline
import nltk
nltk.download("stopwords")
nltk.download("punkt")


class TextSummarization:
    def __init__(self, model_name_or_path: str = "facebook/bart-large-cnn"):
        self.model_name_or_path = model_name_or_path
        self.summarizer = pipeline("summarization", model=self.model_name_or_path)


    def summarize_custom(self, text):
        # Process text by removing numbers and unrecognized punctuation
        processedText = re.sub("’", "'", text)
        processedText = re.sub("[^a-zA-Z' ]+", "", processedText)
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
            if sentence[:12] in sentenceValue and sentenceValue[sentence[:12]] > (1.0 * average):
                summary += " " + " ".join(sentence.split())

        # Post-process the text in summary
        summary = re.sub("’", "'", summary)
        summary = re.sub("[^a-zA-Z0-9'\"():;,.!?— ]+", "", summary)

        return summary


    def summarize_model(self, text):
        # Process text by removing numbers and unrecognized punctuation
        processedText = re.sub("’", "'", text)
        processedText = re.sub("[^a-zA-Z' ]+", "", processedText)
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
            res = self.summarizer(text, max_length=140, min_length=40, do_sample=False)
            res = str(res[0]["summary_text"])
            if len(summary) == 0:
                summary += res.capitalize() 
            elif res[-1] == ".":
                summary += " " + res.capitalize()
            else:
                summary += ". " + res.capitalize()

        # Post-process the text in summary
        summary = re.sub("’", "'", summary)
        summary = re.sub("[^a-zA-Z0-9'\"():;,.!?— ]+", "", summary)

        return summary