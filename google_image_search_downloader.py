import base64
import concurrent.futures
import os
import random
import string
import subprocess
import sys
import threading
import time

from concurrent.futures import wait, ALL_COMPLETED
from multiprocessing import Process
import multiprocessing
import tkinter as tk

import requests

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
    from PIL import Image
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

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page

        time.sleep(SCROLL_PAUSE_TIME)
        try:

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
    save_directory = os.path.join(f"{query}", "")
    if os.path.exists(save_directory) is False:
        os.mkdir(save_directory)
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    global browser
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options, executable_path=r'driver/geckodriver.exe')

    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={query}"
    browser.get(search_url)

    time.sleep(1)

    scroll_to_infinite_page(browser, page_number)

    elements = browser.find_elements_by_xpath("//img[contains(@class, 'rg_i') and contains(@class, 'Q4LuWd')]")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_file, query, number, args) for args in elements]
        wait(futures, timeout=None, return_when=ALL_COMPLETED)
        browser.quit()
        time.sleep(1)
        number.value = -1


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

    button_clicked = True


def update_ui():
    # global parent_connection
    global process_spawned
    global download_started
    global button_clicked
    global query_search
    global total_images
    window.after(100, update_ui)

    if not button_clicked:
        return
    if query_search == "":
        return
    if not process_spawned:
        saved_images.value = 0
        pages.value = 1
        process_spawned = True

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


if __name__ == '__main__':
    print('Installing/upgrading dependency')
    subprocess.run(['pip', 'install', '--upgrade', 'selenium'], capture_output=True)
    subprocess.run(['pip', 'install', '--upgrade', 'Pillow'], capture_output=True)

    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    queue = multiprocessing.Queue()
    saved_images = multiprocessing.Value('d', 0.0)
    pages = multiprocessing.Value('d', 1.0)
    browser_created = multiprocessing.Value('d', 0)
    window = tk.Tk()

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
