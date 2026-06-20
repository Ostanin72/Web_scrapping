from time import sleep

import bs4
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


# Определяем список ключевых слов:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Определяем url сайта:
URL = 'https://habr.com/ru/all/'


# Функция получения текста со страницы статей
def get_data(driver):
    try:
        articles_block = driver.find_element(By.TAG_NAME, 'main')
        articles_list = articles_block.find_elements(
            By.CSS_SELECTOR, 'div.article-snippet'
        )
    except Exception as e:
        print("Не удалось найти список статей:", e)
        return []

    data = []
    for article in articles_list:
        try:
            time = article.find_element(
                By.CSS_SELECTOR, 'time'
            ).get_attribute('datetime')
            title_el = article.find_element(By.CSS_SELECTOR, 'h2 a')
            title = title_el.text.strip()
            link = title_el.get_attribute('href')

            text_els = article.find_elements(
                By.CSS_SELECTOR, 'div.article-formatted-body > p'
            )
            text = text_els[0].text.strip() if text_els else ""

            tags_els = article.find_elements(
                By.CSS_SELECTOR, 'a.tm-article-snippet__hubs-item-link'
            )
            tags_text = ' '.join([t.text.strip() for t in tags_els])

            data.append({
                'link': link,
                'title': title,
                'time': time,
                'text': text,
                'tags': tags_text,
            })
        except Exception as e:
            print(f"Ошибка при обработке статьи '{title[:30]}...'. "
                  f"Пропускаем. Ошибка: {e}")
            continue

    return data


# Функция поиска статей по ключевым словам со страницы статей
def get_keywords(keywords, articles_data):

    result_data = []

    for article in articles_data:
        title = article['title']
        text = article['text']
        tags = article['tags']

        if any(
            (keyword.lower() in title.lower()
             or keyword.lower() in text.lower()
             or keyword.lower() in tags.lower())
            for keyword in keywords
        ):

            result_data.append({
                'time': article['time'],
                'title': article['title'],
                'link': article['link'],
            })

    return result_data


# Функция получения текста со страницы статьи
def get_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)

        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.text, features='lxml')

        body_div = soup.find('div', class_='article-formatted-body')

        if body_div:
            return body_div.text.strip()
        else:
            print(f"Блок с текстом не найден на странице: {url}")
            return ""

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к {url}: {e}")
        return ""
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return ""


# Функция поиска не выбранных статей
def get_unique_links(get_data, result_data):
    links_from_get_data = {
        item['link'] for item in get_data if 'link' in item
    }
    links_in_result_data = {
        item['link'] for item in result_data if 'link' in item
    }
    unique_links = links_from_get_data - links_in_result_data
    filtered_data = [
        item for item in get_data if 'link' in item
        and item['link'] in unique_links
    ]

    return filtered_data


# Функция поиска статей по ключевым словам по тексту статей
def get_data_text(keywords, filtered_data):
    result_text_data = []
    for article_info in filtered_data:
        text = get_text(article_info['link'])
        if any(keyword.lower() in text.lower() for keyword in keywords):
            result_text_data.append({
                'link': article_info['link'],
                'title': article_info['title'],
                'time': article_info['time']
            })

    return result_text_data


def main():
    driver = Chrome()
    try:
        driver.get(URL)
        sleep(5)

        data = get_data(driver)
        result_data = get_keywords(KEYWORDS, data)
        for result in result_data:
            print(f"{result['time']} - {result['title']} - {result['link']}")

        print('Дополнительный поиск по тексту статей')
        filtered_data = get_unique_links(data, result_data)
        result_text_data = get_data_text(KEYWORDS, filtered_data)
        for result in result_text_data:
            print(f"{result['time']} - {result['title']} - {result['link']}")
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
