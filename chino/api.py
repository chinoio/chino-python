import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from chino.exceptions import MethodNotSupported, CallError, CallFail

__author__ = 'Stefano Tranquillini <stefano@chino.io>'

logger = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class ChinoAPI:
    """
    CHINO API wrapper
    """
    __username = ''
    __password = ''
    __url = 'https://api.chino.io/'

    # TODO: write docstring
    def __init__(self, username, password, version='v1', url=None):
        self.__username = username
        self.__password = password
        if url:
            self.__url = url
        self.__url = self.__url + version + "/"

    # AUTH
    def auth_user_login(self, username, password, customer_id):
        url = "auth/login"
        pars = dict(username=username, password=password, customer_id=customer_id)
        return self.__apicall(POST, url, params=pars)

    def auth_user_status(self):
        url = "auth/info"
        return self.__apicall(GET, url)

    def auth_user_logout(self):
        url = "auth/logout"
        return self.__apicall(GET, url)

    # USER
    def user_list(self, **pars):
        url = "users"
        return self.__apicall(GET, url, params=pars)

    def user_detail(self, user_id):
        url = "users/%s" % user_id
        return self.__apicall(GET, url)['user']

    def user_create(self, username, password, attributes):
        data = dict(username=username, password=password, attributes=attributes, )
        url = "users"
        return self.__apicall(POST, url, data=data)['user']

    def user_update(self, user_id, **kwargs):
        url = "users/%s" % user_id
        return self.__apicall(PUT, url, data=kwargs)['user']

    def user_delete(self, user_id, force=False):
        url = "users/%s" % user_id
        if force:
            params = dict(force=True)
        else:
            params = None
        return self.__apicall(DELETE, url, params)

    # GROUP
    def group_list(self, **pars):
        url = "groups"
        return self.__apicall(GET, url, params=pars)

    def group_detail(self, group_id):
        url = "groups/%s" % group_id
        return self.__apicall(GET, url)['group']

    def group_create(self, groupname, attributes):
        data = dict(groupname=groupname, attributes=attributes)
        url = "groups"
        return self.__apicall(POST, url, data=data)['group']

    def group_update(self, group_id, **kwargs):
        url = "groups/%s" % group_id
        return self.__apicall(PUT, url, data=kwargs)['group']

    def group_delete(self, group_id, force=False):
        url = "groups/%s" % group_id
        if force:
            params = dict(force=True)
        else:
            params = None
        return self.__apicall(DELETE, url, params)

    def group_add_user(self, group_id, user_id):
        url = "groups/%s/users/%s" % (group_id, user_id)
        return self.__apicall(POST, url)

    def group_del_user(self, group_id, user_id):
        url = "groups/%s/users/%s" % (group_id, user_id)
        return self.__apicall(DELETE, url)

    # PERMISSIONS

    def permission_user(self, user_id):
        url = "perms/users/%s" % user_id
        return self.__apicall(GET, url)

    def permission_create_user(self, schema_id, user_id, own_data, all_data, insert=True):
        data = dict(own_data=own_data, all_data=all_data, insert=insert)
        url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        return self.__apicall(POST, url, data)

    def permission_delete_user(self, schema_id, user_id):
        url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        return self.__apicall(DELETE, url)

    def permission_group(self, group_id):
        url = "perms/groups/%s" % group_id
        return self.__apicall(GET, url)

    def permission_schema(self, schema_id):
        url = "perms/schemas/%s" % schema_id
        return self.__apicall(GET, url)

    def permission_create_group(self, schema_id, group_id, own_data, all_data, insert=True):
        data = dict(own_data=own_data, all_data=all_data, insert=insert)
        url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        return self.__apicall(POST, url, data)

    def permission_delete_group(self, schema_id, group_id):
        url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        return self.__apicall(DELETE, url)

    # REPOSITORY

    def repository_list(self, **pars):
        """
        Gets the list of repository

        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset`` and the list of items
        inside a property with its name (e.g., ``documents``)
        """
        url = "repositories"
        return self.__apicall(GET, url, params=pars)

    def repository_detail(self, repository_id):
        """
        Gets the details of repository.

        :param repository_id: (id) the id of the repository
        :return: (dict) the repository.
        """
        url = "repositories/%s" % repository_id
        return self.__apicall(GET, url)['repository']

    def repository_create(self, description):
        """
        Creates a a repository.

        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        data = dict(description=description)
        url = "repositories"
        return self.__apicall(POST, url, data=data)['repository']

    def repository_update(self, repository_id, **kwargs):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        url = "repositories/%s" % repository_id
        return self.__apicall(PUT, url, data=kwargs)['repository']

    def repository_delete(self, repository_id, force=False):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :return: None
        """
        url = "repositories/%s" % repository_id
        if force:
            params = dict(force=True)
        else:
            params = None
        return self.__apicall(DELETE, url, params)

    # SCHEMA

    def schemas_list(self, repository_id, **pars):
        """
        Gets the list of docuemnts by schema

        :param repository_id: (id) the id of the repository
        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset``,``repositories``
        """
        url = "repositories/%s/schemas" % repository_id
        return self.__apicall(GET, url, params=pars)

    def schema_create(self, repository, description, fields):
        """
        Creates a schema in a repository.

        :param repository: (id) the repository in which the schema is created
        :param description: (str) the name of the schema
        :param fields: list(dict) the list of fields
        :return: (dict) the schema.
        """
        data = dict(description=description, structure=dict(fields=fields))
        url = "repositories/%s/schemas" % repository
        return self.__apicall(POST, url, data=data)['schema']

    def schema_detail(self, schema_id):
        """
        Details of a schema in a repository.

        :param schema_id: (id) of the schema
        :return: (dict) the schema.
        """
        url = "schemas/%s" % schema_id
        return self.__apicall(GET, url)['schema']

    def schema_update(self, schema_id, **kwargs):
        url = "schemas/%s" % schema_id
        return self.__apicall(PUT, url, data=kwargs)['schema']

    def schema_delete(self, schema_id, force=False):
        url = "schemas/%s" % schema_id
        if force:
            params = dict(force=True)
        else:
            params = None
        return self.__apicall(DELETE, url, params)

    # DOCUMENT

    def documents_list(self, schema_id, **pars):
        url = "schemas/%s/documents" % schema_id
        return self.__apicall(GET, url, params=pars)

    def document_create(self, schema_id, content, insert_user=None):
        data = dict(content=content)
        if insert_user:
            data['insert_user'] = insert_user
        url = "schemas/%s/documents" % schema_id
        return self.__apicall(POST, url, data=data)['document']

    def document_detail(self, document_id):
        url = "documents/%s" % document_id
        return self.__apicall(GET, url)['document']

    def document_update(self, document_id, **kwargs):
        # data = dict(content=content)
        url = "documents/%s" % document_id
        return self.__apicall(PUT, url, data=kwargs)['document']

    def document_delete(self, document_id, force=False):
        url = "documents/%s" % document_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.__apicall(DELETE, url, params)

    # BLOBS

    def blob_start(self, document_id, field, field_name):
        url = 'blobs'
        data = dict(document_id=document_id, field=field, field_name=field_name)
        return self.__apicall(POST, url, data=data)['blob']

    def blob_chunk(self, upload_id, data, offset):
        url = 'blobs'
        data = dict(upload_id=upload_id, data=data, offset=offset)
        return self.__apicall(PUT, url, data=data)['blob']

    def blob_commit(self, upload_id):
        url = 'blobs/commit'
        data = dict(upload_id=upload_id)
        return self.__apicall(POST, url, data=data)['blob']

    def blob_detail(self, blob_id):
        url = 'blobs/%s' % blob_id
        # this is different
        res = self.__apicall_get(url, None)
        fname = res.headers['Content-Disposition'].split(';')[1].split('=')[1]
        return dict(filename=fname, blob=res.json())

    def blob_delete(self, blob_id):
        url = 'blobs/%s' % blob_id
        return self.__apicall(DELETE, url)

    # Search

    def search(self, schema_id, result_type="FULL_CONTENT", filter_type="and", sort=None, filters=None):
        url = 'search'
        if not sort:
            sort = []
        if not filters:
            filters = []
        data = dict(schema_id=schema_id, result_type=result_type, filter_type=filter_type, sort=sort, filters=filters)
        return self.__apicall(POST, url, data=data)['documents']

    # UTILS
    def __apicall(self, method, url, params=None, data=None):

        url = self.__url + url
        print "-- calling %s %s (%s) %s" % (method, url, params, data)
        if method == GET:
            res = self.__apicall_get(url, params)
        elif method == POST:
            res = self.__apicall_post(url, data)
        elif method == PUT:
            res = self.__apicall_put(url, data)
        elif method == DELETE:
            res = self.__apicall_delete(url, params)
        else:
            raise MethodNotSupported
        self.valid_call(res)
        try:
            # if result has data
            data = res.json()['data']
            return data
        except:
            # emtpy response without errors, return True
            return True

    def __apicall_put(self, url, data):
        r = requests.put(url, auth=HTTPBasicAuth(self.__username, self.__password), data=json.dumps(data))
        return r

    def __apicall_post(self, url, data):
        r = requests.post(url, auth=HTTPBasicAuth(self.__username, self.__password), data=json.dumps(data))
        return r

    def __apicall_get(self, url, params):
        r = requests.get(url, auth=HTTPBasicAuth(self.__username, self.__password), params=params)
        return r

    def __apicall_delete(self, url, params):
        r = requests.delete(url, auth=HTTPBasicAuth(self.__username, self.__password), params=params)
        return r

    @staticmethod
    def valid_call(r):
        if r.status_code == requests.codes.ok:
            return True
        else:
            try:
                status = r.json()['result']
            except:
                raise CallError(code=500, message="Something went wrong with the server")
            if status == "error":
                raise CallError(code=r.status_code, message=r.json()['message'])
            elif status == "fail":
                raise CallFail(code=r.status_code, message=r.json()['data'])
            else:
                raise CallError(code=r.status_code, message=r.json())
