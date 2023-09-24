from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests
import time
import json

with open('data.json', 'w') as f:
    json.dump([], f)
    
def write_json(new_data, filename='data.json'):
    """Writes information to the json file

    Args:
        new_data (type): description
        filename (str, optional): description. Defaults to 'data.json'.
    """
    
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data.append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

def get_youtube_thumbnail(video_url):
    response = requests.get(video_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        thumbnail = soup.find("meta", property="og:image")
        
        if thumbnail:
            thumbnail_url = thumbnail["content"]
            return thumbnail_url
        else:
            print("Thumbnail not found on the page.")
    else:
        print(f"Error accessing the page. Status code: {response.status_code}")
        
def scrape_short(driver, url):
    driver.get(url)
    driver.implicitly_wait(10)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    channel_name = soup.select_one('.style-scope.ytd-channel-name a').text

    soup = BeautifulSoup(page_source, 'html.parser')

    divs = soup.find_all('div', class_='yt-spec-button-shape-with-label__label')

    like_count = divs[0].find('span', class_='yt-core-attributed-string')
    like_count = like_count.text

    comment_count = divs[2].find('span', class_='yt-core-attributed-string yt-core-attributed-string--white-space-pre-wrap yt-core-attributed-string--text-alignment-center yt-core-attributed-string--word-wrapping')
    comment_count = comment_count.text

    title_element = soup.find('yt-formatted-string', class_='style-scope ytd-reel-player-header-renderer')
    title = title_element.text

    url = driver.current_url
    
    thumbnail_url = get_youtube_thumbnail(url)

    
    res = {
        'url': url,
        'thumbnail_url': thumbnail_url,
        'title': title,
        'channel_name': channel_name,
        'like_count': like_count,
        'comment_count': comment_count
    }  
    
    write_json(res)  
    return res

def scroll_down(driver):
    actions = ActionChains(driver)
    actions.send_keys(Keys.END).perform()
    time.sleep(10)


def all_urls(url):
    def scroll_to_bottom(driver):
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    driver = webdriver.Firefox()
    
    try:
        driver.get(url)
        scroll_to_bottom(driver)
        page_source = driver.page_source
    finally:
        driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    links = soup.find_all('a', href=True)
    
    all_urls = [link['href'] for link in links if link['href'].startswith('/')]
    base_url = 'https://www.youtube.com'
    absolute_urls = [base_url + url for url in all_urls]
    
    return absolute_urls    

def get_latest_short(url):
    return all_urls(url)[8]

url = "https://www.youtube.com/@" + input("Channel: @") + "/shorts/"

driver = webdriver.Firefox()
urls = all_urls(url)[8:]
urls = list(dict.fromkeys(urls))

for url in urls:
    ans = scrape_short(driver, url)
    time.sleep(10)
    print(ans)
    
driver.quit()