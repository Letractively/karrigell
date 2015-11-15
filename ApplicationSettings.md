# Introduction #

The server can run one or several applications. By default, starting the server with

```
Karrigell.run()
```

means that there is only one application, serving scripts and documents from the directory where the server script stands

This page explains how you can change these default settings

# Application settings #

An application is described by a subclass of the class <font color='#333388' size='2'><b><code>Karrigell.App</code></b></font>. Each subclass defines the following attributes :

### root\_url ###
> A string beginning with a forward slash (/), indicates the first part of the urls served by this application. Defaults to "/"

### root\_dir ###
> The directory in the file system to serve scripts and documents from. Defaults to the directory where the server script stands

### session\_storage\_class ###
> The class used to manage the storage and retrieval of session objects (see SessionManagement). Defaults to the class <font color='#333388' size='2'><b><code>SQLiteSessionManagement</code></b></font> in module <font color='#336633' size='2'><b>Karrigell.sessions</b></font>

### users\_db ###
> An object representing the users database. It must have the same interface as the class <font color='#333388' size='2'><b><code>SQLiteUsersDb</code></b></font> in module <font color='#336633' size='2'><b>Karrigell.admin_db</b></font>

> You can use a SQLite users database by specifying its path in the file system :

```
users_db = Karrigell.admin_db.SQLiteUsersDb(db_path)
```

> Defaults to <font color='#333388' size='2'><b>None</b></font>, meaning that there is no users management for this application

### login\_url ###
> If a users database has been defined, indicates the url where a script must be redirected if it requires user login

> Defaults to _root\_url/admin/login.py/login_ (the script <font color='#106010' face='courier'>login.py</font> is provided in the directory <font color='#106010' face='courier'>www/admin</font> of the distribution)

### filters ###
> A list of methods of the application class. Each method takes a single argument, an instance of the class <font color='#333388' size='2'><b><code>RequestHandler</code></b></font> in module <font color='#336633' size='2'><b>Karrigell</b></font>

> The filters are applied one after the other when the request has been received from the client. The function can either return a value or raise an exception :
    * if it returns <font color='#333388' size='2'><b>None</b></font>, the next filter in the list is applied
    * if it returns another value, this value is the absolute path of a script in the file system
    * if it raises <font color='#333388' size='2'><b><code>HTTP_REDIRECTION(url)</code></b></font>, the request is redirected to the specified url
    * if it raises <font color='#333388' size='2'><b><code>HTTP_ERROR(code,message)</code></b></font>, the request handling stops and the specified HTTP error is sent to the client

> Filters offer a flexible way of managing directives like access control to files according to their extension, or to folders according to the user's role, etc

# Serving applications #

Edit the script <font color='#106010' face='courier'>server.py</font> :

```
import Karrigell
import Karrigell.admin_db

class Default(Karrigell.App):
    pass

class Pictures(Karrigell.App):
    root_url = "/pics"
    root_dir = "/path/to/pictures"
    users_db = Karrigell.admin_db.SQLiteUsersDb('/path/to/users_db')

Karrigell.run(apps=[Default,Pictures])
```

The function run() takes a keyword argument <font color='#333388' size='2'><b>apps</b></font>, set to a list of application classes

In this example, the server runs 2 application : the default application, and an application serving requests for urls starting with /pics/, taking the files and scripts from the specified root\_dir. This application manages users login in an SQLite database at the specified location in the file system

For obvious security reasons, the users database should be located outside of the root directory