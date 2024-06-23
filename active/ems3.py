# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest EMS journals
# JH 2022-31-07

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
from sys import argv
import os
import ejlmod3
import re
import json

publisher = 'European Mathematical Society'
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year()),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2))]

years = 2
jnls = ['qt', 'jems', 'jncg', 'aihpd', 'aihpc', 'rmi', 'pm', 'cmh', 'rsmup']

done = []
reems = re.compile('.*ems_(\d+)_[a-z]+\d.*.doki')
for ejldir in ejldirs:
    for datei in os.listdir(ejldir):
        if reems.search(datei):
            done.append(reems.sub(r'\1', datei))
print('%i EMS dokis in backup' % (len(done)))



def get_sub_site(sess, url, jnl, jnlname, tc):
    rec = {'autaff': [], 'jnl': jnlname, 'tc': tc, 'fc' : 'm'}

    inner_resp = sess.get(url)
    if inner_resp.status_code != 200:
        return
    artpage = BeautifulSoup(inner_resp.content.decode('utf8'), 'lxml')
    # license
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_publication_date', 'citation_doi', 'citation_volume', 'citation_issue', 'citation_firstpage', 'citation_lastpage', 'citation_pdf_url', 'description'])
    else:
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_publication_date', 'citation_doi', 'citation_volume', 'citation_issue', 'citation_firstpage', 'citation_lastpage', 'description'])


    #read JSON information
    for script in artpage.find_all('script'):
        st = script.text.strip()
        if re.search('^self.__next_f.*articleId', st):
            stjson = json.loads(re.sub('\\\\', '', re.sub('.*?articleId.*?(\{.*\}).*', r'\1', st)))
            try:
                stdict = stjson['children']['description'][3]['article']['data']
                #print('     ', stdict.keys())
                #DOI
                if 'doi' in stdict:
                    rec['doi'] = stdict['doi']
                #keywords
                if 'keywords' in stdict:
                    rec['keyw'] = stdict['keywords']
                #pages
                if 'pageEnd' in stdict:
                    rec['p2'] = str(stdict['pageEnd'])
                if 'pageStart' in stdict:
                    rec['p1'] = str(stdict['pageStart'])
                #date
                if 'publishedAt' in stdict:
                    rec['date'] = stdict['publishedAt'][:10]
                #title
                if 'title' in stdict:
                    rec['tit'] = stdict['title']
                #abstract
                if 'abstractMarkdownTex' in stdict:
                    rec['abs'] = stdict['abstractMarkdownTex']
                #license
                if 'licenseUrl' in stdict:
                    rec['license'] = {'url' : stdict['licenseUrl']}
                #authors
                if 'personGroups' in stdict:
                    for person in stdict['personGroups']['data'][0]['members']['data']:
                        rec['autaff'].append([person['name']])
                        if 'organization' in person:
                            rec['autaff'][-1].append(person['organization'])
                #volume, issue
                if 'serialIssue' in stdict:
                    if 'volume' in stdict['serialIssue']['data']:
                        rec['vol'] =  str(stdict['serialIssue']['data']['volume'])
                    if 'issue' in stdict['serialIssue']['data']:
                        rec['issue'] =  str(stdict['serialIssue']['data']['issue'])
                #fulltext
                if 'serialArticleFiles':
                    if 'url' in stdict['serialArticleFiles']['data'][0]:
                        rec['pdf_url'] = stdict['serialArticleFiles']['data'][0]['url']
                        #rec['pdf_url'] = 'https://ems.press/journals/' + jnl + '/articles/' + stdict['serialArticleFiles']['data'][0]['id']
            except:
                pass
                
                    
                
        
    #title
    #for h1 in artpage.find_all('h1'):
    #    rec['tit'] = h1.text.strip()
    # Get the abstract
    if not 'abs' in rec or len(rec['abs']) < 10:
        abstract_section = artpage.find_all('div', attrs={'class': 'formatted-text'})
        if len(abstract_section) == 1:
            abstract = abstract_section[0].find_all('p')
            if len(abstract) == 1:
                rec['abs'] = abstract[0].text

    #affiliations
    #for div in artpage.find_all('div', attrs={'role' : 'group'}):
    #    lis = div.find_all('li', attrs={'class' : 'list-item'})
    #    if len(lis):
    #        rec['autaff'] = []
    #        for li in lis:
    #            for h3 in li.find_all('h3'):
    #                rec['autaff'].append([h3.text])
    #            for span in li.find_all('span'):
    #                rec['autaff'][-1].append(span.text)

    ejlmod3.printrecsummary(rec)
    return rec

