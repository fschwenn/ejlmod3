# -*- coding: utf-8 -*-
#harvest theses from TU Delft
#FS: 2023-07-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True
years = 2

boring = ['Urban Studies', 'Transport and Logistics', 'Sanitary Engineering',
          'Environmental & Climate Design', 'Water Resources', 'Coastal Engineering',
          'Urban Design', 'Complex Fluid Processing', 'Housing Quality and Process Innovation',
          'Mechatronic Design', 'OLD Housing Systems', 'Real Estate Management',
          'RST/Biomedical Imaging', 'RST/Neutron and Positron Methods in Materials',
          'Urban Data Science', 'Bio-Electronics', 'Design & Construction Management',
          'Dynamics of Micro and Nano Systems', 'Housing Management',
          'Large Scale Energy Storage', 'OLD ChemE/Organic Materials and Interfaces',
          'Steel & Composite Structures', 'Cyber-Physical Systems',
          'Design Conceptualization and Communication', 'Numerics for Control & Identification',
          'Optimization', 'Rivers, Ports, Waterways and Dredging Engineering',
          'ChemE/Inorganic Systems Engineering', 'Circular Product Design',
          'ImPhys/Acoustical Wavefield Imaging', 'ImPhys/Microscopy Instrumentation & Techniques',
          'Intensified Reaction and Separation Systems', 'Landscape Architecture',
          'Offshore and Dredging Engineering', 'Offshore Engineering',
          'OLD BT/Cell Systems Engineering', 'Science Education and Communication',
          'BT/Biotechnology and Society', 'Design Aesthetics', 'Embedded and Networked Systems',
          'Human-Robot Interaction', 'ImPhys/Medical Imaging', 'OLD Urban Compositions',
          'Pavement Engineering', 'QID/Hanson Lab', 'Spatial Planning and Strategy',
          'Web Information Systems', 'Comp Graphics & Visualisation', 'Design Informatics',
          'Design of Constrution', 'Human Information Communication Design',
          'Integral Design and Management', 'Mathematical Geodesy and Positioning',
          'RST/Storage of Electrochemical Energy', 'Structural Optimization and Mechanics',
          'Aircraft Noise and Climate Effects', 'Applied Geology', 'History & Complexity',
          'Microwave Sensing, Signals & Systems', 'Network Architectures and Services',
          'Aerospace Transport & Operations', 'ChemE/Product and Process Engineering',
          'Climate Design and Sustainability', 'Intelligent Vehicles',
          'RST/Applied Radiation & Isotopes', 'System Engineering',
          'Economics of Technology and Innovation', 'Marketing and Consumer Research',
          'Multimedia Computing', 'ChemE/Transport Phenomena', 'Energy Technology',
          'Biomechatronics & Human-Machine Control', 'ChemE/Advanced Soft Matter',
          'Design for Sustainability', 'ChemE/Opto-electronic Materials',
          'Mechatronic Systems Design', 'Photovoltaic Materials and Devices',
          'BT/Bioprocess Engineering', 'Fluid Mechanics', 'Atmospheric Remote Sensing',
          'Biomaterials & Tissue Biomechanics', 'BT/Biocatalysis',
          'Engineering Thermodynamics', 'Ethics & Philosophy of Technology',
          'Interactive Intelligence', 'Ship Design, Production and Operations',
          'ChemE/Catalysis Engineering', 'Medical Instruments & Bio-Inspired Technology',
          'Railway Engineering', 'ChemE/Materials for Energy Conversion & Storage',
          'Aerospace Structures & Computational Mechanics', 'Applied Ergonomics and Design',
          'Structural Integrity & Composites', 'Intelligent Electrical Power Grids',
          'Policy Analysis', 'Flight Performance and Propulsion', 'BT/Industrial Microbiology',
          'Organisation and Governance', 'Wind Energy',
          'DC systems, Energy conversion & Storage', 'Petroleum Engineering',
          'Geo-engineering', 'Applied Mechanics', 'Pattern Recognition and Bioinformatics',
          'Ship Hydromechanics and Structures', 'Environmental Fluid Mechanics',
          'Applied Geophysics and Petrophysics', 'Hydraulic Structures and Flood Risk',
          'Transport Engineering and Logistics', 'Energy & Industry', 'Aerodynamics',
          'Materials and Environment', 'BT/Environmental Biotechnology',
          'Transport and Planning', 'Building Services']

