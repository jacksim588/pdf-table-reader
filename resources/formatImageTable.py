import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\home\site\wwwroot\App_Data\jobs\triggered\CO2DataMining\runner\resources\Tesseract-OCR\tesseract.exe'

def removeLines(imagePath):
    image = cv2.imread(imagePath,0)
    result = image.copy()
    #gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)

    return result

def get_Y_Contours(imagePath):
    # read image
    img = cv2.imread(imagePath)
    hh, ww = img.shape[:2]

    # convert to grayscale 
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # threshold gray image
    thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]

    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 255, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilate = cv2.dilate(thresh, kernel, iterations=4)


    # count number of non-zero pixels in each column
    count = np.count_nonzero(cv2.bitwise_not(dilate), axis=0)

    # threshold count at hh (height of image)
    count_thresh = count.copy()
    count_thresh[count==hh] = 255
    count_thresh[count<hh] = 0
    count_thresh = count_thresh.astype(np.uint8)

    # get contours
    Ycontours = cv2.findContours(count_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    Ycontours = Ycontours[0] if len(Ycontours) == 2 else Ycontours[1]
    return Ycontours

def get_X_Contours(imagePath):
    # read image
    img = cv2.imread(imagePath)
    hh, ww = img.shape[:2]

    # convert to grayscale 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # average gray image to one column
    column = cv2.resize(gray, (1,hh), interpolation = cv2.INTER_AREA)

    # threshold on white
    thresh = cv2.threshold(column, 254, 255, cv2.THRESH_BINARY)[1]

    # get contours
    Xcontours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    Xcontours = Xcontours[0] if len(Xcontours) == 2 else Xcontours[1]
    return Xcontours

def formatImages(Folder):
    imgFolder=Folder+'\\'+'dataExtract'
    filterPhrases = ['scope',
                    'total',
                    'emissions']

    os.mkdir(imgFolder)
    i=0
    '''
    
    
    '''
    for file in os.listdir(Folder):
        if file.endswith(".jpeg") or file.endswith(".jpg"):
            
            image = cv2.imread(Folder+'\\'+file)
            original = image.copy()
            height, width, channels = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (7,7), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Create rectangular structuring element and dilate
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            dilate = cv2.dilate(thresh, kernel, iterations=8)

            # Find contours and draw rectangle
            cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            

            
            
            for c in cnts:
                x,y,w,h = cv2.boundingRect(c)
                #cv2.rectangle(image, (x, y), (width-x, y + h), (36,255,12), 2)
                crop_img = image[y:y+h, x:width]
                
                text = pytesseract.image_to_string(crop_img)
                if any(substring in text.lower() for substring in filterPhrases):
                    cv2.imwrite(imgFolder+'\\image_'+str(i)+'.jpg', crop_img)
                i+=1
    #print('adding lines')
    for file in os.listdir(imgFolder):
        if file.endswith(".jpeg") or file.endswith(".jpg"):
            filePath=imgFolder+'\\'+file
            image = removeLines(filePath)

            hh, ww = image.shape[:2]
            result = image.copy()
            cv2.imwrite(filePath, result)
            xContours = get_X_Contours(filePath)
            yContours = get_Y_Contours(filePath)


            for cntr in yContours:
                # must transpose x,y and w,h since count is one-dimensional but represents each column
                y,x,h,w = cv2.boundingRect(cntr)
                xcenter = x+w//2
                cv2.line(result, (xcenter,0), (xcenter, hh-1), (0, 0, 0), 2)


            for cntr in xContours:
                x,y,w,h = cv2.boundingRect(cntr)
                ycenter = y+h//2
                cv2.line(result, (0,ycenter), (ww-1,ycenter), (0, 0, 0), 2)
            cv2.imwrite(filePath+'', result)





