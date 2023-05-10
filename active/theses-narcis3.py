# -*- coding: utf-8 -*-
#harvest theses from NARCIS
#FS: 2019-09-15

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'NARCIS'
jnlfilename = 'THESES-NARCIS-%s' % (ejlmod3.stampofnow())
bunchlength = 1000

boringpublishers = ['Biomedical Signals and Systems; TechMed Centre',
                    'TechMed Centre; Biomedical Signals and Systems',
                    'LOT', 'Building Materials',
                    'International and European Law; RS: FdR Institute MCEL',
                    'RS: GROW - R2 - Basic and Translational Cancer Biology; Precision Medicine',
                    'RS: GSBE other - not theme-related research; Marketing & Supply Chain Management',
                    'A+BE | Architecture and the Built Environment', 'ACS - Atherosclerosis & ischemic syndromes; Cardiology',
                    'Adult Psychiatry; Amsterdam Neuroscience - Compulsivity, Impulsivity & Attention; Graduate School',
                    'AII - Infectious diseases; AII - Inflammatory diseases; Amsterdam Reproduction & Development (AR&D); Paediatric Intensive Care',
                    'AII - Infectious diseases; APH - Global Health; Graduate School', 'AII - Infectious diseases; Graduate School',
                    'AII - Inflammatory diseases; Rheumatology', 'AIMMS; Systems Bioinformatics', 'AIMMS; Theoretical Chemistry',
                    'AMS - Rehabilitation & Development; IBBA; Motor learning & Performance',
                    'AMS - Rehabilitation & Development; Physiology', 'Amsterdam Neuroscience - Brain Imaging; Integrative Neurophysiology',
                    'Amsterdam Neuroscience - Compulsivity, Impulsivity & Attention; Adult Psychiatry; Graduate School',
                    'Amsterdam Neuroscience - Compulsivity, Impulsivity & Attention; Amsterdam Neuroscience - Brain Imaging; Adult Psychiatry; Graduate School',
                    'Amsterdam Neuroscience - Neurodegeneration; Amsterdam Neuroscience - Cellular & Molecular Mechanisms; Molecular and Cellular Neurobiology',
                    'Amsterdam Neuroscience - Neurodegeneration; Neurology', 'Amsterdam Reproduction & Development (AR&D); AII - Cancer immunology; Graduate School',
                    'Amsterdam Reproduction & Development (AR&D); AII - Infectious diseases; AII - Inflammatory diseases; Graduate School',
                    'AMS - Tissue Function & Regeneration; Plastic, Reconstructive and Hand Surgery', 'Analytical Biochemistry',
                    'Anatomy and neurosciences; VU University medical center', 'Anesthesiology', 'APH - Digital Health; APH - Mental Health',
                    'APH - Global Health; Amsterdam Neuroscience - Mood, Anxiety, Psychosis, Stress & Sleep; APH - Mental Health; Graduate School',
                    'APH - Personalized Medicine; Biological Psychology', 'APH - Quality of Care; Plastic, Reconstructive and Hand Surgery',
                    'APH - Societal Participation & Health; VU University medical center', 'Applied Economics', 'Art and Culture, History, Antiquity; CLUE+',
                    'Astronomy', 'Automotive Systems Design', 'Beliefs and Practices; CLUE+', 'Beliefs and Practices',
                    'Biochemie; RS: Carim - B03 Cell biochemistry of thrombosis and haemostasis', 'Biochemie',
                    'Biomedical Engineering and Physics; ACS - Microcirculation; Amsterdam Neuroscience - Brain Imaging; ACS - Atherosclerosis & ischemic syndromes; Amsterdam Neuroscience - Neurovascular Disorders; Graduate School',
                    'Biotechnology', 'Brein en Cognitie (Psychologie, FMG)', 'Building Acoustics', 'Building Performance',
                    'Cardiologie; RS: Carim - H05 Gene regulation', 'Cardiology; ACS - Atherosclerosis & ischemic syndromes', 'Cardiology',
                    'Cardiothoracic Surgery', 'CBITE; RS: MERLN - Cell Biology - Inspired Tissue Engineering (CBITE)', 'CCA - Cancer Treatment and quality of life; Hematology',
                    'CCA - Imaging and biomarkers; ACS - Atherosclerosis & ischemic syndromes; Graduate School', 'Cell biology',
                    'Cell-Matrix Interact. Cardiov. Tissue Reg.; Modeling in Mechanobiology',
                    'Cell-Matrix Interact. Cardiov. Tissue Reg.',
                    'CentER, Center for Economic Research', 'Center for Care & Cure Technology Eindhoven; Eindhoven MedTech Innovation Center; Signal Processing Systems',
                    'Chemical Biology 1', 'Chemical Process Intensification', 'Clinical Pharmacy; RS: CAPHRI - R5 - Optimising Patient Care',
                    'Clinical Psychology and Experimental Psychopathology', 'Cognitive Neuropsychology', 'Cognitive Science & AI',
                    'Communication Choices, Content and Consequences (CCCC); Network Institute; Communication Science',
                    'Communication Science; Communication Choices, Content and Consequences (CCCC); Network Institute',
                    'CTR; RS: MERLN - Complex Tissue Regeneration (CTR)', 'Cultural Sociology (AISSR, FMG)', 'Delft : IHE Delft, Institute for Water Education',
                    'Department Cognitive Science and Artificial Intelligence', 'Department Communication and Cognition', 'Department of Arts and Culture Studies',
                    'Department of Clinical Psychology; RS-Research Line Clinical psychology (part of UHC program)', 'Department of Culture Studies',
                    'Department of Earth Observation Science; UT-I-ITC-ACQUAL; Faculty of Geo-Information Science and Earth Observation; Digital Society Institute',
                    'Department of History', 'Department of Philosophy', 'Department of Psychology, Education and Child Studies', 'Department of Tax Law',
                    'Design Engineering', 'Developmental Psychology', 'Deventer : Wolters Kluwer', 'Device Physics of Complex Materials',
                    'Discrete Technology and Production Automation', 'Drug Design', 'Economics; Amsterdam Centre for World Food Studies',
                    'Economics; Tinbergen Institute', 'Educational Research and Development; RS: GSBE other - not theme-related research',
                    'ELAN Teacher Development', 'Empirical and Normative Studies; A-LAB; Criminology', 'Entrepreneurship, Technology, Management',
                    'Environmental Economics', 'Environmental Geography', 'Enzymology', 'Epidemiologie', 'Epidemiology and Data Science',
                    'Epidemiology', 'Erasmus School of Social and Behavioural Sciences', 'Ethics, Governance and Society; APH - Quality of Care',
                    'Faculteit der Geneeskunde', 'Faculteit Economie en Bedrijfskunde', 'Faculty of Arts', 'Faculty of Economics and Business', 'Faculty of Religion and Theology',
                    'Family Medicine; RS: CAPHRI - R5 - Optimising Patient Care', 'FdR overig onderzoek', 'Finance; RS: GSBE other - not theme-related research',
                    'Finance; Tinbergen Institute', 'Functional Genomics; Amsterdam Neuroscience - Cellular & Molecular Mechanisms',
                    'Future Everyday', 'Gastroenterology & Hepatology', 'General practice', 'General Practice',
                    'Genetica & Celbiologie; RS: GROW - R2 - Basic and Translational Cancer Biology', 'Global Health; Graduate School',
                    'Governance and Inclusive Development (GID, AISSR, FMG)', 'Graduate School; APH - Mental Health; APH - Personalized Medicine; Medical Psychology',
                    'Graduate School; Infectious diseases', 'Graduate School; Ophthalmology', 'Graduate School; Radiotherapy', 'Health & Food',
                    'Health promotion; RS: CAPHRI - R6 - Promoting Health & Personalised Care', 'Health Sciences; APH - Mental Health',
                    'Health Services Management & Organisation (HSMO)', 'Health Services Research; RS: CAPHRI - R1 - Ageing and Long-Term Care',
                    'Health Technology & Services Research; TechMed Centre', 'Health Technology Assessment (HTA)', 'Hematology',
                    'History; RS: FASoS MUSTS', 'History; RS: FASoS PCE', 'Humane Biologie; RS: NUTRIM - R1 - Obesity, diabetes and cardiovascular health',
                    'Humanist Chaplaincy Studies for a plural society; A meaningful life in a just and caring society', 'IBBA; Cognitive Psychology',
                    'IBED Other Research (FNWI)', 'ILLC (FGw); Faculteit der Geesteswetenschappen',
                    'ILLC (FGw); Logic and Language (ILLC, FNWI/FGw); Faculteit der Geesteswetenschappen', 'Immunoengineering',
                    'Industrial Engineering & Business Information Systems; Digital Society Institute', 'Industrial Engineering & Business Information Systems',
                    'Innovation Technology Entrepr. & Marketing', 'Inorganic Materials & Catalysis',
                    'Institute for Logic, Language and Computation', 'Institutions, Inequalities, and Life courses (IIL, AISSR, FMG)',
                    'Integrated Research on Energy, Environment & Socie', 'Integrative Neurophysiology; Amsterdam Neuroscience - Cellular & Molecular Mechanisms',
                    'Internal Medicine; Medical Informatics', 'Internal Medicine',
                    'Jewish, Christian and Islamic Origins', 'Klassieke en mediterrane archeologie',
                    'KNO; RS: GROW - R2 - Basic and Translational Cancer Biology', 'Language, Communication and Cognition',
                    'LaserLaB - Biophotonics and Microscopy; LaserLaB - Physics of Light', 'LaserLaB - Energy; Biophysics Photosynthesis/Energy',
                    'Law and Economics', 'Law, Markets and Behavior; Intellectual Property Law; Network Institute',
                    'LEARN! - Child rearing; LEARN! - Brain, learning and development; Clinical Developmental Psychology',
                    'LEARN! - Educational neuroscience, learning and development; IBBA; Clinical Developmental Psychology',
                    'LEARN! - Learning sciences; Educational Studies', 'Maastricht Graduate School of Governance; RS: GSBE MGSoG',
                    'Macromolecular Chemistry & New Polymeric Materials', 'Macro-Organic Chemistry',
                    'Management and Organisation; Amsterdam Business Research Institute', 'Marketing; Amsterdam Business Research Institute',
                    'Maxillofacial Surgery (AMC + VUmc)', 'Medical and Clinical Psychology',
                    'Medical Microbiology and Infection Prevention; APH - Quality of Care; AII - Infectious diseases',
                    'Medical Oncology', 'Medicinal chemistry; AIMMS', 'Membrane Materials and Processes',
                    'MESA+ Institute; Biomedical and Environmental Sensorsystems', 'MESA+ Institute; Catalytic Processes and Materials',
                    'MESA+ Institute; Inorganic Materials Science', 'MESA+ Institute; Membrane Science & Technology',
                    'Microeconomics (ASE, FEB)', 'Microsystems; Group Wyss',
                    'Migration Law; Kooijmans Institute; Migration Law',
                    'Molecular cell biology and Immunology; ACS - Microcirculation; Amsterdam Neuroscience - Neuroinfection & -inflammation; Amsterdam Neuroscience - Neurovascular Disorders',
                    'Molecular Cytology (SILS, FNWI)', 'Molecular Genetics', 'Molecular Pharmacology',
                    'Multi-Modality Medical Imaging', 'MUMC+: DA CDL Algemeen (9); RS: Carim - B01 Blood proteins & engineering',
                    'MUMC+: MA AIOS Heelkunde (9); RS: GROW - R3 - Innovative Cancer Diagnostics & Therapy; Plastische Chirurgie (PLC)',
                    'MUMC+: MA Medische Staf Obstetrie Gynaecologie (9); RS: GROW - R4 - Reproductive and Perinatal Medicine; Obstetrie & Gynaecologie',
                    'Nanoscopy for Nanomedicine; Molecular Biosensing for Med. Diagnostics', 'Network Institute; Language', 'Neurology',
                    'Neurosciences', 'New Public Governance (NPG); Political Science and Public Administration',
                    'Obstetrics and Gynaecology; CCA - Cancer Treatment and Quality of Life; APH - Societal Participation & Health; APH - Quality of Care; Amsterdam Reproduction & Development (AR&D); Graduate School',
                    'Ophthalmology', 'Oral Biochemistry', 'Oral Cell Biology', 'Organisation,Strategy & Entrepreneurship; RS: GSBE other - not theme-related research',
                    'Organization Sciences; Organization & Processes of Organizing in Society (OPOS); Network Institute', 'Orthopaedic Biomechanics',
                    'Orthopedics and Sports Medicine', 'Otorhinolaryngology and Head and Neck Surgery', 'Pathology',
                    'PDEng Data Science Support', 'Pediatrics', 'Pediatric surgery; CCA - Quality of life', 'Pediatric surgery', 'Pharmaceutical Analysis',
                    'PharmacoTherapy, -Epidemiology and -Economics', 'Physical Chemistry', 'Political Economy and Transnational Governance (PETGOV, AISSR, FMG)',
                    'Political Science and Public Administration; New Public Governance (NPG)', 'Polymer Chemistry and Bioengineering',
                    'Power & Flow; Group Bastiaans; Group Deen', 'Power & Flow; Group Deen', 'Power & Flow; Group Van Oijen',
                    'Power Electronics Lab; Electromechanics and Power Electronics', 'Precision Medicine; RS: GROW - R3 - Innovative Cancer Diagnostics & Therapy',
                    'Preventive Youth Care (RICDE, FMG)', 'Printsupport4U', 'Private Law; RS: FdR Institute M-EPLI',
                    'Private Law', 'Process and Product Design', 'Products and Processes for Biotechnology', 'Psychiatry',
                    'Psychologische Methodenleer (Psychologie, FMG)', 'Public Administration', 'Public and occupational health; APH - Mental Health',
                    'Public and occupational health; APH - Personalized Medicine', 'Public Law & Governance', 'Pulmonologie; RS: NUTRIM - R3 - Respiratory & Age-related Health',
                    'Radiology & Nuclear Medicine', 'Radiology and nuclear medicine', 'Radiotherapy; CCA - Cancer Treatment and Quality of Life; CCA - Imaging and biomarkers; Graduate School',
                    'Research & Education', 'Research Methods and Techniques', 'RS: CAPHRI - R1 - Ageing and Long-Term Care; Health Services Research',
                    'RS: CAPHRI - R2 - Creating Value-Based Health Care; Health Services Research',
                    'RS: CAPHRI - R3 - Functioning, Participating and Rehabilitation; Epidemiologie',
                    'RS: CAPHRI - R3 - Functioning, Participating and Rehabilitation; Orthopedie',
                    'RS: CAPHRI - R6 - Promoting Health & Personalised Care; Family Medicine',
                    'RS: Carim - B04 Clinical thrombosis and Haemostasis; MUMC+: HVC Pieken Trombose (9); Interne Geneeskunde',
                    'RS: Carim - B06 Imaging', 'RS: Carim - B07 The vulnerable plaque: makers and markers', 'RS: Carim - V04 Surgical intervention; CTC',
                    'RS: Carim - V04 Surgical intervention', 'RS: FASoS WTMC', 'RS: FdR IC Rechtsbescherming; RS: FdR not Institute related',
                    'RS: FdR Institute METRO; RS: FdR; Maastr Inst for Transnat Legal Research', 'RS: FPN CPS IV; Section Forensic Psychology',
                    'RS: FPN M&S I; FPN Methodologie & Statistiek', 'RS: FPN WSP II; Section Applied Social Psychology',
                    'RS: FSE AMIBM; AMIBM', 'RS: FSE UCV', 'RS: GROW - R2 - Basic and Translational Cancer Biology',
                    'RS: GROW - R3 - Innovative Cancer Diagnostics & Therapy; Dermatologie',
                    'RS: GROW - R3 - Innovative Cancer Diagnostics & Therapy; Epidemiologie',
                    'RS: GROW - R3 - Innovative Cancer Diagnostics & Therapy',
                    'RS: GSBE other - not theme-related research; Educational Research and Development',
                    'RS: GSBE other - not theme-related research; Finance',
                    'RS: GSBE other - not theme-related research; ROA / Education and transition to work',
                    'RS: GSBE Studio Europa Maastricht; RS: GSBE MGSoG; Maastricht Graduate School of Governance',
                    'RS: MERLN - Complex Tissue Regeneration (CTR); RS: GROW - R4 - Reproductive and Perinatal Medicine; Metamedica',
                    'RS: MHeNs - R3 - Neuroscience', 'RS: NUTRIM - R3 - Respiratory & Age-related Health; Nutrition and Movement Sciences',
                    'Science Education and Communication', 'Section Applied Social Psychology; RS: FPN WSP II', 'Section Forensic Psychology; RS: FPN CPS IV',
                    'Social AI; Network Institute; Computer Systems', 'Social Psychology', 'Sociology', 'Stimuli-responsive Funct. Materials & Dev.',
                    'Studio', 'Surfaces and Thin Films', 'Surgery', 'Surgery; VU University medical center', 'Sustainable Process Technology',
                    'Synthetic Organic Chemistry (HIMS, FNWI)', 'Synthetic Organic Chemistry', 'Systemic Change', 'Systems, Control and Applied Analysis', 'Tax Law; RS: FdR Institute MCT',
                    'Texts and Traditions; CLUE+', 'Theoretical Philosophy', 'Thermal Engineering', 'Thermo-Chemical Materials Lab; Transport in Permeable Media',
                    'TILT', 'Transboundary Legal Studies', 'Transnational Configurations, Conflict and Governance (AISSR, FMG)',
                    'Transport Engineering and Management; Digital Society Institute', 'Transport in Permeable Media; Thermo-Chemical Materials Lab',
                    'Tranzo, Scientific center for care and wellbeing', 'University of Humanistic Studies; A meaningful life in a just and caring society',
                    'Urban Planning and Transportation', 'Urologie; RS: MHeNs - R3 - Neuroscience', 'Urology',
                    'Verslaving; Tranzo, Scientific center for care and wellbeing', 'Video Coding & Architectures; Mobile Perception Systems Lab', 'Virology',
                    'VUmc - School of Medical Sciences', 'VU University medical center', 'Water and Climate Risk', 'Youth & Media Entertainment (ASCoR, FMG)',
                    'AIMMS; Medicinal chemistry', 'Biophotonics and Medical Imaging; LaserLaB - Biophotonics and Microscopy',
                    'Center for Neurogenomics and Cognitive Research; Amsterdam Neuroscience - Neurodegeneration; Amsterdam Neuroscience - Cellular & Molecular Mechanisms',
                    'Clinical Genetics', 'Department of Geo-information Processing; UT-I-ITC-ST Faculty of Geo-Information Science and Earth Observation',
                    'Ethics, Law & Medical humanities; APH - Societal Participation & Health', 'Faculty of Behavioural and Movement Sciences',
                    'Genetic Identification', 'Management and Organisation', 'Medical Microbiology & Infectious Diseases',
                    'Membrane Science & Technology; MESA+ Institute', 'Multi-Modality Medical Imaging; TechMed Centre',
                    'Nanobiophysics; MESA+ Institute; TechMed Centre',
                    'Nutrition and Movement Sciences; RS: NUTRIM - R1 - Obesity, diabetes and cardiovascular health',
                    'Photocatalytic Synthesis; MESA+ Institute', 'Product-Market Relations',
                    'RS: Carim - V03 Regenerative and reconstructive medicine vascular disease; Vascular Surgery',
                    'RS: GROW - R4 - Reproductive and Perinatal Medicine; Obstetrie & Gynaecologie',
                    'School of Med. Physics and Eng. Eindhoven; EngD School AP; Eindhoven MedTech Innovation Center',
                    'Surgical Robotics', 'Sustainable Process Engineering; Inorganic Membranes and Membrane Reactors',
                    'University of Twente, Faculty of Geo-Information Science and Earth Observation (ITC)',
                    'Amsterdam Interdisciplinary Centre for Emotion (AICE, Psychology, FMG)',
                    'Analytical Chemistry and Forensic Science (HIMS, FNWI)',
                    'Cardiologie; RS: Carim - H05 Gene regulation; RS: Carim - Blood', 'Civil Law',
                    'Corporate Communication (ASCoR, FMG)', 'Periodontology', 'Preventive Dentistry',
                    'Department of Technology Enhanced Learning and Innovation; RS-Theme Open Education',
                    'Endodontology', 'Epidemiologie; RS: GROW - R1 - Prevention',
                    'Family Medicine; RS: CAPHRI - R5 - Optimising Patient Care; Family Medicine',
                    'Freshwater and Marine Ecology (IBED, FNWI)', 'Groninger Instituut voor Archeologie',
                    'Homogeneous and Supramolecular Catalysis (HIMS, FNWI)', 'Integrated Circuit Design',
                    'Maxillofacial Surgery (AMC); Oral Kinesiology', 'Maxillofacial Surgery (AMC); Oral Medicine',
                    'Mechanics of Materials; Group Hoefnagels', 'Neurosurgery', 'Optima Grafische Communicatie',
                    'Orale Kinesiologie (ORM, ACTA)', 'Oral Kinesiology; Orthodontics', 'Oral Kinesiology',
                    'Oral Public Health', 'Orthopedie; RS: CAPHRI - R3 - Functioning, Participating and Rehabilitation',
                    'RS: CAPHRI - R3 - Functioning, Participating and Rehabilitation',
                    'RS: CAPHRI - R4 - Health Inequities and Societal Participation; Med Microbiol, Infect Dis & Infect Prev',
                    'RS: CAPHRI - R4 - Health Inequities and Societal Participation; Sociale Geneeskunde',
                    'RS: Carim - B03 Cell biochemistry of thrombosis and haemostasis',
                    'RS: FdR IC Const. proc. rechtsorde; International and European Law; RS: FdR Institute MCfHR',
                    'RS: FdR Institute METRO; Maastr Inst for Transnat Legal Research',
                    'Sustainable Chemistry Industrial (HIMS, FNWI)']
