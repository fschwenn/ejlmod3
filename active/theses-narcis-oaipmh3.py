# -*- coding: utf-8 -*-
#harvest theses from NARCIS via OAI-PMH
#seems to be incomplete
#FS: 2022-07-12


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'NARCIS'
jnlfilename = 'THESES-NARCIS-%s' % (ejlmod3.stampofnow())
bunchlength = 100
pages = 300


startdate = '%i%s' % (ejlmod3.year(backwards=1), ejlmod3.stampoftoday()[4:])
stopdate = ejlmod3.stampoftoday()
#check individual pages of bunch of records

boring = ['Applied Ergonomics and Design', 'BT/Biocatalysis', 'Ethics & Philosophy of Technology',
          'Aerodynamics', 'Aerospace Manufacturing Technologies', 'Aerospace Structures & Computational Mechanics',
          'Aerospace Transport & Operations', 'Aircraft Noise and Climate Effects', 'Applied Geology',
          'Applied Geophysics and Petrophysics', 'Atmospheric Remote Sensing', 'Bio-Electronics',
          'Biomaterials & Tissue Biomechanics', 'Biomechatronics & Human-Machine Control',
          'BT/Bioprocess Engineering', 'BT/Biotechnology and Society', 'BT/Environmental Biotechnology',
          'BT/Enzymology', 'BT/Industrial Microbiology', 'Building Law', 'Building Product Innovation',
          'Building Services', 'ChemE/Advanced Soft Matter', 'ChemE/Catalysis Engineering',
          'ChemE/Materials for Energy Conversion & Storage', 'ChemE/Opto-electronic Materials',
          'ChemE/Product and Process Engineering', 'ChemE/Transport Phenomena', 'Circular Product Design',
          'CITG Section Building Engineering', 'Climate Design and Sustainability', 'Coastal Engineering',
          'Comp Graphics & Visualisation', 'Control & Simulation', 'Cyber-Physical Systems',
          'DC systems, Energy conversion & Storage', 'Delft University Wind energy research institute',
          'Design Aesthetics', 'Design & Construction Management', 'Design and Politics',
          'Design Conceptualization and Communication', 'Design for Sustainability', 'Design of Constrution',
          'Digital Architecture', 'Distributed Systems', 'Dynamics of Micro and Nano Systems',
          'Economics of Technology and Innovation', 'Electrical Power Processing',
          'Electronic Components, Technology and Materials', 'Electronic Instrumentation', 'Emerging Materials',
          'Energy & Industry', 'Energy Technology', 'Engineering Thermodynamics', 'Environmental Fluid Mechanics',
          'Flight Performance and Propulsion', 'Geo-engineering', 'Heritage & Technology', 'Housing Management',
          'Human Information Communication Design', 'Human-Robot Interaction', 'Hydraulic Structures and Flood Risk',
          'Integral Design and Management', 'Intelligent Electrical Power Grids',
          'Intelligent Vehicles & Cognitive Robotics', 'Intensified Reaction and Separation Systems',
          'Interactive Intelligence', 'Lab Geoscience and Engineering', 'Landscape Architecture',
          'Large Scale Energy Storage', 'Learning & Autonomous Control', 'Marketing and Consumer Research',
          'Materials and Environment', 'Mathematical Geodesy and Positioning', 'Mechatronic Design',
          'Mechatronic Systems Design', 'Medical Instruments & Bio-Inspired Technology', 'Micro and Nano Engineering',
          'Microwave Sensing, Signals & Systems', 'Multimedia Computing', 'Network Architectures and Services',
          'Novel Aerospace Materials', 'Numerical Analysis', 'Offshore and Dredging Engineering',
          'Offshore Engineering', 'OLD BT/Cell Systems Engineering', 'OLD ChemE/Organic Materials and Interfaces',
          'OLD Geo-information and Land Development', 'OLD High-Voltage Technology and Management',
          'OLD Housing Quality and Process Innovation', 'OLD Housing Systems', 'OLD Intelligent Control & Robotics',
          'OLD Interior', 'OLD Management and Organisation', 'OLD Metals Processing, Microstructures and Properties',
          'OLD Methods & Analysis', 'OLD Public Buiding', 'OLD Structural Design', 'OLD Support RES',
          'OLD Urban and Regional Development', 'OLD Urban Compositions', 'OLD Urban Design',
          'OLD Urban Renewal and Housing', 'OLD Virtual Materials and Mechanics', 'OLD Woningbouw',
          'Optical and Laser Remote Sensing', 'Optimization', 'Organisation and Governance',
          'Pattern Recognition and Bioinformatics', 'Pavement Engineering', 'Petroleum Engineering',
          'Photovoltaic Materials and Devices', 'Policy Analysis', 'Programming Languages', 'Railway Engineering',
          'Real Estate Management', 'Resource Engineering', 'Rivers, Ports, Waterways and Dredging Engineering',
          'Robot Dynamics', 'RST/Applied Radiation & Isotopes', 'RST/Biomedical Imaging',
          'RST/Fundamental Aspects of Materials and Energy', 'RST/Neutron and Positron Methods in Materials',
          'RST/Storage of Electrochemical Energy', 'Safety and Security Science', 'Sanitary Engineering',
          'Science Education and Communication', 'Ship Design, Production and Operations',
          'Ship Hydromechanics and Structures', 'Software Engineering', 'Space Systems Egineering',
          'Spatial Planning and Strategy', 'Steel & Composite Structures', 'Structural Design & Mechanics',
          'Structural Integrity & Composites', 'Structural Optimization and Mechanics', 'System Engineering',
          'Teachers of Practice', 'Transport and Logistics', 'Transport and Planning', 'Transport Engineering and Logistics',
          'Urban Data Science', 'Water Resources', 'Web Information Systems', 'Wind Energy', 'Architectural Engineering',
          'Bio-based Structures & Materials', 'BN/Greg Bokinsky Lab', 'Circuits and Systems', 'History & Complexity',
          'Mathematical Geodesy & Positioning', 'Methods & Matter', 'Urban Design']

                




