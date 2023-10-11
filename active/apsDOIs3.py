# -*- coding: UTF-8 -*-
#program to harvest individual articles from APS
# FS 2012-06-01
# FS 2023-09-22

import os
import ejlmod3
import re
import sys
import unicodedata
import string
import time
 
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup


tmpdir = '/tmp'
def tfstrip(x): return x.strip()


bunchsize = 10
sleeptime = 33

publisher = 'APS'
#jnl = sys.argv[1]
#vol = sys.argv[2]
#issue = sys.argv[3]
#jnlfilename = jnl+vol+'.'+issue


dois = ["10.1103/PRXQuantum.1.010002", "10.1103/PRXQuantum.1.010301", "10.1103/PRXQuantum.1.010302", "10.1103/PRXQuantum.1.010303", "10.1103/PRXQuantum.1.010304", "10.1103/PRXQuantum.1.010305", "10.1103/PRXQuantum.1.010306", "10.1103/PRXQuantum.1.010307", "10.1103/PRXQuantum.1.010308", "10.1103/PRXQuantum.1.010309", "10.1103/PRXQuantum.1.020001", "10.1103/PRXQuantum.1.020101", "10.1103/PRXQuantum.1.020102", "10.1103/PRXQuantum.1.020301", "10.1103/PRXQuantum.1.020302", "10.1103/PRXQuantum.1.020303", "10.1103/PRXQuantum.1.020304", "10.1103/PRXQuantum.1.020305", "10.1103/PRXQuantum.1.020306", "10.1103/PRXQuantum.1.020307", "10.1103/PRXQuantum.1.020308", "10.1103/PRXQuantum.1.020309", "10.1103/PRXQuantum.1.020310", "10.1103/PRXQuantum.1.020311", "10.1103/PRXQuantum.1.020312", "10.1103/PRXQuantum.1.020313", "10.1103/PRXQuantum.1.020314", "10.1103/PRXQuantum.1.020315", "10.1103/PRXQuantum.1.020316", "10.1103/PRXQuantum.1.020317", "10.1103/PRXQuantum.1.020318", "10.1103/PRXQuantum.1.020319", "10.1103/PRXQuantum.1.020320", "10.1103/PRXQuantum.1.020321", "10.1103/PRXQuantum.1.020322", "10.1103/PRXQuantum.1.020323", "10.1103/PRXQuantum.1.020324", "10.1103/PRXQuantum.1.020325", "10.1103/PRXQuantum.2.010001", "10.1103/PRXQuantum.2.010101", "10.1103/PRXQuantum.2.010102", "10.1103/PRXQuantum.2.010103", "10.1103/PRXQuantum.2.010201", "10.1103/PRXQuantum.2.010301", "10.1103/PRXQuantum.2.010302", "10.1103/PRXQuantum.2.010303", "10.1103/PRXQuantum.2.010304", "10.1103/PRXQuantum.2.010305", "10.1103/PRXQuantum.2.010306", "10.1103/PRXQuantum.2.010307", "10.1103/PRXQuantum.2.010308", "10.1103/PRXQuantum.2.010309", "10.1103/PRXQuantum.2.010310", "10.1103/PRXQuantum.2.010311", "10.1103/PRXQuantum.2.010312", "10.1103/PRXQuantum.2.010313", "10.1103/PRXQuantum.2.010314", "10.1103/PRXQuantum.2.010315", "10.1103/PRXQuantum.2.010316", "10.1103/PRXQuantum.2.010317", "10.1103/PRXQuantum.2.010318", "10.1103/PRXQuantum.2.010319", "10.1103/PRXQuantum.2.010320", "10.1103/PRXQuantum.2.010321", "10.1103/PRXQuantum.2.010322", "10.1103/PRXQuantum.2.010323", "10.1103/PRXQuantum.2.010324", "10.1103/PRXQuantum.2.010325", "10.1103/PRXQuantum.2.010326", "10.1103/PRXQuantum.2.010327", "10.1103/PRXQuantum.2.010328", "10.1103/PRXQuantum.2.010329", "10.1103/PRXQuantum.2.010330", "10.1103/PRXQuantum.2.010331", "10.1103/PRXQuantum.2.010332", "10.1103/PRXQuantum.2.010333", "10.1103/PRXQuantum.2.010334", "10.1103/PRXQuantum.2.010335", "10.1103/PRXQuantum.2.010336", "10.1103/PRXQuantum.2.010337", "10.1103/PRXQuantum.2.010338", "10.1103/PRXQuantum.2.010339", "10.1103/PRXQuantum.2.010340", "10.1103/PRXQuantum.2.010341", "10.1103/PRXQuantum.2.010342", "10.1103/PRXQuantum.2.010343", "10.1103/PRXQuantum.2.010344", "10.1103/PRXQuantum.2.010345", "10.1103/PRXQuantum.2.010346", "10.1103/PRXQuantum.2.010347", "10.1103/PRXQuantum.2.010348", "10.1103/PRXQuantum.2.010349", "10.1103/PRXQuantum.2.010350", "10.1103/PRXQuantum.2.010351", "10.1103/PRXQuantum.2.010352", "10.1103/PRXQuantum.2.010353", "10.1103/PRXQuantum.2.017001", "10.1103/PRXQuantum.2.017002", "10.1103/PRXQuantum.2.017003", "10.1103/PRXQuantum.2.020101", "10.1103/PRXQuantum.2.020301", "10.1103/PRXQuantum.2.020302", "10.1103/PRXQuantum.2.020303", "10.1103/PRXQuantum.2.020304", "10.1103/PRXQuantum.2.020305", "10.1103/PRXQuantum.2.020306", "10.1103/PRXQuantum.2.020307", "10.1103/PRXQuantum.2.020308", "10.1103/PRXQuantum.2.020309", "10.1103/PRXQuantum.2.020310", "10.1103/PRXQuantum.2.020311", "10.1103/PRXQuantum.2.020312", "10.1103/PRXQuantum.2.020313", "10.1103/PRXQuantum.2.020314", "10.1103/PRXQuantum.2.020315", "10.1103/PRXQuantum.2.020316", "10.1103/PRXQuantum.2.020317", "10.1103/PRXQuantum.2.020318", "10.1103/PRXQuantum.2.020319", "10.1103/PRXQuantum.2.020320", "10.1103/PRXQuantum.2.020321", "10.1103/PRXQuantum.2.020322", "10.1103/PRXQuantum.2.020323", "10.1103/PRXQuantum.2.020324", "10.1103/PRXQuantum.2.020325", "10.1103/PRXQuantum.2.020326", "10.1103/PRXQuantum.2.020327", "10.1103/PRXQuantum.2.020328", "10.1103/PRXQuantum.2.020329", "10.1103/PRXQuantum.2.020330", "10.1103/PRXQuantum.2.020331", "10.1103/PRXQuantum.2.020332", "10.1103/PRXQuantum.2.020333", "10.1103/PRXQuantum.2.020334", "10.1103/PRXQuantum.2.020335", "10.1103/PRXQuantum.2.020336", "10.1103/PRXQuantum.2.020337", "10.1103/PRXQuantum.2.020338", "10.1103/PRXQuantum.2.020339", "10.1103/PRXQuantum.2.020340", "10.1103/PRXQuantum.2.020341", "10.1103/PRXQuantum.2.020342", "10.1103/PRXQuantum.2.020343", "10.1103/PRXQuantum.2.020344", "10.1103/PRXQuantum.2.020345", "10.1103/PRXQuantum.2.020346", "10.1103/PRXQuantum.2.020347", "10.1103/PRXQuantum.2.020348", "10.1103/PRXQuantum.2.020349", "10.1103/PRXQuantum.2.020350", "10.1103/PRXQuantum.2.030101", "10.1103/PRXQuantum.2.030102", "10.1103/PRXQuantum.2.030201", "10.1103/PRXQuantum.2.030202", "10.1103/PRXQuantum.2.030203", "10.1103/PRXQuantum.2.030204", "10.1103/PRXQuantum.2.030301", "10.1103/PRXQuantum.2.030302", "10.1103/PRXQuantum.2.030303", "10.1103/PRXQuantum.2.030304", "10.1103/PRXQuantum.2.030305", "10.1103/PRXQuantum.2.030306", "10.1103/PRXQuantum.2.030307", "10.1103/PRXQuantum.2.030308", "10.1103/PRXQuantum.2.030309", "10.1103/PRXQuantum.2.030310", "10.1103/PRXQuantum.2.030311", "10.1103/PRXQuantum.2.030312", "10.1103/PRXQuantum.2.030313", "10.1103/PRXQuantum.2.030314", "10.1103/PRXQuantum.2.030315", "10.1103/PRXQuantum.2.030316", "10.1103/PRXQuantum.2.030317", "10.1103/PRXQuantum.2.030318", "10.1103/PRXQuantum.2.030319", "10.1103/PRXQuantum.2.030320", "10.1103/PRXQuantum.2.030321", "10.1103/PRXQuantum.2.030322", "10.1103/PRXQuantum.2.030323", "10.1103/PRXQuantum.2.030324", "10.1103/PRXQuantum.2.030325", "10.1103/PRXQuantum.2.030326", "10.1103/PRXQuantum.2.030327", "10.1103/PRXQuantum.2.030328", "10.1103/PRXQuantum.2.030329", "10.1103/PRXQuantum.2.030330", "10.1103/PRXQuantum.2.030331", "10.1103/PRXQuantum.2.030332", "10.1103/PRXQuantum.2.030333", "10.1103/PRXQuantum.2.030334", "10.1103/PRXQuantum.2.030335", "10.1103/PRXQuantum.2.030336", "10.1103/PRXQuantum.2.030337", "10.1103/PRXQuantum.2.030338", "10.1103/PRXQuantum.2.030339", "10.1103/PRXQuantum.2.030340", "10.1103/PRXQuantum.2.030341", "10.1103/PRXQuantum.2.030342", "10.1103/PRXQuantum.2.030343", "10.1103/PRXQuantum.2.030344", "10.1103/PRXQuantum.2.030345", "10.1103/PRXQuantum.2.030346", "10.1103/PRXQuantum.2.030347", "10.1103/PRXQuantum.2.030348", "10.1103/PRXQuantum.2.030349", "10.1103/PRXQuantum.2.030350", "10.1103/PRXQuantum.2.030351", "10.1103/PRXQuantum.2.030352", "10.1103/PRXQuantum.2.030353", "10.1103/PRXQuantum.2.040101", "10.1103/PRXQuantum.2.040201", "10.1103/PRXQuantum.2.040202", "10.1103/PRXQuantum.2.040203", "10.1103/PRXQuantum.2.040204", "10.1103/PRXQuantum.2.040301", "10.1103/PRXQuantum.2.040302", "10.1103/PRXQuantum.2.040303", "10.1103/PRXQuantum.2.040304", "10.1103/PRXQuantum.2.040305", "10.1103/PRXQuantum.2.040306", "10.1103/PRXQuantum.2.040307", "10.1103/PRXQuantum.2.040308", "10.1103/PRXQuantum.2.040309", "10.1103/PRXQuantum.2.040310", "10.1103/PRXQuantum.2.040311", "10.1103/PRXQuantum.2.040312", "10.1103/PRXQuantum.2.040313", "10.1103/PRXQuantum.2.040314", "10.1103/PRXQuantum.2.040315", "10.1103/PRXQuantum.2.040316", "10.1103/PRXQuantum.2.040317", "10.1103/PRXQuantum.2.040318", "10.1103/PRXQuantum.2.040319", "10.1103/PRXQuantum.2.040320", "10.1103/PRXQuantum.2.040321", "10.1103/PRXQuantum.2.040322", "10.1103/PRXQuantum.2.040323", "10.1103/PRXQuantum.2.040324", "10.1103/PRXQuantum.2.040325", "10.1103/PRXQuantum.2.040326", "10.1103/PRXQuantum.2.040327", "10.1103/PRXQuantum.2.040328", "10.1103/PRXQuantum.2.040329", "10.1103/PRXQuantum.2.040330", "10.1103/PRXQuantum.2.040331", "10.1103/PRXQuantum.2.040332", "10.1103/PRXQuantum.2.040333", "10.1103/PRXQuantum.2.040334", "10.1103/PRXQuantum.2.040335", "10.1103/PRXQuantum.2.040336", "10.1103/PRXQuantum.2.040337", "10.1103/PRXQuantum.2.040338", "10.1103/PRXQuantum.2.040339", "10.1103/PRXQuantum.2.040340", "10.1103/PRXQuantum.2.040341", "10.1103/PRXQuantum.2.040342", "10.1103/PRXQuantum.2.040343", "10.1103/PRXQuantum.2.040344", "10.1103/PRXQuantum.2.040345", "10.1103/PRXQuantum.2.040346", "10.1103/PRXQuantum.2.040347", "10.1103/PRXQuantum.2.040348", "10.1103/PRXQuantum.2.040349", "10.1103/PRXQuantum.2.040350", "10.1103/PRXQuantum.2.040351", "10.1103/PRXQuantum.2.040352", "10.1103/PRXQuantum.2.040353", "10.1103/PRXQuantum.2.040354", "10.1103/PRXQuantum.2.040355", "10.1103/PRXQuantum.2.040356", "10.1103/PRXQuantum.2.040357", "10.1103/PRXQuantum.2.040358", "10.1103/PRXQuantum.2.040359", "10.1103/PRXQuantum.2.040360", "10.1103/PRXQuantum.2.040361", "10.1103/PRXQuantum.2.040362"]

