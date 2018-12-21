from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import json
from collections import namedtuple

__author__ = 'Stefano Tranquillini <stefano@chino.io>'
import logging
logger = logging.getLogger('chino')


class ChinoBaseObject(object):
    __str_name__ = 'not set'
    __str_names__ = 'not set'

    @property
    def _id(self):
        return '-'

    def to_json(self):
        # raise NotImplementedError()
        return json.dumps(self, default=lambda o: o.to_dict() if hasattr(o, 'to_dict()') else o.__dict__,
                          sort_keys=True, indent=4)

    def to_dict(self):
        # make a copy here
        return dict(self.__dict__)

    def __str__(self):
        # return str(self.to_dict())
        return "%s - %s" % (self.__str_name__.upper(), self.to_dict())

    def __repr__(self):
        # return str(self.to_dict())
        return "<%s:%s>" % (self.__str_name__.upper(), self._id)


class Paging(ChinoBaseObject):

    def __init__(self, offset=0, limit=100, count=-1, total_count=-1, **kwargs):
        super(Paging, self).__init__()
        self.offset = offset
        self.limit = limit
        self.total_count = total_count
        self.count = count

    def as_map(self):
        return {
            'offset': self.offset,
            'limit': self.limit,
        }

    def __str__(self):
        return "Paging [offset:%s,limit:%s,count:%s,total_count:%s]" % (self.offset, self.limit, self.count, self.total_count)


class ListResult(ChinoBaseObject):

    def __init__(self, class_obj, result, **kwargs):
        self.paging = Paging(result['offset'], result['limit'], result[
                             'count'], result['total_count'])
        results = []
        for r in result[class_obj.__str_names__]:
            if type(r) == dict:
                results.append(class_obj(**r))
            else:
                results.append(class_obj(r))
        self.__setattr__(class_obj.__str_names__, results)
        self.class_obj = class_obj.__str_names__

    def to_dict(self):
        res = super(ListResult, self).to_dict()
        res['paging'] = self.paging.to_dict()
        res[self.class_obj] = [o.to_dict()
                               for o in self.__getattribute__(self.class_obj)]
        del res['class_obj']
        return res


class _DictContent(ChinoBaseObject):
    """
    Subclass for the content that is a dict.

    Example::

        "content": {
            "physician_id": "130b875a-d291-453e-8559-1b3c54500432",
            "physician_name": "Jack",
            "observation": "The patient was ok.",
            "visit_date": "2015-02-19 16:39:47"
        }
    """

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @property
    def _id(self):
        return "-"


class IDs(ChinoBaseObject):
    __str_name__ = 'ID'
    __str_names__ = 'IDs'

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return self.id

    def __str__(self):
        return self.id

class Repository(ChinoBaseObject):
    """

    Example::

            "repository": {
              "repository_id": "d88084ef-b6f7-405d-9863-d35b99543389",
              "last_update": "2015-02-24T21:48:16.332",
              "is_active": true,
              "description": "This is a test repo",
              "insert_date": "2015-02-24T21:48:16.332"
            }

    """
    __str_name__ = 'repository'
    __str_names__ = 'repositories'

    @property
    def _id(self):
        return self.repository_id

    def __init__(self, repository_id=None, insert_date=None, last_update=None, description=None, is_active=True, **kwargs):
        self.repository_id = repository_id
        self.description = description
        self.insert_date = insert_date
        self.last_update = last_update
        self.is_active = is_active


