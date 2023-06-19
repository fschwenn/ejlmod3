import re
import os
from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3

jnlfilename = 'THESES-ILLINOIS-%s' % (ejlmod3.stampoftoday())
recs = []

skipalreadyharvested = True
tocpages = 1

boring = []
for deg in ['M.S.', 'M.A.', 'MS', 'MA', 'A.Mus.D.', 'Ed.D.', 'M.S.', 'M.F.A.', 'M.L.A.', 'J.S.D.', 'M.U.P.']:
    boring.append('thesis.degree.name:::' + deg)
for disc in ['Animal Sciences', 'Chemistry', 'Education', 'Aerospace Engineering',
             'Crop Sciences', 'Natural Res & Env Sciences', 'Nutritional Sciences',
             'Portuguese', 'Psychology', 'Systems & Entrepreneurial Engr', 'Agricultural & Applied Econ',
             'Agricultural & Biological Engr', 'Anthropology', 'Architecture', 'Atmospheric Sciences',
             'Biochemistry', 'Bioengineering', 'Biology', 'Biophysics & Quant Biology',
             'Cell and Developmental Biology', 'Chemical Engineering', 'Civil Engineering', 'Communications and Media',
             'Community Health', 'Curriculum and Instruction', 'Ecol, Evol, Conservation Biol', 'Economics',
             'Educational Psychology', 'Educ Policy, Orgzn & Leadrshp', 'English', 'Entomology', 'Geography',
             'Geology', 'Human Dvlpmt & Family Studies', 'Industrial Engineering', 'Kinesiology',
             'Library & Information Science', 'Linguistics', 'Materials Science & Engr', 'Mechanical Engineering',
             'Molecular & Integrative Physi', 'Musicology', 'Music', 'Neuroscience', 'Plant Biology',
             'Regional Planning', 'Social Work', 'Spanish', 'VMS - Pathobiology',
             'Advertising', 'AfricanStudies', 'ArtandDesign', 'ArtEducation', 'ArtHistory', 'Bioinformatics',
             'Biophysics&ComputnlBiology', 'BusinessAdministration', 'ClassicalPhilology', 'Communication',
             'ComparativeLiterature', 'E.AsianLanguages&Cultures', 'EAsianLanguages&Cultures',
             'EnvironEngrinCivilEngr', 'EuropeanUnionStudies', 'FoodScience&HumanNutrition', 'FoodScience', 'French',
             'History', 'HumanRes&IndustrialRels', 'HumanResourceEducation', 'InformationSciences',  'Theatre',
              'LandscapeArchitecture', 'LatinAmericanStudies', 'Microbiology', 'MusicEducation',
             'NaturalResourcesandEnvironmentalSciences', 'Philosophy', 'PoliticalScience', 
             'Recreation,Sport,andTourism', 'Sociology', 'Speech&HearingScience', 'Statistics',
             'TeachingofEnglishSecLang', 'VMS-ComparativeBiosciences', 'VMS-VeterinaryClinicalMedcne',
             'Accountancy', 'AgriculturalandAppliedEconomics', 'BiophysicsandQuantitativeBiology', 'Communications',
             'EastAsianLanguagesandCultures', 'EdOrganizationandLeadership', 'EducationalPolicyStudies', 'Finance',
             'German', 'HumanDevelopmentandFamilyStudies', 'Italian', 'Law', 'SlavicLanguages&Literature',
             'SpecialEducation', 'UrbanPlanning',
             'Agr&ConsumerEconomics', 'ChemicalPhysics', 'CivilandEnvironmentalEngineering',
             'EducationPolicyStudies', 'EnvironScienceinCivilEngr', 'HumanResourcesandIndustrialRelations',
             'PsychologyPsychology', 'SlavicLanguages&Literature', 'SpanishLinguistics',
             'CommunicationsandMediaStudies', 'ComparativeandWorldLiterature', 'Human&CommunityDevelopment',
             'LibraryandInformationScience', 'MolecularandIntegrativePhysiology',
             'NaturalResourcesandEnvironmentalScience', 'Recreation,SportandTourism', 'SpeechCommunication']:
    boring.append('thesis.degree.discipline:::' + re.sub('\s', '', disc))

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def get_sub_site(url, fc, sess, aff):
    if ejlmod3.checkinterestingDOI(url):
        print('  [{}] --> Harvesting Data'.format(url))
    else:
        print('  [{}]'.format(url))
        return
    rec = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}
    keepit = True

    if fc: rec['fc'] = fc

    sleep(5)
    resp = sess.get(url)

    # Check if site correctly loaded
    if resp.status_code != 200:
        print("Can't reach this page:", url)
        return

    artpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['dc.contributor.advisor', 'dc.description.abstract',
                                        'dc.identifier.uri', 'dc.rights', 'citation_title', 'citation_author',
                                        'citation_keywords', 'citation_pdf_url', 'citation_public_url',
                                        'thesis.degree.name', 'citation_publication_date',
                                        'thesis.degree.discipline'])
    if 'thesis.degree.name' in rec:
        for d in rec['thesis.degree.name']:
            degree = re.sub('[\n\r\t\s]', '', d)
            if degree in boring:
                keepit = False
                print('     ~~~ skip %s ~~~' % (degree))
            elif not degree in ['thesis.degree.name:::PhD',
                                'thesis.degree.name:::PHD',
                                'thesis.degree.name:::Ph.D.']:
                rec['note'].append(degree)
    if 'thesis.degree.discipline' in rec:
        for d in rec['thesis.degree.discipline']:
            disc = re.sub('[\n\r\t\s]', '', d)
            if disc in boring:
                keepit = False
                print('     ~~~ skip %s ~~~' % (disc))
            elif disc == 'thesis.degree.discipline:::Astronomy':
                rec['fc'] = 'a'
            elif disc in ['thesis.degree.discipline:::Mathematics',
                          'thesis.degree.discipline:::AppliedMathematics']:
                rec['fc'] = 'm'
            elif disc in ['thesis.degree.discipline:::Informatics',
                          'thesis.degree.discipline:::ComputerScience']:
                rec['fc'] = 'c'
            elif not disc in ['thesis.degree.discipline:::Physics',
                              'thesis.degree.discipline:::Nuclear,Plasma,RadiolgcEngr']:
                rec['note'].append(disc)
    # Add the aff
    if not 'autaff' in rec or not rec['autaff']:
        for h4 in artpage.find_all('h4', attrs = {'class' : 'creators'}):
            rec['autaff'] = [[ re.sub('"', '', h4.text.strip()) ]]
    for author in range(0,len(rec['autaff'])):
        rec['autaff'][author].append(aff)
    # Title
    if not 'tit' in rec:
        for title in artpage.find_all('title'):
            rec['tit'] = re.sub('\|.*', '', title.text)

