# -*- coding: utf-8 -*-
#harvest theses from MPG
#FS: 2022-09-02

import sys
import datetime
import requests
import time
import urllib3
import json
import re
import ejlmod3
import codecs
import os

urllib3.disable_warnings()

now = datetime.datetime.now()

publisher = 'MPG'
jnlfilename = 'THESES-MPG-%s' % (ejlmod3.stampoftoday())

rpp = 500
years = [ejlmod3.year(), ejlmod3.year(backwards=1)]
sleepingtime = 3
apiurl = "https://pure.mpg.de/rest/items/search"

contexts = {"Import Context of the MPI for Mathematics" : 'm',
            "Publications of the MPI for Mathematics" : 'm',
            "Publications of the Max Planck Institute for Software Systems" : 'c',
            "Publications of the MPI for Gravitational Physics" : 'g',
            "Publications of the MPI for Nuclear Physics" : '',
            "Publications of the MPI for Physics" : '',
            "Publications of the MPI for Plasma Physics" : '',
            "Publications of the MPI for Radio Astronomy" : 'a',
            "Publications of the MPI for the Physics of Complex Systems" : '',
            "Publications of the MPI for the Structure and Dynamics of Matter" : '',
            "Import Context of the MPI for the Physics of Complex Systems" : '',
            "Import Context of the MPI for Informatics" : 'c',
            "Publications of the MPI for Extraterrestrial Physics" : 'a',
            "Publications of the MPI for Solar System Research" : 'a',
            "Publications of the MPI of Quantum Optics" : 'k'}
boring = ["External Context of the MPI for Human Development",
          "General Context of the MPI for the History of Science",
          "Import Context of the MPI for Foreign and International Criminal Law",
          "Import Context of the MPI for Terrestrial Microbiology",
          "Non MPI Publications by MPI for Chemical Ecology Staff",
          "Non MPI Publications by MPI for Evolutionary Anthropology Staff",
          "Non MPI publications by MPI Psycholinguistics staff",
          "Publications of caesar",
          "Publications of the Max Planck Institute for Foreign and International Criminal Law",
          "Publications of the Max Planck Institute of Psychiatry",
          "Publications of the Max Planck Institut für Eisenforschung GmbH",
          "Publications of the MPI for Brain Research",
          "Publications of the MPI for Chemical Energy Conversion",
          "Publications of the MPI for Chemistry",
          "Publications of the MPI for Evolutionary Anthropology",
          "Publications of the MPI for Evolutionary Biology",
          "Publications of the MPI for Human Cognitive and Brain Sciences",
          "Publications of the MPI for Human Development",
          "Publications of the MPI for Immunobiology and Epigenetics",
          "Publications of the MPI for Medical Research",
          "Publications of the MPI for Molecular Genetics",
          "Publications of the MPI for Plant Breeding Research",
          "Publications of the MPI for Polymer Research",
          "Publications of the MPI for Psycholinguistics",
          "Publications of the MPI for Terrestrial Microbiology",
          "Publications of the MPI for the Study of Societies",
          "Publications of the MPI of Biochemistry",
          "Publications of the MPI of Biophysics",
          "Publications of the MPI of Colloids and Interfaces",
          "Publications of the MPI of Experimental Medicine",
          "Publications of the MPI of Molecular Physiology",
          "Publications of the MPI of Neurobiology",
          "Sync Data of the MPI for Chemical Ecology",
          "Theses of the MPI for Biogeochemistry",
          "Theses of the MPI for Chemical Ecology",
          "External Context of the MPI for Molecular Genetics",
          "Externer Kontext des MPI BPC",
          "Import Context of the Max Planck Institut für Eisenforschung GmbH",
          "Import Context of the MPI for Biological Cybernetics",
          "Import Context of the MPI for Brain Research",
          "Import Context of the MPI for Immunobiology and Epigenetics",
          "Import Context of the MPI for Marine Microbiology",
          "Import Context of the MPI for Molecular Genetics",
          "Import Context of the MPI of Colloids and Interfaces",
          "Import Context of the MPI of Experimental Medicine",
          "Publications of the CliSAP Cluster of Excellence",
          "Publications of the Fritz Haber Institute",
          "Publications of the GWDG",
          "Publications of the Kunsthistorisches Institut in Florenz, MPI",
          "Publications of the Max Planck Institute for Intelligent Systems",
          "Publications of the MPI for Biophysical Chemistry",
          "Publications of the MPI for Comparative and International Private Law",
          "Publications of the MPI for Meteorology",
          "Publications of the MPI for Research on Collective Goods",
          "Publications of the MPI for Social Anthropology",
          "Publications of the MPI for Tax Law and Public Finance",
          "Publications of the MPI für Kohlenforschung"]