class User(ChinoBaseObject):
    """

    Example::

        "user": {
          "username": "james",
          "user_id": "d88084ef-b6f7-405d-9863-d35b99543389",
          "insert_date": "2015-02-05T10:53:38.157",
          "last_update": "2015-02-05T10:53:38.157",
          "is_active": true,
          "attributes": {
            "first_name": "James",
            "last_name": "Ford",
            "email": "james@acme.com"
          },
          "groups": [
            "d88084ef-b6f7-405d-9863-d35b99543389",
            "1eb39c88-3ac8-4664-b897-849dd260c72b"
          ]
        }

    For the creation it has `password`
    """
    __str_name__ = 'user'
    __str_names__ = 'users'

    @property
    def _id(self):
        return self.user_id

    def to_dict(self):
        res = super(User, self).to_dict()
        if hasattr(res, 'password'):
            del res['password']
        if self.attributes:
            if type(self.attributes) is not dict:
                res['attributes'] = self.attributes.to_dict()
        return res

    def __init__(self, user_id=None, username=None, insert_date=None, schema_id=None, last_update=None, is_active=None,
                 attributes=None,
                 groups=None, password=None, **kwargs):
        self.username = username
        self.user_id = user_id
        self.insert_date = insert_date
        self.last_update = last_update
        self.schema_id = schema_id
        self.is_active = is_active
        self.attributes = _DictContent(**attributes) if attributes else None
        self.groups = groups
        self.password = password


# TODO: add attribute funciton

class Group(ChinoBaseObject):
    """

    Example::

        "group": {
          "groupname": "pysiciansXY",
          "group_id": "77de01d8-492d-4cc2-a2b2-d3e76edc0657",
          "insert_date": "2015-02-07T12:14:46.754",
          "is_active": true,
          "last_update": "2015-02-21T19:07:45.832",
          "attributes": {
            "hospital": "Main Hospital"
          }
        }

    """

    __str_name__ = 'group'
    __str_names__ = 'groups'

    @property
    def _id(self):
        return self.group_id

    def to_dict(self):
        res = super(Group, self).to_dict()
        if self.attributes:
            if type(self.attributes) is not dict:
                res['attributes'] = self.attributes.to_dict()
        return res

    def __init__(self, group_id=None, group_name=None, insert_date=None, is_active=None, last_update=None,
                 attributes=None, **kwargs):
        """Constructor for Group"""
        self.group_id = group_id
        self.group_name = group_name
        self.insert_date = insert_date
        self.last_update = last_update
        self.is_active = is_active
        self.attributes = _DictContent(**attributes) if attributes else None


class Document(ChinoBaseObject):
    """
    Class for the document.

    Example::

        "document": {
          "document_id": "c373ba1a-1f23-4e36-a099-0ea3306b093d",
          "repository_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
          "schema_id": "130b875a-d291-453e-8559-1b3c54500432",
          "insert_date": "2015-02-24T22:27:35.919",
          "is_active": true,
          "last_update": "2015-02-24T22:27:35.919",
          "content": {
            "physician_id": "130b875a-d291-453e-8559-1b3c54500432",
            "physician_name": "Jack",
            "observation": "The patient was ok.",
            "visit_date": "2015-02-19 16:39:47"
          }
        }
    """
    __str_name__ = 'document'
    __str_names__ = 'documents'

    @property
    def _id(self):
        return self.document_id

    def to_dict(self):
        res = super(Document, self).to_dict()
        if self.content:
            res['content'] = self.content.to_dict()
        return res

    def __init__(self, document_id=None, repository_id=None, schema_id=None, insert_date=None, last_update=True,
                 content=None, is_active=False, **kwargs):
        self.document_id = document_id
        self.repository_id = repository_id
        self.schema_id = schema_id
        self.insert_date = insert_date
        self.last_update = last_update
        self.is_active = is_active
        self.content = _DictContent(**content) if content else None


class _Field(ChinoBaseObject):

    def __init__(self, type, name, indexed=None, **kwargs):
        self.type = type
        self.name = name
        if indexed:
            self.indexed = indexed

    __str_name__ = 'field'
    __str_names__ = 'fields'

    @property
    def _id(self):
        return '-'


class _Fields(ChinoBaseObject):

    def __init__(self, fields):
        self.fields = fields


