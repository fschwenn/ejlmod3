#program to harvest "Revista Mexicana de Fisica"
# -*- coding: UTF-8 -*-
## JH 2022-03-12
#FS 2022-12-12

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from time import sleep
import undetected_chromedriver as uc



if sys.argv[1] in ['E', 'S']:
        letter = sys.argv[1]
        volume = sys.argv[2]
        issue = sys.argv[3]
else:
        letter = ''
        volume = sys.argv[1]
        issue = sys.argv[2]
        

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)

publisher = 'Sociedad Mexicana de Fisica'
jnlfilename = 'rmf%s%s.%s' % (letter, volume, issue)
if len(sys.argv) > 4:
        jnlfilename += '_'+sys.argv[4]

if letter == '':
        jnl = 'Rev.Mex.Fis.'
        tocurl = "https://rmf.smf.mx/ojs/index.php/rmf/issue/archive"
elif letter == 'E':
        jnl = 'Rev.Mex.Fis.E'
        tocurl = "https://rmf.smf.mx/ojs/index.php/rmf-e/issue/archive"
elif letter == 'S':
        jnl = 'Rev.Mex.Fis.Suppl.'
        tocurl = "https://rmf.smf.mx/ojs/index.php/rmf-s/issue/archive"

recs = []

redoi = re.compile('.*doi.org\/(10.\d+\/.*?)(, .*|\.$|$)')
def get_article(url, section):
        rec = {'jnl': jnl, 'tc': 'P', 'note' : [section], 'refs' : [],
               'vol' : volume, 'issue' : issue, 'keyw' : []}
        if len(sys.argv) > 4:
                rec['cnum'] = sys.argv[4]
                rec['tc'] = 'C'

        soup = BeautifulSoup(urllib.request.urlopen(url), 'lxml')

        print("ARTICLE: ["+url+"] --> Harvesting data")
        ejlmod3.metatagcheck(rec, soup, ['citation_date', 'citation_title', 'DC.Identifier.DOI',
                                         'DC.Rights', 'DC.Description', 'citation_keywords',
                                         'citation_pdf_url', 'citation_reference',
                                         'DC.Language'])
        for meta in soup.find_all('meta'):
                if meta.has_attr('name'):
                        #pages
                        if meta['name'] == 'citation_firstpage':
                                p1 = meta['content']
                                rec['p1'] = re.sub(' .*', '', p1)
                        elif meta['name'] == 'citation_lastpage':
                                if re.search(' ', p1):                                        
                                        rec['pages'] = re.sub('.*\D', '', meta['content'])
                                else:
                                        rec['p2'] = meta['content']

        # Get the authors
        authors_section = soup.find_all('ul', attrs={'class': 'authors'})
        if len(authors_section) == 1:
                rec['autaff'] = []
                for author in authors_section[0].find_all('li'):
                        for name in author.find_all('span', attrs={'class': 'name'}):
                                rec['autaff'].append([name.text.replace('\t','').replace('\n', '')])
                        for orcid in author.find_all('span', attrs={'class': 'orcid'}):
                                rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', orcid.text.replace('\t','').replace('\n', '')))
                        for aff in author.find_all('span', attrs={'class': 'affiliation'}):
                                rec['autaff'][-1].append(aff.text.replace('\t', '').replace('\n', ''))


        # Get the references
        references_section = soup.find_all('section', attrs={'class': 'item references'})
        if len(references_section) == 1:
                references_sub_section = references_section[0].find_all('div', attrs={'class': 'value'})
                if len(references_sub_section) == 1:
                        references = references_sub_section[0].find_all('p')
                        refs = []
                        for reference in references:
                                # Get the reference's DOI
                                ref_doi = reference.find_all('a')
                                if len(ref_doi) == 1:
                                        ref_doi = ref_doi[0].text.split('/')
                                        refs.append(ref_doi[-2] + "/" + ref_doi[-1])
                                        
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

def get_issue(url):
        soup = BeautifulSoup(urllib.request.urlopen(url), 'lxml')
        print("ISSUE: ["+url+"] --> Harversting data")
        # Get volume and issue number
        heading = soup.find_all('h1')
        if len(heading) == 1:
                vol_num = heading[0].text.split('):')[0].split(' (')[0]
                vol_num = vol_num.split(' ')
                vol = int(vol_num[1])
                issue = int(vol_num[3])
        for div in soup.find_all('div', attrs={'class': 'section'}):
                for h2 in div.find_all('h2'):
                        section = h2.text.strip()
                articles = div.find_all('div', attrs={'class': 'obj_article_summary'})
                for article in articles:
                        link = article.a
                        if link.get('href') is None:
                                continue
                        href = link.get('href')
                        get_article(href, section)
                        sleep(10)




jtocpage = BeautifulSoup(urllib.request.urlopen(tocurl).read(), 'lxml')
#find issue link
for h2 in jtocpage.body.find_all('h2'):
        if re.search('.*Vol.? %s,? No.? %s .*' % (volume, issue), h2.text):
                for a in h2.find_all('a'):
                        tocurl = a['href']
                        print(tocurl)
get_issue(tocurl)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
