# Item Catalog Project

Item Catalog Project is a data driven project utilizing API for CRUD operation, with a secure Google login solution

### Installation
1. Install Vagrant and VirtualBox
2. Clone the fullstack-nanodegree-vm
3. Clone or download code: 
    https://github.com/choikyo/Category_Item.git
4. Launch the Vagrant VM (vagrant up)
5. initilize a SQLite database with starting data: 
    ```
    python itempopulator.py
    ```
    This command generates two tables Item and Category, with simply data saved in 
    itemcategory.db file. To regenerate the data file, simply delete the file, and execute the command above again. 
6. start the server:
    ```
    python project.py
    ```
    This project was specifically using port 5000. Other choices available are 8000 and 80. Please change accordingly in "project.py" file, line 297
    ```
    app.run(host='0.0.0.0', port=5000)
    ```
### Google Login
This project implements a Google Login. It requries user to user a Google credential for CRUD operation through UI. If you wish to switch a user, then clear up your browser cache.


### URI & Functionality:

| URI | FUNCTION |  Login Require |
| ------ | ------ | -------|
| / | main page | no |
| /main | main page | no |
| /catalog/<string:category_name>/items | view list of items for selected category | no |
| /catalog/<string:category_name>/<string:item_name> | view item description | no |
| /catalog/newItem | add an item | yes |
| /catalog/<string:item_name>/edit | edit an item | yes |
| /catalog/<string:item_name>/delete  | delete an item | yes |
  

### JSON Endpoint
It provides 3 JSON endpoints: 

| URI | Return |
| ------ | ------ |
| /catalog.json | Json string of all items |
| /catalog/<string:category_name>.json | Json String of specific category |
| /catalog/<string:item_name>.json | Json String of specific item |


