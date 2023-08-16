
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def login_to_website(browser, login_url, username, password):
    browser.get(login_url)

    # Assuming there are input fields for username and password
    username_field = browser.find_element(By.ID, 'username')  # Change to the actual ID
    password_field = browser.find_element(By.ID, 'password')  # Change to the actual ID

    # Fill in the credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Submit the form
    password_field.submit()

def make_a_dict(browser, url, item):
    race_day_url = f'{url}/{item}'
    time.sleep(5)
    browser.get(race_day_url)
    wait = WebDriverWait(browser, 5)
    time.sleep(5)
    answer = browser.page_source

    return answer

def make_a_soup(browser, url, item):
    race_day_url = f'{url}/{item}'
    browser.get(race_day_url)
    wait = WebDriverWait(browser, 5)
    while True:
        try:
            bouton_voir_plus = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div[1]/lsp-shop/div/div/div/lsp-supermarket-container/main/div[1]/app-category-level-container/app-category-level1/div/div/app-products-display/div[2]/div/button")))
            bouton_voir_plus.click()
            time.sleep(3)
        except Exception as e:
            print("Bouton non trouvé ou erreur :", e)
            break
    answer = browser.page_source

    return answer

def dict_to_scrap(soup, item, Subitem):

    healthsoup = soup.find_all('li', class_='item ng-star-inserted')
    dictSup = {}
    for elem in healthsoup :
        dictSub = {}
        product_id_element = elem.select_one('[data-cy^="product-name"]')
        if product_id_element:
            key = product_id_element['data-cy'].split('-')[-1]
        dictSub = {}
        dictSub['Marque'] = elem.find('lsp-product-name').find('div').find('span').text.strip()
        product_name1 = elem.find('span', {'data-cy': f'product-name-{key}'})
        product_name2 = elem.find('span', {'data-cy': f'product-versioning-{key}'})
        if product_name1 and product_name2:
            product_name = product_name1.text.strip() + " " + product_name2.text.strip()
        elif product_name1:
            product_name = product_name1.text.strip()
        elif product_name2:
            product_name = product_name2.text.strip()
        else:
            product_name = "N/A"
        dictSub['Produit'] = product_name
        price_span = elem.find('span', id=f'{key}-current-price')
        if price_span:
            dictSub['Prix'] = price_span.text.strip()
        else:
            dictSub['Prix'] = "0"
        dictSub['Quantity'] = elem.find('lsp-product-quantity').text.strip()
        original_price_span = elem.find('span', id=f'{key}-original-price')
        if original_price_span:
            dictSub['Prix Original'] = original_price_span.text.strip()
        else:
            dictSub['Prix Original'] = "0"
        try :
            dictSub['Commentaire'] = elem.find('lsp-product-badge').text.strip()
        except :
            None
        dictSub['Catégorie'] = item
        dictSub['Sous-catégorie'] = Subitem
        try :
            dictSub['Image'] = elem.find('img', class_='ng-star-inserted')['src']
        except :
            None

        try:
            bio_image = elem.find('lsp-product-picto')
            dictSub['BIO'] = 1 if bio_image else 0
        except:
            dictSub['BIO'] = 0


        dictSup[key] = dictSub

    return dictSup





def dict_links(soup):
    links = soup.find_all('a' , id=lambda value: value and value.startswith('nav-level3-category'))
    dictLex = {}
    for link in links:
        key = link['href']
        value = link.get_text()
        dictLex[key] = value
    return dictLex

def converter_final(temp):
    converted = []
    elem = re.findall(r'\d+|\D+',temp)
    elem = temp.split()
    elem = [e.strip() for e in elem]
    try :
        if elem[1] == 'x' or elem[1] == 'X':
            temp = float(elem[0]) * float(elem[2])
            if elem[3] == 'kg' or elem[3] == 'l' or elem[3] == 'pièce' or elem[3] == 'pe':
                converted.append(temp)
            elif elem[3] == 'g' or elem[3] == 'ml':
                converted.append(temp / 1000)
            elif elem[3] == 'cl':
                converted.append(temp / 100)
            else:
                converted.append(0)
        elif elem[1] == 'kg' or elem[1] == 'l' or elem[1] == 'pièce' or elem[1] == 'pe':
            converted.append(float(elem[0]))
        elif elem[1] == 'cl':
            converted.append(float(elem[0]) / 100)
        elif elem[1] == 'g' or elem[1] == 'ml':
            converted.append(float(elem[0]) / 1000)

        else:
            converted.append(0)
    except:
        converted.append(0)
    return converted[0]
