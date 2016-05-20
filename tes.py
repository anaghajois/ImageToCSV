from PIL import Image
from tesserwrap import Tesseract
import csv
import glob

#Get the object from the list whose value starts with the given key
def get_object(lst, key):
    for l in lst:
        if l.value.lower().startswith(key):
            return l
    return None

#Create a csv file and write the list to it as rows
def save_to_csv(strings):
    myfile = open('csv/results.csv', 'a+')
    wr = csv.writer(myfile)
    wr.writerows(strings)

#Get the header rects. They have been found to work with all the images
def get_header_rects():
    header_rects = [(285,0,820,0), (821,0,940,0), (941,0,1380,0), (1381,0,1870,0), (1871,0,2310,0), (2311,0,2610,0), (2611,0,2720,0), (2721,0,2990,0) ]
    return header_rects

#Find the most suitable column for the given word object
def find_most_suitable_column(word, header_rects):
    word_rect = word.box
    min_deviation = 32000
    min_index = 0
    for index, rect in enumerate(header_rects):
        #if word is contained in a header rect, return the column
        #if not find the row with the mnimum deviation. This handles all the error cases
        if rect[0] < word_rect[0] and rect[2] > word_rect[2]:
            return index
        if abs(rect[0] - word_rect[0]) < min_deviation:
            min_deviation = abs(rect[0] - word_rect[0])
            min_index = index

        if abs(rect[2] - word_rect[2]) < min_deviation:
            min_deviation = abs(rect[2] - word_rect[2])
            min_index = index

    return min_index

#write the header to the csv
def write_header_to_file():
    csv_strings = [['Customer', 'Status', 'Compliance Notes', 'Ship To Street1', 'Ship To Street2', 'Ship To City', 'Ship To State', 'Ship To Zip']]
    save_to_csv(csv_strings)

#process each line in the image as a row in the csv
def process_lines(lines, words, header_rects):
    cur_word_index = 0
    csv_strings = []
    for line in lines:
        csv_lst = [""] * len(header_rects)
        words_in_line = line.value.split()
        for word in words_in_line:
            if( word == words[cur_word_index].value):
                word_index = find_most_suitable_column(words[cur_word_index], header_rects)
                csv_lst[word_index] = csv_lst[word_index] + " " + words[cur_word_index].value
            cur_word_index += 1
        csv_strings.append(csv_lst)

    save_to_csv(csv_strings)

#Get a csv file for a given image
def get_csv(file_name):
    #Open the image and get the lines and words
    img = Image.open(file_name)
    tr = Tesseract()
    tr.ocr_image(img)
    lines = tr.get_textlines()
    words = tr.get_words()

    #Find the header line
    header = get_object(lines, 'customer')
    header_index = lines.index(header)

    if not header:
        print "Fatal Error: Couldn't find the header"
        return

    header_rects = get_header_rects()
    zip_word = get_object(words, 'zip')
    zip_word_pos = words.index(zip_word)

    #send only the non header lines and words
    process_lines(lines[header_index + 1:-3], words[zip_word_pos + 1:], header_rects)

#convert data in each file in the folder to a csv file
def convert_all_in_folder(folder):
    images = glob.glob(folder + "*")
    write_header_to_file()
    for image_name in images:
        print image_name
        try:
            get_csv(image_name)
        except Exception, e:
            print 'exception', e
