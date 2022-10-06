# -*- coding: utf-8 -*-
#harvest theses from Nijmegen U.
#FS: 2022-09-30

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Nijmegen U.'

rpp = 100
pages = 4

hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-NIJMEGEN-%s' % (ejlmod3.stampoftoday())

boring= ["Clinical Pharmacy", "Health Evidence", "Paediatrics", "Rheumatology", "Surgery", "Anesthesiology",
         "Animal Ecology & Physiology", "Bedrijfskunde", "Bestuurskunde (leerstoel)", "Biochemistry (UMC)",
         "Business Economics", "Cardiology", "Cardio Thoracic Surgery", "Cell Biology (UMC)",
         "Center for Biblical and Theological Studies", "Cognitive Neuroscience", "Communicatie in Organisaties",
         "Cultuurgeschiedenis", "DCCN (FNWI)", "Dentistry", "Dermatology",  "Engelse Taalkunde",
         "Duitse Taal en Cultuur, inzonderheid Duitslandstudies", "Economie", "Faculteit der Rechtsgeleerdheid", 
         "Economische theorie en economisch beleid", "Emergency Medicine", "Empirische politicologie",
         "Financiële economie en ondernemingsfinanciering", "Gastroenterology", "Gynaecology", "Haematology",
         "Geografie, Planologie en Milieu", "Geschiedenis, Kunstgeschiedenis en Oudheid", "Geschiedenis", 
         "Human Genetics", "Intensive Care", "Internal Medicine", "Internationale Bedrijfscommunicatie",
         "Internationale economie", "IQ Healthcare", "Kunstgeschiedenis", "Laboratory Medicine",
         "Leerstoel Empirische en praktische religiewetenschap", "Leerstoel Geschiedenis van de filosofie",
         "Leerstoel Metafysica en filosofische antropologie",  "Leerstoel Vergelijkende Godsdienstwetenschappen",
         "Leerstoel Textuele, historische en systematische studies van het Jodendom en Christendom",
          "Leerstoel Wijsgerige ethiek en politieke filosofie", "Literatuurwetenschap en Cultuurwetenschap",
         "Medical Imaging", "Medical Microbiology", "Medical Oncology", "Medical Psychology", "Methoden",
         "Nederlandse Letterkunde", "Nederlandse Taal en Cultuur", "Nephrology", "Neurology", "Neurosurgery",
         "Onderzoekcentrum Onderneming & Recht (OO&R)", "Onderzoekcentrum voor Staat en Recht",
         "Operating Rooms", "Ophthalmology", "Oral and Maxillofacial Surgery", "Orthopaedics",
         "Otorhinolaryngology", "Oude en Middeleeuwse Geschiedenis", "Pathology", "Personeelsmanagement",
         "Pharmacology-Toxicology", "Physiology", "PI Group Affective Neuroscience",
         "PI Group Decision Neuroscience", "PI Group Intention & Action", "PI Group Memory & Emotion",
         "PI Group Motivational & Cognitive Control", "PI Group MR Techniques in Brain Function",
         "PI Group Neurobiology of Language", "PI Group Predictive Brain",  "Plastic Surgery", 
         "PI Group Statistical Imaging Neuroscience", "PI Group Visual Computation", "Planologie",
         "Politieke Geschiedenis", "Primary and Community Care", "Psychiatry", "Pulmonary Diseases",
         "Radboudumc Extern", "Radiation Oncology", "Rehabilitation", "Scanning Probe Microscopy",
         "Sociale geografie", "Spaanse Taal en Cultuur", "Strategie", "Taalwetenschap",
         "Theoretische Taalwetenschap", "Toegepaste Taalwetenschap", "Tumorimmunology", "Urology",
         "Werkplaats buitenpromovendi FFTR", "Action, intention, and motor control",
         "Anthropology and Development Studies", "Behaviour Change and Well-being", "Donders Thesis Series",
         "Experimental Psychopathology and Treatment", "ICS Dissertation Series",
         "Inequality, cohesion and modernization", "Learning and Plasticity", "MPI Series in Psycholinguistics",
         "Ongelijkheid, cohesie en modernisering", "Psycholinguistics", "Social Development",
         "Algemene Cultuurwetenschappen (ACW)", "Anatomy", "Auxilia, archeologisch projectbureau",
         "Bestuurskunde & Politicologie", "Bestuurskunde", "Bestuurskunde t/m 2019", "Biophysical Chemistry",
         "Central Animal Laboratory", "Centrum voor Notarieel Recht", "Engelse Taal en Cultuur", 
         "Centrum voor Parlementaire Geschiedenis (CPG)", "CLST - Centre for Language and Speech Technology", 
         "CLST_Centre for Language and Speech Technology", "Communicatie en Beïnvloeding",
         "Communicatie- en informatiewetenschappen", "Economische, Sociale en Demografische Geschiedenis",
         "external organisation", "Geriatrics", "Politicologie t/m 2019", "Radboud Docenten Academie", 
         "Griekse en Latijnse Taal en Cultuur (t/m 2018)", "Innovatiemanagement t/m 2013", "Innovation Studies",
         "Instituut voor Oosters Christendom (IvOC)", "Internationale betrekkingen", "Kunstgeschiedenis (t/m 2018)",
         "Laboratory of Genetic, Endocrine and Metabolic Diseases", "Radboud Universitair Medisch Centrum", 
         "Leerstoel Bronteksten van Jodendom en Christendom", "Leerstoel Filosofie van cognitie en taal",
         "Leerstoel Fundamentele filosofie", "Leerstoel Geschiedenis van het Christendom", "Leerstoel Islamstudies",
         "Leerstoel Praktische filosofie", "Leerstoel Systematische religiewetenschap", "Marketing",
         "Milieu maatschappijwetenschappen", "Organisatie-ontwikkeling", "Radiology",
         "Organismal Animal Physiology", "Paediatrics - OUD tm 2017", "PI Group Neuronal Oscillations", 
         "Taalbeheersing van het Nederlands", "Theoretical Chemistry",
         "Ultrafast Spectroscopy of Correlated Materials", "Bedevaarten in Nederland", "Categories Contested",
         "Center for Biblical and Theological Studies (CBTS)", "Center for Catholic Studies (CCS)",
         "Center for Cognition, Culture and Language (CCCL)", "Center for Contemporary European Philosophy (CCEP)",
         "Center for Political Philosophy and Ethics (CPPE)", "Center for Religion and Contemporary Society (CRCS)",
         "Centre for Notarial Law", "Cognitive artificial intelligence", "Communication and Media", "Company Law",
         "COMPAS: Creativity, Object, Materiality, and Practice of Art in Society",
         "Cultivating Creativity in Education", "DI-BCB_DCC_Theme 3: Plasticity and Memory", 
         "De liturgische feesten 'de tempore' en 'de sanctis' in het oude bisdom Kamerijk (ca. 1200-ca. 1500)",
         "De liturgische identiteit van de modene devoten, met bijzondere aandacht voor de Congregatie van Windesheim en het werk van Thomas van Kempen (1380-1471)",
         "Developmental Psychopathology", "DI-BCB_DCC_Theme 2: Perception, Action and Control",
         "DI-BCB_DCC_Theme 4: Brain Networks and Neuronal Communication", "Donders Center for Medical Neuroscience",
         "Donders Graduate School for Cognitive Neuroscience Series", "Donders series", "Donders Series",
         "EE-Network dissertation series", "Europe and its Worlds before 1800", "Europe in a Changing World",
         "Gender and Power in Politics and Management", "Work, Health and Performance",
         "Global-Local Divides and Connections (GLOCAL)", "Grammar & Cognition", "Innovation studies",
         "Institute for Management Research", "IPA Dissertation Series", "Language & Communication",
         "Language & Speech Technology", "Language and Crossmodal Correspondences",
         "Language and Speech, Learning and Therapy", "Language in Interaction", "Languages in Transition Stages",
         "Leaving Islam", "Meaning, culture and cognition",
         "Narrative health communication (ZonMw-project: Prevention and health regulation behaviour by understandable personal narratives)",
         "Nederlab", "Neuro- en revalidatiepsychologie", "Neuropsychology and rehabilitation psychology",
         "Non-nativeness in Communication", "Olfactory language and cognition in experts", "Ondernemingsrecht",
         "Persuasive Communication", "Project in ADNEXT (Commit)", "Radboud Group for Historical Demography and Family History",
         "Radboud Institute for Health Sciences", "Radboud Institute for Molecular Life Sciences",
         "Radboudumc 0: Other Research RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 0: Other ResearchRIHS: Radboud Institute for Health Sciences",
         "Radboudumc 10: Reconstructive and regenerative medicineRIHS: Radboud Institute for Health Sciences",
         "Radboudumc 10: Reconstructive and regenerative medicine", "Radboudumc 13: Stress-related disorders",
         "Radboudumc 13: Stress-related disorders DCMN: Donders Center for Medical Neuroscience",
         "Radboudumc 13: Stress-related disordersDCMN: Donders Center for Medical Neuroscience",         
         "Radboudumc 14: Tumours of the digestive tractRIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 14: Tumours of the digestive tract", "Radboudumc 15: Urological cancers",
         "Radboudumc 15: Urological cancersDonders Center for Medical Neuroscience",         
         "Radboudumc 16: Vascular damage RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 16: Vascular damage", "Radboudumc 17: Women's cancers RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 17: Women's cancersRIHS: Radboud Institute for Health Sciences", "Radboudumc 17: Women's cancers",
         "Radboudumc 18: Healthcare improvement science RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 18: Healthcare improvement science", "Radboudumc 1: Alzheimer`s disease",
         "Radboudumc 19: NanomedicineDCMN: Donders Center for Medical Neuroscience",
         "Radboudumc 19: NanomedicineRIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 19: Nanomedicine", "Radboudumc 1: Alzheimer`s disease DCMN: Donders Center for Medical Neuroscience",
         "Radboudumc 1: Alzheimer`s diseaseDCMN: Donders Center for Medical Neuroscience",
         "Radboudumc 1: Alzheimer`s disease RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 1: Alzheimer`s diseaseRIHS: Radboud Institute for Health Sciences",         
         "Radboudumc 3: Disorders of movement DCMN: Donders Center for Medical Neuroscience",
         "Radboudumc 3: Disorders of movement", "Radboudumc 4: lnfectious Diseases and Global Health",
         "Radboudumc 4: lnfectious Diseases and Global Health RIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 4: lnfectious Diseases and Global HealthRIMLS: Radboud Institute for Molecular Life Sciences",         
         "Radboudumc 5: Inflammatory diseases RIHS: Radboud Institute for Health Sciences",
         "Radboudumc 5: Inflammatory diseases RIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 5: Inflammatory diseases", "Radboudumc 6: Metabolic Disorders",
         "Radboudumc 6: Metabolic Disorders RIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 6: Metabolic DisordersRIMLS: Radboud Institute for Molecular Life Sciences",         
         "Radboudumc 7: Neurodevelopmental disordersRIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 7: Neurodevelopmental disorders",  "Transnational Europe", "Variation and Distance", 
         "Radboudumc 9: Rare cancersRIHS: Radboud Institute for Health Sciences",
         "Radboudumc 9: Rare cancers", "Research Programm of Donders Centre for Neuroscience",
         "The Ancient World", "Theologie en Cultuur. Transdisciplinaire Perspectieven", "The Seventies",
         "The silent nose: Determining the mechanisms behind our poor ability to name odors",
         "The study of olfactory language and cognition across diverse cultures, as well as within specialist communities such as perfumiers and wine-tasters (Vici)",
         "Analytical Chemistry", "Aquatic Ecology and Environmental Biology", "Bioinformatics", "Biomolecular Chemistry",
         "Bio-organic Chemistry", "Biophysics", "Cell biology", "Department for Sustainable Management of Resources",
         "Donders Centre for Cognitive Neuroimaging", "Donders Centre for Neuroscience", "Duitse Taal en Cultuur",
         "Ecological Microbiology", "Environmental Science", "Experimental Plant Ecology",
         "Faculteit der Managementwetenschappen", "Faculty of Philosophy", "Faculty of Theology",
         "F.C. Donders Centre for Cognitive Neuroimaging", "FELIX Molecular Structure and Dynamics",
         "FSW_Institute for Gender Studies (IGS)", "Laboratory of Hematology", "Laboratory of Medical Immunology",
         "LOT: Landelijke Onderzoekschool Taalwetenschap", "Molecular and Biophysics", "Molecular Animal Physiology",
         "Molecular Biology", "Molecular Materials", "Molecular Plant Physiology", "Molecular Structure and Dynamics",
         "Neuroinformatics", "Nuclear Medicine", "Philosophy and Science Studies", "Physical Chemistry/Solid State NMR",
         "Physical Organic Chemistry", "Plant Genetics", "Proteomics and Chromatin Biology",
         "Research Institute for Philosophy, Theology & Religious Studies", "Romaanse Talen en Culturen/Spaans",
         "Solid State Chemistry", "Solid State NMR", "Spectroscopy of Solids and Interfaces", "Synthetic Organic Chemistry",
         "110 000 Neurocognition of Language", "110 003 Autism & depressions", "110 003 Autism & depression",
         "150 000 MR Techniques in Brain Function", "160 000 Neuronal Oscillations",
         "170 000 Motivational & Cognitive Control", "Animal Ecology and Physiology", "Aquatic Ecology",
         "Bio-Molecular Chemistry", "Bio-Organic Chemistry", "Biophysics", "Cell Biology",
         "Cognition, Interpretation and Context",
         "Creoles at birth? The role of nativization in language formation (Veni)",
         "Das Niederländische aus der Sicht Hoffmanns von Fallersleben: Die Bewahrung einer Vergangenheit",
         "DCN PAC - Perception action and control", "Department of Sustainable Management of Resources",
         "Developments in the languages of Surinam (Traces of Contact)",
         "Distributional Conflicts in a Globalizing World: Consequences for State-Market-Civil Society Arrangements",
         "Donders Graduate School for Cognitive Neuroscience series",
         "Donders Graduate School for Cognitive Neuroscience", "Donders series publications", "Dynamics of gender",
         "Environmental Sciences", "Europe and its Worlds after 1800", "IGMD 1: Functional imaging",
         "IGMD 6: Hormonal regulationONCOL 5: Aetiology, screening and detection", "IPA dissertation series",
         "Language in Society", "Languages in Contact", "LOT Publications",
         "Mechanisms and constraints in biodiversity conservation and restoration",
         "Memory, Materiality and Meaning in the Age of Transnationalism", "Molecular Biology",
         "Molecular Structure and Dynamics", "MPI series in psycholinguistics",
         "N4i 4: Auto-immunity, transplantation and immunotherapy NCMLS 2: Immune Regulation",
         "N4i 4: Auto-immunity, transplantation and immunotherapyNCMLS 2: Immune Regulation",
         "NCEBP 9: Mental health", "NCMLS 2: Immune Regulation ONCOL 3: Translational research",
         "NCMLS 2: Immune RegulationONCOL 3: Translational research",
         "NCMLS 4: Energy and redox metabolismIGMD 8: Mitochondrial medicine",
         "NCMLS 4: Energy and redox metabolism", "NCMLS 6: Genetics and epigenetic pathways of disease",
         "NCMLS 7: Chemical and physical biology", "Neuroinformatics",
         "ONCOL 3: Translational research NCMLS 2: Immune Regulation",
         "ONCOL 3: Translational researchNCMLS 2: Immune Regulation", "Mediated communication",
         "Onderzoeksprogramma Religiewetenschappen", "Philosophy and Science Studies", "Plant Ecology",
         "Radboudumc 2: Cancer development and immune defence RIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 2: Cancer development and immune defenceRIMLS: Radboud Institute for Molecular Life Sciences",
         "Radboudumc 5: Inflammatory diseasesRIMLS: Radboud Institute for Molecular Life Sciences",
         "Research Program in Religious Studies", "Spectroscopy of Cold Molecules", 
         "Research Programme of Radboud Institute for Molecular Life Sciences", "Responsible Organization",
         "Studien zur Geschichte und Kultur Nordwesteuropas", "Studying Criticism And Reception Across Borders",
         "Traces of contact: Language contact studies and historical linguistics",
         "Neurophysiology", "Cellular Animal Physiology", "Laboratory of Clinical Chemistry",
         "IGMD 7: Iron metabolismN4i 1: Pathogenesis and modulation of inflammation",
         "Planologie, ihb lokale en reg. ruimtelijke beleid", "Werkplaats Buitenpromovendi Religiewetenschappen",
         "Werkplaats Buitenpromovendi Religiewetenschappen", "Orthodontics and Oral Biology",
         "Arabisch en Islam", "Cellular Animal Physiology", "Ethics, Philosophy, History of Medical Sciences",
         "General Internal Medicine", "Instituut voor Leraar en School (ILS)", "Laboratory of Clinical Chemistry",
         "Medical Informatics", "Neurophysiology", "Orthodontics and Oral Biology",
         "Planologie, ihb lokale en reg. ruimtelijke beleid", "Radboud universitair medisch centrum",
         "Werkplaats Buitenpromovendi Religiewetenschappen", "Werkplaats Buitenpromovendi Theologie",
         "Wiskunde en Natuurwetenschappen", "aminozuren, peptiden, eiwitten",
         "Biblical Studies, Ancient Judaism, Early Christianity, and Gnosticism", "Bloedstolling",
         "Chromogeen substraat assay", "De professionele ontwikkeling van leraren",
         "Developing normativity in education", "Digital Security", "EBP 2: Effective Hospital Care",
         "Euresource. Religious Sources of Solidarity", "Fotochemie",
         "IGMD 7: Iron metabolismN4i 1: Pathogenesis and modulation of inflammation",
         "IPA Dissertation series", "Islam in beweging", "Mediated communication",
         "Missie en Multiculturaliteit", "Missionary Work and Multiculturality",
         "N4i 1: Pathogenesis of the inflammatory response",  "Onderzoeksprogramma Theologie",
         "NCEBP 2: Evaluation of complex medical interventions", "NCEBP 5: Health care ethics",
         "NCEBP 7: Effective primary care and public health", "NCMLS 1: Immunity, infection and tissue repair",
         "organische verbindingen: overige", "Reframing Spirituality and Mysticism in Past and Present",
         "Religious Identity Transformation in Context", "Research Program in Theology",
         "Shaping and Changing of Places and Spaces", "Sulfinen", "The Dynamics of Islamic Culture",
         "The professional development of teachers", "Trombine", "Vinylstilbenen"]

