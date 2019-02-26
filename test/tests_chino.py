import time

from . import cfg
from chino.api import ChinoAPIClient
from chino.exceptions import CallError
from chino.objects import _DictContent, _Field

__author__ = 'Stefano Tranquillini <stefano@chino.io>'

import unittest
import logging
import logging.config
import hashlib
from os import path
import os

# logging.config.fileConfig(path.join(path.dirname(__file__), 'logging.conf'))


class BaseChinoTest(unittest.TestCase):
    def setUp(self):
        self.chino = ChinoAPIClient(customer_id=cfg.customer_id, customer_key=cfg.customer_key,
                                    url=cfg.url, client_id=cfg.client_id, client_secret=cfg.client_secret, timeout=3600)
        self.logger = logging.getLogger('test.api')
        self.logger.debug("log")

    def _equals(self, i_d1, i_d2):
        """
        checks if d1 is equal of d2
        """
        if type(i_d1) is not dict:
            d1 = i_d1.to_dict()
        else:
            d1 = i_d1
        if type(i_d2) is not dict:
            d2 = i_d2.to_dict()
        else:
            d2 = i_d2
        for key, value in d1.items():
            if not key in d2:
                self.logger.error("ERROR: Key missing  %s" % key)
                return False
            v2 = d2[key]
            if type(v2) is _DictContent and value:
                if not self._equals(value.to_dict(), v2.to_dict()):
                    return False
            else:
                if not v2 == value:
                    # last update is 99% of the time different, especially after an update
                    if key != 'last_update':
                        self.logger.error("Value error %s: %s %s " % (key, value, v2))
                        return False
        for key in d2.keys():
            if not key in d1:
                self.logger.error("ERROR: Key missing  %s" % key)
                return False
        return True

    def _has_keys(self, keys, d):
        """
        checks if the dictionary has the keys
        """
        for key in keys:
            if not key in d:
                # self.logger.debug("Key missing  %s: %s" % (key, d))
                self.logger.error("ERROR: Key is missing %s" % key)
                return False
        for key in d.keys():
            if not key in keys:
                self.logger.error("ERROR: Dictionary has an extra key %s" % key)
                return False

        return True


