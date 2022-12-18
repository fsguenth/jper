import json
import os
import io
import re
import tempfile
import csv
from datetime import datetime
from statistics import mean
from pathlib import Path
import chardet
import openpyxl
import itertools
import uuid
from octopus.core import app
from octopus.lib import dates
from flask import Blueprint, abort, render_template, request, redirect, url_for, send_file, flash
from flask_login.utils import current_user
from service.models.ezb import LICENSE_TYPES, Alliance, License
from service.models.license_management import LicenseManagement

blueprint = Blueprint('manage_license', __name__)
ALLOWED_DEL_STATUS = ["validation failed", "archived", "validation passed"]


@blueprint.app_template_filter()
def pretty_json(value, indent=2):
    return json.dumps(value, indent=indent, ensure_ascii=False)


@blueprint.app_template_filter()
def display_order(active_element, list_len):
    reversed_order = list(reversed(range(1, list_len+1)))
    reversed_order.remove(active_element)
    reversed_order.insert(0, active_element)
    return reversed_order


@blueprint.route('/')
def details():
    if not current_user.is_super:
        abort(401)

    managed_licenses = LicenseManagement.pull_all_records()

    return render_template('manage_license/details.html',
                           allowed_lic_types=LICENSE_TYPES,
                           allowed_del_status=ALLOWED_DEL_STATUS,
                           managed_licenses=managed_licenses)


@blueprint.route('/view_license')
def view_license():
    rec_id = request.values.get('record_id')
    if rec_id:
        rec = License.pull(rec_id)
        if not rec:
            data = {'Error': f"Record {rec_id} not found"}
        else:
            data = rec.data
    else:
        data = {'Error': f"Please specify a record_id"}
    return render_template('manage_license/view_license.html', rec=data)


@blueprint.route('/download_license_file')
def download_license_file():
    if not current_user.is_super:
        abort(401)

    manager_id = request.values.get('management_id')
    record_id = request.values.get('record_id')

    management_record = LicenseManagement.pull(manager_id)
    for lic in management_record.licenses:
        if lic['record_id'] == record_id:
            dir_path, file_path = _get_file_path(lic['file_name'])

            # check file exist
            if not file_path.is_file():
                app.logger.warning(f'file not found [{file_path.as_posix()}]')
                abort(404)

            # define mimetype
            mimetype = _get_mime_type(file_path)

            return send_file(io.BytesIO(file_path.read_bytes()),
                             as_attachment=True, attachment_filename=lic['file_name'],
                             mimetype=mimetype)
    abort(404)


@blueprint.route('/upload_license', methods=['POST'])
def upload_license():
    if not current_user.is_super:
        abort(401)

    license_type = request.values.get('lic_type')
    uploaded_file = request.files.get('file')
    license_name = request.values.get('license_name', '')
    admin_notes = request.values.get('admin_notes', '')
    ezb_id = request.values.get('ezb_id', '')

    messages = [f"Uploading license file for {ezb_id}"]

    ans, msg = _upload_new_license_file(license_type, uploaded_file, license_name, admin_notes, ezb_id)
    messages.append(msg)
    if not ans:
        flash("<br/>".join(messages), 'error')
    else:
        flash("<br/>".join(messages), 'success')
    return redirect(url_for('manage_license.details'))


@blueprint.route("/update_license", methods=['POST'])
def update_license():
    if not current_user.is_super:
        abort(401)

    uploaded_file = request.files.get('file')
    management_id = request.values.get('management_id')
    management_record = LicenseManagement.pull(management_id)

    messages = [f"Updating license file for {management_record.ezb_id}"]

    ans, msg = _update_license_file(management_record.type, uploaded_file, management_record)
    messages.append(msg)
    if not ans:
        flash("<br/>".join(messages), 'error')
    else:
        flash("<br/>".join(messages), 'success')
    return redirect(url_for('manage_license.details'))


@blueprint.route("/activate_license", methods=['POST'])
def activate_license():
    pass


@blueprint.route("/archive_license")
def archive_license():
    pass


@blueprint.route("/delete_license")
def delete_license():
    pass


