import os
import sys
import csv
import requests
import cv2
import glob
import pandas as pd
from pathlib import Path
from pdf2image import convert_from_path
import pdf2image
import resources.extract_tables as extract_tables
import resources.extract_cells as extract_cells
import resources.ocr_image as ocr_image
import resources.ocr_to_csv as ocr_to_csv
import resources.mine_csv as mine_csv
import resources.file_structure as file_structure
import resources.get_pdf as get_pdf
import resources.pdf_to_image as pdf_to_image
import resources.errorHandling as errorHandling
import resources.formatImageTable as formatImageTable
import time
import psycopg2

print("Beginning Demo 2.0")

def main(image_filepath):
    #image_tables = table_ocr.extract_tables.main([image_filepath])
    print(image_filepath)
    image_tables = extract_tables.main([image_filepath],findTables=True)
    #print("Running `{}`".format(f"extract_tables.main([{image_filepath}])."))
    #print("Extracted the following tables from the image:")
    #print(image_tables)
    for image, tables in image_tables:
        #print(f"Processing tables for {image}.")
        for table in tables:
            #print(f"Processing table {table}.")
            cells = extract_cells.main(table)
            ocr = [
                ocr_image.main(cell, None)
                for cell in cells
            ]
            #print("Extracted {} cells from {}".format(len(ocr), table))
            #print("Cells:")
            for c, o in zip(cells[:3], ocr[:3]):
                with open(o) as ocr_file:
                    # Tesseract puts line feeds at end of text.
                    # Stript it out.
                    text = ocr_file.read().strip()
                    #print("{}: {}".format(c, text))
            # If we have more than 3 cells (likely), print an ellipses
            # to show that we are truncating output for the demo.
            
            if len(cells) > 3:
                print("...")
            outFilePath = (image_filepath[:-4]+'.csv')
            ocr_to_csv.main(ocr,outFilePath)
            

df = pd.read_csv('Input.csv', names=['CompanyNames'])           
companyNumbers = df.CompanyNames.tolist()


companyNumbers=[str(item).zfill(8) for item in companyNumbers]            
f = open("F:\Data Mining\SharepointAuthentication.txt", "r")
auth=f.read().split('|')
DB_NAME=auth[0]
USER=auth[1]
PASS = auth[2]
HOST = auth[3]
conn = psycopg2.connect(
   database=DB_NAME, user=USER, password=PASS, host=HOST, port= '5432'
)
conn.autocommit = True


folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\Filtered - Copy\\"
#folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\test\\"



companyNumbers=['03777037',
                '00184594',
                '01532937',
                '05650187',
                '03664571',
                '10537415',
                'JE111714',
                'IE620851']  
folder = 'F:\Data Mining\CO2Extraction'
file_structure.remove_contents(folder)
Path(folder+'\imageOutput').mkdir(parents=True, exist_ok=True)
getPDFCount=0
getPDFAvg=0
filterPDFCount=0
filterPDFAvg=0
dataMineCount=0
dataMineAvg=0
for companyNumber in companyNumbers[:1000]:
    print('CN: '+companyNumber)
    try:
        '''
        Takes company number and creates new folder
        '''
        file_structure.create_folder(folder,companyNumber)
        '''
        Takes company number and downloads latest company accounts from companies house
        Stores it in the folder created above
        '''
        print('Retrieving PDF')
        accountsDate=''
        accountsDate = get_pdf.get_pdf_from_companies_house(folder,companyNumber)
        '''
        takes the PDF, and filters it down to the pages with CO2 data on it
        takes the filtered PDF & converts it to an images
        '''
        print('Filtering PDF')

        pdf_to_image.pdf_to_images(folder,companyNumber)
        imageFiles = pdf_to_image.getImagePaths(folder,companyNumber)

        '''
        Takes the path of an image and extracts the table from this image
        '''
        print('Extracting data from image')


        imgFolderPath=(folder+'\\'+companyNumber+'\\images')
        formatImageTable.formatImages(imgFolderPath)


        try:
            for file in os.listdir(imgFolderPath+'\\dataExtract'):
                if file.endswith(".jpg"):
                    main(imgFolderPath+'\\dataExtract\\'+file)
        except cv2.error:
            print('Image Conversion Error')
        except IndexError:
            #raises a custom exception so that other Index Errors are caught
            raise errorHandling.NoPhraseInPDFError

        print('Mining output data')
        output = mine_csv.csv_to_array(folder+'\\'+companyNumber+'\\images\\dataExtract',companyNumber)
        output.insert(1, accountsDate)
        print(output)

    except errorHandling.AccountsNotFoundError:
        output=[companyNumber,accountsDate,'','','','','','','','AccountsNotFoundError']
    except errorHandling.NoPhraseInPDFError:
        output=[companyNumber,accountsDate,'','','','','','','NoPhraseInPDFError']
    except errorHandling.FailedToExtractDataError:
        output=[companyNumber,accountsDate,'','','','','','','FailedToExtractDataError']
    except pdf2image.exceptions.PDFPageCountError:
        output=[companyNumber,accountsDate,'','','','','','','PDFPageCountError']
    except Exception as e:
        if 'Syntax Error' in str(e):
            continue
        output=[companyNumber,'','','','','','','',e]

    print('Exporting Data for: ',companyNumber)
    print('data exporting: ',output)
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO "Co2_Annual_Accounts_Mining" VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s)''',(output[0],output[1],output[2],output[3],output[4],output[5],output[6],output[7],str(output[8])))
    except IndexError:
        cursor.execute('''INSERT INTO "Co2_Annual_Accounts_Mining" VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s)''',(output[0],output[1],output[2],output[3],output[4],output[5],output[6],output[7],''))
    #Commit changes in the database
    conn.commit()

    


