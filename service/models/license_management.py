import csv
from typing import Union, Iterable, Type, Optional

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
        "active_license": "<The latest active license version number>",
        "active_participant": "<The latest active participant version number>",
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

    def increment_license_version(self):
        val = self.license_version + 1
        self._set_single("license_version", val, coerce=dataobj.to_int())

    @property
    def active_license(self):
        val = self._get_single("active_license", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    @active_license.setter
    def active_license(self, val):
        self._set_single("active_license", val, coerce=dataobj.to_int())

    @property
    def license_versions(self):
        print("In license versions")
        return self._get_list("license_versions")

    @license_versions.setter
    def license_versions(self, vals):
        self._set_list("license_versions", vals)

    def add_license_version(self, vals):
        do_int = dataobj.to_int()
        do_uc = dataobj.to_unicode()
        if vals.get('version', None) and vals.get('status', None) and vals['status'] in LRF_STATUS:
            vals['version'] = self._coerce(vals['version'], do_int)
            vals['status'] = self._coerce(vals['status'], do_uc)
            self._add_to_list("license_versions", vals)
            return vals
        return False

    def license_states(self):
        print("In License states")
        versions = self.license_versions
        print(versions)
        return self._version_states(versions)

    def validate_license_versions(self):
        all_version = []
        versions_by_state = self.license_states()
        print('versions_by_state')
        print(versions_by_state)
        print(versions_by_state.values())
        for version_list in self.license_states().values():
            all_version = all_version + version_list
        return all_version == list(set(all_version)) and max(all_version) == self.license_version

    @property
    def participant_version(self):
        val = self._get_single("participant_version", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    def increment_participant_version(self):
        val = self.participant_version + 1
        self._set_single("participant_version", val, coerce=dataobj.to_int())

    @property
    def participant_versions(self):
        return self._get_list("participant_versions")

    @participant_versions.setter
    def participant_versions(self, vals):
        self._set_list("participant_versions", vals)

    def add_participant_version(self, vals):
        do_int = dataobj.to_int()
        do_uc = dataobj.to_unicode()
        if vals.get('version', None) and vals.get('status', None) and vals['status'] in LRF_STATUS:
            vals['version'] = self._coerce(vals['version'], do_int)
            vals['status'] = self._coerce(vals['status'], do_uc)
            self._add_to_list("license_versions", vals)
            return vals
        return False

    @property
    def active_participant(self):
        val = self._get_single("active_participant", coerce=dataobj.to_int())
        if not val:
            val = 0
        return val

    @active_participant.setter
    def active_participant(self, val):
        self._set_single("active_participant", val, coerce=dataobj.to_int())

    def participant_states(self):
        return self._version_states(self.participant_versions())

    def validate_participant_versions(self):
        all_version = []
        for version_list in self.participant_states().values():
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
        # validate the object structure quickly
        self.increment_license_version()
        if not self._validate_version(self.license_version, self.license_versions):
            return False
        obj['version'] = self.license_version
        obj = self._validate_child(obj)
        self._add_to_list("license", obj)
        version_record = {
            'version': obj['version'],
            'status': obj['validation_status']
        }
        self.add_license_version(version_record)
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
        # validate the object structure quickly
        self.increment_participant_version()
        if not self._validate_version(self.participant_version, self.participant_versions):
            return False
        obj['version'] = self.participant_version
        obj = self._validate_child(obj)
        self._add_to_list("participant", obj)
        version_record = {
            'version': obj['version'],
            'status': obj['validation_status']
        }
        self.add_participant_version(version_record)
        return True

    def activate_license(self, version_to_activate):
        """
        # "validation failed", "validation passed", "active", "archived", "deleted"
        Activate the given version
        from state: validation passed or archived
        to state: active
        set current active license to archived
        """
        print('In activate')
        states = self.license_states()
        versions = self.license_versions
        print(states)
        print(versions)
        print('-'*50)
        new_versions = self._activate_child(versions, states, version_to_activate)
        print('updated versions')
        print(new_versions)
        is_valid = self._validate_versions(new_versions, self.license_version)
        if is_valid:
            self.license_versions = new_versions
            self.active_license = version_to_activate
            return True
        return False

    def activate_participant(self, version_to_activate):
        """
        # "validation failed", "validation passed", "active", "archived", "deleted"
        Activate the given version
        from state: validation passed or archived
        to state: active
        set current active license to archived
        """
        states = self.participant_states()
        versions = self.participant_versions()
        new_versions = self._activate_child(versions, states, version_to_activate)
        is_valid = self._validate_versions(new_versions, self.participant_version)
        if is_valid:
            self.participant_versions = new_versions
            self.active_participant = version_to_activate
            return True
        return False

    def archive_license(self, version_to_archive):
        """
        Archive the given version
        from state: "validation failed", "validation passed", "active"
        to state: "archived"
        """
        states = self.license_states()
        versions = self.license_versions
        new_versions = self._archive_child(versions, states, version_to_archive)
        is_valid = self._validate_versions(new_versions, self.license_version)
        if is_valid:
            self.license_versions = new_versions
            return True
        return False

    def archive_participant(self, version_to_archive):
        """
        Archive the given version
        from state: "validation failed", "validation passed", "active"
        to state: "archived"
        """
        states = self.participant_states()
        versions = self.participant_versions()
        new_versions = self._archive_child(versions, states, version_to_archive)
        is_valid = self._validate_versions(new_versions, self.participant_version)
        if is_valid:
            self.license_versions = new_versions
            return True
        return False

    def delete_license(self, version_to_delete):
        """
        Delete the given version
        from state: "validation failed", "validation passed", "archived"
        to state: "deleted"
        Delete license record
        Delete license file on disk
        """
        pass

    def delete_participant(self, version_to_delete):
        """
        Delete the given version
        from state: "validation failed", "validation passed", "archived"
        to state: "deleted"
        Delete participant record
        Delete participant file on disk
        """
        pass

    def record_id(self, record_version):
        # record_id will be same as id with version appended '{self.id}_v{record_version}'
        return f"{self.id}_v{record_version}"

    def _validate_child(self, obj):
        """
        The object will be validated and types coerced as needed.
          - version of child will be the latest version
          - record_id will be same as id with latest version appended '{self.id}_v{latest_version}'
          - uploaded date will be set to now
        """
        obj['record_id'] = self.record_id(obj['version'])
        allowed = ["file_name", "name", "admin_notes", "uploaded_date", "record_id",
                   "validation_notes", "validation_status", "version"]
        for k in list(obj.keys()):
            if k not in allowed:
                raise dataobj.DataSchemaException("License object must only contain the following keys: {x}".
                                                  format(x=", ".join(allowed)))
        # coerce the values of the keys
        do_unicode = dataobj.to_unicode()
        for k in allowed:
            if k in ['uploaded_date', 'version']:
                continue
            if obj.get(k, None):
                obj[k] = self._coerce(obj[k], do_unicode)
        # uploaded_date
        do_date = dataobj.date_str()
        if obj.get("uploaded_date", None):
            uploaded_date = obj["uploaded_date"]
        else:
            uploaded_date = dates.now()
        obj["uploaded_date"] = self._coerce(uploaded_date, do_date)
        # version
        do_int = dataobj.to_int()
        obj["version"] = self._coerce(obj["version"], do_int)
        return obj

    def _validate_version(self, latest_version, versions):
        is_valid = True
        for rec in versions:
            if latest_version == rec['version']:
                is_valid = False
                return is_valid
        return is_valid

    def _version_states(self, versions):
        states = {}
        for state in LRF_STATUS:
            states[state] = []
        print(states)
        for rec in versions:
            print(rec)
            print('-'*5)
            states[rec['status']].append(rec['version'])
        return states

    def _validate_versions(self, versions, current_version):
        all_version_numbers = []
        for version in versions:
            all_version_numbers.append(version['version'])
        print(all_version_numbers)
        is_unique = all_version_numbers == list(set(all_version_numbers))
        version_is_correct = max(all_version_numbers) == current_version
        return is_unique and version_is_correct

    def _activate_child(self, versions, states, version_to_activate):
        acceptable_versions = states["validation passed"] + states["archived"]
        if version_to_activate in acceptable_versions:
            # archive existing one
            for rec in versions:
                if rec['status'] == 'active':
                    rec['status'] = 'archived'
            # set new one as active
            for rec in versions:
                if rec['version'] == version_to_activate:
                    rec['status'] = 'active'
        return versions

    def _archive_child(self, versions, states, version_to_archive):
        """
        # "validation failed", "validation passed", "active", "archived", "deleted"
        Archive the given version
        from state: "validation failed", "validation passed", "active"
        to state: "archived"
        """
        acceptable_versions = states["validation failed"] + states["validation passed"] + states["active"]
        if version_to_archive in acceptable_versions:
            # set new one as archive
            for rec in versions:
                if rec['version'] == version_to_archive:
                    rec['status'] = 'archived'
        return versions