@blueprint.route('/view_participant')
def view_participant():
    rec_id = request.values.get('record_id')
    if rec_id:
        rec = Alliance.pull(rec_id)
        if not rec:
            data = {'Error': f"Record {rec_id} not found"}
        else:
            data = rec.data
    else:
        data = {'Error': f"Please specify a record_id"}
    return render_template('manage_license/view_participant.html', rec=data)


@blueprint.route('/download_participant_file')
def download_participant_file():
    if not current_user.is_super:
        abort(401)

    manager_id = request.values.get('id')
    record_id = request.values.get('record_id')

    management_record = LicenseManagement.pull(manager_id)
    for par in management_record.participants:
        if par['record_id'] == record_id:
            dir_path, file_path = _get_file_path(par['file_name'])

            # check file exist
            if not file_path.is_file():
                app.logger.warning(f'file not found [{file_path.as_posix()}]')
                abort(404)

            # define mimetype
            mimetype = _get_mime_type(file_path)

            return send_file(io.BytesIO(file_path.read_bytes()),
                             as_attachment=True, attachment_filename=par['file_name'],
                             mimetype=mimetype)
    abort(404)


@blueprint.route("/upload_participant")
def upload_participant():
    pass


@blueprint.route("/update_participant")
def update_participant():
    pass


@blueprint.route("/activate_participant")
def activate_participant():
    pass


@blueprint.route("/archive_participant")
def archive_participant():
    pass


@blueprint.route("/delete_participant")
def delete_participant():
    pass


def _upload_new_license_file(lic_type, uploaded_file, license_name, admin_notes, ezb_id):
    if uploaded_file is None:
        return False, 'parameter "file" not found'

    # create management record. It should not exist.
    ans, msg, management_record = _create_management_record(ezb_id, license_name, admin_notes, lic_type)
    if not ans:
        return ans, msg

    ans, msg = _update_license_file(lic_type, uploaded_file, management_record)
    return ans, msg


def _update_license_file(lic_type, uploaded_file, management_record):
    # load lic_file
    filename = uploaded_file.filename
    file_bytes = uploaded_file.stream.read()

    # save file
    version_datetime = datetime.now()
    versioned_filename = _save_file(filename, file_bytes, version_datetime)

    license_record = _create_license_hash(version_datetime, versioned_filename)

    ans, msg, license_record, rows = _validate_license_file(license_record, lic_type, filename, file_bytes, management_record.ezb_id)

    license_record['validation_notes'] = _convert_to_string(license_record['validation_notes'])
    management_record.add_license(license_record)
    if not ans:
        version_record = {
            'version': management_record.license_version,
            'status': "validation failed"
        }
        management_record.add_license_version(version_record)
        # Save management record with license details and return
        management_record.save()
        return False, f"Validation failed for license #{management_record.ezb_id}"

    # license is valid
    # create a new license
    license_data = _extract_license_data(rows)
    license_id = management_record.record_id(management_record.license_version)
    _create_license(license_id, management_record.ezb_id, management_record.name, lic_type, license_data)

    # activate the license
    management_record.activate_license(management_record.license_version)
    management_record.save()
    return True, f'License #{management_record.ezb_id} has been created and activated'


def _save_file(filename, file_bytes, version_datetime):
    versioned_filename = _create_versioned_filename(filename, version_datetime)
    dir_path, file_path = _get_file_path(filename)
    if not dir_path.exists():
        dir_path.mkdir(exist_ok=True, parents=True)
    file_path.write_bytes(file_bytes)
    return versioned_filename


def _get_file_path(filename):
    file_dir = app.config.get('LICENSE_FILE_DIR', '/data/license_files')
    dir_path = Path(file_dir)
    file_path = dir_path.joinpath(filename)
    return dir_path, file_path


def _create_versioned_filename(filename, version_datetime):
    if not version_datetime:
        version_datetime = datetime.now()
    file_name, file_extension = os.path.splitext(filename)
    date_str = version_datetime.strftime('%Y%m%dT%H%M%S')
    return f'{file_name}_{date_str}{file_extension}'


def _create_management_record(ezb_id, license_name, admin_notes, lic_type):
    management_record = LicenseManagement.pull_by_ezb_id(ezb_id)
    if management_record:
        return False, "ezb_id #{ezb_id} already exists", management_record
    management_record = LicenseManagement()
    management_record.id = uuid.uuid4().hex
    management_record.ezb_id = ezb_id
    management_record.name = license_name
    management_record.admin_notes = admin_notes
    if lic_type in LICENSE_TYPES:
        management_record.type = lic_type
    return True, '', management_record