class UserChinoTest(BaseChinoTest):
    user = None

    def setUp(self):
        super(UserChinoTest, self).setUp()
        fields = [dict(name='first_name', type='string'), dict(name='last_name', type='string'),
                  dict(name='email', type='string')]
        self.us = self.chino.user_schemas.create('test', fields)
        self.app_list = []

    def tearDown(self):
        # if user has been created we remove it.
        self.logger.debug("tearing down %s", self.user)
        self.chino.auth.set_auth_admin()
        list = self.chino.users.list(self.us._id)
        for user in list.users:
            self.chino.users.delete(user._id, force=True)
        self.chino.user_schemas.delete(self.us._id, force=True)
        if hasattr(self, 'app'):
            self.chino.applications.delete(self.app._id)

        # delete also every Application which was created forthis test
        for app in self.chino.applications.list().to_dict()['applications']:
            self.chino.applications.delete(app['app_id'], force=True)

    def test_list(self):
        list = self.chino.users.list(self.us._id)
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.users)

    def test_CRUD(self):
        NAME = 'test.user.new'
        EDIT = NAME + '.edited'
        user = self.chino.users.create(self.us._id, username=NAME, password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        self.user = user
        self.assertIsNotNone(user)
        self.assertEqual(user.username, NAME)
        list = self.chino.users.list(self.us._id)
        # NOTE: this may fail if key are used by someone else.
        ste_2 = self.chino.users.detail(list.users[0]._id)
        self.assertEqual(ste_2.username, NAME)

        user.username = EDIT
        # remove extra params
        data = user.to_dict()
        del data['insert_date']
        del data['last_update']
        del data['groups']
        del data['schema_id']
        ste_2 = self.chino.users.update(**data)
        self.logger.debug(ste_2)
        self.assertEqual(user._id, ste_2._id)
        self.assertEqual(ste_2.username, EDIT)

        ste_2 = self.chino.users.detail(user._id)
        self.assertEqual(ste_2.username, EDIT)

        # partial update
        ste_3 = self.chino.users.partial_update(user._id, **dict(attributes=dict(first_name=EDIT)))
        self.assertEqual(user._id, ste_3._id)
        self.assertEqual(ste_3.attributes.first_name, EDIT)
        ste_4 = self.chino.users.detail(user._id)
        self.assertEqual(ste_4.attributes.first_name, EDIT)
        # current not working for main user
        self.assertRaises(CallError, self.chino.users.current)

        # this invalidates the user
        self.chino.users.delete(user._id)

    # @unittest.skip("method disabled locally")
    def test_auth(self):
        # login
        NAME = 'test.user.new'
        EDIT = NAME + '.edited'
        self.app = self.chino.applications.create("test", grant_type='password')
        self.chino_user = ChinoAPIClient(customer_id=cfg.customer_id, customer_key=cfg.customer_key,
                                         url=cfg.url, client_id=self.app.app_id, client_secret=self.app.app_secret)
        user = self.chino.users.create(self.us._id, username=EDIT, password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        self.chino_user.users.login(EDIT, '12345678')
        ste_2 = self.chino_user.users.current()
        self.assertEqual(ste_2.username, EDIT)

        self.chino_user.users.refresh()
        # it should be impossible to create the user after login with self.chino_user (no admin access)
        self.assertRaises(CallError, self.chino_user.users.create, self.us._id, username='error', password='12345678',
                          attributes=dict(first_name='john', last_name='doe',
                                          email='test@chino.io'))

        self.chino_user.users.logout()
        self.assertRaises(Exception, self.chino_user.users.login, EDIT, '')

        self.assertRaises(CallError, self.chino.users.current)

    def test_auth_public(self):
        # login
        NAME = 'test.user.new'
        EDIT = NAME + '.edited'
        self.app = self.chino.applications.create("test", grant_type='password', client_type='public')
        # Init 'public' client
        self.chino_user = ChinoAPIClient(customer_id=cfg.customer_id,
                                            url=cfg.url,
                                            client_id=self.app.app_id,
                                            client_secret=None
                                        )
        self.assertIsNone(self.chino_user.auth.client_secret)

        user = self.chino.users.create(self.us._id, username=EDIT, password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))

        self.chino_user.users.login(EDIT, '12345678')
        ste_2 = self.chino_user.users.current()
        self.assertEqual(ste_2.username, EDIT)

        self.chino_user.users.refresh()
        # it should be impossible to create the user after login with self.chino_user (no admin access)
        self.assertRaises(CallError, self.chino_user.users.create, self.us._id, username='error', password='12345678',
                          attributes=dict(first_name='john', last_name='doe',
                                          email='test@chino.io'))

        self.chino_user.users.logout()
        self.assertRaises(Exception, self.chino_user.users.login, EDIT, '')

        self.assertRaises(CallError, self.chino.users.current)


# @unittest.skip("Class disabled locally")
class ApplicationsChinoTest(BaseChinoTest):
    user = None

    def setUp(self):
        super(ApplicationsChinoTest, self).setUp()

    def tearDown(self):
        # if user has been created we remove it.
        self.logger.debug("tearing down %s", self.user)

    def test_CRUD(self):
        app = self.chino.applications.create(name='tesssst_confidential', grant_type='password')
        app_public = self.chino.applications.create(name='test_public', grant_type='password', client_type='public')

        app_public1 = self.chino.applications.detail(app_public._id)
        self.assertEqual(app_public._id, app_public1._id)
        self.assertEqual(app_public.app_name, app_public1.app_name)

        newname = 'test_confidential'
        self.chino.applications.update(app._id, name=newname)
        app1 = self.chino.applications.detail(app._id)
        self.assertEqual(app1.app_name, newname)

        apps = self.chino.applications.list()
        self.chino.applications.delete(app_public1._id, force=True)
        self.chino.applications.delete(app1._id, force=True)


# @unittest.skip("Class disabled locally")
class GroupChinoTest(BaseChinoTest):
    def tearDown(self):
        list = self.chino.groups.list()
        for group in list.groups:
            self.chino.groups.delete(group._id, force=True)

        list = self.chino.user_schemas.list()
        for repo in list.user_schemas:
            self.chino.user_schemas.delete(repo._id, force=True)

    def test_list(self):
        list = self.chino.groups.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.groups)

    def test_CRUD(self):
        group_created = self.chino.groups.create('testing', attributes=dict(hospital='test'))
        self.assertTrue(self._equals(group_created.attributes.to_dict(), dict(hospital='test')))
        self.assertEqual(group_created.group_name, 'testing')
        # NOTE: this may fail
        list = self.chino.groups.list()
        group = list.groups[0]
        details = self.chino.groups.detail(group._id)
        # print group.to_dict()
        # print details.to_dict()
        self.assertTrue(self._equals(details, group), "\n %s \n %s \n" % (details.to_json(), group.to_json()))
        group.group_name = 'updatedtesting'
        # remove extra params
        data = group.to_dict()
        del data['insert_date']
        del data['last_update']
        self.chino.groups.update(**data)
        details = self.chino.groups.detail(group._id)
        self.assertTrue(self._equals(details, group), "\n %s \n %s \n" % (details.to_json(), group.to_json()))
        self.chino.groups.delete(details._id)

    def test_group_user(self):
        group_created = self.chino.groups.create('testing', attributes=dict(hospital='test'))
        fields = [dict(name='first_name', type='string'), dict(name='last_name', type='string'),
                  dict(name='email', type='string')]
        us = self.chino.user_schemas.create('test', fields)

        user = self.chino.users.create(us._id, username="ste", password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        self.user =user
        # if nothing is raised, then fine
        add = self.chino.groups.add_user(group_created._id, user._id)
        users = self.chino.groups.list_users(group_created._id)
        self.assertEqual(users.paging.count, 1)
        users = self.chino.groups.list_users(group_created._id, offset=2 )
        self.assertEqual(users.paging.count, 0)
        rem = self.chino.groups.del_user(group_created._id, user._id)
        # delete the user at the end
        self.chino.groups.delete(group_created._id, force=True)
        self.chino.users.delete(user._id, force=True)


class RepositoryChinoTest(BaseChinoTest):
    def setUp(self):
        super(RepositoryChinoTest, self).setUp()
        list = self.chino.repositories.list()
        for repo in list.repositories:
            self.chino.repositories.delete(repo._id, force=True, all_content=True)

    def tearDown(self):
        list = self.chino.repositories.list()
        for repo in list.repositories:
            self.chino.repositories.delete(repo._id, force=True, all_content=True)

    def test_list(self):
        list = self.chino.repositories.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.repositories)

    def test_crud(self):
        created = self.chino.repositories.create('test')
        self.assertEqual(created.description, 'test')
        first = self.chino.repositories.list().repositories[0]
        self.assertTrue(
            self._equals(created.to_dict(), first.to_dict()),
            "\n %s \n %s \n" % (created.to_json(), first.to_json()))
        first.description = 'edited'

        resp = self.chino.repositories.update(first._id, description=first.description)
        detail = self.chino.repositories.detail(first._id)
        self.assertTrue(
            self._equals(resp.to_dict(), detail.to_dict()), "\n %s \n %s \n" % (resp.to_json(), detail.to_json()))

        self.chino.repositories.delete(first._id)


