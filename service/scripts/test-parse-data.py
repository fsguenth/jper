from octopus.modules.epmc.models import JATS
import os.path, argparse, traceback, sys
from lxml import etree

parser = argparse.ArgumentParser(description="sends NISO-JATS file through the JATS parser for testing purposes and "
                                             "prints relevant extracted bibliographic data.")
parser.add_argument("file",
                    help="the JATS file to be tested")
args = parser.parse_args()

# set stdout encoding to ascii to set up exception handling for Unicode errors
# sys.stdout=open(sys.stdout.fileno(), mode='w', encoding='ANSI_X3.4-1968', buffering=1)

if os.path.isfile(args.file):
    xml_tree = etree.parse(args.file)
    jats = JATS(xml=xml_tree)

    try:
        print('\nFile parsed:\t{}'.format(os.path.realpath(args.file)))
        print('Title:\t\t%s' % jats.title)
        print('DOI:\t\t%s' % jats.doi)
        print('in:\t\t{} {}({}), {}'.format(jats.journal, jats.volume, jats.issue, jats.publication_date))
        print('Publisher:\t{}'.format(jats.publisher))
        print('Authors:\t', end="")
        for person in jats.authors:
            print(person['given-names'], person['surname'], end=", ")

        aff_list = []
        for person in jats.contribs:
            if 'affiliations' in person:
                affiliations = person['affiliations']
                for affiliation in affiliations:
                    if affiliation not in aff_list:
                        aff_list.append(affiliation)
        print('\nAffiliations:\t{}'.format(aff_list))

    except UnicodeError:
        print(f'\n\n{traceback.format_exc()}')
        print(f"The bibliographic information to be printed contains Unicode characters. \n\
The encoding for stdout in Python is {sys.stdout.encoding}.\n\
Export the environment variable PYTHONIOENCODING='utf_8' and try again.")

else:
    raise FileNotFoundError(f"No such file: {os.path.realpath(args.file)}")
