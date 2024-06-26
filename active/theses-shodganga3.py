# -*- coding: utf-8 -*-
#harvest theses from Shodghanga
#FS: 2018-02-05
#FS: 2023-01-09

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import pickle
import datetime

picklefile = '/afs/desy.de/user/l/library/lists/shodghanga.list.pickle'

publisher = 'Shodhganga'
pages = 2
years = 3
recsperxml = 50
skipalreadyharvested = True
skiptooold = True
server = 'shodhganga.inflibnet.ac.in'
#server = 'sg.inflibnet.ac.in'

kw = sys.argv[1]
start = int(sys.argv[2])
ende = int(sys.argv[3])

now = datetime.datetime.now()


fourofour = 0
#check list of departments for physics and math
comlistlink = 'https://%s/community-list' % (server)
comlistfile = '/tmp/shodganga.community.list-%4i-%02i' % (ejlmod3.year(), now.month)
if not os.path.isfile(comlistfile):
    print('downloading "%s" to "%s"' % (comlistlink, comlistfile))
    os.system('wget -O %s %s' % (comlistfile, comlistlink))
    if int(os.path.getsize(comlistfile)) <= 0:
        print('"%s" is empty :(' % (comlistfile))
        os.remove(comlistfile)        
try:
    inf = open(comlistfile, 'r')
    comlist = BeautifulSoup(''.join(inf.readlines()), features="lxml")
    inf.close()
    departments = {'Physics' : [], 'Math' : [], 'Astro' : []}
    for div in comlist.find_all('div', attrs = {'class' : 'container'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'ul':
                for child2 in child.children:
                    try:
                        child2.name
                    except:
                        continue
                    if child2.name == 'li':
                        for child3 in child2.children:
                            try:
                                child3.name
                            except:
                                continue
                            if child3.name == 'div':
                                for child4 in child3.children:
                                    try:
                                        child4.name
                                    except:
                                        continue
                                    if child4.name == 'h4':
                                        for a in child4.find_all('a'):
                                            uni = a.text.strip()
                                    elif child4.name == 'ul':
                                        for li in child4.find_all('li'):
                                            for a in li.find_all('a'):
                                                hdl = re.sub('.*handle\/', '', a['href'])
                                                dep = a.text.strip()
                                                for kwt in list(departments.keys()):
                                                    if re.search(kwt, dep, flags=re.IGNORECASE):
                                                        departments[kwt].append((hdl, uni, dep))
                                                        continue
    ouf = open(picklefile, 'wb')
    pickle.dump(departments, ouf, 2)
    ouf.close()
except:
    print('load departments from pickle')
    inf = open(picklefile, 'rb')
    departments = pickle.load(inf)
    inf.close()
                               

alreadyharvested = []
jnlfilename = 'THESES-SHODHGANGA1'
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    
recs = []
i = 0
k = 0
for (hdl, uni, dep) in departments[kw]:
    i += 1
    if i < start or i > ende:
        continue
    try:
        ejlmod3.printprogress("=", [[kw], [i-start+1, ende-start+1], [i, len(departments[kw])], [uni]])
    except:
        ejlmod3.printprogress("=", [[kw], [i-start+1, ende-start+1], [i, len(departments[kw])]])
    pickedfromuni = 0
    gotall = False
    for j in range(pages):
        if gotall:
            print('   got all %s' % (nall))
            break
        tocurl = 'https://%s/handle/%s?offset=%i' % (server, hdl, j*20)            
        ejlmod3.printprogress('-', [[j+1, pages], [tocurl]])
        nall = 0 
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(5)
        except:
            if not fourofour:
                try:
                    print("retry %s in 300 seconds" % (tocurl))
                    time.sleep(300)
                    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
                except:
                    print(' +++ 404 +++')
                    fourofour += 1
                    break
            else:
                print(' +++ 404 +++')
                fourofour += 1
                break
        #pick individual links            
        for tr in tocpage.body.find_all('tr'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'keyw' : [], 'note' : []}
            keepit = True
            #fc
            if kw == 'Astro':
                rec['fc'] = 'a'
            elif kw == 'Math':
                rec['fc'] = 'm'
            #affiliation
            rec['aff'] = ['%s, %s, India' % (uni, dep)]
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                #no! this is just date of the record, not of the thesis
                #rec['date'] = re.sub('\-', ' ', td.text.strip())
                #title and link
                for td2 in tr.find_all('td', attrs = {'headers' : 't2'}):   
                    rec['tit'] = td2.text.strip()
                    for a in td2.find_all('a'):                
                        rec['link'] = 'http://%s%s' % (server, a['href'])
                        rec['hdl'] = re.sub('.*handle\/', '',  a['href'])
                        if rec['hdl'] in alreadyharvested:
                            print('    %s already harvested' % (rec['hdl']))
                            keepit = False
                        elif ejlmod3.checknewenoughDOI(rec['hdl']):
                            rec['FFT'] = re.sub('\/', '_', rec['hdl']) + '.pdf'
                        else:
                            print('    %s already known to be too old' % (rec['hdl']))
                            keepit = False
                #author
                for td2 in tr.find_all('td', attrs = {'headers' : 't3'}):   
                    rec['auts'] = [ td2.text.strip() ]
                #supervisor
                for td2 in tr.find_all('td', attrs = {'headers' : 't4'}):
                    for sv in re.split(' and ', td2.text.strip()):
                        rec['supervisor'].append( [ sv ])
                ##get article page
                if not keepit:
                    continue
                try:
                    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
                    time.sleep(5)
                except:
                    try:
                        print("retry %s in 180 seconds" % (rec['link']))
                        time.sleep(180)
                        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
                    except:
                        print("no access to %s" % (rec['link']))                            
                        continue
                for meta in artpage.head.find_all('meta'):
                    if 'name' in meta.attrs:
                        #pages
                        if meta['name'] in ['DCTERMS.spatial', 'DCTERMS.extent']:
                            if re.search('\d\d+', meta['content']):
                                rec['pages'] = re.sub('^\D?(\d\d+).*', r'\1', meta['content'])
                        #date
                        elif meta['name'] == 'DC.date':
                            if re.search('\d\d\d\d', meta['content']):
                                if re.search('[A-Za-z]+.*\d\d\d\d', meta['content']):
                                    rec['date'] = re.sub('.*(\d\d\d\d).*', r'\1',  meta['content'])
                                elif meta ['content'] == '25.11.2011':
                                    rec['date'] = '2011-11-25'
                                else:
                                    rec['date'] = meta['content']
                        #abstract
                        elif meta['name'] == 'DCTERMS.abstract':
                            if len(meta['content']) > 50:
                                rec['abs'] = meta['content']
                        #keywords
                        elif meta['name'] == 'DC.subject':
                            rec['keyw'].append(meta['content'])
                if not 'abs' in list(rec.keys()):
                    rec['note'].append('Vorsicht! kein Abstract')
                #license
                for a in artpage.find_all('a'):
                    if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                        rec['license'] = {'url' : a['href']}
                #year
                if 'date' in list(rec.keys()):
                    year = int(re.sub('.*(\d\d\d\d).*', r'\1', rec['date']))
                    if year > ejlmod3.year() - years:
                        recs.append(rec)
                        pickedfromuni += 1
                        if len(recs) % recsperxml == 0:
                            jnlfilename = 'THESES-SHODHGANGA-%s_%s_%02i-%i_%i-%i_%i' % (ejlmod3.stampoftoday(), kw, k, start, ende, i, len(departments[kw]))
                            #closing of files and printing
                            ejlmod3.writenewXML(recs, publisher, jnlfilename)
                            #metarecs.append(recs)
                            recs = []
                            k += 1 
                    else:
                        print('    %s: %i is too old' % (rec['hdl'], year))
                        ejlmod3.addtoooldDOI(rec['hdl'])
                else:
                    rec['note'].append('kein Datum')
        #got already all
        for div in tocpage.body.find_all('div', attrs = {'class' : 'browse_range'}):
            divt = div.text.strip()
            if re.search('\d+ of \d+', divt):
                nsofar = re.sub('.* (\d+) of \d+.*', r'\1', divt)
                nall = re.sub('.* \d+ of (\d+).*', r'\1', divt)
                if nsofar == nall: gotall = True
    print('        picked %s of %s (total %s)' % (pickedfromuni, nall, len(recs)))
if recs:
    if fourofour:
        jnlfilename = 'THESES-SHODHGANGA-%s_%s_%02i-%i_%i-%i_%i_fin_%isites_not_reached' % (ejlmod3.stampoftoday(), kw, k, start, ende, i, len(departments[kw]), fourofour)
    else:
        jnlfilename = 'THESES-SHODHGANGA-%s_%s_%02i-%i_%i-%i_%i_fin' % (ejlmod3.stampoftoday(), kw, k, start, ende, i, len(departments[kw]))
    #closing of files and printing
    ejlmod3.writenewXML(recs, publisher, jnlfilename)
    
    
