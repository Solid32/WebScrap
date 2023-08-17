from selenium import webdriver
from app.app import login_to_website, dict_to_scrap , make_a_soup, dict_links, make_a_dict, converter_final, converter_pièce
from app.params import *
import datetime
import pandas as pd
import os
import re
import numpy as np

from bs4 import BeautifulSoup

produc_list=['fruits-legumes','snacks-confiseries', 'viandes-poissons', 'produits-laitiers-ufs-plats-prep' , 'boulangerie-patisserie-petit-dej', 'pates-condiments-conserves' , 'surgeles' , 'boissons-cafe-the' , 'vins-bieres-spiritueux']
browser = webdriver.Firefox()
login_url = 'https://login.migros.ch/login'
# Replace with the actual login URL
login_to_website(browser, login_url, MAIL, PWD)
url = 'https://www.migros.ch/fr/category'
df = pd.DataFrame()


for elem in produc_list:
    print('************************************************************')
    print(f'Chargement des dictionnaires de liens pour {elem}')
    print('************************************************************')

    answer = make_a_dict(browser, url, elem)
    soup = BeautifulSoup(answer, 'html.parser')
    dictLex = dict_links(soup)

    for key, value in dictLex.items():
        print('************************************************************')
        print(f'Chargement des données de {value}')
        print('************************************************************')

        answers = make_a_soup(browser, 'https://www.migros.ch', key)
        soup = BeautifulSoup(answers, 'html.parser')
        data = dict_to_scrap(soup, elem, value)
        dftemp = pd.DataFrame.from_dict(data, orient='index')
        df = pd.concat([df, dftemp])
browser.close()

df = df.drop_duplicates()
df['Prix'] = df['Prix'].str.replace('.–$', '').astype(float)
df['Prix Original'] = df['Prix Original'].str.replace('.–$', '').astype(float)
df['Brut Quantity'] = df['Quantity'].apply(converter_final)
df['Prix au kilo'] = df['Prix']/df['Brut Quantity']
df['Prix à la pièce'] = df['Prix']/df['Quantity'].apply(converter_pièce)

colonnes = ['Prix à la pièce', 'Prix au kilo']
for colonne in colonnes:
    df[colonne] = df[colonne].replace([np.inf, -np.inf], 0)

current_directory = os.path.dirname(os.path.abspath(__file__))
excel_directory = os.path.join(current_directory, 'Xcl')
excel_file_path = os.path.join(excel_directory, f'scrapped_{datetime.datetime.today().date()}.xlsx')
df.to_excel(excel_file_path, engine='openpyxl')


print(f"La DataFrame a été sauvegardée dans le fichier Excel : {excel_file_path}")
