import sys
import cfg
from chino.api import ChinoAPI

__author__ = 'Stefano Tranquillini <stefano.tranquillini@gmail.com>'

import unittest
import logging
import logging.config



# logging.basicConfig(stream=sys.stderr)



class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.chino = ChinoAPI(cfg.customer_id, cfg.customer_key)
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('chino')
        # self.logger.setLevel(logging.DEBUG)
        # self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def test_user(self):
        repositories_list = self.chino.repository_list()
        repositories = repositories_list['repositories']
        # self.logger.debug("Total repositories %s" % repositories_list['total_count'])
        for repository in repositories:
            self.logger.debug("Repo %s " % repository['repository_id'])
            schemas_list = self.chino.schemas_list(repository['repository_id'])
            # self.logger.info("Total schemas %s" % schemas_list['total_count'])
            schemas = schemas_list['schemas']
            for schema in schemas:
                self.logger.debug("\t Schema %s " % schema['schema_id'])
                documents_list = self.chino.documents_list(schema['schema_id'])
                # self.logger.info("Total documents %s" % documents_list['total_count'])
                documents = documents_list['documents']
                for document in documents:
                    self.logger.debug("\t \t Document %s " % document['document_id'])


if __name__ == '__main__':


    unittest.main()
