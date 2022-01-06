#!/usr/bin/python

# a script to scrape reviews from tripadvisor
from data_collector import ReviewCollector
import os
import sys, getopt

def main(argv):
    place = ''
    country = ''
    try:
        opts, args = getopt.getopt(argv,"hp:c:",["place=","country="])
    except getopt.GetoptError:
        print('main.py -p <place> -c <country>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -p <place> -c <country>')
            sys.exit()
        elif opt in ("-p", "--place"):
            place = arg
        elif opt in ("-c", "--country"):
            country = arg
    print(f"Search review for place {place} in country {country}")
    collector = ReviewCollector("chromedriver_win32/chromedriver.exe")
    output_folder = f"./output/{country}"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    collector.fetch_reviews(place, country, f"./output/{country}/{place}.txt")
    # self, authenticity_type, keyword_file, review_file, output_folder):
    collector.filter_authenticity("object-authenticity", "../../keywords/object-authenticity.txt", f"./output/{country}/{place}.txt", output_folder)
    collector.filter_authenticity("constructive-authenticity", "../../keywords/constructive-authenticity.txt", f"./output/{country}/{place}.txt", output_folder)
    collector.filter_authenticity("existential-authenticity", "../../keywords/existential-authenticity.txt", f"./output/{country}/{place}.txt", output_folder)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("usage: main.py -p <place> -c <country>")
        sys.exit(2)
    main(sys.argv[1:])