class Schema(ChinoBaseObject):
    """

    Example::

            "schema": {
              "description": "testSchema",
              "schema_id": "b1cc4a53-19a1-4819-a8c7-20bf153ec9cf",
              "repository_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
              "is_active": true,
              "insert_date": "2015-02-15T16:22:04.058",
              "last_update": "2015-02-15T16:22:04.058",
              "structure": {
                "fields": [
                  {
                    "type": "integer",
                    "name": "test_int"
                  },
                  {
                    "type": "float",
                    "name": "test_float"
                  },
                  {
                    "type": "string",
                    "name": "test_string"
                  },
                  {
                    "type": "boolean",
                    "name": "test_boolean"
                  },
                  {
                    "type": "data",
                    "name": "test_date"
                  },
                  {
                    "type": "time",
                    "name": "test_time"
                  },
                  {
                    "type": "datetime",
                    "name": "test_datetime"
                  }
                ]
              }
            }
    """

    __str_name__ = 'schema'
    __str_names__ = 'schemas'

    def to_dict(self):
        res = super(Schema, self).to_dict()
        res['structure'] = dict(fields=[f.to_dict()
                                        for f in self.structure.fields])
        return res

    # # print res
    #     if self.structure:
    #         if type(self.structure) is not dict:
    #             res['structure'] = dict(fields=[f.to_dict() for f in self.structure.fields])
    #     return res

    @property
    def _id(self):
        return self.schema_id

    def __init__(self, schema_id=None, description=None, repository_id=None, is_active=None, insert_date=None,
                 last_update=None, structure=None, **kwargs):
        self.schema_id = schema_id
        self.description = description
        self.repository_id = repository_id
        self.is_active = is_active
        self.insert_date = insert_date
        self.last_update = last_update
        # assuming it's a dict.
        if structure:
            self.structure = _Fields(
                fields=[_Field(**f) for f in structure['fields']])


class UserSchema(ChinoBaseObject):
    """
    Similar to Schema
    """
    __str_name__ = 'user_schema'
    __str_names__ = 'user_schemas'

    def to_dict(self):
        res = super(UserSchema, self).to_dict()
        res['structure'] = dict(fields=[f.to_dict()
                                        for f in self.structure.fields])
        return res

    @property
    def _id(self):
        return self.user_schema_id

    def __init__(self, user_schema_id=None, description=None, is_active=None, insert_date=None,
                 last_update=None, structure=None, groups=None, **kwargs):
        self.user_schema_id = user_schema_id
        self.description = description
        self.groups = groups
        self.is_active = is_active
        self.insert_date = insert_date
        self.last_update = last_update
        # assuming it's a dict.
        if structure:
            self.structure = _Fields(
                fields=[_Field(**f) for f in structure['fields']])


class Collection(ChinoBaseObject):
    """
    Class for the Collection.

    Example::

        "collection":
            {
              "collection_id": "de991a83-da39-4a72-a79e-1376124ebd57",
              "last_update": "2016-02-08T11:05:26.571Z",
              "is_active": true,
              "name": "testCollection",
              "insert_date": "2016-02-08T11:05:26.571Z"
            }
    """
    __str_name__ = 'collection'
    __str_names__ = 'collections'

    @property
    def _id(self):
        return self.collection_id

    def __init__(self, collection_id=None, name=None, insert_date=None, last_update=True,
                 content=None, is_active=False, **kwargs):
        self.collection_id = collection_id
        self.name = name
        self.insert_date = insert_date
        self.last_update = last_update
        self.is_active = is_active


class Application(ChinoBaseObject):
    """
    Class for the Collection.

    Example::
          "data": {
            "app_secret": "bBRdHHPmIHbEzywlrK3v9sjbvDXLG20xNhMuyX7g1hAbP4ht7aznD7O7gcKlfhWUZ8osgJezZGK4EainErX4ktxkMX56KtihFiKVtfw8pMVDIVx1N3XjhqTbTTIGv4g7",
            "grant_type": "authorization-code",
            "app_name": "Teest",
            "redirect_url": "http://127.0.0.1/",
            "app_id": "4ke1mor5GW4YtH80Y9eIaAFLHUAwLtQ1l7wOQnQV"
          },
    """
    __str_name__ = 'application'
    __str_names__ = 'applications'

    @property
    def _id(self):
        return self.app_id

    def __init__(self, app_name=None, app_secret=None, app_id=None, redirect_url=None, grant_type=None,  **kwargs):
        self.app_name = app_name
        self.app_secret = app_secret
        self.app_id = app_id
        self.redirect_url = redirect_url
        self.grant_type = grant_type
        # self.client_type = client_type

