# -*- coding: utf-8 -*-
#program to harvest books from Taylor & Francis
# FS 2024-05-28

import sys
import os
import ejlmod3
import re
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

years = 2
skipalreadyharvested = True
subjects = {'SCPC' :  '', 'SCMA' : 'm', 'SCCM' : 'c', 'SCEC' :  ''}
boring = ['Environment & Agriculture', 'Arts', 'Behavioral Sciences', 'Bioscience',
          'Built Environment', 'Business & Industry', 'Dentistry', 'Development Studies',
          'Earth Sciences', 'Economics', 'Education', 'Humanities', 'Communication Studies',
          'Environment and Sustainability', 'Environment', 'Finance',
          'Food Science & Technology', 'Health and Social Care', 'Language & Literature',
          'Hospitality and Events', 'Law', 'Medicine', 'Nursing & Allied Health',
          'Politics & International Relations', 'Social Sciences', 'Social Work',
          'Tourism', 'Urban Studies', 'Geography', 'Global Development', 'Sports and Leisure']
backupbunchlength = 100

jnlfilename = 'tandf_books_%s_' % (ejlmod3.stampoftoday())
publisher = 'Taylor and Francis'

subjectcode = sys.argv[1]
if len(sys.argv) > 2:
    einzelaufnahmen = re.split(',', sys.argv[2])
else:
    einzelaufnahmen = []

host = os.uname()[1]
options = uc.ChromeOptions()
if host == 'l00schwenn':
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    bibclassifycommand = "/usr/bin/python3 /afs/desy.de/user/l/library/proc/python3/bibclassify/bibclassify_cli.py  -k /afs/desy.de/user/l/library/akw/HEPont.rdf -n 10"
else:
    options.binary_location='/usr/bin/google-chrome'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=chromeversion, options=options)
    bibclassifycommand = "python /afs/desy.de/user/l/library/proc/python3/bibclassify/bibclassify_cli.py  -k /afs/desy.de/user/l/library/akw/HEPont.rdf -n 10"
absdir = '/afs/desy.de/group/library/publisherdata/abs'
tmpdir = '/afs/desy.de/user/l/library/tmp'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

driver.get('https://www.taylorfrancis.com')
time.sleep(5)

#check lists of books
prerecs = []
artlinks = []
publisherrecs = {}
toclink = 'https://www.taylorfrancis.com/search?sortBy=newest-to-oldest&key=&subject=' + subjectcode + '&from=' + str(ejlmod3.year(backwards=years-1)) + '&to=' + str(ejlmod3.year())
ejlmod3.printprogress('===', [[toclink]])
driver.get(toclink)
time.sleep(5)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
for ul in tocpage.find_all('ul', attrs = {'class' : 'ngx-pagination'}):
    for li in ul.find_all('li', attrs = {'class' : 'small-screen'}):
        pages = int(re.sub('.*\/ ', '', li.text.strip()))
        print('   %i pages' % (pages))
        pages = min(100, int(re.sub('.*\/ ', '', li.text.strip())))
            
            

for page in range(pages):
    if page > 0:
        time.sleep(3)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for srp in tocpage.find_all('search-results-product'):
        for a in srp.find_all('a', attrs = {'data-gtm' : 'gtm-search-result'}):
            rec = {'jnl' : 'BOOK', 'tc' : 'B', 'autaff' : [], 'note' : [], 'isbns' : [],
                   'chapterlinks' : [], 'editor' : False}
            if subjectcode in subjects:
                rec['fc'] = subjects[subjectcode]
            rec['artlink'] = re.sub('\?context.*', '', a['href'])
            doi = re.sub('.*orfrancis.com\/books\/.*?\/(10\..*)\/.*', r'\1', rec['artlink'])
            if doi in einzelaufnahmen:
                print('   %s explicitely requested' % (doi))
                prerecs.append(rec)
                artlinks.append(rec['artlink'])
            elif skipalreadyharvested and rec['artlink'] in alreadyharvested:
                print('   %s already in backup' % (doi))                        
            elif rec['artlink'] in artlinks:
                print('   %s already in list' % (doi))
            elif ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)
                artlinks.append(rec['artlink'])
            else:
                print('   %s uninteresting' % (doi))
    print('  %i records so far' % (len(prerecs)))
    time.sleep(10)
    if page < pages-1:            
        ejlmod3.printprogress('=', [[subjectcode], [page+2, pages]])        
        #for clp in tocpage.find_all('core-lib-pagination'):
        #    print(clp)
        xp = '//a[@aria-label="Next page"]'
        try:
            driver.find_element(by=By.XPATH, value=xp).click()
        except:
            print('can not click next page :(')
time.sleep(180)

