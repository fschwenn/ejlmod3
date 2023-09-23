# -*- coding: utf-8 -*-
#harvest theses from IFM-UMSNH, Michoacan
#FS: 2023-06-16

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 50
pages = 2
skipalreadyharvested = True
boring = ['info:eu-repo/semantics/masterThesis']
boring += ['Facultad de Arquitectura. Programa Interinstitucional de Doctorado en Arquitectura',
           'Facultad de Contaduría y Ciencias Administrativas. Doctorado en Administración',
           'Facultad de Economía Vasco de Quiroga. Doctorado en Ciencias en Desarrollo Sustentable',
           'Facultad de Economía Vasco de Quiroga. Doctorado Interinstitucional en Economía Social Solidaria',
           'Instituto de Investigación en Metalurgia y Materiales. Doctorado en Ciencias en Metalurgia y Ciencias de los Materiales',
           'Instituto de Investigaciones Agropecuarias y Forestales. Instituto de Investigaciones sobre los Recursos Naturales. Instituto de Investigaciones Químico Biológicas. Facultad de Biología. Facultad de Medicina Veterinaria y Zootecnia. Facultad de Químico Farmacobiología. Programa Institucional de Doctorado en Ciencias Biológicas',
           'Instituto de Investigaciones Históricas. Facultad de Historia. Programa Institucional de Doctorado en Historia',
           'Facultad de Derecho y Ciencias Sociales. Doctorado interinstitucional en Derecho',
           'Facultad de Ingeniería Química. Doctorado en Ciencias en Ingeniería Química',
           'Facultad de Psicología. Doctorado Institucional en Psicología',
           'Instituto de Investigaciones Económicas y Empresariales. Ciencias en Negocios Internacionales',
           'Instituto de Investigaciones Económicas y Empresariales. Doctorado en Ciencias del Desarrollo Regional',
           'Instituto de Investigaciones Económicas y Empresariales. Doctorado en Políticas Públicas',
           'Instituto de Investigaciones Filosóficas. Facultad de Filosofía. Doctorado Institucional en Filosofía',
           'Instituto de Investigaciones Químico Biológicas. Doctorado en Ciencias Químicas',
           'Facultad de Letras. Arte y Cultura',
           'Instituto de Investigaciones Económicas y Empresariales. Ciencias del Desarrollo Regional',
           'Instituto de Investigaciones Económicas y Empresariales. Políticas Públicas',
           'Instituto de Investigaciones Metalúrgicas. Doctorado en Ciencias en Metalurgia y Ciencias de los Materiales',
           'Instituto de Investigaciones Químico Biológicas. Doctorado en Ciencias en Biología Experimental',
           'Instituto de Investigaciones Químico Biológicas. Doctorado en Ciencias en Biología Experimenta']

publisher = 'IFM-UMSNH, Michoacan'
jnlfilename = 'THESES-UMSNHMIchoacan-%s' % (ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

rerepnr = re.compile('^[A-Z\-]+20\d\d[A-Z\-]+$')
for page in range(pages):
    prerecs = []
    tocurl = 'http://bibliotecavirtual.dgb.umich.mx:8083/xmlui/handle/DGB_UMICH/3/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1 + 6) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    except:
        print("retry %s in 300 seconds" % (tocurl))
        time.sleep(300)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    try:
        for rec in ejlmod3.getdspacerecs(tocpage, 'http://bibliotecavirtual.dgb.umich.mx:8083', fakehdl=True):
            rec['doi'] = '20.2000/UMSNH_Michoacan/' + re.sub('.*handle\/', '', rec['link'])
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    prerecs.append(rec)
    except:
        print('              could not read page')
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

    recs = []
    for (i, rec) in enumerate(prerecs):
        keepit = True
        i += 1
        ejlmod3.printprogress("-", [[page+1, pages], [i+1, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            time.sleep(7)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['link']))
                time.sleep(180)
                req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
                artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            except:
                print("no access to %s" % (rec['link']))
                continue
        ejlmod3.metatagcheck(rec, artpage, ['DC.rights', 'DCTERMS.issued', 'DCTERMS.abstract',
                                            'DC.language', 'DC.title', 'citation_pdf_url'])
        #detailed view
        tabelle = {}
        for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
            for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
                label = td.text.strip()
                td.decompose()
            tds = tr.find_all('td')
            if len(tds) >= 1:
                if label in list(tabelle.keys()):
                    tabelle[label].append(tds[0].text.strip())
                else:
                    if tds[0].text.strip():
                        tabelle[label] = [ tds[0].text.strip() ]
        #type
        if 'dc.type' in tabelle:
            for ty in tabelle['dc.type']:
                #print('  ty:', ty)
                if ty in boring:
                    keepit = False
                    print('  skip "%s"' % (ty ))
                elif ty != 'info:eu-repo/semantics/doctoralThesis':
                    rec['note'].append('TYPE:::' + ty)
        #pages
        if 'dc.format.extent' in tabelle:
            for pages in  tabelle['dc.format.extent']:
                if re.search('\d\d+', pages):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)
        #keywords
        if 'dc.subject' in tabelle:
            for kw in tabelle['dc.subject']:
                #print('     kw:', kw)
                if not re.search('^info:eu', kw) and not rerepnr.search(kw):
                    rec['keyw'].append(kw)
        #area
        if 'dc.description' in tabelle:
            for area in tabelle['dc.description']:
                #print('     area:', area)
                if area in boring:
                    keepit = False
                    print('  skip "%s"' % (area))
                else:
                    rec['note'].append('AREA:::' + area)
        #supervisor
        if 'dc.contributor.advisor' in tabelle:
            for sv in tabelle['dc.contributor.advisor']:
                rec['supervisor'].append([sv])
        #author  
        if 'dc.contributor.author' in tabelle:
            for aut in tabelle['dc.contributor.author']:
                rec['autaff'] = [[ aut, publisher ]]
        if keepit:        
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['doi'])
    jnlfilename = 'THESES-UMSNHMIchoacan-%02i-%s' % (page, ejlmod3.stampoftoday())    
    ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
