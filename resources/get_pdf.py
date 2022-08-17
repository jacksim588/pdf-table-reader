from urllib.request import Request, urlopen
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import resources.errorHandling as errorHandling

def get_pdf_from_companies_house(folder,companyNumber):

    print('Extracting Annual Accounts')
    api_key = "H6h3Vz7mXSehD5TJeZ_iJEH72k_ooGtP6M0wnfvo" 

    response = requests.get('https://api.companieshouse.gov.uk/company/'+companyNumber+'/filing-history', auth=(api_key, ''))

    respDict = json.loads(response.text)
    documentDict=respDict['items']
    output_dict=[]
    try:
        output_dict = [x for x in documentDict if x['category'] == 'accounts']
        output_dict = [x for x in output_dict if (x['description'] == 'accounts-with-accounts-type-group') or (x['description'] == 'accounts-with-accounts-type-full')]
        documentURL = output_dict[0]['links']['document_metadata']

        accountsresponse = requests.get(documentURL+'/content', auth=(api_key, ''))
        #print(accountsresponse)
        with open(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 'wb') as f:
                f.write(accountsresponse.content)
    except:
        raise errorHandling.AccountsNotFoundError




