import os
from pdf2image import convert_from_path
#from PyPDF2 import PdfReader
from fpdf import FPDF
#from PyPDF4 import PdfFileReader, PdfFileWriter
import cv2
import shutil
import pytesseract
from os import walk
import time
from PIL import Image
import fitz
pytesseract.pytesseract.tesseract_cmd = r'C:\home\site\wwwroot\App_Data\jobs\triggered\CO2DataMining\runner\resources\Tesseract-OCR\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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
    
    #pages = convert_from_path(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 350,thread_count=16)
 
    filteredPages = []
    pdf = FPDF()

    imageCount = 0
    dataFound=False
    bufferPageCount=0


    mat = fitz.Matrix(300 / 72, 300 / 72)  # sets zoom factor for 300 dpi
    pages = fitz.open(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf')
    while pageNumbers:
        pageNumber =pageNumbers.pop(int(len(pageNumbers)/2))
        #print(pageNumber)
        page = pages[pageNumber]
        pix = page.get_pixmap(matrix=mat)

        number=("page-%04i" % page.number)
        

        pix.pil_save(tempImagePath+'\\'+number+'.tiff', format="TIFF", dpi=(300,300))
        im = Image.open(tempImagePath+'\\'+number+'.tiff')
        im.save(tempImagePath+'\\'+number+'.jpeg')
        os.remove(tempImagePath+'\\'+number+'.tiff')
        image = cv2.imread(tempImagePath+'\\'+number+'.jpeg')
        text = str(pytesseract.image_to_string(image))
        if not any(word in text for word in filterPhrases):
            os.remove(tempImagePath+'\\'+number+'.jpeg')
        else:
            dataFound=True
            #print('Data Found')
        if dataFound==True:
                bufferPageCount+=1
                #print('Buffer Page Check: '+str(bufferPageCount))
                if bufferPageCount==5:
                    #print('Buffer page count reached')
                    pageNumbers=[]
                    #print(pageNumbers)

    ''' pages = convert_from_path(folder+'\\'+companyNumber+'\\'+companyNumber+'_fullPDF.pdf', 500)
    
    pageNumbers = list(range(0, len(pages)))

    for page in pages:
        
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG')
        image = cv2.imread(imagePath)
        text = str(pytesseract.image_to_string(image))
        if not any(word in text for word in filterPhrases):
            os.remove(imagePath)

        print('Count: '+str(imageCount))
        imageCount+=1

    while pages:
        print(imageCount)
        page = pages.pop(int(len(pages)/2))
        imagePath = tempImagePath+'\\'+str(imageCount)+'.jpg'
        page.save(imagePath,'JPEG')
        image = cv2.imread(imagePath)
        text = str(pytesseract.image_to_string(image))
        if not any(word in text for word in filterPhrases):
            os.remove(imagePath)
        else:
            dataFound=True
            print('Data Found')
        if dataFound==True:
            bufferPageCount+=1
            print('Buffer Page Check: '+str(bufferPageCount))
            if bufferPageCount==5:
                print('Buffer page count reached')
                pages=[]
                #print(pages)

        imageCount+=1'''






    


   


    '''
    Collects all images remaining
    '''
    images=[]
    for file in os.listdir(tempImagePath):
        if file.endswith(".jpeg") or file.endswith(".jpg"):
            images.append(os.path.join(tempImagePath, file))

    outFolder=folder+'\imageOutput'
    i=0
    for image in images:
        outDir=outFolder+'\\'+companyNumber+'-'+str(i)+'.jpeg'
        shutil.copy(image,outDir)
        i+=1

    tempImagePath

def getImagePaths(folder,companyNumber):
    return next(walk(folder+'\\'+companyNumber+'\\images'), (None, None, []))[2]  # [] if no file


start = time.time()
pdf_to_images('F:\Data Mining\CO2Extraction','00184594')
end = time.time()
print('Time: ',end - start)