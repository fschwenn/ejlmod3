# -*- coding: UTF-8 -*-
#program to harvest ACS journals
# FS 2020-12-04

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

publisher = 'ACS'

jnl =  sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'
downloadpath = '/tmp'


jnlfilename = 'acs_%s%s.%s' % (jnl, vol, iss)
if jnl == 'nalefd': # 1 issue per month
    jnlname = 'Nano Lett.'
    letter = ''
elif jnl == 'jpccck': # 1 issue per week
    jnlname = 'J.Phys.Chem.'
    letter = 'C'
elif jnl == 'apchd5': # 1 issue per month
    jnlname = 'ACS Photonics'
    letter = ''
elif jnl == 'jacsat': # 1 issue per week
    jnlname = 'J.Am.Chem.Soc.'
    letter = ''
elif jnl == 'chreay': # 1 issue per two weaks
    jnlname = 'Chem.Rev.'
    letter = ''
elif jnl == 'jpcafh': # 1 issue per week
    jnlname = 'J.Phys.Chem.A'
    letter = ''
elif jnl == 'jctcce': # 1 issue per two weeks
    jnlname = 'J.Chem.Theor.Comput.'
    letter = ''
else:
    print(' unknown journal "%s"' % (jnl))
    sys.exit(0)

host = os.uname()[1]
options = uc.ChromeOptions()
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
if host == 'l00schwenn':
    options.binary_location='/usr/bin/chromium'
    tmpdir = '/home/schwenn/tmp'
else:
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    tmpdir = '/tmp'
    options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


tocurl = 'https://pubs.acs.org/toc/%s/%s/%s' % (jnl, vol, iss)
print(tocurl)
driver.get(tocurl)
time.sleep(30)
tocpage =  BeautifulSoup(driver.page_source, features="lxml")
section = False
recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'toc'}):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'h6':
            section = child.text.strip()
            print(section)
        elif  child.name == 'div':
            if not section in ['Mastheads', 'Editorial']:
                for input in child.find_all('input', attrs = {'name' : 'doi'}):
                    rec = {'jnl' : jnlname, 'vol' : letter+vol, 'issue' : iss, 'tc' : 'P',
                           'keyw' : [], 'note' : [], 'autaff' : []}
                    rec['doi'] = input['value']
                    rec['artlink'] = 'https://pubs.acs.org/doi/' + input['value']
                    if section:
                        rec['note'] = [ section ]
                    #title
                    for h5 in child.find_all('h5'):
                        rec['tit'] = h5.text.strip()
                    #authors
                    for author in child.find_all('span', attrs = {'class' : 'hlFld-ContribAuthor'}):
                        rec['autaff'].append([author.text.strip()])
                    #pages
                    for span in child.find_all('span', attrs = {'class' : 'issue-item_page-range'}):
                        rec['p1'] = re.sub('\D*(\d+).*', r'\1', span.text.strip())
                        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', span.text.strip())
                    #abs
                    for span in child.find_all('span', attrs = {'class' : 'hlFld-Abstract'}):
                        rec['abs'] = span.text.strip()
                    #date
                    for span in child.find_all('span', attrs = {'class' : 'pub-date-value'}):
                        rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', span.text.strip())
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        time.sleep(60)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        try:
            print('   wait 10 minutes')
            time.sleep(600)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:            
            print('  keep only', list(rec.keys()))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Subject', 'og:description', 'dc.Date'])
    #keywords
    for div in artpage.find_all('div', attrs = {'class' : 'article_header-taxonomy'}):
        if not 'keyw' in rec or not rec['keyw']:
            rec['keyw'] = []
            for a in div.find_all('a'):
                rec['keyw'].append(a.text)
    #fulltext
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:      
        targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec['doi']), re.sub('[\(\)\/]', '_', rec['doi']))
        if os.path.isfile(targetfilename):
            print('     %s already exists' % (targetfilename))
            rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
        else:
            for a in artpage.find_all('a', attrs = {'class' : 'pdf-button'}):
                pdfurl = 'https://pubs.acs.org' + a['href'] + '?download=true'
                savedfilereg = re.compile('%s\-.*\d\d\d\d\-%s.*.pdf$' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            print('     get PDF from %s' % (re.sub('epdf', 'pdf', pdfurl)))
            time.sleep(20)
            #driver.get(pdfurl)
            driver.get(re.sub('epdf', 'pdf', pdfurl))
            #print('        looking for %s\-.*\d\d\d\d\-%s.*.pdf\n\n  --> please click download button <--\n' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            print('        looking for %s\-.*\d\d\d\d\-%s.*.pdf\n' % (re.sub('.* ', '', rec['autaff'][0][0].lower()), re.sub('\W*$', '', re.sub(' .*', '', rec['tit'].lower()))))
            time.sleep(120)
            found = False
            for j in range(18):
                if not found:
                    for datei in os.listdir(downloadpath):
                        if savedfilereg.search(datei):
                            savedfilename = '%s/%s' % (downloadpath, datei)
                            print('     mv %s to %s' % (savedfilename, targetfilename))
                            os.system('mv "%s" %s' % (savedfilename, targetfilename))
                            rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
                            found = True
                if found:
                    break
                else:
                    time.sleep(10)






                
    #authors
    autaff = []
    for span in artpage.find_all('span'):
        divs = span.find_all('div', attrs = {'class' : 'loa-info-name'})
        if divs:
            for div in divs:
                autaff.append([div.text.strip()])
                for a in span.find_all('a', attrs = {'title' : 'Orcid link'}):
                    autaff[-1].append(re.sub('.*\/', r'ORCID:', a['href']))
                for div2 in span.find_all('div', attrs = {'class' : 'loa-info-affiliations-info'}):
                    autaff[-1].append(div2.text.strip())
    if len(autaff) >= len(rec['autaff']):
        rec['autaff'] = autaff
    #pages
    for span in artpage.find_all('span', attrs = {'class' : 'cit-fg-pageRange'}):
        rec['p1'] = re.sub('\D*(\d+).*', r'\1', span.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', span.text.strip())
    #references
    for ol in artpage.find_all('ol', attrs = {'id' : 'references'}):
        rec['refs'] = []
        for div in ol.find_all('div', attrs = {'class' : ['citationLinks', 'casRecord']}):
            div.decompose()
        for li in ol.find_all('li'):
            for a in li.find_all('a', attrs = {'class' : 'refNumLink'}):
                refnum = a.text
                a.replace_with('[%s] ' % (refnum))
            ref = li.text.strip()
            ref = re.sub('[\n\t\r]', ' ', ref)
            rec['refs'].append([('x', ref)])


    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
