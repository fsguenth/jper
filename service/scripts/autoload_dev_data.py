import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Union

import pkg_resources

from octopus.core import app
from service import models
from service.__utils import ez_dao_utils
from service.models import Account, RepositoryConfig
from service.scripts import loadcsvjournals, loadezbparticipants

log: logging.Logger = app.logger
for h in log.handlers:
    h.setFormatter(logging.Formatter('%(asctime)s %(levelname).1s [%(module)s:%(lineno)d] - %(message)s'))

account_data_list = [
    {'email': 'MDPI@deepgreen.org', 'role': 'publisher', 'password': 'publisher1_MDPI'},
    {'email': 'Karger@deepgreen.org', 'role': 'publisher', 'password': 'publisher1_Karger'},
    {'email': 'Frontiers@deepgreen.org', 'role': 'publisher', 'password': 'publisher1_Frontiers'},
    {'email': 'SAGE@deepgreen.org', 'role': 'publisher', 'password': 'publisher1_SAGE'},
    {'email': 'wiley@deepgreen.org', 'role': 'publisher', 'password': 'publisher1_Wiley'},
    {
        'email': 'UBR@deepgreen.org', 'role': 'repository', 'password': 'repository1_UBR',
        'repository_name': 'Universität Regensburg',
        'repository_bibid': 'UBR',
        'packaging': 'http://purl.org/net/sword/package/METSMODS',
    },
    {
        'email': 'UBEN@deepgreen.org', 'role': 'repository', 'password': 'repository1_UBEN',
        'repository_name': 'Friedrich-Alexander-Universität Erlangen-Nürnberg',
        'repository_bibid': 'UBEN',
        'packaging': 'http://purl.org/net/sword/package/OPUS4Zip'
    },
    {
        'email': 'UBK@deepgreen.org', 'role': 'repository', 'password': 'repository1_UBK',
        'repository_name': 'Christian-Albrechts-Universität zu Kiel',
        'repository_bibid': 'UBK',
        'packaging': 'http://purl.org/net/sword/package/SimpleZip'
    },
    {
        'email': 'TUBB@deepgreen.org', 'role': 'repository', 'password': 'repository1_TUBB',
        'repository_name': 'Technische Universität Berlin',
        'repository_bibid': 'TUBB',
        'packaging': 'http://purl.org/net/sword/package/SimpleZip'
    },
    {
        'email': 'TFRD@deepgreen.org', 'role': ['repository', 'subject_repository', 'match_all'],
        'password': 'repository1_TFRD',
        'repository_name': 'Fachrepositorium Test',
        'repository_bibid': 'TFRD',
    },
]


def create_acc(acc_dict: dict):
    acc_dict['role'] = acc_dict.get('role', [])
    if type(acc_dict['role']) == str:
        acc_dict['role'] = [acc_dict['role']]

    account = models.Account()
    account.add_account(acc_dict)
    account.save()
    if 'publisher' in acc_dict['role']:
        account.become_publisher()


def prepare_accounts():
    log.info('[START] prepare accounts')
    for acc_data in account_data_list:
        log.info(f'create acc for {acc_data["email"]}')
        if Account.pull_by_email(acc_data['email']) is not None:
            log.warning(f'skip create acc for [{acc_data["email"]}] --- already exist')
            continue
        create_acc(acc_data)


def _find_acc_by_email(email, timeout_sec=10):
    def _find(_email):
        return Account.pull_by_email(email)

    if ez_dao_utils.wait_unit(lambda: _find(email) is not None, timeout=timeout_sec):
        return _find(email)

    log.warning(f'account not found [{email}]')
    return None


def _path_aff_file(acc) -> Path:
    return Path(pkg_resources.resource_filename(
        'service', f'scripts/test_data/Affiliations files/{acc.data["repository"]["bibid"]}.csv'))


def _path_lic_file(file_name) -> Path:
    return Path(pkg_resources.resource_filename('service', f'scripts/test_data/Test License Files/{file_name}'))


def upload_affiliation_files():
    log.info('[START] upload affiliation files ')
    acc_email_list = (acc['email'] for acc in account_data_list if 'repository_name' in acc)
    acc_list: Iterable[Account] = (_find_acc_by_email(email) for email in acc_email_list)
    acc_list = filter(None, acc_list)

    # filter bibid not found
    _acc_list = []
    for acc in acc_list:
        bibid = acc.data.get('repository', {}).get('bibid')
        if not bibid:
            log.warning(f'bibid not found [{acc.email}]')
            continue
        else:
            _acc_list.append(acc)
    acc_list = _acc_list

    data_list = ((acc, _path_aff_file(acc)) for acc in acc_list)
    data_list = ((acc, path) for acc, path in data_list if filter_not_file(path))

    for acc, aff_path in data_list:
        log.info(f'working for acc -- [{acc.email}]')

        # prepare repository config
        rec = RepositoryConfig().pull_by_repo(acc.id)
        if rec is None:
            rec = RepositoryConfig()
            rec.repository = acc.id

        # save file
        saved = rec.set_repo_config(csvfile=aff_path.open(), repository=acc.id)
        if not saved:
            log.warning(f'save affiliation files FAIL -- [{aff_path.as_posix()}]')
        log.info(f'save affiliation files success -- [{aff_path.as_posix()}]')


