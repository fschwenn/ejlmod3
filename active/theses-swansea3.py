# -*- coding: utf-8 -*-
#harvest theses from Swansea
#JH: 2019-11-21
#FS: 2023-04-27

from bs4 import BeautifulSoup
from time import sleep
import urllib.request, urllib.error, urllib.parse
from json import loads
import urllib.parse
import ejlmod3
import sys
import os
import re

recs = []

publisher = 'Swansea U.'
jnlfilename = 'THESES-SWANSEA-%s' % (ejlmod3.stampoftoday())
pages = 2+5
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def http_request(url):
    try:
        soup = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url), features="lxml")
        req = urllib.request.Request(url, headers=hdr)
        soup = BeautifulSoup(urllib.request.urlopen(req).read(), 'lxml')
    except:
        sleep(60)
        req = urllib.request.Request(url, headers=hdr)
        soup = BeautifulSoup(urllib.request.urlopen(req).read(), 'lxml')
    return soup


def get_subside(url):
    print("["+ url + "] --> Harvesting data")
    rec = {'tc' : 'T', 'jnl' : 'BOOK'}
    try:
        soup = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url), features="lxml")
        ejlmod3.metatagcheck(rec, soup, ['citation_author', 'citation_doi'])
        rec['autaff']
    except:
        try:
            sleep(60)
            soup = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url), features="lxml")
            ejlmod3.metatagcheck(rec, soup, ['citation_author', 'citation_doi'])
        except:
            return
            

    # Get the title
    title_section = soup.find_all('strong', attrs={'property': 'name'})
    if len(title_section) == 1:
        rec['tit'] = title_section[0].text

    # Get the author's name
    author_section = soup.find_all('span', attrs={'property': 'author'})
    if len(author_section) == 1:
        rec['autaff'] = [[author_section[0].text ]]
        if not 'autaff' in list(rec.keys()):
            for meta in soup.find_all('meta', attrs={'name' : 'citation_author'}):
                rec['autaff'] = [[ meta['content'] ]]
    if not 'autaff' in list(rec.keys()):
        print('   no author found')
        return
    else:
        rec['autaff'][-1].append(publisher)

    # Get DOI
    doi_section = soup.find_all('a', attrs={'class': 'online'})
    if len(doi_section) == 1:
        rec['doi'] = doi_section[0].text

    # Get the abstract
    table_section = soup.find_all('div', attrs={'class': 'description-tab'})
    if len(table_section) == 1:
        table_rows = table_section[0].find_all('tr')
        for tr in table_rows:
            table_header = tr.find_all('th')
            if len(table_header) > 0:
                if table_header[0].text.find('Abstract') != -1:
                    abstract_raw = tr.find_all('td')
                    if len(abstract_raw) == 1:
                        rec['abs'] = abstract_raw[0].text.replace('\n', '').replace('                  ', '')

    details_section = soup.find_all('table', attrs={'summary': 'Bibliographic Details'})
    if len(details_section) == 1:
        for tr in details_section[0].find_all('tr'):
            th = tr.find_all('th')
            td = tr.find_all('td')

            if len(th) == 1 and len(td) == 1:
                # Get the URL
                if th[0].text.find('URI') != -1:
                    rec['link'] = td[0].text

                # Get Publish Date
                if th[0].text.find('Published') != -1:
                    rec['year'] = td[0].text.split('\n')[-3]
                # Get Supervisor
                if th[0].text.find('Supervisor') != -1:
                    supervisors = td[0].text.split(';')
                    rec['supervisor'] = []
                    for i in supervisors:
                        rec['supervisor'].append([i])
                    #print rec['supervisor']

    # Get the pdf link
    pdf_section = soup.find_all('a', attrs={'class': 'file-download'})
    if len(pdf_section) == 1:
        pdf_link = pdf_section[0].get('href')
        rec['hidden'] = "https://cronfa.swan.ac.uk" + pdf_link
    
    # Get the Keywords
    description_table = soup.find_all('table', attrs={'summary': 'Description'})
    if len(description_table) == 1:
        rows = description_table[0].find_all('tr')
        for tr in rows:
            th = tr.find_all('th')
            if len(th) == 1:
                if th[0].text.find('Keywords') != -1:
                    rec['keyw'] = tr.find_all('td')[0].text.replace('\n', '').replace('                  ', '').split(', ')

    #pseudoDOI
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/Swansea/' + re.sub('\W', '', url[20:])

    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

# Get Index Pages

for page in range(1, pages+1):
    url = "https://cronfa.swan.ac.uk/Search/Results?type=AllFields&sort=year&filter%5B%5D=college_str%3A%22College+of+Science%22&filter%5B%5D=format%3A%22E-Thesis%22&page=" + str(page)
    url = 'https://cronfa.swan.ac.uk/Search/Results?join=AND&bool0%5B%5D=AND&lookfor0%5B%5D=&type0%5B%5D=AllFields&filter%5B%5D=%7Eformat%3A%22E-Thesis%22&filter%5B%5D=college_str%3A%22Faculty+of+Science+and+Engineering%22&page=' + str(page)
    ejlmod3.printprogress('=', [[page, pages], [url]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url), features="lxml")
    sleep(5)
    for link in tocpage.find_all('a', attrs={'class': 'title'}):
        get_subside("https://cronfa.swan.ac.uk" + link.get('href'))
        sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
