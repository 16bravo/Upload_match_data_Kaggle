from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

chrome_path = 'chrome-driver/chromedriver'
driver = webdriver.Chrome(service=ChromeService(executable_path=chrome_path))
url = 'https://www.eloratings.net/latest'
driver.get(url)
wait = WebDriverWait(driver, 10)  # Attendez jusqu'à 10 secondes au maximum
table_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'maintable')))
html_content = driver.page_source
driver.quit()
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('div', class_='maintable')

# Initialisez des listes pour stocker les données
date = []
team1 = []
team2 = []
score1 = []
score2 = []
tournament = []
country = []

# Parcourez les lignes du tableau
for row in table.find_all('div', class_='slick-row'):
    
    date_text = row.find('div', class_='l0').get_text(separator='<br>').strip()
    date_list = date_text.split('<br>')
    date.append(date_list[0]+" "+date_list[1])
    
    match_text = row.find('div', class_='l1').get_text(separator='<br>').strip()
    match_list = match_text.split('<br>')
    team1.append(match_list[0])
    team2.append(match_list[1] if len(match_list) > 1 else '')

    score_text = row.find('div', class_='l2').get_text(separator='<br>').strip()
    score_list = score_text.split('<br>')
    score1.append(score_list[0])
    score2.append(score_list[1] if len(score_list) > 1 else '')

    tournament_text = row.find('div', class_='l3').get_text(separator='<br>').strip()
    tournament_text = tournament_text.replace("<br> & <br>", " and ")
    tournament_list = tournament_text.split('<br>')
    tournament.append(tournament_list[0])
    country.append(tournament_list[1] if len(tournament_list) > 1 else '')

# Créez un DataFrame pandas
df = pd.DataFrame({
    'date': date,
    'home_team': team1,
    'away_team': team2,
    'home_score': score1,
    'away_score': score2,
    'tournament': tournament,
    'country': country
})

df['country'] = df['country'].str.replace(r'^(in the |in )', '', regex=True)
df['neutral'] = (df['home_team'] == df['country'])
df['date'] = pd.to_datetime(df['date'], format='%b %d %Y')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

history_data = './dataset/all_matches.csv'
history_csv = pd.read_csv(history_data)
history_csv['date'] = pd.to_datetime(history_csv[['year', 'month', 'day']])
max_date = history_csv['date'].max()

df = df[df['date'] > max_date]

history_csv = pd.concat([history_csv, df])

# Affichez le DataFrame
history_csv.to_csv('./dataset/all_matches.csv')
