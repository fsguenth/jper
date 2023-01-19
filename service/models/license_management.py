import csv
from typing import Union, Iterable, Type, Optional
from copy import deepcopy

from octopus.core import app
from octopus.lib import dataobj
from service import dao
from octopus.lib import dates

LICENSE_TYPES = ["alliance", "national", "gold", "deal", "fid", "hybrid"]
LRF_STATUS = ["validation failed", "validation passed", "active", "archived", "deleted"]
VALIDATION_STATUS = ["validation failed", "validation passed"]
LRF_FILE_TYPES = ["license", "participant"]

LIC_STATUS_ACTIVE = 'active'
LIC_STATUS_INACTIVE = 'inactive'


class LicenseManagement(dataobj.DataObj, dao.LicenseManagementDAO):
    """
    The license management object is structured as below
    <{
        "id" : "<unique persistent account id>",
        "created_date" : "<date account created>",
        "last_updated" : "<date account last modified>",
        "ezb_id": "<ezb id uniquely identifying the license and participant files>",
        "name": "<The name of the license and participant record>",
        "type": "<type of license - allowed_values: LICENSE_TYPES>",
        "admin_notes": "<Any admin notes>",
        "active_license": "<The current active license version number>",
        "active_participant": "<The current active participant version number>",
        "license_version": "<The latest license version number>",
        "participant_version": "<The latest license version number>",
        "license" : [{
            "version": "<Version number>",
            "file_name" : "<Name of file uploaded>",
            "name": "<The name of the license record>"
            "admin_notes": "<Any admin notes for this license>",
            "uploaded_date": "<Date uploaded - utcdatetime>",
            "record_id": "<The license record id>",
            "validation_notes": "<The validation notes for this file>",
            "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
        }],
        "participant": [{
            "version": "<Version number>",
            "file_name" : "<Name of file uploaded>",
            "name": "<The name of the participant record>"
            "admin_notes": "<Any admin notes for this license>",
            "uploaded_date": "<Date uploaded - utcdatetime>",
            "record_id": "<The participant record id>",
            "validation_notes": "<The validation notes for this file>",
            "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
        }],
        license_versions: [{
            "version": "<The version number>",
            "status": "<The status of the license - allowed_values: LRF_STATUS>",
        }],
        participant_versions: [{
            "version": "<The version number>",
            "status": "<The status of the participant - allowed_values: LRF_STATUS>",
        }]
    }>
    """

    def __init__(self, raw=None):
        struct = {
            "lists": {
                "license": {"contains": "object"},
                "participant": {"contains": "object"},
                "license_versions": {"contains": "object"},
                "participant_versions": {"contains": "object"}
            },
            "fields": {
                "id": {"coerce": "unicode"},
                "created_date": {"coerce": "utcdatetime"},
                "last_updated": {"coerce": "utcdatetime"},
                "ezb_id": {"coerce": "unicode"},
                "name": {"coerce": "unicode"},
                "type": {"coerce": "unicode", "allowed_values": LICENSE_TYPES},
                "admin_notes": {"coerce": "unicode"},
                "license_version": {"coerce": "integer"},
                "participant_version": {"coerce": "integer"},
                "active_license": {"coerce": "integer"},
                "active_participant": {"coerce": "integer"},
            },
            "structs": {
                "license": {
                    "fields": {
                        "version": {"coerce": "integer"},
                        "file_name": {"coerce": "unicode"},
                        "name": {"coerce": "unicode"},
                        "admin_notes": {"coerce": "unicode"},
                        "uploaded_date": {"coerce": "utcdatetime"},
                        "record_id": {"coerce": "unicode"},
                        "validation_notes": {"coerce": "unicode"},
                        "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
                    }
                },
                "license_versions": {
                    "fields": {
                        "version": {"coerce": "integer"},
                        "status": {"coerce": "unicode", "allowed_values": LRF_STATUS},
                    }
                },
                "participant": {
                    "fields": {
                        "version": {"coerce": "integer"},
                        "file_name": {"coerce": "unicode"},
                        "name": {"coerce": "unicode"},
                        "admin_notes": {"coerce": "unicode"},
                        "uploaded_date": {"coerce": "utcdatetime"},
                        "record_id": {"coerce": "unicode"},
                        "validation_notes": {"coerce": "unicode"},
                        "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
                    }
                },
                "participant_versions": {
                    "fields": {
                        "version": {"coerce": "integer"},
                        "status": {"coerce": "unicode", "allowed_values": LRF_STATUS},
                    }
                },
            }
        }
        self._add_struct(struct)
        super(LicenseManagement, self).__init__(raw=raw)

    @property
    def ezb_id(self):
        return self._get_single("ezb_id", coerce=dataobj.to_unicode())

    @ezb_id.setter
    def ezb_id(self, val):
        self._set_single("ezb_id", val, coerce=dataobj.to_unicode())

    @property
    def name(self):
        return self._get_single("name", coerce=dataobj.to_unicode())

    @name.setter
    def name(self, val):
        self._set_single("name", val, coerce=dataobj.to_unicode())

    @property
    def type(self):
        return self._get_single("type", coerce=dataobj.to_unicode())

    @type.setter
    def type(self, val):
        self._set_single("type", val, coerce=dataobj.to_unicode(), allowed_values=LICENSE_TYPES)

    @property
    def admin_notes(self):
        return self._get_single("admin_notes", coerce=self._utf8_unicode())

    @admin_notes.setter
    def admin_notes(self, val):
        self._set_single("admin_notes", val, coerce=dataobj.to_unicode())

    @property
    def license_version(self):
        val = self._get_single("license_version", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    @property
    def participant_version(self):
        val = self._get_single("participant_version", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    def increment_license_version(self):
        val = self.license_version + 1
        self._set_single("license_version", val, coerce=dataobj.to_int())

    def increment_participant_version(self):
        val = self.participant_version + 1
        self._set_single("participant_version", val, coerce=dataobj.to_int())

    @property
    def active_license(self):
        val = self._get_single("active_license", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    @property
    def active_participant(self):
        val = self._get_single("active_participant", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    @active_license.setter
    def active_license(self, val):
        self._set_single("active_license", val, coerce=dataobj.to_int())

    @active_participant.setter
    def active_participant(self, val):
        self._set_single("active_participant", val, coerce=dataobj.to_int())

    @property
    def license_versions(self):
        return self._get_list("license_versions")

    @property
    def participant_versions(self):
        return self._get_list("participant_versions")

    @license_versions.setter
    def license_versions(self, vals):
        self._set_list("license_versions", vals)

    @participant_versions.setter
    def participant_versions(self, vals):
        self._set_list("participant_versions", vals)

    def add_license_version(self, vals):
        if vals.get('version', None) and vals.get('status', None) and vals['status'] in LRF_STATUS:
            do_int = dataobj.to_int()
            do_uc = dataobj.to_unicode()
            vals['version'] = self._coerce(vals['version'], do_int)
            vals['status'] = self._coerce(vals['status'], do_uc)
            self._add_to_list("license_versions", vals)
            return vals
        return False

    def add_participant_version(self, vals):
        if vals.get('version', None) and vals.get('status', None) and vals['status'] in LRF_STATUS:
            do_int = dataobj.to_int()
            do_uc = dataobj.to_unicode()
            vals['version'] = self._coerce(vals['version'], do_int)
            vals['status'] = self._coerce(vals['status'], do_uc)
            self._add_to_list("participant_versions", vals)
            return vals
        return False

    @property
    def license_states(self):
        return self._version_states(self.license_versions)

    @property
    def participant_states(self):
        return self._version_states(self.participant_versions)

    def validate_license_versions(self):
        all_version = []
        for version_list in self.license_states.values():
            all_version = all_version + version_list
        return all_version == list(set(all_version)) and max(all_version) == self.license_version

    def validate_participant_versions(self):
        all_version = []
        for version_list in self.participant_states.values():
            all_version = all_version + version_list
        return all_version == list(set(all_version)) and max(all_version) == self.participant_version

    @property
    def licenses(self):
        """
        The licenses associated with the ezb id

        The returned object is as follows:

        ::
            [{
                "version": "<Version number>",
                "file_name" : "<Name of file uploaded>",
                "name": "<The name of the license record>"
                "admin_notes": "<Any admin notes for this license>",
                "uploaded_date": "<Date uploaded - utcdatetime>",
                "record_id": "<The license record id>",
                "validation_notes": "<The validation notes for this file>",
                "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
            }]

        :return: The repository information as a python dict object
        """
        return self._get_list("license")

    @licenses.setter
    def licenses(self, vals):
        self._set_list("license", vals)

    def create_license_hash(self, version_datetime, file_name):
        """
            "version": "<Version number>",
            "file_name" : "<Name of file uploaded>",
            "name": "<The name of the license record>"
            "admin_notes": "<Any admin notes for this license>",
            "uploaded_date": "<Date uploaded - utcdatetime>",
            "record_id": "<The license record id>",
            "validation_notes": "<The validation notes for this file>",
            "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
        """
        # set version
        self.increment_license_version()
        if not self._validate_license_version(self.license_version):
            return False
        # Initialise license hash
        license_hash = {
            "version": self.license_version,
            "name": "",
            "file_name": file_name,
            "uploaded_date": dates.format(version_datetime),
            "validation_notes": [],
            "validation_status": 'validation failed',
        }
        return license_hash

    def add_license(self, obj):
        """
        Add the license object

        The object will be validated and types coerced as needed.

        The supplied object should be structured as follows:

        ::
            {
                "version": "<Version number>",
                "file_name" : "<Name of file uploaded>",
                "name": "<The name of the license record>"
                "admin_notes": "<Any admin notes for this license>",
                "uploaded_date": "<Date uploaded - utcdatetime>",
                "record_id": "<The license record id>",
                "validation_notes": "<The validation notes for this file>",
                "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
            }

        :param obj: the license object as a dict
        :return:
        """
        # coerce data in object
        obj = self._coerce_child(obj)
        # add license obj to management record
        self._add_to_list("license", obj)
        return obj

    @property
    def participants(self):
        """
        The participants associated with the ezb id

        The returned object is as follows:

        ::
            [{
                "version": "<Version number>",
                "file_name" : "<Name of file uploaded>",
                "name": "<The name of the participant record>"
                "admin_notes": "<Any admin notes for this license>",
                "uploaded_date": "<Date uploaded - utcdatetime>",
                "record_id": "<The participant record id>",
                "validation_notes": "<The validation notes for this file>",
                "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
            }]

        :return: The repository information as a python dict object
        """
        return self._get_list("participant")

    @participants.setter
    def participants(self, vals):
        self._set_list("participant", vals)

    def create_participant_hash(self, version_datetime, file_name):
        """
            "version": "<Version number>",
            "file_name" : "<Name of file uploaded>",
            "name": "<The name of the participant record>"
            "admin_notes": "<Any admin notes for this license>",
            "uploaded_date": "<Date uploaded - utcdatetime>",
            "record_id": "<The participant record id>",
            "validation_notes": "<The validation notes for this file>",
            "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
        """
        # set version
        self.increment_participant_version()
        if not self._validate_participant_version(self.participant_version):
            return False
        # Initialise license hash
        participant_hash = {
            "version": self.participant_version,
            "name": "",
            "file_name": file_name,
            "uploaded_date": dates.format(version_datetime),
            "validation_notes": [],
            "validation_status": 'validation failed',
        }
        return participant_hash

    def add_participant(self, obj):
        """
        Add the participant object

        The object will be validated and types coerced as needed.
          - version of child will be the latest version
          - record_id will be same as id with latest version appended '{self.id}_v{latest_version}'
          - uploaded date will be set to now

        The supplied object should be structured as follows:

        ::
            {
                "version": "<Version number>",
                "file_name" : "<Name of file uploaded>",
                "name": "<The name of the participant record>"
                "admin_notes": "<Any admin notes for this license>",
                "uploaded_date": "<Date uploaded - utcdatetime>",
                "record_id": "<The participant record id>",
                "validation_notes": "<The validation notes for this file>",
                "validation_status": {"coerce": "unicode", "allowed_values": VALIDATION_STATUS},
            }

        :param obj: the participant object as a dict
        :return:
        """
        # coerce data in object
        obj = self._coerce_child(obj)
        # add license obj to management record
        self._add_to_list("participant", obj)
        return obj

    def valid_license(self, version):
        return self._valid(self.licenses, version)

    def valid_participant(self, version):
        return self._valid(self.participants, version)

    def can_activate_license(self, version):
        return self._can_activate(self.license_states, version)

    def can_activate_participant(self, version):
        return self._can_activate(self.participant_states, version)

    def can_archive_license(self, version):
        return self._can_archive(self.license_states, version)

    def can_archive_participant(self, version):
        return self._can_archive(self.participant_states, version)

    def can_delete_license(self, version):
        return self._can_delete(self.license_states, version)

    def can_delete_participant(self, version):
        return self._can_delete(self.participant_states, version)

    def activate_license(self, version_to_activate):
        """
        # "validation failed", "validation passed", "active", "archived", "deleted"
        Activate the given version
        from state: validation passed or archived
        to state: active
        """
        if self.can_activate_license(version_to_activate):
            versions = self._activate(self.license_versions, version_to_activate)
            self.license_versions = versions
            self.active_license = version_to_activate
            return True
        return False

    def activate_participant(self, version_to_activate):
        """
        # "validation failed", "validation passed", "active", "archived", "deleted"
        Activate the given version
        from state: validation passed or archived
        to state: active
        """
        if self.can_activate_participant(version_to_activate):
            versions = self._activate(self.participant_versions, version_to_activate)
            self.participant_versions = versions
            self.active_participant = version_to_activate
            return True
        return False

    def archive_license(self, version_to_archive):
        """
        Archive the given version
        from state: "validation failed", "validation passed", "active"
        to state: "archived"
        """
        if self.can_archive_license(version_to_archive):
            new_versions = self._archive(self.license_versions, version_to_archive)
            self.license_versions = new_versions
            return True
        return False

    def archive_participant(self, version_to_archive):
        """
        Archive the given version
        from state: "validation failed", "validation passed", "active"
        to state: "archived"
        """
        if self.can_archive_participant(version_to_archive):
            new_versions = self._archive(self.participant_versions, version_to_archive)
            self.participant_versions = new_versions
            return True
        return False

    def delete_license(self, version_to_delete):
        """
        Delete the given version
        from state: "validation failed", "validation passed", "archived"
        to state: "deleted"
        """
        if self.can_delete_license(version_to_delete):
            new_versions, new_licenses = self._delete(self.license_versions, self.licenses, version_to_delete)
            self.license_versions = new_versions
            self.licenses = new_licenses
            return True
        return False

    def delete_participant(self, version_to_delete):
        """
        Delete the given version
        from state: "validation failed", "validation passed", "archived"
        to state: "deleted"
        """
        if self.can_delete_participant(version_to_delete):
            new_versions, new_participants = self._delete(self.participant_versions, self.participants, version_to_delete)
            self.participant_versions = new_versions
            self.participants = new_participants
            return True
        return False

    def record_id(self, record_version):
        # record_id will be same as id with version appended '{self.id}_v{record_version}'
        return f"{self.id}_v{record_version}"

    def _coerce_child(self, obj):
        """
        The object will be validated and types coerced as needed.
          - version of child will be the latest version
          - record_id will be same as id with latest version appended '{self.id}_v{latest_version}'
          - uploaded date will be set to now
        """
        allowed = ["file_name", "name", "admin_notes", "uploaded_date", "record_id",
                   "validation_notes", "validation_status", "version"]
        # coerce the values of the keys
        do_unicode = dataobj.to_unicode()
        for k in allowed:
            if k == "uploaded_date":
                # uploaded_date
                do_date = dataobj.date_str()
                if obj.get("uploaded_date", None):
                    uploaded_date = obj["uploaded_date"]
                else:
                    uploaded_date = dates.now()
                obj["uploaded_date"] = self._coerce(uploaded_date, do_date)
            elif k == "version":
                do_int = dataobj.to_int()
                obj["version"] = self._coerce(obj["version"], do_int)
            elif obj.get(k, None):
                obj[k] = self._coerce(obj[k], do_unicode)
        return obj

    def _validate_license_version(self, latest_version):
        for rec in self.license_versions:
            if latest_version == rec['version']:
                return False
        return True

    def _validate_participant_version(self, latest_version):
        for rec in self.participant_versions:
            if latest_version == rec['version']:
                return False
        return True

    def _version_states(self, versions):
        states = {}
        for state in LRF_STATUS:
            states[state] = []
        for rec in versions:
            states[rec['status']].append(rec['version'])
        return states

    def _validate_versions(self, versions, current_version):
        all_version_numbers = []
        for version in versions:
            all_version_numbers.append(version['version'])
        is_unique = all_version_numbers == list(set(all_version_numbers))
        version_is_correct = current_version in all_version_numbers
        return is_unique and version_is_correct

    def _can_activate(self, states, version_to_activate):
        acceptable_versions = states["validation passed"] + states["archived"]
        if version_to_activate in acceptable_versions:
            return True
        return False

    def _can_archive(self, states, version):
        # can archive if validation passed or active
        acceptable_versions = states["validation passed"] + states['active']
        if version in acceptable_versions:
            return True
        return False

    def _can_delete(self, states, version):
        # can delete if validation failed or archived
        acceptable_versions = states["validation failed"] + states["archived"]
        if version in acceptable_versions:
            return True
        return False

    def _valid(self, lic_or_parti, version_to_match):
        for record in lic_or_parti:
            if record['version'] == version_to_match and record['validation_status'] == 'validation passed':
                return True
        return False

    def _activate(self, versions, version_to_activate):
        new_versions = deepcopy(versions)
        for rec in new_versions:
            if rec['version'] == version_to_activate:
                rec['status'] = 'active'
        return new_versions

    def _archive(self, versions, version_to_archive):
        new_versions = deepcopy(versions)
        for rec in new_versions:
            if rec['version'] == version_to_archive:
                rec['status'] = 'archived'
        return new_versions

    def _delete(self, versions, lic_or_parti, version_to_delete):
        new_versions = deepcopy(versions)
        for rec in new_versions:
            if rec['version'] == version_to_delete:
                rec['status'] = 'deleted'
        new_lic_or_parti = deepcopy(lic_or_parti)
        for rec in new_lic_or_parti:
            if rec['version'] == version_to_delete:
                rec['record_id'] = ''
                rec['file_name'] = ''
        return new_versions, new_lic_or_parti

