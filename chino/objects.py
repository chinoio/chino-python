import json
from collections import namedtuple

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'


class ChinoBaseObject(object):
    __str_name__ = 'not set'
    __str_names__ = 'not set'

    @property
    def id(self):
        raise NotImplementedError()

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
        return "<%s:%s>" % (self.__str_name__.upper(), self.id)


class Paging(ChinoBaseObject):
    def __init__(self, offset=0, limit=100, total_count=-1, count=-1):
        super(Paging, self).__init__()
        self.offset = offset
        self.limit = limit
        self.count = count
        self.total_count = total_count

    def as_map(self):
        return {
            'offset': self.offset,
            'limit': self.limit,
        }

    def __str__(self):
        return "Paging [offset:%s,limit:%s,count:%s]" % (self.offset, self.limit, self.count)


class ListResult(ChinoBaseObject):
    def __init__(self, class_obj, result):
        self.paging = Paging(result['offset'], result['limit'], result['count'], result['total_count'])
        results = []
        for r in result[class_obj.__str_names__]:
            results.append(class_obj(**r))
        self.__setattr__(class_obj.__str_names__, results)
        self.class_obj = class_obj.__str_names__

    def to_dict(self):
        res = super(ListResult, self).to_dict()
        res['paging'] = self.paging.to_dict()
        res[self.class_obj] = [o.to_dict() for o in self.__getattribute__(self.class_obj)]
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
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    @property
    def id(self):
        return "-"


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
    def id(self):
        return self.repository_id

    def __init__(self, repository_id=None, insert_date=None, last_update=None, description=None, is_active=True):
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
    def id(self):
        return self.user_id

    def to_dict(self):
        res = super(User, self).to_dict()
        if hasattr(res, 'password'):
            del res['password']
        if self.attributes:
            if type(self.attributes) is not dict:
                res['attributes'] = self.attributes.to_dict()
        return res

    def __init__(self, user_id=None, username=None, insert_date=None, last_update=None, is_active=None, attributes=None,
                 groups=None, password=None):
        self.username = username
        self.user_id = user_id
        self.insert_date = insert_date
        self.last_update = last_update
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
    def id(self):
        return self.group_id

    def to_dict(self):
        res = super(Group, self).to_dict()
        if self.attributes:
            if type(self.attributes) is not dict:
                res['attributes'] = self.attributes.to_dict()
        return res

    def __init__(self, group_id=None, groupname=None, insert_date=None, is_active=None, last_update=None,
                 attributes=None):
        """Constructor for Group"""
        self.group_id = group_id
        self.groupname = groupname
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
    def id(self):
        return self.document_id

    def to_dict(self):
        res = super(Document, self).to_dict()
        if self.content:
            res['content'] = self.content.to_dict()
        return res

    def __init__(self, document_id=None, repository_id=None, schema_id=None, insert_date=None, last_update=True,
                 content=None, is_active=False):
        self.document_id = document_id
        self.repository_id = repository_id
        self.schema_id = schema_id
        self.insert_date = insert_date
        self.last_update = last_update
        self.is_active = is_active
        self.content = _DictContent(**content) if content else None


class _Field(ChinoBaseObject):
    def __init__(self, type, name):
        self.type = type
        self.name = name

    __str_name__ = 'field'
    __str_names__ = 'fields'

    @property
    def id(self):
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
                    "type": "date",
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
        res['structure'] = dict(fields=[f.to_dict() for f in self.structure.fields])
        return res

    #     # print res
    #     if self.structure:
    #         if type(self.structure) is not dict:
    #             res['structure'] = dict(fields=[f.to_dict() for f in self.structure.fields])
    #     return res

    @property
    def id(self):
        return self.schema_id

    def __init__(self, schema_id=None, description=None, repository_id=None, is_active=None, insert_date=None,
                 last_update=None, structure=None, ):
        self.schema_id = schema_id
        self.description = description
        self.repository_id = repository_id
        self.is_active = is_active
        self.insert_date = insert_date
        self.last_update = last_update
        # assuming it's a dict.
        if structure:
            self.structure = _Fields(fields=[_Field(**f) for f in structure['fields']])
            # print "init %s" % type(structure)
            # if type(structure) == _Fields.__class__:
            #     self.structure = structure
            # elif type(structure) is dict:
            #
            # else:
            #     raise Exception('The field structure as an unknown type, only _Fields and dict are allowed.')


class _SortField(ChinoBaseObject):
    def __init__(self, field, order='asc'):
        self.field = field
        self.order = order

    @property
    def id(self):
        return "-"


class _FilterField(ChinoBaseObject):
    def __init__(self, field, value, type='eq', case_sensitive=False):
        self.field = field
        self.type = type
        self.case_sensitive = case_sensitive
        self.value = value

    @property
    def id(self):
        return "-"


class Search(ChinoBaseObject):
    def __init__(self, schema_id, result_type, sort=None, filters=None):
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


_PermissionProperty = namedtuple('_PermissionProperty', ['read', 'delete', 'update'])


# class _PermissionProperty(ChinoBaseObject):
#     """
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

class _Permission(ChinoBaseObject):
    """

    "permission": {
                  "insert": true,
                  "all_data": {
                    "read": true,
                    "update": false,
                    "delete": true
                  },
                  "own_data": {
                    "read": true,
                    "update": true,
                    "delete": false
                  }
                }
    """

    def __init__(self, insert, all_data, own_data):
        self.insert = insert
        if type(all_data) is dict:
            self.all_data = _PermissionProperty(**all_data)
        else:
            self.all_data = all_data
        if type(own_data) is dict:
            self.own_data = _PermissionProperty(**own_data)
        else:
            self.own_data = own_data

    def to_dict(self):
        res = super(_Permission, self).to_dict()
        if self.all_data:
            res['all_data'] = [p.to_dict() for p in self.all_data]
        if self.own_data:
            res['own_data'] = [p.to_dict() for p in self.own_data]
        return res


class Permission(ChinoBaseObject):
    """

    Example::

            "permissions": [
              {
                "repository_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
                "schema_id": "b1cc4a53-19a1-4819-a8c7-20bf153ec9cf",
                "group_id": "3ddba8af-6965-4416-9c5c-acf6af95539d",
                "user_id": "b1cc4a53-19a1-4819-a8c7-20bf153ec9cf",
                "permission": {
                  "insert": true,
                  "all_data": {
                    "read": true,
                    "update": false,
                    "delete": true
                  },
                  "own_data": {
                    "read": true,
                    "update": true,
                    "delete": false
                  }
                }
              }
            ]
    """

    def __init__(self, repository_id=None, schema_id=None, group_id=None, user_id=None, permission=None):
        self.repository_id = repository_id
        self.schema_id = schema_id
        self.group_id = group_id
        self.user_id = user_id
        if permission:
            if dict(permission) is dict:
                self.permission = _Permission(permission)
            else:
                self.permission = permission

    def to_dict(self):
        res = super(Permission, self).to_dict()
        if self.permission:
            res['permission'] = [p.to_dict() for p in self.permission]
        return res


Blob = namedtuple('Blob', ['filename', 'content'])
BlobDetail = namedtuple('BlobDetail', ['bytes', 'blob_id', 'sha1', 'document_id', 'md5'])
