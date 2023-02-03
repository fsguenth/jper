from octopus.core import app
from service.models import License, Alliance, LicenseManagement
import json


def create_management_records(lic_related_file, testing=True):
    with open(lic_related_file) as f:
        data = json.load(f)

    for ezb_id_hash in data.get('aggregations', {}).get("ezb_id", {}).get('buckets', []):
        # ezb_id, name, type, admin_notes, license_version, active_license, participant_version, active_participant
        # license = [{ version, file_name, name, uploaded_date, record_id, validation_notes, validation_status }]
        # license_versions = [{ version, status }]
        # participant = [{ version, file_name, name, uploaded_date, record_id, validation_notes, validation_status }]
        # participant_versions = [{ version, status }]
        ezb_id = ezb_id_hash["key"]
        print(f"Starting with {ezb_id}")
        management_record = {
            'ezb_id': ezb_id,
            'license_versions': [],
            'license_version': 0,
            'active_license_versions': [],
            'active_license': 0,
            'license': [],
            'participant_versions': [],
            'participant_version': 0,
            'active_participant_versions': [],
            'active_participant': 0,
            'participant': []
        }
        licences = []
        number_active_license = 0
        active_license = None
        active_license_version = 0
        licences_to_archive = []
        participants = []
        number_active_participant = 0
        active_participant = None
        active_participant_version = 0
        participants_to_archive = []
        admin_notes = []
        error_records = []

        for file_type_hash in ezb_id_hash.get("file_type", {}).get("buckets", []):
            if file_type_hash["key"] == "license":
                licences = file_type_hash.get('docs', {}).get('hits', {}).get('hits', [])
            elif file_type_hash["key"] == "participant":
                management_record['participant_version'] = file_type_hash["doc_count"]
                participants = file_type_hash.get('docs', {}).get('hits', {}).get('hits', [])

        interested_licences = []
        for index, lic_hash in enumerate(licences):
            lic = lic_hash['_source']
            if lic.get('record_id', ''):
                interested_licences.append(lic)
        management_record['license_version'] = len(interested_licences)

        for index, lic in enumerate(interested_licences):
            # lic contains
            # created_date, last_updated, file_name, type, ezb_id, name, status, upload_date, admin_notes, validation_notes, record_id
            new_lic = {} # version, file_name, name, uploaded_date, record_id, validation_notes, validation_status
            lic_version = index + 1
            v_status = ''
            record_id = ''

            status = lic.get('status', '')
            if not lic.get('validation_notes', '') or 'Warning' in lic.get('validation_notes', ''):
                v_status = 'validation passed'
            else:
                v_status = 'validation failed'
            ver_record = {'version': lic_version, 'status': status}
            new_lic['version'] = lic_version
            new_lic['file_name'] = lic.get('file_name', '')
            new_lic['name'] = lic.get('name', '')
            if lic.get('upload_date', ''):
                new_lic['uploaded_date'] = lic['upload_date']
            elif lic.get('last_updated', ''):
                new_lic['uploaded_date'] = lic['last_updated']
            elif lic.get('created_date', ''):
                new_lic['uploaded_date'] = lic['created_date']
            if lic.get('admin_notes', ''):
                admin_notes.append(lic.get('admin_notes', ''))
            new_lic['old_record_id'] = lic.get('record_id', '')
            new_lic['validation_notes'] = lic.get('validation_notes', '')
            new_lic['validation_status'] = v_status

            if status not in ['validation failed', 'deleted'] and v_status != 'validation failed':
                management_record['active_license_versions'].append(lic_version)

            if status == 'active':
                number_active_license += 1
                active_license = lic
                active_license_version = lic_version
            management_record['license'].append(new_lic)
            management_record['license_versions'].append(ver_record)

        if active_license:
            management_record['active_license'] = active_license_version
            # name, type, admin_notes,
            management_record['id'] = active_license.get('record_id', '')
            management_record['name'] = active_license.get('name', '')
            management_record['type'] = active_license.get('type', '')
        else:
            management_record['active_license'] = 0
            management_record['id'] = licences[-1].get('record_id', '')
            management_record['name'] = licences[-1].get('name', '')
            management_record['type'] = licences[-1].get('type', '')
        if admin_notes:
            management_record['admin_notes'] = "\n".join(list(set(admin_notes)))

        for lic in management_record['license']:
            old_id = lic.pop('old_record_id', None)
            if status == 'deleted':
                lic['record_id'] = ''
            elif lic['version'] == active_license_version:
                new_id = management_record['id']
                if old_id != new_id:
                    print(f"ERROR: License {old_id} is active and needs id changed to #{new_id}")
                lic['record_id'] = old_id
            elif old_id != management_record['id']:
                new_id = f"{management_record['id']}_v{lic['version']}"
                lic['record_id'] = new_id
                licences_to_archive.append({'id': old_id, 'new_id': new_id, 'status': 'inactive'})

        interested_participants = []
        for index, par_hash in enumerate(participants):
            par = par_hash['_source']
            if par.get('record_id', ''):
                interested_participants.append(par)
        management_record['participant_version'] = len(interested_participants)

        for index, par in enumerate(interested_participants):
            # par contains
            # created_date, last_updated, file_name, type, ezb_id, name, status, upload_date, admin_notes, validation_notes, record_id
            new_par = {} # version, file_name, name, uploaded_date, record_id, validation_notes, validation_status
            par_version = index + 1
            v_status = ''
            record_id = ''

            status = par.get('status', '')
            if par.get('validation_notes', ''):
                v_status = 'validation failed'
            else:
                v_status = 'validation passed'
            ver_record = {'version': par_version, 'status': status}
            new_par['version'] = par_version
            new_par['file_name'] = par.get('file_name', '')
            new_par['name'] = par.get('name', '')
            new_par['uploaded_date'] = par.get('upload_date', '')
            if par.get('upload_date', ''):
                new_par['uploaded_date'] = par['upload_date']
            elif par.get('last_updated', ''):
                new_par['uploaded_date'] = par['last_updated']
            elif par.get('created_date', ''):
                new_par['uploaded_date'] = par['created_date']
            new_par['old_record_id'] = par.get('record_id', '')
            new_par['validation_notes'] = par.get('validation_notes', '')
            new_par['validation_status'] = v_status

            if status not in ['validation failed', 'deleted'] and v_status != 'validation failed':
                management_record['active_participant_versions'].append(par_version)

            if status == 'active':
                number_active_participant += 1
                active_participant_version = par_version
            management_record['participant'].append(new_par)
            management_record['participant_versions'].append(ver_record)

        management_record['active_participant'] = active_participant_version

        for par in management_record['participant']:
            old_id = par.pop('old_record_id', None)
            if status == 'deleted':
                par['record_id'] = ''
            elif par['version'] == active_participant_version:
                new_id = management_record['id']
                par['record_id'] = new_id
                participants_to_archive.append({'id': old_id, 'new_id': new_id, 'status': 'active', 'license_id': management_record['id']})
            else:
                new_id = f"{management_record['id']}_v{par['version']}"
                par['record_id'] = new_id
                participants_to_archive.append({'id': old_id, 'new_id': new_id, 'status': 'inactive', 'license_id': management_record['id']})

        if number_active_license != 1:
            print(f"ERROR: {ezb_id} has {number_active_license} active license")
            if management_record['participant_version'] > 0 and number_active_participant != 1:
                print(f"ERROR: {ezb_id} has {number_active_participant} active participants")
            error_records.append([management_record, licences_to_archive, participants_to_archive])

        if testing:
            if active_license:
                l = License.pull(active_license['record_id'])
                if not isinstance(l, License):
                    print(f"Error license {active_license['record_id']} does not exist for {ezb_id}")
            with open(f"logs/management_records/{ezb_id}.json", 'w') as f:
                json.dump(management_record, f, indent=4)
            if licences_to_archive:
                with open(f"logs/management_records/{ezb_id}_licenses_to_archive.json", 'w') as f:
                    json.dump(licences_to_archive, f, indent=4)
            if participants_to_archive:
                with open(f"logs/management_records/{ezb_id}_participants_to_archive.json", 'w') as f:
                    json.dump(participants_to_archive, f, indent=4)
        elif number_active_license == 1:
            add_management_record(management_record)
            if licences_to_archive:
                archive_licences(licences_to_archive)
            if participants_to_archive:
                archive_participants(participants_to_archive)
        print('-' * 10)


