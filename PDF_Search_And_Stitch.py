# import parser object from tika
import os
import pathlib
import re
import timeit
from glob import glob
from itertools import chain
import PyPDF2
import pandas as pd
from tika import parser

start = timeit.default_timer()
print(start)
# looks for all entries of regex string finding all unique entries
regexString = r"1.13.01.129.00*\w"  # put in function as argument

# gets all pdf form the working directory and makes a list of all pdf file names and replaces spaces with underscores
pdfs = glob('*.pdf')
newFolder = [folder.replace(".pdf", "") for folder in pdfs]
newFolder = [folder.replace(" ", "_") for folder in newFolder]

# makes directories of all pdf's in folder
for i in newFolder:
    fullDirectory = str(os.getcwd()) + '/temp/' + i
    pathlib.Path(fullDirectory).mkdir(parents=True, exist_ok=True)
print("Folders Created:")
print(*newFolder, sep=', ')

# splits all pdf's into folders and pages
pageFiles = []
for i in pdfs:
    inputPdf = PyPDF2.PdfFileReader(open(i, "rb"))
    for page in range(inputPdf.numPages):
        output = PyPDF2.PdfFileWriter()
        output.addPage(inputPdf.getPage(page))
        filename = str(os.getcwd()) + "\\temp\\" + str(newFolder[pdfs.index(i)]) + "\\" + "%04i.pdf" % (page + 1)
        with open(filename, "wb") as outputStream:
            output.write(outputStream)
        pageFiles.append(filename)

# find unique regexString instances and writes all parsed data from pdf to dictionary
regexStringInstanceNested = []
pageFileContent = {}
for pageFile in pageFiles:
    parsed_pdf = parser.from_file(pageFile)
    data = parsed_pdf['content']
    pageFileContent[pageFile] = data
    regexStringInstance = re.findall(regexString, data)
    regexStringInstanceNested.append(regexStringInstance)

# uniqueRegexLong is all unique regex string instances that exist in file/s no matter the length
uniqueRegexLong = list(set(chain(*regexStringInstanceNested)))
print("uniqueRegexLong = ", uniqueRegexLong, "\n")
# re-write to only get 19 characters
regex19char = [rep[:19] for rep in uniqueRegexLong]
print("regex19char 1st = ", regex19char, "\n")
string = ','.join(regex19char)
# regex19char = re.findall(r'\w{19,}', string)  # this is supposed to limit to 19 characters
# print("regex19char 2nd = ", regex19char, "\n")
uniqueRegex19char = list(set(chain(regex19char)))
uniqueRegex19char.sort()
# print(uniqueRegexLong)
# print(uniqueRegex19char)

# converts scraped pdf data to dictionary
pageFileContentDF = pd.DataFrame.from_dict(data=pageFileContent, orient='index', columns=['content'])
# .to_csv('dict_file.csv', header=True)  # writes to csv file for easier viewing

# looks in page files for uniqueRegex19char (also picks up less than 19 character strings) then writes/merges target
# into one file
newFolderSuffix = "SpecSheet"

for i in uniqueRegex19char:
    target = pageFileContentDF[pageFileContentDF['content'].str.contains(i)]
    merger = PyPDF2.PdfFileMerger()
    #
    for pdf in target.index:
        merger.append(pdf)
    newDirectory = str(os.getcwd()) + '/' + newFolderSuffix
    pathlib.Path(newDirectory).mkdir(parents=True, exist_ok=True)
    merger.write(str(newDirectory) + str("/") + str(i) + "_" + newFolderSuffix + ".pdf")

end = timeit.default_timer()
print(end)
print("That took ", round(end - start, 0), "s")

# only need to change newFolderSuffix to type of file in working directory