boringkeywords = ['Anxiety', 'Aquaculture and Fisheries', 'Aquacultuur en Visserij', 'biomarkers',
                  'Bio Process Engineering', 'Business Management & Organisation', 'Case study',
                  'circulaire economie', 'circular economy', 'Depression', 'duurzaamheid',
                  'Food Process Engineering', 'human rights', 'Immunotherapy', 'Inflammation',
                  'Laboratorium voor Geo-informatiekunde en Remote Sensing',
                  'Laboratory of Geo-information Science and Remote Sensing',
                  'LOT dissertation series', 'mensenrechten', 'Microbiologie', 'Microbiology',
                  'Parenting', 'physical activity', 'Physical therapy', 'refugees', 'room 0.710',
                  'Systeem en Synthetische Biologie', 'Systems and Synthetic Biology',
                  'systems biology', 'Tuberculosis', 'vluchtelingen', 'Water Resources Management',
                  'Baggage Handling Systems', 'Cancer', 'Development Economics',
                  'ERIM PhD Series Research in Management', 'Global Nutrition',
                  'Laboratorium voor Plantenveredeling', 'Ontwikkelingseconomie', 'Plant Breeding',
                  'sustainability', 'Wereldvoeding', 'climate change', 'Kennis',
                  'MPI series in Psycholinguistics', 'SDG 3 - Good Health and Well-being',
                  'Glomerulosclerosis', 'Proteinuria', 'Renal disease']
