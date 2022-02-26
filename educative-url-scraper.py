from time import sleep
from selenium.webdriver.common.by import By
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OS_ROOT = os.path.expanduser('~')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_chrome_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')
    options.add_argument(f'user-data-dir={os.path.join(OS_ROOT,"User Data URL")}')
    options.add_argument('--profile-directory=Default')
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.56 Safari/537.36"
    options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(
        chrome_type=ChromeType.CHROMIUM).install()), options=options)
    driver.set_window_size(1920, 1080)
    print("Driver Loaded")
    return driver


def scrape_path_course_url(driver):
    clear()
    xpath_modules = "//a[contains(@href,'/module/') and contains(@href,'module/lesson/')=false]/following-sibling::div[1]"
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, xpath_modules)))
    except Exception as e:
        pass
    modules = driver.find_elements(
        By.XPATH, xpath_modules)
    course_urls = ""
    for module in modules:
        try:
            WebDriverWait(module, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a")))
        except Exception as e:
            pass
        course_urls += module.find_element(By.TAG_NAME,
                                           "a").get_attribute('href') + "\n"
    return course_urls


def scrape_single_course_url(driver):
    lesson_id = "lesson-title"
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f"[id='{lesson_id}']")))
    except Exception as e:
        pass
    return driver.find_element(By.CSS_SELECTOR, f"[id='{lesson_id}']").get_attribute('href')


def find_urls(driver, title):
    course_urls = ""
    url_elements = driver.find_elements(
        By.CSS_SELECTOR, f"[title*='{title}']")
    for url_element in url_elements:
        course_urls += url_element.find_element(
            By.XPATH, "../../..").find_element(By.TAG_NAME, "a").get_attribute('href') + "\n"
    return course_urls


def generate_course_urls():
    course_title = "Course Cover Image"
    path_title = "Path Cover Image"
    show_more_button_xpath = "//button[contains(.,'Show More')]"
    save_path = os.path.join(OS_ROOT, "Desktop", "course_urls.txt")
    print('''
                Course URL Generator Started
                Go to the url where all courses are listed
    ''')
    driver = load_chrome_driver(headless=False)
    driver.get("https://educative.io")
    input("Login and start scraping")

    driver.get("https://www.educative.io/explore")
    sleep(5)
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, show_more_button_xpath)))
        except Exception as e:
            break
        driver.find_element(
            By.XPATH, show_more_button_xpath).click()
    course_urls = ""
    course_urls += find_urls(driver, course_title)

    driver.get("https://www.educative.io/paths")
    sleep(5)
    course_urls += find_urls(driver, path_title)
    with open(save_path, 'w') as f:
        f.write(course_urls)


def scrap_course_urls():
    clear()
    print('''
                URL Generator Started
    ''')
    try:
        driver = load_chrome_driver(headless=False)
        url_save_path = os.path.join(OS_ROOT, "Desktop")
        url_text_file = os.path.join(url_save_path, "course_urls.txt")
        topic_url_text_file = os.path.join(
            url_save_path, "topic_course_urls.txt")
        with open(url_text_file, 'r') as f:
            url_list = f.readlines()

        course_urls = ""
        for index, url in enumerate(url_list):
            try:
                print(f'''
                                    Starting Scraping: {index}, {url}
                    ''')
                driver.get(url)
                sleep(2)
                if "courses" in url:
                    course_urls += scrape_single_course_url(driver) + "\n"
                elif "path" in url:
                    course_urls += scrape_path_course_url(driver)
                else:
                    course_urls += url

            except Exception as e:
                pass
        with open(topic_url_text_file, 'w') as file:
            file.write(course_urls)
        print("Script Execution Complete")
        driver.quit()
    except Exception as e:
        driver.quit()
        print("Exception, Driver exited")
        raise Exception(e)


def login_educative():
    clear()
    driver = load_chrome_driver(headless=False)
    try:
        driver.get("https://educative.io")
        input("Press enter to return to Main Menu after Login is successfull")
    except Exception as e:
        print("Exception occured, Try again", e)
    driver.quit()


def clear():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    while True:
        clear()
        try:
            print('''
                        Educative Url Scraper, made by Anilabha Datta
                        Project Link: github.com/anilabhadatta/educative-url-scraper
                        Read the documentation for more information about this project.

                        Press 1 to Generate Course/Path Urls
                        Press 2 to Scrap Course Topic Urls
                        Press 3 to Login if your account isn't signed in
                        Press any key to exit
            ''')
            choice = input("Enter your choice: ")
            if choice == "1":
                generate_course_urls()
            elif choice == "2":
                scrap_course_urls()
            elif choice == "3":
                login_educative()
            else:
                break
        except KeyboardInterrupt:
            input("Press Enter to continue")
        except Exception as e:
            print("Main Exception", e)
            input("Press Enter to continue")
