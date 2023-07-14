from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import os
from datetime import datetime


def crawl_web(crawl_base_url, crawl_from='July 5, 2023', crawl_to='July 12, 2023'):
    date_format = '%B %d, %Y'
    crawl_from = datetime.strptime(crawl_from, date_format).date()
    crawl_to = date_object = datetime.strptime(crawl_to, date_format).date()

    metadata = []
    stop = False
    for page in range(1, 3):
        if stop == True:
            break
        
        req = Request(
            url=f"{crawl_base_url}/page/{page}/",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, features='lxml')
        articles = soup.find('main', {'id': 'main'}).find_all('article')
        
        for i, article in enumerate(articles):
            info = {}
            date_string = article.find('time', {'class': 'entry-date published'}).get_text()
            date_object = datetime.strptime(date_string, date_format).date()
            
            if date_object > crawl_to:
                continue
            
            if date_object <= crawl_to and date_object >= crawl_from:
                info['date'] = date_object
                info['title'] = article.find('h2').get_text()
                info['author'] = article.find('span', {'class': 'author vcard'}).get_text()
                info['thumbnail'] = article.find('img')['src']
                url = article.find('a')['href']
                html = urlopen(url).read().decode('utf-8')
                soup = BeautifulSoup(html, features='lxml')
                content = soup.find('div', {'class': 'entry-content'})
                info['text'] = ''
                
                for el in content.find_all(recursive=False):
                    if 'Related' not in el.get_text():
                        info['text'] += el.get_text() + '\n'
                
                print("Crawled web: ", info)
                
                metadata.append(info)
                
                if date_object < crawl_from:
                    stop = True
                    break
            
            if i == 1: # Just 2 articles for demo
                break
    
    return metadata


def crawl_pdf(crawl_base_url):
    metadata = []
    if os.path.exists('pdf/') is False:
        os.mkdir('pdf/')
    for page in range(1, 2): # Crawl 1 web pages (not pdf pages) which includes many pdf files
        req = Request(
            url=f"{crawl_base_url}&page={page}",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, features="lxml")
        articles = soup.find_all('div', {'class': 'row infinite-item item paper-card'})
        
        for i, article in enumerate(articles):
            info = {}
            info["title"] = article.find('h1').get_text()
            info["stars"] = article.find('div', {'class': 'entity-stars'}).get_text()
            detail = article.find('a', {'class': 'badge badge-light'})['href']
            pdf = "https://paperswithcode.com" + detail
            print("Crawling pdf:", pdf)
            
            req = Request(
                url=pdf,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            html = urlopen(req).read().decode('utf-8')
            soup = BeautifulSoup(html, features="lxml")
            authors = soup.find_all('span', {'class': 'author-span'})
            info['date'] = authors[0].get_text()
            info['authors'] = ''
            
            for a in authors[1:]:
                info['authors'] += a.get_text()
            
            if not soup.find('a', {'class': 'badge badge-light'}):
                continue
            
            info['pdf_url'] = soup.find('a', {'class': 'badge badge-light'})['href']
            response = requests.get(info['pdf_url'])
            
            with open(f"./pdf/{info['pdf_url'].split('/')[-1]}", 'wb') as f:
                f.write(response.content)
            metadata.append(info)

            if i == 1: # Just 2 pdfs for demo
                break
    
    return metadata


def extract_OCR(file):
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
