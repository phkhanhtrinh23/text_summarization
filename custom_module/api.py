from flask import Flask, render_template, request, url_for, redirect
from base import TextSummarization
from threading import Thread
import pandas as pd
from utils import crawl_web, crawl_pdf, extract_OCR
import os

os.environ["TOKENIZERS_PARALLELISM"] = "1"

app = Flask(__name__)
obj = TextSummarization()

# Example
messages = [
        {
            'text_web': 'https://urlfromsciencewebsite.com',
            'text_pdf': 'https://urlfrompdfwebsite.com',
            'answer_web': [['This is a title from a website.', 'This is the summarization of the answer.']],
            'answer_pdf': [['This is a title from multiple pdf files.', 'This is the summarization of multiple pdf files.']],
        },
            ]

def process_web(obj, web_url, summary=[]):
    metadata = crawl_web(web_url)
    df = pd.DataFrame(metadata)
    print("Processing web information...")
    for title, text in zip(df["title"], df["text"]):
        print(f"Processing article: {title}")
        res = obj.summarize_custom(text)
        summary.append([title, res])
    summaryText = open("WebSummary.txt", "w")
    for title, res in summary:
        summaryText.write(title + "\n" + res + "\n\n")
    summaryText.close()
    print("Finish processing web information.")

def process_pdf(obj, pdf_url, summary=[]):
    metadata = crawl_pdf(pdf_url)
    df = pd.DataFrame(metadata)
    print("Processing multiple pdf file information...")
    for title, pdf_url in zip(df["title"], df["pdf_url"]):
        pdf_filename = os.path.basename(pdf_url)
        print(f"Processing a pdf file: {pdf_filename}")
        text = extract_OCR(f"./pdf/{pdf_filename}")
        res = obj.summarize_model(text)
        summary.append([title, res])
    summaryText = open("PDFSummary.txt", "w")
    for title, res in summary:
        summaryText.write(title + "\n" + res + "\n\n")
    summaryText.close()
    print("Finish processing multiple pdf files.")

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        web_url = request.form['text_web']
        pdf_url = request.form['text_pdf']

        summary_web, summary_pdf = [], []
        thread_web = Thread(target=process_web, args=(obj, web_url, summary_web, ))
        thread_pdf = Thread(target=process_pdf, args=(obj, pdf_url, summary_pdf, ))
        thread_web.start()
        thread_pdf.start()
        thread_web.join()
        thread_pdf.join()

        # summary_web = process_web(obj, web_url)
        # summary_pdf = process_pdf(obj, pdf_url)

        # print("After processing:", summary_web)

        if len(summary_web) == 0 or len(summary_pdf) == 0:
            return render_template('create.html')
        else:
            messages[0] = {'text_web': web_url, 'text_pdf': pdf_url, 'answer_web': summary_web, 'answer_pdf': summary_pdf}
            return redirect(url_for('index'))

    return render_template('create.html')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8016, debug=True)