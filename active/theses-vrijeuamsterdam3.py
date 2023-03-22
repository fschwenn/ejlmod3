# -*- coding: utf-8 -*-
#harvest theses from Vrije U., Amsterdam
#FS: 2021-12-20
#FS: 2023-03-22

import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Vrije U., Amsterdam'
jnlfilename = 'THESES-VrijeUAmsterdam-%s' % (ejlmod3.stampoftoday())

years = [ejlmod3.year(backwards=1), ejlmod3.year(), ejlmod3.year(forwards=1)]
rpp = 50
skipalreadyharvested = True

#concept
boring = ['Alzheimer Disease', 'Amsterdam', 'Amyloid', 'Anxiety Disorders', 'Anxiety', 'Astrocytes', 'Biomarkers', 'Blood Platelets', 'Brain', 'Cardiovascular Diseases', 'Child', 'climate change', 'Cognition', 'Cognitive Dysfunction', 'Colorectal Neoplasms', 'Cost-Benefit Analysis', 'Critical Care', 'dementia', 'Dementia', 'Depression', 'Depressive Disorder', 'Diaphragm', 'Ecclesiology', 'economics', 'education', 'Empirical Study', 'employee', 'Endothelial Cells', 'Epigenomics', 'Fathers', 'health', 'Health', 'Immunotherapy', 'Indonesia', 'Inflammation', 'Interneurons', 'learning', 'Major Depressive Disorder', 'Multiple Sclerosis', 'Muscles', 'Neoplasms', 'Netherlands', 'Neuropeptides', 'Palliative Care', 'Pancreatic Neoplasms', 'Parenting', 'Pathology', 'Pediatrics', 'politics', 'proteins', 'Proteins', 'Pulmonary Arterial Hypertension', 'Pulmonary Hypertension', 'Roads', 'Secretory Vesicles', 'Sleep', 'Synapses', 'teeth', 'The Netherlands', 'Theology', 'Therapeutics', 'worker', 'Wounds and Injuries', 'diet', 'Rheumatic Diseases', 'Non-Small Cell Lung Carcinoma', 'surgery', 'head and neck neoplasms', 'Oral Biochemistry', 'Delivery of Health Care', 'Infections', 'American Pragmatism', 'Antibiotic', 'Antibody Response', 'Appetite', 'Bacterium', 'B Cell', 'Bioassay', 'Biological Data Visualization', 'Breast Implant', 'Cardiovascular Disease', 'Clinical ethics', 'Clinician', 'Coronary Angiography', 'Coronary Artery Disease', 'Decision Support System', 'Dental Caries', 'Diaphragm', 'Diffuse Large B Cell Lymphoma', 'Diseases', 'Education', 'Emotion', 'Episiotomy', 'Escherichia coli', 'Estradiol', 'Famine', 'Glycemic Control', 'Gut Microbiota', 'Healthcare Professional', 'Healthcare', 'Health', 'Hemodialysis', 'Hospital', 'Immunoglobulin A', 'Incidence', 'Inflammation', 'Intellectual Disabilities', 'Intestine Flora', 'Italian Risorgimento', 'Lung', 'Lymphoma', 'Malignant Neoplasm', 'Maternal Care', 'Microflora', 'Microglia', 'Microorganism', 'Multiple Myeloma', 'Multiple Sclerosis', 'Neck Radiotherapy', 'Neurodegenerative Disorder', 'Newborn Care', 'Odor', 'Older Adult', 'Olfaction', 'Pathology', 'Pathophysiology', 'Patient Referral', 'Patient', 'Plaque', 'Pregnancy', 'Purple Bacteria', 'Quality of Life', 'Radiomics', 'Reduction (Chemistry)', 'Risorgimento', 'Serositis', 'Sex', 'Skin Scar', 'Solid State', 'Statistical Method', 'Testosterone', 'Therapeutic Procedure', 'Wellbeing']
#citation_author_institution
boring += ['Accounting', 'Amsterdam Business Research Institute', 'Amsterdam Movement Sciences', 'Amsterdam Neuroscience - Brain Imaging', 'Amsterdam Neuroscience - Cellular &amp; Molecular Mechanisms', 'Amsterdam Neuroscience - Complex Trait Genetics', 'Amsterdam Neuroscience - Compulsivity, Impulsivity &amp; Attention', 'Amsterdam Neuroscience - Mood, Anxiety, Psychosis, Stress &amp; Sleep', 'Amsterdam Neuroscience - Systems &amp; Network Neuroscience', 'Amsterdam Public Health', 'Animal Ecology', 'APH - Aging &amp; Later Life', 'APH - Global Health', 'APH - Health Behaviors &amp; Chronic Diseases', 'APH - Mental Health', 'APH - Methodology', 'APH - Quality of Care', 'APH - Societal Participation &amp; Health', 'Art and Culture, History, Antiquity', 'Artificial Intelligence (section level)', 'Artificial intelligence', 'Beliefs and Practices', 'Biological Psychology', 'Biophotonics and Medical Imaging', 'Biophysics Photosynthesis/Energy', 'Boundaries of Law', 'Cariology', 'Center for Neurogenomics and Cognitive Research', 'Civil Society and Philantropy (CSPh)', 'Clinical Developmental Psychology', 'Clinical Neuropsychology', 'Clinical Psychology', 'Cognitive Psychology', 'Communication Choices, Content and Consequences (CCCC)', 'Communication Science', 'Complex Trait Genetics', 'Computational Intelligence', 'Coordination Dynamics', 'Criminology', 'Dental Material Sciences', 'E&H: Environmental Bioanalytical Chemistry', 'E&H: Environmental Chemistry and Toxicology', 'E&H: Environmental Health and Toxicology', 'Earth and Climate', 'Earth Sciences', 'Economics', 'Educational and Family Studies', 'Educational Studies', 'Environmental Economics', 'Environmental Geography', 'Environmental Policy Analysis', 'Ethics, Governance and Society', 'EU Law', 'Faculty of Behavioural and Movement Sciences', 'Faculty of Humanities', 'Faculty of Law', 'Faculty of Religion and Theology', 'Faculty of Social Sciences', 'Filosofie van cultuur, politiek en organisatie', 'Finance', 'Functional Genomics', 'Geology and Geochemistry', 'Health Economics and Health Technology Assessment', 'High Performance Distributed Computing', 'Identities, Diversity and Inclusion (IDI)', 'Innovations in Human Health &amp; Life Sciences', 'Integrative Neurophysiology', 'Intellectual Property Law', 'Internet Law', 'Kooijmans Institute', 'Language, Literature and Communication', 'Language', 'LaserLaB - Biophotonics and Microscopy', 'LaserLaB - Molecular Biophysics', 'LEARN! - Child rearing', 'Literature', 'Management and Organisation', 'Mathematics', 'Maxillofacial Surgery (AMC)', 'Medicinal chemistry', 'Methodology and Applied Biostatistics', 'Migration Law', 'Mobilities, Beliefs and Belonging: Confronting Global Inequalities and Insecurities (MOBB)', 'Molecular and Cellular Neurobiology', 'Molecular and Computational Toxicology', 'Molecular Cell Physiology', 'Molecular Microbiology', 'Multi-layered governance in EUrope and beyond (MLG)', 'Network Institute', 'Neuromechanics', 'New Public Governance (NPG)', 'Nutrition and Health', 'Operations Analytics', 'Oral Cell Biology', 'Oral Implantology', 'Oral Kinesiology', 'Oral Public Health', 'Organic Chemistry', 'Organizational Psychology', 'Organization &amp; Processes of Organizing in Society (OPOS)', 'Organization Sciences', 'Periodontology', 'Philosophy, Politics and Economics', 'Philosophy', 'Physiology', 'Political Science and Public Administration', 'Preventive Dentistry', 'Public International Law', 'School of Business and Economics', 'Science &amp; Business Innovation', 'Secure and Liable Computer Systems', 'Sensorimotor Control', 'Social and Cultural Anthropology', 'Social Change and Conflict (SCC)', 'Social Inequality and the Life Course (SILC)', 'Social Law', 'Social Psychology', 'Sociology', 'Software and Sustainability (S2)', 'Spatial Economics', 'Structural Biology', 'Systems Bioinformatics', 'Systems Ecology', 'Texts and Traditions', 'Theoretical Chemistry', 'The Social Context of Aging (SoCA)', 'Tinbergen Institute', 'VU Business School', 'Water and Climate Risk', 'Youth and Lifestyle', 'AMS - Sports', 'BioAnalytical Chemistry', 'Epistemology and Metaphysics', 'Motor learning & Performance', 'Integrative Bioinformatics', 'BioAnalytical Chemistry', 'Physics of Living Systems', 'Amsterdam Centre for Family Law', 'APH - Health Behaviors &amp; Chronic Diseases', 'Art and Culture', 'Chemistry and Biology', 'Clinical Child and Family Studies', 'Criminal Law', 'Dutch Private Law', 'Educational Neuroscience', 'Family Law and the Law of Persons', 'Infectious Diseases', 'KIN Center for Digital Innovation', 'Legal Theory and Legal History', 'Prevention and Public Health', 'Research and Theory in Education', 'Systems and Network Security', 'Bioinformatics', 'Constitutional and Administrative Law', 'Epistemology and Metaphysics', 'Science &amp; Business Innovation', 'Tax Law', 'Business Web and Media', 'Geoarchaeology']

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
recs = []
for year in years:
    tocurl = 'https://research.vu.nl/en/publications/?type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput%2Fresearchoutputtypes%2Fthesis%2Fdoc1&nofollow=true&format=&publicationYear=' + str(year)
    ejlmod3.printprogress("=", [[year], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
    time.sleep(10)
    for li in tocpages[0].find_all('li', attrs = {'class' : 'search-pager-information'}):
        numoftheses = int(re.sub('\D', '', re.sub('.*of', '', li.text.strip())))
        print('  expecting %i theses' % (numoftheses))
        pages = 1 + (numoftheses-1) // rpp
    for page in range(pages-1):
        tocurl = 'https://research.vu.nl/en/publications/?type=%2Fdk%2Fatira%2Fpure%2Fresearchoutput%2Fresearchoutputtypes%2Fthesis%2Fdoc1&nofollow=true&format=&publicationYear=' + str(year) + '&page=' + str(page+1)
        ejlmod3.printprogress("=", [[year], [page+2, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
        time.sleep(10)
    rec = False
    for tocpage in tocpages:
        j = 0
        for ul in tocpage.body.find_all('ul', attrs = {'class' : 'list-results'}):
            for li in ul.find_all('li'):
                divs = li.find_all('div', attrs = {'class' : 'result-container'})
                for div in divs:
                    keepit = True
                    rec = {'tc' : 'T', 'note' : [], 'jnl' : 'BOOK', 'supervisor' : [],
                           'keyw' : [], 'isbns' : []}
                    #number of pages
                    for span in div.find_all('span', attrs = {'class' : 'numberofpages'}):
                        rec['pages'] = re.sub('\D', '', span.text.strip())
                    #link and title
                    for h3 in div.find_all('h3'):
                        for a in h3.find_all('a'):
                            rec['link'] = a['href']
                            rec['tit'] = a.text.strip()
                            rec['doi'] = '30.3000/VrijeUAmsterdam/' + re.sub('\W', '', a['href'])[41:]
                    #thesis type
                    for span in div.find_all('span', attrs = {'class' : 'type_classification_parent'}):
                        j += 1
                        thesistype = span.text.strip()
                        if not re.search('^PhD Thesis', thesistype):
                            rec['note'].append(thesistype)
                            if thesistype in boring:
                                ejlmod3.adduninterestingDOI(rec['doi'])
                        #"Finger print" concepts
                        for span in li.find_all('span', attrs = {'class' : 'concept'}):
                            concept = span.text.strip()
                            if not concept in rec['note']:
                                if concept in boring:
                                    ejlmod3.adduninterestingDOI(rec['doi'])
                                else:
                                    rec['note'].append(concept)
                        if ejlmod3.checkinterestingDOI(rec['doi']):
                            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                                prerecs.append(rec)
            print('  %4i records checked on this page' % (j))
        print('  %4i records so far' % (len(prerecs)))        

i = 0
for rec in prerecs:    
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [re.sub('.*\/', '../', rec['link'])], [len(recs)]])
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        continue
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['og:title', 'citation_author', 'citation_publication_date',
                                        'citation_pdf_url', 'citation_language', 'citation_keywords'])
    rec['autaff'][-1].append(publisher)
    #department
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_author_institution'}):
        department = meta['content']
        if department in boring:
            keepit = False
        elif not department in ['Faculty of Science']:
            rec['note'].append('DEP:'+department)
    for table in artpage.find_all('table', attrs = {'class' : 'properties'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #supervisor
                if tht == 'Supervisors/Advisors':
                    for span in td.find_all('strong'):
                        rec['supervisor'].append([re.sub(' \(.*', '', span.text.strip())])
                #ISBN
                elif tht == 'Print ISBNs':
                    for isbn in re.split(', *', td.text.strip()): 
                        rec['isbns'].append([('a', isbn), ('b', 'Print')])
                elif tht == 'Electronic ISBNs':
                    for isbn in re.split(', *', td.text.strip()): 
                        rec['isbns'].append([('a', isbn), ('b', 'Online')])
    #abstract
    for div in artpage.find_all('div', attrs = {'class' : 'content-content'}):
        div2 = div.find_all('div', attrs = {'class' : 'rendering'})[0]
        for h3 in div2.find_all('h2'):
            h3.decompose()
        rec['abs'] = div2.text
    if keepit:
        if skipalreadyharvested and rec['isbns'] and rec['isbns'][0][0][1] in alreadyharvested:
            print('    %s already in backup' % (rec['isbns'][0][0][1]))
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
