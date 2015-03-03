import cfg
from chino.api import ChinoAPI

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

import unittest


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.chino = ChinoAPI(cfg.customer_id, cfg.customer_key)

    def test_user(self):
        # repository = self.chino.repository_create("ciao")
        # print repository.description
        # repository = self.chino.repository_update(repository.repository_id, repository)
        # print repository.description
        # res = self.chino.repository_list()
        # for repo in res.results:
        #     print repo.repository_id

        res = self.chino.repository_list()
        print res
        for repo in res['repositories']:
            print repo['repository_id']


if __name__ == '__main__':
    unittest.main()