#check detail pages of books
recs = []
for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    keepit = True
    #title
    for h1 in artpage.body.find_all('h1'):
        rec['tit'] = h1.text.strip()
    #chapter links
    for pt in artpage.find_all('product-toc'):
        for a in pt.find_all('a', attrs = {'data-gtm' : 'gtm-toc-chapter'}):
            rec['chapterlinks'].append('https://www.taylorfrancis.com' + re.sub('\?context.*', '', a['href']))
        pt.decompose()
    for div in artpage.find_all('div', attrs = {'class' : 'product-details'})[:1]:
        for slpa in div.find_all('shared-lib-product-authors'):
            #collection or monography?
            for span in slpa.find_all('span', attrs = {'class' : 'product-banner-author'}):
                if span.text.strip() == 'Edited By':
                    rec['editor'] = True
            #authors/editors
            for span in slpa.find_all('span', attrs = {'class' : 'product-banner-author-name'}):
                for a in span.find_all('a'):
                    if a.has_attr('href') and re.search('contributorName', a['href']):
                        if rec['editor']:
                            rec['autaff'].append([a.text.strip() + ' (Ed.)'])
                        else:
                            rec['autaff'].append([a.text.strip()])
                    elif a.has_attr('href') and re.search('orcid.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    else:
                        print('[author-info???]', a)
    #abstract
    for div2 in artpage.body.find_all('div', attrs = {'class' : 'book-content'}):
        rec['abs'] = div2.text.strip()
    for div2 in artpage.body.find_all('div', attrs = {'class' : 'product-banner-publication'}):
        for div3 in div2.find_all('div', attrs = {'class' : 'display-row'}):
            for span in div3.find_all('span', attrs = {'class' : 'display-label'}):
                th = span.text.strip()
                #DOI
                if th == 'DOI':
                    for a in div3.find_all('a'):
                        rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
                        if skipalreadyharvested and rec['doi'] in alreadyharvested:
                            if not rec['doi'] in einzelaufnahmen:
                                keepit = False
                                print('    %s already in backup' % (rec['doi']))
            for span in div3.find_all('span', attrs = {'class' : 'product-ryt-detail'}):
                #edition
                if th == 'Edition':
                    rec['note'].append(span.text.strip())
                #date
                elif th in ['First Published', 'eBook Published']:
                    rec['date'] = span.text.strip()
                #publisher
                elif th == 'Imprint':
                    rec['publisher'] = span.text.strip()
                #pages
                elif th == 'Pages':
                    rec['pages'] = span.text.strip()
                #ISBN
                elif th == 'eBook ISBN':
                    rec['isbns'].append([('a', span.text.strip()), ('b', 'Online')])
                #OA                
                elif th == 'OA Funder':
                    ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
                #subjects
                elif th == 'Subjects':
                    for subj in re.split(', ', span.text.strip()):
                        if subj == 'Computer Science':
                            if 'fc' in rec:
                                if not 'c' in rec['fc']:
                                    rec['fc'] += 'c'
                            else:
                                rec['fc'] = 'c'
                        elif subj in boring:
                            if keepit:
                                print('   skip "%s"' % (subj))
                                keepit = False
                                ejlmod3.adduninterestingDOI(rec['artlink'])
                        elif not subj in ['Engineering & Technology', 'Physical Sciences',
                                          'Mathematics & Statistics']:
                            rec['note'].append('SUBJECT:::' + subj)
                elif not th in ['Pub. Location']:
                    print('  [th???]', th)
    #DOI
    if not 'doi' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_doi'])
    #publisher
    if not 'publisher' in rec:
        rec['publisher'] = publisher

    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        #ejlmod3.printrec(rec)
        if rec['publisher'] in publisherrecs:
            publisherrecs[rec['publisher']].append(rec)
        else:
            publisherrecs[rec['publisher']] = [rec]
        if len(recs) % backupbunchlength == 0:
            ejlmod3.writenewXML(recs[-backupbunchlength:], publisher, jnlfilename + '_' +  str(len(recs)), retfilename='retfiles_special')    
    time.sleep(10)


#save hauptaufnahmen grouped by publisher
for publisher in publisherrecs:
    pjnlfilename = jnlfilename + re.sub('[\W ]', '', publisher)
    ejlmod3.writenewXML(publisherrecs[publisher], publisher, pjnlfilename, retfilename='retfiles_special')    
    

#2nd detailed run for einzelaufnahmen
reqis = re.compile('^\d+ *')
recorekeywords = re.compile('^Core keywords')
recsforeinzelaufnahmen = []
for (i, rec) in enumerate(recs):
    try:
        ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['doi']]])
    except:
        ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])

    if rec['editor']:
        rec['einzelaufnahmen'] = False
        if 'doi' in rec:
            if rec['doi'] in einzelaufnahmen:
                rec['einzelaufnahmen'] = True
            else:
                doi1 = re.sub('[\(\)\/]', '_', rec['doi'])
                absfilename = os.path.join(absdir, doi1)
                bibfilename = os.path.join(tmpdir, doi1+'.bib')
                if not os.path.isfile(bibfilename):
                    print(' >bibclassify %s' % (doi1))
                    try:
                        print(' >%s %s > %s' % (bibclassifycommand, absfilename, bibfilename))
                        os.system('%s %s > %s' % (bibclassifycommand, absfilename, bibfilename))
                    except:
                        print('FAILURE: %s %s > %s' % (bibclassifycommand, absfilename, bibfilename))
                    time.sleep(.3)
                if os.path.isfile(bibfilename):
                    absbib = open(bibfilename, 'r')
                    lines = absbib.readlines()
                    corekeywords = False
                    for line in lines:
                        if corekeywords:
                            if reqis.search(line):
                                print(line.strip())
                                rec['einzelaufnahmen'] = True
                        elif recorekeywords.search(line):
                            corekeywords = True                            
                    absbib.close()
            print('  einzelaufnahmen?', rec['einzelaufnahmen'])
            if rec['einzelaufnahmen']:
                recsforeinzelaufnahmen.append(rec)
                try:
                    cjnlfilename = jnlfilename + re.sub('\/', '_', rec['doi'])
                except:
                    cjnlfilename = jnlfilename + re.sub('\/', '_', rec['isbns'][0][0][1])
                rec['note'].append('einzelaufnahmen in %s' % (cjnlfilename))