#def get_issue(jnl, vol, issue):
def get_issue(session, jnl, issnr):
    recs = []
    tc = 'P'
    issn = ''
    if jnl == 'jncg':
        issn = '1661-6952'
        journal_name = 'J.Noncommut.Geom.'
    elif jnl == 'aihpd':
        issn = '2308-5827'
        journal_name = 'Ann.Inst.H.Poincare D Comb.Phys.Interact.'
    elif jnl == 'aihpc':
        issn = '0294-1449'
        journal_name = 'Ann.Inst.H.Poincare C Anal.Non Lineaire'
    elif jnl == 'jems':
        issn = '1435-9855'
        journal_name = 'J.Eur.Math.Soc.'
    elif jnl == 'qt':
        issn = '1663-487X'
        journal_name = 'Quantum Topol.'
    elif jnl == 'rmi':
        issn = '0213-2230'
        journal_name = 'Rev.Mat.Iberoam.'
    elif jnl == 'pm':
        issn = '0032-5155'
        journal_name = 'Portug.Math.'
    elif jnl == 'cmh':
        issn = '0010-2571'
        journal_name = 'Comment.Math.Helv.'
    elif jnl == 'rsmup':
        issn = '0041-8994'
        journal_name = 'Rend.Sem.Mat.Padova'
    #not yet in journal database
    elif jnl == 'lem':
        issn = '0013-8584'
        journal_name = 'L’Enseignement Mathématique'
    elif jnl == 'jst':
        issn = '1664-039X'
        journal_name = 'Journal of Spectral Theory'
    elif jnl == 'emss':
        issn = '2308-2151'
        journal_name = 'EMS Surveys in Mathematical Sciences'
    elif jnl == 'owr':
        issn = '1660-8933'
        journal_name = 'Oberwolfach Reports'
        tc = ''
    elif jnl == 'em':
        issn = '0013-6018'
        journal_name = 'Elemente der Mathematik'
    elif jnl == 'ggd':
        issn = '1661-7207'
        journal_name = 'Groups, Geometry, and Dynamics'
    elif jnl == 'ifb':
        issn = '1463-9963'
        journal_name = 'Interfaces and Free Boundaries'
    elif jnl == 'jca':
        issn = '2415-6302'
        journal_name = 'Journal of Combinatorial Algebra'
    elif jnl == 'jfg':
        issn = '2308-1309'
        journal_name = 'Journal of Fractal Geometry'
    elif jnl == 'zaa':
        issn = '0232-2064'
        journal_name = 'Zeitschrift für Analysis und ihre Anwendungen'
    to_curl = 'https://ems.press/journals/%s/issues/%s' % (jnl, issnr)
    print(to_curl)

    #print('--- OPEN JOURNAL ', journal_name.upper(), 'VOLUME', vol, 'ISSUE', issue, '---')
    resp = session.get(to_curl)

    if resp.status_code != 200:
        print("Can't reach the page")
        exit(0)
    tocpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    artlinks = []
    for div in  tocpage.find_all('div', attrs={'class': 'content-container'}):
        for a in div.find_all('a'):
            if a.has_attr('href'):
                artlinks.append('https://ems.press{}'.format(a.get('href')))
    for (j, artlink) in enumerate(artlinks):
        ejlmod3.printprogress('~', [[jnl, issnr], [j+1, len(artlinks)], [artlink]])
        recs.append(get_sub_site(session, artlink, jnl, journal_name, tc))
        sleep(5)
    if recs:
        if 'issue' in recs[-1]:
            jnlfilename = 'ems_%s_%s%s.%s' % (issnr, jnl, recs[-1]['vol'], recs[-1]['issue'])
        else:
            jnlfilename = 'ems_%s_%s%s' % (issnr, jnl, recs[-1]['vol'])
        ejlmod3.writenewXML(recs, publisher, jnlfilename)
    return

session = Session()
i = 0
for jnl in jnls:
    i += 1
    todo = []
    jnlurl = 'https://ems.press/journals/%s/read' % (jnl)
    ejlmod3.printprogress('=', [[i, len(jnls)], [jnlurl]])
    resp = session.get(jnlurl)
    if resp.status_code != 200:
        print("Can't reach the page")
        exit(0)
    jnlpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    year = 9999
    for ul in jnlpage.find_all('ul', attrs = {'class' : 'issue-list'}):
        for child in ul.children:
            try:
                cn = child.name
            except:
                continue
            if cn == 'h2':
                for span in child.find_all('span'):
                    st = span.text
                    if re.search('[12]\d\d\d', st):
                        year = int(re.sub('.*?([12]\d\d\d).*', r'\1', st))
                        print('    ', year)
            elif cn == 'li':
                if year > ejlmod3.year(backwards=years):
                    for a in child.find_all('a'):
                        issnr = re.sub('.*\/', '', a['href'])
                        print('      ', issnr)
                        if not issnr in done:
                            if not issnr in todo:
                                todo.append(issnr)
    j = 0
    for issnr in todo:
        j += 1
        ejlmod3.printprogress('-', [[i, len(jnls)], [j, len(todo)], [jnl, issnr]])
        get_issue(session, jnl, issnr)
        sleep(90)
