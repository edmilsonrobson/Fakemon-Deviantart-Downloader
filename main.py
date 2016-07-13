import os, bs4, requests, re

min_comments = 0
repetidos = 0
poke_erros = 0
saved_fakemon = 0
digging_max = 500

if not os.path.exists('imgs'):
    os.makedirs('imgs')

def download(img_url):    
    
    try:
        img = requests.get(img_url)

        filename = re.search('/([\-_a-zA-Z0-9]+\.[a-z][a-z][a-z]$)', img_url).group(1)
        print "[OK] Filename: \"%s\"" % filename
        checkstring = "./imgs/" + filename        
        if os.path.isfile(checkstring):
            print "[DUPLICATE] This file has already been downloaded before. Skipping..."
            global repetidos
            repetidos += 1
        else:
            print "[NEW] New Fakemon detected!"
            imageFile = open(os.path.join('imgs', os.path.basename(filename)), 'wb')
            for chunk in img.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
    
            print "[OK] Successfully saved image."
            global saved_fakemon
            saved_fakemon += 1
    except Exception as error:
        print "[ERROR] An unknown error has ocurred. Skipping..."
        print error
        global poke_erros
        poke_erros += 1
        
    

def prepare_to_download(src):    
    req = requests.get(src)
    soup = bs4.BeautifulSoup(req.text, "html.parser")

    number_field = soup.find("dt",text="Comments")
    #print src
    try:
        number = int(number_field.find_next_sibling('dd').text.strip())    
        link = soup.select('.dev-view-deviation > img')[0]
        img_url = link.get('src')
        print "------------------------------------------------------"
        print img_url
        
        if (number >= min_comments):
            print "[OK] Preparing to download..."
            download(img_url)
        else:
            print "[IGNORED] Less than %d comments (this post has: %d)" % (min_comments, number)
    except Exception as error:
        print "[ERROR] There was an error trying to read the post. Skipping post..."
        print error
        global poke_erros
        poke_erros += 1

    
url = "http://www.deviantart.com/browse/all/digitalart/pixelart/?order=5&q=fakemon&offset="

offset = 0

min_comments = int(raw_input("Minimum number of comments to download Fakemon? (Ex: 3)\n"))
digging_max = int(raw_input("Number of Fakemon to dig, starting from newest?(Ex: 500, Min: 20)\n"))

req = requests.get(url + str(offset))

soup = bs4.BeautifulSoup(req.text, "html.parser")

print "Digging for %d~ Fakemon..." % digging_max
while offset < digging_max:
    for src in soup.select('.torpedo-thumb-link'):
        prepare_to_download(src.get('href'))
        offset += 1
    req = requests.get(url + str(offset))

    soup = bs4.BeautifulSoup(req.text, "html.parser")
    
print "------------------------------------------------------"

print "\nEnd of digging.\n"
print "Total Fakemon: %d" % int(offset)
percent = float(float(saved_fakemon)/float(offset))*100.0
print "NEW Fakemon saved: %d (%f%% do total)" % (int(saved_fakemon), percent)
print "IGNORED Duplicated Fakemon: %d" % repetidos
print "Failed Fakemon downloads: %d" % poke_erros