class Permission(ChinoBaseObject):
    """
    Class for the Permission.

    Example::

        {
           "message":null,
           "data":{
              "permissions":[
                 {
                    "access":"Structure",
                    "permission":{
                       "Authorize":[
                          "R",
                          "U",
                          "D",
                          "A"
                       ],
                       "Manage":[
                          "R",
                          "U",
                          "D"
                       ]
                    },
                    "resource_type":"Schema",
                    "resource_id":"6cc90e37-4018-4503-8e9b-c0f3057abd6d"
                 }
              ]
           },
           "result":"success",
           "result_code":200
        }
    """
    __str_name__ = 'permission'
    __str_names__ = 'permissions'

    @property
    def _id(self):
        return "-"

    def __init__(self, access=None, permission=None, resource_type=None, resource_id=None, parent_id=None, **kwargs):
        self.access = access
        if permission:
            self.permission = _PermissionField(**permission)
        self.resource_type = resource_type
        if resource_id:
            self.resource_id = resource_id
        else:
            # TODO: can parent_id be None?
            self.parent_id = parent_id

    def to_dict(self):
        res = super(Permission, self).to_dict()
        res['permission'] = self.permission.to_dict()
        return res


class _PermissionField(ChinoBaseObject):

    def __init__(self, Authorize=None, Manage=None, created_document=None, **kwargs):
        if Authorize:
            self.authorize = Authorize
        if Manage:
            self.manage = Manage
        if created_document:
            self.created_document = created_document

    # TODO: support functions to help in managing grants

    @property
    def _id(self):
        return "-"

    def to_dict(self):
        res = dict()
        if hasattr(self, 'authorize'):
            res['authorize'] = self.authorize
        if hasattr(self, 'manage'):
            res['manage'] = self.manage
        if hasattr(self, 'created_document'):
            res['created_document'] = self.created_document
        return res


class _SortField(ChinoBaseObject):

    def __init__(self, field, order='asc', **kwargs):
        self.field = field
        self.order = order

    @property
    def _id(self):
        return "-"


class _FilterField(ChinoBaseObject):

    def __init__(self, field, value, type='eq', case_sensitive=False, **kwargs):
        self.field = field
        self.type = type
        self.case_sensitive = case_sensitive
        self.value = value

    @property
    def _id(self):
        return "-"


class Search(ChinoBaseObject):

    def __init__(self, schema_id, result_type, sort=None, filters=None, **kwargs):
        self.schema_id = schema_id
        self.result_type = result_type
        self.sort = []
        self.filters = []
        if sort:
            for s in sort:
                if type(s) is dict:
                    self.sort.append(_SortField(**s))
                else:
                    self.sort.append(s)
        if filters:
            for f in filters:
                if type(f) is dict:
                    self.filters.append(_FilterField(**f))
                else:
                    self.sort.append(f)

    def to_dict(self):
        res = super(Search, self).to_dict()
        if self.sort:
            res['sort'] = [s.to_dict() for s in self.sort]
        if self.filters:
            res['filters'] = [f.to_dict() for f in self.filters]
        return res

