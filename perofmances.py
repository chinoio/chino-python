import random
import time

from chino.api import ChinoAPIClient

m_customer_id = '***REMOVED***'
m_customer_key = '***REMOVED***'
m_repository_id = 'b09e06c9-4a7c-44e5-9243-52699ebf3667'
chino = ChinoAPIClient(m_customer_id, m_customer_key, session=False)


def create_schema():
    r = chino.schemas.create(m_repository_id, "testSchema", [
        {"name": "pharmacy_id", "type": "string", "indexed": True},
        {"name": "history_date", "type": "integer", "indexed": True},
        {"name": "creation_date", "type": "integer", "indexed": True},
        {"name": "attempt_id", "type": "string", "indexed": True},
        # {"name":"history","type": "text"}
    ])
    print r.id
    return r.id


def performances():
    schema = create_schema()
    real_start = time.time()
    data = {
        'pharmacy_id': "1234567890",
        'history_date': 12345,
        'creation_date': 0000,
        'attempt_id': "0987654321",
        # 'history': info[3],
    }
    for i in range(1000):
        start = time.time()
        doc = chino.documents.create(schema, data)
        n = time.time()
        ex_c = n - start
        start = time.time()
        chino.documents.delete(doc.id, force=True)
        n = time.time()
        ex_d = n - start
        print "%s; %f; %f; %f" % (i, ex_c, ex_d, n - real_start)
        # print "---waiting: %s "  % w
        # time.sleep(w)
    chino.schemas.delete(schema, force=True)


# performances()

def scheams_delete():
    repo = chino.repositories.list()
    print "list %s "% repo.paging
    for r in repo.repositories:
        print "repo %s" % r.id
        schemas = chino.schemas.list(r.id)
        for s in schemas.schemas:
            print "deleting %s " % s.id
            n = time.time()
            chino.schemas.delete(s.id, force=True)
            print "deleted in %f " % (time.time()-n)
        chino.repositories.delete(r.id, force=True)
scheams_delete()