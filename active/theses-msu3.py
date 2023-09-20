# -*- coding: utf-8 -*-
#harvest theses from Michigan State U.
#FS: 2023-08-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Michigan State U.'
jnlfilename = 'THESES-MichiganStateU-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 10
skipalreadyharvested = True
boring = ['Biomedical Engineering', 'Biosystems Engineering', 'Business Administration - Operations and Sourcing Management',
          'Chemical Engineering', 'Chemistry', 'Civil Engineering', 'Communication', 'Criminal Justice',
          'Crop and Soil Sciences', 'Educational Psychology and Educational Technology', 'English', 'Epidemiology',
          'Fisheries and Wildlife', 'Geography', 'Higher, Adult, and Lifelong Education', 'History', 'Human Nutrition',
          'Human Resources and Labor Relations-Doctor of Philosophy', 'Integrative Biology', 'Kinesiology',
          'Mathematics Education', 'Mechanical Engineering', 'Microbiology and Molecular Genetics', 'Music Education',
          'Packaging', 'Pharmacology and Toxicology', 'Economics', 'Pathology','Planning, Design and Construction',
          'Biology', 'Plant Biology', 'Political Science', 'Psychology', 'Rhetoric and Writing', 'School Psychology',
          'Special Education', 'Agricultural, Food and Resource Economics', 'Animal Science- Doctor of Philosophy',
          'Anthropology', 'Biochemistry and Molecular Biology', 'Business Administration - Accounting',
          'Business Administration -Finance', 'Business Administration - Strategic Management',
          'Comparative Medicine and Integrative Biology', 'Curriculum, Instruction, and Teacher Education', 'Economics',
          'Educational Policy', 'Entomology', 'Environmental Engineering', 'Fisheries and Wildlife - Environmental Toxicology',
          'Forestry', 'Human Development and Family Studies', 'Information and Media', 'Agricultural Economics',
          'K-12 Educational Administration', 'Microbiology - Environmental Toxicology',
          'Plant Breeding, Genetics and Biotechnology - Plant Biology', 'Plant Pathology', 'Biostatistics',
          'Business Administration -Business Information Systems', 'Business Administration', 'Food Science',
          'Business Administration -Logistics', 'Business Administration-Marketing-Doctor of Philosophy',
          'Business Administration - Organization Behavior - Human Resource Management', 'Cell and Molecular Biology',
          'Community Sustainability-Doctor of Philosophy', 'Food Science-Environmental Toxicology', 'Genetics',
          'Geological Sciences', 'Hispanic Cultural Studies', 'Horticulture', 'Information and Media--Doctor of Philosophy',
          'Linguistics', 'Nursing', 'Pharmacology and Toxicology-Environmental Toxicology', 'Philosophy', 'Physiology',
          'Plant Breeding, Genetics and Biotechnology - Crop and Soil Sciences', 'Rehabilitation Counselor Education',
          'Second Language Studies', 'Sociology', 'Zoology', 'African American and African Studies',
          'Agricultural, Food and Resource Economics - Master of Science', 'American Studies', 'Chicano/Latino Studies',
          'Biochemistry and Molecular Biology-Environmental Toxicology', 'Industrial Relations and Human Resources',
          'Business Administration - Organization Behavior - Huamn Resource Management', 'Strategic Management',
          'Cell and Molecular Biology - Environmental Toxicology', 'Chemistry - Environmental Toxicology',
          'Communicative Sciences and Disorders', 'Educational Administration', 'Educational Leadership - Doctor of Education',
          'Engineering Mechanics', 'Environmental Geosciences', 'German Studies', 'Large Animal Clinical Sciences',
          'Media and Information Studies', 'Media and Information',  'Fisheries and Wildlife - Environmental Toxicology',
          'Music Conducting', 'Neuroscience - Environmental Toxicology', 'Pathobiology', 'Pharmacology & Toxicology',
          'Plant Breeding, Genetics and Biotechnology - Horticulture', 'Sustainable Tourism and Protected Area Management',
          'French, Language and Literature', 'Neuroscience', 'Genetics - Environmental Toxicology', 'Social Work',
          'Crop and Soil Sciences- Environmental Toxicology', 'Community, Agriculture, Recreation and Resource Studies',
          'Pathobiology-Environmental Toxicology', 'Ecology, Evolutionary Biology and Behavior - Dual Major',
          'Accounting and Information Systems', 'Advertising', 'Agriculture & Natural Resources Education and Communication Systems',
          'Agriculture and Natural Resources Education and Communication Systems', 'Animal Science',
          'Audiology and Speech Sciences', 'Biosystems and Agricultural Engineering', 'Botany and Plant Pathology',
          'Cell and Molecular Biology Program', 'Center for Systems Integration and Sustainability, Fisheries and Wildlife',
          'Chemical Engineering and Material Science', 'Chemical Engineering and Materials Science',
          'Civil and Environmental Engineering', 'Community, Agriculture, Recreation and Resources',
          'Counseling and Educational Psychology', 'Counseling, Educational Psychology & Special Education',
          'Counseling, Educational Psychology and Special Education', 'Counseling, Educational Psychology, and Special Education',
          'Counseling, Education Psychology and Special Education', 'Counsiling, Educational Psychology and Special Education',
          'Crop & Soil Science', 'Crop and Soil Sciences and Environmental Toxicology Programs, Crop and Soil Sciences',
          'Crop and Soil Sciences, Plant Breeding and Genetics Program', 'Curriculum Teaching and Education Policy',
          'Education Administration', 'Educational Administration Higher, Adult, and Lifelong Education', 'Educational Psychology',
          'Education', 'Family and Child Ecology', 'Family and Human Ecology', 'Finance',
          'Fisheries and Wildlife and Program in Ecology, Evolutionary Biology and Behavior', 'Food Science and Human Nutrition',
          'Forestry; Ecology, Evolutionary Biology, and Behavior Program',
          'Forestry, Program in Ecology, Evolutionary Biology, and Behavior', 'Genetics Program', 'Graduate Education',
          'Higher, Adult, and Lifelong Education. Educational Administration', 'Higher, Adult and Lifelong Education',
          'Higher, Adult, Learning and Education (i.e. Educational Administration. Higher, Adult, and Lifelong Education',
          'Human Ecology', 'Human Environment and Design', 'Human Environment: Design and Management', 'K-12 Administration Education',
          'Learning, Culture, and Technology', 'Linguistics and Germanic, Slavic, Asian and African Languages',
          'Linguistics and Germanic, Slavic, Asian, and African Languages',
          'Linguistics, and Germanic, Slavic, Asian, and African Languages', 'Marketing and Supply Chain Management', 'Mass Media',
          'Materials Science and Mechanics', 'Measurement and Quantitative Methods', 'Music', 'Neuroscience Program',
          'Park, Recreation and Tourism Resources', 'Parks, Recreation, and Tourism Resources',
          'Pathobiology and Diagnostic Investigation', 'Plant Biology Program in Ecology, Evolutionary Biology, and Behavior',
          'Plant Biology, Program in Ecology, Evolutionary Biology, and Behavior, W.K. Kellogg Biological Station',
          'Plant Breeding and Genetics - Forestry', 'Plant Breeding and Genetics Program and Horticulture',
          'Program in Cell and Molecular Biology', 'Psychology and Criminal Justice', 'Resource Development and Urban Studies',
          'Resource Development, Institute of Environmental Toxicology', 'Resource Development', 'Sociology and Urban Affairs Programs',
          'Spanish and Portuguese', 'Teacher Education', 'Accounting', 'African American and African Studies History',
          'Agricultural, Food, and Resource Economics', 'Biochemistry and Molecular Biology and Chemistry',
          'Biochemistry and Molecular Biology - Environmental Toxicology', 'Business Information Systems',
          'Chemical Engineering and Biochemistry & Molecular Biology', 'Communication Arts and Sciences - Media and Information Studies',
          'Communications Arts and Sciences, Media and Information Studies', 'Community, Agriculture, Recreation, and Resource Studies',
          'Computer Science, Ecology, Evolutionary Biology, and Behavior', 'Computer Science; Ecology, Evolutionary Biology and Behavior',
          'Construction Management', 'Counseling Psychology', 'Crop and Soil Sciences and Ecology, Evolutionary Biology, and Behavior',
          'Crop and Soil Sciences - Environmental Toxicology', 'Crop and Soil Science', 'Curiculum, Instruction, and Teacher Education',
          'Curriculum, Instruction and Teacher Education', 'Curriculum, Teaching, & Educational Policy',
          'Curriculum, Teaching, and Educaional Policy', 'Curriculum, Teaching and Educational Policy ; Sociology',
          'Curriculum, Teaching and Educational Policy', 'Curriculum, Teaching, and Education al Policy',
          'Curriculum, Teaching, and Educational Policy', 'Curriculum, Teaching, and Education Policy', 'Economics Finance',
          'Educational Leadership', 'Entomology and Ecology, Evolutionary Biology and Behavior', 'Family & Child Psychology',
          'Fisheries and Wildlife - Ecology, Evolutionary Biology and Behavior', 'Food Science - Environmental Toxicology',
          'French Language and Literature', 'Geological Science', 'Higher Adult and Lifelong Education',
          'Higher, Adult, and Life-Long Education', 'Human Resources and Labor Relations', 'Labor & Industrial Relations',
          'Literature in English', 'Logistics', 'Marketing', 'Microbiology - Enviromental Toxicology', 'Music Performance',
          'Operations and Sourcing Management', 'Organizational Behavior/Human Resource Management',
          'Organizational Behavior--Human Resources Management', 'Orginazational Behavior - Human Resource Management',
          'Park, Recreation, and Tourism Resources', 'Pathology and Environmental Toxicology',
          'Pharmacology and Toxicology - Environmental Toxicology', 'Plant Biology, Ecology, Evolutionary Biology & Behavior',
          'Plant Biology, Ecology, Evolutionary Biology, and Behavior', 'Plant Biology; Ecology, Evolutionary Biology and Behavior',
          'Plant Breeding & Genetics--Horticulture', 'Plant Breeding and Genetics, Crop and Soil Sciences',
          'Psychology, Ecology, Evolutionary Biology, and Behavior', 'Resource Development-Environmental Toxicology', 'Retailing',
          'Telecomunication, Information Studies and Media', 'Zoology and Ecology, Evolutionary Biology and Behavior',
          'Zoology ; Ecology, Evolutionary Biology, and Behavior', 'Zoology, Ecology, Evolutionary Biology and Behavior',
          'Zoology, Ecology, Evolutionary Biology, and Behavior', 'Zoology-Environmental Toxicology',
          'Adverising, Public Relations and Retailing', 'Advertising, Journalism, and Telecommunication and Mass Media Program',
          'Advertising, Public Relations and Retailing', 'Advertising, Public Relations, and Retailing',
          'Agricultural Economics, Economics', 'Agricultural Economics. Economics', 'Agricultural Engineering',
          'Agriculture and Extension Education', 'American Studies Program', 'Animal Science and Environmental Toxicology',
          'ANR Education and Communication Systems', 'Arts and Communication',
          'Botany and Plant Pathology and Program in Ecology, Evolutionary Biology and Behavior',
          'Chemical Engineering & Materials Science', 'Chemistry & Biochemistry and Molecular Biology',
          'Chemistry and Center for Integrative Toxicology', 'Chemistry and Chemical Engineering & Material Science',
          'Chemistry and Chemical Engineering & Materials Science', 'Civil and Environment Engineering',
          'Comparative Medicine and Integrative Biology, Pathobiology and Diagnostic Investigation',
          'Counseling, Educational Psychology, & Special Education', 'Counseling/Educational Psychology and Special Education',
          'Crop and Soil Sciences Center of Integrated Toxicology', 'Depts. of Agricultural Economics and Economics',
          'Crop and Soil Sciences, Ecology, Evolutionary Biology, and Behavior Program', 'Dept of Chemistry',
          'Dept of Comparative Medicine and Integrative Biology Graduate Program',
          'Dept of Counseling, Educational Psychology and Special Education', 'Dept of Crop & Soil Science',
          'Dept of Educational Administration. Higher, Adult and Lifelong Education', 'Dept of Epidemiology',          
          'Dual Major, Kinesiology; Counseling, Educational Psychology, and Special Education', 'Educational Administration. Higher, Adult, and Lifelong Education',
          'Education Higher, Adult, Lifelong Education', 'Education, K-12 Educational Administration',
          'Education Policy, Education', 'Education. School Administration', 'Electrical and Computer Engineering',
          'Entomology and Program in Ecology, Evolutionary Biology & Behavior', 'Family & Child Ecology',
          'Fisheries & Wildlife, Ecology, Evolutionary Biology, and Behavior Program',
          'Fisheries and Wildlife and Program in Ecology, Evolutionary Biology, and Behavior',
          'Fisheries and Wildlife Ecology, Evolutionary Biology, and Behavior Program',
          'Fisheries and Wildlife; Ecology, Evolutionary Biology, and Behavior Program',
          'Food Science and Human Nutrition and Institute for Environmental Toxicology',
          'Food Science and Human Nutrition, Center for Integrative Toxicology',
          'Food Sciences and Human Nutrition, Institute of Environmental Toxicology', 'Food Sciences',
          'French, Classics, and Italian', 'Genetics Graduate Program and Graduate Program in Cell and Molecular Biology',
          'Genetics Graduate Program', 'Graduate Program in Biochemistry and Molecular Biology', 'Graduate Program in Genetics',
          'Higher, Adult, & Lifelong Education', 'Higher, Adult, and Lifelong Education Educational Administration',
          'Higher, Adult, and Lifelong Education (HALE', 'Higher and Lifelong Education',
          'Hispanic Cultural Studies, Spanish and Portuguese', 'Horticulture/Plant Breeding and Genetics', 'Journalism',
          'Large Animal Clinical Sciences (Epidemiology', 'Linguistics & Germanic, Slavic, Asian, & African Languages',
          'Linguistics and German, Slavic, Asian, and African Languages', 'Microbiology & Molecular Genetics',
          'Linguistics, Germanic, Slavic, Asian, and African Languages', 'Management', 'Mass Media Ph. D. Program', 'Mechanical',          
          'Microbiology and Molecular Genetics, Program in Ecology, Evolutionary Biology and Behavior', 'Musicology',
          'Park, Recreation and Tourism Research', 'Parks, Recreation and Tourism Resources',
          'Pathobiology and Diagnostic Investigaion', 'Plant Biology and Program in Ecology, Evolutionary Biology, and Behavior',
          'Plant Biology, Program in Ecology, Evolutionaly Biology & Behavior',
          'Plant Biology, Program in Ecology, Evolution and Behavioral Biology',
          'Plant Biology, Program in Ecology, Evolutionary Biology, and Behavior', 'Plant Breeding and Genetics - Horticulture',
          'Plant Breeding and Genetics Program Crop and Soil Sciences',
          'Plant Breeding and Genetics Program, Crop and Soil Sciences', 'Plant Breeding and Genetics Program, Horticulture',
          'Plant Breeding and Genetics Program', 'Plant Breeding and Genetics', 'Probability and Statistics',
          'Program in American Studies', 'Program in Genetics', 'Rhetoric and Writing Program', 'Social Science',
          'Sociology and Urban Studies', 'Telecommunication, Information Studies and Media',
          'Telecommunication, Information Studies, and Media', 'Telecommunications, Information Studies and Media',
          'Telecommunication', 'Veterinary Medicine', 'W.K. Kellogg Biological Station and Zoology',
          'W.K. Kellogg Biological Station. Zoology and Ecology, Evolutionary Biology & Behavior Program',
          'W.K. Kellogg Biological Station, Zoology and Ecology, Evolutionary Biology, and Behavior Program',
          'Zoology and Center for Integrated Toxicology', 'Zoology and Ecology, Evolutionary Biology, and Behavior Program',
          'Zoology and Program in Ecology, Evolutionary Biology and Behavior and Center for Integrative Toxicology',
          'Zoology and the Ecology, Evolutionary Biology, and Behavior Program',
          'Zoology, Ecology, Evolutionary Biology, and Behavior Program',
          'Zoology. Program in Ecology, Evolutionary Biology & Behavior',
          'Zoology. Program in Ecology, Evolutionary Biology & Behavior. W.K. Kellogg Biological Station',
          'Zoology Program in Ecology, Evolutionary Biology, and Behavior',
          'Zoology. Program in Ecology, Evolutionary Biology and Behavior',
          'Zoology. Program in Ecology, Evolutionary Biology, and Behavior', 'Accounting and Information Studies',
          'Advertising, Public Relations, & Retailing Specialized in Retailing', 'Advertising, Public Relations & Retailing',
          'African History', 'Agricultural and Extension Education', 'Agricultural and Natural Resource',
          'Agricultural Economics and Economics', 'Agricultural Engineering, Civil and Environmental Engineering',
          'Agriculture and Natural Resources, Education and Communication Systems',
          'Agriculture Natural Resources Education & Communication Systems', 'Animal Science - Environmental Toxicology',
          'Anthropolgy', 'Arts and Letters, Program in American Studies', 'Biochemistry & Molecular Biology',
          'Biochemistry and Molecular Biology, Chemistry', 'Biosystem Engineering', 'Building Construction Management',
          'Chemical Engineering & Materials Science and Chemistry', 'Chemistry and Biochemistry & Molecular Biology',
          'Chemistry, Biochemistry and Molecular Biology', 'Chemisty', 'Child and Family Ecology',
          'Civil & Environmental Engineering', 'Communicatinos Arts & Sciences, Mass Media Ph. D. Program',
          'Communication Arts & Science - Media & Information Studies', 'Communication Arts & Sciences',
          'Communication Arts and Sciences, Mass Media Program', 'Communication Arts and Sciences, Mass Media',
          'Communication Arts and Sciences', 'Communications Arts and Sciences',
          'Comparative Medicine and Integrative Biology--Environmental Toxicology', 'Comparative Medicine and integrative Biology',
          'Counseling Educational Psychology and Special Education', 'Counseling Educational Psychology, and Special Education',
          'Counseling, Education Psychology, and Special Education', 'Counseling, Education, Psychology and Special Education',
          'Crop and Soil Sciences--Environmental Toxicology', 'Crops and Soil Sciences',
          'Curriculum, Instruction and Educational Policy', 'Curriculum, Teaching & Educational Policy',
          'Curriculum Teaching, and Educational Policy', 'Curriculum, Teaching, and Educational Policy, Teacher Education',
          'Curriculum, Teaching, and Educational Policy. Teacher Education',
          'Dept of Agriculture and Natural Resources Education and Communication Systems',
          'Dept of Food Science and Human Nutrition', 'Dept of Higher, Adult, Lifelong Education',
          'Depts. of Biosystems and Agricultural Engineering and Civil and Environmental Engineering',
          'Depts. of Kinesiology and Epidemiology', 'Division of Anatomy and Structural Biology, Radiology',
          'Educational Administration, Education', 'Educational Administration K-12',
          'Educational Psychology & Educational Technology', 'Education, Higher Adult and Lifelong Education (H.A.L.E',
          'Education Policy', 'Education, Teacher Education', 'Engineering Mechanics in Mechanical Engineering',
          'Entomology and Program in Ecology, Evolutionary Biology and Behavior',
          'Entomology and Program in Ecology, Evolutionary Biology, and Behavior',
          'Entomology and the Program in Ecology, Evolutionary Biology, and Behavior', 'Family Studies',
          'Fisheries and Wildlife, and Ecology, Evolutionary Biology, and Behavior',
          'Fisheries and Wildlife. Ecology, Evolutionary Biology, and Behavior Graduate Program',
          'Fisheries and Wildlife, Ecology, Evolutionary Biology, and Behavior',
          'Fisheries and Wildlife, Program in Ecology, Evolutionary Biology, and Behavior', 'Food Scienc and Human Nutrition',
          'Food Science & Human Nutrition and Institute of Environmental Toxicology', 'Food Science & Human Nutrition',
          'Food Science and Environmental Toxicology', 'Food Science and Human Nutrition, Institute of Environmental Toxicology',
          'Forestry Ecology, Evolutionary Biology, and Behavior', 'Forestry / Plant Breeding and Genetics',
          'Forestry Program in Ecology, Evolutionary Biology and Behavior', 'French, Classics and Italian',
          'Geological Sciences and Biosystems and Agricultural Engineering', 'Higher, Adult, and Lifelong Educational Administration',
          'Higher, Adult, and Lifelong Education Program', 'Higher, Adult, and Life Long Education',
          'Higher, Adult, Lifelong Education', 'History-Urban Studies', 'Human Environment: Design Management', 'Human Pathology',
          'Industrial/Organizational Psychology', 'K-12 Education Administration, Education Administration',
          'K-12 Education Administration', 'K 12 Educational Administration', 'Kinesiology and Psychology', 'Kinesiology, Education',
          'Labor and Industrial Relations', 'Large Animal Clicical Sciences (Epidemeiology',
          'Linguistics and Germanic, Asian and African Languages', 'Linguistics, Germanic, Slavic, Asian and African Languages',
          'Literature of English', 'Mass Media Program', 'Materials Science and Engineering & Biochemistry and Molecular Biology',
          'Measurement and Quantiative Methods Educational Policy', 'Media & Information Studies',
          'Microbiology and Molecular Genetics/ Institute of Environmental Toxicology', 'Music Theory, Music',          
          'Pharmacology and Toxicology and the Institute of Environmental Toxicology', 'Plant Biology and Cell and Molecular Biology',
          'Plant Biology and Program in Ecology, Evolutionary Biology and Behavior',
          'Plant Biology Ecology, Evolution, and Behavioral Biology Program', 'Plant Breeding, Genetics and Biotechnology',
          'Political science', 'Program in Ecology, Evolutionary Biology, and Behavior',
          'Program in Educational Psychology and Educational Technology', 'Psychologoy', 'Psychology, Kinesiology',
          'Psychology, Neuroscience Program', 'Psychology-Urban Affairs', 'Resource Development and Urban Affairs Programs',
          'Resource Development-Urban Studies', 'Rhetoric & Writing', 'Romance and Classical Languages',
          'Romance and Classical Language', 'School. of Music', 'Social Sciences. Anthropology', 'Social Sciences',
          'Supply Chain Management', 'Zoology & Environmental Toxicology', 'Organizational Behavior - Human Resource Management',
          'Zoology and Ecology, Evolutionary Biology and Behavior Program', 'Zoology and Ecology, Evolutionary Biology, and Behavior',
          'Zoology and Program in Ecology, Evolutionary Biology and Behavior',
          'Zoology and Program in Ecology, Evolutionary Biology, and Behavior',
          'Zoology, and Program in Ecology, Evolutionary Biology and Behavior',
          'Zoology and Program in Environmental Toxicology and Center for Integrative Toxicology',
          'Zoology, Ecology, Evolutional Biology, and Behavior', 'Zoology. Ecology, Evolutionary Biology, and Behavior Program',
          'Zoology; Ecology, Evolutionary Biology, and Behaviour Program', 'Zoology Ecology, Evolutionay Biology, and Behavior',
          'Zoology, Institute of Environmental Toxicology', 'Zoology, Program in Ecology, Evolutionary Biology and Behavior',
          'Zoology, Program in Ecology, Evolutionary Biology, and Behavior',
          'Zoology, W.K. Kellogg Biological Station and Program in Ecology, Evolutionary Biology, and Behavior']
