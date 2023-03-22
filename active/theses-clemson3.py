# -*- coding: utf-8 -*-
#harvest thesis from Clemson U.
#FS: 2022-11-10

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3
import re

publisher = 'Clemson U.'
jnlfilename = 'THESES-CLEMSON-%s' % (ejlmod3.stampoftoday())

pages = 4
boring = ['Chemical Engineering', 'Applied Health Research and Evaluation',
          'Automotive Engineering', 'Biochemistry and Molecular Biology',
          'Bioengineering', 'Chemical and Biomolecular Engineering', 'Chemistry',
          'Civil Engineering', 'Economics', 'Educational Leadership - Higher Education',
          'Educational Leadership', 'Education and Organizational Leadership Development',
          'Education Systems Improvement Science', 'Food Technology', 
          'Environmental Engineering and Earth Science', 'Food Science and Human Nutrition',
          'Genetics and Biochemistry', 'Genetics', 'Healthcare Genetics',
          'Industrial Engineering', 'International Family and Community Studies',
          'Literacy, Language and Culture', 'Materials Science and Engineering',
          'Parks, Recreation and Tourism Management', 'Wildlife and Fisheries Biology',
          'Planning, Design, and the Built Environment', 'Plant and Environmental Science',
          'Public Health Services', 'Rhetorics, Communication, and Information Design',
          'Animal and Veterinary Sciences', 'Biological Sciences',
          'Construction Science and Management', 'Curriculum and Instruction',
          'Educational Leadership P-12', 'Education and Human Development',
          'Engineering and Science Education', 'Entomology, Soils and Plant Sciences',
          'Environmental Engineering', 'Environmental Toxicology',
          'Food, Nutrition, and Culinary Science', 'Teaching and Learning',
          'Forestry and Environmental Conservation', 'Human Factors Psychology',
          'Industrial-Organizational Psychology', 'Institute on Family and Community Life',
          'Learning Sciences', 'Policy Studies', 'Psychology',
          'School of Materials Science and Engineering', 'Special Education',
          'Biosystems Engineering', 'Communication Studies',
          'Division of Agriculture (SAFES)', 'Environmental Engineering and Earth Sciences',
          'Environmental Engineering and Science', 'Literacy', 'Management',
          'Mechanical Engineering', 'Microbiology', 'Social Sciences',
          'Planning, Development, and Preservation', 'School of Nursing',
          'School of Architecture', 'Applied Economics', 'Biochemistry',
          'Career and Technical Education', 'Curriculum and Instruction, Literacy',
          'Curriculum and Instruction, Special Education', 'Education', 'Entomology',
          'Food, Nutrition and Packaging Sciences', 'Forest Resources',
          'Forestry and Natural Resources', 'Higher Educational Leadership',
          'Industrial and Organizational Psychology', 'Materials Science', 'Nursing',
          'Parks, Recreation, and Tourism Management', 'Polymer and Fiber Science',
          'Analytical Chemistry', 'Animal Physiology', 'Career and Technology Education',
          'Environmental Design and Planning', 'Fiber and Polymer Science',
          'Management and Information Systems', 'Wildlife Biology',
          'Construction Engineering and Management', 'Hydrogeology',
          'Vocational/Technical Education', 'Industrial Management', 'Nutrition',
          'Operations and Supply Chain Management']          
          
skipalreadyharvested = True

recs: list = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def get_sub_site(url, sess):
    rec: dict = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}
    rec['doi'] = '30.3000/Clemson/' + re.sub('\D', '', url)
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        return

    record_resp = sess.get(url)

    if record_resp.status_code != 200:
        print("[{}] --> Error: Can't reacht this site! Skipping...")
        return

    soup = BeautifulSoup(record_resp.content.decode('utf-8'), 'lxml')
    sleep(5)        

    # Metatagcheck
    ejlmod3.metatagcheck(rec, soup, ['bepress_citation_author', 'bepress_citation_title', 'bepress_citation_pdf_url', 'bepress_citation_date', 'description'])
    #author
    for div in soup.find_all('div', attrs = {'id' : 'orcid'}):
        for h4 in div.find_all('h4'):
            if h4.text == 'Author ORCID Identifier':
                for p in div.find_all('p'):
                    rec['autaff'][-1].append('ORCID:'+p.text)
            else:
                print('   ?', h4.text)
    rec['autaff'][-1].append(publisher)

    # Get the committee members
    advisor_section = soup.find_all('div', attrs={'id': 'advisor1'})
    if len(advisor_section) == 1:
        rec['supervisor'] = [[advisor_section[0].find_all('p')[0].text]]

    # Get the pdf link
    pdf_link = soup.find_all('a', attrs={'id': 'pdf'})
    if len(pdf_link) == 1:
        rec['hidden'] = pdf_link[0].get('href')

    #department
    for div in soup.find_all('div', attrs = {'id' : ['department', 'legacy_department']}):
        for p in div.find_all('p'):
            dep = p.text
            if dep in boring:
                ejlmod3.adduninterestingDOI(url)
                return
            elif dep in ['Human Centered Computing', 'School of Computing',
                         'Computer Engineering', 'Computer Science']:
                rec['fc'] = 'c'
            elif dep in ['Mathematical Sciences', 'Mathematical Science',
                         'School of Mathematical and Statistical Sciences',
                         'Mathematics', 'Number Theory']:
                rec['fc'] = 'm'
            elif dep in ['Statistics']:
                rec['fc'] = 's'
            else:
                rec['note'].append(dep)

    recs.append(rec)
    ejlmod3.printrecsummary(rec)

with Session() as session:
    index_url = "https://tigerprints.clemson.edu/all_dissertations/index.html"
    for page in range(pages):
        ejlmod3.printprogress('=', [[page+1, pages], [index_url]])
        index = session.get(index_url)

        if index.status_code != 200:
            print("Error: Can't open the index page")
            exit(0)
        links = []
        for article in BeautifulSoup(index.content.decode('utf-8'), 'lxml').find_all('p', attrs={'class': 'article-listing'}):
            link = article.find_all('a')
            if len(link) == 1:
                if ejlmod3.checkinterestingDOI(link[0].get('href')):
                    links.append(link[0].get('href'))
        for (k, link) in enumerate(links):
            ejlmod3.printprogress('-', [[page+1, pages], [k+1, len(links)], [link], [len(recs)]])
            get_sub_site(link, session)
        index_url = "https://tigerprints.clemson.edu/all_dissertations/index."+str(page+2)+'.html'



ejlmod3.writenewXML(recs, publisher, jnlfilename)

