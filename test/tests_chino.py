import cfg
from chino.api import ChinoAPIClient
from chino.exceptions import CallError
from chino.objects import _DictContent, _Field

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

import unittest
import logging
import logging.config
import hashlib


# logging.basicConfig(stream=sys.stderr)



class BaseChinoTest(unittest.TestCase):
    def setUp(self):
        self.chino = ChinoAPIClient(customer_id=cfg.customer_id, customer_key=cfg.customer_key)
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('chino')
        self.logger.setLevel(logging.DEBUG)

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
        for key, value in d1.iteritems():
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
        for key in d2.iterkeys():
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

    def tearDown(self):
        # if user has been created we remove it.
        self.logger.debug("tearing down %s", self.user)
        list = self.chino.users.list()
        for user in list.users:
            self.chino.users.delete(user.id, force=True)

    def test_list(self):
        list = self.chino.users.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.users)

    def test_CRUD(self):
        NAME = 'test.user'
        EDIT = NAME + '.edited'
        user = self.chino.users.create(username=NAME, password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        self.user = user
        self.assertIsNotNone(user)
        self.assertEqual(user.username, NAME)
        list = self.chino.users.list()
        # NOTE: this may fail if key are used by someone else.
        ste_2 = self.chino.users.detail(list.users[0].id)
        self.assertEqual(ste_2.username, NAME)

        user.username = EDIT

        ste_2 = self.chino.users.update(**user.to_dict())
        self.logger.debug(ste_2)
        self.assertEqual(user.id, ste_2.id)
        self.assertEqual(ste_2.username, EDIT)

        ste_2 = self.chino.users.detail(user.id)
        self.assertEqual(ste_2.username, EDIT)

        # current not working for main user
        self.assertRaises(CallError, self.chino.users.current)

        # login
        self.chino.users.login(EDIT, '12345678')
        ste_2 = self.chino.users.current()
        self.assertEqual(ste_2.username, EDIT)

        # now should be impossible to create the user
        self.assertRaises(CallError, self.chino.users.create, username='error', password='12345678',
                          attributes=dict(first_name='john', last_name='doe',
                                          email='test@chino.io'))

        self.chino.users.logout()
        self.assertRaises(CallError, self.chino.users.current)

        self.assertRaises(Exception, self.chino.users.login, EDIT, '')

        # rest to admin to delete it
        self.chino.auth.set_auth_admin()
        # this invalidates the user
        self.chino.users.delete(user.id)


class GroupChinoTest(BaseChinoTest):
    def tearDown(self):
        list = self.chino.groups.list()
        for group in list.groups:
            self.chino.groups.delete(group.id, force=True)

    def test_list(self):
        list = self.chino.groups.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.groups)

    def test_CRUD(self):
        group_created = self.chino.groups.create('testing', attributes=dict(hospital='test'))
        self.assertTrue(self._equals(group_created.attributes.to_dict(), dict(hospital='test')))
        self.assertEqual(group_created.groupname, 'testing')
        # NOTE: this may fail
        list = self.chino.groups.list()
        group = list.groups[0]
        details = self.chino.groups.detail(group.id)
        # print group.to_dict()
        # print details.to_dict()
        self.assertTrue(self._equals(details, group), "\n %s \n %s \n" % (details.to_json(), group.to_json()))
        group.groupname = 'updatedtesting'
        self.chino.groups.update(**group.to_dict())
        details = self.chino.groups.detail(group.id)
        self.assertTrue(self._equals(details, group), "\n %s \n %s \n" % (details.to_json(), group.to_json()))
        self.chino.groups.delete(details.id)

    def test_group_user(self):
        group_created = self.chino.groups.create('testing', attributes=dict(hospital='test'))
        user = self.chino.users.create(username="ste", password='12345678',
                                       attributes=dict(first_name='john', last_name='doe',
                                                       email='test@chino.io'))
        # if nothing is raised, then fine
        add = self.chino.groups.add_user(group_created.id, user.id)
        rem = self.chino.groups.del_user(group_created.id, user.id)
        # delete the user at the end
        self.chino.groups.delete(group_created.id, force=True)
        self.chino.users.delete(user.id, force=True)


