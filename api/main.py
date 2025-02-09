# from scholarly import scholarly
from thefuzz import fuzz
import bibtexparser
# from scholarly import scholarly, ProxyGenerator
import json
import os
os.environ['PYB_CONFIG_FILE'] = "./config.ini"
from pybliometrics.scopus.utils import config
from nanoid import generate
import pandas as pd
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from pybliometrics.scopus import AbstractRetrieval, ScopusSearch, CitationOverview
from dotenv import load_dotenv
import tempfile



gcloud_credentials = {}

config['Directories']['AbstractRetrieval'] = f'{tempfile.gettempdir()}/Scopus/abstract_retrieval'
config['Directories']['AffiliationSearch'] = f'{tempfile.gettempdir()}/Scopus/affiliation_search'
config['Directories']['AuthorRetrieval'] = f'{tempfile.gettempdir()}/Scopus/author_retrieval'
config['Directories']['AuthorSearch'] = f'{tempfile.gettempdir()}/Scopus/author_search'
config['Directories']['CitationOverview'] = f'{tempfile.gettempdir()}/Scopus/citation_overview'
config['Directories']['AffiliationRetrieval'] = f'{tempfile.gettempdir()}/Scopus/affiliation_retrieval'
config['Directories']['ScopusSearch'] = f'{tempfile.gettempdir()}/Scopus/scopus_search'
config['Directories']['SerialTitle'] = f'{tempfile.gettempdir()}/Scopus/serial_title'


if (config['GOOGLE']['ENV'] != 'DEV'):
    gcloud_credentials_dict = {
        'type': 'service_account',
        'client_id': config['GOOGLE']['GCLOUD_CLIENT_ID'],
        'client_email': config['GOOGLE']['GCLOUD_CLIENT_EMAIL'],
        'private_key_id':config['GOOGLE']['GCLOUD_PRIVATE_KEY_ID'],
        'private_key' : config['GOOGLE']['GCLOUD_PRIVATE_KEY'].replace('\\n', '\n')
    }
    print(gcloud_credentials_dict)
    gcloud_credentials = ServiceAccountCredentials.from_json_keyfile_dict(gcloud_credentials_dict)

def splitEid(eid):
    return eid.split('-')[2]

def getScopusDoc(title):
     s = ScopusSearch(query=title)
     df = pd.DataFrame(s.results)
     d = df.loc[df['title'].str.lower() == title]
     if (d.empty):
        return None
     doc = AbstractRetrieval(d['eid'].item(), view='FULL')
     pub_year = doc.coverDate.split('-')[0]
     references = getReferences(doc)
     citations = getCitations(doc)
     dd = {'uid': generate(), 'id': (doc.identifier), 'pub_title': title, 'pub_year': pub_year, 'references': references, 'citations': citations, 'num_pub_citations':len(citations)}
     return dd

def getReferences(doc):
    refs = []
    refIds = []
    for ref in doc.references:
        if ref.title:
            refIds.append(ref.id)
            formatRef = {}
            formatRef['uid'] = generate()
            formatRef['id'] = ref.id
            formatRef['pub_title'] = ref.title
            formatRef['pub_year'] = ref.publicationyear
            try:
                citations = CitationOverview(identifier=[ref.id], id_type="scopus_id", start=1950,end=2021)
                formatRef['num_pub_citations'] = citations.grandTotal
                refs.append(formatRef)
            except:
               continue
#     print("Refs")
#     print(len(refs))
#     print(refs)
    return refs



def getCitations(doc):
    doc_id = splitEid(doc.eid)
    c = ScopusSearch(query=f"REF({doc_id})")
#     print(c)
    citations = []
    citationIds = []
    for citation in c.results:
#         print(citation)
        if citation.title:
            doc_id = splitEid(citation.eid)
#             refIds.append(ref.id)
            formatCite = {}
            formatCite['uid'] = generate()
            formatCite['id'] = doc_id
            formatCite['pub_title'] = citation.title
            formatCite['pub_year'] = citation.coverDate.split('-')[0]
            try:
#                 print(doc_id)
                subCites = CitationOverview(identifier=[doc_id], id_type="scopus_id", start=1950,end=2021)
#                 print(subCites)
                formatCite['num_pub_citations'] = subCites.grandTotal
                citations.append(formatCite)
            except:
               continue
#     print("Citations")
#     print(len(citations))
#     print(citations)
    return citations

# test = getScopusDoc("safety first? production pressures and the implications on safety and health")

