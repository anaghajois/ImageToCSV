import os
import shutil
import tes

#Make sure that there's an empty directory called csv
dirs = ['csv']
for dir in dirs:
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

#start conversion
tes.convert_all_in_folder('images/')
