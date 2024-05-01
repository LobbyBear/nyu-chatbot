

import requests
from bs4 import BeautifulSoup
import json


def scrape_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    faq_items = []
    blocks = soup.find_all('details', class_='expandable singleton')
    for block in blocks:
        question = block.find('summary', class_='expandable-item-title').text.strip()
        answer_paragraphs = block.find_all('p')
        answer_text = ''
        for paragraph in answer_paragraphs:
            for link in paragraph.find_all('a'):
                if 'href' in link.attrs:
                    link_text = link.text
                    link_url = link['href']
                    markdown_link = f"[{link_text}](https://www.nyu.edu{link_url})" if not link_url.startswith('http') else f"[{link_text}]({link_url})"
                    link.replace_with(markdown_link)
            text_with_markdown_links = ''.join(str(content) for content in paragraph.contents).replace('<br/>', '\n').strip()
            answer_text += text_with_markdown_links + ' '
        faq_items.append({'question': question, 'answer': answer_text})
    
    return faq_items
