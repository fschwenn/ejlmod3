# -*- coding: utf-8 -*-
#harvest theses from Groningen U.
#FS: 2022-02-14
#FS: 2023-01-09

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Groningen U.'

rpp = 50
pages = 20
skipalreadyharvested = True
jnlfilename = 'THESES-GRONINGEN-%s' % (ejlmod3.stampoftoday())
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'

boringdegrees = ['Master of Philosophy', 'Master of Science']
boringinstitutes = ['Education in Culture', 'Analytical Biochemistry', 'Arctic and Antarctic studies',
                    'Artificial Intelligence', 'Chemical Biology 2', 
                    'Drug Design', 'Effective Criminal Law', 'Electron Microscopy',
                    'Environmental Psychology', 'Etienne group', 'Faculty of Philosophy',
                    'Intelligent Systems', 'Molecular Dynamics', 'Culture, Language & Technology',
                    'Nanostructures of Functional Oxides', 'Sociology/ICS', 'SOM EEF', 'SOM Marketing',
                    'SOM OPERA', 'Theoretical Chemistry', 'Theory and History of Psychology',
                    'Transboundary Legal Studies', 'Zernike Institute for Advanced Materials',
                    'Archaeology of Northwestern Europe', 'Beersma lab', 'Beukeboom lab',
                    'Biomolecular Chemistry & Catalysis', 'Biotechnology',
                    'Center for Language and Cognition (CLCG)',
                    'Center for Liver, Digestive and Metabolic Diseases (CLDM)',
                    'Chemical and Pharmaceutical Biology', 'Chemical Technology',
                    'Classical and Mediterranean Archaeology', 'Clinical Neuropsychology',
                    'Clinical Psychology and Experimental Psychopathology', 'Conservation Ecology Group',
                    'Culture, Language & Technology', 'Department of Social Sciences',
                    'Discrete Technology and Production Automation', 'Dugdale group',
                    'Energy and Sustainability Research Institute Gron.', 'Enzymology', 'Eriksson group',
                    'Experimental Psychology', 'Falcao Salles lab', 'Fontaine lab',
                    'Groningen Institute for Gastro Intestinal Genetics and Immunology (3GI)',
                    'Groothuis lab', 'Komdeur lab', 'Maan group', 'Molecular Genetics',
                    'Molecular Microbiology', 'Molecular Pharmacology', 'Van Dijk lab',
                    'Nanostructured Materials and Interfaces', 'Ocean Ecosystems',
                    'Organizational Psychology', 'Product Technology', 'Public Trust and Public Law',
                    'Research and Evaluation of Educational Effectiveness',
                    'Science Education and Communication', 'Tieleman lab', 'Van de Zande lab',
                    'Scientific Visualization and Computer Graphics', 'Smart Manufacturing Systems',
                    'Software Engineering', 'Solid State Materials for Electronics',
                    'Systems, Control and Applied Analysis', 'Cell Biochemistry',
                    'Damage and Repair in Cancer Development and Cancer Treatment (DARE)',
                    'Developmental and behavioural disorders in education and care: assessment and intervention',
                    'Developmental Psychology', 'Distributed Systems', 'Ethics, Social and Political Philosophy',
                    'Faculteit Medische Wetenschappen', 'Host-Microbe Interactions', 'Kas lab',
                    'Macromolecular Chemistry & New Polymeric Materials', 'Molecular Systems Biology',
                    'Palsbøll lab', 'Pharmaceutical Analysis', 'Pharmaceutical Technology and Biopharmacy',
                    'PharmacoTherapy, -Epidemiology and -Economics', 'Photophysics and OptoElectronics',
                    'Products and Processes for Biotechnology', 'Public Interests and Private Relationships',
                    'Research Centre for the Study of Democratic Cultures and Politics (DemCP)',
                    'Stratingh Institute for Chemistry', 'Surfaces and Thin Films', 'Synthetic Organic Chemistry',
                    'Teaching and Teacher Education', 'Advanced Production Engineering',
                    'Adv Res Ctr Nanolithog ARCNL', 'Billeter lab', 'Bioproduct Engineering', 'Both group',
                    'Chemical Biology 1', 'Chemistry of (Bio)organic Materials and Devices',
                    'Comparative Study of Religion', 'Cosmic Frontier', 'Department of Humanities',
                    'Discourse and Communication (DISCO)', 'Eisel lab', 'Elizabeth Hosp, Dept Surg',
                    'Govers group', 'Greek Archaeology', 'Havekes lab', 'History of Philosophy',
                    'Isala Hosp, Dept Cardiol', 'Jewish, Christian and Islamic Origins',
                    'Law on Energy and Sustainability', 'Meerlo lab', 'Molecular Biophysics',
                    'Molecular Cell Biology', 'Molecular Immunology', 'Molecular Inorganic Chemistry',
                    'Mol Enzymol Groningen Biomol Sci & Biotechnol Ins', 'Nanomedicine & Drug Targeting',
                    'Olff group', 'Olivier lab', 'Palsbøll lab', 'Piersma group',
                    'Polymer Chemistry and Bioengineering', 'Protecting European Citizens and Market Participants',
                    'Psychometrics and Statistics', 'Radboud University Nijmegen Medical Centre',
                    'Research unit Medical Physics', 'Rijnstate Hosp, Dept Surg, Div Vasc Surg', 'Smit group',
                    'Social Psychology', 'Spaarne Hosp, Dept Pulm Dis', 'Sustainable Economy',
                    'Sust Entr. in a Circular Econ', 'System Chemistry', 'Theoretical Philosophy',
                    'UMC Utrecht, University of Utrecht, Dept Rehabil Nursing Sci & Sports',
                    'Univ Amsterdam, University of Amsterdam, University of Groningen, Acad Med Ctr, Dept Resp Med, Univ Groningen',
                    'University of Groningen, Faculty of Behavioural and Social Sciences',
                    'Groningen Biomolecular Sciences and Biotechnology',
                    'Groningen Institute for Organ Transplantation (GIOT)',
                    'Groningen Research Institute of Pharmacy', 'Urban and Regional Studies Institute',
                    'Univ. Giessen, Justus-Liebig-Universität Giessen, Fac. Psychologie und Sportwissenschaften, Institut für Psychologische Diagnostik',
                    'Univ Groningen, University of Groningen, Grad Sch Humanities', 'Univ Groningen, University of Groningen, Univ Med Ctr Groningen, Div Geriatr Med, Univ Ctr Geriatr Med',
                    'Univ Med Ctr Groningen, University of Groningen, Dept Surg, Div Vasc Surg',
                    'Groningen Institute of Archaeology', 'Neurolinguistics and Language Development (NLD)',
                    'User-friendly Private Law', 'Van der Heide group', 'Van der Zee lab', 'Van Doorn group',
                    'Vrije Universiteit Amsterdam, Amsterdam', 'Wertheim lab', 'X-ray Crystallography']
