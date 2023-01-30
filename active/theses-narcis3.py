# -*- coding: utf-8 -*-
#harvest theses from NARCIS
#FS: 2019-09-15

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'NARCIS'
jnlfilename = 'THESES-NARCIS-%s' % (ejlmod3.stampofnow())
bunchlength = 100

boringpublishers = ['Biomedical Signals and Systems; TechMed Centre',
                    'TechMed Centre; Biomedical Signals and Systems',
                    'LOT', 'Building Materials',
                    'International and European Law; RS: FdR Institute MCEL',
                    'RS: GROW - R2 - Basic and Translational Cancer Biology; Precision Medicine',
                    'RS: GSBE other - not theme-related research; Marketing & Supply Chain Management']
boringkeywords = ['Anxiety', 'Aquaculture and Fisheries', 'Aquacultuur en Visserij', 'biomarkers',
                  'Bio Process Engineering', 'Business Management & Organisation', 'Case study',
                  'circulaire economie', 'circular economy', 'Depression', 'duurzaamheid',
                  'Food Process Engineering', 'human rights', 'Immunotherapy', 'Inflammation',
                  'Laboratorium voor Geo-informatiekunde en Remote Sensing',
                  'Laboratory of Geo-information Science and Remote Sensing',
                  'LOT dissertation series', 'mensenrechten', 'Microbiologie', 'Microbiology',
                  'Parenting', 'physical activity', 'Physical therapy', 'refugees', 'room 0.710',
                  'Systeem en Synthetische Biologie', 'Systems and Synthetic Biology',
                  'systems biology', 'Tuberculosis', 'vluchtelingen', 'Water Resources Management',
                  'Baggage Handling Systems', 'Cancer', 'Development Economics',
                  'ERIM PhD Series Research in Management', 'Global Nutrition',
                  'Laboratorium voor Plantenveredeling', 'Ontwikkelingseconomie', 'Plant Breeding',
                  'sustainability', 'Wereldvoeding', 'climate change', 'Kennis',
                  'MPI series in Psycholinguistics', 'SDG 3 - Good Health and Well-being',
                  'Glomerulosclerosis', 'Proteinuria', 'Renal disease']

#check individual pages of bunch of records
def processrecs(recs, bunchcounter):
    i = 0
    recs = []
    for rec in prerecs:
        keepit = True
        uni = 'unknown'
        i += 1
        ejlmod3.printprogress('-', [[bunchcounter], [i, len(prerecs)], [rec['artlink']], [len(recs)]])
        #req = urllib2.Request(rec['artlink'], headers=hdr)    
        #artpage = BeautifulSoup(urllib2.urlopen(req))
        artfilename = '/tmp/THESES-NARCIS_%s' % (re.sub('\W', '', rec['artlink']))
        if not os.path.isfile(artfilename):
            os.system('wget -q -T 300 -O %s "%s"' % (artfilename, rec['artlink']))
            time.sleep(5)
        inf = open(artfilename, 'r')
        artpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
        inf.close()
        ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_dissertation_institution', 'citation_abstract',
                                            'citation_publication_date', 'citation_title', 'citation_language'])
        for table in artpage.find_all('table', attrs = {'class' : 'size02'}):
            for tr in table.find_all('tr'):
                for th in tr.find_all('th'):
                    tht = th.text.strip()
                for td in tr.find_all('td'):
                    tdt = td.text.strip()
                if tht == 'Reference(s)':
                    rec['keyw'] = re.split(', ', tdt)
                    for kw in rec['keyw']:
                        if kw in boringkeywords:
                            print('   skip "%s"' % (kw))
                            keepit = False
                elif tht == 'ISBN':
                    isbns = re.split(' *; *', tdt)
                    rec['isbns'] = [[('a', re.sub('\-', '', isbn))] for isbn in isbns]
                elif re.search('DOI$', tht):
                    rec['doi'] = re.sub('.*doi.org\/', '', tdt)
                elif re.search('Handle$', tht):
                    rec['hdl'] = tdt
                elif re.search('NBN$', tht):
                    rec['urn'] = tdt
                elif tht == 'Persistent Identifier':
                    if tdt[:4] in ['urn', 'URN']:
                       rec['urn'] = tdt
                elif tht == 'Thesis advisor':
                    rec['supervisor'] = [[sv] for sv in re.split('; *', tdt)]
                elif tht == 'Publication':
                    rec['link'] = tdt
                    if not 'hdl' in list(rec.keys()) and not 'doi' in list(rec.keys()):
                        if re.search('\/handle\/\d', rec['link']):
                            rec['hdl'] = re.sub('.*handle\/', '', rec['link'])
                elif tht == 'Publisher':
                    realpublisher = tdt
                    if realpublisher in boringpublishers:
                        print('   skip "%s"' % (realpublisher))
                        keepit = False
                    else:
                        rec['note'].append('publisher:::'+tdt)
        if 'link' in list(rec.keys()):
            print('  try to get PDF from %s' % (rec['link']))
            try:
                req = urllib.request.Request(rec['link'], headers=hdr)
                origpage = BeautifulSoup(urllib.request.urlopen(req))
                ejlmod3.metatagcheck(rec, origpage, ['citation_pdf_url', 'citation_isbn', 'citation_doi'])
            except:
                print('    could not find PDF')
            if not 'FFT' in list(rec.keys()):
                rec['link'] = rec['artlink']
        if not 'doi' in list(rec.keys()) and not 'isbn' in list(rec.keys()) and not 'urn' in list(rec.keys()) and not 'hdl' in list(rec.keys()):
            rec['doi'] = '20.2001/NARCIS/' + re.sub('\W', '', rec['artlink'])
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['artlink'])
    ejlmod3.writenewXML(recs, publisher, '%s_%03i' % (jnlfilename, bunchcounter))
    return

                                            
