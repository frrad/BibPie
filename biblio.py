import re

biblocation = 'Index.bib'

class BibItem:
   def __init__(self, category):
      self.category = category


# Extract everything from file starting at index and ending with first 
# set of brackets encountered
def clip(file, index):
    start = index
    proceed = True
    count = 0
    while proceed or count != 0:
        # print file[index], proceed, count
        if file[index] == "{":
            proceed = False
            count += 1
        if file[index]== "}":
            count -= 1
        index += 1
    return file[start:index]

def parse(text):
    match = re.search("@.*?{",text,flags=0)
    if match:
        print "\n\nItem Category: "+match.group()[1:-1]
    attributes = re.finditer("(?P<key>.*?)=(?P<val>.*)",text,flags=0)
    for obj in attributes:
        entry = obj.groupdict()
        print entry["key"].strip('\t')
        print clip(entry["val"],0).strip(" ")

def main():
    bibFile = open(biblocation, 'r')
    fileContents = bibFile.read()

    bibliography = []

    for x in xrange(0,  len(fileContents)):
        if fileContents[x:x+2] == "\n@":
            entry = clip(fileContents, x+1)
            # print entry
            bibliography.append(parse(entry))

    print bibliography


main() 