boringinsts = ['Faculty of Medicine, Leiden University Medical Center (LUMC) Leiden University',
               'Department of Social Psychology', 'Institute for Globalisation and International Regulation',
               'Institute of Security and Global Affairs , Faculty of Governance and Global Affairs , Leiden University',
               'Vascular Surgery', 'Obstetrie & Gynaecologie',
               'Leiden Academic Centre for Drug Research (LACDR) , Faculty of Science , Leiden University',
               'Leiden University Institute for History , Faculty of Humanities , Leiden University',
               'Beukeboom lab - Evolutionary Genetics', 'CAPHRI - Functioning, Participating and Rehabilitation',
               'Carim - Blood', 'Carim - Cell biochemistry of thrombosis and haemostasis', 'Civil Law',
               'Department of Technology Enhanced Learning and Innovation',
               'Eisel lab - Molecular Neurobiology and Neuroimmunology', 'Endodontology',
               'Engineering Fluid Dynamics', 'Etienne group - Theoretical and Evolutionary Community Ecology',
               'Faculty of Archaeology , Leiden University', 'Groningen Institute of Archeology', 
               'Faculty of Medicine, Leiden University Medical Center (LUMC) , Leiden University', 'Family Medicine',               
               'Institute of Biology Leiden (IBL) , Faculty of Science , Leiden University',
               'Institute of Political Science , Faculty of Social and Behavioural Sciences , Leiden University',
               'Institute of Public Administration , Faculty of Governance and Global Affairs , Leiden University',
               'Institute of Public Law , Faculty of Law , Leiden University', 'Sociale Geneeskunde',
               'Leiden Institute of Chemistry (LIC) , Faculty of Science , Leiden University',
               'Leiden Institute of Education and Child Studies , Faculty of Social and Behavioural Sciences , Leiden University',
               'Maastricht Centre for Human Rights', 'Maastr Inst for Transnat Legal Research',
               'Med Microbiol, Infect Dis & Infect Prev', 'Neurosurgery', 'Oral Kinesiology', 'Oral Medicine',
               'Oral Public Health', 'Orthodontics', 'Periodontology', 'Preventive Dentistry', 'Psychometrics and Statistics']