def processrecs(prerecs, bunchcounter):
    i = 0
    recs = []
    for rec in prerecs:
        keepit = True
        #print(rec['xml'])
        uni = 'unknown'
        i += 1
        rec['artlink'] = 'https://www.narcis.nl/publication/RecordID/' + rec['identifier']
        rec['note'].append(rec['artlink'])
        ejlmod3.printprogress('-', [[bunchcounter], [i, len(prerecs)], [len(recs)], [rec['artlink']]])
        #req = urllib2.Request(rec['artlink'], headers=hdr)    
        #artpage = BeautifulSoup(urllib2.urlopen(req))
        #artfilename = '/tmp/THESES-NARCIS_%s' % (re.sub('\W', '', rec['artlink']))
        #if not os.path.isfile(artfilename):
        #    os.system('wget -T 300 -O %s "%s"' % (artfilename, rec['artlink']))
        #    time.sleep(5)
        #abstract
        for abstract in rec['xml'].metadata.find_all('abstract'):
            rec['abs'] = abstract.text
        #DOI
        for doi in rec['xml'].metadata.find_all('identifier', attrs = {'type' : 'doi'}):
            rec['doi'] = doi.text
        #ISBN
        for isbn in rec['xml'].metadata.find_all('identifier', attrs = {'type' : 'isbn'}):
            rec['isbn'] = isbn.text
        #URN
        for dii in rec['xml'].metadata.find_all('dii:identifier'):
            rec['urn'] = dii.text
        #people
        for name in rec['xml'].metadata.find_all('name', attrs = {'type' : 'personal'}):
            for np in name.find_all('namepart', attrs = {'type' : 'family'}):
                person = [np.text]
            for np in name.find_all('namepart', attrs = {'type' : 'given'}):
                person[0] += ', ' + np.text
            for aff in name.find_all('affiliation'):
                person.append(aff.text)
            for ni in name.find_all('nameidentifier', attrs = {'type' : 'orcid'}):
                person.append('ORCID:'+ni.text)
            for rt in name.find_all('roleterm', attrs = {'type' : 'code'}):
                if rt.text == 'aut':
                    rec['autaff'].append(person)
                elif rt.text == 'ths':
                    rec['supervisor'].append(person)
        #institution
        for name in rec['xml'].metadata.find_all('name', attrs = {'type' : 'corporate'}):
            for np in name.find_all('namepart'):
                rec['note'].append('INST:' + np.text)
        #research group
        for note in rec['xml'].metadata.find_all('note', attrs = {'type' : 'research group'}):
            if note.text in boring:
                keepit = False
            else:
                rec['note'].append('RESEARCHGROUP:'+note.text)
        #date
        for di in rec['xml'].metadata.find_all('dateissued'):
            rec['date'] = di.text
        #pages
        for ex in rec['xml'].metadata.find_all('extent', attrs = {'unit' : 'pages'}):
            for to in ex.find_all('total'):
                rec['pages'] = to.text
        #title
        for tit in rec['xml'].metadata.find_all('title'):
            rec['tit'] = tit.text
        #OA
        for oa in rec['xml'].metadata.find_all('dcterms:accessrights'):
            if oa.text == 'info:eu-repo/semantics/openAccess':
                rec['oa'] = True
            else:
                rec['note'].append(oa.text)
        #FFT
        for res in rec['xml'].metadata.find_all('resource', attrs = {'mimetype' : 'application/pdf'}):
            if rec['oa']:
                rec['FFT'] = res['ref']
            else:
                rec['hidden'] = res['ref']
        #keywords
        for subject in rec['xml'].metadata.find_all('subject'):
            for topic in subject.find_all('topic'):
                rec['keyw'].append(topic.text)
        #check other page
        if not 'doi' in rec:
            for res in rec['xml'].metadata.find_all('resource', attrs = {'mimetype' : 'text/html'}):
                rec['link'] = res['ref']
        ejlmod3.printrecsummary(rec)
        if not 'doi' in rec or (rec['oa'] and not 'FFT' in rec):
            if 'link' in rec:
                print('  try to get PDF from %s' % (rec['link']))
                try:
                    req = urllib.request.Request(rec['link'], headers=hdr)
                    origpage = BeautifulSoup(urllib.request.urlopen(req), features="xml")
                    ejlmod3.metatagcheck(rec, origpage, ['citation_pdf_url', 'citation_isbn', 'citation_doi'])
                except:
                    print('  could not find PDF')
                if not 'FFT' in list(rec.keys()):
                    rec['link'] = rec['artlink']
                if 'hdl' in list(rec.keys()) or 'doi' in list(rec.keys()):
                    del rec['link']
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['identifier'])
        
    ejlmod3.writenewXML(recs, publisher, '%s_%03i' % (jnlfilename, bunchcounter))#, retfilename='retfiles_special')
    return

                                            