#    else:
#        print('  monograph')

#save hauptaufnahmen grouped by publisher
for publisher in publisherrecs:
    pjnlfilename = jnlfilename + subjectcode + re.sub('[\W ]', '', publisher)
    ejlmod3.writenewXML(publisherrecs[publisher], publisher, pjnlfilename)#, retfilename='retfiles_special')    


#actually get the einzelaufnahmen
for (i, rec) in enumerate(recsforeinzelaufnahmen):
    ejlmod3.printprogress('+', [[i+1, len(recsforeinzelaufnahmen)], [rec['artlink']]])
    try:
        ejlmod3.printprogress('+', [[i+1, len(recs)], [rec['doi']]])
        cjnlfilename = jnlfilename + re.sub('\/', '_', rec['doi'])
    except:
        ejlmod3.printprogress('+', [[i+1, len(recs)], [rec['artlink']]])
        cjnlfilename = jnlfilename + re.sub('\/', '_', rec['isbns'][0][0][1])
    crecs = []
    for (j, artlink) in enumerate(rec['chapterlinks']):
        ejlmod3.printprogress('~', [[i+1, len(recsforeinzelaufnahmen)], [j+1, len(rec['chapterlinks'])], [artlink]])
        crec = {'tc' : 'S', 'jnl' : 'BOOK', 'date' : rec['date'],
                'motherisbn' : rec['isbns'][0][0][1],
                'artlink' : artlink, 'autaff' : []}
        crec['note'] = ['chapter in "%s"' % (rec['tit'])]
        if 'fc' in rec:
            crec['fc'] = rec['fc']
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(crec, artpage, ['citation_doi', 'citation_firstpage', 'citation_lastpage'])
        #title
        for h1 in artpage.body.find_all('h1'):
            crec['tit'] = h1.text.strip()
        #authors
        for slpa in artpage.body.find_all('shared-lib-product-authors'):
            for span in slpa.find_all('span', attrs = {'class' : 'product-banner-author-name'}):
                for a in span.find_all('a'):
                    if a.has_attr('href') and re.search('contributorName', a['href']):
                        crec['autaff'].append([a.text.strip()])
                    elif a.has_attr('href') and re.search('orcid.org', a['href']):
                        crec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    else:
                        print('[author-info???]', a)
        #abstract
        for div2 in artpage.body.find_all('div', attrs = {'class' : 'book-content'}):
            crec['abs'] = div2.text.strip()
        for div2 in artpage.body.find_all('div', attrs = {'class' : 'product-banner-publication'}):
            for div3 in div2.find_all('div', attrs = {'class' : 'display-row'}):
                for span in div3.find_all('span', attrs = {'class' : 'display-label'}):
                    th = span.text.strip()
                for span in div3.find_all('span', attrs = {'class' : 'product-ryt-detail'}):
                    #pages
                    if th == 'Pages':
                        crec['pages'] = span.text.strip()
                    #OA                
                    elif th == 'OA Funder':
                        ejlmod3.metatagcheck(crec, artpage, ['citation_pdf_url'])
                    elif not th in ['Pub. Location', 'Edition', 'Imprint',
                                    'First Published', 'eBook Published', 'eBook ISBN']:
                        print('  [th???]', th)
        crecs.append(crec)
        ejlmod3.printrecsummary(rec)
        time.sleep(10)            
    ejlmod3.writenewXML(crecs, rec['publisher'], cjnlfilename)#, retfilename='retfiles_special')    
    time.sleep(10)
        
