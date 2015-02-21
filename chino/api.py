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
    __url = 'http://136.243.19.82/v1/'

    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    @staticmethod
    def __response_list(l, field):
        """
        Creates the response for the paginated queries

        to access the result ::

            res[0] # the list of objects
            res[1][0] #count
            res[1][1] #total_count
            res[1][2] #limit
            res[1][3] #offset

        :param l: list
        :param field: the field where the data are contained
        :return: (list, (tuple)) the list of objects and a tuple containing ``count``, ``total_count``, ``limit``, ``offset``
        """
        return l[field], (l['count'], l['total_count'], l['limit'], l['offset'])

    def repository_list(self, **pars):
        """
        Gets the list of reporitory

        :param repository_id: (id) the id of the repository
        :return: (list, (tuple)) see :py:func:``CHINOAPI.__response_list``
        """
        url = "repositories"
        return self.__response_list(self.apicall(GET, url, **pars), 'repositories')


    def repository_detail(self, repository_id):
        """
        Gets the details of repository.

        :param repository_id: (id) the id of the repository
        :return: (dict) the repository.
        """
        url = "repositories/%s" % repository_id
        return self.apicall(GET, url)['repository']

    def repository_create(self, description):
        """
        Creates a a repository.

        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        data = dict(description=description)
        url = "/repositories"
        return self.apicall(POST, url, data=data)['repository']

    def repository_update(self, repository_id, description):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :param description: (str) the name of the repository
        :return: (dict) the repository.
        """
        data = dict(description=description)
        url = "/repositories/%s" % repository_id
        return self.apicall(PUT, url, data=data)['repository']

    def repository_delete(self, repository_id):
        """
        Creates a a repository.

        :param repository_id: (id) the id of the repository
        :return: None
        """
        url = "/repositories/%s" % repository_id
        return self.apicall(DELETE, url)['repository']


    def schema_create(self, repository, description, fields):
        """
        Creates a schema in a repository.

        :param repository: (id) the repository in which the schema is created
        :param description: (str) the name of the schema
        :param fields: list(dict) the list of fields
        :return: (dict) the schema.
        """
        data = dict(description=description, structure=dict(fields=fields))
        url = "/repositories/%s/schemas" % repository
        return self.apicall(POST, url, data=data)['schema']

    def document_create(self, schema, content):
        """
        Creates a document with a schema and content

        :param schema: (id) the schema for the doc
        :param content: (dict) the content of the doc
        :return: (dict) the document
        """
        data = dict(content=content)
        url = "/schemas/%s/documents" % schema
        return self.apicall(POST, url, data=data)['document']

    def apicall(self, method, url, data=None):
        url = self.__url + url
        if method == GET:
            res = self.__apicall_get(url)
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
        r = requests.put(url, auth=HTTPBasicAuth(self.__username, self.__username), data=json.dumps(data))
        return r

    def __apicall_post(self, url, data):
        r = requests.post(url, auth=HTTPBasicAuth(self.__username, self.__username), data=json.dumps(data))
        return r

    def __apicall_get(self, url, params=None):
        r = requests.get(url, auth=HTTPBasicAuth(self.__username, self.__username), params=params)
        return r

    def __apicall_delete(self, url):
        r = requests.delete(url, auth=HTTPBasicAuth(self.__username, self.__username))
        return r

    @staticmethod
    def valid_call(r):
        if r.status_code == requests.codes.ok:
            return True
        else:
            status = r.json()['status']
            if status == "error":
                raise CallError(code=r.status_code, message=r.json()['errors'])
            elif status == "fail":
                raise CallFail(code=r.status_code, message=r.json()['data'])
            else:
                raise CallError(code=r.status_code, message=r.json())