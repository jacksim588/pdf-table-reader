import os
import sys
import csv
import requests
import cv2
import glob
import pandas as pd

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
import time
print("Beginning Demo 2.0")

def main(image_filepath):
    #image_tables = table_ocr.extract_tables.main([image_filepath])
    image_tables = extract_tables.main([image_filepath])
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



folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\Filtered - Copy\\"
#folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\test\\"

'''companyNumbers=['00457936','00329613','03707899','02242204','01872622'
               ,'04768193','SC044986','SC339123','OC304378',
                '07563201','11593130','07036902']'''

#companyNumbers=['04768193']     
folder = 'F:\Data Mining\CO2Extraction'
file_structure.remove_contents(folder)

getPDFCount=0
getPDFAvg=0
filterPDFCount=0
filterPDFAvg=0
dataMineCount=0
dataMineAvg=0
for companyNumber in companyNumbers:
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
        getPDFstart = time.time()

        get_pdf.get_pdf_from_companies_house(folder,companyNumber)

        getPDFend = time.time()
        getPDFAvg=(getPDFCount*getPDFAvg+(getPDFend-getPDFstart))/(getPDFCount+1)
        getPDFCount+=1
        '''
        takes the PDF, and filters it down to the pages with CO2 data on it
        takes the filtered PDF & converts it to an images
        '''
        print('Filtering PDF')
        filterPDFstart = time.time()

        pdf_to_image.pdf_to_images(folder,companyNumber)
        imageFiles = pdf_to_image.getImagePaths(folder,companyNumber)

        
        filterPDFend = time.time()
        filterPDFAvg=(filterPDFCount*filterPDFAvg+(filterPDFend-filterPDFstart))/(filterPDFCount+1)
        filterPDFCount+=1
        '''
        Takes the path of an image and extracts the table from this image
        '''
        print('Extracting data from image')

        dataMinestart = time.time()

        try:
            image_filepath=(folder+'\\'+companyNumber+'\\images\\'+imageFiles[0])
            main(image_filepath)
        except cv2.error:
            print('Image Conversion Error')
        except IndexError:
            #raises a custom exception so that other Index Errors are caught
            raise errorHandling.NoPhraseInPDFError

        print('Mining output data')
        output = mine_csv.csv_to_array(folder+'\\'+companyNumber+'\\images',companyNumber)
        print(output)

        dataMineend = time.time()
        dataMineAvg=(dataMineCount*dataMineAvg+(dataMineend-dataMinestart))/(dataMineCount+1)
        dataMineCount+=1
    except errorHandling.AccountsNotFoundError:
        output=[companyNumber,'','','','','','','AccountsNotFoundError']
    except errorHandling.NoPhraseInPDFError:
        output=[companyNumber,'','','','','','','NoPhraseInPDFError']
    except errorHandling.FailedToExtractDataError:
        output=[companyNumber,'','','','','','','FailedToExtractDataError']
    except pdf2image.exceptions.PDFPageCountError:
        output=[companyNumber,'','','','','','','PDFPageCountError']
    except Exception as e:
        if 'Syntax Error' in str(e):
            continue
        output=[companyNumber,'','','','','','',e]

    print('Exporting Data for: ',companyNumber)
    print('data exporting: ',output)
    f = open(folder+'\\'+'output.csv', 'a+', newline='')
    writer = csv.writer(f)
    writer.writerow(output)
    f.close()

    print('Get PDF Averge Time: ',getPDFAvg)
    print('filter PDF Averge Time: ',filterPDFAvg)
    print('Data Mining PDF Averge Time: ',dataMineAvg)
    


