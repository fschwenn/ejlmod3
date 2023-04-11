# -*- coding: utf-8 -*-
#program to harvest The Messenger
# FS 2019-08-21
# FS 2023-04-05

import sys
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import json


publisher = 'European Southern Observatory'
typecode = ''
vol = sys.argv[1]

jnlname = 'The Messenger'

jnlfilename = 'messenger%s' % (vol)

toclink = 'https://www.eso.org/sci/publications/messenger/toc.html?v=%s&m=X&y=X' % (vol)

print(toclink)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(toclink), features='lxml')
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunk))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(toclink), features='lxml')

section = False
recs = []
for div in tocpage.body.find_all('div', attrs = {'id' : 'col3_content'}):
    for child in div.children:
        try:
            name = child.name
        except:
            continue
        if name == 'h2':
            childt = child.text.strip()
            if childt:
                section = childt
                print(section)
        elif name == 'div':
            if child.has_attr('class'):
                if 'msg_entry' in child['class']:
                    rec = {'jnl' : jnlname, 'vol' : vol, 'tc' : typecode, 'autaff' : []}
                    if section:
                        rec['note'] = [ section ]
                    for div in child.find_all('div', attrs = {'class' : 'msg_page'}):
                        for a in div.find_all('a'):
                            rec['FFT'] = 'https://www.eso.org/sci/publications/messenger/' + a['href']
                            a.replace_with('')
                        pages = re.sub(' *\(.*', '', div.text.strip())
                        rec['p1'] = re.sub('\-.*', '', pages)
                        rec['p2'] = re.sub('.*\-', '', pages)
                        print('  ', rec['p1'])
                    for div in child.find_all('div', attrs = {'class' : 'msg_title'}):
                        rec['tit'] = div.text.strip()
                elif 'msg_abstract' in child['class']:
                    for a in child.find_all('a'):
                        link = a['href']
                        if re.search('doi.org', link) and not 'Astronomical News' in rec['note']:
                            rec['doi'] = re.sub('.*?(10\.\d+.*)', r'\1', link)
                            recs.append(rec)
                    #preDOI era
                    if not 'doi' in list(rec.keys()) and int(vol) < 167:
                        for strong in child.find_all('strong'):
                            strongt = strong.text.strip()
                            if re.search('efere', strongt):
                                strong.replace_with('REFERENCESSS')
                            elif re.search('bstract', strongt):
                                strong.replace_with('ABSTRACTTT')
                            elif re.search('uthor', strongt):
                                strong.replace_with('AUTHORRR')
                        childt = re.sub('[\n\t\r]', ' ', child.text.strip()).strip()
                        if re.search('REFERENCESSS', childt):
                            rec['refs'] = []
                            references = re.sub('.*REFERENCESSS', '', childt)
                            for ref in re.split(' *; *', references):
                                rec['refs'].append([('x', ref)])
                            childt = re.sub('REFERENCESSS.*', '', childt)
                        if re.search('ABSTRACTTT', childt):
                            rec['abs'] = re.sub('.*ABSTRACTTT', '', childt)
                        for br in child.find_all('br'):
                            br.replace_with('BRBRBR')
                        childt2 = re.sub('[\r\n\t]', ' ', child.text.strip()).strip()
                        authors = re.sub('.*AUTHORRR.*?BRBRBR *(.*?) *BRBRBR.*', r'\1', childt2)
                        authors = re.sub(' et al.', '', authors)
                        for author in re.split(' *; *', authors):
                            rec['autaff'].append([author])
                        recs.append(rec)
                            

i = 0
for rec in recs:
    i += 1
    if not 'doi' in list(rec.keys()):
        ejlmod3.printprogress("-", [[i, len(recs)], ['NODOI']])
        continue
    else:
        ejlmod3.printprogress("-", [[i, len(recs)], [rec['doi']]])
    artlink = 'http://doi.eso.org/' + rec['doi']
    artreq = urllib.request.Request(artlink, headers={'User-Agent' : "Magic Browser"})
    response = urllib.request.urlopen(artreq)
    truelink = response.geturl()
    try:
        artpage = BeautifulSoup(response, features='lxml')
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (artlink))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(truelink), features='lxml')
    for script in artpage.head.find_all('script', attrs = {'type' : 'application/ld+json'}):
        if script.contents:
            scriptt = script.contents[0].strip()
            metadata = json.loads(scriptt)
            if 'description' in list(metadata.keys()):
                rec['abs'] = metadata['description']
            rec['tit'] = metadata['name']
            rec['year'] = str(metadata['datePublished'])
            for author in metadata['author']:
                autaff = [ author['name'] ]
                if 'affiliation' in author:
                    autaff.append(author['affiliation'])
                    rec['autaff'].append(autaff)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
