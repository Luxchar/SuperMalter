from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import asyncio
import time

proxy_pool = [
    'proxy1:port',
]

def get_next_profile(df):
    """
    get the next profile to scrap
    
    Parameters:
    df (pd.DataFrame): the dataframe with the profiles to scrap
    """
    
    next_profile = df[df['scraped']==False].iloc[0] # get the next profile to scrap
    # update the df
    df.loc[df['profil']==next_profile['profil'], 'scraped'] = True
    return df, next_profile


df_raw = pd.DataFrame(columns=['name', 'profile_image', 'headline', 'experience', 'price', 'response_rate', 'response_time', 'categories', 'competences', 'supermalter', 'location','presentation', 'recommendations', 'missions', 'teletravail_preference', 'profil', 'link', 'creation_date'])

index = 0
def add_to_df(data): # save the data in a global df
    """
    Add the user data to the global DataFrame df_raw and save it to a CSV file every 1000 users.
    
    Parameters
    ----------
    data : dict
        A dictionary containing the user data.
    """
    
    global df_raw, index_scrap
    
    user_df = pd.DataFrame([data])  # Convert the user data to a DataFrame
    
    # Check if the user DataFrame has the same columns as df_raw
    if user_df.columns.tolist() != df_raw.columns.tolist():
        # If the columns don't match, ensure they align and reorder columns accordingly
        user_df = user_df.reindex(columns=df_raw.columns)
    
    # Append the user DataFrame to df_raw
    df_raw = pd.concat([df_raw, user_df], ignore_index=True)
    
    time = pd.Timestamp.now() # get the current time
    print(f'Scraped {index} users, at {time} last one is: {data}')
    
    # Save the DataFrame to a CSV file every 1000 users
    if index_scrap % 1000 == 0:
        df_raw.to_csv('scraped_data_final.csv', index=False)

def scrap_user(row, driver):
    """ 
    Scrap the user data from the given row and add it to the global DataFrame df_raw.
    
    Parameters
    ----------
    row : pandas.Series
        A row from the DataFrame df.
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        The Selenium driver used to scrap the user data.
    """
    
    try:
        wait = WebDriverWait(driver, 10)
        driver.get(row['link'])
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
    except:
        print('error couldnt fetch the page')
        driver.quit()
        return None

    data = {}
    
    # get link of profile image
    profile_image_element = soup.find('div', class_='joy-avatar joy-avatar__large joy-avatar__secondary')
    if profile_image_element:
        profile_image = profile_image_element.find('img')['src']
        data['profile_image'] = profile_image
    else:
        data['profile_image'] = 'No profile image'

    price_element = soup.find('div', {'data-testid': 'profile-price'})
    if price_element:
        price = price_element.find('span', class_='block-list__price').text
        data['price'] = price.strip()

    # Récupérer l'expérience
    experience_element = soup.find('span', string='Expérience')
    if experience_element:
        experience = experience_element.find_next('span', class_='profile-indicators-content').text
        data['experience'] = experience.strip()
    
    # Récupérer le taux de réponse
    response_rate_element = soup.find('span', string='Taux de réponse')
    if response_rate_element:
        response_rate = response_rate_element.find_next('span', class_='profile-indicators-content').text
        data['response_rate'] = response_rate.strip()
    
    # Récupérer le temps de réponse
    response_time_element = soup.find('span', string='Temps de réponse')
    if response_time_element:
        response_time = response_time_element.find_next('span', class_='profile-indicators-content').text
        data['response_time'] = response_time.strip()
        
    # Récupérer le nom 
    name_element = soup.find('div', {'data-testid': 'profile-fullname'})
    if name_element:
        name = name_element.text
        data['name'] = name.strip()
        
    # Récupérer le métier
    headline_element = soup.find('div', {'data-testid': 'profile-headline'})
    if headline_element:
        headline = headline_element.text
        data['headline'] = headline.strip()
        
    # Récupérer le nombre de missions
    missions_element = soup.find('div', {'data-testid': 'profile-counter-missions'})
    if missions_element:
        missions = missions_element.find('strong').text
        data['missions'] = missions.strip()
        
    # Récupérer toutes les catégories
    categories_elements = soup.find_all('li', {'class': 'categories__list-item'})
    categories = [category.find('a').text for category in categories_elements]
    data['categories'] = categories
    
    # Récupérer les compétences
    competences_element = soup.find_all('div', {'class': 'profile-expertises__content-list-item__label'})
    competences = [competence.find('a', class_='joy-link joy-link_teal').text.strip() for competence in competences_element]
    data['competences'] = competences
    
    # Récupérer le statut "Supermalter"
    supermalter_element = soup.find('span', class_='joy-badge-level__tag blue')
    if supermalter_element:
        supermalter = supermalter_element.get_text(strip=True)
        data['supermalter'] = supermalter
        
    # Récupérer la localisation
    location_element = soup.find('dl', {'class': 'profile__location-and-workplace-preferences__item'})
    if location_element:
        location_label = location_element.find('dt', {'data-testid': 'profile-location-address-label'})
        location_value = location_element.find('dd', {'data-testid': 'profile-location-preference-address'})

        if location_label and location_value:
            location = {location_label.text: location_value.text}
            data['location'] = location
            
    # Récupérer la préférence de télétravail
    teletravail_element = soup.find('dl', {'class': 'profile-page-mission-preferences__item'})
    if teletravail_element:
        teletravail_label = teletravail_element.find('dt')
        teletravail_value = teletravail_element.find('dd')

        if teletravail_label and teletravail_value:
            teletravail_preference = {teletravail_label.text: teletravail_value.text}
            data['teletravail_preference'] = teletravail_preference
            
    # Récupérer le nombre de recommandations
    recommendations_element = soup.find('span', {'data-testid': 'profile-counter-recommendations'})
    if recommendations_element:
        recommendations_count = int(recommendations_element.text.split()[0])
        data['recommendations'] = recommendations_count    

    # Récupérer le message de présentation
    presentation_element = soup.find('div', {'class': 'profile-description__content'})
    if presentation_element:
        presentation_message = presentation_element.get_text(strip=True)
        data['presentation'] = presentation_message
        
    # add link of the profile
    data['link'] = row['link']
    
    # add created date
    data['creation_date'] = row['creation_date']
    
    # add name to the data
    data['profil'] = row['profil']
        
    driver.quit() # close the browser

    add_to_df(data) # add the data to the global df

