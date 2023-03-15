from requests import Session
from json import loads
from time import sleep
import ejlmod3


publisher = 'Wien U.'
jnlfilename = 'THESES-WIEN_%s' % ejlmod3.stampoftoday()
pages = 3  # Change this variable to set the number of pages
skipalreadyharvested = True


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    
with Session() as session:

    recs = []
    for page in range(0, pages):
        url = "https://utheses-admin.univie.ac.at/api/proxy/solrSelect/q%3d*%3a*%20%20AND%20thesis_type%3a(" \
              "*1PHE-7VMS)%20AND%20department_id%3a(" \
              "*5EX2-079H%20OR%20*WWYA-96YK%20OR%20*4QFF-GVQ4)%20AND%20utheses_obj_type%3a%22container%22%26rows%3d25" \
              "%26start%3d"+str(25*page)+"%26sort%3dpublication_date%20desc "
        ejlmod3.printprogress('=', [[page+1, pages], [url]])

        index_resp = session.get(url)

        if index_resp.status_code != 200:
            print("[%s] --> Can't open index page!" % url)
            continue

        index_data = loads(index_resp.content.decode('utf-8'))

        articles = index_data.get('response').get('docs')

        for article in articles:
            rec: dict = {'tc': 'T', 'jnl': 'BOOK'}

            # Add abstract
            if len(article.get('abstracts')) == 2:
                rec['abs'] = article.get('abstracts')[1]
            else:
                rec['abs'] = article.get('abstracts')[0]
                rec['language'] = 'German'
                rec['notes'] = ['Abstract only in german']

            # Add Supervisor
            rec['supervisor'] = []
            for supervisor in article.get('advisers'):
                rec['supervisor'].append([supervisor])

            # Add Assessors as Supervisors
            #for assessor in article.get('assessors'):
            #    rec['supervisor'].append([assessor])

            # Add the authors
            rec['autaff'] = []
            for author in article.get('authors'):
                rec['autaff'].append([author, publisher])

            # Add DOI
            if article.get('doi') is not None:
                rec['doi'] = article.get('doi')
            else:
                rec['doi'] = '20.2000/Wien/' + article.get('id')

            # Add keywords
            rec['keyw'] = article.get('keywords').split(', ')

            # Add title
            rec['tit'] = article.get('main_title')

            # Add date
            rec['date'] = article.get('publication_date')

            # Add urn
            rec['urn'] = article.get('urn')

            # Add fc
            department_id = article.get('department_id')

            if department_id == 'https://pid.phaidra.org/univie-org/4QFF-GVQ4':
                rec['fc'] = 'm'
            elif department_id == 'https://pid.phaidra.org/univie-org/WWYA-96YK':
                rec['fc'] = 'c'

            # Add pages
            rec['pages'] = article.get('number_of_pages')

            # Add pdf link
            rec['hidden'] = 'https://phaidra.univie.ac.at/download/' + article.get('thesis_doc_pid')

            # Add link
            rec['link'] = 'https://utheses.univie.ac.at/detail/' + article.get('id')
            if skipalreadyharvested:
                if 'doi' in rec and rec['doi'] in alreadyharvested:
                    print('  %s already in backup' % (rec['doi']))
                elif 'urn' in rec and rec['urn'] in alreadyharvested:
                    print('  %s already in backup' % (rec['urn']))
                else:
                    recs.append(rec)
                    ejlmod3.printrecsummary(rec)
            else:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
        sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
