#Import Libraries
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import time
import pygame
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
import pygame

#Loading Alarm Sound
pygame.mixer.init()  # Initialize the mixer module
pygame.mixer.music.load('Alarm04.wav')  # Load the sound file
pygame.mixer.music.play()

#Firefox browser
options = FirefoxOptions()
options.binary_location  = r'C:\Program Files\Mozilla Firefox\firefox.exe'
service=FirefoxService(executable_path='geckodriver.exe')

#Bilyoner account information to login
tc_kimlik_no = '' #TC Kimlik No 
bilyoner_password = '' #TC Kimlik No 

# Bilyoner Login Function
def bilyoner_login():
'''Opens Firefox browser and logins to Bilyoner account'''
    driver = webdriver.Firefox(service=service, options=options)
    time.sleep(3)
    driver.get("https://www.bilyoner.com/sans-oyunlari/zeplin")
    time.sleep(4)
    driver.find_element(By.CSS_SELECTOR, '[name="username"]').send_keys(tc_kimlik_no)
    driver.find_element(By.CSS_SELECTOR, '[name="password"]').send_keys(bilyoner_password)
    driver.find_element(By.XPATH, "//button[@title='GİRİŞ YAP']").click()
    time.sleep(8)
    #driver.refresh()
    #time.sleep(8)
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    return driver

# Odds history to csv function
def saver(insert_time,round_counts,odds):
'''Saves odds history to csv'''
    df = pd.DataFrame({'insert_time':insert_time, 'round_counts':round_counts,'odds':odds,'get_type':get_type})
    df.to_csv('zeplin.csv', index=False) 

def get_odds_history():
'''Gets the eisting odds history(last 100 rounds)'''
    odds_history = driver.find_element(By.XPATH, "//app-game-content/div/app-rounds-history/div[1]").get_property("innerText")
    odds_history = odds_history.replace('x','')
    odds_history = odds_history.split('\n')
    odds_history = [float(e) for e in odds_history]
    odds_history.reverse()
    return odds_history


def history_correction():
'''Fills missing odds after connection lost'''
    global round_no
    hist = get_odds_history()
    if odds_history[-10:] != hist[-10:]:
        search = []
        for i in range(len(hist)-9):
            search.append(hist[i:i+10])
        ind = search.index(odds_history[-10:])
        for e in hist[ind+10:]:
            round_no += 1
            print("Corrected Round: ",round_no, " odd:", e )
            odds_history.append(e)
            round_counts.append(round_no)
            insert_time.append(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            get_type.append('corrected round')

#Login to bilyoner account
driver = bilyoner_login()

#Create odd plot
fig = plt.figure(figsize=(16,12))
ax = fig.add_subplot(1, 1, 1)
plt.pause(2)


odds_history = get_odds_history()
round_counts = list(np.arange(1,len(odds_history)+1))
round_no = len(odds_history)
insert_time = [datetime.now().strftime("%d.%m.%Y %H:%M:%S") for e in range(99)]
get_type = ['last 99' for e in range(99)]

while round_no < 10000:
    try:
        if odds_history[-15:] != get_odds_history()[-15:]:
            round_no += 1
            odd = get_odds_history()[-1]
            print("Round: ",round_no, " odd:", odd)
            odds_history.append(odd)
            round_counts.append(round_no)
            insert_time.append(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            get_type.append('live')
            ax.plot(round_counts, odds_history)
            time.sleep(1)
            if round_no%15 == 0:
                saver(insert_time,round_counts,odds_history)
                time.sleep(1)
        else:
            i=0
            while odds_history[-15:] == get_odds_history()[-15:]:
                plt.pause(2)
                time.sleep(4)
                i += 1
                if i > 50:
                    print("timeout")
                    driver.quit()
                    plt.pause(1)
                    time.sleep(3)
                    driver = bilyoner_login()
                    i = 0
                    history_correction()
                    break
    except Exception as e:
        print(f"An exception occurred: {str(e)}")
        saver(insert_time,round_counts,odds_history)
        driver.quit()
        plt.pause(1)
        driver = bilyoner_login()
        history_correction()
