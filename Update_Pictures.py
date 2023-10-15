import sqlite3
import os

def getImageFiles(imagesRoot):
    imageFiles = {}
    for path, subdirs, files in os.walk(imagesRoot):
        for name in files:
            # print(path, name, os.path.join(path, name))
            if name in imageFiles:
                print("DUPLICATE FILENAME: ", name)
                break
            else:
                imageFiles[name] = os.path.join(path, name)

    print('Found', str(len(imageFiles)), 'files in directory', imagesRoot)

    return imageFiles

def getDBImages(mcfxFile):
    con = sqlite3.connect(mcfxFile)
    cur = con.cursor()
    res = cur.execute("SELECT Filename, Data FROM Files WHERE Filename LIKE '%.jpeg' OR Filename LIKE '%.jpg'")
        
    dbImages = res.fetchall()

    print('Read', str(len(dbImages)), 'files from', mcfxFile)
    cur.close()
    con.close()
    
    return dbImages

def getCleanedDBImageFilenames(dbImages):
    originalNames = list(dbImages[i][0] for i in range(len(dbImages)))
    
    cleanedNames = (n.replace('_1_', '_') for n in originalNames)
    cleanedNames = ( n[0:n.find('adjust-horizon')-1] + '.jpg' if 'adjust-horizon' in n else n for n in cleanedNames)

    return dict(zip(cleanedNames, originalNames))

def match(imageFiles, dbImageFilenames):
    matching = {}

    for image in imageFiles:
        for dbImage in dbImageFilenames:
            if image.lower() in dbImage.lower():
                matching[dbImageFilenames[dbImage]] = imageFiles[image]

    print('Matched', str(len(matching)), 'of', str(len(dbImageFilenames)), 'images.')
    return matching

def readLocalFile(localFileName):
    with open(localFileName, "rb") as f:
        data = f.read()

    return data

def updateInDB(mcfxFile, matchedFilenames):
    try:
        con = sqlite3.connect(mcfxFile)
        cur = con.cursor()

        for dbImageFilename in matchedFilenames:
            localFilename = matchedFilenames[dbImageFilename]

            data = readLocalFile(localFilename)

            query = "UPDATE Files SET Data = ? WHERE Filename = ?"
            data_tuple = (data, dbImageFilename)
            res = cur.execute(query, data_tuple)
            
            print('Updated', dbImageFilename, 'to', localFilename)

            con.commit()

        cur.close()
        
    finally:
        if con:
            con.close()


# --------------- MAIN -------------------

# Config
mcfxFilename = 'D:\\Software\Programmierung\\CEWE SQLite\\test.mcfx'
localImagesPath = 'D:\\Bilder\\__2023\\Weltreise\\02 Neuseeland Album'

# Read
imageFiles = getImageFiles(localImagesPath)
dbImages = getDBImages(mcfxFilename)
dbImageFilenames = getCleanedDBImageFilenames(dbImages)

matchedFilenames = match(imageFiles, dbImageFilenames)
notMatched = list(n for n in dbImageFilenames.values() if not n in matchedFilenames)
print('NOT MATCHED:', notMatched)

# Update
updateInDB(mcfxFilename, matchedFilenames)