prerecs = []
for page in range(pages):
    tocurl = 'https://repository.ubn.ru.nl/handle/2066/30204/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=type&value=Dissertation&order=DESC'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://repository.ubn.ru.nl')
    time.sleep(5)

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.abstract', 'DC.identifier', 'DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'citation_pdf_url', 'citation_isbn'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
    for div in artpage.body.find_all('div', attrs = {'class' : 'item-page-field-wrapper'}):
        for h5 in div.find_all('h5'):
            #department
            if re.search('Organization', h5.text):
                for div2 in div.find_all('div'):
                    orga = div2.text.strip()
                    if orga in boring:
                        keepit = False
                    elif orga in ['Theoretical High Energy Physics']:
                        rec['fc'] = 'pt'
                    elif orga in ['Astrophysics', 'Astronomy']:
                        rec['fc'] = 'a'
                    elif orga in ['Soft Condensed Matter and Nanomaterials',
                                  'Soft Condensed Matter & Nanomaterials',
                                  'FELIX Condensed Matter Physics',
                                  'Semiconductors and Nanostructures',
                                  'Condensed Matter Science (HFML)',
                                  'Correlated Electron Systems',
                                  'Theory of Condensed Matter']:
                        rec['fc'] = 'f'
                    elif orga in ['Experimental High Energy Physics']:
                        rec['fc'] = 'e'
                    elif orga in ['Software Science',
                                  'ICIS - Institute for Computing and Information Sciences']:
                        rec['fc'] = 'c'
                    elif orga in ['Mathematics', 'Algebra & Topologie',
                                  'Algebra and Logic', 'Algebra and Topology',
                                  'Applied Mathematics', 'Mathematical Physics']:
                        rec['fc'] = 'm'
                    elif not 'SUBJ:'+orga in rec['note']:
                        if not 'fc' in rec:
                            rec['note'].append('ORGA:'+orga)
            #subject
            elif re.search('Subject', h5.text):
                for div2 in div.find_all(['div', 'span']):
                    subjs = re.split(' *; *', re.sub('[\n\t\r]', '', div2.text.strip()))
                    for subj in subjs:
                        if subj in boring:
                            keepit = False
                        elif not 'ORGA:'+subj in rec['note']:
                            if not 'fc' in rec:
                                rec['note'].append('SUBJ:'+subj)
            #pages
            elif re.search('Number of pages', h5.text):
                for div2 in div.find_all('div'):
                    divt = re.sub('[\n\t\r]', '', div2.text.strip())
                    if re.search('\d\d', divt):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', divt)
            elif re.search('Annotation', h5.text):
                for div2 in div.find_all('div'):
                    divt = re.sub('[\n\t\r]', '', div2.text.strip())
                    divt = re.sub(' *Co.promotor.*', '', divt)
                    if re.search('(Promoter|Promotores) *:', divt):
                        proms = re.split(', ', re.sub('(Promoter|Promotores) *: *', '', divt)                        )
                        if len(proms) % 2 == 0:
                            for j in range(len(proms)//2):
                                rec['supervisor'].append([proms[2*j] + ', ' + proms[2*j+1]])
    if keepit:            
        recs.append(rec)        
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
