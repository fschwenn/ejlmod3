# -*- coding: UTF-8 -*-
#program to harvest Leibniz International Proceedings in Informatics
# FS 2023-09-22

import os
import ejlmod3
import re
import sys
import unicodedata
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'Dagstuhl Publishing'

#semnr = sys.argv[1]
#url = 'https://drops.dagstuhl.de/opus/portals/lipics/index.php?semnr=' + semnr
vol = sys.argv[1]
url = 'https://drops.dagstuhl.de/entities/volume/LIPIcs-volume-' + vol
print(url)


tocpage = BeautifulSoup(urllib.request.urlopen(url), features='lxml')
recs = []

#Hauptaufnahme
harec = {}
conferencename = ''
for div in tocpage.body.find_all('div', attrs = {'class' : 'mt-5'}):
    harec = {'jnl' : 'Leibniz Int.Proc.Inf.', 'tc' : 'K', 'autaff' : [], 'vol' : vol, 'note' : [], 'link' : url}
    for h1 in tocpage.body.find_all('h1'):
        conferencename =  h1.text.strip()
        harec['tit'] = 'Proceedings, ' + conferencename
    if len(sys.argv) > 2:
        harec['cnum'] = sys.argv[2]
    (acronym, location, conferencename) = ('', '', '')
    for section in div.find_all('section'):
        for h4 in section.find_all('h4'):
            h4t = h4.text.strip()
            h4.decompose()
            if h4t == 'Event':
                harec['note'].append(section.text.strip())
            elif h4t == 'Editors':
                for div in section.find_all('div', attrs = {'class' : 'author'}):
                    for span in div.find_all('span', attrs = {'class' : 'name'}):
                        harec['autaff'].append([re.sub('(.*) (.*)', r'\2, \1 (Ed.)', span.text.strip())])
                    for a in div.find_all('a'):
                        if a.has_attr('href') and re.search('orcid.org\/', a['href']):
                            harec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
                    for li in div.find_all('li', attrs = {'class' : 'affiliation'}):
                        harec['autaff'][-1].append(li.text.strip())
            elif h4t == 'Publication Details':
                for li in section.find_all('li'):
                    lit = li.text.strip()
                    if re.search('ISBN.*978', lit):
                        harec['isbn'] = re.sub('\-', '', re.sub('.*?(978[0-9\-X]+).*', r'\1', lit))
                    elif re.search('published.*[12]\d\d\d', lit):
                        harec['date'] = re.sub('.*?([12]\d\d\d.*) *.*', r'\1', lit)                                
    ejlmod3.printrecsummary(harec)
                                                       
                                                       
for div in tocpage.body.find_all('div', attrs = {'class' : 'entity-list-item'}):
    rec = {'jnl' : ' Leibniz Int.Proc.Inf.', 'tc' : 'C', 'autaff' : [], 'note' : [], 'vol' : vol}
    category = ''
    if 'isbn' in harec:
        rec['motherisbn'] = harec['isbn']
    if len(sys.argv) > 2:
        rec['cnum'] = sys.argv[2]
    for div2 in div.find_all('div', attrs = {'class' : 'category'}):
        category = div2.text.strip()
    for h5 in div.find_all('h5', attrs = {'class' : 'card-title'}):
        for a in h5.find_all('a'):
            rec['artlink'] = a['href']
            rec['tit'] = a.text.strip()
            rec['note'].append(conferencename)
            if category == 'Complete Volume' and harec:
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('pdf$', a['href']):
                        harec['pdf_url'] = a['href']
            elif not category in ['Front Matter', 'Backmatter']:                
                rec['note'].append(category)
                recs.append(rec)
                

print('found %i links to articles' % (len(recs)))

for (i, rec) in enumerate(recs):
    time.sleep(3)
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']), features='lxml')
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'DC.Identifier', 'DC.Subject', 'citation_date',
                                        'citation_pdf_url', 'DC.Description', 'DC.Rights'])
    #authors
    for section in artpage.find_all('section', attrs = {'class' : 'authors'}):
        for div in section.find_all('div', attrs = {'class' : 'author'}):
            for span in div.find_all('span', attrs = {'class' : 'name'}):
                rec['autaff'].append([span.text.strip()])
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org\/', a['href']):
                        rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
                for li in div.find_all('li', attrs = {'class' : 'affiliation'}):
                    rec['autaff'][-1].append(li.text.strip())
    #BibTeX
    for pre in artpage.body.find_all('pre'):
        pret = pre.text.strip()
        pret = re.sub('[\t]', '  ', pret)
        for part in re.split('\n', pret):
            #pages
            if re.search('pages = *\{', part):
                if re.search('\-\-', part):
                    rec['p1'] = re.sub('.*\{(.*)\-\-.*', r'\1', part)
                    rec['p2'] = re.sub('.*\-\-(.*)\}.*', r'\1', part)
                else:
                    rec['p1'] = re.sub('.*\{(.*)\}.*', r'\1', part)
            #ISBN
            #elif re.search('ISBN', part):
            #    rec['motherisbn'] = re.sub('[^0-9X]', '', part)
            #year
            elif re.search('year = *\{', part):
                rec['year'] = re.sub('\D', '', part)
        pre.replace_with('PRE_XXX_PRE')
    #pages
    if 'p1' in rec and 'p2' in rec:
        if re.search('\d+:\d+', rec['p1']) and re.search('\d+:\d+', rec['p2']):
            rec['alternatejnl'] = rec['jnl']
            rec['alternatevol'] = rec['vol']
            rec['alternatep1'] = re.sub(':.*', '', rec['p1'])
            rec['pages'] = re.sub('.*:', '', rec['p2'])
    #references
    for section in artpage.find_all('section', attrs = {'class' : 'references'}):
        rec['refs'] = []        
        for li in section.find_all('li'):
            ref = []
            for a in li.find_all('a'):
                if a.has_attr('href'):
                    if re.search('arxiv.org\/', a['href']):
                        rarxiv = 'arXiv:' + re.sub('.*abs\/', '', a['href'])
                        ref.append(('r', rarxiv))
                    elif re.search('.*doi.org\/', a['href']):
                        rdoi = 'doi:' + re.sub('.*doi.org\/', '', a['href'])
                        ref.append(('a', rdoi))
                    elif re.search('scholar.google.com', a['href']):
                        a.decompose()
            ref.append(('x', li.text.strip()))
            rec['refs'].append(ref)
                        
    ejlmod3.printrecsummary(rec)

if 'year' in rec:
    harec['year'] = rec['year']
recs.append(harec)
#if 'vol' in harec:
#    jnlfilename = 'lipics%s.%s' % (harec['vol'], semnr)
#else:
#    jnlfilename = 'lipics_.%s' % (semnr)
jnlfilename = 'lipics%s' % (vol)
if len(sys.argv) > 2:
    jnlfilename += '.' + sys.argv[2]

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
