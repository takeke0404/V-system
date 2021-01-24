from selenium import webdriver
import os


def main():

    #driver = webdriver.Firefox(executable_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "geckodriver")))
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    #options.add_argument('--no-sandbox')
    #options.add_argument('--disable-setuid-sandbox')
    driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options = options)

    driver.get("https://www.youtube.com/channel/UC2OacIzd2UxGHRGhdHl1Rhw")

    item_sections = driver.find_elements_by_tag_name("ytd-item-section-renderer")
    print(item_sections[0].text)

    driver.quit()

if __name__ == "__main__":
    main()
