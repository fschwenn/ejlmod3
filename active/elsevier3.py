# -*- coding: utf-8 -*-
#program to webcrawl Elsevier-journals
# FS 2022-08-14

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import json
from inspirelabslib3 import *

regexpref = re.compile('[\n\r\t]')

publisher = 'Elsevier'
tc = 'P'
jnl = sys.argv[1]
vol = sys.argv[2]
jnlfilename = 'elseviercrawl_'+jnl+vol
if len(sys.argv) > 3: 
    iss = sys.argv[3]
    jnlfilename = jnl + vol + '.' + iss
if   (jnl == 'npb'): 
    jnlname = 'Nucl.Phys.B'
    urljnlname = 'nuclear-physics-b'
elif (jnl == 'plb'):
    jnlname = 'Phys.Lett.B'
    urljnlname = 'physics-letters-b'

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)


tocurl = 'https://www.sciencedirect.com/journal/%s/vol/%s' % (urljnlname, vol)
print(tocurl)

driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")


sectit = False
prerecs = []
for ol in tocpage.body.find_all('ol', attrs = {'class' : 'article-list-items'}):
    #for child in ol.children:
    for child in ol.contents:
        try:
            cn = child.name
        except:
            pass
        if cn == 'li':
            for h2 in child.find_all('h2', attrs = {'class' : 'section-title'}):
                sectit = h2.text
            for a in child.find_all('a', attrs = {'class' : 'article-content-title'}):
                rec = {'tc' : tc, 'jnl' : jnlname, 'vol' : vol, 'note' : [], 'autaff' : []}
                if sectit:
                    rec['note'].append(sectit)
                    if sectit in ['Quantum Field Theory and Statistical Systems', 'High Energy Physics ‒ Theory', 'Theory']:
                        rec['fc'] = 't'
                    elif sectit in ['High Energy Physics ‒ Phenomenology', 'Phenomenology']:
                        rec['fc'] = 'p'
                    elif sectit in ['High Energy Physics ‒ Experiment']:
                        rec['fc'] = 'e'
                    elif sectit in ['Astrophysics and Cosmology']:
                        rec['fc'] = 'a'

                rec['artlink'] = 'https://www.sciencedirect.com' + a['href']
                prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink'], rec['note']], [len(recs)]])
    time.sleep(5)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_doi',
                                        'citation_online_date', 'citation_title'])
    #year
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_publication_date'}):
        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', meta['content'])
    #JSON
    for script in artpage.find_all('script', attrs = {'type' : 'application/json'}):
        scriptt = regexpref.sub('', script.contents[0].strip())
        scripttjson = json.loads(scriptt)
        #authors and affiliations
        if 'authors' in scripttjson and 'content' in scripttjson['authors'] and scripttjson['authors']['content']:
            affdict = {}
            #print(scripttjson['authors'])
            #affiliations
            for affkey in scripttjson['authors']['affiliations']:
                #print (scripttjson['authors']['affiliations'][affkey]['$$'])
                for aff in scripttjson['authors']['affiliations'][affkey]['$$']:
                    if aff['#name'] == 'textfn':
                        if '_' in aff:
                            affstring = aff['_']
                        else:
                            print(aff)
                            print(scripttjson['authors']['affiliations'])
                affdict[affkey] = affstring
            #authors
            for authorc in scripttjson['authors']['content']:
                for author in authorc['$$']:
                    affsfound = False
                    #print(author)
                    if author['#name'] == 'author':
                        for entry in author['$$']:
                            if entry['#name'] == 'surname':
                                authorname = entry['_']
                        for entry in author['$$']:
                            if entry['#name'] == 'given-name':
                                authorname += ',  ' + entry['_']
                        rec['autaff'].append([authorname])
                        if 'orcid' in author['$']: 
                            rec['autaff'][-1].append('ORCID:' + author['$']['orcid'])
                        for entry in author['$$']:
                            if entry['#name'] == 'cross-ref':
                                affkey = entry['$']['refid']
                                if affkey in affdict:
                                    rec['autaff'][-1].append(affdict[affkey])
                                    affsfound = True
                                elif not affkey in ['cr0010']:
                                    print(affkey, '???')
                        if len(affdict) == 1 and not affsfound:
                            rec['autaff'][-1].append(affstring)
#                            rec['note'].append('only affiliation?!')

        #license
        if 'article' in scripttjson:
            if 'access' in scripttjson['article']:
                rec['license'] = {'url' : scripttjson['article']['access']['license']}
                if 'pdfDownload' in scripttjson['article']:
                    urlmd = scripttjson['article']['pdfDownload']['urlMetadata']
                    #rec['FFT'] = 'https://www.sciencedirect.com/science/article/pii/%s/pdfft?md5=%s&pid=%s' % (urlmd['pii'], urlmd['queryParams']['md5'], urlmd['queryParams']['pid'])
    #abstract
    abstract = artpage.body.find_all('div', attrs = {'class' : ['abstract', 'author']})
    for a in abstract:
        for div in a:
            rec['abs'] = div.text
    #INSPIRE check
    if perform_inspire_search_FS('doi:%s' % (rec['doi'])):
        print('    doi:%s already in INSPIRE' % (rec['doi']))
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        #ejlmod3.printrec(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
driver.quit()
