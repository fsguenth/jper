from octopus.modules.epmc.models import JATS
import os.path, argparse
from lxml import etree

parser = argparse.ArgumentParser(description="sends NISO-JATS file through the JATS parser for testing purposes and "
                                             "prints relevant extracted bibliographic data.")
parser.add_argument("file",
                    help="the JATS file to be tested")
args = parser.parse_args()

if os.path.isfile(args.file):
    xml_tree = etree.parse(args.file)
    jats = JATS(xml=xml_tree)

    print('\nFile parsed:\t{}'.format(os.path.realpath(args.file)))
    print('Title:\t\t%s' % jats.title)
    print('DOI:\t\t%s' % jats.doi)
    print('in:\t\t{} {}({}), {}'.format(jats.journal, jats.volume, jats.issue, jats.publication_date))
    print('Publisher:\t{}'.format(jats.publisher))
    print('Authors:\t', end="")

    for person in jats.authors:
        print(person['given-names'], person['surname'], end=", ")
    # print('Authors: %s ' % jats.authors)

    aff_list = []
    for person in jats.contribs:
        if 'affiliations' in person:
            affiliations = person['affiliations']
            for affiliation in affiliations:
                if affiliation not in aff_list:
                    aff_list.append(affiliation)
    print('\nAffiliations:\t{}'.format(aff_list))

else:
    raise FileNotFoundError(f"No such file: {os.path.realpath(args.file)}")
