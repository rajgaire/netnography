#!/usr/bin/python

# a script to scrape reviews from tripadvisor
import sys
sys.path.append("../tripadvisor")
from data_collector import ReviewCollector

def main():
    # place = 'Patan (Lalitpur)'
    # country = 'Nepal'
    collector = ReviewCollector("../tripadvisor/chromedriver_win32/chromedriver.exe", True, True)
    # Test Attractions
    # test_url = "https://www.tripadvisor.com/Attraction_Review-g315764-d11045427-Reviews-Asian_Eco_Journeys-Patan_Lalitpur_Kathmandu_Valley_Bagmati_Zone_Central_Region.html"
    # collector.fetch_attraction_reviews(test_url, "Attraction", f"./temp_attraction.txt")
    # # Test Hotel
    # test_url = "https://www.tripadvisor.com//Hotel_Review-g315764-d6995667-Reviews-The_Inn_Patan-Patan_Lalitpur_Kathmandu_Valley_Bagmati_Zone_Central_Region.html"
    # collector.fetch_hotel_reviews(test_url, "Hotel", f"./temp_hotel.txt")
    # # Test Restaurant
    # test_url = "https://www.tripadvisor.com//Restaurant_Review-g315764-d1156668-Reviews-Patan_Museum_Cafe-Patan_Lalitpur_Kathmandu_Valley_Bagmati_Zone_Central_Region.html"
    # collector.fetch_restaurant_reviews(test_url, "Restaurant", f"./temp_restaurant.txt")
    test_url = "https://www.tripadvisor.com/AttractionProductReview-g315764-d19529632-Kathmandu_Sightseeing_Tour_with_car_and_Driver-Patan_Lalitpur_Kathmandu_Valley_Bag.html"
    collector.fetch_attraction_reviews(test_url, "Activity", f"./temp_activity.txt")


if __name__ == "__main__":
    main()
