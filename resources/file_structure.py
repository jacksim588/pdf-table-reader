import os, shutil

def create_folder(folder,companyNumber):
    os.mkdir(folder+'\\'+companyNumber)
    with open(folder+'\\'+companyNumber+'\\'+'output.csv', "w") as my_empty_csv:
        # now you have an empty file already
        pass


def remove_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))