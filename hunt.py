from job_pages import job_pages
from keywords import keywords
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

def keywords_in_link(link_text, keyword_group):
    result = []
    for keyword in keyword_group:
        result.append(keyword in link_text.lower())
    return all(result)

def format_link_text(original):
    pieces = original.split(" ")
    formatted = []
    total_length = 0
    chars = re.compile('[^a-zA-Z]')
    for piece in pieces:
        total_length += len(piece)
        if total_length < 80:
            piece = piece.rstrip()
            piece = chars.sub('', piece)
            formatted.append(piece)
        else:
            break
    return " ".join(formatted)

def get_jobs(links, domain):
    for link in links:
        href = link.get_attribute('href')
        link_text = link.get_attribute("innerText")
        link_text = format_link_text(link_text.strip())
        for keyword_group in keywords:
            if keywords_in_link(link_text, keyword_group):
                if "://" in href:
                    full_url = href
                else:
                    full_url = domain + href
                print("\t" + link_text + "\n\t" + full_url + "\n")
                break
    return False


def init():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options = chrome_options)
    
    for job_page in job_pages:
        url = job_page["url"]
        path = job_page["path"]
        print("HUNTING @ ", url, "\n")
        try:
            if job_page["checkManual"]:
                print("CHECK THIS PAGE MANUALLY")
                continue
        except:
            pass
        domain = "https://" + url.split("://")[1].split("/")[0]
        driver.get(url)
        links = driver.find_elements_by_xpath(f'//a[contains(@href,"{path}")]')
        get_jobs(links, domain)
    driver.close()

init()
