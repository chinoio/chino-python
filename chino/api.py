__author__ = 'Stefano Tranquillini <stefano@chino.io>'

import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from chino.exceptions import MethodNotSupported, CallError, CallFail


log = logging.getLogger(__name__)

GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class ChinoAPI():
    __username = ''
    __password = ''
    __url = 'http://api.chino.io/v1/'

    def __init__(self, username, password):
        self.__username = username
        self.__password = password

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

    def repository_update(self, repository_id, description):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        data = dict(description=description)
        url = "repositories/%s" % repository_id
        return self.__apicall(PUT, url, data=data)['repository']

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
        return self.__apicall(DELETE, url, params)['repository']

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

    #DOCUMENT

    def documents_list(self, schema_id, **pars):
        """
        Gets the list of docuemnts by schema

        :param schema_id: (id) the id of the schema
        :param: usual for a list ``offset``, ``limit``, plus ``full_document``
        :return: dict containing ``count``,``total_count``,``limit``,``offset``,``documents``
        """
        url = "schemas/%s/documents" % schema_id
        return self.__apicall(GET, url, params=pars)    

    def document_create(self, schema, content):
        """
        Creates a document with a schema and content

        :param schema: (id) the schema for the doc
        :param content: (dict) the content of the doc
        :return: (dict) the document
        """
        data = dict(content=content)
        url = "schemas/%s/documents" % schema
        return self.__apicall(POST, url, data=data)['document']

    #UTILS

    def __apicall(self, method, url, params=None, data=None):
        url = self.__url + url
        if method == GET:
            res = self.__apicall_get(url, params)
        elif method == POST:
            res = self.__apicall_post(url, data)
        elif method == PUT:
            res = self.__apicall_put(url, data)
        elif method == DELETE:
            res = self.__apicall_delete(url)
        else:
            raise MethodNotSupported
        self.valid_call(res)
        return res.json()['data']

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
        r = requests.delete(url, auth=HTTPBasicAuth(self.__username, self.__password),params=params)
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