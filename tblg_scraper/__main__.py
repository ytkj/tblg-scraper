import time
import os
from typing import *
import chromedriver_binary
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas as pd


def driver_factory():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    d = webdriver.Chrome(options=options)
    return d


URL_FORMAT_FOR_LIST = 'https://tabelog.com/atw/rvw/COND-0-2-1-0/D-edited_at/{0}/?LstRange=&rvw_part=all&sw='
FILE_NAME = 'result_20190622.csv'


def count_reviews() -> int:

    d = driver_factory()
    d.get('https://tabelog.com/atw/rvw/')
    page_count_elements = d.find_element_by_class_name('c-page-count').find_elements_by_class_name('c-page-count__num')
    count_str = page_count_elements[2].find_element_by_tag_name('strong').text
    try:
        count = int(count_str)
    except ValueError:
        count = 10329151

    return count


def get_review_comment(page_url: str) -> str:
    d = driver_factory()
    d.get('https://tabelog.com' + page_url)
    inner_html = d.find_element_by_class_name('rvw-item__rvw-comment') \
        .find_element_by_tag_name('p').text
    d.quit()

    return inner_html.replace(os.linesep, '<br>')


driver = driver_factory()
n_reviews = count_reviews()
print('total pages: {0}'.format(n_reviews))
n_pages = n_reviews // 100 + 1
url_set = set()
is_first_row = True

for i_page in range(n_pages):

    print('page-{0}'.format(i_page + 1))
    url = URL_FORMAT_FOR_LIST.format(i_page + 1)
    driver.get(url)
    data = []

    for i_review, review_item in enumerate(driver.find_elements_by_class_name('rvw-item')):

        print('scraping {0}th review'.format(i_page * 100 + i_review))

        # review content
        try:
            clickable_element = review_item.find_element_by_css_selector('div.rvw-item__frame.js-rvw-clickable-area')
        except NoSuchElementException:
            print('no clickable element')
            continue
        review_url = clickable_element.get_attribute('data-detail-url')
        if review_url in url_set:
            continue
        else:
            url_set.add(review_url)

        try:
            content = get_review_comment(review_url)

            # get restaurant info
            restaurant_name_anchor = review_item.find_element_by_class_name('rvw-item__rst-name')
            restaurant_url = restaurant_name_anchor.get_attribute('href')
            restaurant_name = restaurant_name_anchor.text

            # rating
            rating = review_item.find_element_by_class_name('c-rating__val--strong').text

            # amount paid
            amount_paid_dinner, amount_paid_lunch = (
                el.text for el in review_item.find_elements_by_class_name('rvw-item__usedprice-price')
            )

            # review title
            try:
                title = review_item.find_element_by_class_name('rvw-item__title-target').find_element_by_tag_name('strong').text
            except NoSuchElementException:
                title = None

            data.append(
                (restaurant_name, restaurant_url, rating, amount_paid_dinner, amount_paid_lunch, title, content)
            )

            time.sleep(5)

        except Exception as e:
            print(e)
            print(review_url)

        break

    df = pd.DataFrame(data, columns=[
        'restaurant_name',
        'restaurant_url',
        'rating',
        'amount_paid_for_dinner',
        'amount_paid_for_lunch',
        'review_title',
        'review_content',
    ])
    if is_first_row:
        df.to_csv(FILE_NAME, encoding='utf-8', index=False)
        is_first_row = False
    else:
        df.to_csv(FILE_NAME, encoding='utf-8', index=False, mode='a', header=False)

