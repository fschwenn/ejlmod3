# -*- coding: UTF-8 -*-
#program to digest feeds from Wiley-journals
# FS 2022-09-16

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import datetime

publisher = 'WILEY'

wileydirtmp = '/afs/desy.de/group/library/publisherdata/wiley/tmp'
wileydirraw = '/afs/desy.de/group/library/publisherdata/wiley/raw'
wileydirdone = '/afs/desy.de/group/library/publisherdata/wiley/done'
now = datetime.datetime.now()
stampoftoday = '%4d-%02d-%02d-%02d-%02d' % (now.year, now.month, now.day, now.hour, now.minute)

#harvested vi desydoc
jnldict = {'annphys' : [['1521-3889'], '10.1002/andp', 'Annalen Phys.'],
           'fortp' : [['1521-3978'], '10.1002/prop', 'Fortsch.Phys.'],
           'cpama' : [['1097-0312'], '10.1002/cpa', 'Commun.Pure Appl.Math.'  ],
           'mdpc' : [['2577-6576'], '10.1002/mdp2', 'Mater.Des.Proc.Comm.'],
           'anyaa' : [['1749-6643', '1749-6632'], '10.1111/nyas', 'Annals N.Y.Acad.Sci.'],
           'ctpp' : [['1521-3986'], '10.1002/ctpp', 'Contrib.Plasma Phys.'],
           'mma' : [['1099-1476'], '10.1002/mma', 'Math.Methods Appl.Sci.'],
           'jamma' : [['1521-4001'], '10.1002/zamm', 'J.Appl.Math.Mech.'],
           'puz' : [['1521-3943'], '10.1002/piuz', 'Phys.Unserer Zeit'],
           'mnraa' : [['1356-2966'], '10.1111/mnr', 'Mon.Not Roy.Astron.Soc.'],
           'mnraal' : [['1745-3933'], '10.1002/mnl', 'Mon.Not.Roy.Astron.Soc.'],
           'asnaa' : [['1521-3994'], '10.1002/asna', 'Astron.Nachr.'],
           'mtk' : [['2041-7942'], '10.1112/mtk.', 'Mathematika'],
           'aqt' : [['2511-9044'], '10.1002/qute.', 'Adv.Quantum Technol.'],
           'quanteng' : [['2577-0470'], '10.1002/que', 'Quantum Eng.'],
           'mana' : [['1522-2616'], '10.1002/mana', 'Math.Nachr.'],
           'pssa' : [['1862-6319'], '10.1002/pssa', 'Phys.Status Solidi'],
           'pssr' : [['1862-6270'], '10.1002/pssr', 'Phys.Status Solidi RRL'],
           'qua' : [['1097-461x'], '10.1002/qua', 'Int.J.Quant.Chem.'],
           'pssb' : [['1521-3951'], '10.1002/pssb', 'Phys.Status Solidi B'],
           'adma' : [['1521-4095'], '10.1002/adma', 'Adv.Mater.'],
           'xrs' : [['1097-4539'], '10.1002/', 'X Ray Spectrom.'],
           'qj' : [['1477-870X'], '10.1002/qj', 'Q.J.R.Meteorol.Soc.'],
           'mop' : [['1098-2760'], '10.1002/mop', 'Microw.Opt.Technol.Lett.']}
issntojnl = {}
for j in jnldict:
    for issn in jnldict[j][0]:
        issntojnl[issn] = j
recs = {}


