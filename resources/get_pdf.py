from urllib.request import Request, urlopen
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json

def get_pdf_from_companies_house(folder,companyNumber):
    print('Extracting Annual Accounts')
    api_key = "H6h3Vz7mXSehD5TJeZ_iJEH72k_ooGtP6M0wnfvo" 

    response = requests.get('https://api.companieshouse.gov.uk/company/'+companyNumber+'/filing-history', auth=(api_key, ''))
    #print(response.text)

    respDict = json.loads(response.text)
    documentDict=respDict['items']
    output_dict=[]

    output_dict = [x for x in documentDict if x['category'] == 'accounts']
    print(output_dict)
    output_dict = [x for x in output_dict if (x['description'] == 'accounts-with-accounts-type-group') or (x['description'] == 'accounts-with-accounts-type-full')]
    print(output_dict)
    print(output_dict[0]['links']['document_metadata'])
    documentURL = output_dict[0]['links']['document_metadata']

    accountsresponse = requests.get(documentURL+'/content', auth=(api_key, ''))
    print(accountsresponse)
    with open(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 'wb') as f:
            f.write(accountsresponse.content)









    '''req = Request('https://find-and-update.company-information.service.gov.uk/company/'+companyNumber+'/filing-history')
    html_page = urlopen(req).read()
    soup = bs(html_page, 'html.parser')
    fileTable = soup.find_all("table", {"class": "full-width-table"})
    
    accounts_url=[]
    fileRows = fileTable[0].find_all("tr")
    headers = {
    "User-Agent": "PostmanRuntime/7.20.1",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Postman-Token": "8eb5df70-4da6-4ba1-a9dd-e68880316cd9,30ac79fa-969b-4a24-8035-26ad1a2650e1",
    "Host": "medianet.edmond-de-rothschild.fr",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "cache-control": "no-cache",
    }
    for row in fileRows:
        if 'accounts' in row.text.strip():
            for a in row.find_all('a', href=True):
                accounts_url=a['href']
                print(accounts_url)
    if accounts_url !=[]:
        response = requests.get('https://find-and-update.company-information.service.gov.uk/'+accounts_url[0],headers=headers)
        with open(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 'wb') as f:
            f.write(response.content)'''