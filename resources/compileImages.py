
import os
import shutil
from pathlib import Path

def foldersIn(path_to_parent):
    for fname in os.listdir(path_to_parent):
        if os.path.isdir(os.path.join(path_to_parent,fname)):
            yield os.path.join(path_to_parent,fname)

def compileImages(folder,outFolder):

    Path(outFolder).mkdir(parents=True, exist_ok=True)

    print('Compiling Images')
    os.walk(folder)
    folders = [ f.path for f in os.scandir(folder) if f.is_dir() ]
    folders = [x for x in folders if not 'imageOutput' in x]
    print(folders)

    for companyFolder in folders:
        if list(foldersIn(companyFolder)):
            companyNumber=companyFolder[-8:]
            print(companyNumber)

            imgFolder= companyFolder+'\\images'
            print(imgFolder)

            images=[]
            for file in os.listdir(imgFolder):
                if file.endswith(".jpeg") or file.endswith(".jpg"):
                    images.append(os.path.join(imgFolder, file))


            
            print(images)
            i=0
            for image in images:
                outDir=outFolder+'\\'+companyNumber+'-'+str(i)+'.jpeg'
                print(outDir)
                shutil.copy(image,outDir)
                i+=1
#folder = r'F:\Data Mining\CO2Extraction Run 0.1\CO2Extraction'
#outFolder=r'F:\Data Mining\CO2Extraction Run 0.1\CO2Extraction\imageOutput'
#compileImages(folder,outFolder)

#print(list(foldersIn("F:\Data Mining\CO2Extraction Run 0.1\CO2Extraction")))