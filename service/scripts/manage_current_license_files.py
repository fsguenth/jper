# _create_versioned_filename(filename: str,
#                                version_datetime: datetime = None)
#
#
# lrf_raw = dict(file_name=lic_file.versioned_filename,
#                    type=lic_type,
#                    ezb_id=ezb_id,
#                    status='validation passed',
#                    admin_notes=admin_notes,
#                    record_id=lic.id,
#                    upload_date=dates.format(lic_file.version_datetime), )
#     if validation_notes:
#         lrf_raw['validation_notes'] = validation_notes
#     lrf = LicRelatedFile.save_by_raw(lrf_raw, blocking=False)

import os
import json
from service.views.license_manage import upload_existing_license, upload_existing_participant

# lic_dir_path = '/home/anusha/Documents/src/deepgreen/license_files'
lic_dir_path = '/home/green/license_files/'

all_files = []
for f in os.listdir(lic_dir_path):
    file_path = os.path.join(lic_dir_path, f)
    if os.path.isfile(file_path):
        all_files.append(file_path)

done = []
errored = {}
for f in os.listdir(lic_dir_path):
    file_path = os.path.join(lic_dir_path, f)
    if os.path.isfile(file_path) and file_path not in done:
        try:
            upload_existing_license(file_path)
            done.append(file_path)
        except Exception as e:
            errored[file_path] = str(e)
            print(f'str{e}')

print(json.dumps(errored, indent=4))

print(json.dumps(done, indent=4))


# parti_dir_path = '/home/anusha/Documents/src/deepgreen/participant_files'
parti_dir_path = '/home/green/participant_files/'

all_files = []
for f in os.listdir(parti_dir_path):
    file_path = os.path.join(parti_dir_path, f)
    if os.path.isfile(file_path):
        all_files.append(file_path)

done = []
errored = {}
for f in os.listdir(parti_dir_path):
    file_path = os.path.join(parti_dir_path, f)
    if os.path.isfile(file_path) and file_path not in done:
        try:
            upload_existing_participant(file_path)
            done.append(file_path)
        except Exception as e:
            errored[file_path] = str(e)
            print(f'str{e}')

print(json.dumps(errored, indent=4))

print(json.dumps(done, indent=4))

# errored
license_errored = {
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIX-00001_Karger_AL_2022-04-21.csv":
        "(<class 'ValueError'>, 'licence not found for EZB-NALIX-00001, /home/anusha/Documents/src/deepgreen/license_files/EZB-NALIX-00001_Karger_AL_2022-04-21.csv')",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-KARGER-00001_Karger_OA_2021-07-29.csv":
        "(<class 'ValueError'>, '2 licences found for PUB-KARGER-00001, /home/anusha/Documents/src/deepgreen/license_files/OA-KARGER-00001_Karger_OA_2021-07-29.csv')",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALJB-00001_Karger_NL_2022-04-21.csv":
        "(<class 'ValueError'>, 'licence not found for EZB-NALJB-00001, /home/anusha/Documents/src/deepgreen/license_files/EZB-NALJB-00001_Karger_NL_2022-04-21.csv')",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-IOP-00001_IOP_OA_2021-11-29.csv":
        "(<class 'ValueError'>, 'licence not found for PUB-IOP-00001, /home/anusha/Documents/src/deepgreen/license_files/OA-IOP-00001_IOP_OA_2021-11-29.csv')"
}
license_done = [
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALJC-00505_SAGE_NL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01784_Sage-STM-Upgrade21_AL_2021-07-13.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIX-00498_Karger_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01785_SAGE-HSS-Upgrade2021_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-MDPI-00001_MDPI_OA_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALFK-00448_DeGruyterLLH1_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALJB-00504_Karger_NL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00495_SAGE-Complete_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01317_SAGE-Complete-Upgrade15-16_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00492_SAGE-HSS_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/FID-FUTURES-00001_FutureScience_FID_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01762_SAGE-Health-Upgrade15-16_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01757_SAGE-STM-Upgrade17-20_AL_2021-07-13.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01315_SAGE-Materials_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01756_SAGE-HSS-Upgrade2017-20_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00493_SAGE-IMechE_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01786_SAGE-Complete-Upgrade21_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01763_SAGE-Materials-Upgrade17-20_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01319_SAGE-STM-Upgrade15-16_AL_2021-07-13.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-FRONTIERS-00001_Frontiers_OA_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-WILEY-00001_Wiley_OA_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00496_SAGE-RSM_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00497_SAGE-STM_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-HOGREFE-00001_Hogrefe_OA_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01314_SAGE-HSS-Upgrade15-16_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALLH-00543_DeGruyterLLH2_AL_2021-07-05.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01758_SAGE-Health-Upgrade17-20_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/OA-BMJ-00001_BMJ_OA_2021-10-04.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01682_SAGE-Materials-Upgrade15-16_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-WIDEA-01707_Wiley_DEAL_2021-07-29.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-00491_SAGE-Health_AL_2021-07-06.csv",
    "/home/anusha/Documents/src/deepgreen/license_files/EZB-NALIW-01755_SAGE-Complete-Upgrade17-20_AL_2021-07-05.csv"
]
participant_errored = {
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALJC-00505_SAGE_NL_2021-07-05_participants.csv":
        "(<class 'ValueError'>, '2 participants found for EZB-NALJC-00505, /home/anusha/Documents/src/deepgreen/participant_files/EZB-NALJC-00505_SAGE_NL_2021-07-05_participants.csv')",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIX-00001_Karger_AL_2022-04-21_participants.csv":
        "400 Bad Request: Found no related license files",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALJB-00001_Karger_NL_2022-04-21_participants.csv":
        "400 Bad Request: Found no related license files",
    "/home/anusha/Documents/src/deepgreen/participant_files/OA-Wiley-00001_Wiley_OA_2021-10-21_participants.csv":
        "400 Bad Request: Found no related license files",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-WIDEA-01707_Wiley_DEAL_2021-10-21_participants.csv":
        "400 Bad Request: Found no related license files"
}