import threading

def configure_webdriver(proxy_address):
    """
    Configure the Selenium driver with the given proxy address.
    
    Parameters
    ----------
    proxy_address : str
        The proxy address to use for the Selenium driver.
    """
    
    # define custom options for the Selenium driver
    options = Options()

    options.add_argument(f'--proxy-server={proxy_address}')
    options.add_argument("window-size=800,400")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    # create the ChromeDriver instance with custom options
    # driver = webdriver.Remote("http://192.168.0.250:4444/wd/hub", options=options) # for docker
    driver = webdriver.Chrome(options=options) # for local
    
    return driver
 
def scrap_all_users_proxy(proxy_addresses, df):
    """
    Scrap all the users from the given DataFrame df using the given proxy addresses.
    
    Parameters
    ----------
    proxy_addresses : list
        A list of proxy addresses to use for the Selenium driver.
    df : pandas.DataFrame
        A DataFrame containing the users to scrap.
    """
    
    global index # To keep track of the progress
    
    while df[df['scraped'] == False].shape[0] > 0:  # While there are profiles to scrap
        threads = []  # Store threads to manage them
        
        if len(proxy_addresses) > df[df['scraped'] == False].shape[0]: # If there are more proxies than profiles to scrap (to avoid length mismatch)
            proxy_addresses = proxy_addresses[:df[df['scraped'] == False].shape[0]]

        for proxy_address in proxy_addresses:
            driver = configure_webdriver(proxy_address)
            df, row = get_next_profile(df)

            # Create a thread for each scraping task
            thread = threading.Thread(target=scrap_user, args=(row, driver))
            threads.append(thread)
            thread.start()  # Start the thread
                        
            print(f'Trying to scrap profile {index} advancement: {round(index/df.shape[0]*100, 2)}%')
            index+=1
        
        # Wait for all threads to complete before proceeding
        for thread in threads:
            thread.join()

if __name__ == '__main__':
    profile_links = pd.read_csv('../datasets/profile_links.csv')
    profile_links['profil'] = profile_links['profil'].apply(lambda x: x.replace('https://www.malt.fr/profile/', ''))

    # add column link to the DataFrame
    profile_links['link'] = profile_links['profil'].apply(lambda x: f'https://www.malt.fr/profile/{x}')

    profile_links['scraped'] = False # add column scraped to the DataFrame

    df = profile_links

    def main():
        return scrap_all_users_proxy(proxy_pool, df)
    
    main()
    
    df_raw.to_csv('../datasets/df_raw_final.csv', index=False)