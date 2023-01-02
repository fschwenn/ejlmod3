# -*- coding: utf-8 -*-
#!/usr/bin/python
#program to harvest articles from Frontiers-journal
# FS 2018-08-28
# FS 2022-12-19

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import codecs
from bs4 import BeautifulSoup
import time

tmpdir = '/tmp'

timestamp = time.strftime("%03j-%H%M", time.localtime())
publisher = 'Frontiers'
typecode = 'P'
jnlfilename = 'frontiers.' + timestamp

sectiontofc = {'Astrobiology' : 'a', 'Astrochemistry' : 'a',
               'Exoplanets' : 'a', 'Astrostatistics' : 'a',
               'Extragalactic Astronomy' : 'a', 'Fundamental Astronomy' : 'a',
               'Space Physics' : 'a', 'Space Robotics' : 'a',
               'High-Energy and Astroparticle Physics' : 'a',
               'Planetary Science' : 'a', 'Stellar and Solar Physics' : 'a',
               'Astronomical Instrumentation' : 'ai',
               'Radiation Detectors and Imaging' : 'i',
               'Cosmology' : 'ag',
               'Condensed Matter Physics' : 'f',
               'Machine Learning and Artificial Intelligence' : 'c',
               'Mathematical and Statistical Physics' : 'm',
               'AI for Human Learning and Behavior Change' : 'c',
               'AI in Business' : 'c',
               'AI in Food, Agriculture and Water' : 'c',
               'Artificial Intelligence in Finance' : 'c',
               'Big Data and AI in High Energy Physics' : 'c',
               'Big Data Networks' : 'c',
               'Quantum Engineering and Technology' : 'q'}

urls = sys.argv[1:]
recs = []
i = 0
for artlink in urls:
    i += 1
    ejlmod3.printprogress('-', [[i, len(urls)], [artlink]])
    if artlink in ['http://click.engage.frontiersin.com/?qs=42b61da43a3f9df6013a23b68436a54baa8c80ffee48007a24c58c48dea197f28e8e542608b09cd5f247e97e276ce0ad2dc2d41a82d633a97db80e0b25f249be',
                   'http://click.engage.frontiersin.com/?qs=f38f1870c56dcbfecc918de16e443951cd63dd13638046942de37046a6b277e1b668fc558b74e4d8fce61d9c60b0fbbaa011c26e0b58e0b1aed51711d07b43af',
                   'http://click.engage.frontiersin.com/?qs=7924d9eced8ace4bc1fe79b5d27da08c4edb5ac2f674162f35a53feaecc1801271ce07c9c7c074668b8e64e1ccf21c2135d1cb211cc57e34a6b9cffc865f7d03',
                   'http://click.engage.frontiersin.com/?qs=f38f1870c56dcbfecc918de16e443951cd63dd13638046942de37046a6b277e135eed14992b8c3c7d2122930241cf225aa6a324ac73c3f57366a06bbc2fdd4a1',
                   'http://click.engage.frontiersin.com/?qs=f38f1870c56dcbfe8541a1a57ac950e6a60498ebc55375cffafff4fd3132555d20394944b66337553cda0df56ba94f01d305afd60124df417ca75062ffee02cd',
                   'http://click.engage.frontiersin.com/?qs=f38f1870c56dcbfe8541a1a57ac950e6a60498ebc55375cffafff4fd3132555dc2671c4873b888b1088098d8c958d81929a3a95368064553cb63c83832025ef4']:
        continue
    rec = {'tc' : 'P', 'autaff' : [], 'refs' : [], 'note' : []}
    artfilename = re.sub('.*=', '/tmp/frontiers.', artlink)
    if not os.path.isfile(artfilename):
        print('     downloading "%s"' % (artfilename))
        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (artfilename, artlink))
        time.sleep(3)
    #artfile = codecs.EncodedFile(codecs.open(artfilename, mode='rb', errors='replace'), 'utf8')
    artfile = open(artfilename, 'r')
    artlines = ''.join(artfile.readlines())
    artfile.close()
    artlines = re.sub('.*<html', '<html', artlines)
    artpage = BeautifulSoup(artlines, features="lxml")       
    #try:
        #artpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(artlink), features="lxml")
        #time.sleep(3)
    #except:
        #print "retry %s in 180 seconds" % (artlink)
        #time.sleep(180)
        #artpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(artlink), features="lxml")
    autaff = False
    try:
        artpage.head.find_all('meta')
    except:
        continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_volume', 'citation_doi', 'citation_pages',
                                        'citation_title', 'citation_keywords', 'citation_abstract',
                                        'citation_pdf_url', 'citation_online_date', 'citation_author',
                                        'citation_author_institution', 'citation_author_orcid',
                                        'citation_author_email'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #journal
            if meta['name'] == 'citation_journal_title':
                if meta['content'] == 'Frontiers in Astronomy and Space Sciences':
                    rec['jnl'] = 'Front.Astron.Space Sci.'
                elif meta['content'] == 'Frontiers in Physics':
                    rec['jnl'] = 'Front.in Phys.'
                elif meta['content'] == 'Frontiers in Artificial Intelligence':
                    rec['jnl'] = 'Front.Artif.Intell.'
                elif meta['content'] == 'Frontiers in Big Data':
                    rec['jnl'] = 'Front.Big Data'
                else:
                    print('do not know journal "%s"!' % (meta['content']))
                    sys.exit(0)
            #year
            elif meta['name'] == 'citation_date':
                rec['year'] = meta['content']
    if not 'doi' in list(rec.keys()):
        continue
    #license
    for a in artpage.body.find_all('a', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : a['href']}
    #FFT
    if not 'FFT' in list(rec.keys()):
        rec['FFT'] = 'https://www.frontiersin.org/articles/%s/pdf' % (rec['doi'])
    #section
    for a in artpage.body.find_all('a', attrs = {'data-test-id' : 'section-link'}):
        section = a.text.strip()
        if section in list(sectiontofc.keys()):
            if 'fc' in list(rec.keys()):
                for fc in sectiontofc[section]:
                    if not fc in rec['fc']:
                        rec['fc'] += fc
            else:
                rec['fc'] = sectiontofc[section]
        else:
            rec['note'].append(section)
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'References'}):
        for a in div.find_all('a'):
            a.replace_with('')
        rec['refs'].append([('x', div.text.strip())])
    ### meta tags not well formatted or filled
    #date
    for div in artpage.body.find_all('div', attrs = {'class' : 'article-header-container'}):
        if not 'date' in list(rec.keys()) or rec['date'] == '0001/01/01':            
            for div2 in div.find_all('div', attrs = {'class' : 'header-bar-three'}):
                div2t = re.sub('[\n\r\t]', ' ', div2.text.strip())
                if re.search(' [12]\d\d\d', div2t):
                    rec['date'] = re.sub('.*, (.*?[12]\d\d\d).*', r'\1', div2t)
    #pubnote
    for div in artpage.body.find_all('div', attrs = {'class' : 'AbstractSummary'}):
        for p in div.find_all('p'):
            for span in p.find_all('span'):
                if re.search('Citation:', span.text):
                    pt = p.text.strip()
                    if re.search('Front.* (\d+:\d+)\. doi', pt):
                        rec['vol'] = re.sub('.*Front.* (\d+):\d+\. doi.*', r'\1', pt)
                        rec['p1'] = re.sub('.*Front.* \d+:(\d+)\. doi.*', r'\1', pt)        
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
