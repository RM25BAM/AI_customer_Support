from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import time


load_dotenv("server/.env.dev")

my_cse_id = "f188e2180323e449e"
dev_key = os.getenv("GOOGLE_SEARCH_API_KEY")


def google_search(search_term, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=dev_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    result = res['items']
    info = {}
    for index, result in enumerate(results):
        title = result.get('title')
        link = result.get('link')
        snippet = result.get("snippet")
        paragraph = details(link)
        time.sleep(3)
        info[index] = [title, link, snippet, paragraph]

    return info
        




results = google_search('Best food in Dominican Republic in San Jose de ocoa', my_cse_id, num=10, cr="us", lr="lang_en")
# for result in results:
#     title = result.get('title')
#     link = result.get('link')
#     snippet = result.get("snippet")
#     # print(result.get('title'))
    # print(result.get('link'))
    # print(result.get('snippet'))
    # print('\n')


def details(url):
    response = requests.get(url)

    if response.status_code == 200:
         # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the relevant content; this might need adjustment depending on the structure of the webpage
        # For example, extracting all paragraph text
        article_content = soup.find_all('p')

        # Print the content
        for paragraph in article_content:
            print(paragraph.get_text())

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")