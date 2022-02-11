import csv
import time
import dataclasses
import io
import itertools
import logging
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, Callable

import chardet
import openpyxl
from flask import Blueprint, abort, render_template, request, redirect, url_for
from flask_login.utils import current_user

from octopus.core import app
from octopus.lib import dates
from service import models
from service.__utils import ez_dao_utils
from service.__utils.ez_dao_utils import object_query_first
from service.models import License
from service.models.ezb import LRF_TYPES, LicRelatedFile, Alliance

blueprint = Blueprint('license-manage', __name__)

log: logging.Logger = app.logger


def _create_versioned_filename(filename: str,
                               version_datetime: datetime) -> str:
    idx = filename.rfind('.')
    if idx == -1:
        name = filename
        fmt = ''
    else:
        name = filename[:idx]
        fmt = filename[idx + 1:]

    date_str = version_datetime.strftime('%Y%m%dT%H%M%S')
    return f'{name}.{date_str}.{fmt}'


@dataclasses.dataclass
class LicenseFile:
    ezb_id: str
    name: str
    table_str: str  # table data as csv string
    filename: str
    version_datetime: datetime = dataclasses.field(default_factory=datetime.now)

    @property
    def versioned_filename(self):
        return _create_versioned_filename(self.filename,
                                          self.version_datetime)


@dataclasses.dataclass
class ParticipantFile:
    lic_ezb_id: str
    table_str: str
    filename: str
    version_datetime: datetime = dataclasses.field(default_factory=datetime.now)

    @property
    def versioned_filename(self):
        return _create_versioned_filename(self.filename,
                                          self.version_datetime)


@dataclasses.dataclass
class ActiveLicRelatedRow:
    lic_lrf_id: str
    lic_filename: str
    lic_upload_date: str
    lic_type: str
    parti_lrf_id: str
    parti_filename: str
    parti_upload_date: str


def abort_if_not_admin():
    # KTODO change it to Decorators
    if not current_user.is_super:
        abort(401)


def _split_list_by_cond_fn(cond_fn: Callable[[any], bool],
                           obj_list: list[any], ) -> tuple[Iterable, Iterable]:
    return filter(cond_fn, obj_list), itertools.filterfalse(cond_fn, obj_list)


def _to_active_lr_rows(lic_lrf: LicRelatedFile,
                       parti_lr_files: list[LicRelatedFile]) -> ActiveLicRelatedRow:
    parti = [lr for lr in parti_lr_files if lr.lic_related_file_id == lic_lrf.id]
    parti = parti and parti[0]
    if parti:
        parti_filename = parti.file_name
        parti_upload_date = parti.upload_date
        parti_lrf_id = parti.id
    else:
        parti_filename = ''
        parti_upload_date = ''
        parti_lrf_id = ''

    return ActiveLicRelatedRow(lic_lrf.id, lic_lrf.file_name, lic_lrf.upload_date, lic_lrf.type,
                               parti_lrf_id, parti_filename, parti_upload_date)


@blueprint.route('/')
def details():
    abort_if_not_admin()

    lic_related_files = [l for l in LicRelatedFile.object_query()]
    active_lr_files, inactive_lr_files = _split_list_by_cond_fn(lambda l: l.status == 'active',
                                                                lic_related_files)
    active_lr_files = list(active_lr_files)

    # if lic_related_file_id is None, this record must be license file
    lic_lr_files, parti_lr_files = _split_list_by_cond_fn(lambda l: l.lic_related_file_id is None,
                                                          active_lr_files)
    parti_lr_files = list(parti_lr_files)

    # prepare active_list
    active_list: Iterable[ActiveLicRelatedRow] = (_to_active_lr_rows(lic_lrf, parti_lr_files)
                                                  for lic_lrf in lic_lr_files)
    return render_template('license_manage/details.html',
                           allowed_lic_types=LRF_TYPES,
                           active_list=active_list,
                           history_list=(l.data for l in inactive_lr_files),
                           )


def _load_lic_file_by_csv_bytes(file_bytes: bytes, filename: str) -> LicenseFile:
    csv_str = _decode_csv_bytes(file_bytes)

    first_line = csv_str[:csv_str.find('\n')]
    name, ezb_id = _extract_name_ezb_id_by_line(first_line)

    # find header line index
    header_idx = 0
    for _ in range(4):  # header in line 4
        header_idx = csv_str.find('\n', header_idx + 1)
        if header_idx == -1:
            raise ValueError('header index not found')

    table_str = csv_str[header_idx + 1:]
    return LicenseFile(ezb_id, name, table_str, filename=filename)


def _convert_data_to_csv_str(headers: list, data: Iterable[list]) -> str:
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


def _load_rows_by_xls_bytes(xls_bytes: bytes) -> list[list]:
    workbook = openpyxl.load_workbook(io.BytesIO(xls_bytes))
    sheet = workbook.active
    rows = [[c.value for c in r] for r in sheet.rows]
    return rows


