# from job_pages import job_pages
# from keywords import keywords
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

no_opening_texts = [
    'We do not have any current job openings.',
    'There are currently no job openings',
    'Sorry, no job openings at the moment',
    'We don\'t have any open positions at the moment',
    'We currently don’t have any job openings.',
    'We have no positions available right now',
    'no open positions at this time'
]

generic_texts = [
    'more info', 'read more', 'view job', 'apply'
] 

def keywords_in_link(link_text, keyword_group):
    result = []
    for keyword in keyword_group:
        result.append(keyword in link_text.lower())
    return all(result)

def format_link_text(original):
    pieces = original.split(' ')
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
    return ' '.join(formatted).upper()

def no_openings():
    global driver
    for text in no_opening_texts:
        no_openings = driver.find_elements_by_xpath(f'//*[contains(text(),"{text}")]')
        if len(no_openings) > 0:
            return True
    return False

def get_pages(next_link_xpath):
    global driver
    links = []
    while True:
        try:
            driver.find_element_by_xpath(next_link_xpath).click()
            links += get_links()
        except:
            return links

def get_link_text(link):
    if len(link.get_attribute('innerText')) > 0 and link.get_attribute('innerText').lower().strip() not in generic_texts:
        text = format_link_text(link.get_attribute('innerText').strip())
    else:
        text = format_link_text(link.find_element_by_xpath('.//parent::*').get_attribute('innerText').strip())
        if text.lower().strip() in generic_texts:
            text = format_link_text(link.find_element_by_xpath('.//parent::*').find_element_by_xpath('.//preceding-sibling::*').get_attribute('innerText').strip())
    return text

def get_links():
    global driver, current_page
    if no_openings():
        print('No Openings')
        return []
    path = current_page['path']
    link_elements = driver.find_elements_by_xpath(f'//a[contains(@href,"{path}")]')
    links = []
    for link in link_elements:
        links.append({
            'href': link.get_attribute('href'),
            'text': get_link_text(link)
        })
    if len(links) < 1:
        print('Either something is wrong or there are 0 openings')
    return links

def get_iframe(iframe_name):
    global driver, current_page
    driver.switch_to_frame(iframe_name)
    links = get_links()
    driver.switch_to_default_content()
    return links

def get_jobs(links):
    global driver, current_page
    jobs = []
    for link in links:
        for keyword_group in keywords:
            if keywords_in_link(link['text'], keyword_group):
                if "://" in link['href']:
                    full_url = link['href']
                else:
                    full_url = current_page['domain'] + link['href']
                jobs.append("\t" + link['text'] + "\n\t" + full_url + "\n")
                print("\t" + link['text'] + "\n\t" + full_url + "\n")
                break
    return jobs


def get_driver(headless=True, mobile=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    if mobile:
        mobile_emulation = {
            "deviceMetrics": { "width": 375, "height": 800, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1" 
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    return webdriver.Chrome(options = chrome_options)

def init(job_pages=job_pages):
    global driver, current_page
    for job_page in job_pages:
        current_page = job_page
        current_page['domain'] = 'https://' + current_page['url'].split('://')[1].split('/')[0]
        print('HUNTING @ ', current_page['url'], '\n')
        # try:
        driver.get(current_page['url'])
        if job_page['custom_method']:
            links = eval(job_page['custom_method'])
        else:
            links = get_links()
        jobs = get_jobs(links)
        for job in jobs:
            print(job)
        # except:
            # print('Issue getting jobs @ ' + url)
    # driver.close()


def get_next():
    global i
    job_pages_slice = job_pages[i:i+1]
    init(job_pages_slice)
    i += 1

def get_previous():
    global i
    job_pages_slice = job_pages[i-1:i]
    init(job_pages_slice)
    i -= 1

i = 0
current_page = False
driver = get_driver(headless=False)
# init()
