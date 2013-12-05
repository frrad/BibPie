import re
import base64 
import curses

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


#takes .bib file path and returns a list of BibItems
def load(location):
    bibFile = open(location, 'r')
    fileContents = bibFile.read()

    bibliography = []

    # Basic .bib parsing
    for x in xrange(0,  len(fileContents)):
        if fileContents[x:x+2] == "\n@":
            entry = clip(fileContents, x+1)
            # print entry
            bibliography.append(parse(entry))

    # Parsing for BibDesk file information
    for item in bibliography:
        # If there's a file referenced add its path
        # Note: should add check for further files
        if 'Bdsk-File-1' in item.attributes:
            code = item.attributes['Bdsk-File-1'][1:-1]
            decode =  base64.b64decode(code)
            # print "============\n"+decode
            item.file1 = deskParse(decode)

    return bibliography


def drawHits(window, search, hilite):
    selected = 0
    window.clear()
    show = ["Title", "Author","Year"]
    placement = [(1,45),(46,90),(91,97)]
    
    window.addstr(0,0,zipRow(show,placement))

    height, width =  window.getmaxyx()

    hits = searchBib(search, height-1)

    for index in xrange(0,len(hits)):
        if index == hilite:
            window.addstr(index+1,0, makeRow(hits[index],show, placement),curses.A_REVERSE)
            selected = hits[index]
        else:
            window.addstr(index+1,0, makeRow(hits[index],show, placement))

    window.refresh()
    return selected

def searchBib(searchString,stop):
    results = []
    index = 0
    while len(results) < stop and index < len(bibliography):
        if bibMatch(searchString, bibliography[index]):
            results.append(index)
        index+=1
    return results

def bibMatch(string, item):
    string = string.upper()
    terms = string.split()
    match = ""
    for val in item.attributes.values():
        match += val
        match += " "
    
    match = match.upper()

    for term in terms:
        if not term in match:
            return False

    return True

def pad(string, x):
    if len(string) >= x:
        return string[:x]
    while len(string) < x:
        string  = string + " "
    return string

def zipRow(string, locs):
    answer = pad("",locs[0][0])
    for x in range(0,len(string)):
        answer = answer + pad(string[x], locs[x][1] - locs[x][0])
        if x != len(string)-1:
            answer = answer + pad("",locs[x+1][0]- locs[x][1])
    return answer

def makeRow(index, atts, state):
    strangs = []
    item = bibliography[index]
    for att in atts:
        if att in item.attributes.keys():
            strangs.append(item.attributes[att])
        else:
            strangs.append("")
    return zipRow(strangs,state)


#fill info window with appropriate information
def infoRefresh(window, index):
    window.clear()
    window.box()
    
    window.move(1,1)
    window.addstr("Title: ")
    window.addstr(bibliography[index].attributes["Title"])

    window.move(3,1)
    window.addstr("Author: ")
    window.addstr(bibliography[index].attributes["Author"])

    window.refresh()

def main(screen):
    global bibliography
    bibliography = load(biblocation)
    # for item in bibliography:
    #     if hasattr(item, 'file1'):
    #         print item.attributes["Title"]+"="+item.file1["relativePath"]


    screen.refresh() 
    (maxy,maxx) = screen.getmaxyx()

    searchHeight=3
    search = curses.newwin(searchHeight,maxx,0,0) 
    search.box() 
    search.move(1,1)
    search.addstr("Search:")
    search.refresh()

    searchstring = ""

    matchHeight = int (2*maxy/3)
    matches = curses.newwin(matchHeight, maxx,searchHeight,0)
    drawHits(matches, "", 0)

    infoHeight = maxy -matchHeight - searchHeight
    info = curses.newwin(infoHeight,maxx,matchHeight+searchHeight,0)
    infoRefresh(info,0)

    highlight = 0
    currentSelection = 0

    while True:
        search.refresh()
        key = screen.getch()
        (y,x) = search.getyx()
        if key== curses.KEY_BACKSPACE:
            #Check if we would leave screen
            if x<=8:
                continue
            #erace in search
            search.move(y,x-1)
            search.addch(" ")
            search.move(y,x-1)

            searchstring = searchstring[:len(searchstring)-1]
            currentSelection = drawHits(matches, searchstring, highlight)
            infoRefresh(info, currentSelection)
        elif key == curses.KEY_DOWN:
            if highlight < matchHeight -2:
                highlight += 1
                currentSelection = drawHits(matches, searchstring, highlight)
                infoRefresh(info, currentSelection)
        elif key == curses.KEY_UP:
            if highlight > 0:
                highlight -= 1
                currentSelection = drawHits(matches, searchstring, highlight)
                infoRefresh(info, currentSelection)
        else:
            if x > maxx -2:
                continue
            search.addch(key)

            searchstring = searchstring + curses.keyname(key)
            currentSelection = drawHits(matches, searchstring, highlight)
            infoRefresh(info, currentSelection)





try: 
     curses.wrapper(main) 
except KeyboardInterrupt: 
     print "KeyboardInterrupt: Exiting." 
     exit() 