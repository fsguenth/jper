from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login.utils import current_user
from lxml import etree
import traceback
from service import models

blueprint = Blueprint('test_xml', __name__)

@blueprint.route('/')
def index():
    if not current_user.is_super:
        abort(401)

    return render_template('test_xml/index.html', allowed_transformation_formats=_available_transformations().keys(), answer={})

@blueprint.route('/transform', methods=['POST'])
def transform():
    if not current_user.is_super:
        abort(401)
    xsl_format = request.values.get('format')
    uploaded_file = request.files.get('file')
    filename = uploaded_file.filename
    data = uploaded_file.stream.read()

    answer = _transform_xml(data, xsl_format)
    answer['filename'] = filename
    answer['xsl_format'] = xsl_format
    if not answer['success']:
        flash(answer['message'], 'error')
    return render_template('test_xml/index.html', allowed_transformation_formats=_available_transformations().keys(), answer=answer)


def _transform_xml(data, xsl_format):
    answer = {
        'success': False,
        'message': None,
        'long_message': None,
        'xml': None
    }

    if not xsl_format in _available_transformations().keys():
        answer['message'] = "Unknown format"
        return answer

    try:
        xslt_root = etree.XML(_available_transformations()[xsl_format])
        transformer = etree.XSLT(xslt_root)
        parser = etree.XMLParser(load_dtd=True, no_network=False)
        transformed_xml = transformer(etree.fromstring(data, parser))
        transformed_xml_formatted = etree.tostring(transformed_xml, encoding="unicode", pretty_print=True)
        answer['success'] = True
        answer['message'] = "XML has been transformed"
        answer['xml'] = transformed_xml_formatted
    except Exception as e:
        answer['message'] = "Could not transform XML"
        answer['long_message'] = repr(e)
        #  for full stack trace
        print(traceback.print_exc())
    return answer



def _available_transformations():
    return {
        'rsc to opus4': models.XSLT.rsc2opus4,
        'rsc to escidoc': models.XSLT.rsc2escidoc,
        'rsc to mets dspace': models.XSLT.rsc2metsdspace,
        'rsc to mets mods': models.XSLT.rsc2metsmods,
        'jats to opus4': models.XSLT.jats2opus4,
        'jats to escidoc': models.XSLT.jats2escidoc,
        'jats to mets dspace': models.XSLT.jats2metsdspace,
        'jats to mets mods': models.XSLT.jats2metsmods
    }



