# -*- coding: utf-8 -*-
#program to harvest Communications/Papers in Physics
# FS 2017-12-13
# FS 2023-03-22

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl

tmpdir = '/tmp'
skipalreadyharvested = True

def tfstrip(x): return x.strip()
regexpref = re.compile('[\n\r\t]')

typecode = 'P'

jnl = sys.argv[1]
vol = sys.argv[2]

if jnl == 'pip':
    publisher = 'Papers in Physics'
    jnlname = 'Papers Phys.'
    urltrunk = 'http://www.papersinphysics.org/papersinphysics/issue/view/%s' % (vol)
elif jnl == 'cip':
    publisher = 'Publishing House for Science and Technology, Vietnam Academy of Science and Technology'
    jnlname = 'Commun.in Phys.'
    urltrunk = 'http://vjs.ac.vn/index.php/cip/issue/view/%s/showToc' % (vol)
    urltrunk = 'http://vjs.ac.vn/index.php/cip/issue/view/%s' % (vol)
elif jnl == 'eureka':
    publisher = 'Scientific Route OU'
    jnlname = 'Eureka'
    urltrunk = 'http://eu-jr.eu/engineering/issue/view/%s' % (vol)

    


jnlfilename = '%s%s_%s' % (jnl, vol, ejlmod3.stampoftoday())
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

print(urltrunk)
try:
    tocpage = BeautifulSoup(urllib.request.urlopen(urltrunk, context=ctx), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunk))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")

prerecs = []
if jnl in ['pip', 'cip']:
    tables = tocpage.body.find_all('div', attrs = {'class' : ['obj_article_summary', 'article_summary_body']})
elif jnl == 'eureka':
    tables = tocpage.body.find_all('table', attrs = {'class' : 'tocArticle'})

print('%i potential articles found' % (len(tables)))

for table in tables:
    rec = {'jnl' : jnlname, 'tc' : typecode, 'vol' : vol, 'keyw' : [], 'autaff' : [], 'refs' : []}
    #PDF
    for a in table.find_all('a'):
        if re.search('PDF', a.text):
            rec['FFT'] = re.sub('\/view\/', '/download/', a['href'])
    #article link
    for td in table.find_all('td', attrs = {'class' : 'tocTitle'}):
        rec['tit'] = td.text.strip()
        for a in td.find_all('a'):
            rec['artlink'] = a['href']
    if 'tit' not in rec:
        for div in table.find_all('div', attrs = {'class' : 'tocTitle'}):
            rec['tit'] = div.text.strip()
            for a in div.find_all('a'):
                rec['artlink'] = a['href']
    if 'tit' not in rec:
        for div in table.find_all('div', attrs = {'class' : 'title'}):
            rec['tit'] = div.text.strip()
            for a in div.find_all('a'):
                rec['artlink'] = a['href']
    if 'tit' not in rec:
        for h3 in table.find_all('h3', attrs = {'class' : 'title'}):
            for a in h3.find_all('a'):
                rec['artlink'] = a['href']
                rec['tit'] = a.text.strip()
    if 'tit' not in rec:
        for h5 in table.find_all('h5', attrs = {'class' : 'summary_title_wrapper'}):
            for a in h5.find_all('a'):
                rec['artlink'] = a['href']
                rec['tit'] = a.text.strip()
    prerecs.append(rec)


i = 0
recs = []
for rec in prerecs:
    i += 1
    autaff = False
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    artpage =  BeautifulSoup(urllib.request.urlopen(rec['artlink'], context=ctx), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_firstpage', 'citation_keywords', 'citation_doi',
                                        'citation_author', 'citation_author_institution', 'DC.Description', 'citation_reference',
                                        'citation_pdf_url'])
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        continue
    time.sleep(3)
    #volume and issue
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'citation_issue':
                if jnl in ['cip', 'eureka']:
                    rec['issue'] = meta['content']
            elif meta['name'] == 'citation_volume':
                if jnl == 'cip':
                    rec['vol'] = meta['content']
    #year as volume
    if jnl == 'eureka':
        rec['vol'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
    #authors, 2nd possibility
    if not rec['autaff']:
        for div in artpage.body.find_all('div', attrs = {'id' : 'authorBio'}):
            for p in div.find_all('p'):
                for em in p.find_all('em'):
                    rec['autaff'].append([ em.text ])
                    em.replace_with('')
                aff = p.text.strip()
                if aff != 'normally':
                    rec['autaff'][-1].append(re.sub('[\n\t\r]', ' ', aff))
    #keywords aftermath
    if len(rec['keyw']) == 1:
        rec['keyw'] = re.split(', ', rec['keyw'][0])
    #abstract
    divs = artpage.body.find_all('div', attrs = {'id' : 'articleAbstract'})
    if not divs:
        divs = artpage.body.find_all('div', attrs = {'class' : 'abstract'})
    for div in divs:
        for p in div.find_all('p'):
            if 'abs' not in rec:
                rec['abs'] = p.text
                break
        if 'abs' not in rec:
            for div2 in div.find_all('div'):
                rec['abs'] = div2.text
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #references
    if jnl in ['pip']:
        reflink = False
        #reflink = re.sub('(.*)\/(.*)', r'https://www.papersinphysics.org/papersinphysics/article/download/\2/ref\2?inline=1', rec['artlink'])
        for a in artpage.body.find_all('a', attrs = {'class' : 'obj_galley_link file'}):
            if re.search('REFERENCES', a.text):
                reflink = re.sub('view', 'download', a['href'])
        if reflink:
            print(reflink)
            refpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(reflink), features='lxml')
            time.sleep(3)
            for a in refpage.body.find_all('a'):
                if a.has_attr('href') and re.search('doi.org', a['href']):
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    a.replace_with(', DOI: %s' % (rdoi))
            allrefs = re.sub('[\n\t\r]', ' ', refpage.body.text.strip())
            allrefs = re.sub('  +', ' ', allrefs)
            allrefs = re.sub('\. *, DOI:', ', DOI:', allrefs)        
            for ref in re.split('\[\d+\] +', allrefs):
                rec['refs'].append([('x', ref)])
        else:
            print('   no references!')    
    elif jnl in ['eureka']:
        for div in artpage.body.find_all('div', attrs = {'id' : 'articleCitations'}):
            for p in div.find_all('p'):
                rec['refs'].append([('x', p.text.strip())])
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
 
ejlmod3.writenewXML(recs, publisher, jnlfilename)
