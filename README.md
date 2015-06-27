#  CHINO.io Python client #
*Official* Python wrapper for **CHINO.io** API,

Docs is available [here](http://docs.chino.apiary.io/)

#How to use it
First create a variable from the `Chino` class

`chino = ChinoAPI(<customer_id>, <customer_key>)`

passing your `customer_id` and `customer_key`

this will give you access to the methods:

**User**

- user_list:
- user_detail
- user_create
- user_update
- user_delete

**Group**

- group_list
- group_detail
- group_create
- group_update
- group_delete
- group_add_user
- group_del_user

**Permission**

- permission_user
- permission_create_user
- permission_group
- permission_schema

**Repository**

- repository_list
- repository_detail
- repository_create
- repository_update
- repository_delete

**Schemas**

- schemas_list
- schema_create
- schema_detail
- schema_update
- schema_delete
- schema_add_user
- schema_del_user

**Document**

- documents_list
- document_create
- document_detail
- document_update
- document_delete

*Plus methods that are utils for auth and to manage comunications*

##Note:

The calls returns the object (as explained in the doc) for correct calls or raise an Exception if there's an error. Thus, you can catch the exception in the code if something bad happens.

Create methods specifies the required parameters, e.g.:

`document_create(self, schema_id, content, insert_user=None):`

Update methods accepts arbitrary parameters (check the docs):

`document_update(self, document_id, **kwargs):`

This means that the `document_update` can be called as: 

- `document_update(<id_doc>,content=dict(...))` 
- `document_update(<id_doc>,description='')` 
- or with both


## Requirements ##
- requests (already in requirements.txt)

## DOC ##
Not completed. Can be compiled with [sphinx](sphinx-doc.org). 

requires the following package (via pip)

- sphinx-autobuild
- sphinx-autodoc-annotation
- sphinx-rtd-theme

#Status
Still in dev

##TODO:

- add missing calls
- test all the methods: BLOB, Search 
- upload test class