def add_management_record(management_record):
    try:
        l = LicenseManagement(management_record)
        l.save()
    except Exception as e:
        print(management_record)
        raise e


def archive_licences(licences_to_archive):
    # [{'id': old_id, 'new_id': new_id, 'status': 'inactive'}]
    for lic in licences_to_archive:
        if lic['status'] == 'active':
            print(f"ERROR: Want to change id of active license from {lic['id']} to {lic['new_id']}")
            return
        l = License.pull(lic['id'])
        if isinstance(l, License):
            l.archive(lic['new_id'])
            l.delete()
            print(f"Change id of license from {lic['id']} to {lic['new_id']}")
        else:
            print(f"Error: License {lic['id']} does not exist")
    return


def archive_participants(participants_to_archive):
    # license_id should be same as new_id
    # [{'id': old_id, 'new_id': new_id, 'status': 'inactive'}]
    l = License.pull(participants_to_archive[0]['license_id'])
    for par in participants_to_archive:
        p = Alliance.pull(par['id'])
        if isinstance(p, Alliance) and isinstance(l, License) and p.license_id != l.id:
            p.license_id = par['new_id']
            p.save()

    for par in participants_to_archive:
        p = Alliance.pull(par['id'])
        if isinstance(p, Alliance):
            if par['status'] == 'active':
                p.activate(par['new_id'])
            else:
                p.archive(par['new_id'])
            p.delete()
            print(f"Change id of participant from {par['id']} to {par['new_id']}")
        else:
            print(f"Error: Participant {par['id']} does not exist")
    return


if __name__ == "__main__":
    """
    Save the data from jper-lic_related_file grouped by ezb_id and file_type as a json file
    query = {
        "aggs": {
            "ezb_id": {
                "terms": {
                    "field": "ezb_id.exact",
                    "size": 10000
                },
                "aggs": {
                    "file_type": {
                        "terms": {
                            "field": "file_type.exact"
                        },
                        "aggs": {
                            "docs": {
                                "top_hits": {
                                    "size": 20
                                }
                            }
                        }
                    }
                }
            }
        },
        "size": 0
    }
    """

    create_management_records('logs/jper-lic_related_file-production.json', testing=False)