class SchemaChinoTest(BaseChinoTest):
    def setUp(self):
        super(SchemaChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test')._id

    def tearDown(self):
        list = self.chino.schemas.list(self.repo)
        for repo in list.schemas:
            self.chino.schemas.delete(repo._id, force=True)
        self.chino.repositories.delete(self.repo, True)

    def test_list(self):
        list = self.chino.schemas.list(self.repo)
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.schemas)

    def test_crud(self):
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        created = self.chino.schemas.create(self.repo, 'test', fields)
        list = self.chino.schemas.list(self.repo)
        detail = self.chino.schemas.detail(list.schemas[0]._id)
        detail2 = self.chino.schemas.detail(created._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))

        detail.structure.fields.append(_Field('string', 'new one'))
        data = detail.to_dict()
        del data['repository_id']
        del data['insert_date']
        del data['last_update']
        self.chino.schemas.update(**data)
        detail2 = self.chino.schemas.detail(detail._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.schemas.delete(detail._id)


class UserSchemaChinoTest(BaseChinoTest):
    def setUp(self):
        super(UserSchemaChinoTest, self).setUp()

    def tearDown(self):
        list = self.chino.user_schemas.list()
        for repo in list.user_schemas:
            self.chino.user_schemas.delete(repo._id, force=True)

    def test_list(self):
        list = self.chino.user_schemas.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.user_schemas)

    def test_crud(self):
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        created = self.chino.user_schemas.create('test', fields)
        list = self.chino.user_schemas.list()
        self.assertGreater(list.paging.count, 0)
        id = 0
        for schema in list.user_schemas:
            if schema._id == created._id:
                id = schema._id
        detail = self.chino.user_schemas.detail(id)
        detail2 = self.chino.user_schemas.detail(created._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))

        detail.structure.fields.append(_Field('string', 'new one'))
        data = detail.to_dict()
        del data['insert_date']
        del data['last_update']
        del data['user_schema_id']
        del data['groups']
        self.chino.user_schemas.update(detail.user_schema_id, **data)
        detail2 = self.chino.user_schemas.detail(detail._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.user_schemas.delete(detail._id, force=True)


class CollectionChinoTest(BaseChinoTest):
    def setUp(self):
        super(CollectionChinoTest, self).setUp()

    def tearDown(self):
        list = self.chino.collections.list()
        for coll in list.collections:
            self.chino.collections.delete(coll._id, force=True)

    def test_list(self):
        list = self.chino.user_schemas.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.user_schemas)

    def test_crud(self):
        created = self.chino.collections.create("test_")
        list = self.chino.collections.list()
        detail = self.chino.collections.detail(list.collections[0]._id)
        detail2 = self.chino.collections.detail(created._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.collections.update(detail._id, name='test2')
        detail2 = self.chino.collections.detail(detail._id)
        self.assertTrue(detail2.name == 'test2')
        self.chino.collections.delete(detail._id)

    def test_search(self):
        ids = []
        for i in range(10):
            created = self.chino.collections.create("test" + str(i))
            ids.append(created._id)

        res = self.chino.collections.search('test', contains=True)
        self.assertEqual(res.paging.total_count, 10)
        res = self.chino.collections.search('test2', contains=False)
        for collection in res.collections:
            self.assertTrue(collection.name.startswith('test'))
        self.assertEqual(res.paging.total_count, 1)
        self.assertEqual(res.collections[0].name, 'test2')
        for id in ids:
            self.chino.collections.delete(id, True)

    def test_docs(self):
        repo = self.chino.repositories.create('test')._id
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        schema = self.chino.schemas.create(repo, 'test', fields)._id
        content = dict(fieldInt=123, fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        document = self.chino.documents.create(schema, content=content)
        collection = self.chino.collections.create("test")
        l = self.chino.collections.list_documents(collection._id)
        self.assertEqual(l.paging.count, 0)
        self.chino.collections.add_document(collection._id, document._id)
        l = self.chino.collections.list_documents(collection._id)
        self.assertEqual(l.paging.count, 1)
        self._equals(l.documents[0].to_dict(), document.to_dict())
        self.chino.collections.rm_document(collection._id, document._id)
        l = self.chino.collections.list_documents(collection._id)
        self.assertEqual(l.paging.count, 0)

        # delete
        self.chino.documents.delete(document._id, force=True)
        self.chino.schemas.delete(schema, force=True)
        self.chino.repositories.delete(repo, force=True)
        self.chino.collections.delete(collection._id, force=True)


@unittest.skip("Test to be updated")
class PermissionChinoTest2(BaseChinoTest):
    def setUp(self):
        super(PermissionChinoTest2, self).setUp()
        # list = self.chino.users.list()
        # for u in list.users:
        # self.chino.users.delete(u._id,force=True)

    def test_premissions(self):
        # create user via userschema
        repo = self.chino.repositories.create('test')._id
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        schema = self.chino.schemas.create(repo, 'test', fields)._id
        # schema = "c0d0d956-8cd1-405b-90a9-62d3b3f70e84"
        content = dict(fieldInt=123, fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        document = self.chino.documents.create(schema, content=content)
        fields = [dict(name='first_name', type='string'), dict(name='last_name', type='string'),
                  dict(name='email', type='string')]
        us = self.chino.user_schemas.create('test', fields)
        username = 'test_%s' % round(time.time())
        user = self.chino.users.create(us._id, username=username, password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        self.chino.permissions.resources('grant', 'repositories', 'users', user._id, manage=['R'])
        self.chino.users.login(username, '12345678')
        permissions = self.chino.permissions.read_perms()
        self.assertTrue(permissions[0].permission.manage == ['R'])
        self.chino.users.logout()
        self.chino.auth.set_auth_admin()
        self.chino.permissions.resource('grant', 'documents', document._id, 'users', user._id, manage=['R', 'U'])
        self.chino.users.login(username, '12345678')
        permissions = self.chino.permissions.read_perms_document(document._id)
        self.assertTrue(permissions[0].permission.manage == ['R', 'U'])
        self.chino.users.logout()
        self.chino.auth.set_auth_admin()
        self.chino.permissions.resource_children('grant', 'schemas', schema, 'documents', 'users', user._id,
                                                 manage=['R', 'U', 'L'], authorize=['A'])
        self.chino.users.login(username, '12345678')
        permissions = self.chino.permissions.read_perms()
        # 0 is the one above
        self.assertTrue(permissions[1].permission.manage == ['R', 'U', 'L'])
        self.assertTrue(permissions[1].permission.authorize == ['A'])

        permissions = self.chino.permissions.read_perms_user(user._id)
        self.assertTrue(permissions[0].permission.manage == ['R'])
        self.assertTrue(permissions[1].permission.manage == ['R', 'U', 'L'])
        self.assertTrue(permissions[1].permission.authorize == ['A'])
        self.chino.users.logout()
        self.chino.auth.set_auth_admin()
        self.chino.documents.delete(document._id, force=True)
        self.chino.schemas.delete(schema, force=True)
        self.chino.repositories.delete(repo, force=True)
        self.chino.users.delete(user._id, force=True)
        self.chino.user_schemas.delete(us._id, force=True)


class DocumentChinoTest(BaseChinoTest):
    def setUp(self):
        super(DocumentChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test')._id
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        self.schema = self.chino.schemas.create(self.repo, 'test', fields)._id
        fields = [dict(name='fieldString', type='text')]
        self.schema_1 = self.chino.schemas.create(self.repo, 'test', fields)._id

    def tearDown(self):
        list = self.chino.documents.list(self.schema)
        for doc in list.documents:
            self.chino.documents.delete(doc._id, force=True)
        self.chino.schemas.delete(self.schema, True)
        self.chino.repositories.delete(self.repo, force=True, all_content=True)

    def test_list(self):
        content = dict(fieldInt=123, fieldString='test', fieldBool=False,
                       fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        document = self.chino.documents.create(self.schema, content=content)
        list = self.chino.documents.list(self.schema)
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.documents)
        self.assertIsNone(list.documents[0].content)
        list = self.chino.documents.list(self.schema, True)
        self.assertIsNotNone(list.documents[0].content)
        self.chino.documents.delete(document._id, True)

    # @unittest.skip("not working, timeout`")
    def test_too_big(self):
        k_bit = 'YXNkc2FkamtzZGprYWhqa3NkaGFqa3NoZGpzYWhkamtzYWhkamtoc2Fqa2xoamRrc2ZsaGpka2xzaGZhamtkbHNoamFrZmxoZGp' \
                'za2xhaGZqZGtsc2hqZmtsYWhqZmtkbGhzYWpma2xkaHNqa2xhaGZqZGtsc2hhamZrbGFoamtkc2xoamZrZGxzaGpma2xkc2hham' \
                'tmbGRoc2pha2xmaGpka2xzaGpma2FzZGRqc2FpbyBkanNpYW9qZGlzYWpkaW9zYWpkaW9zYWppZG9qc2Fpb2RqaXNhb2pkaXNvY' \
                'WpkaW9zamFpZG9qc2Fpb2RqaXcxMDkzMDgyMTkwOGRtMXdpMDltZGk5MDFtaTlkMG13MWk5MGRtaXc5MTBtaWQ5dzBtaGRzamFr' \
                'aGRqa3NoYWRqbGFoZnNqa2xkaHNhamZrbGRoc2pha2xoZmpkc2tsYWhmamRrc2xoZmllYXVoZmlvZWgyYXVpb2ZoZXVpb3BxamV' \
                'pb3dlangsYXNhZHNhc2RzYWRqa3NkamthaGprc2RoYWprc2hkanNhaGRqa3NhaGRqa2hzYWprbGhqZGtzZmxoamRrbHNoZmFqa2' \
                'Rsc2hqYWtmbGhkanNrbGFoZmpka2xzaGpma2xhaGpma2RsaHNhamZrbGRoc2prbGFoZmpka2xzaGFqZmtsYWhqa2RzbGhqZmtkb' \
                'HNoamZrbGRzaGFqa2ZsZGhzamFrbGZoamRrbHNoamZrYXNkZGpzYWlvIGRqc2lhb2pkaXNhamRpb3NhamRpb3Nhamlkb2pzYWlv' \
                'ZGppc2FvamRpc29hamRpb3NqYWlkb2pzYWlvZGppdzEwOTMwODIxOTA4ZG0xd2kwOW1kaTkwMW1pOWQwbXcxaTkwZG1pdzkxMG1' \
                'pZDl3MG1oZHNqYWtoZGprc2hhZGpsYWhmc2prbGRoc2FqZmtsZGhzamFrbGhmamRza2xhaGZqZGtzbGhmaWVhdWhmaW9laDJhdW' \
                'lvZmhldWlvcHFqZWlvd2VqeCxhc2Fkc2FzZHNhZGprc2Rqa2FoamtzZGhhamtzaGRqc2FoZGprc2FoZGpraHNhamtsaGpka3Nmb' \
                'GhqZGtsc2hmYWprZGxzaGpha2ZsaGRqc2tsYWhmamRrbHNoamZrbGFoamZrZGxoc2FqZmtsZGhzamtsYWhmamRrbHNoYWpma2xh' \
                'aGprZHNsaGpma2Rsc2hqZmtsZHNoYWprZmxkaHNqYWtsZmhqZGtsc2hqZmthc2RkanNhaW8gZGpzaWFvamRpc2FqZGlvc2FqZGl' \
                'vc2FqaWRvanNhaW9kamlzYW9qZGlzb2FqZGlvc2phaWRvanNhaW9kaml3MTA5MzA4MjE5MDhkbTF3aTA5bWRpOTAxbWk5ZDBtdz' \
                'FpOTBkbWl3OTEwbWlkOXcwbWhkc2pha2hkamtzaGFkamxhaGZzamtsZGhzYWpma2xkaHNqYWtsaGZqZHNrbGFoZmpka3NsaGZpZ' \
                'WF1aGZpb2VoMmF1aW9maGV1aW9wcWplaW93ZWp4LGFzYWRzYXNkc2FkamtzZGprYWhqa3NkaGFqa3NoZGpzYWhkamtzYWhkamto' \
                'c2Fqa2xoamRrc2ZsaGpka2xzaGZhamtkbHNoamFrZmxoZGpza2xhaGZqZGtsc2hqZmtsYWhqZmtkbGhzYWpma2xkaHNqa2xhaGZ' \
                'qZGtsc2hhamZrbGFoamtkc2xoamZrZGxzaGpma2xkc2hhamtmbGRoc2pha2xmaGpka2xzaGpma2FzZGRqc2FpbyBkanNpYW9qZG' \
                'lzYWpkaW9zYWpkaW9zYWppZG9qc2Fpb2RqaXNhb2pkaXNvYWpkaW9zamFpZG9qc2Fpb2RqaXcxMDkzMDgyMTkwOGRtMXdpMDltZ' \
                'Gk5MDFtaTlkMG13MWk5MGRtaXc5MTBtaWQ5dzBtaGRzamFraGRqa3NoYWRqbGFoZnNqa2xkaHNhamZrbGRoc2pha2xoZmpkc2ts' \
                'YWhmamRrc2xoZmllYXVoZmlvZWgyYXVpb2ZoZXVpb3BxamVpb3dlangsYXNhZHNkc2Fh'
        n = 10  # number of MB
        k = 0
        dat = ""
        self.chino.documents.create(self.schema_1, content=dict(fieldString=dat))
        while k < n * 512:
            dat += "%s" % k_bit
            k += 1
        #
        with self.assertRaises(CallError):  # must fail because is too big
            self.chino.documents.create(self.schema_1, content=dict(fieldString=dat))

    def test_crud(self):
        content = dict(fieldInt=123, fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        document = self.chino.documents.create(self.schema, content=content)
        # get the last
        document_det = self.chino.documents.detail(document._id)
        self.assertEqual(document.last_update, document_det.last_update)
        content = dict(fieldInt=123,
                       fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        self.chino.documents.update(document._id, content=content)
        document = self.chino.documents.detail(document._id)
        self.assertEqual(123, document.content.fieldInt)
        self.chino.documents.update(document._id,
                                    content=dict(fieldInt=349, fieldString='test', fieldBool=False,
                                                 fieldDate='2015-02-19',
                                                 fieldDateTime='2015-02-19T16:39:47'))
        document = self.chino.documents.detail(document._id)
        self.assertEqual(349, document.content.fieldInt)
        self.chino.documents.delete(document._id)

        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        created = self.chino.schemas.create(self.repo, 'test', fields)
        list = self.chino.schemas.list(self.repo)
        s_id = 0
        for schema in list.schemas:
            if schema._id == created._id:
                s_id = schema._id
        detail = self.chino.schemas.detail(s_id)
        detail2 = self.chino.schemas.detail(created._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))

        detail.structure.fields.append(_Field('string', 'new one'))
        # delete repository_id
        data = detail.to_dict()
        del data['repository_id']
        del data['insert_date']
        del data['last_update']
        self.chino.schemas.update(**data)
        detail2 = self.chino.schemas.detail(detail._id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()),
            "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.schemas.delete(detail._id, force=True)


class BlobChinoTest(BaseChinoTest):
    def setUp(self):
        super(BlobChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test')._id
        fields = [dict(name='blobTest', type='blob'), dict(name='name', type='string')]
        self.schema = self.chino.schemas.create(self.repo, 'test', fields)._id

    def tearDown(self):
        if hasattr(self, 'blob'):
            self.chino.blobs.delete(self.blob.blob_id)
        self.chino.documents.delete(self.document._id, True)
        self.chino.schemas.delete(self.schema, True)
        self.chino.repositories.delete(self.repo, True)

    # @unittest.skip("not working on prod")
    def test_blob(self):
        self.document = self.chino.documents.create(self.schema, content=dict(name='test'))
        src = os.path.join(os.path.sep, os.path.dirname(__file__), 'logo.png')
        blob = self.chino.blobs.send(self.document._id, 'blobTest', str(src), chunk_size=32*1024)
        blob_detail = self.chino.blobs.detail(blob.blob_id)
        rw = open("out" + blob_detail.filename, "wb")
        rw.write(blob_detail.content)
        rw.close()
        # rd = open('test/logo.png', "rb")
        md5_detail = hashlib.md5()
        md5_detail.update(blob_detail.content)
        # self.assertEqual(md5_detail.digest(), md5_original.digest())
        self.assertEqual(md5_detail.hexdigest(), blob.md5)
        self.blob = blob
        self.chino.blobs.delete(self.blob.blob_id)
        src = os.path.join(os.path.sep, os.path.dirname(__file__), 'test.sh')
        blob = self.chino.blobs.send(self.document._id, 'blobTest', str(src), chunk_size=32*1024)

        blob_detail = self.chino.blobs.detail(blob.blob_id)
        rw = open("out" + blob_detail.filename, "wb")
        rw.write(blob_detail.content)
        rw.close()
        # rd = open('test/logo.png', "rb")
        md5_detail = hashlib.md5()
        md5_detail.update(blob_detail.content)
        # self.assertEqual(md5_detail.digest(), md5_original.digest())
        self.assertEqual(md5_detail.hexdigest(), blob.md5)
        self.blob = blob

    @unittest.skip("Skipping for size")
    def test_large_blob(self):
        self.document = self.chino.documents.create(self.schema, content=dict(name='test'))
        import random
        blob = self.chino.blobs.send(self.document._id, 'blobTest', 'dummy.file',
                                     chunk_size=random.choice([1, 10]) * 1024 * 1024)
        blob_detail = self.chino.blobs.detail(blob.blob_id)
        rw = open("out" + blob_detail.filename, "wb")
        rw.write(blob_detail.content)
        rw.close()
        # rd = open('test/logo.png', "rb")
        md5_detail = hashlib.md5()
        md5_detail.update(blob_detail.content)
        sha1_detail = hashlib.sha1()
        sha1_detail.update(blob_detail.content)
        # self.assertEqual(md5_detail.digest(), md5_original.digest())
        self.assertEqual(md5_detail.hexdigest(), blob.md5)
        self.assertEqual(sha1_detail.hexdigest(), blob.sha1)
        # self.blob = blob


# @unittest.skip("not working on prod`")
class SearchDocsChinoTest(BaseChinoTest):
    def setUp(self):
        super(SearchDocsChinoTest, self).setUp()
        fields = [dict(name='fieldInt', type='integer', indexed=True),
                  dict(name='fieldString', type='string', indexed=True),
                  dict(name='fieldBool', type='boolean', indexed=True),
                  dict(name='fieldDate', type='date', indexed=True),
                  dict(name='fieldDateTime', type='datetime', indexed=True)]
        self.repo = self.chino.repositories.create('test')._id
        self.schema = self.chino.schemas.create(self.repo, 'test', fields)._id

    # def tearDown(self):
    #     documents = self.chino.documents.list(self.schema)
    #     for document in documents.documents:
    #         self.chino.documents.delete(document._id, force=True)
    #     self.chino.schemas.delete(self.schema, True)
    #     self.chino.repositories.delete(self.repo, True)

    def test_search_docs(self):
        tot=9
        print(self.schema)
        for i in range(tot):
            res=self.chino.documents.create(self.schema, content=dict(fieldInt=123, fieldString='test', fieldBool=False,
                                                              fieldDate='2015-02-19',
                                                              fieldDateTime='2015-02-19T16:39:47'),consistent=True)
        last_doc = self.chino.documents.create(self.schema,
                                               content=dict(fieldInt=123, fieldString='test', fieldBool=False,
                                                            fieldDate='2015-02-19',
                                                            fieldDateTime='2015-02-19T16:39:47'),consistent=True)

        # self.chino.searches.search(self.schema) # TODO: improve tests
        time.sleep(5)  # wait the index max update time
        res = self.chino.searches.documents(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
        self.assertEqual(res.paging.total_count, 10, res)
        self.chino.documents.delete(last_doc.document_id, force=True)
        time.sleep(5)
        res = self.chino.searches.documents(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
        self.assertEqual(res.paging.total_count, 9, res)
        res = self.chino.searches.documents_complex(self.schema, query={"field": "fieldInt", "type": "eq", "value": 123})
        self.assertEqual(res.paging.total_count, 9, res)
        # print res.documents
        ids = []
        for d in res.documents[:3]:
            ids.append(d._id)
        res = self.chino.searches.documents(self.schema, filters=[{"field": "_id", "type": "in", "value": ids}])
        self.assertEqual(res.paging.total_count, 3, res)

    def test_search_docs_consistent(self):
        doc = None
        max = 4
        for i in range(max):
            doc = self.chino.documents.create(self.schema, content=dict(fieldInt=i, fieldString='test', fieldBool=False,
                                                                        fieldDate='2015-02-19',
                                                                        fieldDateTime='2015-02-19T16:39:47'),
                                              consistent=True)
        time.sleep(2)
        res = self.chino.searches.documents(self.schema,
                                            filters=[{"field": "fieldInt", "type": "eq", "value": i}])
        self.assertEqual(res.paging.total_count, 1, res)
        res = self.chino.searches.documents(self.schema,
                                            filters=[{"field": "fieldInt", "type": "eq", "value": max - 1}])
        self.assertEqual(res.paging.total_count, 1, res)
        self.chino.documents.delete(doc._id, consistent=True, force=True)
        res = self.chino.searches.documents(self.schema,
                                            filters=[{"field": "fieldInt", "type": "eq", "value": max - 1}])
        self.assertEqual(res.paging.total_count, 0, res)

    def test_search_docs_complex(self):
        doc = None
        max = 4
        for i in range(max):
            doc_content = dict(fieldInt=i, fieldString='test', fieldBool=False,
                             fieldDate='2018-12-19',fieldDateTime='2018-12-19T16:39:47')
            doc = self.chino.documents.create(
                self.schema,
                content=doc_content,
                consistent=True
            )
            res = self.chino.searches.documents_complex(self.schema, result_type="ONLY_ID",
                        query={
                            "and": [{"field": key, "type": "eq", "value": doc_content[key]} for key in doc_content.keys()]
                                   + [
                                       {"field": "_id", "type": "eq", "value": doc.document_id}
                                   ]
                        }
                    )
            self.assertEquals(
                doc.document_id, str(res.IDs[0])
            )

        self.assertEquals(
            0,
            len(
                self.chino.searches.documents_complex(self.schema, result_type="NO_CONTENT",
                    query={
                        "or": [
                            {"field": "fieldInt", "type": "eq", "value": max + 1},
                            {"not": [
                                {"field": "fieldInt", "type": "lte", "value": max}
                            ]}
                        ]
                    }
                ).documents
            )
        )

        count_docs = self.chino.searches.documents_complex(self.schema, result_type="COUNT",
            query={"field": "fieldDate", "type": "gte", "value": '2018-12-19'}
        )
        self.assertEqual(max, count_docs)

        all_ids = self.chino.searches.documents_complex(self.schema, result_type="ONLY_ID",
            query={"field": "fieldDate", "type": "gte", "value": '2018-12-19'}
        )
        self.assertIn(doc.document_id, [str(_id['id']) for _id in all_ids.to_dict()["IDs"]])

        self.assertEquals(
            doc.document_id,    # last created document
            self.chino.searches.documents_complex(self.schema,
                sort=[dict(field="fieldInt", order="desc")],
                query={"field": "fieldDate", "type": "gte", "value": '2018-12-19'},
                limit=1
            ).documents[0].document_id
        )


class SearchUsersChinoTest(BaseChinoTest):
    def setUp(self):
        super(SearchUsersChinoTest, self).setUp()
        fields = [dict(name='fieldInt', type='integer', indexed=True),
                  dict(name='fieldString', type='string', indexed=True),
                  dict(name='fieldBool', type='boolean', indexed=True),
                  dict(name='fieldDate', type='date', indexed=True),
                  dict(name='fieldDateTime', type='datetime', indexed=True)]
        self.schema = self.chino.user_schemas.create('test', fields)._id

    def tearDown(self):
        users = self.chino.users.list(self.schema)
        for user in users.users:
            self.chino.users.delete(user._id, force=True)
        self.chino.user_schemas.delete(self.schema, True)

    def test_search_users(self):
        for i in range(9):
            self.chino.users.create(self.schema, username="user_test_%s" % i, password='1234567890AAaa',
                                    attributes=dict(fieldInt=123, fieldString='test', fieldBool=False,
                                                    fieldDate='2015-02-19',
                                                    fieldDateTime='2015-02-19T16:39:47'))
            time.sleep(3)

        last_doc = self.chino.users.create(self.schema, username="user_test_last", password='1234567890AAaa',
                                           attributes=dict(fieldInt=123, fieldString='test', fieldBool=False,
                                                           fieldDate='2015-02-19',
                                                           fieldDateTime='2015-02-19T16:39:47'))

        # self.chino.searches.search(self.schema) # TODO: improve tests
        time.sleep(15)  # wait twice the index max update time

        res = self.chino.searches.users(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
        self.assertEqual(res.paging.total_count, 10, res)
        res = self.chino.searches.users(self.schema,
                                        filters=[{"field": "username", "type": "eq", "value": 'user_test_last'}])
        self.assertEqual(res.paging.total_count, 1, res)
        res = self.chino.searches.users(self.schema, filters=[{"field": "username", "type": "eq", "value": 'user_test_last'}],result_type="EXISTS")
        self.assertEqual(res, True, res)
        res = self.chino.searches.users(self.schema, filters=[{"field": "username", "type": "eq", "value": 'user_test_last'}],result_type="USERNAME_EXISTS")
        self.assertEqual(res, True, res)
        self.chino.users.delete(last_doc.user_id, force=True)
        time.sleep(5)
        res = self.chino.searches.users(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
        self.assertEqual(res.paging.total_count, 9, res)

        res = self.chino.searches.users_complex(self.schema, query={"field": "fieldInt", "type": "eq", "value": 123})
        self.assertEqual(res.paging.total_count, 9, res)

    def test_search_users_consistent(self):
        doc = None
        for i in range(4):
            doc = self.chino.users.create(self.schema, username="user_test_%s" % i, password='1234567890AAaa',
                                          attributes=dict(fieldInt=123, fieldString='test', fieldBool=False,
                                                          fieldDate='2015-02-19',
                                                          fieldDateTime='2015-02-19T16:39:47'), consistent=True)
        res = self.chino.searches.users(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
        self.assertEqual(res.paging.total_count, i + 1, res)

            # self.chino.users.delete(doc.user_id, force=True,consistent=True)
            # res = self.chino.searches.users(self.schema, filters=[{"field": "fieldInt", "type": "eq", "value": 123}])
            # self.assertEqual(res.paging.total_count, 9, res)

    def test_search_users_complex(self):
        usr = None
        max = 4
        for i in range(max):
            usr_attributes = dict(fieldInt=i, fieldString='test', fieldBool=False,
                               fieldDate='2018-12-19', fieldDateTime='2018-12-19T16:39:47')
            usr = self.chino.users.create(self.schema, username="user_test_%s" % i, password='1234567890AAaa',
                                          attributes=usr_attributes,
                                          consistent=True
            )
            self.assertTrue(
                self.chino.searches.users_complex(self.schema, result_type="EXISTS",
                    query={
                        "and": [{"field": key, "type": "eq", "value": usr_attributes[key]}
                                for key in usr_attributes.keys()]
                               + [
                                   {"field": "_id", "type": "eq",
                                    "value": usr.user_id}
                               ]
                    }
                )
            )
            self.assertTrue(
                self.chino.searches.users_complex(self.schema, result_type="USERNAME_EXISTS",
                    query={"field": "username", "type": "eq", "value": usr.username}
                )
            )

        self.assertFalse(
            self.chino.searches.users_complex(self.schema, result_type="EXISTS",
                query={
                    "or": [
                        {"field": "fieldInt", "type": "eq", "value": max + 1},
                        {"not": [
                            {"field": "fieldInt", "type": "lte", "value": max}
                        ]}
                    ]
                }
            )
        )

        count_docs = self.chino.searches.users_complex(self.schema, result_type="COUNT",
            query={"field": "fieldDate", "type": "gte", "value": '2018-12-19'}
        )
        self.assertEqual(max, count_docs)

        self.assertEquals(
            usr.user_id,    # last created user
            self.chino.searches.users_complex(self.schema,
                sort=[dict(field="fieldInt", order="desc")],
                query={"field": "fieldDate", "type": "gte", "value": '2018-12-19'},
                limit=1
            ).users[0].user_id
        )


class PermissionChinoTest(BaseChinoTest):
    def setUp(self):
        super(PermissionChinoTest, self).setUp()
        groups = self.chino.groups.list()
        for g in groups.groups:
            self.chino.groups.delete(g._id, True)
        u_schemas = self.chino.user_schemas.list()
        for us in u_schemas.user_schemas:
            li = self.chino.users.list(us._id)
            for user in li.users:
                self.chino.users.delete(user._id, force=True)
        fields = [dict(name='first_name', type='string'), dict(name='last_name', type='string'),
                  dict(name='email', type='string')]
        self.user_schema = self.chino.user_schemas.create('test', fields)._id
        self.password = '12345678'
        self.user0 = self.chino.users.create(user_schema_id=self.user_schema, username='test', password=self.password,
                                             attributes=dict(first_name='user_0', last_name='doe',
                                                             email='test@chino.io'))
        self.user1 = self.chino.users.create(user_schema_id=self.user_schema, username='test1', password=self.password,
                                             attributes=dict(first_name='user_1', last_name='doe',
                                                             email='test@chino.io'))

        self.group = self.chino.groups.create('testing', attributes=dict(hospital='test'))

        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        self.repo = self.chino.repositories.create('test')._id
        self.schema = self.chino.schemas.create(self.repo, 'test', fields)
        app = self.chino.applications.create("test", grant_type='password')
        self.chino_user0 = ChinoAPIClient(customer_id=cfg.customer_id, customer_key=cfg.customer_key,
                                          url=cfg.url, client_id=app.app_id, client_secret=app.app_secret)
        self.chino_user0.users.login(self.user0.username, self.password)
        self.chino_user1 = ChinoAPIClient(customer_id=cfg.customer_id, customer_key=cfg.customer_key,
                                          url=cfg.url, client_id=app.app_id, client_secret=app.app_secret)
        self.chino_user1.users.login(self.user1.username, self.password)

    def tearDown(self):
        u_schemas = self.chino.user_schemas.list()
        for us in u_schemas.user_schemas:
            li = self.chino.users.list(us._id)
            for user in li.users:
                self.chino.users.delete(user._id, force=True)
            self.chino.user_schemas.delete(us._id, True)
        groups = self.chino.groups.list()
        for g in groups.groups:
            self.chino.groups.delete(g._id, True)
        try:
            self.chino.schemas.delete(self.schema, True, all_content=True)
            self.chino.repositories.delete(self.repo, True, all_content=True)
        except CallError:
            pass

    def test_create_a_repository(self):
        with self.assertRaises(CallError):  # user has no create permission, expected an error.
            self.repository = self.chino_user0.repositories.create('test')
        self.chino.permissions.resources('grant', 'repositories', 'users', self.user0._id, manage=['C', 'R', 'U', 'L'],
                                         authorize=['A'])
        # now it has the permissions
        self.repository = self.chino_user0.repositories.create('test')
        # grant to user1 the permission of read all the repository but not to create
        self.chino.permissions.resources('grant', 'repositories', 'users', self.user1._id, manage=['R', 'U', 'L'])
        with self.assertRaises(CallError):  # must fail because user has no create permission
            self.chino_user1.repositories.create('test')
        li = self.chino_user1.repositories.list()
        for repo in li.repositories:
            self.chino_user1.repositories.detail(repo._id)
        with self.assertRaises(CallError):  # must fail because user has no "D" permission
            self.chino_user1.repositories.delete(self.repository._id)
        self.chino_user0.permissions.resource('grant', 'repositories', self.repository._id, 'users', self.user1._id,
                                              manage=['D'])
        with self.assertRaises(CallError):  # must fail because user is not authorized
            self.chino_user1.permissions.resource('grant', 'repositories', self.repository._id, 'users', self.user0._id,
                                                  manage=['D'])
        self.chino_user1.repositories.delete(self.repository._id)

    def test_create_documents(self):
        self.chino.permissions.resources('grant', 'repositories', 'users', self.user0._id, manage=['C'])
        self.repository = self.chino_user0.repositories.create('test')
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        self.schema = self.chino_user0.schemas.create(self.repository._id, 'test_schema', fields)._id
        content = dict(fieldInt=123, fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19T16:39:47')
        self.document = self.chino_user0.documents.create(self.schema, content=content)._id
        with self.assertRaises(CallError):  # must fail because user is not authorized
            self.chino_user1.documents.create(self.schema, content=content)._id
        with self.assertRaises(CallError):  # must fail because user is not authorized
            self.chino_user1.documents.list(self.schema)
        self.chino_user0.permissions.resource_children('grant', 'schemas', self.schema, 'documents', 'users',
                                                       self.user1._id, manage=['L'])
        self.assertEqual(self.chino_user1.documents.list(self.schema).paging.total_count, 0)
        self.assertEqual(self.chino_user0.documents.list(self.schema).paging.total_count, 1)

@unittest.skipIf(cfg.url.startswith('https://api.chino.io'),"not on production")
class ConsentChinoTest(BaseChinoTest):

    def setUp(self):
        super(ConsentChinoTest, self).setUp()
        self.details = {
            "description": "This policy was created for test purposes. The policy url is linked to Chino.io policy.",
            "policy_url": "https://www.chino.io/legal/privacy-policy",
            "policy_version": "test",
            "collection_mode": "none"
        }
        self.data_controller = {
          "company" : "Chino.io",
          "contact" : "controller",
          "address" : "Via S.G. Bosco 27, 38068 Rovereto",
          "email" : "controller@mail.tld",
          "VAT" : "n/d",
          "on_behalf" : True
        }
        self.purposes = [
          {
              "authorized": True,
              "purpose": "testing",
              "description" : "Testing class api.ChinoAPIConsents"
          },
          {
              "authorized": False,
              "purpose": "testing",
              "description" : "Testing class objects.Consent"
          }
        ]
        self.user_id = "user_id"
        self.user_id_alt = "another-user_id"
        # list of Consents for test_list and test_withdraw
        self.consent_ls = []
        self.consent_ls.append(self.chino.consents.create(self.user_id, self.details, self.data_controller, self.purposes))
        self.consent_ls.append(self.chino.consents.create(self.user_id_alt, self.details, self.data_controller, self.purposes))
        self.consent_ls.append(self.chino.consents.create(self.user_id, self.details, self.data_controller, self.purposes))


    def tearDown(self):
        ls = self.chino.consents.list()
        for c in ls.consents:
            if c.to_dict()['policy_version'] == 'test':
                self.chino.consents.delete(c._id)


    def test_list(self):
        ls = self.chino.consents.list()
        self.assertIsNotNone(ls.paging)
        self.assertIsNotNone(ls.consents)

        ls = self.chino.consents.list(self.user_id)
        for consent in ls.consents:
            self.assertEqual(consent.to_dict()['user_id'], self.user_id)


    def test_CRUD(self):
        USER_ID1 = "username@mail.tld"
        USER_ID2 = "another_username@mail.tld"
        # CREATE
        new = self.chino.consents.create(USER_ID1, self.details, self.data_controller, self.purposes)
        list = self.chino.consents.list()
        self.assertGreater(list.paging.count, 0)
        read_id = 0
        for consent in list.consents:
            if consent._id == new._id:
                read_id = consent._id
        self.assertFalse(read_id == 0)
        # READ
        read = self.chino.consents.detail(read_id)
        read_compare = self.chino.consents.detail(new._id)
        self.assertTrue(self._equals(new.to_dict(), read.to_dict()),
            msg="created:\n%s\n\nread:\n\n%s\n" % (new.to_json(), read.to_json())
        )
        # UPDATE
        updated = self.chino.consents.update(read._id, USER_ID2, self.details, self.data_controller, self.purposes)
        self.assertFalse(self._equals(new.to_dict(), updated.to_dict()),
            msg=("Update returned an unmodified object.\nid1: %s\nid2: %s" % (new._id, updated._id)))

        read = self.chino.consents.detail(read_id)
        self.assertTrue(self._equals(updated.to_dict(), read.to_dict()),
            msg="updated:\n%s\n\nread:\n\n%s\n" % (updated.to_json(), read.to_json())
        )
        history = self.chino.consents.history(read._id)
        self.assertGreater(len(history.consents), 1)
        # DELETE
        self.chino.consents.delete(read._id)
        for cid in [new._id, read._id, updated._id]:
            self.assertRaises(CallError,
                self.chino.consents.detail,
                {'consent_id':cid}
            )


    def test_withdraw(self):
        withdraw = self.chino.consents.list(user_id=self.user_id_alt).consents[0]
        self.chino.consents.withdraw(withdraw._id)

        read = self.chino.consents.detail(withdraw._id)
        self.assertIsNotNone(read.to_dict()['withdrawn_date'])



if __name__ == '__main__':
    unittest.main()