recs = []
for year in years:
    for degree in ['PHD', 'HABILITATION']:  # "BACHELOR", "MASTER"
        ejlmod3.printprogress('==', [[year], [degree]])
        payload = {
            "query" :
            {
                "bool" :
                {
                    "must" : [ {"term" : {"publicState" : {"value" : "RELEASED","boost" : 1.0}}}, 
                               {"term" : {"versionState" : {"value" : "RELEASED","boost" : 1.0}}},
                               {"term" : {"metadata.degree" : {"value" : degree,"boost" : 1.0}}},
                               {"term" : {"metadata.genre" : {"value" : "THESIS","boost" : 1.0}}},
                               {"term" : {"metadata.dateAccepted" : {"value" : str(year), "boost" : 1.0}}}, 
                               {"match_all" : {"boost" : 1.0} } ],
                    "adjust_pure_negative" : True,
#                    "boost" : 1.0
                }
            },
            "sort" : [{"metadata.title.keyword" : {"order" : "ASC"}}],
            "size" : str(rpp), "from" : "0"
        }
        payload = {
            "query" :{
                "bool" : {
                    "must" : [ {
                        "term" : {
                            "publicState" : {
                                "value" : "RELEASED"
                            }
                        }
                    }, {
                        "term" : {
                            "versionState" : {
                                "value" : "RELEASED"
                            }
                        }
                    }, {
                        "bool" : {
                            "must" : [ {
                                "bool" : {
                                    "should" : [ {
                                        "range" : {
                                            "metadata.datePublishedInPrint" : {
                                                "gte" : "%i-01-01||/d" % (year),
                                                "lte" : "%i-01-01||/d" % (year+1),
                                            }
                                        }
                                    }, {
                                        "range" : {
                                            "metadata.datePublishedOnline" : {
                                                "gte" : "%i-01-01||/d" % (year),
                                                "lte" : "%i-01-01||/d" % (year+1),
                                            }
                                        }
                                    }, {
                                        "range" : {
                                            "metadata.dateAccepted" : {
                                                "gte" : "%i-01-01||/d" % (year),
                                                "lte" : "%i-01-01||/d" % (year+1),
                                            }
                                        }
                                    }, {
                                        "range" : {
                                            "metadata.dateCreated" : {
                                                "gte" : "%i-01-01||/d" % (year),
                                                "lte" : "%i-01-01||/d" % (year+1),
                                            }
                                        }
                                    } ]
                                }
                            }, {
                                "bool" : {
                                    "must" : [ {
                                        "term" : {
                                            "metadata.genre" : {
                                                "value" : "THESIS"
                                            }
                                        }
                                    }, {
                                        "bool" : {
                                            "should" : [ {
                                                "term" : {
                                                    "metadata.degree" : {
                                                        "value" : degree
                                                    }
                                                }
                                            } ]
                                        }
                                    } ]
                                }
                            } ]
                        }
                    } ]
                }
            }
        }
        headers = {
            'Cache-Control' : 'no-cache',
            'Content-Type' : 'application/json'
        }
        response = requests.post(apiurl, json=payload, headers=headers, timeout=120, verify=False)
        response.raise_for_status()  # will raise an exception if there's an error
        r = response.json()
        i = 0
        if 'records' in r:
            for record in r['records']:
                keepit = True
                i += 1
                ejlmod3.printprogress('-', [[year, degree], [i, r["numberOfRecords"]], [len(recs)]])
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'date' : str(year), 'note' : [], 'autaff' : []}
                #context
                context = record['data']['context']['name']
                if context in boring:
                    keepit = False
                elif context in contexts:
                    if contexts[context]:
                        rec['fc'] = contexts[context]
                else:
                    rec['note'].append('CONTEXT=%s' % (context))
                #HDL
                rec['hdl'] = record['data']['objectPid'][4:]
                rec['link'] = 'http://hdl.handle.net/' + rec['hdl']
                #title
                rec['tit'] = record['data']['metadata']['title']
                #author
                for creator in record['data']['metadata']['creators']:
                    if creator['role'] == 'AUTHOR' and creator['type'] == 'PERSON':
                        rec['autaff'].append(['%s, %s' % (creator['person']['familyName'], creator['person']['givenName'])])
                        if 'organizations' in creator['person']:
                            for org in creator['person']['organizations']:
                                aff = org['name']
                                if 'address' in org:
                                    aff += ', ' + org['address']
                                rec['autaff'][-1].append(aff)
                #language
                if 'languages' in record['data']['metadata']:
                    rec['language'] = record['data']['metadata']['languages'][0]
                #university
                if 'publishingInfo' in record['data']['metadata'] and 'publisher' in record['data']['metadata']['publishingInfo']:
                    uni = record['data']['metadata']['publishingInfo']['publisher']
                    if 'place' in record['data']['metadata']['publishingInfo']:
                        uni += ', ' + record['data']['metadata']['publishingInfo']['place']
                    rec['autaff'][-1].append(uni)
                else:
                    uni = ''
                #keywords
                if 'freeKeywords' in record['data']['metadata']:
                    rec['keyw'] = [record['data']['metadata']['freeKeywords']]
                #pages
                if 'totalNumberOfPages' in record['data']['metadata']:
                    pages = record['data']['metadata']['totalNumberOfPages']
                    if re.search('\d\d', pages):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)
                #PDF
                if 'files' in record['data']:
                    for datei in record['data']['files']:
                        if 'visibility' in datei and datei['visibility'] == 'PUBLIC':
                            if 'mimeType' in datei and datei['mimeType'] == 'application/pdf':
                                rec['pdf_url'] = 'https://pure.mpg.de' + datei['content']
                            elif 'storage' in datei and datei['storage'] == 'EXTERNAL_URL':
                                exturl = datei['metadata']['title']
                                if re.search('^http', exturl):
                                    extcat = datei['metadata']['contentCategory']
                                    #print(extcat, exturl)
                                    if extcat == 'supplementary-material':
                                        rec['link'] = exturl
                                    elif extcat == 'any-fulltext':
                                        if re.search('\.pdf$', exturl):
                                            rec['pdf_url'] = exturl
                                        else:
                                            rec['link'] = exturl
                                    else:
                                        rec['note'].append('%s: %s' % (extcat, exturl))                                    
                #non PhD
                rec['MARC'] = [('502', [('b', degree), ('c', uni), ('d', str(year))])]
                if keepit:
                    ejlmod3.printrecsummary(rec)
                    recs.append(rec)
        else:
            print('    %i found' % (r["numberOfRecords"]))
        time.sleep(sleepingtime)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
