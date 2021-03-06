# my python code that will extract reviews from trip-advisor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import os, time, re
import csv

class ReviewCollector:
    driver_path = None
    debug = True
    info = True

    def __init__(self, driver_path, debug=False, info=True) -> None:
        self.driver_path = driver_path
        self.debug = debug
        self.info = info


    def fetch_reviews(self, place, country, output_file):
        tmp_folder = f"./tmp/{country}"
        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)

        link_file = f"{tmp_folder}/{place}.txt"
        self.fetch_links(place, country, link_file)
        reviewed_links = {}
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding="utf-8") as csv_file:
                for l in csv_file.readlines():
                    parts = l.split(",")
                    self.debug and print(f"already reviewed = {parts[0]}")
                    if len(parts) > 2:
                        reviewed_links[parts[1]] = True
        self.info and print(f"{len(reviewed_links)} already reviewed")
        with open(link_file, "r") as csv:
            for aline in csv:
                parts = aline.split(",")
                if len(parts) < 3:
                    continue
                url = "https://www.tripadvisor.com"+ (parts[3].replace("'", "").strip())
                if url in reviewed_links:
                    continue
                cat = (parts[4].split(":")[1]).replace("'", "").strip()
                self.info and print(f"{cat} => {url}")
                if cat.lower() == "attractions":
                    self.fetch_attraction_reviews(url, cat, output_file)
                elif cat.lower() == "restaurants":
                    self.fetch_restaurant_reviews(url, cat, output_file)
                elif cat.lower() == "hotels":
                    self.fetch_hotel_reviews(url, cat, output_file)
                elif cat.lower() == "activity":
                    self.fetch_attraction_reviews(url, cat, output_file)
                else:
                    self.info and print(f"{cat} review is not supported")

    def fetch_links(self, place, country, link_file):
        # check if the link file already exists and is updated within 1 month
        if os.path.exists(link_file):
            modified_time = os.path.getmtime(link_file)
            seconds_in_one_month = 30*24*60*60
            current_time = time.time()
            if modified_time + seconds_in_one_month > current_time:
                return
        # otherwise, fetch links
        driver = webdriver.Chrome(executable_path=self.driver_path)
        # 1. open https://www.tripadvisor.com/Search?q=<query>""
        url = f'https://www.tripadvisor.com/Search?q={place}'
        self.info and print(f"Searching{url}")
        driver.get(url)
        time.sleep(5)
        with open(link_file, "w") as csv:
            # 2. find: Search results matching ("<place>")
            # results = driver.find_element_by_xpath("//span[starts-with(text(),'Search results matching')]/ancestor::div[@class='search-results-list']") # driver.find_element_by_class_name("section_wrapper") )
            has_more = True
            while has_more:
                href = driver.current_url
                self.debug and print(f">>>{href}")
                
                cards = driver.find_elements_by_class_name("result-card")
                try:
                    driver.find_element_by_xpath("//div[@class='show-block show-more']").click()
                    time.sleep(2)
                except Exception as e:
                    pass

                for c in cards:
                    try:
                        d = c.find_element_by_class_name("result-title") 
                        self.debug and print(f"+ {d.text}")
                        click = d.get_attribute("onClick")
                        if click:
                            a = c.find_element_by_class_name("address") # class="ui_columns is-mobile result-content-columns"
                            address = a.text.strip().lower()
                            if address[-1*len(country.lower()):] == country.lower():
                                csv.write("{}\n".format(click))
                    except Exception as e:
                        print(e)

                csv.flush()
                pagination = driver.find_element_by_class_name("pagination-block")
                driver.execute_script(f"window.scrollTo(0, {pagination.location['y']});")

                next_button = pagination.find_elements_by_xpath('.//a')[1]
                time.sleep(2)
                if next_button and next_button.text == "Next" and next_button.get_attribute("class").strip() == "ui_button nav next primary":
                    driver.execute_script("arguments[0].click();", next_button)
                else:
                    has_more = False
                time.sleep(2)
        driver.close()

    def fetch_attraction_reviews(self, url, cat, review_file):
        driver = webdriver.Chrome(executable_path=self.driver_path)

        with open(review_file, 'a', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            self.info and print(f"# GET ATTRACTION: {url}")
            driver.get(url)
                
            time.sleep(5)
            # loop until all reviews pages are done
            has_more = True
            recview_counter = 0
            while has_more:
                try:
                    # try to click on show more button
                    driver.find_element_by_xpath("//div[@id='tab-data-qa-reviews-0']/div/div[5]/button").click()
                except Exception:
                    pass

                # get all reviews
                reviews = driver.find_elements_by_xpath("//div[@id='tab-data-qa-reviews-0']/div/div[5]/div")
                if len(reviews) == 0: # it has possibly different format
                    reviews = driver.find_elements_by_xpath("//div[@data-test-target='reviews-tab']/div/div")
                    print(f"review counts = {len(reviews)}")
                    for review_elm in reviews:
                        recview_counter += 1
                        self.debug and print(f".{recview_counter}", end="")
                        try:
                            elm = review_elm.find_element_by_xpath("./div/div[@data-test-target='review-title']/a")
                            title = elm.text
                            ancher = elm.get_attribute("href")
                            self.debug and print(f"title={title}")
                            rating = 0.1 * (int)(review_elm.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])
                            self.debug and print(f"rating={rating}")
                            r = review_elm.find_element_by_xpath(".//*[name()='q']")
                            review = r.text.replace("\n", " ").strip()
                            self.debug and print(f"review={review}")
                            
                            d = review_elm.find_element_by_xpath(".//span/span[text()='Date of experience:']/parent::node()")
                            date = d.text.split(":")[1].strip()
                            self.debug and print(f"date={date}")

                            csv_writer.writerow([ancher, url, cat, date, rating, title, review]) 
                        except Exception as e:
                            self.debug and print(f"Error: {e}")
                    # change the page
                    try:
                        driver.find_element_by_class_name('next').click()
                        time.sleep(2)
                    except Exception:
                        has_more = False
                else:
                    review_elm = None
                    for review_elm in reviews:
                        recview_counter += 1
                        self.debug and print(f".{recview_counter}", end="")
                        self.debug and print(driver.current_url)
                        try:
                            rating = review_elm.find_element_by_xpath("./span/span/div[3]/*[name()='svg']").get_attribute("title").split(" ")[0]
                            self.debug and print(f"rating={rating}")
                            t = review_elm.find_element_by_xpath("./span/span/div[4]/a")
                            title = t.text
                            self.debug and print(f"title={title}")
                            ancher = t.get_attribute("href")
                            try:
                                r = review_elm.find_element_by_xpath("./span/span/div[6]/div/div/span")
                                review = r.text.replace("\n", " ").strip()
                                self.debug and print(f"review={review}")

                                d = review_elm.find_element_by_xpath("./span/span/div[5]")
                                date = d.text
                                self.debug and print(f"date={date}")
                            except Exception:
                                r = review_elm.find_element_by_xpath("./span/span/div[5]/div/div/span")
                                review = r.text.replace("\n", " ").strip()
                                self.debug and print(f"review={review}")
                                try: 
                                    # without images
                                    d = review_elm.find_element_by_xpath("./span/span/div[7]/div")
                                    date = d.text
                                    self.debug and print(f"date={date}")
                                except Exception:
                                    # with images
                                    d = review_elm.find_element_by_xpath("./span/span/div[8]/div")
                                    date = d.text
                                    self.debug and print(f"date={date}")

                            csv_writer.writerow([ancher, url, cat, date, rating, title, review]) 
                        except Exception as e:
                            print(e)
                                # pass
                    # click on the next button
                    try:
                        # print(review_elm.find_element_by_xpath(".//a[@aria-label='Next page']").get_attribute("innerHTML"))
                        review_elm.find_element_by_xpath(".//a[@aria-label='Next page']").click()
                        time.sleep(2)
                        self.debug and print("- next page -")
                    except Exception:
                        has_more = False
            csv_writer.writerow(["-", url, "-", "-", "-", "-", "-"]) 
        driver.close()

    def fetch_hotel_reviews(self, url, cat, review_file):
        with open(review_file, 'a', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            self.debug and print(f"# GET HOTEL: {url}")
            driver = webdriver.Chrome(executable_path=self.driver_path)
            driver.get(url)
                
            time.sleep(5)
            # loop until all reviews pages are done
            has_more = True
            recview_counter = 0
            while has_more:
                # get all reviews
                reviews = driver.find_elements_by_xpath("//div[@data-test-target='HR_CC_CARD']")
                self.debug and print(f"Total reviews: {len(reviews)}")
                if len(reviews) == 0:
                    has_more = False
                for i in range(len(reviews)):
                    recview_counter += 1
                    review_elm = reviews[i]
                    self.debug and print(f".{recview_counter}", end="")
                    try:
                        elm = review_elm.find_element_by_xpath("./div/div[@data-test-target='review-title']/a")
                        title = elm.text
                        ancher = elm.get_attribute("href")
                        self.debug and print(f"title={title}")
                        rating = 0.1 * (int)(review_elm.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3])
                        self.debug and print(f"rating={rating}")
                        r = review_elm.find_element_by_xpath(".//*[name()='q']")
                        review = r.text.replace("\n", " ").strip()
                        self.debug and print(f"review={review}")
                        
                        # d = review_elm.find_element_by_xpath("./div[2]/div[3]/div[2]/span")
                        div = review_elm.find_element_by_xpath("./div/div[@data-test-target='review-title']/following-sibling::div")
                        d = div.find_element_by_xpath(".//span/span[text()='Date of stay:']/parent::node()")
                        date = d.text.split(":")[1].strip()
                        # date = date.split("\n")[0]
                        self.debug and print(f"date={date}")

                        csv_writer.writerow([ancher, url, cat, date, rating, title, review]) 
                    except:
                        pass
                # change the page
                try:
                    driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()
                    time.sleep(2)
                except Exception:
                    has_more = False
            csv_writer.writerow(["-", url, "-", "-", "-", "-", "-"]) 
            driver.close()

    def fetch_restaurant_reviews(self, url, cat, review_file):
        with open(review_file, 'a', encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            self.info and print(f"get restaurant {url}")
            driver = webdriver.Chrome(executable_path=self.driver_path)
            driver.get(url)
            time.sleep(5)
            # change the value inside the range to save more or less reviews
            has_more = True
            while has_more:
                # expand the review 
                csv_file.flush()
                containers = driver.find_elements_by_xpath(".//div[@class='review-container']")

                if len(containers) == 0:
                    has_more = False
                for container in containers:
                    try:
                        elm = container.find_element_by_xpath(".//div[@class='quote']/a")
                        title = elm.text
                        ancher = elm.get_attribute("href")
                        self.debug and print(f"title={title}")
                        rating = container.find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3]
                        self.debug and print(f"rating={rating}")
                        date = container.find_element_by_xpath(".//span[contains(@class, 'ratingDate')]").get_attribute("title")
                        self.debug and print(f"date={date}")
                        try:
                            more = driver.find_element_by_xpath(".//span[@class='taLnk ulBlueLinks']")
                            print(f"text = {more.text}")
                            if more.text == "More":
                                more.click()
                        except Exception:
                            pass
                        review = container.find_element_by_xpath(".//p[@class='partial_entry']").text.replace("\n", " ").strip()
                        self.debug and print(f"review={review}")

                        csv_writer.writerow([ancher, url, cat, date, rating, title, review]) 
                    except Exception:
                        pass
                # change the page
                try:
                    driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()
                    time.sleep(2)
                except Exception:
                    has_more = False
            # print(len(link_counter))
            csv_writer.writerow(["-", url, "-", "-", "-", "-", "-"]) 
            driver.close()

    def _get_keywords(self, keyword_file):
        keywords = []
        with open(keyword_file, "r", encoding="utf8") as kf:
            lines = kf.readlines()
            for l in lines:
                l = l.strip().lower()
                if l == "": 
                    continue
                else:
                    keywords.append(l)
        return keywords
    def _get_all_reviews(self, review_file):
        all_reviews = []
        with open(review_file, "r", encoding="utf8") as kf:
            lines = kf.readlines()
            for l in lines:
                l = l.strip()
                if l != "":
                    all_reviews.append(l)
        return all_reviews

    def filter_authenticity(self, authenticity_type, keyword_file, review_file, output_folder):
        keywords = self._get_keywords(keyword_file)
        # regexes = []
        # get old reviews to skip
        auth_reviews = ""
        if os.path.exists(f"{output_folder}/{authenticity_type}.txt"):
            with open(f"{output_folder}/{authenticity_type}.txt", "r", encoding="utf8")  as output:
                auth_reviews = "#".join( output.readlines() )

        all_reviews = self._get_all_reviews(review_file)

        with open(f"{output_folder}/{authenticity_type}.txt", "a", encoding="utf8")  as output:
            for review in all_reviews:
                if  review in auth_reviews:
                    continue
                rv_lower = ",".join(review.split(",")[4:]).lower()
                relevant_keywords = []
                for k in keywords:
                    to_search = r'\b'+k+r'\b'
                    if "******" in k:
                        to_search = r'\b'+ k.replace("******", r"\w+") +r'\b'
                    try:
                        if re.search(to_search, rv_lower):
                            relevant_keywords.append(k)
                    except Exception as e:
                        print(f"searching: {to_search}")
                        print(e)
                if len(relevant_keywords) > 0:
                    output.write(";".join(relevant_keywords) + "," + review + "\n")