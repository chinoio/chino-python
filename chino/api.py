# -*- coding: utf-8 -*-
'''
client for Chino.io API
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 by Chino SrlS
:license: Apache 2.0, see LICENSE for more details.
'''
import hashlib
import json
import os

import requests
from requests.auth import HTTPBasicAuth

from chino.exceptions import MethodNotSupported, CallError, CallFail, ClientError
from chino.objects import Repository, ListResult, User, Group, Schema, Document, Blob, BlobDetail, UserSchema, \
    Collection, Permission
import logging

__author__ = 'Stefano Tranquillini <stefano@chino.io>'

logger = logging.getLogger(__name__)


class ChinoAPIBase(object):  # PRAGMA: NO COVER
    '''
        Base class, contains the utils methods to call the APIs
    '''
    _url = None
    auth = None

    def __init__(self, auth, url):
        '''
        Init the class, auth is ref, so it can be changed and changes applies to all the other classes.

        :param auth: 
        :param url: 
        :return:
        '''
        self._url = url
        self.auth = auth

    # UTILS
    def apicall(self, method, url, params=None, data=None):
        method = method.upper()
        url = self._url + url
        logger.debug("calling %s %s p(%s) d(%s) " % (method, url, params, data))
        if method == 'GET':
            res = self._apicall_get(url, params)
        elif method == 'POST':
            res = self._apicall_post(url, data, params)
        elif method == 'PUT':
            res = self._apicall_put(url, data)
        elif method == 'DELETE':
            res = self._apicall_delete(url, params)
        elif method == 'PATCH':
            res = self._apicall_patch(url, data)
        else:
            raise MethodNotSupported
        self.valid_call(res)
        try:
            # if result has data
            ret = res.json()
            logger.debug("result: %s " % json.dumps(ret))
            logger.debug("-----")
            data = ret['data']
            return data
        except:
            # emtpy response without errors, return True
            return True

    def _apicall_put(self, url, data):
        if hasattr(data, 'to_dict()'):
            d = data.to_dict()
        else:
            d = data
        r = requests.put(url, auth=self._get_auth(), data=json.dumps(d))
        return r

    def _apicall_patch(self, url, data):
        if hasattr(data, 'to_dict()'):
            d = data.to_dict()
        else:
            d = data
        r = requests.patch(url, auth=self._get_auth(), data=json.dumps(d))
        return r

    def _apicall_post(self, url, data, params):
        if hasattr(data, 'to_dict()'):
            d = data.to_dict()
        else:
            d = data
        r = requests.post(url, auth=self._get_auth(), params=params, data=json.dumps(d))
        return r

    def _apicall_get(self, url, params):
        r = requests.get(url, auth=self._get_auth(), params=params)
        return r

    def _apicall_delete(self, url, params):
        r = requests.delete(url, auth=self._get_auth(), params=params)
        return r

    def _get_auth(self):
        return self.auth.get_auth()

    @staticmethod
    def valid_call(r):
        # logger.debug("%s Response %s ", r.request.url, r.json())
        if r.status_code == requests.codes.ok:
            return True
        else:
            try:
                status = r.json()['result']
            except:
                raise CallError(code=500, message="Something went wrong with the server")
            if status == 'error':
                raise CallError(code=r.status_code, message=r.json()['message'])
            elif status == 'fail':
                raise CallFail(code=r.status_code, message=r.json()['data'])
            else:
                raise CallError(code=r.status_code, message=r.json())


class ChinoAPIUsers(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIUsers, self).__init__(auth, url)

    def login(self, username, password, customer_id=None):
        # remove auth and save in temp var (in case of problems)

        auth = self.auth
        # self.auth = None
        url = "auth/login"
        if not customer_id:
            customer_id = self.auth.customer_id
        pars = dict(username=username, password=password, customer_id=customer_id)
        try:
            user = self.apicall('POST', url, data=pars)['user']
            self.auth.access_token = user['access_token']
            self.auth.set_auth_user()
            return user
        except Exception as ex:
            # reset auth if things go wrong
            self.auth = auth
            # propagate exception
            raise ex

    def current(self):
        url = "auth/info"
        return User(**self.apicall('GET', url)['user'])

    def logout(self):
        url = "auth/logout"
        return self.apicall('POST', url)

        # USER

    def list(self, user_schema_id, **pars):
        url = "user_schemas/%s/users" % user_schema_id
        return ListResult(User, self.apicall('GET', url, params=pars))

    def detail(self, user_id):
        url = "users/%s" % user_id
        return User(**self.apicall('GET', url)['user'])

    def create(self, user_schema_id, username, password, attributes=None):
        data = dict(username=username, password=password, attributes=attributes, )
        url = "user_schemas/%s/users" % user_schema_id
        return User(**self.apicall('POST', url, data=data)['user'])

    def update(self, user_id, **kwargs):
        url = "users/%s" % user_id
        u_updated = self.apicall('PUT', url, data=kwargs)['user']
        return User(**u_updated)

    def partial_update(self, user_id, **kwargs):
        url = "users/%s" % user_id
        u_updated = self.apicall('PATCH', url, data=kwargs)['user']
        return User(**u_updated)

    def delete(self, user_id, force=False):
        url = "users/%s" % user_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)


