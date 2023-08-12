from selenium import webdriver
from app.app import login_to_website, dict_to_scrap , make_a_soup
from app.params import *
import datetime
import pandas as pd
import os


produc_list=['fruits-legumes']#,'snacks-confiseries', 'viandes-poissons', 'produits-laitiers-ufs-plats-prep' , 'boulangerie-patisserie-petit-dej', 'pates-condiments-conserves' , 'surgeles' , 'boissons-cafe-the' , 'vins-bieres-spiritueux']
browser = webdriver.Firefox()
login_url = 'https://login.migros.ch/login'
# Replace with the actual login URL
login_to_website(browser, login_url, MAIL, PWD)
url = 'https://www.migros.ch/fr/category'
df = pd.DataFrame()
for item in produc_list :
    print('************************************************************')
    print(f'Chargement des données de {item}')
    print('************************************************************')
    answer, item = make_a_soup(browser, url, item)
    data = dict_to_scrap(answer)
    dftemp = pd.DataFrame.from_dict(data, orient ='index')
    df = df.append(dftemp)

browser.close()

df = df.drop_duplicates()
current_directory = os.path.dirname(os.path.abspath(__file__))
excel_directory = os.path.join(current_directory, 'Xcl')
excel_file_path = os.path.join(excel_directory, f'scrapped_{datetime.datetime.today().date()}.xlsx')
df.to_excel(excel_file_path, engine='openpyxl')


print(f"La DataFrame a été sauvegardée dans le fichier Excel : {excel_file_path}")