jnlfilename = 'APS_QIS_retro.' + ejlmod3.stampoftoday()


recnr = 0
subject = ''
recs = []
for doi in dois:
    ejlmod3.printprogress('-', [[recnr+1, len(dois)], [doi]])
    if re.search('PhysRev[A-Z].\d', doi):
        letter = doi[15].lower()
        artlink = 'https://journals.aps.org/pr%s/abstract/%s' % (letter, doi)
    elif re.search('PhysRevLett', doi):
        artlink = 'https://journals.aps.org/prl/abstract/' + doi
    elif re.search('PhysRevAccelBeams', doi):
        artlink = 'https://journals.aps.org/prab/abstract/' + doi
    elif re.search('PRXQuantum', doi):
        artlink = 'https://journals.aps.org/prxquantum/abstract/' + doi
    elif re.search('RevModPhys', doi):
        artlink = 'https://journals.aps.org/rmp/abstract/' + doi
    elif re.search('PhysRevResearch', doi):
        artlink = 'https://journals.aps.org/prresearch/abstract/' + doi
    else:
        print('??? can can create article link for', doi)
        continue
    print(' -', artlink)
    try:
        page = BeautifulSoup(urllib.request.urlopen(artlink), features='lxml')
    except:
        try:
            print(' - sleep 5minutes')
            time.sleep(300)
            page = BeautifulSoup(urllib.request.urlopen(artlink), features='lxml')
        except:
            print(' - probleme')
            continue
    rec = {'doi' : doi, 'autaff' : [], 'tc' : 'P'}
    ejlmod3.metatagcheck(rec, page, ['citation_title', 'citation_date', 'citation_volume',
                                     'citation_issue', 'citation_firstpage', 'citation_author',
                                     'citation_author_institution', 'description'])
    for meta in page.head.find_all('meta'):
        if 'name' in meta.attrs:
            if meta['name'] == 'citation_journal_abbrev':
                rec['jnl'] = re.sub(' +', '', meta['content'])
            elif meta['name'] == 'citation_journal_title':
                if meta['content'] == 'PRXQuantum':
                    rec['jnl'] = 'PRX Quantum'
                else:
                    rec['jnl'] = meta['content']
    ejlmod3.globallicensesearch(rec, page)
    time.sleep(10)
    reflink = re.sub('abstract', 'references', artlink)
    refpage = BeautifulSoup(urllib.request.urlopen(reflink), features='lxml')
    for ol in refpage.find_all('ol', attrs = {'class' : 'references'}):
        rec['refs'] = []
        for li in ol.find_all('li'):
            rdoi = False
            for a in li.find_all('a'):
                if a.has_attr('href'):
                    link = a['href']
                    if re.search('doi.org.10', link):
                        rdoi = re.sub('.*?(10\.\d+\/.*)', r'\1', link)
            ref = li.text 
            if rdoi:
                ref = re.sub('\. *$', '', ref)
                ref += ', DOI: %s.' % (rdoi)
            rec['refs'].append([('x', ref)])
    if 'tit' in rec:
        recnr += 1
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
            
    print('\n-------------------------\n--- sleep %3i seconds ---\n-------------------------\n' % (sleeptime))
    time.sleep(sleeptime)