#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=3)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup']
redoki = re.compile('THESES.NARCIS.*doki$')
rehttp = re.compile('^I\-\-http.*ID\/(oai.*)\-\-$')
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
                        http = rehttp.sub(r'\1', line.strip())
                        http = re.sub('%3A', ':', http)
                        http = regenre.sub('', re.sub('2F', '/', http))
                        if not http in bereitsin:
                            if not http in nochmal:
                                bereitsin.append(http)
    print('  %6i' % (len(bereitsin)))



hdr = {'User-Agent' : 'Magic Browser'}

tocurl = 'http://oai.tudelft.nl/ir/oai/oai2.php?verb=ListRecords&metadataPrefix=nl_didl&from=' + startdate + '&until=' + stopdate
recs = []
bunchcounter = 0
for i in range(pages):
    ejlmod3.printprogress('=', [[i], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    records = tocpage.find_all('record')
    for record in records:
        for genre in record.find_all('genre'):
            if genre.text == 'info:eu-repo/semantics/doctoralThesis':
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'oa' : False, 'autaff' : [], 'supervisor' : [], 'keyw' : [],
                       'note' : []}
                rec['xml'] = record
                rec['identifier'] = rec['xml'].header.identifier.text
                if not rec['identifier'] in bereitsin:
                    if ejlmod3.ckeckinterestingDOI(rec['identifier']):
                        recs.append(rec)
    print('   ', len(recs))
    if len(recs) >= bunchlength:
        processrecs(recs, bunchcounter)
        bunchcounter += 1
        recs = []
    rts = tocpage.find_all('resumptiontoken')
    if rts:
        for rt in rts:
            tocurl = 'http://oai.tudelft.nl/ir/oai/oai2.php?verb=ListRecords&resumptionToken=' + rt.text.strip()
            time.sleep(2)
    else:
        break
if len(recs) < bunchlength:
    processrecs(recs, bunchcounter)
    bunchcounter += 1
    recs = []