boring += ['Urban agriculture', 'Urban ecology (Sociology)', 'Protein folding', 'Proteins--Analysis', 'Proteins',
           'Bioinformatics', 'Biochemistry', 'Chemistry--Computer simulation', 'Evolution (Biology)', 'Microbiology',
           'Biomedical engineering', 'Genetic algorithms', 'Human-computer interaction', 'Microbial diversity']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
recs = []
for page in range(pages):
    tocurl = 'https://d.lib.msu.edu/search?fq=ndltd.level%3ADoctoral&rows=' + str(rpp) + '&sort=date_sort+desc%2C+title+asc&start=' + str(rpp*page)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(6)
    for div in tocpage.find_all('div', attrs = {'class' : 'search_results'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for a in div.find_all('a'):
            if a.has_attr('href'):
                if re.search('creativeommons.org\/li', a['href']):
                    rec['license'] = {'url' : a['href']}
                elif re.search('^\/etd\/\d+$', a['href']):
                    rec['artlink'] = 'https://d.lib.msu.edu' + a['href']

        if 'artlink' in rec:
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)
    print('\n  %4i records so far\n' % (len(prerecs)))

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5-2)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    for h1 in artpage.body.find_all('h1'):
        rec['tit'] = h1.text.strip()
    for dl in artpage.body.find_all('dl'):
        for dt in dl.find_all('dt'):
            dtt = dt.text.strip()
        for dd in dl.find_all('dd'):
            #author
            if dtt == 'Authors':
                rec['autaff'] = [[ dd.text.strip(), publisher ]]
            #supervisor
            elif dtt == 'Thesis Advisors':
                for a in dd.find_all('a'):
                    rec['supervisor'].append([a.text.strip()])
            #date
            elif dtt == 'Date':
                rec['date'] = dd.text.strip()
            #subject
            elif dtt == 'Subjects':
                for a in dd.find_all('a'):
                    subject = a.text.strip()
                    if subject in boring:
                        keepit = False
                    else:
                        rec['keyw'].append(subject)
            #program
            elif dtt == 'Program of Study':
                for a in dd.find_all('a'):
                    program = re.sub(' *\- Doctor of .*', '', a.text.strip())
                    if program in boring:
                        keepit = False
                    elif program in ['Statistics']:
                        rec['fc'] = 's'
                    elif program in ['Computer Science', 'Computer Science and Engineering']:
                        rec['fc'] = 'c'
                    elif program in ['Astrophysics and Astronomy',
                                     'Astronomy and Astrophysics']:
                        rec['fc'] = 'a'
                    elif program in ['Applied Mathematics', 'Mathematics']:
                        rec['fc'] = 'm'
                    elif not program in ['Physics', 'Electrical Engineering',
                                         'Physics and Astronomy',
                                         'Computational Mathematics, Science and Engineering']:
                        rec['note'].append('PROG:::' + program)
            #pages
            elif dtt == 'Pages':
                ddt = dd.text.strip()
                if re.search('\d\d', ddt):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', ddt)
            #DOI
            elif dtt == 'Permalink':
                ddt = dd.text.strip()
                if re.search('doi.org.*10\.25335', ddt):
                    rec['doi'] = re.sub('.*?(10\.25335.*)', r'\1', ddt)
            #ISBN
            elif dtt == 'ISBN':
                rec['isbns'] = []
                for span in dd.find_all('span'):
                    rec['isbns'].append([('a', re.sub('[^X\d]', '', span.text.strip()))])
    #FFT
    for li in artpage.body.find_all('li', attrs = {'class' : 'dropdown-item'}):
        for a in li.find_all('a'):
            if a.has_attr('href') and re.search('OBJ', a['href']):
                rec['pdf_url'] = 'https://d.lib.msu.edu' + a['href']
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'sh-expand-block'}):
        rec['abs'] = div.text.strip()

    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    elif keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