matched_pubs = []
pubsInYearCount = {}
ySeparation = 5



#Get the y value from the year by reading how many pubs have already been added under that year
def getY(x):
    if x in pubsInYearCount.keys():
#         print(x + " is found")
        pubsInYearCount[x] += 1
        return pubsInYearCount[x] * ySeparation
    else:
#         print(x + " is not found")
        pubsInYearCount[x] = 1
        return ySeparation

mapPubs = []

def extractMapFromPub(pub, yOffset):
    mapPub = {}
    if pub:
#         print(pub)
        mapPub["id"] = pub['uid']
        mapPub["doc_id"] = pub['id']
        mapPub["x"] = int(pub['pub_year']) * 5
        mapPub["y"] = getY(pub['pub_year']) + yOffset
        mapPub["weight"] = pub['num_pub_citations']
        mapPub["label"] = pub['pub_title']
        return mapPub

# def extractGsPubData(pub):
#     pub_to_add = {}
#     pub_year = pub['bib']['pub_year']
#     pub_citations = pub['num_citations']
#     if not(pub_year.isdigit()):
#         return
# #     if (pub['citedby_url']):
# #         return
# #     pub_cite_id = pub['citedby_url'].split('?')[1].split('=')[1].split('&')[0]
#     pub_title = pub['bib']['title'].lower()
#     pub_to_add["id"] = generate()
#     pub_to_add["pub_year"] = pub_year
# #     pub_to_add["pub_cite_id"] = pub_cite_id
#     pub_to_add["pub_title"] = pub_title
#     pub_to_add["num_pub_citations"] = pub_citations
# #     pub_to_add["x"] = int(pub_year)
# #     pub_to_add["y"] = getY(pub_year)
# #     pub_to_add["weight"] = pub_citations
# #     print(pub_to_add)
# #     print(extractMapFromPub(pub_to_add))
#     return pub_to_add



# def getCitationsFromGs:
def checkCrossReferences(pubMap):
    extraLinks = []
    for item in pubMap:
        for i in pubMap:
            count = 0
            if (i['doc_id'] == item['doc_id'] and i['id'] != item['id']):
                print("Duplicate found, create additional link")
                print(i['label'])
                extraLinks.append({'source_id': i['id'],'target_id':item['id']})
    return extraLinks

# bibstr =  "@article{singh1997state,title={State of the art in automation of earthmoving},author={Singh, Sanjiv},journal={Journal of Aerospace Engineering},volume={10},number={4},pages={179--188},year={1997},publisher={American Society of Civil Engineers}}"
# bidb = bibtexparser.loads(bibstr)
# print(bidb)

def bibvis(request):
    items = []
    links = []
    matched_pubs = []
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    request_json = request.get_json()
    if request_json['bibtex']:
       bibtex_database = bibtexparser.loads(request_json['bibtex'])
       print(bibtex_database)
       for bibentry in bibtex_database.entries:
           bib_entry_title = bibentry['title'].lower()
           doc = getScopusDoc(bib_entry_title)
           matched_pubs.append(doc)



       for i, pub in enumerate(matched_pubs):
           yOffset = i * 100
           if not(pub):
               break
           items.append(extractMapFromPub(pub,yOffset))
           for citation in pub["citations"]:
               if not(citation):
                   break
               items.append(extractMapFromPub(citation,yOffset))
               links.append({'source_id': citation['uid'],'target_id':pub['uid']})
           for reference in pub["references"]:
               if not(reference):
                   break
               items.append(extractMapFromPub(reference,yOffset))
               links.append({'source_id': reference['uid'],'target_id':pub['uid']})

       extraLinks = checkCrossReferences(items)
       links = links + extraLinks
       if (len(items) < 1):
        return(500)
       print(f"Total pubs: {len(items)}")

       vosJson = {'network': {'items': items,'links':links},'config': {}}
       with open(f'{tempfile.gettempdir()}/result.json', 'w') as fp:
           json.dump(vosJson, fp)

       gcloud_storage_client = storage.Client(credentials=gcloud_credentials, project='bibvis')
       bucket = gcloud_storage_client.get_bucket('bibvis.appspot.com')
       blob = bucket.blob(f'{generate()}.json')
       blob.upload_from_filename(f'{tempfile.gettempdir()}/result.json')
       os.remove(f'{tempfile.gettempdir()}/result.json')
       items = []
       links = []
       print(blob.public_url)
       return ({"jsonUrl": blob.public_url}, 200, headers)

    else:
        return ('Something went wrong', 500, headers)


