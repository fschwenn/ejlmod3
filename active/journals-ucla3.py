# -*- coding: utf-8 -*-
#harvest journals from University of California
#FS: 2023-08-22

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import json

jnl = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]

publisher = 'UCLA'

tocurl = 'https://escholarship.org/uc/%s/%s/%s' % (jnl, vol, iss)

if jnl == 'combinatorial_theory':
    jnlname = 'Combin.Theor.'

jnlfilename = 'ucla_%s%s.%s_%s'  % (jnl, vol, iss, ejlmod3.stampoftoday())
problematiclinks = []

recs = []
ejlmod3.printprogress('=', [[tocurl]])
tocfilename = '/tmp/%s.toc' % (jnlfilename)
if not os.path.isfile(tocfilename):
    os.system('wget -T 300 -t 3 -q -O %s "%s"' % (tocfilename, tocurl))
    time.sleep(10)
inf = open(tocfilename, 'r')
lines = ''.join(inf.readlines())
tocpage = BeautifulSoup(lines, features="lxml")
inf.close()
#req = urllib2.Request(tocurl, headers=hdr)
#tocpage = BeautifulSoup(urllib2.urlopen(req))

divs = tocpage.body.find_all('div', attrs = {'class' : 'c-pub'})
count = [0, 0, 0]
for div in divs:
    for h2 in div.find_all('h4'):
        for a in h2.find_all('a'):
            rec = {'tc' : 'P', 'keyw' : [], 'jnl' : jnlname, 'note' : [],
                   'autaff' : [], 'vol' : vol, 'issue' : iss}
            rec['artlink'] = 'https://escholarship.org' + a['href']
            rec['tit'] = a.text.strip()
            if rec['artlink'] in problematiclinks:
                print(' link "%s" is problematic' % (rec['artlink']))
            recs.append(rec)
#else:
#    divs2 = re.split('<div class="c-pub">', lines)[1:]
#    print('BeautifulSoup failed to get all links (now %i instead of %i)' % (len(divs2), len(divs)))
#    i = 0
#    for div in divs2:
#        parts = re.split('<\/', div)
#        i += 1
#        #print(' - ', i, len(parts), len(div))
#        for part in parts:
#            if re.search('<h2', part):
#                rec = {'tc' : 'P', 'keyw' : [], 'jnl' : jnlname, 'note' : [], 'vol' : vol, 'issue' : iss}
#                rec['artlink'] = 'https://escholarship.org' + re.sub('.*href="(.*?)".*', r'\1', part)
#                rec['tit'] = re.sub('.*<div class="c-clientmarkup">', '', part)
#                #print(rec['artlink'])
#                break
#        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    artfilename = '/tmp/ucla_%s.html' % (re.sub('\W', '', rec['artlink']))
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    if not os.path.isfile(artfilename):
        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (artfilename, rec['artlink']))
        time.sleep(10)
    if int(os.path.getsize(artfilename)) == 0:
        time.sleep(30)
        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (artfilename, rec['artlink']))
        time.sleep(10)
    inf = open(artfilename, 'r')
    artpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
    inf.close()
    #withdrawn?
    withdrawn = False
    for div in artpage.find_all('div', attrs = {'class' : 'c-clientmarkup'}):
        if re.search('This item has been withdrawn', div.text): 
            withdrawn = True
            recs.remove(rec)
    if withdrawn: continue                      
    #req = urllib2.Request(rec['artlink'], headers=hdr)
    #artpage = BeautifulSoup(urllib2.urlopen(req))
    ejlmod3.metatagcheck(rec, artpage, ['citation_abstract', 'citation_online_date', 'citation_pdf_url'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name'):
            #author
            #if meta['name'] == 'citation_author':
            #    rec['autaff'] = [[ meta['content'], publisher ]]
            #year 
            if meta['name'] == 'citation_publication_date':
                rec['year'] = meta['content']
    #for late online
    if 'date' in rec and 'year' in rec:
        onlineyear = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        if onlineyear > rec['year']:
            print('   change rec_date from "%s" to "%s"' % (rec['date'], rec['year']))
            rec['date'] = rec['year']
    #JSON
    for script in artpage.body.find_all('script'):
        if script.contents:
            #scriptt = re.sub('[\n\t]', '', script.text.strip())
            scriptt = re.sub('[\n\t]', '', script.contents[0].strip())
            scriptt = re.sub('.*window.jscholApp_initialPageData *= *(\{.*\}).*', r'\1', scriptt)
            if not re.search('abstract.*authors', scriptt):
                scriptt = False
        else:
            scriptt = False
        if scriptt:
            scripttjson = json.loads(scriptt)
#            for k in scripttjson:
#                print('|>', k, scripttjson[k])
#                print('---\n')

            if 'attrs' in list(scripttjson.keys()):
                #keywords
                if 'keywords' in list(scripttjson['attrs'].keys()):
                    rec['keyw'] = scripttjson['attrs']['keywords']
                #subject
                if 'subjects' in list(scripttjson['attrs'].keys()):
                    rec['subjects'] = scripttjson['attrs']['subjects']
                    rec['note'] += scripttjson['attrs']['subjects']
            #author
            if 'authors' in list(scripttjson.keys()):
                for author in scripttjson['authors']:
                    if 'ORCID_id' in author:
                        rec['autaff'].append([ author['name'], 'ORCID:%s' % (author['ORCID_id'])])
                    if 'email' in author:
                        rec['autaff'].append([ author['name'], 'EMAIL:%s' % (author['email'])])
                    if 'institution' in author:
                        rec['autaff'][-1].append(author['institution'])
                            
            #license
            if 'rights' in list(scripttjson.keys()):
                if scripttjson['rights'] and re.search('creativecommons.org', scripttjson['rights']):
                    rec['license'] = {'url' : scripttjson['rights']}
            if 'citation' in list(scripttjson.keys()):
                #DOI
                if 'doi' in list(scripttjson['citation'].keys()) and scripttjson['citation']['doi']:
                    rec['doi'] = scripttjson['citation']['doi']
                else:
                    rec['doi'] = '20.2000/%s/%s' % (abbr.upper(), re.sub('.*\/', '', rec['artlink']))
                    rec['link'] = rec['artlink']
                if 'id' in scripttjson['citation']:
                    rec['p1'] = scripttjson['citation']['id']
            #OA
            if 'oa_policy' in list(scripttjson.keys()) and scripttjson['oa_policy']:
                rec['note'].append(scripttjson['oa_policy'])
                print('  ', scripttjson['oa_policy'])

    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
