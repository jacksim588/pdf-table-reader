import csv
import io
import os


def text_files_to_csv(files,outFilePath):
    """Files must be sorted lexicographically
    Filenames must be <row>-<colum>.txt.
    000-000.txt
    000-001.txt
    001-000.txt
    etc...
    """
    rows = []
    for f in files:
        directory, filename = os.path.split(f)
        with open(f) as of:
            txt = of.read().strip()
        row, column = map(int, filename.split(".")[0].split("-"))
        if row == len(rows):
            rows.append([])
        rows[row].append(txt)
    
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerows(rows)

    #print('Output File:',outFilePath)
    f = open(outFilePath, 'w')
    writer = csv.writer(f)
    writer.writerows(rows)
    f.close()
    
    #return csv_file.getvalue()
    return rows

def main(files,outFilePath):
    return text_files_to_csv(files,outFilePath)
