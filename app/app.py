
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


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

def make_a_soup(browser, url, item):
    race_day_url = f'{url}/{item}'


    time.sleep(3)
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

    return answer, item

def dict_to_scrap(answer, item):
    soup = BeautifulSoup(answer, 'html.parser')
    healthsoup = soup.find_all('li', class_='item ng-star-inserted')
    dictSup = {}
    for elem in healthsoup :
        dictSub = {}
        product_id_element = elem.select_one('[data-cy^="product-name"]')
        if product_id_element:
            key = product_id_element['data-cy'].split('-')[-1]
        dictSub = {}
        dictSub['Brand'] = elem.find('lsp-product-name').find('div').find('span').text.strip()
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
        dictSub['Product'] = product_name
        price_span = elem.find('span', class_='actual')
        if price_span:
            dictSub['Prix'] = price_span.text.strip()
        else:
            dictSub['Prix'] = "0"
        original_price_span = elem.find('span', id=f'{key}-original-price')
        if original_price_span:
            dictSub['Prix Original'] = original_price_span.text.strip()
        else:
            dictSub['Prix Original'] = "0"
        try :
            dictSub['Comment'] = elem.find('lsp-product-badge').text.strip()
        except :
            None
        dictSub['Quantity'] = elem.find('lsp-product-quantity').text.strip()
        try :
            dictSub['Image'] = elem.find('img', class_='ng-star-inserted')['src']
        except :
            None
        dictSub['Categorie'] = item
        dictSup[key] = dictSub

    return dictSup
