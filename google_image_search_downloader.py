import base64
import concurrent.futures
import multiprocessing
import os
import random
import string
import subprocess
import sys
import threading
import time
import tkinter as tk
from collections import defaultdict
from concurrent.futures import wait, ALL_COMPLETED
from multiprocessing.dummy import Process

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

query_search = ""
browser = None
lock = threading.Lock()
button_clicked = False
process_spawned = False
parent_connection = None
download_started = False
browser_created = False
total_images = 0
pages_downloaded = 0
saved_images = 0
pages = 0


def save_file(query, number, element):
    # print(arg)
    global pages_downloaded
    url = element.get_attribute("src")
    while url is None:
        browser.execute_script("arguments[0].scrollIntoView();", element)
        url = element.get_attribute("src")
        # print("No sources found taking screenshot")
        # url = element.screenshot_as_base64
    try:

        # print("Downloading image")
        response = requests.get(url)
        if 'encrypted' in url:
            return
        print(url)
        img_data = response.content
    except Exception:

        # print("Downloading base64 image")
        img_data = base64.b64decode(url.split(",")[1])
        # if not base64_image:
        #     if response.status_code == 200:
        #         print("Downloading image")
    search = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    with open(os.path.join(f"{query}", f"search_{search}.jpg"), "wb") as file:
        # print("Saving image to path")
        file.write(img_data)

        number.value += 1
        # connection.send(f"pictures downloaded {str(pages_downloaded)}")
    try:
        img = Image.open(os.path.join(f"{query}", f"search_{search}.jpg"))
        img.verify()
    except  (IOError, SyntaxError) as e:
        os.remove(os.path.join(f"{query}", f"search_{search}.jpg"))

        number.value -= 1
        # connection.send(f"pictures removed {str(pages_downloaded)}")


def scroll_to_infinite_page(browser, page_number):
    SCROLL_PAUSE_TIME = 4

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        # connection.send(f"Scrolling to bottom of page {pages}")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        # connection.send(f"Waiting to load page {pages}")
        time.sleep(SCROLL_PAUSE_TIME)
        try:
            # connection.send("Find the show more button")

            end_result = browser.find_element_by_class_name("mye4qd")
            end_result.click()
            time.sleep(SCROLL_PAUSE_TIME)
            # connection.send("Show more button found")

            # scroll_to_infinite_page(browser)
        except Exception:
            pass

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # connection.send("End of page reached")
            break
        last_height = new_height
        page_number.value += 1

        # connection.send("Downloading images")
    page_number.value = -1


def search_in_google_image(query, number, page_number, browser_launched):
    global browser_created

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

    # connection.send("Creating directory")
    save_directory = os.path.join(f"{query}", "")
    if os.path.exists(save_directory) is False:
        os.mkdir(save_directory)

    # connection.send("Opening browser")
    global browser
    options = Options()
    options.headless = False
    # args = ["hide_console", ]

    # browser = webdriver.Firefox(options=options, executable_path=r'driver/geckodriver.exe', service_args=args)
    # if browser_launched.value == 0:
    browser = webdriver.Firefox(options=options, executable_path=r'driver/geckodriver.exe')
    # browser_launched.value = 1

    # connection.send("Searching the query")
    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"
    browser.get(search_url)

    # click on first result image
    # e = browser.find_elements_by_class_name('rg_i')
    # e[0].click()

    # connection.send(f"Waiting for page {pages} to load")

    def get_image(element):
        # label = element.find_element_by_xpath(
        #     "//a[contains(@class, 'kGQAp') and contains(@class, 'VFACy')]").get_attribute("title")
        print(label)
        element.click()
        # arg = browser.find_elements_by_xpath()
        # # time.sleep(1)
        #
        # # arg = browser.find_elements_by_xpath(
        # #     f"//img[contains(@class, 'n3VNCb') and contains(@alt, 'Image result for {query}')"
        # #     f" and contains(@data-noaft, '1')"
        # #     f" and contains(@jsname, 'HiaYvf')"
        # #     f" and contains(@jsaction, 'load:XAeZkd;')]"
        # # )
        # arg.sort(key=lambda x: x.size['width'], reverse=True)
        # if len(arg) > 0:
        #     save_file(query, number, arg[0])

    # time.sleep(1)

    #    scroll_to_infinite_page(browser, page_number)

    # connection.send(f"Scroll finished, loaded {pages} pages")
    # element = browser.find_elements_by_class_name('v4dQwb')
    # elements = browser.find_elements_by_xpath("//img[contains(@class, 'rg_i') and contains(@class, 'Q4LuWd')]")
    elements = browser.find_elements_by_xpath("//div[contains(@class, 'isv-r') and contains(@class, 'PNCib')]")
    labels_elem = browser.find_elements_by_xpath(
        "//a[contains(@class, 'kGQAp') and contains(@class, 'VFACy')]")
    # .get_attribute("title")
    dict = defaultdict()
    labels = []
    for label in labels_elem:
        labels.append(label.get_attribute("title"))

    for index, element in enumerate(elements):
        if index == len(labels) - 1:
            break
        dict[labels[index]] = element

    return
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for key,value in enumerate()
        futures = [executor.submit(get_image, args) for args in elements and label in lab]

    return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_image, args) for args in elements]

    print("finished")
    return
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_file, query, number, args) for args in elements]
        wait(futures, timeout=None, return_when=ALL_COMPLETED)
        browser.quit()
        time.sleep(1)
        number.value = -1
        # connection.send(f"Downloads finished downloaded {pages_downloaded} images")
    # browser.quit()
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
    global query_search
    global button_clicked
    query_search = entry.get()
    button["state"] = tk.DISABLED
    entry["state"] = tk.DISABLED
    if query_search == "":
        error.config(text="Empty query please type at least on character")
        return
    error.config(text="")
    info.config(text="Please wait for the browser to open and download your images")
    # saved_images = multiprocessing.Value('d', 0.0)
    button_clicked = True

    # manager = multiprocessing.Manager()
    # d = manager.dict()
    # d[0] = info
    # kill_queue = multiprocessing.Queue()
    # parent_connection, child_connection = multiprocessing.Pipe()
    # p = Process(target=search_in_google_image, args=(query_search, saved_images, child_connection))
    # p.start()

    # window.quit()
    #
    # file_browser_opened = False
    # while time.perf_counter() < 90:
    #     print(time.perf_counter())
    #     window.update()
    #     window.attributes("-topmost", True)
    #     received_text = f"{parent_connection.recv()}"
    #     info.config(text=received_text)
    #     if received_text.__contains__("Downloads finished") and not file_browser_opened:
    #         # if time.perf_counter() > 60 and not file_browser_opened:
    #         file_browser_opened = True
    #         subprocess.call(f"explorer {query_search}")
    #         return
    # sys.exit()


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

