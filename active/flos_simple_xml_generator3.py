# -*- coding: utf-8 -*-
import os
import ejlmod3
import re
import sys

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

tmpdir = '/tmp'


publisher = 'KEK'


jnlfilename = 'PASJ2022'
#inf = open('/afs/desy.de/user/s/schwenn/contempmath780', 'r')
inf = open('/afs/desy.de/user/s/schwenn/PASJ2022', 'r')
recs = []
cnum = 'C22-10-18.1'
hdr = {'User-Agent' : 'Magic Browser'}

lines =  inf.readlines()
inf.close()
pagehash = {}
p1 = ''
p2 = 0
columnwithpages = 2
if 1 == 1:
    for line in lines:    
        #print line
        if re.search('XXX', line):
            parts = re.split(' *XXX *', line.strip())
            try:
                page = re.sub('\-.*', '', parts[columnwithpages])
                p2 += int(page) - 1
                if p1 != '':
                    pagehash[p1] = str(p2)
                    p2 = 0
            except:
                continue
            p1 = parts[columnwithpages]
#        else:
#            p2 -= 1

i = 0
note = ''
for line in lines:
    i += 1
    if re.search('^#', line):
        note = line[1:].strip()
    if re.search('XXX', line):
        rec = {'jnl' : 'BOOK', 'cnum' : cnum, 
               'year' : '2023', 'tc' : 'C'}#, 'vol' : '763'}
        rec['fc'] = 'b'
#        rec['licence'] = {'url' : 'http://creativecommons.org/licenses/by/4.0',
#                          'statement' : 'CC-BY-4.0'}
        if note: rec['note'] = [ note ]
        parts = re.split(' *XXX *', line.strip())
        if len(parts) == 6:
            rec['tit'] = parts[5]
            rec['transtit'] = parts[4]
        elif len(parts) == 8:
            rec['tit'] = parts[4]
            rec['transtit'] = parts[5]
            rec['language'] = 'Japanese'
        else:
            continue
        #rec['doi'] = parts[3]
        rec['p1'] = parts[columnwithpages]
        #rec['p1'] = str(i)
        #rec['p1'] = re.split('\-', parts[2])[0]
        #rec['p2'] = re.split('\-', parts[2])[1]            
        if rec['p1'] in pagehash:
            rec['p2'] = pagehash[rec['p1']]
        rec['FFT'] = parts[0]
        #rec['arxiv'] = parts[2]
        print(parts)
        rec['auts'] = []
        #rec['pages'] = parts[2]
        if len(parts) == 8:
            autoren = re.split(' *, *', re.sub(' (and|et) ', ', ', parts[7].strip()))
        else:
            autoren = re.split(' *, *', re.sub(' (and|et) ', ', ', parts[5].strip()))
        rec['aff'] = []
        affnr = 0
        for aut in autoren:
            if re.search('\(', aut):
                affnr += 1
                rec['aff'].append(re.sub('.*\((.*)\)', r'Aff%02i= \1' % (affnr), aut))
                rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', re.sub(' *\(.*', '', aut)))
            else:
                #rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', aut))
                rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', aut.strip()).strip())
                #rec['auts'].append(aut.strip())
        #rec['abs'] = parts[3]
        #rec['vol'] = parts[3]
        #rec['motherisbn'] = parts[4]
        rec['link'] = parts[0]

        rec['doi'] = '20.2000/PASJ2022/' + re.sub('.*\/', '', parts[1])

        if 1 == 0:
            print(rec['artlink'])
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            for a in artpage.find_all('a'):
                if re.search('\.pdf', a.text):
                    rec['FFT'] = 'https://www.sao.ru/hq/grb/conf_2017/proc/'+a['href']
            atext = re.sub('[\n\t\r]', ' ', artpage.text.strip())
            rec['abs'] = re.sub('.*Abstract *(.*) *Reference:.*', r'\1', atext)
            rec['doi'] = re.sub('.*(10.26119.*) *Down.*', r'\1', atext)
                                

        recs.append(rec)
        print(rec)

        
    elif re.search('#', line):
        note = re.sub('#', '', line.strip())







        


#



#retrival


line = jnlfilename+'.xml'+ "\n"








ejlmod3.writenewXML(recs, publisher, jnlfilename)
