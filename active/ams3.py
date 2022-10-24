# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest http://www.ams.org
# FS 2016-07-22
# FS 2022-10-24

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import ssl

jrnid = sys.argv[1]
year = sys.argv[2]
jnlfilename = 'ams_%s%s' % (jrnid, year)
(vol, iss) = ('0', '0')
if len(sys.argv) > 3:
    vol = sys.argv[3]
    jnlfilename += '.%s' % (vol)
    if len(sys.argv) > 4:
        iss = sys.argv[4]
        jnlfilename += '.%s' % (iss)
else:
    jnlfilename += '_%s' % (ejlmod3.stampoftoday())

    


jnldict = {'ecgd' : {'tit' : 'Conform.Geom.Dyn.',
                     'link' : 'home-%s.html' % (year),
                     'oa' : True},
           'jams' : {'tit' : 'J.Am.Math.Soc.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'embargo' : 5}, 
           'mcom' : {'tit' : 'Math.Comput.',
                     'link' : '%s-%s-%s/home.html' % (year, vol, iss),
                     'embargo' : 5}, 
#           'memoirs' : {'tit' : 'Mem.Am.Math.Soc.',
           'proc' : {'tit' : 'Proc.Am.Math.Soc.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'embargo' : 5}, 
           'bproc' : {'tit' : 'Proc.Am.Math.Soc.Ser.B',
                      'link' : 'home-%s.html' % (year),
                      'oa' : True},
           'ert' : {'tit' : 'Represent.Theory',
                      'link' : 'home-%s.html' % (year),
                      'oa' : True},
           'tran' : {'tit' : 'Trans.Am.Math.Soc.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'embargo' : 5}, 
           'btran' : {'tit' : 'Trans.Am.Math.Soc.Ser.B',
                      'link' : 'home-%s.html' % (year),
                      'oa' : True},
           #member journals
           #          '' : {'tit' : 'Not.Amer.Math.Soc.',
           'bull' : {'tit' : 'Bull.Am.Math.Soc.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'oa' : True}, 
           #           '' : {'tit' : 'Abstracts Amer.Math.Soc.',
           #translation journals
           'spmj' : {'tit' : 'St.Petersburg Math.J.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'embargo' : 5},
           'tpms' : {'tit' : 'Theor.Probab.Math.Stat.',
                     'link' : '%s-%s-00/home.html' % (year, vol),
                     'oa' : True}, 
           'mosc' : {'tit' : 'Trans.Moscow Math.Soc.',
                     'link' : '%s-%s-00/home.html' % (year, vol),
                     'embargo' : 6},
           #distributed journals
           'qam' : {'tit' : 'Q.Appl.Math.',
                    'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                    'oa' : False}, 
           #           'mmj' : {'tit' : 'Moscow Math.J.',
           #           'jrms' : {'tit' : 'Ramanujan J.',
           #           '' : {'tit' : 'Asterisque',
           #           '' : {'tit' : 'Bull.Soc.Math.Fr.',
           #           '' : {'tit' : 'Mem.Soc.Math.France',
           #           'jot' : {'tit' : 'J.Operator Theor.',
           'jag' : {'tit' : 'J.Alg.Geom.',
                     'link' : '%s-%s-%02i/home.html' % (year, vol, int(iss)),
                     'oa' : False},}
#           '' : {'tit' : 'Annales Sci.Ecole Norm.Sup.',


#bad cerificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


#check embargo time
if 'embargo' in jnldict[jrnid]:
    now = datetime.datetime.now()
    if now.year - int(year) > jnldict[jrnid]['embargo']:
        jnldict[jrnid]['oa'] = True

publisher = 'AMS'

tocurl = 'http://www.ams.org/journals/%s/%s' % (jrnid, jnldict[jrnid]['link'])
print(tocurl)
tocpage = BeautifulSoup(urllib.request.urlopen(tocurl, context=ctx), features="lxml")



artlinks = []
for a in tocpage.body.find_all('a'):
    if a.has_attr('href') and re.search('article information', a.text):
        artlinks.append(re.sub('^(.*\/).*', r'\1', tocurl) + a['href'])

if not artlinks:
    for dt in tocpage.body.find_all('dt'):
        for a in dt.find_all('a'):
            if a.has_attr('href') and re.search('active=current', a['href']):
                if a.text:
                    artlinks.append(re.sub('^(.*\/).*', r'\1', tocurl) + a['href'])
                

print(artlinks) 


recs = []
for (i, artlink) in enumerate(artlinks):
    ejlmod3.printprogress('-', [[i+1, len(artlinks)], [artlink]])
    try:
        artpage = BeautifulSoup(urllib.request.urlopen(artlink, context=ctx), features="lxml")
        time.sleep(10)
    except:
        print(" - sleep -")
        time.sleep(300)
        artpage = BeautifulSoup(urllib.request.urlopen(artlink, context=ctx), features="lxml")
    rec = {'jnl' : jnldict[jrnid]['tit'], 'tc' : 'P', 'year' : year, 
           'autaff' : [], 'link' : artlink}
    if jrnid == 'spmj':
        rec['note'] = [ 'translation of "Alg.Anal." ']
    ejlmod3.metatagcheck(rec, artpage, ['citation_online_date', 'citation_author',
                                        'citation_author_email', 'citation_author_orcid',
                                        'citation_author_institution', 'citation_volume',
                                        'citation_issue', 'citation_firstpage', 'citation_lastpage',
                                        'citation_doi', 'citation_keywords', 'citation_title',
                                        'citation_reference'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        rec['link'] = meta['content']
        if 'oa' in jnldict[jrnid] and jnldict[jrnid]['oa']:
            rec['FFT'] = meta['content']
      #abstract
    for p in artpage.body.find_all('p'):
        for a in p.find_all('a', attrs = {'name' : 'Abstract'}):
            rec['abs'] = re.sub(' *Abstract: *', '', p.text.strip())
    #references
    if not 'refs' in rec:
        rec['refs'] = []
        for span in artpage.body.find_all('span', attrs = {'class' : 'references'}):
            for dd in span.find_all('dd'):
                rec['refs'].append([('x', dd.text)])
        if not rec['refs']:
            for ul in artpage.body.find_all('ul', attrs = {'class' : 'journalsReferenceList'}):
                for a in ul.find_all('a'):
                    if a.has_attr('href') and re.search('doi.org', a['href']):
                        rdoi = re.sub('.*doi.org\/', '', a['href'])
                        rdoi = re.sub('%28', '(', rdoi)
                        rdoi = re.sub('%29', ')', rdoi)
                        rdoi = re.sub('%2F', '/', rdoi)
                        rdoi = re.sub('%3A', ':', rdoi)
                        a.replace_with(' '+rdoi+' ')
                for li in ul.find_all('li'):
                    rec['refs'].append([('x', li.text)])
    ejlmod3.printrecsummary(rec)
    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