def update_ui():
    # global parent_connection
    global process_spawned
    global download_started
    global button_clicked
    global query_search
    global total_images
    window.after(100, update_ui)

    # if not download_started:

    # else:
    #     window.after(10, update_ui)

    if not button_clicked:
        return
    if query_search == "":
        return
    if not process_spawned:
        saved_images.value = 0
        pages.value = 1
        process_spawned = True
        # parent_connection, child_connection = multiprocessing.Pipe()

        p = Process(target=search_in_google_image, args=(query_search, saved_images, pages, browser_created))
        p.start()
    else:
        if pages.value != -1:
            info2.config(text=f"Please wait until the end of the process ")
            info.config(text=f"Loading page {str(pages.value)}")
        else:
            if saved_images.value != -1:
                total_images = saved_images.value
                info.config(text=f"Downloading image {str(saved_images.value)}")
            else:
                info2.config(text=f"Download finished")
                info.config(text=f"Downloaded  {str(total_images)} pictures")
                subprocess.call(f"explorer {query_search}")
                print(time.perf_counter())
                process_spawned = False
                button_clicked = False
                query_search = ""
                button["state"] = tk.NORMAL
                entry["state"] = tk.NORMAL

        # if not parent_connection.closed:
        #     received_text = f"{parent_connection.recv()}"
        #     info.config(text=received_text)
        #     if received_text.__contains__("pictures downloaded"):
        #         download_started = True
        #     if received_text.__contains__("Downloads finished"):
        #         # if time.perf_counter() > 60 and not file_browser_opened:
        #         file_browser_opened = True
        #         subprocess.call(f"explorer {query_search}")
        #         parent_connection.close()
        #         button["state"] = tk.NORMAL
        #         entry["state"] = tk.NORMAL
        #         print(time.perf_counter())
    # schedule this to run again


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    queue = multiprocessing.Queue()
    saved_images = multiprocessing.Value('d', 0.0)
    pages = multiprocessing.Value('d', 1.0)
    browser_created = multiprocessing.Value('d', 0)
    window = tk.Tk()
    # window.tk.call('tk', 'windowingsystem', window._w)
    window.geometry("350x200")
    window.winfo_toplevel().title("Google image downloader")
    search_label = tk.Label(text="Search images")
    entry = tk.Entry()
    button = tk.Button(text="Download images", command=search_download_images)
    info = tk.Label(text="", fg='#0000CD')
    error = tk.Label(text="", fg='#f00')
    info2 = tk.Label(text="", fg='#008000')

    search_label.pack()
    entry.pack()
    button.pack(pady=10, side=tk.TOP)
    error.pack(pady=5, side=tk.TOP)
    info2.pack(pady=7, side=tk.TOP)
    info.pack(pady=5, side=tk.TOP)
    window.resizable(False, False)
    window.attributes("-topmost", True)
    update_ui()
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
