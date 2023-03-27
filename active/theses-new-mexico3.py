# -*- coding: UTF-8 -*-
# Program to harvest New Mexico University
# JH 2021-12-20
# FS 2023-03-25


from bs4 import BeautifulSoup
from time import sleep
import urllib.request, urllib.error, urllib.parse
from json import loads
import urllib.parse
import getopt
import sys
import os
import ejlmod3


import re
#import classifier
from base64 import b64encode

publisher = 'UNM, Albuquerque'
jnlfilename = 'THESES-NEW-MEXICO-%s' % (ejlmod3.stampoftoday())

numoftheses = 20
skipalreadyharvested = True


recs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


def http_request(url):
    hdr = {'User-Agent' : 'Magic Browser'}
    req = urllib.request.Request(url, headers=hdr)
    soup = BeautifulSoup(urllib.request.urlopen(req).read(), 'lxml')
    return soup

def get_sub_site(url, fc, aff):
    rec = {'link' : str(url), 'tc' : 'T', 'jnl' : 'BOOK', 'note': []}
    rec['doi'] = '20.2000/NewMexico/' + re.sub('\W', '', url[25:])

    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print("["+url+"] --> already in backup")
        return
    else:
        print("["+url+"] --> harvesting data")
        sleep(3)


    if fc:
        rec['fc'] = fc

    soup = http_request(url)

    # Extract the title and pdf link
    title_section = soup.find_all('div', attrs={'id': 'title'})
    if len(title_section) == 1:
        title = title_section[0].find_all('a')

        if len(title) == 1:
            rec['hidden'] = title[0].get('href')
            rec['tit'] = str(title[0].text)

    # Extract author
    author_section = soup.find_all('p', attrs={'class': 'author'})
    if len(author_section) == 1:
        author_link = author_section[0].a
        author_query = urllib.parse.parse_qsl(urllib.parse.urlsplit(author_link.get('href')).query)
        if len(author_query) == 3:
            first_name_raw, name_raw = author_query[0][1].split("\" ")
            first_name = first_name_raw.split(':"')[1]
            last_name = name_raw.split(':"')[1]

            first_name = first_name[0:len(first_name)]
            last_name = last_name[0:len(last_name)-1]
            rec['autaff'] = [[ last_name + ", " + first_name, aff ]]

    # Extract Publication date
    for date_section in soup.find_all('div', attrs={'id': 'publication_date'}):
        for p in date_section.find_all('p'):
            if re.search(' ', p.text):
                rec['date'] = re.sub('^\D*', '', p.text)
            else:
                rec['date'] = p.text


    # Extract the committee members and abstract
    committee_members = []
    div_elements = soup.find_all('div', attrs={'class', 'element'})
    for element in div_elements:
        if element.get('id') is None:
            continue
        if element.get('id') == 'abstract':
            abstract_paragraphs = element.find_all('p')
            abstract = ""
            for paragraph in abstract_paragraphs:
                abstract += paragraph.text
            rec['abs'] = str(abstract)

        if element.get('id').find('advisor') != -1:
            for p in element.find_all('p'):
                committee_members.append([p.text])

    rec['supervisor'] = committee_members
    # Extract Keywords
    keywords_section = soup.find_all('div', attrs={'id': 'keywords'})

    if len(keywords_section) == 1:
        keywords_subsection = keywords_section[0].find_all('p')

        if len(keywords_subsection) == 1:
            keywords = keywords_subsection[0].text.replace('\n', '').split(', ')
            rec['keyw'] = keywords

    recs.append(rec)
    ejlmod3.printrecsummary(rec)

for (fc, dep, aff) in [('', 'phyc', 'New Mexico U.'), ('m', 'math', 'UNM, Albuquerque')]:
    index_url = "https://digitalrepository.unm.edu/%s_etds/" % (dep)
    print("--- OPENING article list ---", dep)
    v = 0
    for article in http_request(index_url).find_all('p', attrs={'class': 'article-listing'}):
        article_link = article.a
        get_sub_site(article_link.get('href'), fc, aff)
        if v >= numoftheses:
            break
        v += 1


ejlmod3.writenewXML(recs, publisher, jnlfilename)
