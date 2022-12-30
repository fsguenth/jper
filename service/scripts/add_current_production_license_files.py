import os

from service.models import LicRelatedFile
from service.views.license_manage import read_production_license_csv_file, \
    save_production_file, add_lrf_for_production, save_production_participant_file, add_parti_lrf_for_production

lic_dir_path = '/home/anusha/Documents/src/deepgreen/deepgreen_cl/License Files/production_license_files'
par_dir_path = '/home/anusha/Documents/src/deepgreen/deepgreen_cl/License Files/production_participant_files'

data_from_csv_file = read_production_license_csv_file()

# Add the license files
license_files = {}
for f in os.listdir(lic_dir_path):
    file_path = os.path.join(lic_dir_path, f)
    if os.path.isfile(file_path):
        data = save_production_file(file_path)
        license_files[data['ezb_id']] = data

for ezb_id, data in data_from_csv_file.items():
    lrf_id = add_lrf_for_production(data, license_files.get(ezb_id, {}))
    data_from_csv_file[ezb_id]['license_lrf'] = lrf_id


# data_from_csv_file has participant_id, license_id, ezb_id, name, type, admin_note
# license_files has ezb_id, name, filename, version_datetime, versioned_filename
# Save the file. Match it to the license record, using file prefix, which will give us the participant id also
# Create new lic related file record
parti_files = {}
unmatched_parti_files = []
for f in os.listdir(par_dir_path):
    file_path = os.path.join(par_dir_path, f)
    file_prefix = f.split('_')[0]
    matched_license = {}
    for ezb_id, lic_data in license_files.items():
        if lic_data.get('filename', '').startswith(file_prefix):
            matched_license = lic_data
            break
    data = save_production_participant_file(file_path, matched_license.get('ezb_id', ''))
    if matched_license.get('ezb_id', ''):
        parti_files[data['ezb_id']] = data
    else:
        unmatched_parti_files.append(data)

for ezb_id, data in data_from_csv_file.items():
    if not data.get('participant_id', ''):
        continue
    lrf_id = add_parti_lrf_for_production(data, parti_files.get(ezb_id, {}))
    data_from_csv_file[ezb_id]['participant_lrf'] = lrf_id

for ezb_id, data in data_from_csv_file.items():
    lic_id = data.get('license_lrf', None)
    parti_id = data.get('participant_lrf', None)