def _create_license_hash(version_datetime, file_name):
    return {
        "file_name": file_name,
        "name": '',
        "uploaded_date": dates.format(version_datetime),
        "validation_notes": [],
        "validation_status": 'validation failed',
    }


def _validate_license_file(license_record, license_type, filename, file_bytes, ezb_id):
    license_record['validation_status'] = "validation failed"
    if not license_record.get('validation_notes', []):
        license_record['validation_notes'] = []

    # check license type is valid
    if license_type not in LICENSE_TYPES:
        msg = f"Invalid license type {license_type}"
        license_record['validation_notes'].append(msg)
        return False, msg, license_record, None

    # check file type is valid (csv, tsv, xls, xlsx)
    filename_lower = filename.lower().strip()
    _, file_extension = os.path.splitext(filename_lower)

    if file_extension not in ['.tsv', '.csv', '.xls', '.xlsx']:
        msg = f"Invalid file format {filename}"
        license_record['validation_notes'].append(msg)
        return False, msg, license_record, None

    if file_extension in ['.xls', '.xlsx']:
        rows = _load_rows_by_xls_bytes(file_bytes)
    else:
        csv_str = _decode_csv_bytes(file_bytes)
        rows = _load_rows_by_csv_str(csv_str)

    # validate license file contents
    ans, msg, license_record = _validate_lic_lrf(rows, ezb_id, license_record)
    if not ans:
        return False, msg, license_record, None
    license_record["validation_status"] = "validation passed"
    return True, "License file is valid", license_record, rows


def _decode_csv_bytes(csv_bytes):
    encoding = chardet.detect(csv_bytes)['encoding']
    if encoding == 'ISO-8859-1':
        return csv_bytes.decode(encoding='iso-8859-1', errors='ignore')
    else:
        if encoding != 'utf-8':
            app.logger.warning(f'unknown encoding[{encoding}], decode as utf8')
        return csv_bytes.decode(encoding='utf-8', errors='ignore')


def _extract_name_ezb_id_by_line(line):
    results = re.findall(r'.+:\s*(.+?)\s*\[(.+?)\]', line)
    if len(results) and len(results[0]) == 2:
        name, ezb_id = results[0]
        return name.strip(), ezb_id.strip()
    else:
        return None, None


def _load_rows_by_csv_str(csv_str):
    """ Convert csv string to row list
    auto guess delimiter "\t" or ","
    """

    def _load_rows(delimiter):
        return [row for row in csv.reader(io.StringIO(csv_str),
                                          delimiter=delimiter,
                                          quoting=csv.QUOTE_ALL)]

    rows = _load_rows('\t')
    if mean([len(r) == 1 for r in rows]) < 0.5:
        # use \t if 50% rows have been split more than one column
        return rows
    else:
        return _load_rows(',')


