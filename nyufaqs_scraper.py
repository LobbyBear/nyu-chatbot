import requests
from bs4 import BeautifulSoup
import json

urls = [
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/newly-admitted/frequently-asked-questions.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/newly-admitted/short-term-international-student-FAQ.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/Emergencyinformation.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/current-students/employment-and-tax/curricular-practical-training/cpt-frequently-asked-questions.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/current-students/employment-and-tax/optional-practical-training/opt-frequently-asked-questions.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/alumni/extend-your-opt/stem-opt/FAQs-on-the-new-regulations-for-STEM-OPT.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/current-students/employment-and-tax/tax/tax-frequently-asked-questions.html",
    "https://www.nyu.edu/students/student-information-and-resources/student-visa-and-immigration/current-students/visa-and-academic-changes/effect-of-arrest-on-immigration-status.html"
]

faqs = []

for url in urls:
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    blocks = soup.find_all('details', class_= 'expandable singleton')
    for b in blocks:
        question = b.find('summary', class_='expandable-item-title').text.strip()
        answers_paragraphs = b.find_all('p')
        answer_text = ''
        for p in answers_paragraphs:
            for a in p.find_all('a'):
                if 'href' in a.attrs:
                    link_text = a.text
                    link_url = a['href']
                    markdown_link = f"[{link_text}](https://www.nyu.edu{link_url})" if not link_url.startswith('http') else f"[{link_text}]({link_url})"
                    a.replace_with(markdown_link)
            text_with_markdown_links = ''.join([str(x) for x in p.contents]).replace('<br/>', '\n').strip()
            answer_text += text_with_markdown_links + ' '
        
        # print(f"question: {question}")
        # print(f"answer: {answer_text}")
        faqs.append({'question': question, 'answer': answer_text})

faqs_json = json.dumps(faqs, indent=4)

with open('faqs.json', 'w') as file:
    file.write(faqs_json)