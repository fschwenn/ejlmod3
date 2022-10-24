# -*- coding: utf-8 -*-
#harvest theses from Royal Holloway, U. of London
#FS: 2021-11-30

import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

jnlfilename = 'THESES-RoyalHolloway-%s' % (ejlmod3.stampoftoday())

startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year()
publisher = 'Royal Holloway, U. of London'



hdr = {'User-Agent' : 'Magic Browser'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
deps = [('department-of-physics(54da7e90-0544-4dbe-bd6d-4e85fa8f7465)', ''),
        ('department-of-mathematics(7ff3623d-1e5a-45d1-8ab1-6929b58c0f0b)', 'm')]
recs = []
for (dep, fc) in deps:
    tocurl = 'https://pure.royalholloway.ac.uk/portal/en/organisations/' + dep + '/publications.html?query=&organisationName=&organisations=&type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput%2Fresearchoutputtypes%2Fthesis%2Fdoc&language=+&publicationYearsFrom=' + str(startyear) + '&publicationYearsTo=' + str(stopyear) + '&publicationcategory=&peerreview=&openAccessPermissionStatus='
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    for h2 in tocpage.body.find_all('h2'):
        for a in h2.find_all('a'):
            rec = {'tc' : 'T', 'note' : [], 'jnl' : 'BOOK', 'supervisor' : []}
            rec['link'] = a['href']
            rec['tit'] = a.text.strip()
            if fc:
                rec['fc'] = fc
            if re.search('\(....+\)', a['href']):
                rec['doi'] = '20.2000/RoyalHolloway/' + re.sub('.*\((.*)\).*', r'\1', a['href'])
            else:
                rec['doi'] = '20.2000/RoyalHolloway/' + re.sub('\W', '', re.sub('.*\/', '', a['href'])[:-4])
            recs.append(rec)
    time.sleep(5)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [re.sub('.*\/', '../', rec['link'])]])
    try:        
        #artpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(rec['link']), features="lxml")
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #author
    for ul in artpage.find_all('ul', attrs = {'class' : 'relations persons'}):
        rec['autaff'] = [[ ul.text.strip(), publisher ]]
    for tr in artpage.find_all('tr'):
        tht = ''
        for th in tr.find_all('th'):
            tht = th.text.strip()
        for td in tr.find_all('td'):
            #supervisor
            if tht == 'Supervisors/Advisors':
                for strong in td.find_all('strong'):
                    rec['supervisor'].append([strong.text.strip()])
            #date
            if tht == 'Award date':
                for span in td.find_all('span'):
                    rec['date'] = span.text.strip()
    #date
    if not 'date' in recs:
        for span in artpage.find_all('span', attrs = {'class' : 'date'}):
            rec['date'] = span.text.strip()            
    #license
    for div in artpage.find_all('div', attrs = {'class' : 'creative_commons_license'}):
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['license'] = {'url' : a['href']}
    #PDF
    for ul in artpage.find_all('ul', attrs = {'class' : 'relations documents'}):
        for a in ul.find_all('a'):
            if a.has_attr('href') and re.search('\.pdf$', a['href']):
                if 'license' in rec:
                    rec['FFT'] = a['href']
                else:
                    rec['hidden'] = a['href']
    #abstract
    for div in artpage.find_all('div', attrs = {'class' : 'textblock'}):
        rec['abs'] = div.text.strip()
    #pages
    for div in artpage.find_all('div', attrs = {'class' : 'publication_view_title'}):
        divt = re.sub('[\n\t\r]', ' ', div.text.strip())
        if re.search('[12]\d\d\d\. *\d\d+ p\.', divt):
            rec['pages'] = re.sub('.*[12]\d\d\d\. *(\d\d+) p\..*', r'\1', divt)
            if not 'date' in rec:
                rec['date'] =re.sub('.*([12]\d\d\d)\. *\d\d+ p\..*', r'\1', divt)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