participant_done = [
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-WIDEA-01707_Wiley_DEAL_2021-07-29_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01315_SAGE-Materials_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALLH-00543_DeGruyterLLH2_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01763_SAGE-Materials-Upgrade17-20_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00497_SAGE-STM_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01762_SAGE-Health-Upgrade15-16_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00496_SAGE-RSM_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01314_SAGE-HSS-Upgrade15-16_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01786_SAGE-Complete-Upgrade21_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01785_SAGE-HSS-Upgrade2021_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00491_SAGE-Health_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/OA-WILEY-00001_Wiley_OA_2021-07-29_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALFK-00448_DeGruyterLLH1_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01784_Sage-STM-Upgrade21_AL_2021-07-13_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01319_SAGE-STM-Upgrade15-16_AL_2021-07-13_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01758_SAGE-Health-Upgrade17-20_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00492_SAGE-HSS_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01757_SAGE-STM-Upgrade17-20_AL_2021-07-13_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01317_SAGE-Complete-Upgrade15-16_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00493_SAGE-IMechE_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIX-00498_Karger_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01756_SAGE-HSS-Upgrade2017-20_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALJB-00504_Karger_NL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-00495_SAGE-Complete_AL_2021-07-05_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/FID-FUTURES-00001_FutureScience_FID_2021-07-29_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01682_SAGE-Materials-Upgrade15-16_AL_2021-07-06_participants.csv",
    "/home/anusha/Documents/src/deepgreen/participant_files/EZB-NALIW-01755_SAGE-Complete-Upgrade17-20_AL_2021-07-05_participants.csv"
]