#check individual pages of bunch of records
def processrecs(recs, bunchcounter):
    i = 0
    recs = []
    for rec in prerecs:
        keepit = True
        uni = 'unknown'
        i += 1
        ejlmod3.printprogress('-', [[bunchcounter], [i, len(prerecs)], [rec['artlink']], [len(recs)]])
        #req = urllib2.Request(rec['artlink'], headers=hdr)    
        #artpage = BeautifulSoup(urllib2.urlopen(req))
        artfilename = '/tmp/THESES-NARCIS_%s' % (re.sub('\W', '', rec['artlink']))
        if not os.path.isfile(artfilename):
            os.system('wget -q -T 300 -O %s "%s"' % (artfilename, rec['artlink']))
            time.sleep(5)
        inf = open(artfilename, 'r')
        artpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
        inf.close()
        ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_dissertation_institution', 'citation_abstract',
                                            'citation_publication_date', 'citation_title', 'citation_language'])
        for table in artpage.find_all('table', attrs = {'class' : 'size02'}):
            for tr in table.find_all('tr'):
                for th in tr.find_all('th'):
                    tht = th.text.strip()
                for td in tr.find_all('td'):
                    tdt = td.text.strip()
                if tht == 'Reference(s)':
                    rec['keyw'] = re.split(', ', tdt)
                    for kw in rec['keyw']:
                        if kw in boringkeywords:
                            print('   skip "%s"' % (kw))
                            keepit = False
                elif tht == 'ISBN':
                    isbns = re.split(' *; *', tdt)
                    rec['isbns'] = [[('a', re.sub('\-', '', isbn))] for isbn in isbns]
                elif re.search('DOI$', tht):
                    rec['doi'] = re.sub('.*doi.org\/', '', tdt)
                elif re.search('Handle$', tht):
                    rec['hdl'] = tdt
                elif re.search('NBN$', tht):
                    rec['urn'] = tdt
                elif tht == 'Persistent Identifier':
                    if tdt[:4] in ['urn', 'URN']:
                       rec['urn'] = tdt
                elif tht == 'Thesis advisor':
                    rec['supervisor'] = [[sv] for sv in re.split('; *', tdt)]
                elif tht == 'Publication':
                    for a in td.find_all('a'):                        
                        rec['link'] = a['href']
                        if not 'hdl' in list(rec.keys()) and not 'doi' in list(rec.keys()):
                            if re.search('\/handle\/\d', rec['link']):
                                rec['hdl'] = re.sub('.*handle\/', '', rec['link'])
                elif tht == 'Publisher':
                    realpublisher = tdt
                    if realpublisher in boringpublishers:
                        print('   skip "%s"' % (realpublisher))
                        keepit = False
                    else:
                        rec['note'].append('publisher:::'+tdt)
        if 'link' in list(rec.keys()):
            print('  try to get PDF from %s' % (rec['link']))
            try:
                req = urllib.request.Request(rec['link'], headers=hdr)
                origpage = BeautifulSoup(urllib.request.urlopen(req))
                ejlmod3.metatagcheck(rec, origpage, ['citation_pdf_url', 'citation_isbn', 'citation_doi'])
                institution = False
                for dl in origpage.find_all('dl', attrs = {'title' : 'Awarding Institution'}):
                    for dd in dl.find_all('dd'):
                        institution = dd.text.strip()
                if not institution:
                    for li in origpage.find_all('dl', attrs = {'class' : 'department'}):
                        institution = li.text.strip()    
                if not institution:
                    for a in origpage.find_all('a', attrs = {'rel' : 'Organisation'}):
                        institution = a.text.strip()    
                if not institution:
                    prev = ''
                    for dl in origpage.find_all('dl', attrs = {'id' : 'metadata'}):
                        for child in dl.childen:
                            try:
                                if prev == 'Faculty':
                                    institution = child.text
                                else:
                                    prev = child.text
                            except:
                                pass
                if institution:
                    institution = re.sub('  +', ' ', re.sub('[\n\r\t]', ' ', institution))
                    #print('   INSTITUTION:::'+institution)
                    if institution in boringinsts:
                        keepit = False
                        print('   skip "%s"' % (institution))
                    else:
                        rec['note'].append('INSTITUTION:::'+institution)
            except:
                print('    could not find PDF')
            if not 'FFT' in list(rec.keys()):
                rec['link'] = rec['artlink']
        if not 'doi' in list(rec.keys()) and not 'isbn' in list(rec.keys()) and not 'urn' in list(rec.keys()) and not 'hdl' in list(rec.keys()):
            rec['doi'] = '20.2001/NARCIS/' + re.sub('\W', '', rec['artlink'])
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['artlink'])
    ejlmod3.writenewXML(recs, publisher, '%s_%03i' % (jnlfilename, bunchcounter))
    return

                                            
