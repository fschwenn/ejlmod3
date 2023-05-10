# -*- coding: UTF-8 -*-
#program to translate crossref-xmls
# FS 2015-12-03
# FS 2023-01-13

import sys
import ejlmod3
import re
import os
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse

infilename = sys.argv[1]
tmpdir = '/afs/desy.de/user/l/library/tmp'

inf = open(infilename, mode='r')
crossref = BeautifulSoup(''.join(inf.readlines()), features="lxml")
inf.close()
hdr = {'User-Agent' : 'Magic Browser'}

jnlfilename =  re.sub('.*\/', '', infilename)
jnlfilename =  re.sub('.xml', '', jnlfilename)

for registrant in crossref.body.find_all('registrant'):
    publisher = registrant.text

recs = []
for journal in crossref.body.find_all('journal'):
    #metadata of this issue/ volume
    for journalmetadata in journal.find_all('journal_metadata'):
        for full_title in journalmetadata.find_all('full_title'):
            jtit = full_title.text                
    (jvol, jiss, jdate, m, d, y) = (False, False, False, False, False, False)
    for journalissue in journal.find_all('journal_issue'):
        for issue in journalissue.find_all('issue'):
            jiss = issue.text
        for month in journalissue.find_all('month'): m = int(month.text)
        for day  in journalissue.find_all('day'): d = int(day.text)
        for year in journalissue.find_all('year'): y = year.text
        if y:
            if m:
                if d:
                    jdate = '%4s-%02i-%02i' % (y, m, d)
                else:
                    jdate = '%4s-%02i' % (y, m)
            else:
                jdate = y                    
    for journal_volume in journal.find_all('journal_volume'):
        for volume in journal.find_all('volume'):
            jvol = volume.text
    #metadata of article
    for journal_article in journal.find_all('journal_article'):
        rec = {'tc' : 'P', 'refs' : []}
        #DOI
        for doi_data in journal_article.find_all('doi_data'):
            for doi in doi_data.find_all('doi'):
                rec['doi'] = doi.text
            if jtit in ['Acta Physica Polonica A']:
                for resource in doi_data.find_all('resource'):
                    rec['FFT'] = resource.text
        #pbn
        if jtit in ['Acta Physica Polonica B', 'Acta Physica Polonica B Proceedings Supplement']:
            for doi_data in journal_article.find_all('doi_data'):
                for resource in doi_data.find_all('resource'):
                    rec['aid'] = re.sub('.*=', '', resource.text)
                    rec['p1'] = re.sub('.*A', '', resource.text)
                    for last_page in journal_article.find_all('last_page'):
                        rec['pages'] = last_page.text
        else:
            for first_page in journal_article.find_all('first_page'):
                rec['p1'] = first_page.text
            for last_page in journal_article.find_all('last_page'):
                rec['p2'] = last_page.text
        if jvol: rec['vol'] = jvol
        if jiss: rec['issue'] = jiss
        if jdate: rec['date'] = jdate
        if jtit == 'Acta Physica Polonica A':
            rec['jnl'] = 'Acta Phys.Polon.A'
            #rec['vol'] = 'A' + rec['vol']
        elif jtit == 'Acta Physica Polonica B':
            rec['jnl'] = 'Acta Phys.Polon.B'
            rec['licence'] = {'statement' : 'CC-BY-4.0'}
            rec['FFT'] = 'https://www.actaphys.uj.edu.pl/R/%s/%s/%s/pdf' % (rec['vol'], rec['issue'], rec['p1'])
            rec['FFT'] = 'https://www.actaphys.uj.edu.pl/fulltext?series=Reg&vol=%s&aid=%s' % (rec['vol'], rec['aid'])
            #rec['vol'] = 'B' + rec['vol']
            if  rec['vol'] == '52' and rec['issue'] == '8':
                rec['cnum'] = 'C21-01-07'
                rec['tc'] = 'C'
        elif jtit == 'Acta Physica Polonica B Proceedings Supplement':
            rec['jnl'] = 'Acta Phys.Polon.Supp.'
            rec['licence'] = {'statement' : 'CC-BY-4.0'}
            rec['FFT'] = 'https://www.actaphys.uj.edu.pl/S/%s/%s/%s/pdf' % (rec['vol'], rec['issue'], rec['p1'])
            rec['FFT'] = 'https://www.actaphys.uj.edu.pl/fulltext?series=Sup&vol=%s&aid=%s-%s' % (rec['vol'], rec['issue'], rec['p1orig'])
            if  rec['vol'] == '15' and rec['issue'] == '1':
                rec['cnum'] = 'C21-09-20.10'
                rec['FFT'] = 'https://www.actaphys.uj.edu.pl/S/%s/%s/pdf' % (rec['vol'], re.sub('.*\.', '', rec['doi']))
            elif  rec['vol'] == '15' and rec['issue'] == '2':
                rec['cnum'] = 'C21-09-15.3'
                rec['FFT'] = 'https://www.actaphys.uj.edu.pl/S/%s/%s/pdf' % (rec['vol'], re.sub('.*\.', '', rec['doi']))
            rec['tc'] = 'C'
        else:
            rec['jnl'] = jtit
        for publication_date in journal_article.find_all('publication_date', attr = {'media_type' : 'print'}):
            for year in publication_date.find_all('year'):
                rec['year'] = year.text
        #title
        for titles in journal_article.find_all('titles'):
            for title in titles.find_all('title'): rec['tit'] = title.text
        #authors
        for contributors in journal_article.find_all('contributors'):
            rec['autaff'] = []
            for person_name in contributors.find_all('person_name'):
                author = ''
                for surname in person_name.find_all('surname'): 
                    author = surname.text
                for given_name in person_name.find_all('given_name'):
                    author += ', %s' % (given_name.text)
                if person_name.has_attr('contributor_role') and person_name['contributor_role'] == 'editor':
                    author += ' (Ed.)'
                autaff = [author]
                for affiliation in person_name.find_all('affiliation'):
                    autaff.append(affiliation.text)
                rec['autaff'].append(autaff)                
        #references
        for citation_list in journal_article.find_all('citation_list'):
            for citation in citation_list.find_all('citation'):
                ref = ''
                for unstructured_citation in citation.find_all('unstructured_citation'):
                    ref += unstructured_citation.text
                for doi in citation.find_all('doi'):
                    ref += ', DOI: %s' % (doi.text)
                rec['refs'].append([('x', ref)])
        #abstract
        abspage = False
        absdict = False
        keywdict = False
        if jtit == 'Acta Physica Polonica A':
            abspage = 'http://przyrbwn.icm.edu.pl/APP/SPIS/a%s-%s.html' % (rec['vol'], rec['issue'])
        elif jtit == 'Acta Physica Polonica B':
            abspage = 'https://www.actaphys.uj.edu.pl/index_n.php?I=R&V=%s&N=%s' % (rec['vol'], rec['issue'])
        elif jtit == 'Acta Physica Polonica B Proceedings Supplement':
            abspage = 'https://www.actaphys.uj.edu.pl/index_n.php?I=S&V=%s&N=%s' % (rec['vol'], rec['issue'])
        if abspage:
            absfile = os.path.join(tmpdir, re.sub('\W', '', abspage))
            if not os.path.isfile(absfile):
                os.system('wget -q -O %s "%s"' % (absfile, abspage))
            if not absdict:
                inf = open(absfile, 'r')
                abssoup = BeautifulSoup(''.join(inf.readlines()), features="lxml")
                inf.close()
                absdict = {}
                keywdict = {}
                if jtit == 'Acta Physica Polonica A':
                    for a in abssoup.find_all('a'):
                        if a.text.strip() == 'abstract':
                            req = urllib.request.Request(re.sub('^..', 'http://przyrbwn.icm.edu.pl/APP', a['href']), headers=hdr)
                            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
                            text = re.sub('[\n\t\r]', '   ', artpage.text.strip())
                            adoi = re.sub('.*DOI:(10.12693.*?) .*', r'\1', text)
                            abstract = re.sub('.*Full Text PDF *(.*?) *DOI:10.12693.*', r'\1', text)
                            absdict[adoi] = abstract
                            if re.search('topics:', text):
                                keywdict[adoi] = re.split(', ', re.sub('.*topics: *', '', text))                            
                else:    
                    for div in abssoup.find_all('div', attrs = {'class' : 'art'}):
                        for p in div.find_all('p'):
                            if p.text.strip() == 'abstract':
                                p.decompose()
                            elif re.search('doi.org\/10.5506', p.text):
                                adoi = re.sub('.*org\/', '', p.text.strip())
                        for div2 in div.find_all('div', attrs = {'class' : 'abstract'}):
                            absdict[adoi] = div2.text.strip()
            if rec['doi'] in absdict:
                rec['abs'] = absdict[rec['doi']]
            if keywdict and rec['doi'] in keywdict:
                rec['abs'] = keywdict[rec['doi']]
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