class ChinoAPIGroups(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIGroups, self).__init__(auth, url)

    def list(self, **pars):
        url = "groups"
        return ListResult(Group, self.apicall('GET', url, params=pars))

    def detail(self, group_id):
        url = "groups/%s" % group_id
        return Group(**self.apicall('GET', url)['group'])

    def create(self, groupname, attributes=None):
        data = dict(group_name=groupname, attributes=attributes)
        url = "groups"
        return Group(**self.apicall('POST', url, data=data)['group'])

    def update(self, group_id, **kwargs):
        print kwargs
        url = "groups/%s" % group_id
        return self.apicall('PUT', url, data=kwargs)['group']

    def delete(self, group_id, force=False):
        url = "groups/%s" % group_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)

    def add_user(self, group_id, user_id):
        url = "groups/%s/users/%s" % (group_id, user_id)
        return self.apicall('POST', url)

    def del_user(self, group_id, user_id):
        url = "groups/%s/users/%s" % (group_id, user_id)
        return self.apicall('DELETE', url)


class ChinoAPIPermissions(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIPermissions, self).__init__(auth, url)

    def resources(self, action, resource_type, subject_type, subject_id, manage=None, authorize=None):
        url = "perms/%s/%s/%s/%s" % (action, resource_type, subject_type, subject_id)
        data = dict()
        if manage:
            data['manage'] = manage
        if authorize:
            data['authorize'] = authorize
        return self.apicall('POST', url, data=data)

    def resource(self, action, resource_type, resource_id, subject_type, subject_id,
                 manage=None, authorize=None):
        url = "perms/%s/%s/%s/%s/%s" % (action, resource_type, resource_id, subject_type, subject_id)
        data = dict()
        if manage:
            data['manage'] = manage
        if authorize:
            data['authorize'] = authorize
        return self.apicall('POST', url, data=data)

    def resource_children(self, action, resource_type, resource_id, resource_child_type, subject_type, subject_id,
                          manage=None, authorize=None):
        url = "perms/%s/%s/%s/%s/%s/%s" % (
            action, resource_type, resource_id, resource_child_type, subject_type, subject_id)
        data = dict()
        if manage:
            data['manage'] = manage
        if authorize:
            data['authorize'] = authorize
        return self.apicall('POST', url, data=data)

    def read_perms(self):
        url = "perms"
        res = self.apicall('GET', url)
        return [Permission(**p) for p in res['permissions']]

    def read_perms_document(self, document_id):
        url = "perms/documents/%s" % document_id
        return [Permission(**p) for p in self.apicall('GET', url)['permissions']]

    def read_perms_user(self, user_id):
        url = "perms/users/%s" % user_id
        return [Permission(**p) for p in self.apicall('GET', url)['permissions']]

    def read_perms_group(self, group_id):
        url = "perms/groups/%s" % group_id
        return [Permission(**p) for p in self.apicall('GET', url)['permissions']]

        # def user(self, user_id):
        #     url = "perms/users/%s" % user_id
        #     return self.apicall('GET', url)
        #
        # def create_user(self, schema_id, user_id, own_data, all_data, insert=True):
        #     data = dict(permissions=dict(own_data=own_data, all_data=all_data, insert=insert))
        #     url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        #     return self.apicall('POST', url, data=data)
        #
        # def delete_user(self, schema_id, user_id):
        #     url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        #     return self.apicall('DELETE', url)
        #
        # def group(self, group_id):
        #     url = "perms/groups/%s" % group_id
        #     return self.apicall('GET', url)
        #
        # def schema(self, schema_id):
        #     url = "perms/schemas/%s" % schema_id
        #     return self.apicall('GET', url)
        #
        # def create_group(self, schema_id, group_id, own_data, all_data, insert=True):
        #     data = dict(permissions=dict(own_data=own_data, all_data=all_data, insert=insert))
        #     url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        #     return self.apicall('POST', url, data=data)
        #
        # def delete_group(self, schema_id, group_id):
        #     url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        #     return self.apicall('DELETE', url)


        # def user(self, user_id):
        #     url = "perms/users/%s" % user_id
        #     return self.apicall('GET', url)
        #
        # def create_user(self, schema_id, user_id, own_data, all_data, insert=True):
        #     data = dict(permissions=dict(own_data=own_data, all_data=all_data, insert=insert))
        #     url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        #     return self.apicall('POST', url, data=data)
        #
        # def delete_user(self, schema_id, user_id):
        #     url = "perms/schemas/%s/users/%s" % (schema_id, user_id)
        #     return self.apicall('DELETE', url)
        #
        # def group(self, group_id):
        #     url = "perms/groups/%s" % group_id
        #     return self.apicall('GET', url)
        #
        # def schema(self, schema_id):
        #     url = "perms/schemas/%s" % schema_id
        #     return self.apicall('GET', url)
        #
        # def create_group(self, schema_id, group_id, own_data, all_data, insert=True):
        #     data = dict(permissions=dict(own_data=own_data, all_data=all_data, insert=insert))
        #     url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        #     return self.apicall('POST', url, data=data)
        #
        # def delete_group(self, schema_id, group_id):
        #     url = "perms/schemas/%s/groups/%s" % (schema_id, group_id)
        #     return self.apicall('DELETE', url)