#translate Wiley-article to INSPIRE xml
def digestxml(soup):
    global recs
    rec = {'tc' : 'P', 'note' : [], 'auts' : [], 'aff' : [], 'keyw' : []}
    rec['jnlfilename'] = 'wiley-%s-' % (stampoftoday)
    for pm in soup.find_all('publicationmeta', attrs = {'level' : 'product'}):
        #journal name
        for issn in pm.find_all('issn'):
            if issn.text in issntojnl:
                jnl = issntojnl[issn.text]
                rec['jnl'] = jnldict[jnl][2]
                rec['jnlfilename'] += jnl
    for pm in soup.find_all('publicationmeta', attrs = {'level' : 'part'}):
        #volume
        for num in pm.find_all('numbering', attrs = {'type' : 'journalVolume'}):
            rec['vol'] = num.text
            rec['jnlfilename'] += rec['vol']
        #issue
        for num in pm.find_all('numbering', attrs = {'type' : 'journalIssue'}):
            rec['issue'] = num.text
            rec['jnlfilename'] += '.' + rec['issue']
        #year
        for cd in pm.find_all('coverdate'):
            if re.search('[12]\d\d\d', cd.text):
                rec['year'] = re.sub('.*?([12]\d\d\d).*', r'\1', cd.text)
    for pm in soup.find_all('publicationmeta', attrs = {'level' : 'unit'}):
        if pm.has_attr('type'):
            if pm['type'] in ['cover', 'editorial', 'frontmatter', 'backmatter']:
                return
            elif pm['type'] in ['reviewArticle']:
                rec['tc'] = 'RP'
            elif not pm['type'] in ['article']:
                rec['note'].append(pm['type'])
        #DOI
        for doi in pm.find_all('doi'):
            rec['doi'] = doi.text
        #pages
        for ng in pm.find_all('numberinggroup'):
            for num in ng.find_all('numbering', attrs = {'type' : 'pageFirst'}):
                p1 = num.text
                if p1 != 'n/a':
                    rec['p1'] = p1
            for num in ng.find_all('numbering', attrs = {'type' : 'pageLast'}):
                p2 = num.text
                if p2 != 'n/a':
                    rec['p2'] = p2
        if not 'p1' in rec:
            for artid in pm.find_all('id', attrs = {'type' : 'eLocator'}):
                rec['p1'] = artid['value']
        #date
        for ev in pm.find_all('event', attrs = {'type' : 'publishedOnlineEarlyUnpaginated'}):
            rec['date'] = ev['date']
        if not 'date' in rec:
            for ev in pm.find_all('event', attrs = {'type' : 'publishedOnlineFinalForm'}):
                rec['date'] = ev['date']
        #title
        for tit in pm.find_all('articletitle'):
            rec['tit'] = tit.text
    for cm in soup.find_all('contentmeta'):
        #authors
        for creator in cm.find_all('creator', attrs = {'creatorrole' : 'author'}):
            #print (creator)
            for fn in creator.find_all('familyname'):
                name = fn.text
            for gn in creator.find_all('givennames'):
                name += ', ' + gn.text
            for orcid in creator.find_all('id', attrs = {'type' : 'orcid'}):
                name += re.sub('.*org\/', ', ORCID:', orcid['value'])
            rec['auts'].append(name)
            if creator.has_attr('affiliationref'):
                for aff in re.split(' ', creator['affiliationref']):
                    rec['auts'].append('=Aff' + aff[1:])
        #affiliations
        for aff in cm.find_all('affiliation'):
            affnr = aff['xml:id']
            affname = ''
            for affpart in ['orgdiv', 'orgname', 'street']:
                for ap in aff.find_all(affpart):
                    affname += ap.text + ', '
            for ap in aff.find_all('postcode'):
                affname += ap.text + ' '
            for affpart in ['city', 'countrypart', 'country']:
                for ap in aff.find_all(affpart):
                    affname += ap.text + ', '
            rec['aff'].append('Aff%s= %s' % (affnr, re.sub(', $', '', affname)))
        #keywords
        for keyword in cm.find_all('keyword'):
            rec['keyw'].append(keyword.text)
        #abstract
        for abstract in cm.find_all('abstract', attrs = {'type' : 'main'}):
            for title in abstract.find_all('title'):
                title.decompose()
            rec['abs'] = abstract.text
    #references
    for bibliography in soup.find_all('bibliography'):
        rec['refs'] = []
        for bib in bibliography.find_all('bib'):
            rec['refs'].append([('x', bib.text)])
    ejlmod3.printrecsummary(rec)
    if rec['jnlfilename'] in recs:
        recs[rec['jnlfilename']].append(rec)
    else:
        recs[rec['jnlfilename']] = [rec]
    return
            
            
                

        

#check for new feeds
todo = []
done = os.listdir(wileydirdone)
#
#
# GET THE FEEDS
#
#

todo = ['00033804_2022_534_1.zip', '00033804_2022_534_2.zip', '00033804_2022_534_3.zip']

print('%i packages to do: %s' % (len(todo), ', '.join(todo)))
if not todo:
    sys.exit(0)
if not os.path.isdir(wileydirtmp):
    os.system('mkdir %s' % (wileydirtmp))

#extract the feeds:
for datei in todo:
    print('extracting %s' % (os.path.join(wileydirraw, datei)))
    os.system('cd %s && unzip -q -d %s -o %s' % (wileydirraw, wileydirtmp, datei))


#scan extracted directories
artdirs = os.listdir(wileydirtmp)
for (i, artdir) in enumerate(artdirs):
    ejlmod3.printprogress('-', [[i+1, len(artdirs)], [artdir]])
    if os.path.isdir(os.path.join(wileydirtmp, artdir)):
        for artfile in os.listdir(os.path.join(wileydirtmp, artdir)):
            if re.search('xml$', artfile):
                inf = open(os.path.join(wileydirtmp, artdir, artfile), 'r')
                article = BeautifulSoup(''.join(inf.readlines()), features="lxml")
                inf.close()
                digestxml(article)
                #print([(k, len(recs[k])) for k in recs])

for jnlfilename in recs:
    ejlmod3.writenewXML(recs[jnlfilename], publisher, jnlfilename, retfilename='retfiles_special')
