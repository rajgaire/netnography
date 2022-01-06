To run this script, you need chrome driver for the version of the chrome install in your computer. Check the chrome version by opening your chrome browser and visiting [chrome://version/]. Note the version number, then visit [https://chromedriver.chromium.org/downloads] and download the matching version of chromedriver. If the file is in a zip format, extract the files and copy them over to ./chrome_driver_win32/ folder to replace chromedriver.exe file.

Use the following command to run the script:
```bash
python main.py -p <place> -c <country>
```

For example,
```bash
python main.py -p "Patan (Lalitpur)" -c Nepal
```

The script makes chrome to visit tripadvisor, create a file in ./tmp/`<country>`/`<place>`.txt file and save all the links to things like attactions, restaurants, hotels and activities at the place.

Then it makes chrome to visit each of the link one by one (you will notice chrome opening and closing), and collect reviews in those webpages. The reviews are saved in ./output/`<country>`/`<place>`.txt file.

The reviews are then assessed against authenticity keywords saved in /netnography/keywords/ folder. Matching reviews are saved in ./output/`<country>`/constructive-authenticity.csv, ./output/`<country>`/existential-authenticity.csv and ./output/`<country>`/object-authenticity.csv files.