boringinstitutes += ['Christianity and the History of Ideas', 'Faculty of Economics and Business', 'Geo-Energy',
                     'Integrated Research on Energy, Environment & Socie', 'Research Centre Arts in Society (AiS)',
                     'Research Centre for Historical Studies (CHS)', 'SOM Accounting', 'SOM GEM', 'SOM I&O',
                     'SOM OB', 'Theoretical and Empirical Linguistics (TEL)',
                     'Univ Utrecht, University of Utrecht, Dept Sociol ICS']

boringwords = ['health', 'clinical', 'patients', 'cancer', 'disease', 'molecular', 'therapy', 'surgical', 'kidney',
               'diabetes', 'liver', 'biomarkers', 'injury', 'vitro', 'metabolic', 'Disease', 'diseases', 'therapeutic',
               'Molecular', 'metabolism', 'medical', 'Health', 'cellular', 'lung', 'lipid', 'immunotherapy', 'healthy',
               'glaucoma', 'dementia', 'blood', 'lymphoma', 'leukemia', 'pediatric', 'Tumor', 'tumor', 'social',
               'protein', 'proteins', 'asthma', 'Bacillus', 'chemistry', 'surgery', 'Clinical', 'Social', 'patient',
               'bacteria', 'biological', 'schizophrenia', 'cardiovascular', 'psychological', 'Escherichia', 'Drosophila',
               'Bacterial', 'anxiety', 'myocardial', 'cerebral', 'cardiac', 'microbial', 'medicine', 'drugs', 'biology',
               'animal', 'pathogenesis', 'Metabolic', 'influenza', 'dental']
