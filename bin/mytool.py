from bs4 import BeautifulSoup
import codecs

def loadBS(name, encoding = 'utf-8'):
    with codecs.open(name, 'r', encoding) as f:
        return BeautifulSoup(f)

def getfile(name):
    with codecs.open(name, 'r', 'utf-8') as f:
        return f.read()