def filter_not_file(path: Union[Path, str]) -> bool:
    path = Path(path)
    if not os.path.isfile(path):
        log.warning(f'file not found [{path.as_posix()}]')
        return False
    return True


def add_license_files():
    log.info('[START] add license files ')
    data_list = [
        ('EZB-NALIW-00493_AL_2019-02-07.csv', 'alliance'),
        ('EZB-NALIW-00495_AL_2019-02-07.csv', 'alliance'),
        ('EZB-NALIW-00496_AL_2019-02-07.csv', 'alliance'),
        ('EZB-NALIX-00498_AL_2019-02-07.csv', 'alliance'),
        ('EZB-NALJB-00504_NL_2019-05-15.csv', 'alliance'),
        ('EZB-NALJC-00505_NL_2019-05-15.csv', 'alliance'),
        ('PUB-FRONT-00001_OA_2020-12-16.csv', 'gold'),
        ('PUB-MDPI0-00001_OA_2018-11-14.csv', 'gold'),
        ('EZB-SAGE-00001_OA_2021-05-04.csv', 'alliance'),
    ]
    data_list = (
        (_path_lic_file(file_name), lic_type)
        for file_name, lic_type in data_list
    )
    data_list = (d for d in data_list if filter_not_file(d[0]))

    for lic_file_path, lic_type in data_list:
        log.info(f'load_csv_journal for {lic_file_path.as_posix()}')
        loadcsvjournals.load_csv_journal(lic_file_path.as_posix(), lic_type)


def add_participant_files():
    log.info('[START] add participant files ')
    parti_file_name = [
        'EZB-NALIW-00493_OA_participants_current.csv',
        'EZB-NALIW-00495_OA_participants_current.csv',
        'EZB-NALIW-00496_OA_participants_current.csv',
        'EZB-NALIX-00498_OA_participants_current.csv',
        'EZB-NALJB-00504_NL_participants_current.csv',
        'EZB-NALJC-00505_NL_participants_current.csv',
        'EZB-SAGE-00001_OA_participants_2021-05-04.csv',
    ]
    parti_paths: Iterable[Path] = (_path_lic_file(file_name) for file_name in parti_file_name)
    parti_paths = filter(filter_not_file, parti_paths)
    for p in parti_paths:
        log.info(f'working for [{p.as_posix()}]')
        filename = p.name
        if '_' not in filename:
            log.warning(f'invalid participant file name {filename}')
            continue

        alid = filename.split('_')[0].upper()
        loadezbparticipants.upload_csv(p.as_posix(), alid)


def find_routing_test_data_by_doi(doi) -> Iterable[Path]:
    paths = (
        pkg_resources.resource_filename('service', 'scripts/test_data/TestData'),
        pkg_resources.resource_filename('service', 'scripts/test_data/FailedData'),
    )
    paths = (Path(p) for p in paths)
    paths = (p for p in paths if p.is_dir())

    for p in paths:
        for dirpath, _, filenames in os.walk(p):
            filenames = (f for f in filenames if f.startswith(f'10.{doi}'))
            full_paths = (Path(dirpath).joinpath(f) for f in filenames)
            yield from full_paths


def copy_test_data_to_sftp():
    data_list = [
        ('Frontiers@deepgreen.org', '3389'),
        ('SAGE@deepgreen.org', '1177'),
        ('MDPI@deepgreen.org', '3390'),
        ('Karger@deepgreen.org', '1159'),
    ]
    data_list = (
        (_find_acc_by_email(email), doi) for email, doi in data_list
    )
    data_list = ((acc, doi) for acc, doi in data_list if acc is not None)
    data_list = list(data_list)

    # prepare linux account
    for acc, doi in data_list:
        acc: Account
        create_ftp_user_path = pkg_resources.resource_filename('service', 'models/createFTPuser.sh')
        cmd = f'{create_ftp_user_path} {acc.id} {acc.api_key}'
        log.info(f'run command [{cmd}]')
        subprocess.call(cmd, shell=True)

    # copy test data file
    for acc, doi in data_list:
        target_dir = Path(f'/home/sftpusers/{acc.id}/xfer')
        target_dir.mkdir(exist_ok=True, parents=True)
        for test_file_path in find_routing_test_data_by_doi(doi):
            target_file = target_dir.joinpath(test_file_path.name).as_posix()

            # copy file
            shutil.copyfile(test_file_path, target_file)

            # chown
            cmd = ['chown', f'{acc.id}:sftpusers', target_file]
            log.info(f'run cmd {cmd}')
            subprocess.call(cmd)


def run_scheduler():
    from service import scheduler
    scheduler.moveftp()
    scheduler.copyftp()
    scheduler.processftp()
    scheduler.checkunrouted()
    scheduler.monthly_reporting()


def main():
    prepare_accounts()
    upload_affiliation_files()
    add_license_files()
    add_participant_files()
    copy_test_data_to_sftp()
    run_scheduler()


if __name__ == '__main__':
    main()
