import os
from pdf2image import convert_from_path
from fpdf import FPDF
from PyPDF4 import PdfFileReader, PdfFileWriter
import cv2
import pytesseract
from os import walk


def pdf_to_images(folder,companyNumber):
    print('Filtering PDF and converting to images')
    filterPhrases = [
    'Scope 1',
    'Scope 2',
    'Scope 3',
    'scope 1',
    'scope 2',
    'scope 3',
    ]

    tempImagePath=(folder+'\\'+companyNumber+'\\images')
    os.mkdir(tempImagePath)

    pages = convert_from_path(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 350)
    filteredPages = []
    pdf = FPDF()

    imageCount = 0
    for page in pages:
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG')
        image = cv2.imread(imagePath)
        text = str(pytesseract.image_to_string(image))
        if not any(word in text for word in filterPhrases):
            os.remove(imagePath)
        imageCount+=1

def getImagePaths(folder,companyNumber):
    return next(walk(folder+'\\'+companyNumber+'\\images'), (None, None, []))[2]  # [] if no file