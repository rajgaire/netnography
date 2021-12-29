# my python code that will extract reviews from trip-advisor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import time
import csv


query = "Patan (Lalitpur)"
country = "Nepal"

DRIVER_PATH = 'chromedriver_win32/chromedriver.exe'
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
# 1. open https://www.tripadvisor.com/Search?q=<query>""
def fetch_links(query):
    driver.get(f'https://www.tripadvisor.com/Search?q={query}')
    time.sleep(5)
    with open("links.txt", "w") as csv:

        # 2. find: Search results matching ("<query>")
        # results = driver.find_element_by_xpath("//span[starts-with(text(),'Search results matching')]/ancestor::div[@class='search-results-list']") # driver.find_element_by_class_name("section_wrapper") )
        # link_counter = 0
        has_more = True
        # current_page = 0
        while has_more:
            cards = driver.find_elements_by_class_name("result-card")
            try:
                driver.find_element_by_xpath("//div[@class='show-block show-more']").click()
                time.sleep(2)
            except:
                pass

            for c in cards:
                try:
                    a = c.find_element_by_class_name("address") # class="ui_columns is-mobile result-content-columns"
                    address = a.text.strip().lower()
                    # print(address[-1*len(country.lower()): ])
                    if address[-1*len(country.lower()):] == country.lower():
                        d = c.find_element_by_class_name("result-title") # class="ui_columns is-mobile result-content-columns"
                        click = d.get_attribute("onClick")
                        # print(click)
                        if click:
                            csv.write("{}\n".format(click))
                            # parts = click.split(",")
                            # url = parts[3].replace("'", "").strip()
                            # cat = (parts[4].split(":")[1]).replace("'", "").strip()
                            # print(f"{cat} => {url}")
                            # link_counter += 1
                            # print(f"===> {link_counter}", flush=True)
                except Exception as e:
                    print(e)
                    # pass
            csv.flush()
            pagination = driver.find_element_by_class_name("pagination-block")
            # print(f"scroll {pagination.location}")
            driver.execute_script(f"window.scrollTo(0, {pagination.location['y']});")

            next_button = pagination.find_elements_by_xpath('.//a')[1]
            time.sleep(2)
            # print(f'{next_button.get_attribute("class")} .... {next_button.get_attribute("class").strip() == "ui_button nav next primary"}', flush=True)
            if next_button and next_button.text == "Next" and next_button.get_attribute("class").strip() == "ui_button nav next primary":
                driver.execute_script("arguments[0].click();", next_button)
                # next_button.click()
            else:
                has_more = False
            time.sleep(2)
            # has_more = False
    driver.close()

def fetch_reviews(review_file):
    with open("links.txt", "r") as csv:
        for aline in csv:
            parts = aline.split(",")
            url = "https://www.tripadvisor.com/"+ (parts[3].replace("'", "").strip())
            cat = (parts[4].split(":")[1]).replace("'", "").strip()
            print(f"{cat} => {url}")
            if cat.lower() == "attractions":
                pass
                # fetch_attraction_reviews(review_file, url, cat)
            elif cat.lower() == "restaurants":
                pass
                # fetch_restaurant_reviews(review_file, url, cat)
            elif cat.lower() == "hotels":
                fetch_hotel_reviews(review_file, url, cat)

def fetch_attraction_reviews(review_file, url, cat):
    with open(review_file, 'a', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        print(f"# GET ATTRACTION: {url}")
        driver.get(url)
            
        time.sleep(2)
        # loop until all reviews pages are done
        has_more = True
        recview_counter = 0
        while has_more:
            try:
                # try to click on show more button
                driver.find_element_by_xpath("//div[@id='tab-data-qa-reviews-0']/div/div[5]/button").click()
            except:
                pass

            # get all reviews
            reviews = driver.find_elements_by_xpath("//div[@id='tab-data-qa-reviews-0']/div/div[5]/div")
            for i in range(len(reviews)):
                review_elm = reviews[i]
                if i == len(reviews) - 1:
                    print("!")
                    # click on the next button
                    try:
                        # print(review_elm.find_element_by_xpath(".//a[@aria-label='Next page']").get_attribute("innerHTML"))
                        review_elm.find_element_by_xpath(".//a[@aria-label='Next page']").click()
                        time.sleep(2)
                    except:
                        has_more = False
                else:
                    recview_counter += 1
                    print(f".{recview_counter}", end="")
                    rating = review_elm.find_element_by_xpath("./span/span/div[3]/*[name()='svg']").get_attribute("title").split(" ")[0]
                    t = review_elm.find_element_by_xpath("./span/span/a")
                    title = t.text
                    d = review_elm.find_element_by_xpath("./span/span/div[4]")
                    date = d.text
                    r = review_elm.find_element_by_xpath("./span/span/div[5]/div/div/span")
                    review = r.text.replace("\n", " ").strip()

                    csv_writer.writerow([url, cat, date, rating, title, review]) 

def fetch_hotel_reviews(review_file, url, cat):
    with open(review_file, 'a', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        print(f"# GET HOTEL: {url}")
        driver.get(url)
            
        time.sleep(2)
        # loop until all reviews pages are done
        has_more = True
        recview_counter = 0
        while has_more:
            # get all reviews
            reviews = driver.find_elements_by_xpath("//div[@data-test-target='HR_CC_CARD']")
            for i in range(len(reviews)):
                recview_counter += 1
                review_elm = reviews[i]
                print(f".{recview_counter}", end="")
                title = review_elm.find_element_by_xpath("./div/div[@data-test-target='review-title']/a/span/span").text
                print(title)
                rating = 0.1 * (int)(review_elm.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])
                print(rating)
                d = review_elm.find_element_by_xpath("./div[2]/div[3]/div[2]/span")
                print(d.get_attribute("innerHTML"))
                date = (d.text).split(">")[-1]
                r = review_elm.find_element_by_xpath(".//*[name()='q']")
                review = r.text.replace("\n", " ").strip()
                print(review)

                csv_writer.writerow([url, cat, date, rating, title, review]) 
            
            # change the page
            try:
                driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()
            except:
                has_more = False


def fetch_restaurant_reviews(review_file, url, cat):
    with open(review_file, 'a', encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        print(f"get restaurant {url}")
        driver.get(url)
        # change the value inside the range to save more or less reviews
        has_more = True
        while has_more:
            
            # expand the review 
            time.sleep(2)
            driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']").click()

            container = driver.find_elements_by_xpath(".//div[@class='review-container']")

            for j in range(len(container)):

                title = container[j].find_element_by_xpath(".//span[@class='noQuotes']").text
                date = container[j].find_element_by_xpath(".//span[contains(@class, 'ratingDate')]").get_attribute("title")
                rating = container[j].find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3]
                review = container[j].find_element_by_xpath(".//p[@class='partial_entry']").text.replace("\n", " ").strip()

                csv_writer.writerow([url, cat, date, rating, title, review]) 

            # change the page
            try:
                driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()
            except:
                has_more = False
        # print(len(link_counter))

fetch_reviews("all_reviews.csv")
driver.close()

# - It will get a list of placess in patan.
# 3. Click on the first link
# - after the page is loaded, go to the review section
# - extract reviews in the page
# - click on the next page button
# - repate it until all the reviews are extracted.
# 4. repeat for other links (step 3)
