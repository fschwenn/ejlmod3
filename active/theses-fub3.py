# -*- coding: utf-8 -*-
# Program to harvest "Freie Universitaet Berlin"
# JH 2022-03-03
# FS 2023-04-25

from bs4 import BeautifulSoup
from time import sleep
import os
import ejlmod3
import re
import undetected_chromedriver as uc

jnlfilename = "THESES-FUB-%s" % (ejlmod3.stampoftoday())
publisher = 'Freie U., Berlin'

recs = []
rpp = 40
skipalreadyharvested = True
numofpages = 1
boring = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def get_sub_site(url):
    print("["+url+"] --> Harvesting Data")

    rec = {'jnl': 'BOOK', 'tc': 'T', 'note' : []}

    free_access = False

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    if len(soup.find_all('div', attrs={'class': 'box box-search-list list-group'})) == 2:
        table = soup.find_all('div', attrs={'class': 'box box-search-list list-group'})[0]
        for row in table.find_all('div', attrs={'class': 'list-group-item'}):
            columns = row.find_all('div')

            if len(columns) == 0:
                continue

            first_column = columns[0]
            if first_column.text.find('author') != -1:
                rec['autaff'] = [[columns[1].text]]

            elif first_column.text.find('identifier') != -1:
                # Check if it is a DOI
                if columns[1].text.find('doi') != -1:
                    doi_parted = columns[1].text.split('/')
                    rec['doi'] = doi_parted[-2] + "/" + doi_parted[-1]
                elif first_column.text.find('urn') != -1:
                    rec['urn'] = columns[1].text
                else:
                    rec['url'] = columns[1].text

            elif first_column.text.find('rights') != -1:
                if columns[1].text in ['free', 'open access', 'accept']:
                    free_access = True
                    continue
                elif columns[1].text.find('public-domain') != -1:
                    rec['license'] = {"url": columns[1].text, "statement": "CC0"}
                    free_access = True
                elif columns[1].text == "http://www.fu-berlin.de/sites/refubium/rechtliches/Nutzungsbedingungen":
                    free_access = False
                else:
                    unformated_license = columns[1].text.split('/licenses/')[1]
                    formated_license = unformated_license[0:len(unformated_license)-1].replace('/', '-').upper()
                    rec['license'] = {"url": columns[1].text, "statement": formated_license }
                if re.search('creativecommons.org', columns[1].text):
                     free_access = True


            elif first_column.text.find('abstract') != -1:
                if len(columns) > 2:
                    if  columns[2].text.strip() == 'de':
                        rec['absde'] = columns[1].text
                    else:
                        rec['abs'] = columns[1].text
                else:
                    rec['abs'] = columns[1].text

            elif re.search('format.*extent', first_column.text):
                pages = columns[1].text
                if re.search('\d\d+', pages):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)

            elif first_column.text.find('language') != -1:
                language = columns[1].text
                if language == 'ger':
                    rec['language'] = 'German'

            elif first_column.text.find('subject') != -1 and first_column.text.find('ddc') == -1:
                if "keyw" not in list(rec.keys()):
                    rec['keyw'] = []
                rec['keyw'].append(columns[1].text)

            elif first_column.text.find('title') != -1:
                if first_column.text.find('translated') != -1:
                    rec['transtit'] = columns[1].text
                else:
                    rec['tit'] = columns[1].text

            elif first_column.text.find('type') != -1:
                disstype = columns[1].text
                if disstype.find('Dissertation') == -1:
                    if disstype in boring:
                        return None
                    else:
                        rec['note'].append(disstype)

            elif first_column.text.find('contributor') != -1 and first_column.text.find('gender') == -1:
                if not re.search('contact', first_column.text):
                    if "supervisor" not in list(rec.keys()):
                        rec['supervisor'] = []
                    sv = re.sub('(Prof\.|Dr\.|Priv\.\-Doz\.) *', '', columns[1].text)
                    rec['supervisor'].append([sv])

            elif first_column.text.find('issued') != -1:
                rec['date'] = columns[1].text
        #german fallback
        if not 'abs' in list(rec.keys()) and 'absde' in list(rec.keys()):
            rec['abs'] = rec['absde']

    # Get The pdf link
    links = soup.find_all('a', attrs={'class': 'btn btn-default'})
    for link in links:
        if link.get('title') is not None and link.get('href') is not None:
            if link.text.find('ffnen') != -1:
                if free_access:
                    rec['FFT'] = "https://refubium.fu-berlin.de" + link.get('href')
                else:
                    rec['hidden'] = "https://refubium.fu-berlin.de" + link.get('href')
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('  %s already in backup' % (rec['urn']))
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)


v = 0
for (fc, dep) in [('m', 'Mathematik+und+Informatik'), ('', 'Physik')]:
    for page in range(numofpages):
        tocurl = 'https://refubium.fu-berlin.de/handle/fub188/14/browse?rpp=' + str(rpp) + '&offset=' + str(page*rpp) + '&etal=-1&sort_by=2&type=affiliation&value=' + dep + '&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, numofpages], [tocurl]])
        driver.get(tocurl)
        for link in BeautifulSoup(driver.page_source, 'lxml').find_all('a', attrs={'class': 'box-search-list-title'}):
            get_sub_site('https://refubium.fu-berlin.de' + link.get('href') + "?show=full")
            sleep(3)
            v += 1
        sleep(10)
    sleep(10)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
