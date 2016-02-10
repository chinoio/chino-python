#  CHINO.io Python client #
*Official* Python wrapper for **CHINO.io** API,

Docs is available [here](http://docs.chino.apiary.io/)
## Install via pip 
`(sudo) pip install git+https://github.com/chinoio/chino-python-library.git@release/newversion`

> this is for the current branch, specify the branch after `@`

##How to use it
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
Class that manages the auth, `chino.auth`

**In 99% of the cases this class does not need to be used.**
- `init`:
    - `customer_id` mandatory
    - `customer_key` optional
    - `access_token` optional
    - **NOTE:  if `customer_key` is set, it auth as admin, if `access_token` is set, then auth as customer. Admin has precedence in case both are set**
- `set_auth_admin` to set the auth as admin
- `set_auth_user` to set the auth as the user
- `get_auth` to get the Auth object


### User
Class to manage the user, `chino.users`

- `login`
- `current`
- `logout`
- `list`
- `detail`
- `create`
- `update`
- `delete`

### Group
`chino.groups`

- `list`
- `detail`
- `create`
- `update`
- `delete`
- `add_user`
- `del_user`

### Permission
`chino.permissions`

- `resources`
- `resource`
- `resource_children`
- `read_perms`
- `read_perms_doc`
- `read_perms_user`
- `read_perms_group`

### Repository
`chino.repotiories`

- `list`
- `detail`
- `create`
- `update`
- `delete`

### Schemas
`chino.schemas`

- `list`
- `create`
- `detail`
- `update`
- `delete`

### Document
`chino.documents`

- `list`
- `create`
- `detail`
- `update`
- `delete`


### BLOB
`chino.blobs`

- `send`: help function to upload a blob, returns `BlobDetail('bytes', 'blob_id', 'sha1', 'document_id', 'md5')`
- `start`
- `chunk`
- `commit`
- `detail`: returns `Blob(filename, content)``
- `delete`

### SEARCH
`chino.searches`

- `search`: **Note: to be tested**

### UserSchemas
`chino.user_schemas`

- `list`
- `create`
- `detail`
- `update`
- `delete`

### Collections
`chino.user_schemas`

- `list`
- `create`
- `detail`
- `update`
- `delete`
- `list_documents`
- `add_document`
- `rm_document`


### OTHER
*Plus methods that are utils for auth and to manage communications*

##Note:

The calls returns Objects (see object.py) of the type of the call (e.g. documents return Documents) or raise an Exception if there's an error. Thus, you can catch the exception in the code if something bad happens.
In case of `list` it reutrns a ListeResult, which is composed of:
- paging
    - offest
    - count
    - total_count
    - limit
- `name of the object in plural`: such as `documents` that contains the list of objects

**all the objects, except Blob and BlobDetail have a method to be transformed into a `dict` -> `.to_dict()` and to the the id `.id`**


## Requirements ##
- requests (already in requirements.txt)

## DOC 
Not completed. Can be compiled with [sphinx](sphinx-doc.org). 

requires the following package (via pip)

- sphinx-autobuild
- sphinx-autodoc-annotation
- sphinx-rtd-theme

#Status
Beta

##TODO:
- Finish the test



#BUILD AND USAGE

- `python setup.py install`
-  in python `from chino.api import ChinoAPI`