def checkboringwords(title):
    for part in re.split('\W+', title):
        if part in boringwords:
            #print '  skip "%s" because of "%s"' % (title, part)
            return True
    return False
    
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))        
    alreadyharvested += list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s %s/%i/*%s | grep URLDOC=10.33612 | sed 's/.*=//' | sed 's/;//' " % (dokidir, 'THESES-NARCIS*doki', dokidir, ejlmod3.year(backwards=1), 'THESES-NARCIS*doki', dokidir, ejlmod3.year(backwards=2), 'THESES-NARCIS*doki'))))
    print('%i records in backup' % (len(alreadyharvested)))        

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://research.rug.nl/en/publications/?type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput%2Fresearchoutputtypes%2Fthesis%2Fdoc3&type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput%2Fresearchoutputtypes%2Fthesis%2Fdoc&nofollow=true&format=&page=' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for li in tocpage.body.find_all('li', attrs = {'class' : 'list-result-item'}):
        for a in li.find_all('a', attrs = {'rel' : 'Thesis'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'isbns' : []}
            rec['artlink'] = a['href']
            rec['tit'] = a.text.strip()
        for span in li.find_all('span', attrs = {'class' : 'numberofpages'}):
            rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', span.text.strip())
        if ejlmod3.checkinterestingDOI(rec['artlink']):
            if checkboringwords(rec['tit']):
                ejlmod3.adduninterestingDOI(rec['artlink'])
            else:
                prerecs.append(rec)
    print('   picked %i from %i so far (%i to be checked in total)' % (len(prerecs), (page+1)*rpp, pages*rpp))
    time.sleep(5)

    
i = 0
recs = []
for rec in prerecs:    
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_publication_date', 'citation_title', 'citation_author',
                                        'citation_doi', 'citation_language'])
    if 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  already in backup')
        keepit = False
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #institute
            if meta['name'] == 'citation_author_institution':
                rec['autaff'][-1].append('%s, %s' % (meta['content'], publisher))
                if meta['content'] in boringinstitutes:
                    keepit = False
                    print('   skip "%s"' % (meta['content']))
                elif meta['content'] in ['Algebra', 'Dynamical Systems, Geometry & Mathematical Physics',
                                         'Computational and Numerical Mathematics']:
                    rec['fc'] = 'm'
                elif meta['content'] in ['Astronomy', 'Astrophysics']:
                    rec['fc'] = 'a'
                elif meta['content'] in ['Optical Physics of Condensed Matter', 'Theory of Condensed Matter']:
                    rec['fc'] = 'f'
                elif meta['content'] in ['Quantum interactions and structural dynamics']:
                    rec['fc'] = 'k'
                elif meta['content'] in ['Stochastic Studies and Statistics']:
                    rec['fc'] = 's'
                elif not meta['content'] in ['Device Physics of Complex Materials', 'High-Energy Frontier',
                                             'Isotope Research', 'Micromechanics', 'Nuclear Energy',
                                             'Physics of Nanodevices', 'Polymer Science', 'Precision Frontier',
                                             'Van Swinderen Institute for Particle Physics and G']:
                    rec['note'].append(meta['content'])
            #pdf
            elif meta['name'] == 'citation_pdf_url':
                if re.search('Complete_thesis', meta['content']):
                    rec['FFT'] = meta['content']
    for tr in artpage.body.find_all('tr'):
        for th in tr.find_all('th'):
            tht = th.text.strip()
            for td in tr.find_all('td'):
                #ISBN
                if re.search('Print ISBN', tht):
                    for isbn in re.split(', ', td.text.strip()):
                        rec['isbns'].append([('a', re.sub('\-', '', isbn)), ('b', 'Print')])
                elif re.search('Electronic ISBNs', tht):
                    for isbn in re.split(', ', td.text.strip()):
                        rec['isbns'].append([('a', re.sub('\-', '', isbn)), ('b', 'Online')])
                #Supervisor
                elif re.search('Supervisor', tht):
                    for li in td.find_all('li'):
                        if re.search('Supervisor', li.text):
                            for span in li.find_all('span', attrs = {'class' : 'person'}):
                                rec['supervisor'].append([span.text.strip()])
                #Qualification
                elif re.search('Qualification', tht):
                    degree = td.text.strip()
                    if degree != 'Doctor of Philosophy':
                        if degree in boringdegrees:
                            print('   skip "%s"' % (degree))
                            keepit = False
                        else:
                            rec['note'].append(degree)
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'rendering_abstractportal'}):
        for div2 in div.find_all('div', attrs = {'class' : 'textblock'}):
            rec['abs'] = div2.text.strip()
    if keepit:
        if not 'doi' in list(rec.keys()):
            rec['link'] = rec['artlink']
            rec['doi'] = '30.3000/Groningen/' + re.sub('\W', '', rec['link'][39:])
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

line = jnlfilename+'.xml'+ "\n"




ejlmod3.writenewXML(recs, publisher, jnlfilename)
