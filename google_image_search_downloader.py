import base64
import concurrent.futures
import ctypes
import os
import random
import re
import string
import subprocess
import sys
import threading
import time
from concurrent.futures import wait, ALL_COMPLETED
from multiprocessing import Process
import multiprocessing
import tkinter as tk
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

browser = None
lock = threading.Lock()


def save_file(query, number, element, connection):
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

    with open(os.path.join(f"{query}", f"search_{search}.jpg"), "wb") as file:
        print("Saving image to path")
        file.write(img_data)

        number.value = number.value + 1
        connection.send(f"pictures downloaded {str(number.value)}")
    try:
        img = Image.open(os.path.join(f"{query}", f"search_{search}.jpg"))
        img.verify()
    except  (IOError, SyntaxError) as e:
        os.remove(os.path.join(f"{query}", f"search_{search}.jpg"))

        number.value = number.value - 1
        connection.send(f"pictures removed {str(number.value)}")


def scroll_to_infinite_page(browser, connection, pages):
    SCROLL_PAUSE_TIME = 4

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        connection.send(f"Scrolling to bottom of page {pages}")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        connection.send(f"Waiting to load page {pages}")
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            connection.send("End of page reached")
            break
        last_height = new_height

    try:
        connection.send("Find the show more button")
        end_result = browser.find_element_by_class_name("mye4qd")
        end_result.click()
        connection.send("Show more button found")
        time.sleep(SCROLL_PAUSE_TIME)
        scroll_to_infinite_page(browser)
    except Exception:
        pass

    connection.send("Downloading images")


def search_in_google_image(query, number, connection):
    pages = 0
    # while True:
    #     connection.send("go")
    # connection.send("what")

    # dict[0].config(text="Please wait for the browser to open and download your images")

    # class FnScope:
    #     processed_images = 0
    #     showed_explorer = False

    # def finished_downloads(results):

    #
    # FnScope.processed_images += 1
    # with lock:
    #     if FnScope.processed_images > number.value - 5 and not FnScope.showed_explorer:
    #         subprocess.call(f"explorer {query}")
    #         FnScope.showed_explorer = True

    connection.send("Creating directory")
    save_directory = os.path.join(f"{query}", "")
    if os.path.exists(save_directory) is False:
        os.mkdir(save_directory)

    connection.send("Opening browser")
    global browser
    options = Options()
    options.headless = True
    # args = ["hide_console", ]

    # browser = webdriver.Firefox(options=options, executable_path=r'driver/geckodriver.exe', service_args=args)
    browser = webdriver.Firefox(options=options, executable_path=r'driver/geckodriver.exe')

    connection.send("Searching the query")
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"
    browser.get(search_url)

    # click on first result image
    # e = browser.find_elements_by_class_name('rg_i')
    # e[0].click()

    connection.send(f"Waiting for page {pages} to load")
    pages += 1
    time.sleep(1)

    scroll_to_infinite_page(browser, connection, pages)
    connection.send(f"Scroll finished, loaded {pages} pages")
    # element = browser.find_elements_by_class_name('v4dQwb')
    elements = browser.find_elements_by_xpath("//img[contains(@class, 'rg_i') and contains(@class, 'Q4LuWd')]")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_file, query, number, args, connection) for args in elements]
        wait(futures, timeout=None, return_when=ALL_COMPLETED)
        connection.send("Downloads finished")
    browser.quit()
    # results = executor.map(save_file, elements)
    # futures = []
    # for arg in elements:
    #     futures.append(
    #         executor.submit(save_file, query, number, arg, connection).add_done_callback(finished_downloads))

    # print(time.perf_counter())


# sys.exit()
# info.config(text=f"Downloaded {str(images_number)} images successfully")


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


def search_download_images():
    query_search = entry.get()
    if query_search == "":
        error.config(text="Empty query please type at least on character")
        return
    error.config(text="")
    info.config(text="Please wait for the browser to open and download your images")
    saved_images = multiprocessing.Value('d', 0.0)

    # manager = multiprocessing.Manager()
    # d = manager.dict()
    # d[0] = info
    # kill_queue = multiprocessing.Queue()
    parent_connection, child_connection = multiprocessing.Pipe()
    p = Process(target=search_in_google_image, args=(query_search, saved_images, child_connection))
    p.start()
    window.quit()

    file_browser_opened = False
    while time.perf_counter() < 90:
        print(time.perf_counter())
        window.update()
        window.attributes("-topmost", True)
        received_text = f"{parent_connection.recv()}"
        info.config(text=received_text)
        if received_text.__contains__("Downloads finished") and not file_browser_opened:
            # if time.perf_counter() > 60 and not file_browser_opened:
            file_browser_opened = True
            subprocess.call(f"explorer {query_search}")
            return
    sys.exit()


# subprocess.call(f"explorer {query_search}")
# p.join()
# for _ in range(50):
#     print(parent_connection.recv())
# p.join()

# kill_queue = multiprocessing.Queue()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     executor.submit(update_info, saved_images)
# return

# while True:
#     print(f'received {str(saved_images.value)} images')

# Waiting for process to finish
# p.join()

# search_in_google_image(query_search)


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    queue = multiprocessing.Queue()

    window = tk.Tk("Google image search downloader")
    # window.tk.call('tk', 'windowingsystem', window._w)
    window.geometry("350x150")
    window.winfo_toplevel().title("Google image downloader")
    search_label = tk.Label(text="Search images")
    entry = tk.Entry()
    button = tk.Button(text="Download images", command=search_download_images)
    info = tk.Label(text="", fg='#0000CD')
    error = tk.Label(text="", fg='#f00')
    search_label.pack()
    entry.pack()
    button.pack(pady=10, side=tk.TOP)
    error.pack(pady=5, side=tk.TOP)
    info.pack(pady=5, side=tk.TOP)
    window.mainloop()

# query_search = input("enter a search query\n")
# split_query = re.split("\s", query_search)
# valid_query = False
# while not valid_query:
#     for split in split_query:
#         if split != "":
#             valid_query = True
#
#             search_in_google_image(query_search)
#
#             break
#     if not valid_query:
#         query_search = input("Search query can't be empty\n")
#         split_query = re.split("\s", query_search)
