# -*- coding: utf-8 -*-
#harvest theses from Basel U.
#FS: 2019-10-25
#FS: 2022-12-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

pagestocheck = 30
publisher = 'Basel U. (main)'
jnlfilename = 'THESES-BASEL-%s' % (ejlmod3.stampoftoday())

reasonstoskip = []
for reason in ['Master Thesis', 'Faculty of Humanities and Social Sciences',
               'Faculty of Medicine', 'Faculty of Psychology']:
    reasonstoskip.append((reason, re.compile(reason)))
boring = ['Analytische Chemie', 'Applied Microbiology Research', 'Aquatische Ökologie',
          'Archäobotanik', 'Biochemistry', 'Biological clocks and timers in development',
          'Embryology and Stem Cell Biology', 'Gastroenterology DBM', 'Gynäkologie',
          'Molecular Genetics', 'Molekulare Pharmazie', 'Neuronal Development and Degeneration',
          'Organische Chemie', 'Pharmacology/Neurobiology', 'Pharmazeutische Biologie',
          'Pharmazeutische Technologie', 'Physical Hazards and Health', 'Regulatory Evolution',
          'Synthesis of Functional Modules', 'Ambulante innere Medizin', 'Anorganische Chemie',
          'Archäozoologie', 'Bioanalytical Microsystems', 'Bioanorganische Chemie', 'Bioinformatics',
          'Biophysikalische Chemie', 'Bio- und Medizinethik', 'Cancer- and Immunobiology',
          'Cancer Immunology and Biology', 'Cardiovascular Molecular Imaging', 'Cell Biology',
          'Cellular heterogeneity during collective cell behavior', 'Cellular Neurophysiology',
          'Chemische Physik', 'Childhood Leukemia', 'Clinical Pharmacology',
          'Clinical Statistics and Data Management', 'Datenbanken', 'Departement Biozentrum',
          'Developmental Genetics', 'Epidemiology and Transmission Dynamics', 'Evolutionary Biology',
          'Experimental Virology', 'Gender and Inequities', 'Gene regulation in chromatin',
          'Geochemie Stoffkreisläufe', 'Geoökologie', 'Health Impact Assessment',
          'Health Systems and Policy', 'Helminth Drug Development', 
          'Immunobiology', 'Immunodeficiency', 'Institut für Bildungswissenschaften',
          'International HIV and chronic disease care', 'Intervention Effectiveness and Impact',
          'Jüdische Geschichte und Kultur der Moderne', 'Klinische Pharmakologie',
          'Klinische Pharmazie/Spitalpharmazie', 'Labor', 'Liver Immunology',
          'Makromolekulare Chemie', 'Malaria Gene Regulation', 'Malaria Interventions',
          'Malaria Vaccines', 'Meteorologie', 'Molecular and Systems Toxicology',
          'Molecular Bionics', 'Molecular Devices and Materials', 'Molecular Diagnostics',
          'Molecular Microbiology', 'Molekulare Medizin', 'Molekulare Pathologie',
          'Motor circuit function', 'Nanobiology Argovia', 'Nano-diffraction of Biological Specimen',
          'Naturschutzbiologie', 'Non-coding RNAs and chromatin',
          'Nuclear organization in development and genome stability', 'One Health',
          'Ordinariat Privatrecht, insb. Arbeitsrecht',
          'Ordinariat Privatrecht, insb. schweizerisches und internationales Handels- und Wirtschaftsrecht',
          'Ordinariat Privatrecht, Rechtsvergleichung, internationales Handels- und Schiedsrecht',
          'Pädagogik', 'Pädiatrische Immunologie', 'Parasite Chemotherapy',
          'Pflanzenökologie und -evolution', 'Pharmaceutical Care', 'Pharmakologie',
          'Physiopathology of basal ganglia neuronal subcircuits', 'Psychopharmacology Research',
          'Regulatory Toxicology', 'Self-organizing cellular systems', 'Sensory processing and behaviour',
          'Stem Cell Biology', 'Structural Biology', 'Synthetic Systems', 'Synthetische Chemie',
          'Transcriptional and epigenetic networks and function of histone deacetylases in mammals',
          'Transcriptional mechanisms of topographic circuit formation', 'Tumor Biology',
          'Umweltgeowissenschaften', 'Urologie Kliniken BL', 'Air Pollution and Health',
          'Argovia Professur für Medizin', 'Artificial Intelligence', 
          'Biogeographie', 'Biomaterials Science Center', 'Biopharmazie', 'Brain and Sound',
          'Cellular mechanisms of learning and memory', 'Clinical Immunology',
          'Computational Chemistry', 'Departement Physik', 'Departement Umweltwissenschaften',
          'Dermatologie und Venerologie', 'Developmental Immunology',
          'Disease Modelling and Intervention Dynamics', 'Ehemalige Einheiten Pharmazie',
          'Endokrinologie, Diabetologie und Metabolismus',
          'Epigenetic control of mouse germ cell and early embryonic development',
          'Experimental Immunology', 'Exp. Transplantationsimmunologie und Nephrologie',
          'Genetic Epidemiology of Non-Communicable Diseases', 'Germanistische Linguistik',
          'Growth & Development', 'Health Systems and Policies', 'Helminths and Health',
          'Hepatologie', 'Hepatology Laboratory', 'High Performance and Web Computing',
          'Household Economy', 'Immunoregulation', 'Infection Biology', 'Klinische Endokrinologie',
          'Klinische Epidemiologie', 'Klinische Hausarztmedizin', 'Klinische Pharmazie',
          'Medicines Implementation Research', 'Molecular Immunology',
          'Molecular Parasitology and Epidemiology', 'Molekulare Neuroimmunologie', 'Nanomechanik',
          'Nanomedicine Research Group', 'Neuere Allgemeine Geschichte', 'Neural Networks',
          'Neurobiology', 'Neuronal circuits and brain function', 'New Vector Control Interventions',
          'Perioperative Patient Safety', 'Pflanzenökologie', 'Physiogeographie und Umweltwandel',
          'Physiological Plant Ecology', 'Plasticity of neuronal connections', 'Prenatal Medicine',
          'Professur Soziales Privatrecht', 'Radiologische Physik',
          'Sensory processing in the visual cortex', 'Structure and function of neural circuits',
          'Swiss Tropical and Public Health Institute', 'Synthetic Microbiology',
          'Theoretische Petrologie', 'Tissue Engineering', 'Translationale Komplementärmedizin',
          'Translationale Onkologie', 'Translational Immunology', 'Translational Neuroimmunology',
          'Tuberculosis Research', 'Tumorimmunologie']


