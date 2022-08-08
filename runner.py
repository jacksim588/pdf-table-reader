import os
import sys
import csv
import requests
import cv2
import glob


from pdf2image import convert_from_path

import resources.extract_tables as extract_tables
import resources.extract_cells as extract_cells
import resources.ocr_image as ocr_image
import resources.ocr_to_csv as ocr_to_csv

print("Beginning Demo 2.0")

def main(image_filepath):
    #image_tables = table_ocr.extract_tables.main([image_filepath])
    image_tables = extract_tables.main([image_filepath])
    print("Running `{}`".format(f"extract_tables.main([{image_filepath}])."))
    print("Extracted the following tables from the image:")
    print(image_tables)
    for image, tables in image_tables:
        print(f"Processing tables for {image}.")
        for table in tables:
            print(f"Processing table {table}.")
            cells = extract_cells.main(table)
            ocr = [
                ocr_image.main(cell, None)
                for cell in cells
            ]
            print("Extracted {} cells from {}".format(len(ocr), table))
            print("Cells:")
            for c, o in zip(cells[:3], ocr[:3]):
                with open(o) as ocr_file:
                    # Tesseract puts line feeds at end of text.
                    # Stript it out.
                    text = ocr_file.read().strip()
                    print("{}: {}".format(c, text))
            # If we have more than 3 cells (likely), print an ellipses
            # to show that we are truncating output for the demo.
            
            if len(cells) > 3:
                print("...")
            outFilePath = (image_filepath[:-4]+'.csv')
            ocr_to_csv.main(ocr,outFilePath)
            

            
            

image_filepath = r'C:\Users\jacks\Documents\GitHub\OCR-PDF-Mining\output\bin\Filtered PDF Images\6016233-1.png'


folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\Filtered - Copy\\"
#folder = r"C:\Users\jacks\Documents\Document(Offline)\Barcanet\Record Linkage\Filtered\test\\"
for file in os.listdir(folder):
    pdf_filepath=(folder+file)
    images = convert_from_path(pdf_filepath)
    image_filepath = pdf_filepath[:-4]+'.png'
    images[0].save(image_filepath)
    try:
        main(image_filepath)
    except cv2.error:
        print('Image Conversion Error')




