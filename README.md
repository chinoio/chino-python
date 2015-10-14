#  CHINO.io Python client #
*Official* Python wrapper for **CHINO.io** API,

Docs is available [here](http://docs.chino.apiary.io/)

#How to use it
First create a variable from the `Chino` class

`chino = ChinoAPI(<customer_id>, <customer_key>)`

passing your `customer_id` and `customer_key`

this will give you access to the methods:

### Init

- to init the `ChinoAPI` import it `from chino.api import ChinoAPI`
- `chino = ChinoAPI(customer_id=..,customer_key=..,customer_token=..)`
    
    - customer_id: mandatory
    - customer_key: optional, if specified the auth is set as admin
    - customer_token: optional, if specified the auth is as user 
    - if key and token are specified, the auth uses key
    
    
### AUTH

- /auth/login `auth_user_login`. *Note* this overrides the auth, when called (if successful,the auth is set for the user)
- /auth/info `auth_user_status`
- /auth/logout `auth_user_logout`
- `set_auth_admin` to set the auth as admin
- `set_auth_user` to set the auth as the user

### User

- /users `user_list`
- /users `user_detail`
- /users/{user_id} `user_create`
- /users/{user_id} `user_update`
- /users/{user_id} `user_delete`

### Group

- /groups `group_list`
- /groups `group_create`
- /groups/{group_id} `group_detail`
- /groups/{group_id} `group_update`
- /groups/{group_id} `group_delete`
- /groups/{group_id}/users/{user_id} `group_add_user`
- /groups/{group_id}/users/{user_id} `group_del_user`

### Permission

- /perms/users/{user_id} `permission_user`
- /perms/schema/{schema_id}/users/{user_id} `permission_create_user`
- /perms/schema/{schema_id}/users/{user_id} `permission_delete_user`
- /perms/groups/{group_id} `permission_group`
- /perms/schemas/{schema_id} `permission_schema`
- /perms/schema/{schema_id}/groups/{group_id} `permission_create_group`
- /perms/schema/{schema_id}/groups/{group_id} `permission_delete_group`

### Repository

- /repositories `repository_list`
- /repositories `repository_create`
- /repositories/{repository_id} `repository_detail`
- /repositories/{repository_id} `repository_update`
- /repositories/{repository_id} `repository_delete`

### Schemas

- /repositories/{repository_id}/schemas `schemas_list`
- /repositories/{repository_id}/schemas `schema_create`
- /schemas/{schema_id} `schema_detail`
- /schemas/{schema_id} `schema_update`
- /schemas/{schema_id} `schema_delete`

### Document

- /schemas/{schema_id}/documents `documents_list`
- /schemas/{schema_id}/documents `document_create`
- /documents/{document_id} `document_detail`
- /documents/{document_id} `document_update`
- /documents/{document_id} `document_delete`

### BLOB

- /blobs `blob_start`
- /blobs `blob_chunk`
- /blobs/commit `blob_commit`
- /blobs/{blob_id} `blob_detail` (returns a dict with `filename` and `blob`)
- /blobs/{blob_id} `blob_delete`
- `blob_send` help function to upload a file

### SEARCH

- /search/{schema_id} `search`

*Plus methods that are utils for auth and to manage communications*

##Note:

The calls returns the dict (as explained in the doc) for correct calls or raise an Exception if there's an error. Thus, you can catch the exception in the code if something bad happens.


Create methods have the required parameters, e.g.:

`document_create(self, schema_id, content, insert_user=None):`

Update methods accept arbitrary parameters (but check the docs otherwise there will be an error from the server):

`document_update(self, document_id, **kwargs):`

This means that, for example, the `document_update` can be called as: 

- `document_update(<id_doc>,content=dict(...))` 
- `document_update(<id_doc>,description='...')` 
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
Beta

##TODO:

- TEST
- Write 

#BUILD AND USAGE

- `python setup.py install`
-  in python `from chino.api import ChinoAPI`
