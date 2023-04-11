# -*- coding: utf-8 -*-
#harvest theses from Waseda
#JH: 2019-04-03

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3
import re

publisher = 'Waseda U.'
recs = []
years = 2
skipalreadyharvested = True
jnlfilename = 'THESES-WASEDA-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

with Session() as session:
    index: str = "https://waseda.repo.nii.ac.jp/index.php?action=pages_view_main&active_action" \
                 "=repository_view_main_item_snippet&index_id=338&pn=1&count=20&order=7&lang=japanese&page_id=13" \
                 "&block_id=21"

    index_resp = session.get(index)

    if index_resp.status_code != 200:
        print("# Error: Can't open page ({})".format(index))
        exit(0)

    index_soup = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml')

    tables = index_soup.find_all('table', attrs={'class': 'list_table'})

    for table in tables:
        for tr in table.find_all('tr'):
            cols = tr.find_all('td')
            if len(cols) >= 2:

                if len(cols[1].find_all('span')) != 0:
                    a = cols[1].find_all('span')[0].find_all('a')[0]
                    year_link = a.get('href')
                    print(year_link)

                    if re.search('20\d\d', a.text):
                        year = int(re.sub('.*?(20\d\d).*', r'\1', a.text.strip()))
                        print('  ', year)
                        if year <= ejlmod3.year(backwards=years):
                            continue
                    year_resp = session.get(year_link)

                    if year_resp.status_code != 200:
                        print("# Error: Can't open page ({})".format(year_link))
                        continue

                    year_soup = BeautifulSoup(year_resp.content.decode('utf-8'), 'lxml')

                    articles = year_soup.find_all('div', attrs={'class': 'item_title'})

                    if not articles:
                        articles = []
                        for table in year_soup.find_all('table', attrs={'class': 'list_table'}):
                            #print('     table')
                            for a in table.find_all('a'):
                                #print('       ', a)
                                if a.has_attr('href') and re.search('index_id', a['href']) and re.search('20', a.text):
                                     subyear_link = a['href']
                                     print('         ', subyear_link)
                                     subyear_resp = session.get(subyear_link)
                                     subyear_soup = BeautifulSoup(subyear_resp.content.decode('utf-8'), 'lxml')
                                     for article in subyear_soup.find_all('div', attrs={'class': 'item_title'}):
                                         #print('            article')
                                         articles.append(article)
                                     sleep(3)                            
                                     
                    for article in articles:
                        article_link = article.find_all('a')[0].get('href')

                        print("# Harvesting data:", article_link)
                        article_resp = session.get(article_link)
                        sleep(5)

                        if article_resp.status_code != 200:
                            print("# Error! Can't open article page:", article_link)
                            continue

                        article_soup = BeautifulSoup(article_resp.content.decode('utf-8'), 'lxml')
                        
                        oai = article_soup.find_all('img', attrs={'src': 'https://waseda.repo.nii.ac.jp/images'
                                                                         '/repository/default/oai_pmh.png'})
                        if len(oai) == 1:
                            data_link = oai[0].parent.get('href')

                            data_resp = session.get(data_link)

                            if data_resp.status_code != 200:
                                print("# Error! Can't access data:", article_link)
                                continue

                            data_soup = BeautifulSoup(data_resp.content.decode('utf-8'), 'xml')

                            rec = {'tc': 'T', 'jnl': 'BOOK', 'link' : article_link}

                            metadata = data_soup.find('metadata')
                            rec['tit'] = metadata.find('title').text
                            if metadata.find('language').text == 'jpn':
                                rec['language'] = 'japanese'
                            splitted_hdl = metadata.find('URI').text.split('/')
                            rec['hdl'] = '{}/{}'.format(splitted_hdl[-2], splitted_hdl[-1])
                            if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                                continue
                            # Get the creator
                            rec['autaff'] = [[metadata.find('creator').text, publisher]]

                            # Pages
                            try:
                                rec['pages'] = int(metadata.find('epage').text) - int(metadata.find('spage').text)
                            except:
                                pass
                            try:
                                rec['transtit'] = metadata.find('alternative').text
                            except:
                                pass
                            rec['date'] = metadata.find('dateofgranted').text
                            ejlmod3.metatagcheck(rec, article_soup, ['citation_pdf_url'])
                            recs.append(rec)
                            ejlmod3.printrecsummary(rec)
                            sleep(5)                            
                        sleep(5)
            sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
