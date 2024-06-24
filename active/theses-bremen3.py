# -*- coding: utf-8 -*-
#harvest theses from Bremen
#FS: 2023-11-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Jacobs U., Bremen'
jnlfilename = 'THESES-BREMEN-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
rpp = 10
pages = 1

hdr = {'User-Agent' : 'Magic Browser'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (fc, dep) in [('m', '16241'), ('c', '16242'), ('', '16240')]:
    for page in range(pages):
        tocurl = 'https://opus.jacobs-university.de/solrsearch/index/search/searchtype/collection/id/' + dep + '/start/' + str(rpp*page) + '/rows/' + str(rpp) + '/sortfield/year/sortorder/desc/doctypefq/doctoralthesis'
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        for div in tocpage.body.find_all('dl', attrs = {'class' : 'result_box'}):
            for div2 in div.find_all('dt', attrs = {'class' : 'results_title'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : [], 'supervisorprelim' : []}
                if fc:
                    rec['fc'] = fc
                for a in div2.find_all('a'):
                    rec['artlink'] = 'https://opus.jacobs-university.de' + a['href']
                    prerecs.append(rec)
        print('  %i records so far' % (len(prerecs)))
        time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    rec['link'] = re.sub('.*docId', 'https://opus.jacobs-university.de/frontdoor/index/index/docId', rec['artlink'])
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'citation_date',
                                        'citation_keywords', 'description', 'DC.Identifier',
                                        'citation_pdf_url', 'DC.rights', 'keywords'])
    #abstract since language information is not correct
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'dcterms.abstract'}):
        if meta.has_attr('lang' ):
            if meta['lang'] == 'de':
                rec['abs_de'] = meta['content']
            else:
                rec['abs'] = meta['content']
        else:
            if re.search(' the ', meta['content']):
                rec['abs'] = meta['content']
            else:
                rec['abs_de'] = meta['content']
    if not 'abs' in rec.keys() and 'abs_de' in rec.keys():
        rec['abs'] = rec['abs_de']

    rec['autaff'][-1].append(publisher)

    for table in artpage.find_all('table', attrs = {'class' : 'result-data'}):
        profdict = {}
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #author
                if tht == 'Author:':
                    for a in td.find_all('a', attrs = {'class' : 'orcid-link'}):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    for a in td.find_all('a', attrs = {'class' : 'gnd-link'}):
                        gndlink = a['href']
                #URN
                elif tht == 'URN:':
                    rec['urn'] = td.text.strip()
                #DOI
                elif tht == 'DOI:':
                    rec['doi'] = re.sub('.*doi.org\/', '', td.text.strip())
                #reviewers
                elif tht in ['Referee:']:
                    prof = ''
                    for a in td.find_all('a'):
                        if re.search('solrsearch', a['href']):
                            prof = a.text.strip()
                        elif re.search('orcid.org', a['href']):
                            profdict[prof] = re.sub('.*orcid.org\/', 'ORCID:', a['href'])
                #supervisor
                elif tht in ['Advisor:']:
                    for a in td.find_all('a'):
                        if re.search('solrsearch', a['href']):
                            rec['supervisorprelim'].append([a.text.strip()])
                        elif re.search('orcid.org', a['href']):
                            rec['supervisorprelim'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                        elif re.search('nv.info.gnd', a['href']):
                            gnd = a['href']
                    if not rec['supervisorprelim']:
                        for sv in re.split(', ', td.text.strip()):
                            rec['supervisorprelim'].append([sv])
                #language
                elif tht == 'Language:':
                    if td.text.strip() == 'German':
                        rec['language'] = 'German'
                #pages
                elif tht == 'Number of pages:':
                    if re.search('\d\d', td.text):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', td.text.strip())
    #fulltext
    for div in artpage.find_all('div', attrs = {'class' : 'accessible-file'}):
        for a in div.find_all('a', attrs = {'type' : 'application/pdf'}):
            rec['pdf_url'] = 'https://opus.jacobs-university.de' + a['href']
    #check profdict
    for sv in rec['supervisorprelim']:
        if len(sv) == 1 and sv[0] in list(profdict.keys()):
            rec['supervisor'].append([sv[0], profdict[sv[0]]])
            rec['note'].append('%s -> %s' % (sv[0], profdict[sv[0]]))
        else:
            rec['supervisor'].append(sv)
    if not 'doi' in rec.keys():
        rec['doi'] = '20.2000/Jacobs_U_Bremen/' + re.sub('.*\/', '', rec['artlink'])
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        pass
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        pass
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
