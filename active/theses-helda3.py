# -*- coding: utf-8 -*-
#harvest theses from HELDA
#FS: 2019-10-25

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os


publisher = 'Helsinki U.'
jnlfilename = 'THESES-HELSINKI-%s' % (ejlmod3.stampoftoday())
rpp = 50
numofpages = 3
skipalreadyharvested = True

boring = ['116 Chemical sciences', '116 Kemia', '116 Kemi', '1171 Geosciences',
          '1171 Geotieteet', '1171 Geovetenskaper', '1172 Environmental sciences',
          '1172 Miljövetenskap', '1172 Ympäristötiede',
          '1181 Ecology, evolutionary biology', '1181 Ekologia, evoluutiobiologia',
          '1181 Ekologi, evolutionsbiologi', '1182 Biochemistry, cell and molecular biology',
          '1182 Biokemia, solu- ja molekyylibiologia', '1182 Biokemi, cell- och molekylärbiologi',
          '11832 Microbiology and virology', '11832 Mikrobiologia ja virologia',
          '11832 Mikrobiologi och virologi', '1184 Genetics, developmental biology, physiology',
          '1184 Genetiikka, kehitysbiologia, fysiologia',
          '1184 Genetik, utvecklingsbiologi, fysiologi', '215 Chemical engineering',
          '215 Teknillinen kemia, kemian prosessitekniikka', '215 Teknisk kemi, kemisk processteknik',
          '217 Lääketieteen tekniikka', '217 Medical engineering', '217 Medicinsk teknik',
          '218 Environmental engineering', '218 Miljöteknik', '218 Ympäristötekniikka',
          '219 Environmental biotechnology', '219 Miljöbioteknologi', '219 Ympäristön bioteknologia',
          '3122 Cancersjukdomar', '3122 Cancers', '3122 Syöpätaudit', '313 Dentistry',
          '313 Hammaslääketieteet', '313 Odontologi', '3142 Folkhälsovetenskap, miljö och arbetshälsa',
          '3142 Kansanterveystiede, ympäristö ja työterveys',
          '3142 Public health care science, environmental and occupational health',
          '318 Lääketieteen bioteknologia', '318 Medical biotechnology', '318 Medicinsk bioteknologi',
          '4112 Forestry', '4112 Metsätiede', '4112 Skogsvetenskap', '516 Educational sciences',
          '516 Kasvatustieteet', '516 Pedagogik', '5171 Political Science', '5171 Statslära',
          '5171 Valtio-oppi', '519 Social and economic geography',
          '519 Socialgeografi och ekonomisk geografi', '519 Yhteiskuntamaantiede, talousmaantiede',
          '5200 Muut yhteiskuntatieteet', '5200 Other social sciences',
          '5200 Övriga samhällsvetenskaper']

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s  %s/%i/*%s| grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc, dokidir, ejlmod3.year(backwards=2), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for i in range(numofpages):
    tocurl = 'https://helda.helsinki.fi/handle/10138/18070/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (rpp, i*rpp)
    ejlmod3.printprogress('=', [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    oldones = []
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://helda.helsinki.fi'):
        if rec['hdl'] in alreadyharvested:
            oldones.append(rec['hdl'])
        else:
            prerecs.append(rec)
    if oldones:
        print('  %4i already in backup (%s)' % (len(oldones), ', '.join(oldones)))
    print('  %4i records so far' % (len(prerecs)))
        
recs = []
for (j, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[j, len(prerecs)], [rec['link']], [len(recs)]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_author', 'DC.rights',
                                        'citation_language', 'citation_pdf_url',
                                        'DC.identifier', 'DC.type'])
    rec['autaff'][-1].append(publisher)                        
    #abstract
    for meta in artpage.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if meta.has_attr('xml:lang') and meta['xml:lang'] in ['eng', 'en_US']:
            rec['abs'] = meta['content']
    #repair URN
    if 'urn' in rec:
        rec['urn'] = re.sub('–', '-', rec['urn'])
    #subject
    for note in rec['note']:
        if note in ['111 Matematiikka', '111 Matematik', '111 Mathematics']:
            rec['fc'] = 'm'
        elif note in ['113 Computer and information sciences', '113 Data- och informationsvetenskap',
                      '113 Tietojenkäsittely- ja informaatiotieteet']:
            rec['fc'] = 'c'
        elif note in ['115 Astronomy, Space science', '115 Avaruustieteet ja tähtitiede',
                      '115 Rymdvetenskap och astronomi']:
            rec['fc'] = 'a'
        elif note in ['112 Statistics and probability', '112 Statistik', '112 Tilastotiede']:
            rec['fc'] = 's'
        elif note in boring:
            keepit = False    
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)


