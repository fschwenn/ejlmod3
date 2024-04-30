# -*- coding: utf-8 -*-

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3

publisher = 'IOS Press'

def fsunwrap(tag):
    try: 
        for i in tag.find_all('i'):
            cont = i.string
            i.replace_with(cont)
    except:
        print('fsunwrap-i-problem')
    try: 
        for b in tag.find_all('b'):
            cont = b.string
            b.replace_with(cont)
    except:
        print('fsunwrap-b-problem')
    try: 
        for sup in tag.find_all('sup'):
            cont = sup.string
            sup.replace_with('^'+cont)
    except:
        print('fsunwrap-sup-problem')
    try: 
        for sub in tag.find_all('sub'):
            cont = sub.string
            sub.replace_with('_'+cont)
    except:
        print('fsunwrap-sub-problem')
    try: 
        for form in tag.find_all('formula'):
            form.replace_with(' [FORMULA] ')
    except:
        print('fsunwrap-form-problem')
    return tag

def ios(link, jnl, vol):
    print('open %s' % (link))
    page = BeautifulSoup(urllib.request.urlopen(link))
    recs = []
    #series
    for div in page.body.find_all('div', attrs = {'class' : 'value series'}):
        if re.search('Proceedings of the International School of Physics.*Enrico', div.text):
            jnl = 'Proc.Int.Sch.Phys.Fermi'
    #VOLUME
    for div in page.body.find_all('div', attrs = {'class' : 'value volume'}):
        vol = div.string
    for chapter in page.body.find_all('div', attrs = {'class' : 'bookseriesvolumearticlelistitem'}):
        rec = {'auts' : [], 'jnl' : jnl, 'tc' : 'C'}
        rec['vol'] = vol
        #TITLE
        for div in chapter.find_all('div', attrs = {'class' : 'value title'}):
            rec['tit'] = div.text
        #AUTHORS
        for div in chapter.find_all('div', attrs = {'class' : 'value authors'}):
            for aut in re.split(', ', div.string):
                rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', aut))
        #DOI
        for div in chapter.find_all('div', attrs = {'class' : 'value doi'}):
            rec['doi'] = div.string
        #PAGES
        for div in chapter.find_all('div', attrs = {'class' : 'value pages'}):
            rec['p1'] = re.sub(' *\-.*', '', div.string)
            if re.search('\-', div.string):
                rec['p2'] = re.sub('.*\- *', '', div.string)
        #ABSTRACT
        for div in chapter.find_all('div', attrs = {'class' : 'abstract'}):
            for p in div.find_all('p'):
                rec['abs'] = fsunwrap(p).get_text()
        #YEAR, CNUM
        if len(args) > 1:
            rec['year'] = year
            if len(args) > 2:
                rec['cnum'] = cnum  
                if len(args) > 3:
                    rec['fc'] = args[3]
        #APPEND IT TO LIST
        if 'doi' in rec:
            recs.append(rec)
    for a in page.body.find_all('a', attrs = {'title' : 'Show next page'}):
        print('next page')        
        nextpage = 'http://ebooks.iospress.nl' + a['href']
        recs += ios(nextpage, jnl, vol)
    return recs
    


if __name__ == '__main__':
    usage = """
        python ios_crawler.py link year [cnum]
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 4:
            raise getopt.GetoptError("Too many arguments given!!!")
        elif not args:
            raise getopt.GetoptError("Missing mandatory argument link")
    except getopt.GetoptError as err:
        print((str(err)))  # will print something like "option -a not recognized"
        print(usage)
        sys.exit(2)

    link = args[0]
    if len(args) > 1:
        year = args[1]
        if len(args) > 2:
            cnum = args[2]    
    jnlfilename = 'ios_'+re.sub('.*\/', '', link)
    recs = ios(link, 'BOOK', '')

ejlmod3.writenewXML(recs, publisher, jnlfilename)
