# -*- coding: UTF-8 -*-
##!/usr/bin/python
#program to harvest Proc.Nat.Acad.Sci.
# FS 2019-07-17
# Cloudflare -> need for newer OpenSSL -> run on HAL

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import cloudscraper



publisher = 'National Academy of Sciences of the USA'
vol = sys.argv[1]
issues = sys.argv[2]
jnlfilename = 'procnas%s.%s' % (vol, re.sub(',', '_', issues))
jnlname = 'Proc.Nat.Acad.Sci.'

scraper = cloudscraper.create_scraper()
prerecs = []
artlinks = []
for issue in re.split(',', issues):
    (note1, note2) = (False, False)
    tocurl = 'https://www.pnas.org/content/%s/%s' % (vol, issue)
    ejlmod3.printprogress('=', [[issue, issues], [tocurl]])
    tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")

    for contdiv in tocpage.body.find_all('div', attrs = {'class' : 'toc__body'}):
        for section in contdiv.children:
            try:
                childname = section.name
            except:
                continue
            if childname == 'section':
                note1 = ''
                note2 = ''
                for child in section.children:
                    try:
                        childname = child.name
                    except:
                        continue
                    if childname == 'h3':
                        note1 = child.text.strip()
                        ejlmod3.printprogress('  ', [[note1]])
                    elif childname == 'div':
                        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                               'note' : [], 'autaff' : [], 'tc' : 'P'}
                        rec['note1'] = note1
                        rec['note2'] = note2
                        rec['soup'] = child
                        prerecs.append(rec)
                    elif childname == 'section':
                        note2 = ''
                        for child2 in child.children:
                            try:
                                child2name = child2.name
                            except:
                                continue
                            if child2name == 'h4':
                                note2 = child2.text.strip()
                                ejlmod3.printprogress('   ', [[note2]])
                            elif child2name == 'div':
                                rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                                       'note' : [], 'autaff' : [], 'tc' : 'P'}
                                rec['note1'] = note1
                                rec['note2'] = note2
                                rec['soup'] = child2
                                prerecs.append(rec)
                            elif child2name == 'section':
                                for div in child2.find_all('div', attrs = {'class' : 'card'}):
                                    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                                           'note' : [], 'autaff' : [], 'tc' : 'P'}
                                    rec['note1'] = note1
                                    rec['note2'] = note2
                                    rec['soup'] = div
                                    prerecs.append(rec)
    time.sleep(7)
                        

recs = []
for rec in prerecs:
    if not rec['note1'] in ['Commentaries', 'This Week in PNAS', 'News Feature', 'Retrospective',
                            'Biological Sciences', 'Social Sciences']:
        if not rec['note2'] in ['Biophysics and Computational Biology',
                                'Chemistry']:
            rec['note'].append(rec['note2'])
            #date
            for span in rec['soup'].find_all('span', attrs = {'class' : 'card__meta__date'}):
                rec['date'] = span.text.strip()
            #link
            for h3 in rec['soup'].find_all('h3', attrs = {'class' : 'article-title'}):
                for a in h3.find_all('a'):
                    rec['tit'] = a.text
                    rec['artlink'] = 'https://www.pnas.org' + a['href']
                recs.append(rec)

print('kept %i of %i' % (len(recs), len(prerecs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ["citation_firstpage", "citation_pdf_url", "citation_doi",
                                        "citation_online_date", "citation_title"])
    #metadata in script
    for script in artpage.head.find_all('script'):
        if script.contents:
            scriptt = re.sub('.*?= *(\{.*?);.*', r'\1', re.sub('[\n\t]', '', script.contents[0].strip()))
            if re.search('^\{', scriptt):
                metadata = json.loads(scriptt)
                if 'page' in metadata:
                    print("   metadata in JSON found")
                    if 'pageInfo' in metadata['page']:
                        #date
                        if 'pubDate' in metadata['page']['pageInfo']:
                            rec['date'] = metadata['page']['pageInfo']['pubDate']
                        #DOI
                        if 'DOI' in metadata['page']['pageInfo']:
                            rec['doi'] = metadata['page']['pageInfo']['DOI']
                    if 'attributes' in metadata['page']:
                        #keywords
                        if 'keywords' in metadata['page']['attributes']:                
                            rec['keyw'] = metadata['page']['attributes']['keywords']
                        #license
                        if 'openAccess' in metadata['page']['attributes']:
                            if metadata['page']['attributes']['openAccess'] == 'yes':
                                rec['license'] = {'statement' : metadata['page']['attributes']['licenseType']}
    #p1
    for span in artpage.body.find_all('span', attrs = {'property' : 'identifier'}):
        rec['p1'] = span.text.strip()
    #abstract
    for section in artpage.body.find_all('section', attrs = {'id' : 'abstract'}):
        for div in section.find_all('div', attrs = {'role' : 'paragraph'}):
            rec['abs'] = div.text.strip()                
    #references
    for section in artpage.body.find_all('section', attrs = {'id' : 'bibliography'}):
        rec['refs'] = []
        for div in section.find_all('div', attrs = {'role' : 'doc-biblioentry listitem'}):
            for a in div.find_all('a'):
                at = a.text.strip()
                if at == 'Crossref':                    
                    a.replace_with(re.sub('.*org\/', ', DOI: ', a['href']))
                    a.decompose()
                elif at in ['Google Scholar', 'PubMed']:
                    a.decompose()                                                       
            ref = div.text.strip()            
            rec['refs'].append([('x', ref)])
    #authors
    for div in artpage.body.find_all('div', attrs = {'property' : 'author'}):
        #print(div)
        for name in div.find_all('span', attrs = {'property' : 'familyName'}):
            author = name.text
        for name in div.find_all('span', attrs = {'property' : 'givenName'}):
            author += ', ' + name.text
        rec['autaff'].append([author])
        for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
            rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
        for div2 in div.find_all('div', attrs = {'property' : 'affiliation'}):
            for span in div2.find_all('span'):
                rec['autaff'][-1].append(span.text.strip())
    #license
    for section in artpage.body.find_all('section', attrs = {'class' : 'core-copyright'}):
        for a in section.find_all('a'):
            if a.has_attr('href') and re.search('creativecom', a['href']):
                rec['license'] = {'url' : a['href']}
    ejlmod3.printrecsummary(rec)
    time.sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