publisher = 'Delft Tech. U.'
jnlfilename = 'THESES-DELFT-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    alreadyharvested += ejlmod3.getalreadyharvested('THESES-NARCIS', years=7)

#get csv-file with list of theses
csvfilname = '/tmp/%s.csv' % (jnlfilename)
if not os.path.isfile(csvfilname):
    os.system('wget -O ' + csvfilname + ' -q "https://repository.tudelft.nl/islandora/search?page=1&collection=research&f%5B0%5D=mods_genre_s%3A%22doctoral%5C%20thesis%22&sort=mods_originInfo_dateSort_dt%20desc&display=tud_csv"')

#go through csv list
recs = []
inf = open(csvfilname, 'r')
for line in inf.readlines():
    parts = re.split('","', line.strip())
    if re.search('http', parts[1]):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'embargo' : False, 'note' : []}
        keepit = True
        rec['doi'] = '10.4233/' + parts[0][1:]
        rec['artlink'] = parts[1]
        rec['tit'] = parts[2]
        rec['autaff'] = [[ re.sub(' *\(.*', '', parts[3]), re.sub('.*\((.*)\)', r'\1', parts[3])]]
        for sv in re.split('; *',  parts[4]):
            if re.search('\(promotor\)', sv):
                rec['supervisor'].append([re.sub(' *\(.*', '', parts[3])])
        rec['year'] = parts[5]
        if int(rec['year']) <= ejlmod3.year(backwards=years):
            keepit = False
        rec['abs'] = parts[6]
        rec['keyw'] = re.split('; ', parts[7])
        rec['language'] = parts[8]
        if len(parts) > 11 and re.search('\d\d\d', parts[11]):
            rec['isbn'] = parts[11]
        if len(parts) > 17 and re.search('\d\d\d', parts[17]):
            embargo = parts[17]
            if embargo > ejlmod3.stampofnow():
                rec['eyw'] = True
        if len(parts) > 20 and re.search('[a-z]', parts[20]):
            researchgroup = parts[20]
            if researchgroup in boring:
                #print('   skip', researchgroup)
                keepit = False
            else:
                #print(researchgroup)
                rec['note'].append('RG:::'+researchgroup)
        if keepit:
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)
inf.close()
    
hdr = {'User-Agent' : 'Magic Browser'}

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(3)
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        print('  wait 120s')
        time.sleep(120)
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

        
    if not rec['embargo']:
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #get ORCIDs
    for div in artpage.body.find_all('div', attrs = {'class' : 'fieldset-wrapper'}):
        for span in div.find_all('span'):
            if span.has_attr('class'):
                if 'label' in span['class']:
                    label = span.text.strip()
                elif 'value' in span['class']:
                    #author
                    if label == 'Author':
                        for a in span.find_all('a'):
                            if a.has_attr('href') and re.search('orcid.org', a['href']):
                                orcid = re.sub('.*org\/', 'ORCID:', a['href'])
                                newauthor = [[rec['autaff'][0][0], orcid] + rec['autaff'][0][1:]]
                                rec['autaff'] = newauthor
                    #supervisors
                    elif label == 'Contributor':
                        rec['supervisor'] = []
                        for a in span.find_all('a'):
                            if a.has_attr('href') and re.search('orcid.org', a['href']):
                                orcid = re.sub('.*org\/', ';ORCID:', a['href'])
                                a.replace_with(orcid)
                        for br in span.find_all('br'):
                            br.replace_with(';;;')
                        spant = re.sub('[\n\t\r]', '', span.text.strip())
                        for sv in re.split(' *;;; *', spant):
                            if re.search('\(promotor\)', sv):
                                rec['supervisor'].append([re.sub(' *\(.*', '', sv)])
                                if re.search('ORCID', sv):
                                    rec['supervisor'][-1].append(re.sub('.*;ORC', 'ORC', sv))
                    #date
                    elif label == 'Date':
                        rec['date'] = span.text.strip()
    ejlmod3.printrecsummary(rec)                    
                    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
