from octopus.modules.epmc.models import JATS
import sys, os.path
from lxml import etree

try:
    filename = sys.argv[1]
except:
    raise SyntaxError("Missing argument: pass filename.")

if os.path.isfile(filename):
    xml_tree = etree.parse(filename)
    jats = JATS(xml=xml_tree)
    print('Title: %s ' % jats.title)
    print('DOI:   %s ' % jats.doi)
    print('Contributers: %s ' % jats.contribs)
    print('Authors: %s: ' % jats.authors)
    print('Title: %s: \n' % jats.title)

else:
    raise OSError("File does not exist.")