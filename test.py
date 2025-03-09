import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Функция для загрузки HTML-кода страницы с помощью requests
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка {response.status_code} при загрузке {url}")
            return None
    except requests.RequestException as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None

# Функция для поиска ссылок на страницы тендеров
def get_tender_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    tender_links = soup.find_all('a', href=lambda x: x and '/view/common-info.html' in x)
    return [f"https://zakupki.gov.ru{link['href']}" for link in tender_links]

# Функция для извлечения ссылки на печатную форму и даты размещения с помощью Selenium
def get_tender_data(driver, tender_url):
    driver.get(tender_url)
    try:
        # Ожидание загрузки элемента с датой размещения
        date_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[contains(text(), 'Размещено')]/following-sibling::span[@class='cardMainInfo__content']"
            ))
        )
        publish_date = date_element.text.strip()
    except:
        publish_date = "Дата не найдена"

    try:
        # Извлекаем ссылку на печатную форму
        print_form_link = driver.find_element(By.CSS_SELECTOR, 'a[href*="/printForm/view.html"]')
        print_form_url = print_form_link.get_attribute('href')
    except:
        print_form_url = "Ссылка не найдена"

    return print_form_url, publish_date

def main():
    # Настройка Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск в фоновом режиме
    driver = webdriver.Chrome(options=options)

    for page in range(1, 3):  # Обрабатываем страницы 1 и 2
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber={page}"
        print(f"Обрабатываем страницу: {url}")
        html = get_html(url)
        if html:
            tender_links = get_tender_links(html)
            print(f"Найдено {len(tender_links)} тендеров на странице {page}")
            for i, tender_url in enumerate(tender_links, 1):
                print(f"\n{i}. Обрабатываем тендер: {tender_url}")
                print_form_url, publish_date = get_tender_data(driver, tender_url)
                print(f"   Ссылка на печатную форму: {print_form_url}")
                print(f"   Дата размещения: {publish_date}")
        else:
            print(f"Не удалось загрузить страницу {url}")

    driver.quit()

if __name__ == "__main__":
    main()