class ChinoAPIRepositories(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIRepositories, self).__init__(auth, url)

    def list(self, **pars):
        """
        Gets the list of repository

        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset`` and the list of items
        inside a property with its name (e.g., ``documents``)
        """
        url = "repositories"
        return ListResult(Repository, self.apicall('GET', url, params=pars))

    def detail(self, repository_id):
        """
        Gets the details of repository.

        :param repository_id: (id) the id of the repository
        :return: (dict) the repository.
        """
        url = "repositories/%s" % repository_id
        return Repository(**self.apicall('GET', url)['repository'])

    def create(self, description):
        """
        Creates a a repository.

        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        data = dict(description=description)
        url = "repositories"
        return Repository(**self.apicall('POST', url, data=data)['repository'])

    def update(self, repository_id, **kwargs):
        """
        Update a a repository.

        :param repository_id: (id) the id of the repository
        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        url = "repositories/%s" % repository_id
        return Repository(**self.apicall('PUT', url, data=kwargs)['repository'])

    def delete(self, repository_id, force=False):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :return: None
        """
        url = "repositories/%s" % repository_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)


class ChinoAPISchemas(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPISchemas, self).__init__(auth, url)

    def list(self, repository_id, **pars):
        """
        Gets the list of docuemnts by schema

        :param repository_id: (id) the id of the repository
        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset``,``repositories``
        """
        url = "repositories/%s/schemas" % repository_id
        return ListResult(Schema, self.apicall('GET', url, params=pars))

    def create(self, repository, description, fields):
        """
        Creates a schema in a repository.

        :param repository: (id) the repository in which the schema is created
        :param description: (str) the name of the schema
        :param fields: list(dict) the list of fields
        :return: (dict) the schema.
        """
        data = dict(description=description, structure=dict(fields=fields))
        url = "repositories/%s/schemas" % repository
        return Schema(**self.apicall('POST', url, data=data)['schema'])

    def detail(self, schema_id):
        """
        Details of a schema in a repository.

        :param schema_id: (id) of the schema
        :return: (dict) the schema.
        """
        url = "schemas/%s" % schema_id
        return Schema(**self.apicall('GET', url)['schema'])

    def update(self, schema_id, **kwargs):
        url = "schemas/%s" % schema_id
        return Schema(**self.apicall('PUT', url, data=kwargs)['schema'])

    def delete(self, schema_id, force=False):
        url = "schemas/%s" % schema_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)


class ChinoAPIDocuments(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIDocuments, self).__init__(auth, url)

    def list(self, schema_id, **pars):
        url = "schemas/%s/documents" % schema_id
        return ListResult(Document, self.apicall('GET', url, params=pars))

    def create(self, schema_id, content):
        data = dict(content=content)
        url = "schemas/%s/documents" % schema_id
        return Document(**self.apicall('POST', url, data=data)['document'])

    def detail(self, document_id):
        url = "documents/%s" % document_id
        return Document(**self.apicall('GET', url)['document'])

    def update(self, document_id, **kwargs):
        # data = dict(content=content)
        url = "documents/%s" % document_id
        return Document(**self.apicall('PUT', url, data=kwargs)['document'])

    def delete(self, document_id, force=False):
        url = "documents/%s" % document_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)


class ChinoAPIBlobs(ChinoAPIBase):
    # TODO: update to new format
    def __init__(self, auth, url):
        super(ChinoAPIBlobs, self).__init__(auth, url)

    def send(self, document_id, blob_field_name, file_path, chunk_size=12 * 1024):
        if not os.path.exists(file_path):
            raise ClientError("File not found")
        # start the blob
        blobdata = self.start(document_id, blob_field_name, os.path.basename(file_path))
        # get the id and intial offset
        upload_id = blobdata['upload_id']
        offset = 0
        # open the file and start reading it
        logger.debug("file size %s", os.path.getsize(file_path))
        rd = open(file_path, "rb")

        sha1 = hashlib.sha1()
        chunk = ""
        length = 0
        offset = 0
        # read all the file
        with open(file_path, 'rb') as rd:
            # forever
            while True:
                byte = rd.read(1)
                # if we are at the end of the file, than break
                if not byte:
                    break
                # read the byte
                length += 1
                chunk += byte
                # if we have read enough bytes
                if length == chunk_size:
                    # send a cuhnk
                    self.chunk(upload_id, chunk, length=length, offset=offset)
                    # update the hash
                    sha1.update(chunk)
                    chunk = ""
                    offset += length
                    length = 0
        if length != 0:
            # send the last chunk
            self.chunk(upload_id, chunk, length=length, offset=offset)
            sha1.update(chunk)
        rd.close()
        # commit and check if everything was fine
        commit = self.commit(upload_id)
        if sha1.hexdigest() != commit['sha1']:
            raise CallFail(500, 'The file was not uploaded correctly')
        return BlobDetail(**commit)

    def start(self, document_id, field, field_name):
        url = 'blobs'
        data = dict(document_id=document_id, field=field, file_name=field_name)
        return self.apicall('POST', url, data=data)['blob']

    def chunk(self, upload_id, data, length, offset):
        # here we use directly request library to implement the binary
        url = self._url + 'blobs/%s' % upload_id
        # url = "http://httpbin.org/put"
        logger.debug("calling %s %s - h(%s) " % ('PUT', url, dict(length=length, offset=offset)))
        logger.debug("-----")
        res = requests.put(url, data=data, auth=self._get_auth(),
                           headers={'Content-Type': 'application/octet-stream', 'offset': offset, 'length': length})
        self.valid_call(res)
        return res.json()['data']['blob']

    def commit(self, upload_id):
        url = 'blobs/commit'
        data = dict(upload_id=upload_id)
        return self.apicall('POST', url, data=data)['blob']

    def detail(self, blob_id):
        # NOTE: this calls directly the function. needed to get the headers
        url = self._url + 'blobs/%s' % blob_id
        # this is different
        res = self._apicall_get(url, None)
        fname = res.headers['Content-Disposition'].split(';')[1].split('=')[1]
        return Blob(filename=fname, content=res.content)

    def delete(self, blob_id):
        url = 'blobs/%s' % blob_id
        return self.apicall('DELETE', url)


class ChinoAPISearches(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPISearches, self).__init__(auth, url)

    def search(self, schema_id, result_type="FULL_CONTENT", filter_type="and", sort=None, filters=None):
        url = 'search/'
        if not sort:
            sort = []
        if not filters:
            filters = []
        data = dict(schema_id=schema_id, result_type=result_type, filter_type=filter_type, sort=sort, filters=filters)
        return self.apicall('POST', url, data=data)['documents']


class ChinoAuth(object):
    customer_id = None
    customer_key = None
    access_token = None
    ACCESS_TOKEN = 'ACCESS_TOKEN'
    __auth = None

    # TODO: write docstring
    def __init__(self, customer_id, customer_key=None, access_token=None):
        '''
        Init the class

        :param customer_id: mandatory
        :param customer_key: optional, if specified the auth is set as chino customer (admin)
        :param access_token: optional, if specified the auth is as user
        :return: the class
        '''
        self.customer_id = customer_id
        self.customer_key = customer_key
        self.access_token = access_token
        # if customer_key is set, then set auth as that
        if customer_key:
            self.set_auth_admin()
        # if access_token is set, then use it as customer
        elif access_token:
            self.set_auth_user()

    def set_auth_admin(self):
        self.__auth = HTTPBasicAuth(self.customer_id, self.customer_key)

    def set_auth_user(self):
        self.__auth = HTTPBasicAuth(self.ACCESS_TOKEN, self.access_token)

    def get_auth(self):
        return self.__auth


class ChinoAPIUserSchemas(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPIUserSchemas, self).__init__(auth, url)

    def list(self, **pars):
        """
        Gets the list of UserSchemas

        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset``,``repositories``
        """
        url = "user_schemas"
        return ListResult(UserSchema, self.apicall('GET', url, params=pars))

    def create(self, description, fields):
        """
        Creates a UserSchema

        :param description: (str) the name of the schema
        :param fields: list(dict) the list of fields
        :return: (dict) the UserSchema.
        """
        data = dict(description=description, structure=dict(fields=fields))
        url = "user_schemas"
        return UserSchema(**self.apicall('POST', url, data=data)['user_schema'])

    def detail(self, user_schema_id):
        """
        Details of a UserSchema

        :param user_schema_id: (id) of the schema
        :return: (dict) the schema.
        """
        url = "user_schemas/%s" % user_schema_id
        return UserSchema(**self.apicall('GET', url)['user_schema'])

    def update(self, user_schema_id, **kwargs):
        """
        Updates a UserSchema
        :param user_schema_id:
        :param kwargs:
        :return:
        """
        url = "user_schemas/%s" % user_schema_id
        return UserSchema(**self.apicall('PUT', url, data=kwargs)['user_schema'])

    def delete(self, user_schema_id, force=False):
        url = "user_schemas/%s" % user_schema_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)


class ChinoAPICollections(ChinoAPIBase):
    def __init__(self, auth, url):
        super(ChinoAPICollections, self).__init__(auth, url)

    def list(self, **pars):
        """
        Gets the list of Collections

        :param: usual for a list ``offset``, ``limit``
        :return: dict containing ``count``,``total_count``,``limit``,``offset``,``repositories``
        """
        url = "collections"
        return ListResult(Collection, self.apicall('GET', url, params=pars))

    def create(self, name):
        """
        Creates a Collection

        :param name: (str) the name of the collection
        :return: (dict) the UserSchema.
        """
        data = dict(name=name)
        url = "collections"
        return Collection(**self.apicall('POST', url, data=data)['collection'])

    def detail(self, collection_id):
        """
        Details of a Collection

        :param collection_id: (id) of the Collection
        :return: (dict) the Collection.
        """
        url = "collections/%s" % collection_id
        return Collection(**self.apicall('GET', url)['collection'])

    def update(self, collection_id, **kwargs):
        url = "collections/%s" % collection_id
        return Collection(**self.apicall('PUT', url, data=kwargs)['collection'])

    def delete(self, collection_id, force=False):
        url = "collections/%s" % collection_id
        if force:
            params = dict(force='true')
        else:
            params = None
        return self.apicall('DELETE', url, params)

    def list_documents(self, collection_id, **pars):
        url = "collections/%s/documents" % collection_id
        return ListResult(Document, self.apicall('GET', url, params=pars))

    def add_document(self, collection_id, document_id):
        url = "collections/%s/documents/%s" % (collection_id, document_id)
        return self.apicall('POST', url)

    def rm_document(self, collection_id, document_id):
        url = "collections/%s/documents/%s" % (collection_id, document_id)
        return self.apicall('DELETE', url)

    def search(self, name, contains=False, **pars):
        url = "collections/search"
        data = dict(name=name, contains=contains)
        return ListResult(Collection, self.apicall('POST', url, params=pars, data=data))


class ChinoAPIClient(object):
    """
    ChinoAPI the client class
    """
    final_url = ""
    users = groups = permissions = repositories = schemas = documents = blobs = searches = None

    # TODO: change to prod url when ready
    def __init__(self, customer_id, customer_key=None, customer_token=None, version='v1',
                 url='https://api.test.chino.io/'):
        '''
        Init the class

        :param customer_id: mandatory
        :param customer_key: optional, if specified the auth is set as chino customer (admin)
        :param customer_token: optional, if specified the auth is as user
        :param version: default is `v1`, change if you know what to do
        :param url: the url, this should be changed only for testing
        :return: the class
        '''

        # smarter wayt o add slash?
        if not url.endswith('/'):
            url += '/'
        if not version.endswith('/'):
            version += '/'
        final_url = url + version
        self.final_url = final_url
        auth = ChinoAuth(customer_id, customer_key, customer_token)
        self.auth = auth
        self.users = ChinoAPIUsers(auth, final_url)
        self.groups = ChinoAPIGroups(auth, final_url)
        self.permissions = ChinoAPIPermissions(auth, final_url)
        self.repositories = ChinoAPIRepositories(auth, final_url)
        self.schemas = ChinoAPISchemas(auth, final_url)
        self.user_schemas = ChinoAPIUserSchemas(auth, final_url)
        self.collections = ChinoAPICollections(auth, final_url)
        self.documents = ChinoAPIDocuments(auth, final_url)
        self.blobs = ChinoAPIBlobs(auth, final_url)
        self.searches = ChinoAPISearches(auth, final_url)