class Consent(ChinoBaseObject):
    """

    Example:

            consent : {
              "message": null,
              "data": {
                "count": 2,
                "total_count": 2,
                "consents": [
                  {
                    "user_id": "admin@chino.io",
                    "description": "a long textual description",
                    "data_controller": {
                      "company": "Acme",
                      "contact": "John Doe",
                      "address": "221B Baker St.",
                      "email": "info@acme.com",
                      "VAT": "IT03256920228",
                      "on_behalf": true
                    },
                    "consent_id": "0a63b938-c481-42aa-8da2-1db34f2d0dea",
                    "purposes": [
                      {
                        "authorized": true,
                        "purpose": "marketing",
                        "description": "mailing list"
                      }
                    ],
                    "policy_url": "https://chino.io/legal/privacy-policy",
                    "policy_version": "v1.0",
                    "withdrawn_date": null,
                    "inserted_date": "2018-01-26T13:16:28.680Z",
                    "collection_mode": "webform"
                  }
                ],
                "limit": 10,
                "offset": 0
              },
              "result": "success",
              "result_code": 200
            }

    """
    __str_name__ = 'consent'
    __str_names__ ='consents'

    @property
    def _id(self):
        return self.consent_id

    def to_dict(self):
        res = super(Consent, self).to_dict()
        if self.data_controller:
            res['data_controller'] = self.data_controller.to_dict()
        if self.purposes:
            res['purposes'] = [purpose.to_dict() for purpose in self.purposes]

        return res


    def __init__(self, consent_id=None, user_id=None, description=None, data_controller=None, purposes=None,
                        policy_url=None, policy_version=None, collection_mode=None, inserted_date=None, withdrawn_date=None):
        self.user_id = user_id
        self.description = description
        self.data_controller = _DictContent(**data_controller) if data_controller else None
        self.consent_id = consent_id
        # 'purposes' is a list of dict-s
        if purposes:
            self.purposes = []
            for p in purposes:
                self.purposes.append(_DictContent(**p))
        else:
            self.purposes = None

        self.policy_url = policy_url
        self.policy_version = policy_version
        self.withdrawn_date = withdrawn_date    # should be always 'None' when a new instance is created
        self.inserted_date = inserted_date      # set by server
        self.collection_mode = collection_mode

    def is_withdrawn(self):
        """
        Check if this Consent has been withdrawn.

        :return: True if the 'withdrawn_date' attribute of this instance has been set, otherwise False
        """
        return (self.withdrawn_date != None)


_PermissionProperty = namedtuple(
    '_PermissionProperty', ['read', 'delete', 'update'])

# class _PermissionProperty(ChinoBaseObject):
# """
#         "read": true,
#         "update": false,
#         "delete": true
#
#     """
#
#     def __init__(self, read=False, update=False, delete=False):
#         self.read = read
#         self.delete = delete
#         self.update = update

# class _Permission(ChinoBaseObject):
#     """
#
#     "permission": {
#                   "insert": true,
#                   "all_data": {
#                     "read": true,
#                     "update": false,
#                     "delete": true
#                   },
#                   "own_data": {
#                     "read": true,
#                     "update": true,
#                     "delete": false
#                   }
#                 }
#     """
#
#     def __init__(self, insert, all_data, own_data):
#         self.insert = insert
#         if type(all_data) is dict:
#             self.all_data = _PermissionProperty(**all_data)
#         else:
#             self.all_data = all_data
#         if type(own_data) is dict:
#             self.own_data = _PermissionProperty(**own_data)
#         else:
#             self.own_data = own_data
#
#     def to_dict(self):
#         res = super(_Permission, self).to_dict()
#         if self.all_data:
#             res['all_data'] = [p.to_dict() for p in self.all_data]
#         if self.own_data:
#             res['own_data'] = [p.to_dict() for p in self.own_data]
#         return res
#
#
# class Permission(ChinoBaseObject):
#     """
#
#     Example::
#
#             "permissions": [
#               {
#                 "repository_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
#                 "schema_id": "b1cc4a53-19a1-4819-a8c7-20bf153ec9cf",
#                 "group_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
#                 "user_id": "b1cc4a53-19a1-4819-a8c7-20bf153ec9cf",
#                 "permission": {
#                   "insert": true,
#                   "all_data": {
#                     "read": true,
#                     "update": false,
#                     "delete": true
#                   },
#                   "own_data": {
#                     "read": true,
#                     "update": true,
#                     "delete": false
#                   }
#                 }
#               }
#             ]
#     """
#
#     def __init__(self, repository_id=None, schema_id=None, group_id=None, user_id=None, permission=None):
#         self.repository_id = repository_id
#         self.schema_id = schema_id
#         self.group_id = group_id
#         self.user_id = user_id
#         if permission:
#             if dict(permission) is dict:
#                 self.permission = _Permission(permission)
#             else:
#                 self.permission = permission
#
#     def to_dict(self):
#         res = super(Permission, self).to_dict()
#         if self.permission:
#             res['permission'] = [p.to_dict() for p in self.permission]
#         return res
#

Blob = namedtuple('Blob', ['filename', 'content'])
BlobDetail = namedtuple(
    'BlobDetail', ['bytes', 'blob_id', 'sha1', 'document_id', 'md5'])
