#  CHINO.io Python client #

*Official* Python wrapper for **CHINO.io** API,

Docs is available [here](http://docs.chino.io)

## Install via pip

`pip install chino`

##How to use it
First create a variable from the `Chino` class

`from chino.api import ChinoAPIClient`
`chino = ChinoAPIClient(<customer_id>, <customer_key>)`

passing your `customer_id` and `customer_key`

this will give you access to the methods.

### Init

- to init the `ChinoAPIClient` import it `from chino.api import ChinoAPIClient`
- `chino = ChinoAPIClient(customer_id=..,customer_key=..,customer_token=..)`

    - customer_id: mandatory
    - customer_key: optional, if specified the auth is set as admin
    - customer_token: optional, if specified the auth is as user
    - if key and token are specified, the auth uses key


### parameter
The `ChinoAPIClient` accepts the following parameters:

-`customer_id` : see auth section
-`customer_key` : see auth section
-`customer_token`:  see auth section
-`url='https://api.chino.io/'`: the url, deafult is the api. You can also use `api.test.chino.io`
-`version='v1'`: the verison of the API (we have only v1 so far)
-`timeout=30`: timeout for the requests. If you want to get an exception if a request takes more than that time.
- `session=True`: see section on this

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

### requests.Session()
To improve the performances the Python SDKs uses `requests` and [`requests.Session()`](http://docs.python-requests.org/en/master/user/advanced/?highlight=session). The session keeps the connection open and does not add overhead on the request.
This has a *huge* improvment in the performances. It's 4 times faster!
You can, however, disable this functionality setting `session=False` when creating the `ChinoAPIClient()`


### User
Class to manage the user, `chino.users`

- `login`
- `current`
- `logout`
- `list`
- `detail`
- `create`
- `update`
- `partial_update`
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
`chino.collections`

- `list`
- `create`
- `detail`
- `update`
- `delete`
- `list_documents`
- `add_document`
- `rm_document`
- `search`

### Consents
`chino.consents`

- `list`
- `create`
- `detail`
- `history`
- `update`
- `withdraw`
- `delete` (only available for test API)

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

## `_id`
each element has a `_id()` function that returns the `id` of the entity

## DOC
Not completed. Can be compiled with [sphinx](sphinx-doc.org).

requires the following package (via pip)

- sphinx-autobuild
- sphinx-autodoc-annotation
- sphinx-rtd-theme

##Status
Beta

##For contributions:

- install requirements.txt
- dev
- test
:warning: - the test deletes ALL your repo/schemas/document in the teardown function. **be careful!**
- create a pull request.

##Support
use issues of github


### Build for pip (internal notes)
- `rm -r dist/*`
- `python setup.py bdist_wheel --universal`
- `twine upload dist/*`
