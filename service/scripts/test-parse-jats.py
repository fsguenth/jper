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
    normalize = lambda x: " ".join(str(x).split())
    try:
        print('\nFile parsed:\t{}'.format(os.path.realpath(args.file)))
        print('Title:\t\t%s' % normalize(jats.title))
        print('DOI:\t\t%s' % jats.doi)
        print('ISSN:\t\t{}'.format(jats.issn))
        print('in:\t\t{} {}({})'.format(normalize(jats.journal), jats.volume, jats.issue))
        print("on:\t\t{}".format(jats.publication_date))
        print('Publisher:\t{}'.format(jats.publisher))
        print('License:\t{}'.format(jats.get_licence_details()))
        print('Emails:\t\t{}'.format(jats.emails))
        print('Authors:')
        for person in jats.authors:
            print(person['given-names'], person['surname'], end="")
            if person.get('orcid', None) is not None:
                print(", ORICD: {}".format(person['orcid']))
            else: print()
            affs = person.get('affiliations', [])
            print("Affiliations:", "; ".join(affs))
            ids = {}
            if person.get('ror', None) is not None:
                ids['ROR'] = person['ror']
            if person.get('ringgold', None) is not None:
                ids['Ringgold'] = person['ringgold']
            if len(ids) > 0: print(", ".join([ kind+": "+str(id) for kind, id in ids.items() ]))
            print()

    except UnicodeError:
        print(f'\n\n{traceback.format_exc()}')
        print(f"The bibliographic information to be printed contains Unicode characters. \n\
The encoding for stdout in Python is {sys.stdout.encoding}.\n\
Export the environment variable PYTHONIOENCODING='utf_8' and try again.")

    except:
        print(f'\n\n{traceback.format_exc()}')

else:
    raise FileNotFoundError(f"No such file: {os.path.realpath(args.file)}")