def _load_lic_file_by_xls_bytes(xls_bytes: bytes, filename: str) -> LicenseFile:
    rows = _load_rows_by_xls_bytes(xls_bytes)
    headers = rows[4]
    data = rows[5:]
    table_str = _convert_data_to_csv_str(headers, data)

    name, ezb_id = _extract_name_ezb_id_by_line(rows[0][0])
    return LicenseFile(ezb_id, name, table_str, filename=filename)


@blueprint.route('/upload-license', methods=['POST'])
def upload_license():
    if request.values.get('lic_type') not in LRF_TYPES:
        abort(400, f'Invalid parameter "lic_type" [{request.values.get("lic_type")}]')

    # request values
    lic_type = request.values['lic_type']
    admin_notes = request.values.get('admin_notes', '')

    abort_if_not_admin()
    if 'file' not in request.files:
        abort(400, 'parameter "file" not found')

    # load lic_file
    filename = request.files['file'].filename
    file_bytes = request.files['file'].stream.read()
    lic_file = None
    if filename.lower().endswith('.csv'):
        lic_file = _load_lic_file_by_csv_bytes(file_bytes, filename=filename)
    elif any(filename.lower().endswith(fmt) for fmt in ['xls', 'xlsx']):
        lic_file = _load_lic_file_by_xls_bytes(file_bytes, filename=filename)
    else:
        abort(400, f'Invalid file format [{filename}]')

    # save file to hard disk
    _save_lic_related_file(lic_file.versioned_filename, file_bytes)

    # save license to db
    lic = _load_or_create_lic(lic_file.ezb_id)
    lic.set_license_data(lic_file.ezb_id, lic_file.name,
                         type=lic_type, csvfile=lic_file.table_str,
                         init_status='inactive')

    # save lic_related_file to db
    lic_related_file_raw = dict(file_name=lic_file.versioned_filename,
                                type=lic_type,
                                ezb_id=lic_file.ezb_id,
                                status='validation passed',
                                admin_notes=admin_notes,
                                record_id=lic.id,
                                upload_date=dates.format(lic_file.version_datetime), )
    _save_new_lrf(lic_related_file_raw)
    return redirect(url_for('license-manage.details'))


def _save_new_lrf(lrf_raw: dict, blocking=True):
    new_lrf = models.LicRelatedFile(raw=lrf_raw)
    new_lrf.save()
    if blocking:
        ez_dao_utils.wait_unit_id_found(LicRelatedFile, new_lrf.id)


@blueprint.route('/active-lic-related_file', methods=['POST'])
def active_lic_related_file():
    abort_if_not_admin()

    # active lic_related_file
    lrf_id = request.values.get('lrf_id')
    lr_file = _check_and_find_lic_related_file(lrf_id)
    lr_file.status = 'active'
    lr_file.save()
    # KTODO what if related lic already have active parti

    # active
    record_cls = Alliance if lr_file.lic_related_file_id else License
    record = object_query_first(record_cls, lr_file.record_id)
    if record:
        record.status = 'active'
        record.save()
    else:
        log.warning(f'license / alliance not found record_id[{lr_file.record_id}] lrf_id[{lrf_id}]')

    _wait_unit_status(lr_file.id, 'active')
    return redirect(url_for('license-manage.details'))


def _wait_unit_status(lrf_id: str, target_status):
    def _is_updated():
        _obj = object_query_first(LicRelatedFile, lrf_id)
        if _obj:
            return _obj.status == target_status
        return False

    ez_dao_utils.wait_unit(_is_updated)


def _check_and_find_lic_related_file(lrf_id: str) -> LicRelatedFile:
    if not lrf_id:
        abort(404)

    lic_file: LicRelatedFile = object_query_first(LicRelatedFile, lrf_id)
    if not lic_file:
        log.warning(f'lic_related_file not found lrf_id[{lrf_id}]')
        abort(404)

    return lic_file


def _load_parti_csv_str_by_xls_bytes(xls_bytes: bytes) -> str:
    rows = _load_rows_by_xls_bytes(xls_bytes)
    if len(rows) == 0:
        return ''

    table_str = _convert_data_to_csv_str(rows[0], rows[1:])
    return table_str


def _save_lic_related_file(filename: str, file_bytes: bytes):
    path = app.config.get('LIC_RELATED_FILE_DIR', '/data/lic_related_file')
    path = Path(path)
    if not path.exists():
        path.mkdir(exist_ok=True, parents=True)
    path.joinpath(filename).write_bytes(file_bytes)


