# NCHSA Volleyball Data Scraper
Scrapes data from the webpage: https://www.nchsaa.org/news/2022-10-20/2022-volleyball-final-rpi-rankings

## How to set it up
1. Install python version 3.10
2. Run the commands:
```bash
python -m pip install --upgrade pip
python -m pip install pipenv
python -m pipenv install
python -m pipenv shell
```
3. (Optional) Update the links used for webscraping
```bash
python get_urls.py
```

4. Run the command 
```bash
python scraper.py
```
