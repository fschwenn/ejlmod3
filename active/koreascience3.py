# -*- coding: UTF-8 -*-
#program to harvest Korea Science
# FS 2019-04-03
# FS 2023-04-25

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl

journals = {'jkas' : {'issn'      : '1225-4614',
                      'publisher' : 'The Korean Astronomical Society',
                      'jnl'       : 'J.Korean Astron.Soc.',
                      'kojic'     : 'CMHHBA'},
            'jass' : {'issn'      : '2093-5587',
                      'publisher' : 'The Korean Space Science Society',
                      'jnl'       : 'J.Astron.Space Sci.',
                      'kojic'     : 'OJOOBS',
                      'licence'   : {'statement' : 'CC-BY-NC-3.0'}},
            'jkms' : {'issn'      : '0304-9914',
                      'publisher' : 'The Korean Mathematical Society',
                      'jnl'       : 'J.Korean Math.Soc.',
                      'kojic'     : 'DBSHBB'}}
        
journal = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]
if journal not in journals:
    print('do not know journal "%s"' % (journal))
    sys.exit(0)
publisher = journals[journal]['publisher']

jnlfilename = '%s%s.%s' % (journal, vol, iss)
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

starturl = 'http://koreascience.or.kr/journal/%s/v%sn%s.page' % (journals[journal]['kojic'], vol, iss)
print(starturl)
req = urllib.request.Request(starturl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'clear'}):
    rec = {'jnl' : journals[journal]['jnl'], 'vol' : vol, 'issue' : iss, 
           'tc' : 'P', 'autaff' : [], 'keyw' : [], 'refs' : []}
    if len(sys.argv) > 4:
        rec['tc'] = 'C'
        rec['cnum'] = sys.argv[4]
    for a in div.find_all('a'):
        #if a.has_attr('href') and re.search('society', a['href']):
        if a.has_attr('href'):
            if re.search('doi.org', a['href']):
                #rec['artlink'] = re.sub('.*=', 'http://koreascience.or.kr/article/', a['href']) + '.page'
                rec['artlink'] = a['href']
            elif re.search('pdf$', a['href']):
                if 'licence' in list(journals[journal].keys()): 
                    rec['FFT'] = a['href']
    recs.append(rec)


i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    time.sleep(10)
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    page = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    ejlmod3.metatagcheck(rec, page, ['citation_firstpage', 'citation_lastpage', 'citation_doi',
                                     'citation_date', 'citation_title', 'citation_pdf_url',
                                     'citation_publication_date'])
    #license
    if 'licence'  in list(journals[journal].keys()):
        rec['licence'] = journals[journal]['licence']
    #kewyords
    for meta in page.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for keyw in re.split(';', meta['content']):
            rec['keyw'].append(re.sub('<TEX>', '', keyw))
    #affiliations
    affdict = {}
    maildict = {}
    for div in page.body.find_all('div', attrs = {'class' : 'author-aff'}):
        for div2 in div.find_all('div', attrs = {'class' : 'affiliation'}):
            for sup in div2.find_all('sup'):
                affkey = sup.text.strip()
                sup.decompose()
                affdict[affkey] = re.sub('  +', ' ', re.sub('[\n\t\r]', '', div2.text.strip()))
        for div2 in div.find_all('div', attrs = {'class' : 'corresponding-author'}):
            for sup in div2.find_all('sup'):
                mailkey = sup.text.strip()
                for a in div2.find_all('a'):
                    if a.has_attr('href') and a['href'][:6] == 'mailto':
                        maildict[mailkey] = 'EMAIL:' + a['href'][6:]
    #print(affdict)
    #print(maildict)
    #authors
    authors = []
    author = False
    for div in page.body.find_all('div', attrs = {'class' : 'contrib-group'}):
        for sup in div.find_all('sup'):
            affkey = sup.text.strip()
            if affkey == ',':
                sup.decompose()
            else:
                sup.replace_with(',AFFILIATION%s,' % (affkey))
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('orcid.org', a['href']):
                orcid = re.sub('.*org\/(.*)', r',ORCID:\1,', a['href'])
                a.replace_with(orcid)
        divt = re.sub(' and ', ',', re.sub('[\n\t\r]', '', div.text.strip()))
        author = {'name' : False, 'orcid' : False, 'affs' : [], 'mail' : False}
        for part in re.split(' *, *', divt):
            if part:
                #print(' - ', part[:5], part)
                if part[:5] == 'ORCID':
                    author['orcid'] = part
                elif part[:5] == 'AFFIL':
                    if part[11:] in affdict:
                        author['affs'].append(affdict[part[11:]])
                    elif part[11:] in maildict:
                        author['mail'] = maildict[part[11:]]
                    else:
                        print('???', part)
                else:
                    if author['name']:
                        authors.append(author)
                        author = {'name' : part, 'orcid' : False, 'affs' : [], 'mail' : False}
                    else:
                        author['name'] = part
    if author:
        authors.append(author)
        for author in authors:
            rec['autaff'].append([author['name']])
            if author['orcid']:
                rec['autaff'][-1].append(author['orcid'])
            elif author['mail']:
                rec['autaff'][-1].append(author['mail'])
                if author['affs']:
                    rec['autaff'][-1] += author['affs']
    else:
        for meta in page.head.find_all('meta', attrs = {'name' : 'citation_author'}):
            for author in re.split(' *; *',  meta['content']):
                if re.search(',', author):
                    rec['autaff'].append([author])
                else:
                    rec['autaff'].append([re.sub('(.*) (.*)', r'\1, \2', author)])

                
    for div in page.body.find_all('div', attrs = {'class' : 'article-box'}):
        for h4 in div.find_all('h4'):
            #abstract
            if re.search('Abstract', h4.text):
                for p in div.find_all('p'):
                    rec['abs'] = re.sub('[\r\n\t]', '', p.text)
            #references
            elif re.search('References', h4.text):
                for li in div.find_all('li'):
                    adoi = False
                    for a in li.find_all('a'):
                        if a.has_attr('href') and re.search('doi.org', a['href']):
                            adoi = re.sub('.*doi.org.', ', DOI: ', a['href'])
                            a.replace_with('')
                    lit = li.text                    
                    if not re.search('doi.org', lit) and adoi:
                        lit += adoi
#                    lit = re.sub('\.? *https?:\/\/doi.org\/', ', DOI: ', lit)
                    rec['refs'].append([('x', re.sub('  +', '', re.sub('[\r\n\t]', ' ', lit)))])


    if not 'abs' in rec:
        for div in page.body.find_all('div', attrs = {'class' : 'abstract'}):
            rec['abs'] = div.text.strip()
    if not rec['refs']:
        for div in page.body.find_all('div', attrs = {'class' : 'ref-list'}):
            for li in div.find_all('div'):
                if not len(li.find_all('div', attrs = {'class' : 'ref-content cell'})) == 1:
                    continue    
                adoi = False
                for a in li.find_all('a'):
                    if a.has_attr('href') and re.search('doi.org', a['href']):
                        adoi = re.sub('.*doi.org.', '', a['href'])
                        a.replace_with('')
                lit = re.sub('[\n\t\r]', '', li.text)
                if not re.search('doi.org', lit) and adoi:
                    lit += ', DOI: ' + adoi
                if adoi:
                    rec['refs'].append([('a', 'doi:' + adoi), ('x', lit)])
                else:
                    rec['refs'].append([('x', lit)])
                    
                    
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
