# -*- coding: utf-8 -*-
#program to harvest SPIE Proceedings
# FS 2017-08-27
# FS 2023-01-25

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)



def spie(volume):
    jnlname = 'Proc.SPIE Int.Soc.Opt.Eng.'
    #jnlname = 'Proc.SPIE'
    urltrunc = "https://www.spiedigitallibrary.org"
    toclink = "%s/conference-proceedings-of-spie/%s.toc" % (urltrunc, volume)
    print('open %s' % (toclink))
    page = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(toclink), features="lxml")
    for text in page.body.find_all('text', attrs = {'class' : 'ProceedingsArticleVolTitleText'}):
        conftitle = text.text.strip()
    (section, articletype) = ('', '')
    recs = []
    for div in page.body.find_all('div'):
        if 'class' in div.attrs:
            if 'TOCLineItemSectionHeaderDiv' in div['class']:
                section = div.text.strip()
            elif 'articleType' in div['class']:
                articletype = div.find('a').string
            elif 'TOCLineItemRow1' in div['class'] and not re.search('^Front Matter', section):
                media = []
                for img in div.find_all('img'):
                    if img.has_attr('alt'):
                        media = re.split(' \+ ', img['alt'])
                if 'Paper' in media:
                    rec = {'keyw' : [], 'note' : [section, articletype], 'jnl' : jnlname, 'vol' : volume, 
                           'tc' : 'C', 'autaff' : [], 'refs' : []}
                    for a in div.find_all('a', attrs = {'class' : 'TocLineItemAnchorText1'}):
                        rec['artlink'] = '%s%s' % (urltrunc, a['href'])
                        rec['tit'] = a.text.strip()
                        if not rec['artlink'] in [r['artlink'] for r in recs]:
                            if not rec['artlink'] in ['https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11364/113640I/High-speed-electronics-for-silicon-photonics-transceivers/10.1117/12.2558467.full',
                                                      'https://www.spiedigitallibrary.org/conference-proceedings-of-spie/11455/114556D/Photonic-generation-of-phase-coded-chirp-microwave-waveform-by-an/10.1117/12.2565263.full']:
                                recs.append(rec)
                else:
                    print('  skip', media)        
    #get detailed article pages
    i = 0
    for rec in recs:
        i += 1
        print('  get [%i/%i] %s' % (i, len(recs), rec['artlink']))
        try:
            time.sleep(60)
            #articlepage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
            driver.get(rec['artlink'])
            articlepage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('retry %s in 5 minutes' % (rec['artlink']))
            time.sleep(300)
            #articlepage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400), features="lxml")
            driver.get(rec['artlink'])
            articlepage = BeautifulSoup(driver.page_source, features="lxml")
        for meta in articlepage.head.find_all('meta'):
            if meta.has_attr('name'):
                if meta['name'] == 'citation_author':
                    rec['articlepage'] = articlepage
                    print('    found proper articlepage')
                    break
    #get detailed informations from article pages
    i = 0
    for rec in recs:
        i += 1
        if 'articlepage' in rec:
            print('  open [%i/%i] %s' % (i, len(recs), 'use article page in cache'))
            articlepage = rec['articlepage']
        else:
            print('  open [%i/%i] %s' % (i, len(recs), rec['artlink']))
            try:
                time.sleep(60)
                articlepage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400))
            except:
                print('retry %s in 5 minutes' % (rec['artlink']))
                time.sleep(300)
                articlepage = BeautifulSoup(urllib.request.urlopen(rec['artlink'], timeout=400))
        autaff = []
        ejlmod3.metatagcheck(rec, articlepage, ['citation_firstpage', 'citation_lastpage', 'citation_doi',
                                                'citation_abstract', 'citation_keyword', 'citation_publication_date',
                                                'citation_author', 'citation_author_institution',
                                                'citation_author_orcid', 'citation_author_email'])
        if 'date' in rec:
            rec['year'] = rec ['date'][:4]
        for meta in articlepage.head.find_all('meta', attrs = {'name' : 'pdf'}):
            for OA in articlepage.body.find_all('img', attrs = {'src' : "/Content/themes/SPIEImages/OpenAccessIcon.png"}):
                rec['FFT'] = meta['content']
        #presentation only
        for tag in articlepage.body.find_all('text', attrs = {'class' : 'ProceedingsArticleSmallFont'}):
            rec['note'].append(tag.text.strip())
        #number of pages
        for div in articlepage.body.find_all('text', attrs = {'class' : 'ProceedingsArticleSmallFont'}):
            pages = re.split(' *', div.text.strip())
            if len(pages) == 2 and pages[1] in ['pages', 'PAGES']:
                rec['pages'] = pages[0]
        #references
        for div in articlepage.body.find_all('div', attrs = {'class' : 'section ref-list'}):
            for div2 in div.find_all('div'):
                if div2.has_attr('class'):
                    if 'ref-content' in div2['class']:
                        rdoi = False
                        for a in div2.find_all('a'):
                            if a.has_attr('href') and re.search('doi.org.10', a['href']):
                                rdoi = re.sub('.*?(10\.\d+.*)', r'\1', a['href'])
                            a.replace_with('')
                        ref = re.sub('[\n\t\r]', ' ', div2.text.strip())
                        if reflabel:
                            ref = '[%s] %s' % (reflabel, ref)
                            rec['refs'].append([('x', ref)])
                        if rdoi:
                            ref = re.sub('\.? *$', ', DOI: %s' % (rdoi), ref)
                            rec['refs'].append([('x', ref), ('a', 'doi:%s' % (rdoi))])
                        reflabel = False
                    elif 'ref-label' in div2['class']:
                        reflabel = re.sub('.*?(\d+).*', r'\1', div2.text.strip())
        ###
        if rec['doi'] == '10.1117/12.2536012':
            rec['autaff'] = [['Schaefer, H.']]
        if not rec['autaff'][0]:
            rec['autaff'] = [['NONE']]
        if len(args) > 1:
            rec['cnum'] = args[1]
            if len(args) > 2:
                rec['fc'] = args[2]
        if 'year' in rec:
            print('  %s %s (%s) %s' % (jnlname,volume,rec['year'],rec['p1']))
            ejlmod3.printrecsummary(rec)
        else:
            print('=== PROBLEM WITH RECORD ===')
            ejlmod3.printrec(rec)
            print('===========================')            
            

    #pagenumering vs. articlID
    firstpages = {'count' : 0, 'p1s' : [], 'integercount' : 0}
    for rec in recs:
        if 'p1' in rec:
            firstpages['count'] += 1
            if re.search('^\d+$', rec['p1']) and rec['p1'][:4] != rec['vol'][:4]:
                firstpages['integercount'] += 1
                if 'p2' in rec and re.search('^\d+$', rec['p2']):
                    rec['pages'] = int(rec['p2']) - int(rec['p1']) + 1
            if not rec['p1'] in firstpages['p1s']:
                firstpages['p1s'].append(rec['p1'])
    print("%i of %i records have rec['p1'], %i look like pagenumbers; %i different rec['p1']: %s" % (firstpages['count'], len(recs), firstpages['integercount'], len(firstpages['p1s']), firstpages['p1s']))
    todo = False
    if firstpages['integercount'] > len(recs) / 2:
        if len(firstpages['p1s']) < len(recs) / 2:
            todo = 'remove p1'
        else:
            todo = 'add articleID'
    print('action:', todo)
    rearticleid = re.compile('.*spie\/\d+\/(.*?)\/.*')
    for rec in recs:
        if todo:
            if todo == 'remove p1':
                del rec['p1']
            else:
                rec['alternatejnl'] = rec['jnl']
                rec['alternatevol'] = rec['vol']
                rec['alternatep1'] = rec['p1']
                if 'p2' in rec:
                    rec['alternatep2'] = rec['p2']        
            if 'p2' in rec:
                del rec['p2']            
            if todo == 'add articleID':
                for meta in rec['articlepage'].find_all('meta', attrs = {'name' : 'citation_abstract_html_url'}):
                    rec['p1'] = rearticleid.sub( r'\1', meta['content'])            
        try:
            del rec['articlepage']
        except:
            pass
    
    return recs

if __name__ == '__main__':
    usage = """
        python spie_proc_crawler.py volume [cnum] [fc]
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
    volume = args[0]
    publisher = 'International Society for Optics and Photonics'
    recs = spie(volume)
    if len(args) > 1:
        cnum = args[1]
        if len(args) > 2:
            fc = args[2]
        outfile = 'spie%s_%s' % (volume, cnum)
    else:
        outfile = 'spie%s' % (volume)

    ejlmod3.writenewXML(recs, publisher, outfile)