#    rec['hidden'] = rec['pdf_url']
#    rec.pop('pdf_url')
    rec['link'] = url
    pseudodoi = '20.2000/LINK/' + re.sub('\W', '', url[4:])
    if 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('   %s already in backup' % (rec['hdl']))
        if not keepit:
            ejlmod3.adduninterestingDOI(url)
    elif 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
        if not keepit:
            ejlmod3.adduninterestingDOI(url)
    elif pseudodoi in alreadyharvested:
        print('   %s already in backup' % (pseudodoi))
        if not keepit:
            ejlmod3.adduninterestingDOI(url)
    elif keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(url)


publisher = 'Illinois U., Urbana (main)'
departments = [('Dept.+of+Astronomy', 'Illinois U., Urbana, Astron. Dept.', 'a', tocpages),
               ('Dept.+of+Physics', 'Illinois U., Urbana', '', tocpages),
               ('Dept.+of+Computer+Science', 'Illinois U., Urbana (main)', 'c', tocpages),
               ('Dept.+of+Mathematics', 'Illinois U., Urbana, Math. Dept.', 'm', tocpages),
               ('all', 'Illinois U., Urbana (main)', '', tocpages*125)]
rpp = 25

reallinks = []
with Session() as session:
    for (dep, aff, fc, pages) in departments:
        for page in range(pages):
            if dep == 'all':
                tocurl = 'https://www.ideals.illinois.edu/items?direction=desc&fq%5B%5D=k_unit_titles%3AGraduate+Dissertations+and+Theses+at+Illinois&sort=d_element_dc_date_issued&&start=' + str(rpp*(page+110+110))
            else:
                tocurl = 'https://www.ideals.illinois.edu/items?direction=desc&fq%5B%5D=k_unit_titles%3AGraduate+Dissertations+and+Theses+at+Illinois&sort=d_element_dc_date_issued&fq%5B%5D=k_unit_titles%3A' + dep + '&start=' + str(rpp*page)
            ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
            index_resp = session.get(tocurl)

            if index_resp.status_code != 200:
                print("Can't reach this page:", tocurl)
                continue

            link_box = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('div', attrs={'class': 'flex-grow-1'})
            #tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
            #print(tocpage.text)
            #link_box = tocpage.find_all('div', attrs={'class': 'media-body'})
            for (j, box) in enumerate(link_box):
                link = box.find_all('a')
                if len(link) == 1:
                    reallink = link[0].get('href')
                    ejlmod3.printprogress('-', [[dep], [page+1, pages], [j+1, len(link_box)]])
                    if not reallink in reallinks:
                        get_sub_site(reallink, fc, session, aff)
                        reallinks.append(reallink)
            print('\n  %4i records so far\n' % (len(recs)))
            sleep(4)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