def _to_csv_str(headers, data):
    dict_rows = [{headers[col_idx]: row[col_idx] for col_idx in range(len(headers))}
                 for row in data]

    tmp_file_path = tempfile.mkstemp(prefix='__lc__')[1]
    with open(tmp_file_path, 'w') as tmp_file:
        writer = csv.DictWriter(tmp_file, fieldnames=headers, delimiter='\t', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in dict_rows:
            writer.writerow(row)

    with open(tmp_file_path, 'r') as tmp_file:
        table_str = tmp_file.read()

    os.remove(tmp_file_path)
    return table_str


def _load_rows_by_xls_bytes(xls_bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(xls_bytes))
    sheet = workbook.active
    rows = [[c.value for c in r] for r in sheet.rows]
    return rows


def _validate_lic_lrf(rows, ezb_id, license_record):
    n_cols = 9
    header_row_idx = 4

    if len(rows) == 0 or len(rows[0]) == 0:
        license_record['validation_notes'].append('first line not found')
        return False, "Error validating license file", license_record

    if len(rows) < header_row_idx + 1:
        license_record['validation_notes'].append('header not found')
        return False, "Error validating license file", license_record

    header_row = rows[header_row_idx]
    filtered_header_row = list(filter(None, header_row))
    if not filtered_header_row:
        license_record['validation_notes'].append(
            f'Header row is missing. The header should be row {header_row_idx + 1}.')
        return False, "Error validating license file", license_record

    if len(header_row) < n_cols:
        license_record['validation_notes'].append(f'csv should have {n_cols} columns')
        return False, "Error validating license file", license_record

    # check mandatory header
    missing_headers = {'Titel', 'Verlag', 'E-ISSN', 'P-ISSN', 'Embargo', 'erstes Jahr', 'letztes Jahr'} - set(
        header_row)
    if missing_headers:
        license_record['validation_notes'].append(f'missing header {missing_headers}')
        return False, "Error validating license file", license_record

    # CHeck journal year start and year end are integers or empty.
    # It is used during routing.
    validate_fn_list = [
        ValidEmptyOrInt('erstes Jahr', header_row),
        ValidEmptyOrInt('letztes Jahr', header_row),
    ]

    row_validator_list = itertools.product(rows[header_row_idx + 1:], validate_fn_list)
    err_msgs = (validator.validate(row) for row, validator in row_validator_list)
    err_msgs = list(set(filter(None, err_msgs)))
    license_record['validation_notes'].append("\n".join(err_msgs))

    # get warnings
    missing_headers = _check_all_lic_rows_exist(rows)
    if missing_headers:
        license_record['validation_notes'].append(
            f"Warning: Following headers are missing (headers are case sensitive): {missing_headers}")

    name, file_ezb_id = _extract_name_ezb_id_by_line(rows[0][0])
    if not name or not file_ezb_id:
        license_record['validation_notes'].append('Warning: name and ezb_id not found')
    license_record['name'] = name

    # handle ezb_id mismatch
    if ezb_id != file_ezb_id:
        license_record['validation_notes'].append(
            f"Warning, ezb id does not match with license file. Ignoring ezb id in file {file_ezb_id}.")

    if err_msgs:
        return False, "Error validating license file", license_record
    return True, "", license_record


def _check_all_lic_rows_exist(rows):
    # check all headers
    all_headers = {'EZB-Id', 'Titel', 'Verlag', 'Fach', 'Schlagworte', 'E-ISSN', 'P-ISSN', 'ZDB-Nummer',
                   'FrontdoorURL', 'Link zur Zeitschrift', 'erstes Jahr', 'erstes volume', 'erstes issue',
                   'letztes Jahr', 'letztes volume', 'letztes issue', 'Embargo'}
    header_row_idx = 4
    header_row = rows[header_row_idx]
    missing_headers = all_headers - set(header_row)
    return missing_headers


class ValidEmptyOrInt:
    def __init__(self, col_name, header_row):
        self.col_name = col_name
        self.col_idx = _find_idx(header_row, col_name)

    def validate(self, row: list):
        _val = row[self.col_idx].strip()
        if not _val or _val.isdigit():
            return None
        else:
            return f'column [{self.col_name}][{_val}] must be int'


def _find_idx(header_row, col_name):
    for i, v in enumerate(header_row):
        if v == col_name:
            return i


def _extract_license_data(rows):
    headers = rows[4]
    data = rows[5:]
    table_str = _to_csv_str(headers, data)
    name, ezb_id = _extract_name_ezb_id_by_line(rows[0][0])
    return {
        "ezb_id": ezb_id,
        "name": name,
        "table_str": table_str
    }


def _create_license(license_id, ezb_id, license_name, license_type, license_data, license_status="active"):
    # create license by csv file
    lic = License()
    lic.id = license_id
    lic.set_license_data(ezb_id, license_name,
                         type=license_type, csvfile=io.StringIO(license_data['table_str']),
                         init_status=license_status)
    lic.save()


def _get_mime_type(file_path):
    # define mimetype
    _path_str = file_path.as_posix().lower()
    if _path_str.endswith('.xls'):
        mimetype = 'application/vnd.ms-excel'
    elif _path_str.endswith('.xlsx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        mimetype = 'text/csv'
    return mimetype


def _convert_to_string(validation_notes):
    if not type(validation_notes) == list:
        validation_notes = [validation_notes]
    return "<br\>".join(validation_notes)