#! python3
# File name: cloudflare.py - scraping website bypass cloudflare DDoS protection by simulate human navigate through website
'''
NOTE:
* The difficult part is to prevent server from thinking that requests is DDoS attack
Prevent server denial:
    - set stream True and close stream
    - sleep before requests
    - sleep before download
    - sleep every n pages

* Prevent file corrupted:
    .rstrip() to make sure that the URL doesn't contain newline (http://stackoverflow.com/questions/24918267/python-requests-get-showing-404-while-url-does-exists)

* Using Selenium as a way to simulate human browsing
    - trick cloudflare that a person is actually browsing then requests a page by requests or cfscrape
'''
import re
import os
import bs4
import logging
import time
from contextlib import closing
import cfscrape                         # https://github.com/Anorov/cloudflare-scrape // alternative to requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys     # sends key actions
from selenium.webdriver.common.action_chains import ActionChains    # can set macro keys

'''
SET UP CODE
'''
# for debugging
logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)               # comment this to see log msg

# website you want to scrap
url = 'http://sample.com'                       # starting url
os.chdir('F:\workspace')                        # change working directory
os.makedirs('folder_name', exist_ok=True)       # make new folder for downloaded files

# replace "keywords" with image's name you want to ignore in the website
filter = re.compile(r'(keywords1)|(keywords2)|(keywords3)')

# internal logic
totalPage = 448     # the total pages of website, if available
currentPage = 0   # set to 0 if start from first page.
repeatTime = 0
shortTimeoutTimer = 0
longTimeoutTimer = 0
'''
END OF SET UP
'''

'''
MAIN CODE
'''
if currentPage != 1:
        url = url + '/page/' + str(currentPage)
while not currentPage == totalPage + 1:
    # simulate navigate website to trick cloudflare
    browser = webdriver.Chrome(executable_path="F:\workspace\chromedriver.exe")
    browser.get(url)
    actions = ActionChains(browser)
    actions.send_keys(Keys.PAGE_DOWN)

    # download the page
    print('\n######################')
    print('Downloading page %s...' % url)
    print('######################')
    time.sleep(10)
    scraper = cfscrape.create_scraper()
    with closing(scraper.get(url, stream=True)) as res:        # this fixed the partially reading request bodies 'http://docs.python-requests.org/en/master/user/advanced/'
        soup = bs4.BeautifulSoup(res.text, "html.parser")

        # find the url of image
        logging.debug('Start of log')
        found_elements = soup.find_all('img')
        logging.debug(found_elements)
        logging.debug('End of log')
        if not found_elements:
            print('Could not find image.')
        else:
            for elems in found_elements:
                cUrl = elems.get('src')
                cUrl = cUrl.rstrip()        #include this line as a precaution to prevent '\n'
                if filter.findall(cUrl) == []:

                    # download the image
                    print('Downloading image %s...' % (cUrl))
                    res = scraper.get(cUrl)
                    actions.perform()               # keyboard action is performed here
                    time.sleep(2)

                    # save the image to hard dive
                    try:
                        imageFile = open(os.path.join('image', 'page_' + str(currentPage)) + '__' + os.path.basename(cUrl), 'wb')
                        for chunk in res.iter_content(100000):
                            imageFile.write(chunk)
                    except:
                        pass
                    imageFile.close()
        browser.close()

        # go to next page
        currentPage += 1
        url = 'http://sample.com ' + str(currentPage)

        # Prevent corrupted file from cloudflare with timeout
        #shortTimeoutTimer += 1      # comment out to disabled
        #longTimeoutTimer += 1       # comment out to disabled
        if shortTimeoutTimer == 1:
            print('Sleeping for 3 minutes')
            time.sleep(180)
            shortTimeoutTimer = 0
        if longTimeoutTimer == 5:
            print('Sleeping for 5 minutes')
            time.sleep(900)
            longTimeoutTimer = 0

print('Done.')
'''
END OF MAIN CODE
'''