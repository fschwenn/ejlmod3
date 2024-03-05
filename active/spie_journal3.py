# -*- coding: utf-8 -*-
#program to harvest SPIE Proceedings
# FS 2017-08-27
# FS 2023-04-04

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import getopt
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

def spie(jnl, vol, iss):
    if jnl == 'jatis':
        jnlname = 'J.Astron.Telesc.Instrum.Syst.'
        jnlspiename = 'Journal-of-Astronomical-Telescopes-Instruments-and-Systems'
    else:
        print('unknown journal "%s"' % (jnl))
    urltrunc = "https://www.spiedigitallibrary.org"
    toclink = "%s/journals/%s/volume-%s/issue-%02i" % (urltrunc, jnlspiename, vol, int(iss))
    print('open %s' % (toclink))
    page = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(toclink), features="lxml")
    (section, articletype) = ('', '')
    recs = []
    for div in page.body.find_all('div'):
        if 'class' in div.attrs:
            if 'TOCLineItemSectionHeaderDiv' in div['class']:
                section = div.text.strip()
            elif 'articleType' in div['class']:
                articletype = div.find('a').string
            elif 'TOCLineItemRow1' in div['class'] and not re.search('^Front Matter', section):
                rec = {'keyw' : [], 'note' : [section, articletype], 'jnl' : jnlname, 'vol' : vol, 'issue' : iss, 
                       'tc' : 'P', 'autaff' : [], 'refs' : []}
                for a in div.find_all('a', attrs = {'class' : 'TocLineItemAnchorText1'}):
                    rec['artlink'] = '%s%s' % (urltrunc, a['href'])
                    rec['tit'] = a.text.strip()
                    if re.search('(List of Reviewers|Editorial)', rec['tit']):
                        continue
                    if not rec['artlink'] in [r['artlink'] for r in recs]:
                        recs.append(rec)
    #get detailed article pages
    i = 0
    for rec in recs:
        i += 1
        print('  get [%i/%i] %s' % (i, len(recs), rec['artlink']))
        try:
            time.sleep(20)
            #artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('retry %s in 5 minutes' % (rec['artlink']))
            time.sleep(300)
            #artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                if meta['name'] == 'citation_author':
                    rec['artpage'] = artpage
                    print('    found proper articlepage')
                    break
    #get detailed informations from article pages
    i = 0
    for rec in recs:
        i += 1
        if 'artpage' in rec:
            print('  open [%i/%i] %s' % (i, len(recs), 'use article page in cache'))
            artpage = rec['artpage']
        else:
            print('  open [%i/%i] %s' % (i, len(recs), rec['artlink']))
            try:
                time.sleep(20)
                #artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
            except:
                print('retry %s in 5 minutes' % (rec['artlink']))
                time.sleep(300)
                #artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
        autaff = []
        ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_doi',
                                            'citation_abstract', 'citation_keyword',
                                            'citation_publication_date', 'citation_author',
                                            'citation_author_institution', 'citation_author_orcid',
                                            'citation_author_email'])
                                            
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                if 'citation_lastpage' in meta['name']:
                    rec['pages'] = re.sub('.*\-','',meta['content'])
                elif 'pdf' in meta['name']:
                    for OA in artpage.body.find_all('img', attrs = {'src' : "/Content/themes/SPIEImages/OpenAccessIcon.png"}):
                        rec['FFT'] = meta['content']
        #presentation only
        for tag in artpage.body.find_all('text', attrs = {'class' : 'ProceedingsArticleSmallFont'}):
            rec['note'].append(tag.text.strip())
        #number of pages
        for div in artpage.body.find_all('text', attrs = {'class' : 'ProceedingsArticleSmallFont'}):
            pages = re.split(' *', div.text.strip())
            if len(pages) == 2 and pages[1] in ['pages', 'PAGES']:
                rec['pages'] = pages[0]
        #references
        for div in artpage.body.find_all('div', attrs = {'class' : 'section ref-list'}):
            reflabel = False
            for div2 in div.find_all('div'):
                if div2.has_attr('class'):
                    if 'ref-content' in div2['class']:
                        rdoi = False
                        for a in div2.find_all('a'):
                            if a.has_attr('href') and re.search('doi.org.10', a['href']):
                                rdoi = re.sub('.*?(10\.\d+.*)', r'\1', a['href'])
                            a.replace_with('')
                        ref = div2.text.strip()
                        if reflabel:
                            ref = '[%s] %s' % (reflabel, ref)
                            rec['refs'].append([('x', ref)])
                        if rdoi:
                            ref = re.sub('\.? *$', ', DOI: %s' % (rdoi), ref)
                            rec['refs'].append([('x', ref), ('a', 'doi:%s' % (rdoi))])
                        reflabel = False
#                    elif 'ref-label' in div2['class']:
#                        reflabel = re.sub('.*?(\d+).*', r'\1', div2.text.strip())
        try:
            del rec['artpage']
        except:
            pass
        if 'year' in rec:
            #print '  %s %s.%s (%s) %s, %s' % (jnlname,vol, iss, rec['year'],rec['p1'],rec['tit'])
            print('  %s %s.%s (%s) %s' % (jnlname,vol, iss, rec['year'],rec['p1']))
            ejlmod3.printrecsummary(rec)
        else:
            print('=== PROBLEM WITH RECORD ===')
            print(rec)
            print('===========================')
    return recs




if __name__ == '__main__':
    usage = """
        python spie_journal.py journal volume issue
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 3:
            raise getopt.GetoptError("Too many arguments given!!!")
        elif not args:
            raise getopt.GetoptError("Missing mandatory argument volume")
    except getopt.GetoptError as err:
        print((str(err)))  # will print something like "option -a not recognized"
        print(usage)
        sys.exit(2)
    jnl = args[0]
    vol = args[1]
    iss = args[2]
    publisher = 'International Society for Optics and Photonics'
    recs = spie(jnl, vol, iss)
    jnlfilename = 'spie_%s%s.%s' % (jnl, vol, iss)
    #dokf = codecs.EncodedFile(open(os.path.join(xmldir,ou

ejlmod3.writenewXML(recs, publisher, jnlfilename)
