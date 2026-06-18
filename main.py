import bs4
import requests


# Определяем список ключевых слов:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']


# Функция получения текста со страницы статьи
def get_text(url):
    response = requests.get(url, timeout=5)
    soup = bs4.BeautifulSoup(response.text, features='lxml')
    text = soup.find(
        'div', class_='article-formatted-body'
    ).text.strip()
    return text


# Функция получения данных со страницы статей
def get_data():
    URL = 'https://habr.com/ru/articles'
    response = requests.get(URL)

    soup = bs4.BeautifulSoup(response.text, features='lxml')

    articles_block = soup.find('div', class_='tm-layout')
    articles_list = articles_block.find_all(
        'article', class_='tm-articles-list__item'
    )

    data = []
    for article in articles_list:
        time = article.find('time')['title']
        title_tag = article.find('h2', class_='tm-title')
        title = title_tag.text.strip()
        link = title_tag.find('a')['href']
        url_link = 'https://habr.com' + link
        text = get_text(url_link)

        data.append({
            'time': time,
            'title': title,
            'link': link,
            'text': text
        })

    return data


# Функция проверки статей о ключевым словам
def get_keywords(keywords):
    articles_data = get_data()

    # Проходим по каждой статье из полученного списка
    for article in articles_data:
        title = article['title']
        text = article['text']

        if any(
                (keyword.lower() in title.lower()
                 or keyword.lower() in text.lower())
                for keyword in keywords
        ):
            print(f"Совпадение найдено по словам: "
                  f"{', '.join(
                      [kw for kw in keywords
                       if kw.lower() in title.lower()
                       or kw.lower() in text.lower()]
                  )}")
            print(f"Время: {article['time']}")
            print(f"Заголовок: {article['title']}")
            print(f"Ссылка: https://habr.com/ru/articles{article['link']}")
            print('-' * 50)


if __name__ == '__main__':
    get_keywords(KEYWORDS)
