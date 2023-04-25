# -*- coding: utf-8 -*-
#harvest theses from Colombia, U. Natl.
#FS: 2020-11-03
#FS: 2023-04-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 20
pages = 50
skipalreadyharvested = True
boring = ['info:eu-repo/semantics/masterThesis']
boring += ['Biotecnología microbiana', 'Historia cultural', 'Agentes culturales',
           'AEROELASTICIDAD', 'Comunicación Educación', 'Econofísica',
           'Economía del desarrollo', 'Epidemiología Molecular',
           'Estudios del porno y economía política', 'Farmacoeconomía',
           'Museología', 'Química computacional', 'Sostenibilidad alimentaria',
           'Sostenibilidad Urbano Regional', 'Suelos y Aguas']

publisher = 'Colombia, U. Natl.'
jnlfilename = 'THESES-ColombiaUNatl-%s' % (ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://repositorio.unal.edu.co/handle/unal/1/recent-submissions?offset=' + str(rpp*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://repositorio.unal.edu.co', fakehdl=True):
        rec['doi'] = '20.2000/ColumbiaUNatl/' + re.sub('.*handle\/', '', rec['link'])
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            if ejlmod3.checkinterestingDOI(rec['doi']):
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #detailed view
    tabelle = {}
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            if label in list(tabelle.keys()):
                tabelle[label].append(td.text.strip())
            else:
                tabelle[label] = [ td.text.strip() ]
    #author
    if 'dc.contributor.author' in tabelle:
        for au in tabelle['dc.contributor.author']:
            rec['autaff'] = [[ au, publisher ]]
    #date
    if 'dc.date.issued' in tabelle:
        rec['date'] = tabelle['dc.date.issued'][0]
    #DDC
    if 'dc.subject.ddc' in tabelle:
        for ddc in tabelle['dc.subject.ddc']:
            if ddc[0] in ['1', '2', '3', '4', '6', '7', '8', '9']:
                keepit = False
                #print('  skip "%s"' % (ddc))
            elif ddc[:2] in ['54', '55', '56', '57', '58', '59']:
                keepit = False
                #print('  skip "%s"' % (ddc))
            elif ddc[:2] == '51':
                rec['fc'] = 'm'
            elif ddc[:2] == '52':
                rec['fc'] = 'a'
            else:
                rec['note'].append('DDC:::'+ddc)
    #abstract
    if 'dc.description.abstract' in tabelle:
        for abstract in tabelle['dc.date.issued']:
            if re.search(' the ', abstract):
                rec['date'] = abstract
    #license
    if 'dc.rights.uri' in tabelle:
        for lic in tabelle['dc.rights.uri']:
            if re.search('vecommons.org', lic):
                rec['license'] = {'url' : lic}
    #title
    if 'dc.title' in tabelle:
        rec['tit'] = tabelle['dc.title'][0]
    if 'dc.title.translated' in tabelle:
        rec['transtit'] = tabelle['dc.title.translated'][0]
    #type
    if 'dc.type.driver' in tabelle:
        for ty in tabelle['dc.type.driver']:
            if ty in boring:
                keepit = False
                #print('  skip "%s"' % (ty ))
            elif ty != 'info:eu-repo/semantics/doctoralThesis':
                rec['note'].append('TYPE:::' + ty)
    #pages
    if 'dc.format.extent' in tabelle:
        for pages in  tabelle['dc.format.extent']:
            if re.search('\d\d+', pages):
                rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)
    #keywords
    if 'dc.subject.proposal' in tabelle:
        rec['keyw'] += tabelle['dc.subject.proposal']
    #area
    if 'dc.description.researcharea' in tabelle:
        for area in tabelle['dc.description.researcharea']:
            if area in boring:
                keepit = False
                #print('  skip "%s"' % (area))
            elif area == 'Condensed Matter':
                rec['fc'] = 'f'
            else:
                rec['note'].append('AREA:::' + area)
    #language
    if 'dc.language.iso' in tabelle:
        rec['language'] = tabelle['dc.language.iso'][0]
    #supervisor
    if 'dc.contributor.advisor' in tabelle:
        for sv in tabelle['dc.contributor.advisor']:
            rec['supervisor'].append([sv])
    #references
    if 'dc.relation.references' in tabelle:
        rec['refs'] = []
        if len(tabelle['dc.relation.references']) > 10:
            for ref in tabelle['dc.relation.references']:
                rec['refs'].append([('x', ref)])
    #PDF
    for div in artpage.find_all('div', attrs = {'class' : 'thumbnail'}):
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('\.pdf', a['href']):
                rec['pdf_url'] = 'https://repositorio.unal.edu.co' + a['href']
    if keepit:        
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