@blueprint.route('/upload-participant', methods=['POST'])
def upload_participant():
    abort_if_not_admin()

    lic_lrf_id = request.values.get('lrf_id')
    lic_lr_file: LicRelatedFile = _check_and_find_lic_related_file(lic_lrf_id)

    # validate
    lic: License = object_query_first(License, lic_lr_file.record_id)
    lic_ezb_id = lic and lic.get_first_ezb_id()
    if lic_ezb_id is None:
        log.warning(f'ezb_id not found -- {lic_lr_file.record_id}')
        abort(404)

    # load parti_file
    filename = request.files['file'].filename
    file_bytes = request.files['file'].stream.read()
    csv_str: str = None
    if filename.lower().endswith('.csv'):
        csv_str = _decode_csv_bytes(file_bytes)
    elif any(filename.lower().endswith(fmt) for fmt in ['xls', 'xlsx']):
        csv_str = _load_parti_csv_str_by_xls_bytes(file_bytes)
    else:
        abort(400, f'Invalid file format [{filename}]')
    parti_file = ParticipantFile(lic_lrf_id, csv_str, filename)

    # save file to hard disk
    _save_lic_related_file(parti_file.versioned_filename, file_bytes)

    # save participant to db
    alliance = Alliance.pull_by_key('identifier.id', lic_ezb_id) or Alliance()
    alliance.set_alliance_data(lic_lr_file.record_id, lic_ezb_id, csvfile=csv_str,
                               init_status='inactive')

    # save lic_related_file to db
    lr_file_raw = dict(file_name=parti_file.versioned_filename,
                       type=None,
                       ezb_id=lic_ezb_id,
                       status='validation passed',
                       admin_notes=None,
                       record_id=alliance.id,
                       upload_date=dates.format(parti_file.version_datetime),
                       lic_related_file_id=lic_lr_file.id)
    _save_new_lrf(lr_file_raw)
    return redirect(url_for('license-manage.details'))


@blueprint.route('/update-license', methods=['POST'])
def update_license():
    abort_if_not_admin()

    lrf_id = request.values.get('lrf_id')
    lr_file: LicRelatedFile = _check_and_find_lic_related_file(lrf_id)

    # KTODO


@blueprint.route('/update-participant', methods=['POST'])
def update_participant():
    abort_if_not_admin()
    # KTODO


@blueprint.route('/deactivate-license', methods=['POST'])
def deactivate_license():
    abort_if_not_admin()

    lrf_id = request.values.get('lrf_id')
    lr_file = _check_and_find_lic_related_file(lrf_id)

    # KTODO


@blueprint.route('/deactivate-participant', methods=['POST'])
def deactivate_participant():
    abort_if_not_admin()

    lrf_id = request.values.get('lrf_id')
    lr_file = _check_and_find_lic_related_file(lrf_id)
    lr_file.status = "archived"
    lr_file.save()

    alli: Alliance = object_query_first(Alliance, lr_file.record_id)
    if alli is None:
        log.warning(f'alliance[{lr_file.record_id}]] not found')
    else:
        alli.status = 'inactive'
        alli.save()

    _wait_unit_status(lr_file.id, 'archived')
    return redirect(url_for('license-manage.details'))


def _load_or_create_lic(ezb_id: str) -> License:
    lic = None
    if ezb_id:
        lic_list = License.pull_by_key('identifier.id.exact', ezb_id)
        if lic_list and len(lic_list) > 0:
            log.info('Existing license found for #{x}'.format(x=ezb_id))
            lic = lic_list[0]
    if not lic:
        log.info('Adding new license for {x}'.format(x=ezb_id))
        lic = License()
    return lic


def _decode_csv_bytes(csv_bytes: bytes) -> str:
    encoding = chardet.detect(csv_bytes)['encoding']
    if encoding == 'ISO-8859-1':
        return csv_bytes.decode(encoding='iso-8859-1', errors='ignore')
    else:
        if encoding != 'utf-8':
            log.warning(f'unknown encoding[{encoding}], decode as utf8')
        return csv_bytes.decode(encoding='utf-8', errors='ignore')


def _extract_name_ezb_id_by_line(line: str) -> tuple[str, str]:
    results = re.findall(r'.+:\s*(.+?)\s*\[(.+?)\]', line)
    if len(results) and len(results[0]) == 2:
        name, ezb_id = results[0]
        return name.strip(), ezb_id.strip()
    else:
        raise ValueError(f'first line not found [{line}]')


def main3():
    with open('/home/kk/tmp/testing.csv', mode='rb') as f:
        b = f.read()

    lic_file = _load_lic_file_by_csv_bytes(b, 'abc.csv')
    print(lic_file.versioned_filename)


def main4():
    with open('/home/kk/tmp/EZB-NALIW-00493_AL_2019-02-07.xlsx', mode='rb') as f:
        xls_bytes = f.read()
        # w = openpyxl.load_workbook(io.BytesIO(f.read()))

    result = _load_lic_file_by_xls_bytes(xls_bytes)
    print(result)

    # sheet = w.active
    # rows = [[c.value for c in r] for r in sheet.rows]
    # rows = rows[5:]
    # print(rows)


def main5():
    a = License.pull_actives()
    print(a)
    # results = LicRelatedFile.query()
    # print(results)

    # results = LicRelatedFile.object_query()
    # results[0]
    # print(results)


if __name__ == '__main__':
    main5()