#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2))]
redoki = re.compile('THESES.NARCIS.*doki$')
rehttp = re.compile('^I\-\-(http.*id).*')
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
                        http = regenre.sub('', rehttp.sub(r'\1', line.strip()))
                        if not http in bereitsin:
                            if not http in nochmal:
                                bereitsin.append(http)
                                http2 = re.sub(':', '%3A', http)
                                if http2 != http:
                                    bereitsin.append(http)
            print('  %6i %s' % (len(bereitsin), datei))

hdr = {'User-Agent' : 'Magic Browser'}

#there is not set for doctoral theses on OAI-PMH.
#  tocurl = 'http://oai.tudelft.nl/ir/oai/oai2.php?verb=ListRecords&metadataPrefix=nl_didl&from=' + startdate + '&until=' + stopdate
#would give too many results
prerecs = []
pages = 0
pagestotal = 0
bunchcounter = 0
ntarget = 0
for year in [str(ejlmod3.year()), str(ejlmod3.year(backwards=1))]:
    page = 0
    complete = False
    while not complete:
        tocurl = 'https://www.narcis.nl/search/coll/publication/Language/EN/genre/doctoralthesis/dd_year/' + year + '/pageable/' + str(page)
        ejlmod3.printprogress('=', [[page+1, pages], [len(prerecs), 10*pagestotal, ntarget], [tocurl]])
        try:
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print('wait 5 minutes')
            time.sleep(300)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for h1 in tocpage.body.find_all('h1', attrs = {'class' : 'search-results'}):
            target = re.sub('.*of (\d.*\d).*', r'\1', h1.text.strip())
            ntarget = int(re.sub('\D', '', target))
            pages = (ntarget-1) // 10 + 1
        for div in tocpage.body.find_all('div', attrs = {'class' : 'search-results'}):
            for div2 in div.find_all('div', attrs = {'class' : 'search-options'}):
                div2.replace_with('')
            for li in div.find_all('li'):
                for a in li.find_all('a'):
                    if a.has_attr('href'):
                        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'oa' : False}
                        rec['artlink'] = 'https://www.narcis.nl' + a['href']
                        rec['identifier'] = re.sub('.*ecordID\/', '', rec['artlink'])
                        rec['identifier'] = re.sub('%3A', ':', rec['identifier'])
                        rec['identifier'] = re.sub('%2F', '/', rec['identifier'])
                        rec['identifier'] = regenre.sub('', rec['identifier'])
                        rec['tit'] = re.sub(' \(\d\d\d\d\)$', '', a.text.strip())
                        rec['note'] = [ rec['artlink'], '%i of %i' % (len(prerecs) + 1, ntarget) ]
                        for img  in li.find_all('img', attrs = {'class' : 'open-access-logo'}):
                            rec['oa'] = True
                    ihttp = re.sub('(.*id).*', r'\1', rec['artlink'])
                    if regenre.sub('', ihttp) in bereitsin:
                        #print('   skip %s' % (rec['artlink']))
                        pass
                    elif ejlmod3.checkinterestingDOI(rec['identifier']) and ejlmod3.checkinterestingDOI(rec['artlink']):
                        prerecs.append(rec)
                        bereitsin.append(ihttp)
        time.sleep(10)
        page += 1
        pagestotal += 1
        if len(prerecs) >= ntarget or 10*page >= ntarget:
            complete = True
        if len(prerecs) >= bunchlength:
            processrecs(prerecs, bunchcounter)
            bunchcounter += 1
            prerecs = []
if len(prerecs) < bunchlength:
    processrecs(prerecs, bunchcounter)



        