# test machine
test_license_errored = {
    "/home/green/license_files/EZB-NALIX-00498_Karger_AL_2021-07-05.csv": "(<class 'ValueError'>, 'licence not found for EZB-NALIX-00498, /home/green/license_files/EZB-NALIX-00498_Karger_AL_2021-07-05.csv')",
    "/home/green/license_files/EZB-NALJB-00504_Karger_NL_2021-07-05.csv": "(<class 'ValueError'>, 'licence not found for EZB-NALJB-00504, /home/green/license_files/EZB-NALJB-00504_Karger_NL_2021-07-05.csv')"
}
test_license_done = [
    "/home/green/license_files/EZB-NALJC-00505_SAGE_NL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-01784_Sage-STM-Upgrade21_AL_2021-07-13.csv",
    "/home/green/license_files/EZB-FID-ECON_DL_2020-09-21.csv",
    "/home/green/license_files/EZB-NALIW-01785_SAGE-HSS-Upgrade2021_AL_2021-07-06.csv",
    "/home/green/license_files/OA-MDPI-00001_MDPI_OA_2021-07-29.csv",
    "/home/green/license_files/EZB-NALFK-00448_DeGruyterLLH1_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-00495_SAGE-Complete_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-01317_SAGE-Complete-Upgrade15-16_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-FID-PUBLISSO-00001_2021-03-12.tsv",
    "/home/green/license_files/EZB-NALIW-00492_SAGE-HSS_AL_2021-07-06.csv",
    "/home/green/license_files/FID-FUTURES-00001_FutureScience_FID_2021-07-29.csv",
    "/home/green/license_files/EZB-NALIW-01762_SAGE-Health-Upgrade15-16_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-01757_SAGE-STM-Upgrade17-20_AL_2021-07-13.csv",
    "/home/green/license_files/EZB-NALIW-01315_SAGE-Materials_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-01756_SAGE-HSS-Upgrade2017-20_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-00493_SAGE-IMechE_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-01786_SAGE-Complete-Upgrade21_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-01763_SAGE-Materials-Upgrade17-20_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-01319_SAGE-STM-Upgrade15-16_AL_2021-07-13.csv",
    "/home/green/license_files/OA-FRONTIERS-00001_Frontiers_OA_2021-07-29.csv",
    "/home/green/license_files/OA-WILEY-00001_Wiley_OA_2021-07-29.csv",
    "/home/green/license_files/EZB-NALIW-00496_SAGE-RSM_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-00497_SAGE-STM_AL_2021-07-06.csv",
    "/home/green/license_files/OA-HOGREFE-00001_Hogrefe_OA_2021-07-29.csv",
    "/home/green/license_files/EZB-NALIW-01314_SAGE-HSS-Upgrade15-16_2021-07-06.csv",
    "/home/green/license_files/OA-KARGER-00001_Karger_OA_2021-07-29.csv",
    "/home/green/license_files/EZB-NALLH-00543_DeGruyterLLH2_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-NALIW-01758_SAGE-Health-Upgrade17-20_AL_2021-07-06.csv",
    "/home/green/license_files/OA-BMJ-00001_BMJ_OA_2021-10-04.csv",
    "/home/green/license_files/EZB-NALIW-01682_SAGE-Materials-Upgrade15-16_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-WIDEA-01707_Wiley_DEAL_2021-07-29.csv",
    "/home/green/license_files/EZB-NALIW-00491_SAGE-Health_AL_2021-07-06.csv",
    "/home/green/license_files/EZB-NALIW-01755_SAGE-Complete-Upgrade17-20_AL_2021-07-05.csv",
    "/home/green/license_files/EZB-FID-GEOL_DL_2020-09-21.csv"
]
test_participant_errored = {
    "/home/green/participant_files/EZB-NALIX-00498_Karger_AL_2021-07-05_participants.csv": "400 Bad Request: Found no related license files",
    "/home/green/participant_files/EZB-NALJB-00504_Karger_NL_2021-07-05_participants.csv": "400 Bad Request: Found no related license files",
    "/home/green/participant_files/OA-Wiley-00001_Wiley_OA_2021-10-21_participants.csv": "400 Bad Request: Found no related license files",
    "/home/green/participant_files/EZB-WIDEA-01707_Wiley_DEAL_2021-10-21_participants.csv": "400 Bad Request: Found no related license files"
}
test_participant_done = [
    "/home/green/participant_files/EZB-WIDEA-01707_Wiley_DEAL_2021-07-29_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01315_SAGE-Materials_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALLH-00543_DeGruyterLLH2_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01763_SAGE-Materials-Upgrade17-20_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00497_SAGE-STM_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01762_SAGE-Health-Upgrade15-16_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00496_SAGE-RSM_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01314_SAGE-HSS-Upgrade15-16_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01786_SAGE-Complete-Upgrade21_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01785_SAGE-HSS-Upgrade2021_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00491_SAGE-Health_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALJC-00505_SAGE_NL_2021-07-05_participants.csv",
    "/home/green/participant_files/OA-WILEY-00001_Wiley_OA_2021-07-29_participants.csv",
    "/home/green/participant_files/EZB-NALFK-00448_DeGruyterLLH1_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01784_Sage-STM-Upgrade21_AL_2021-07-13_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01319_SAGE-STM-Upgrade15-16_AL_2021-07-13_participants.csv",
    "/home/green/participant_files/EZB-FID-ECON_DL_2020-09-21_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01758_SAGE-Health-Upgrade17-20_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00492_SAGE-HSS_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-FID-PUBLISSO-00001_2021-03-12_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01757_SAGE-STM-Upgrade17-20_AL_2021-07-13_participants.csv",
    "/home/green/participant_files/EZB-FID-GEOL_DL_2020-09-21_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01317_SAGE-Complete-Upgrade15-16_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00493_SAGE-IMechE_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01756_SAGE-HSS-Upgrade2017-20_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-00495_SAGE-Complete_AL_2021-07-05_participants.csv",
    "/home/green/participant_files/FID-FUTURES-00001_FutureScience_FID_2021-07-29_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01682_SAGE-Materials-Upgrade15-16_AL_2021-07-06_participants.csv",
    "/home/green/participant_files/EZB-NALIW-01755_SAGE-Complete-Upgrade17-20_AL_2021-07-05_participants.csv"
]

