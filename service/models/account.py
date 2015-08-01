
from flask.ext.login import UserMixin
from werkzeug import generate_password_hash, check_password_hash

from octopus.core import app
from service import dao
from octopus.lib import dataobj

class Account(dataobj.DataObj, dao.AccountDAO, UserMixin):
    '''
    {
        "id" : "<unique persistent account id>",
        "created_date" : "<date account created>",
        "last_updated" : "<date account last modified>",

        "email" : "<account contact email>",
        "contact_name" : "<name of key contact>",
        "password" : "<hashed password for ui login>",
        "api_key" : "<api key for api auth>",
        "role" : ["<account role: repository, provider, admin>"],

        "repository" : {
            "name" : "<name of the repository>",
            "url" : "<url for the repository>"
        },

        "sword_repository" : {
            "username" : "<username for the router to authenticate with the repository>",
            "password" : "<reversibly encrypted password for the router to authenticate with the repository>",
            "collection" : "<url for deposit collection to receive content from the router>"
        },

        "packaging" : [
            "<identifier - in order of preference - that should be available for this repo.  Esp. via sword interface>"
        ],

        "embargo" : {
            "duration" : "<length of default embargo>",
            "from" : "<reference to field in data to measure embargo from>"
        }
>>>>>>> f95ccfcf622df05825431611afce607c6fbf727b
    }
    '''

    @property
    def hashed_password(self):
        return self._get_single("password", coerce=self._utf8_unicode())

    @hashed_password.setter
    def hashed_password(self, val):
        self._set_single("password", val, coerce=self._utf8_unicode())

        def set_password(self, password):
            coerced = self._utf8_unicode()(password)
            self._set_single("password", generate_password_hash(coerced), coerce=self._utf8_unicode())

    def check_password(self, password):
        coerced = self._utf8_unicode()(password)
        existing = self.hashed_password
        if existing is None:
            return False
        return check_password_hash(existing, coerced)

    def clear_password(self):
        self._delete("password")

    @property
    def is_super(self):
        return self.has_role(app.config["ACCOUNT_SUPER_USER_ROLE"])

    def has_role(self, role):
        return role in self.role

    @property
    def role(self):
        return self._get_list("role", coerce=self._utf8_unicode())

    def add_role(self, role):
        self._add_to_list("role", role, coerce=self._utf8_unicode())

    def remove_role(self, role):
        self.role = self.role.remove(role)

    @role.setter
    def role(self, role):
        self._set_list("role", role, coerce=self._utf8_unicode())

    @property
    def packaging(self):
        return self._get_list("packaging", coerce=self._utf8_unicode())

    def add_packaging(self, val):
        self._add_to_list("packaging", val, coerce=self._utf8_unicode(), unique=True)

    def can_log_in(self):
        return True

    def remove(self):
        if self.has_role('publisher'):
            un = self.id
            try:
                import os, subprocess
                fl = os.path.dirname(os.path.abspath(__file__)) + 'deleteFTPuser.sh'
                print "subprocessing " + fl
                subprocess.call([fl,un])
                print "deleting FTP user for " + un
            except:
                print "could not delete an FTP user for " + un
        self.delete()

    def become_publisher(self):
        # create an FTP user for the account, if it is a publisher
        # TODO / NOTE: if the service has to be scaled up to run on multiple machines, 
        # the ftp users should only be created on the machine that the ftp address points to.
        # so the create user scripts should be triggered on that machine. Alternatively the user 
        # accounts could be created on every machine - but that leaves more security issues. 
        # Better to restrict the ftp upload to one machine that is configured to accept them. Then 
        # when it runs the schedule, it will check the ftp folder locations and send any to the API 
        # endpoints, so the heavy lifting would still be distributed across machines.
        #un = self.data['email'].replace('@','_')
        un = self.id
        try:
            import os, subprocess
            fl = os.path.dirname(os.path.abspath(__file__)) + 'createFTPuser.sh'
            print "subprocessing " + fl
            subprocess.call( [ 'sudo', fl, un, self.data['api_key'] ] )
            print "creating FTP user for " + un
        except:
            print "could not create an FTP user for " + un
        self.add_role('publisher')
        self.save()

    def cease_publisher(self):
        un = self.id
        try:
            import os, subprocess
            fl = os.path.dirname(os.path.abspath(__file__)) + 'deleteFTPuser.sh'
            print "subprocessing " + fl
            subprocess.call(['sudo',fl,un])
            print "deleting FTP user for " + un
        except:
            print "could not delete an FTP user for " + un
        self.remove_role('publisher')
        self.save()
        
        
