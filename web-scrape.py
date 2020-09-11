'''' Scrape the Amazon.com using requests and Beautiful Soup. Increasing the speed
using the Threading/Processing/Pool in python'''
import sys
import threading
from multiprocessing import Process, Queue, Pool, Manager
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
__author__ = "DJ Zevenbergen based off of Tushar SEth's repo at https://github.com/tseth92/web-scraper"
__email__ = "tusharseth93@gmail.com"

# use proxies in requests so as to proxy your request via a proxy server
# as some sites may block the IP if traffic generated by an IP is too high
proxies = {
    'http': 'http://134.119.205.253:8080',
    'https': 'http://134.119.205.253:8080',
}
startTime = time.time()
qcount = 0
links = []  # List to store name of the product
prices = []  # List to store price of the product
ratings = []  # List to store ratings of the product
# names = []
no_pages = 2


def get_data(pageNo, q):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get("https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances",
                     headers=headers)  # , proxies=proxies)
    #      r = requests.get("https://www.amazon.com/s?k=laptops&page=" +
    #  str(pageNo), headers=headers)  # , proxies=proxies)
    content = r.content
    soup = BeautifulSoup(content, "html5lib")
    # print(soup.encode('utf-8')) # uncomment this in case there is some non UTF-8 character in the content and
    # you get error

    response = r.content.decode('utf-8')
    resp = json.dumps(response)

    # print(response)

    # with open('data.txt', 'w') as outfile:

    #     soup.prettify()

    # print(soup.body)

    for d in soup.findAll('span', attrs={'class': 'aok-inline-block zg-item'}):
        # for d in soup.findAll('div', attrs={'class': 'sg-col-4-of-12 sg-col-8-of-16 sg-col-16-of-24 sg-col-12-of-20 sg-col-24-of-32 sg-col sg-col-28-of-36 sg-col-20-of-28'}):
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        link = d.find(
            'a', attrs={'class': 'a-link-normal'})
        #         link = d.find(
        # 'span', attrs={'class': 'a-size-medium a-color-base a-text-normal'})
        price = d.find('span', attrs={'class': 'p13n-sc-price'})
        rating = d.find('span', attrs={'class': 'a-icon-alt'})

        # name = d.find(
        #     'div', attrs={'class': 'p13n-sc-truncate p13n-sc-line-clamp-2 p13n-sc-truncate-mobile-type'})

        all = []

        if link is not None:
            all.append(link.get('href'))
        else:
            all.append("unknown-product")

        if price is not None:
            all.append(price.text)
        else:
            all.append('$0')

        if rating is not None:
            all.append(rating.text)
        else:
            all.append('-1')

        # if name is not None:
        #     all.append(name.string)
        # else:
        #     all.append('-1')
        q.put(all)

        # print("---------------------------------------------------------------")
results = []
if __name__ == "__main__":
    m = Manager()
    q = m.Queue()  # use this manager Queue instead of multiprocessing Queue as that causes error
    p = {}
    if sys.argv[1] in ['t', 'p']:  # user decides which method to invoke: thread, process or pool
        for i in range(1, no_pages):
            if sys.argv[1] in ['t']:
                print("starting thread: ", i)
                p[i] = threading.Thread(target=get_data, args=(i, q))
                p[i].start()
            elif sys.argv[1] in ['p']:
                print("starting process: ", i)
                p[i] = Process(target=get_data, args=(i, q))
                p[i].start()
        # join should be done in seperate for loop
        # reason being that once we join within previous for loop, join for p1 will start working
        # and hence will not allow the code to run after one iteration till that join is complete, ie.
        # the thread which is started as p1 is completed, so it essentially becomes a serial work instead of
        # parallel
        for i in range(1, no_pages):
            p[i].join()
    else:
        pool_tuple = [(x, q) for x in range(1, no_pages)]
        with Pool(processes=8) as pool:
            print("in pool")
            results = pool.starmap(get_data, pool_tuple)

    while q.empty() is not True:
        qcount = qcount+1
        queue_top = q.get()
        links.append(queue_top[0])
        prices.append(queue_top[1])
        ratings.append(queue_top[2])
        # names.append(queue_top[3])

    print("total time taken: ", str(time.time()-startTime), " qcount: ", qcount)
    # print(q.get())
    df = pd.DataFrame(
        {'Product Link': links, 'Price': prices, 'Ratings': ratings})
    print(df)
    df.to_csv('products.csv', index=False, encoding='utf-8')
