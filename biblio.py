import re, base64

biblocation = 'Index.bib'

class BibItem:

    def __init__(self, category):
        self.category = category

    def show(self):
        print "===================="
        print "Category: "+self.category
        # print "Raw: "+self.raw
        print "Attributes"
        print self.attributes
        if hasattr(self, 'file1'):
            print "File 1"
            print self.file1


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
        if index >= len(file):
            break
    return file[start:index]

def parse(text):
    match = re.search("@.*?{",text,flags=0)
    category = match.group()[1:-1]
    # print "\n\nItem Category: "+category
    item = BibItem(category)

    item.raw = text

    parsed = re.finditer("(?P<key>.*?)=(?P<val>.*)",text,flags=0)

    info = dict()

    for obj in parsed:
        entry = obj.groupdict()
        key = entry["key"].strip('\t ')
        value = clip(entry["val"],0).strip(" ")
        info[key] = value

    item.attributes = info

    return item

def deskParse(data):
    store = dict()
    pathS = data.find("\\relativePathYaliasData")
    pathE = data.find("\xD2\x09\x17\x18\x19")
    store["relativePath"] = data[pathS+26:pathE]
    return store



def main():
    bibFile = open(biblocation, 'r')
    fileContents = bibFile.read()

    bibliography = []

    for x in xrange(0,  len(fileContents)):
        if fileContents[x:x+2] == "\n@":
            entry = clip(fileContents, x+1)
            # print entry
            bibliography.append(parse(entry))

    for item in bibliography:
        if 'Bdsk-File-1' in item.attributes:
            code = item.attributes['Bdsk-File-1'][1:-1]
            decode =  base64.b64decode(code)
            # print "============\n"+decode
            item.file1 = deskParse(decode)
        print item.attributes["Title"]+"="+item.file1["relativePath"]


main() 