#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2))]
redoki = re.compile('THESES.NARCIS.*doki$')
rehttp = re.compile('^I\-\-(http.*id).*')
regenre = re.compile('\/genre.*')
nochmal = []
bereitsin = []
for ejldir in ejldirs:
    print(ejldir)
    for datei in os.listdir(ejldir):
        if redoki.search(datei):
            inf = open(os.path.join(ejldir, datei), 'r')
            for line in inf.readlines():
                if len(line) > 1 and line[0] == 'I':
                    if rehttp.search(line):
                        http = regenre.sub('', rehttp.sub(r'\1', line.strip()))
                        if not http in bereitsin:
                            if not http in nochmal:
                                bereitsin.append(http)
                                http2 = re.sub(':', '%3A', http)
                                if http2 != http:
                                    bereitsin.append(http)
            print('  %6i %s' % (len(bereitsin), datei))

hdr = {'User-Agent' : 'Magic Browser'}

#there is not set for doctoral theses on OAI-PMH.
#  tocurl = 'http://oai.tudelft.nl/ir/oai/oai2.php?verb=ListRecords&metadataPrefix=nl_didl&from=' + startdate + '&until=' + stopdate
#would give too many results
prerecs = []
pages = 0
pagestotal = 0
bunchcounter = 0
ntarget = 0
for year in [str(ejlmod3.year()), str(ejlmod3.year(backwards=1))]:
    page = 0
    complete = False
    while not complete:
        tocurl = 'https://www.narcis.nl/search/coll/publication/Language/EN/genre/doctoralthesis/dd_year/' + year + '/pageable/' + str(page)
        ejlmod3.printprogress('=', [[page+1, pages], [len(prerecs), 10*pagestotal, ntarget], [tocurl]])
        try:
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print('wait 5 minutes')
            time.sleep(300)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for h1 in tocpage.body.find_all('h1', attrs = {'class' : 'search-results'}):
            target = re.sub('.*of (\d.*\d).*', r'\1', h1.text.strip())
            ntarget = int(re.sub('\D', '', target))
            pages = (ntarget-1) // 10 + 1
        for div in tocpage.body.find_all('div', attrs = {'class' : 'search-results'}):
            for div2 in div.find_all('div', attrs = {'class' : 'search-options'}):
                div2.replace_with('')
            for li in div.find_all('li'):
                for a in li.find_all('a'):
                    if a.has_attr('href'):
                        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'oa' : False}
                        rec['artlink'] = 'https://www.narcis.nl' + a['href']
                        rec['identifier'] = re.sub('.*ecordID\/', '', rec['artlink'])
                        rec['identifier'] = re.sub('%3A', ':', rec['identifier'])
                        rec['identifier'] = re.sub('%2F', '/', rec['identifier'])
                        rec['identifier'] = regenre.sub('', rec['identifier'])
                        rec['tit'] = re.sub(' \(\d\d\d\d\)$', '', a.text.strip())
                        rec['note'] = [ rec['artlink'], '%i of %i' % (len(prerecs) + 1, ntarget) ]
                        for img  in li.find_all('img', attrs = {'class' : 'open-access-logo'}):
                            rec['oa'] = True
                    ihttp = re.sub('(.*id).*', r'\1', rec['artlink'])
                    if regenre.sub('', ihttp) in bereitsin:
                        #print('   skip %s' % (rec['artlink']))
                        pass
                    elif ejlmod3.checkinterestingDOI(rec['identifier']) and ejlmod3.checkinterestingDOI(rec['artlink']):
                        prerecs.append(rec)
                        bereitsin.append(ihttp)
        time.sleep(10)
        page += 1
        pagestotal += 1
        if len(prerecs) >= ntarget or 10*page >= ntarget:
            complete = True
        if len(prerecs) >= bunchlength:
            processrecs(prerecs, bunchcounter)
            bunchcounter += 1
            prerecs = []
if len(prerecs) < bunchlength:
    processrecs(prerecs, bunchcounter)



        