tocurltrunc = 'https://edoc.unibas.ch/cgi/search/archive/advanced?screen=Search&cache=4845765&order=-date%2Fcreators_name%2Ftitle&_action_search=1&exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Cthesis_status%3Athesis_status%3AANY%3AEQ%3Acomplete%7Ctype%3Atype%3AANY%3AEQ%3Athesis%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow'
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
#check content pages
for i in range(pagestocheck):
    tocurl = '%s&search_offset=%i' % (tocurltrunc, 20*i)
    ejlmod3.printprogress("-", [[i+1, pagestocheck], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        keep = True
        for a in tr.find_all('a'):
            if re.search('edoc.unibas.ch\/\d\d', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                rec['artlink'] = a['href']
        for reason in reasonstoskip:
            if reason[1].search(tr.text):
                #print(' skip %s' % (reason[0]))
                keep = False
                break
        if keep and ejlmod3.checkinterestingDOI(rec['artlink']):
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

#check individual thesis pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    #first get author
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name'])
    #other metadata
    ejlmod3.metatagcheck(rec, artpage, ['eprints.contact_email', 'eprints.creators_orcid','eprints.title',
                                        'eprints.abstract', 'eprints.datestamp', 'eprints.keywords',
                                        'DC.identifier', 'eprints.pages', 'DC.rights', 'DC.language'])
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #table
    for tr in artpage.body.find_all('tr'):
        trs = tr.find_all('tr')
        if trs:
            continue
        for th in tr.find_all('th'):
            tht = th.text.strip()
            for td in tr.find_all('td'):
                #supervisor
                if tht == 'Advisors:':
                    for span in td.find_all('span'):
                        rec['supervisor'].append([span.text.strip()])
                        tht = ''
                #department
                elif tht == 'Faculties and Departments:':
                    dep = re.sub('.*> *', '', td.text.strip())
                    dep = re.sub(' *\(.*', '', dep)
                    if dep in boring:
                        keepit = False
                    elif dep in ['High Performance Computing', 'Computational Mathematics',
                                 'Computergraphik Bilderkennung', 'Computernetzwerke']:
                        rec['fc'] = 'c'
                    elif dep in ['Algebra', 'Analysis', 'Numerik']:
                        rec['fc'] = 'm'
                    elif dep in ['Experimentalphysik Quantenphysik', 'Quantum Physics']:
                        rec['fc'] = 'k'
                    elif dep in ['Theoretische Physik Astrophysik']:
                        rec['fc'] = 'a'
                    else:
                        rec['note'].append('DEP=' + dep)
                    tht = ''
    #upload PDF at least hidden
    if not 'FFT' in list(rec.keys()):
        for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.document_url'}):
            rec['hidden'] = meta2['content']
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
