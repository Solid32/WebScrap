from selenium import webdriver
from app.app import login_to_website, dict_to_scrap , make_a_soup, dict_links, make_a_dict, converter_final, converter_pièce, prix_vrac
from app.params import *
import datetime
import pandas as pd
import os
import re
import numpy as np

from bs4 import BeautifulSoup

produc_list=['fruits-legumes', 'viandes-poissons', 'produits-laitiers-ufs-plats-prep' , 'boulangerie-patisserie-petit-dej', 'pates-condiments-conserves' ,'snacks-confiseries', 'surgeles' , 'boissons-cafe-the' , 'vins-bieres-spiritueux']
browser = webdriver.Firefox()
login_url = 'https://login.migros.ch/login'
login_to_website(browser, login_url, MAIL, PWD)
url = 'https://www.migros.ch/fr/category'
df = pd.DataFrame()
#Entrées manuelles pour les labels qui ne seront pas automatiquement ajoutés, ne pas oublier de mettre au pluriel!
checker = ['broccolis', 'épinards', 'dattes']

for elem in produc_list:
    print('************************************************************')
    print(f'Chargement des dictionnaires de liens pour {elem}')
    print('************************************************************')

    answer = make_a_dict(browser, url, elem)
    soup = BeautifulSoup(answer, 'html.parser')
    dictLex, checker_temp, titles = dict_links(soup)
    checker.extend(checker_temp)
    checker.extend(titles)

    for key, value in dictLex.items():
        print('************************************************************')
        print(f'Chargement des données de {value}')
        print('************************************************************')

        answers = make_a_soup(browser, 'https://www.migros.ch', key)
        soup = BeautifulSoup(answers, 'html.parser')
        selected_items = soup.find_all('li', class_='filter-item unselected ng-star-inserted')
        check = []
        for el in selected_items:
            temp = el.find('span', class_='filter-label').text.strip()
            check_temp = re.split(r'[&,]', temp)
            check.extend(check_temp)
        checker.extend(check)
        data = dict_to_scrap(soup, elem, value)
        dftemp = pd.DataFrame.from_dict(data, orient='index')
        df = pd.concat([df, dftemp])
browser.close()

checker = [elem.strip() for elem in checker]
checker_clean = list(set(item.lower() for item in checker))
df = df.drop_duplicates()
df['Prix'] = df['Prix'].str.replace('.–$', '').astype(float)
df['Prix Original'] = df['Prix Original'].str.replace('.–$', '').astype(float)
df['Brut Quantity'] = df['Quantity'].apply(converter_final)
df['Prix au kilo'] = df['Prix']/df['Brut Quantity']
df['Prix à la pièce'] = df['Prix']/df['Quantity'].apply(converter_pièce)

def labeler(x):
    scanned = []
    for ch in checker_clean:
        pattern = fr'\b{re.escape(ch.lower())}\b'
        pattern2 = fr'\b{re.escape(ch[:-1].lower())}\b'
        if re.search(pattern, x.lower()) or re.search(pattern2, x.lower()):
            scanned.append(ch)
    return ', '.join(scanned) if scanned else x

print('************************************************************')
print(f'Mise en place des labels')
print('************************************************************')
df['Labels'] = df['Produit'].apply(labeler)
df['Prix au kilo'] = df.apply(prix_vrac, axis=1)


colonnes = ['Prix à la pièce', 'Prix au kilo']
for colonne in colonnes:
    df[colonne] = df[colonne].replace([np.inf, -np.inf], 0)

df = df[['Marque', 'Produit', 'Prix', 'Quantity', 'Prix Original', 'Catégorie',
       'Sous-catégorie', 'Labels', 'Image', 'BIO', 'Commentaire', 'Brut Quantity',
       'Prix au kilo', 'Prix à la pièce']]

current_directory = os.path.dirname(os.path.abspath(__file__))
excel_directory = os.path.join(current_directory, 'Xcl')
excel_file_path = os.path.join(excel_directory, f'scrapped_{datetime.datetime.today().date()}.xlsx')
df.to_excel(excel_file_path, engine='openpyxl')


print(f"La DataFrame a été sauvegardée dans le fichier Excel : {excel_file_path}")