class PermissionChinoTest(BaseChinoTest):
    # this is articulated to test. left as last
    pass


class RepositoryChinoTest(BaseChinoTest):
    def tearDown(self):
        list = self.chino.repositories.list()
        for repo in list.repositories:
            self.chino.repositories.delete(repo.id, force=True)

    def test_list(self):
        list = self.chino.repositories.list()
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.repositories)

    def test_crud(self):
        created = self.chino.repositories.create('test')
        self.assertEqual(created.description, 'test')
        first = self.chino.repositories.list().repositories[0]
        self.assertTrue(
            self._equals(created.to_dict(), first.to_dict()), "\n %s \n %s \n" % (created.to_json(), first.to_json()))
        first.description = 'edited'

        resp = self.chino.repositories.update(first.id, description=first.description)
        detail = self.chino.repositories.detail(first.id)
        self.assertTrue(
            self._equals(resp.to_dict(), detail.to_dict()), "\n %s \n %s \n" % (resp.to_json(), detail.to_json()))

        self.chino.repositories.delete(first.id)


class SchemaChinoTest(BaseChinoTest):
    def setUp(self):
        super(SchemaChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test').id

    def tearDown(self):
        list = self.chino.schemas.list(self.repo)
        for repo in list.schemas:
            self.chino.schemas.delete(repo.id, force=True)
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
        detail = self.chino.schemas.detail(list.schemas[0].id)
        detail2 = self.chino.schemas.detail(created.id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()), "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))

        detail.structure.fields.append(_Field('string', 'new one'))
        self.chino.schemas.update(**detail.to_dict())
        detail2 = self.chino.schemas.detail(detail.id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()), "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.schemas.delete(detail.id)


class DocumentChinoTest(BaseChinoTest):
    def setUp(self):
        super(DocumentChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test').id
        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        self.schema = self.chino.schemas.create(self.repo, 'test', fields).id

    def tearDown(self):
        list = self.chino.documents.list(self.schema)
        for doc in list.documents:
            self.chino.documents.delete(doc.id, force=True)
        self.chino.schemas.delete(self.schema, True)
        self.chino.repositories.delete(self.repo, True)

    def test_list(self):
        list = self.chino.documents.list(self.schema)
        self.assertIsNotNone(list.paging)
        self.assertIsNotNone(list.documents)

    def test_crud(self):
        content = dict(fieldInt='123', fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19 16:39:47')
        document = self.chino.documents.create(self.schema, content=content)
        # get the last
        document_det = self.chino.documents.detail(document.id)
        self.assertEqual(document.last_update, document_det.last_update)
        content = dict(fieldInt='123',
                       fieldString='test', fieldBool=False, fieldDate='2015-02-19',
                       fieldDateTime='2015-02-19 16:39:47')
        self.chino.documents.update(document.id, content=content)
        document = self.chino.documents.detail(document.id)
        self.assertEqual(123, document.content.fieldInt)
        self.chino.documents.update(document.id,
                                    content=dict(fieldInt=349, fieldString='test', fieldBool=False,
                                                 fieldDate='2015-02-19',
                                                 fieldDateTime='2015-02-19 16:39:47'))
        document = self.chino.documents.detail(document.id)
        self.assertEqual(349, document.content.fieldInt)
        self.chino.documents.delete(document.id)

        fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
                  dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
                  dict(name='fieldDateTime', type='datetime')]
        created = self.chino.schemas.create(self.repo, 'test', fields)
        list = self.chino.schemas.list(self.repo)
        detail = self.chino.schemas.detail(list.schemas[0].id)
        detail2 = self.chino.schemas.detail(created.id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()), "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))

        detail.structure.fields.append(_Field('string', 'new one'))
        self.chino.schemas.update(**detail.to_dict())
        detail2 = self.chino.schemas.detail(detail.id)
        self.assertTrue(
            self._equals(detail.to_dict(), detail2.to_dict()), "\n %s \n %s \n" % (detail.to_json(), detail2.to_json()))
        self.chino.schemas.delete(detail.id)


class BlobChinoTest(BaseChinoTest):
    def setUp(self):
        super(BlobChinoTest, self).setUp()
        self.repo = self.chino.repositories.create('test').id
        fields = [dict(name='blobTest', type='blob'), dict(name='name', type='string')]
        self.schema = self.chino.schemas.create(self.repo, 'test', fields).id

    def tearDown(self):
        self.chino.blobs.delete(self.blob.blob_id)
        self.chino.documents.delete(self.document.id, True)
        self.chino.schemas.delete(self.schema, True)
        self.chino.repositories.delete(self.repo, True)

    def test_blob(self):
        self.document = self.chino.documents.create(self.schema, content=dict(name='test'))

        blob = self.chino.blobs.send(self.document.id, 'blobTest', 'test/logo.png')

        blob_detail = self.chino.blobs.detail(blob.blob_id)
        rw = open("test/out" + blob_detail.filename, "wb")
        rw.write(blob_detail.content)
        rw.close()
        # rd = open('test/logo.png', "rb")
        md5_detail = hashlib.md5()
        md5_detail.update(blob_detail.content)
        # self.assertEqual(md5_detail.digest(), md5_original.digest())
        self.assertEqual(md5_detail.hexdigest(), blob.md5)
        self.blob = blob

        # /
        #
        # def test_user_and_auth(self):
        #     list = self.chino.users.list()
        #     self.assertIsNotNone(list.paging)
        #     self.assertIsNotNone(list.users)
        #     tot = list.paging.count
        #     ste = None
        #     for u in list.users:
        #         if u.username == 'stefano':
        #             ste = u
        #             break
        #     # create
        #     if not ste:
        #         # like this or a dict is also fine.
        #         # attributes can be a dict too.
        #         ste = self.chino.users.create(username='stefano', password='12345678',
        #                                       attributes=dict(first_name='stefano', last_name='Tranquillini',
        #                                                       email='stefano@chino.io'))
        #         self.assertIsNotNone(ste)
        #         list = self.chino.users.list()
        #         self.assertEqual(list.paging.count, tot + 1)
        #
        #     self.assertRaises(CallError, self.chino.users.status)
        #     self.chino.users.login('stefano', '12345678')
        #     ste_res = self.chino.users.status()
        #     print ste_res.id
        #     self.assertEqual(ste.id, ste_res.id)



        # self.logger.addHandler(logging.StreamHandler(sys.stdout))

        # def test_repsitory(self):
        #     pass
        #     res = self.chino.repositories.list()
        #     # for repo in res.repositories:
        #     #     print repo.id
        #     # print res.repositories[0]
        #     # print res.repositories
        #
        # def test_objects(self):
        #     # d = _DictContent(a=1,b=2)
        #     # print dir(d)
        #     # d = _DictContent(**dict(a=1,b=2))
        #     # print dir(d)
        #     #
        #     # u = User(password='ciao')
        #     # print u.to_dict()
        #     #
        #     # s = Schema(structure=dict(fields=[dict(type='int',name='ciao')]))
        #     # print "A %s" % s.structure
        #     #
        #     # for f in s.structure.fields:
        #     #     print f
        #     #
        #     # s = Search(schema_id='schema', result_type='full', sort=[dict(field=1, order=2),dict(field=2,order=3)])
        #     # print s.to_dict()
        #
        #

        #
        #     #
        #     # def test_creation(self):
        #     #     repository = self.chino.repository_create('test')
        #     #     repository = dict(repository_id='9cc4e5a0-7fb8-4b63-87a6-17ee5b2905fb')
        #     #     self.logger.debug('repo %s', repository)
        #     #     fields = [dict(name='fieldInt', type='integer'), dict(name='fieldString', type='string'),
        #     #     dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
        #     #     dict(name='fieldDateTime', type='datetime')]
        #     #     schema = self.chino.schema_create(repository['repository_id'], 'test_schema', fields)
        #     #     schema = dict(schema_id='23c0fcc3-dd29-4e01-9641-4c42337d0d5e')
        #     #     schema = self.chino.schema_detail(schema['schema_id'])
        #     #     self.logger.debug(schema['structure']['fields'])
        #     #     self.assertEqual('fieldInt', schema['structure']['fields'][0]['name'])
        #     #     self.assertEqual('integer', schema['structure']['fields'][0]['type'])
        #     #     fields = schema['structure']['fields']
        #     #     fields[0]['type']='boolean'
        #     #     self.chino.schema_update(schema['schema_id'],dict(fields=fields))
        #     #     schema = self.chino.schema_detail(schema['schema_id'])
        #     #     self.assertEqual('boolean', schema['structure']['fields'][0]['type'])
        #     #     fields = [dict(name='fieldInt2', type='integer'), dict(name='fieldString', type='string'),
        #     #         dict(name='fieldBool', type='boolean'), dict(name='fieldDate', type='date'),
        #     #               dict(name='fieldDateTime', type='datetime')]
        #     #     self.chino.schema_update(schema['schema_id'],fields)
        #     #     schema = self.chino.schema_detail(schema['schema_id'])
        #     #     self.assertEqual('fieldInt2', schema['structure']['fields'][0]['name'])
        #     #
        #     #
        #     #     # # create
        #     #     content = dict(fieldInt='123', fieldString='test', fieldBool=False, fieldDate='2015-02-19',
        #     #                    fieldDateTime='2015-02-19 16:39:47')
        #     #     document = self.chino.document_create(schema['schema_id'], content=content)
        #     #     document = dict(document_id='d7a2b614-7a64-4f81-b0f1-d721e3fea47a')
        #     #     document = self.chino.document_detail(document['document_id'])
        #     #     self.logger.debug("document %s", document)
        #     #     content = dict(fieldInt='123',
        #     #                    fieldString='test', fieldBool=False, fieldDate='2015-02-19',
        #     #                    fieldDateTime='2015-02-19 16:39:47')
        #     #     self.chino.document_update(document['document_id'], content)
        #     #     document = self.chino.document_detail(document['document_id'])
        #     #     self.assertEqual(123, document['content']['fieldInt'])
        #     #     self.chino.document_update(document['document_id'],
        #     #                                content=dict(fieldInt=349, fieldString='test', fieldBool=False,
        #     #                                             fieldDate='2015-02-19',
        #     #                                             fieldDateTime='2015-02-19 16:39:47'))
        #     #     # update
        #     #     content = dict(fieldInt=349,
        #     #                    fieldString='test', fieldBool=False, fieldDate='2015-02-19',
        #     #                    fieldDateTime='2015-02-19 16:39:47')
        #     #     self.chino.document_update(document['document_id'], content)
        #     #     document = self.chino.document_detail(document['document_id'])
        #     #     self.assertEqual(349, document['content']['fieldInt'])
        #     #     self.chino.document_delete(document['document_id'])
        #     #     document = self.chino.document_detail(document['document_id'])
        #     #     self.chino.document_delete(document['document_id'], force=True)
        #     #     try:
        #     #         self.chino.document_detail(document['document_id'])
        #     #         self.assertEqual(0, 1, 'Delete was not done')
        #     #     except:
        #     #         # means that the document is not found -> correct
        #     #         pass
        #     #
        #     #     self.chino.schema_update(schema['schema_id'], )

        # def test_snippet(self):
        #     _PermissionProperty = namedtuple('_PermissionProperty', ['read', 'delete', 'update'])
        #
        #     a=_PermissionProperty(1,2,3)
        #     print a
        #     print json.dumps(a)
        #     b = dict(a=a)
        #     print b
        #     print json.dumps(b)


        if __name__ == '__main__':
            unittest.main()
