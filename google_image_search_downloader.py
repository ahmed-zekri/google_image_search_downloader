import base64
import concurrent.futures
import os
import random
import re
import string
import time
from concurrent.futures import wait, ALL_COMPLETED

from PIL import Image
from pip._vendor import requests
from selenium import webdriver

browser = None


def save_file(arg, element):
    # print(arg)
    url = element.get_attribute("src")
    while url is None:
        browser.execute_script("arguments[0].scrollIntoView();", element)
        url = element.get_attribute("src")
        # print("No sources found taking screenshot")
        # url = element.screenshot_as_base64
    try:
        print("Downloading image")
        response = requests.get(url)
        img_data = response.content
    except Exception:

        print("Downloading base64 image")
        img_data = base64.b64decode(url)
        # if not base64_image:
        #     if response.status_code == 200:
        #         print("Downloading image")
    search = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    with open(os.path.join(f"{query_search}", f"search_{search}.jpg"), "wb") as file:
        print("Saving image to path")
        file.write(img_data)
    try:
        img = Image.open(os.path.join(f"{query_search}", f"search_{search}.jpg"))
        img.verify()
    except  (IOError, SyntaxError) as e:
        os.remove(os.path.join(f"{query_search}", f"search_{search}.jpg"))


def scroll_to_infinite_page(browser):
    SCROLL_PAUSE_TIME = 4

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        print("Scrolling to bottom")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        print("Waiting to load page")
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("End of page reached")
    try:
        print("Find the show more button")
        end_result = browser.find_element_by_class_name("mye4qd")
        end_result.click()
        print("Show more button found")
        time.sleep(SCROLL_PAUSE_TIME)
        scroll_to_infinite_page(browser)
    except Exception:
        pass

    print("Downloading images")


def search_in_google_image(query):
    print("Creating directory")
    save_directory = os.path.join(f"{query_search}", "")
    if os.path.exists(save_directory) is False:
        os.mkdir(save_directory)
    print("Opening browser")
    global browser
    browser = webdriver.Firefox(executable_path=r'geckodriver.exe')
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"
    images_url = []

    # open browser and begin search
    print("Searching the query")
    browser.get(search_url)
    # e = browser.find_elements_by_class_name('rg_i')

    # e[0].click()
    print("Waiting for page to load")
    time.sleep(1)

    scroll_to_infinite_page(browser)
    # element = browser.find_elements_by_class_name('v4dQwb')
    elements = browser.find_elements_by_xpath("//img[contains(@class, 'rg_i') and contains(@class, 'Q4LuWd')]")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # results = executor.map(save_file, elements)
        option_arg = "option arg"
        futures = [executor.submit(save_file, option_arg, args) for args in elements]
        wait(futures, timeout=None, return_when=ALL_COMPLETED)
        print(time.perf_counter())


# Google image web site logic
# if count == 0:
#     big_img = elements[0].find_element_by_class_name('n3VNCb')
# else:
#     big_img = elements[1].find_element_by_class_name('n3VNCb')
#
# images_url.append(big_img.get_attribute("src"))
#
# # write image to file
# response = requests.get(images_url[count])
# if response.status_code == 200:
#     with open(f"search{count + 1}.jpg", "wb") as file:
#         file.write(response.content)
#
# count += 1
#
# # Stop get and save after 5
# # if count == 5:
# #     break
#


query_search = input("enter a search query\n")
split_query = re.split("\s", query_search)
valid_query = False
while not valid_query:
    for split in split_query:
        if split != "":
            valid_query = True

            search_in_google_image(query_search)

            break
    if not valid_query:
        query_search = input("Search query can't be empty\n")
        split_query = re.split("\s", query_search)
