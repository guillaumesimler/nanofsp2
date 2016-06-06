# Multi User Blog

Authors
----

**Guillaume Simler**, a Udacity Frontend Nanodegree graduate and Full Stack Web Developer Student, more information and contact details on my [Github profile](https://github.com/guillaumesimler)

Project description
----

A multiuser blog with a user access management in order to train:
* the use of Google App Engine, templates and its Datastore Database
* the implementation of access and


Used resources
----

### Libraries & frameworks: **python**

* [**jinja2**](http://jinja.pocoo.org/), a templating library for Python & natively implemented in Google App Engine
* **webapp2**, GAE's main library
* **db**, the old version of the Google Datastore which was part of the course, unlike [~~ndb, the newest version~~](https://cloud.google.com/appengine/docs/python/ndb/db_to_ndb)

### Libraries & frameworks: **html, css, js**

* no specific libraries, frameworks or templates were used-

### App Engine

* [Google App Engine (GAE)](https://cloud.google.com/appengine/docs/python/), Google's [platform as a service solution](https://en.wikipedia.org/wiki/Google_App_Engine)


Data structure
---

The entity (GAE datastore's name for table) is composed of the following elements:

* **title**, a mandatory string, storing the entry's title
* **bodytext**, a mandatory text field (containing more than the 500 characters of the string datatype), storing the entry's main text
* contributor, a mandatory string, storing the contributor's name. Actually one might discuss some attributes:
	- currently it is hardcoded to Guillaume
	- it might be optional (this would imply the rewriting of the current templates - insering an if statement)
* date, an automated time stamp of the first editing
* modified, an automated time of the last editing (currently not used)

How to use
----

#### Initialize the project

1. Clone the [Repo](https://github.com/guillaumesimler/nanofsp2)
2. Open the project with Google App Engine
3. Open the local host with the designed port
4. try and use

#### Later on

* launch the following [webpage](**fresh_tomatoes.html**)

Bugs
----

Bugs can be reported on the [Github section](https://github.com/guillaumesimler/nanofsp2/issues)

They will be discussed there or on "blog/debug"


Repository
----
* the [working project](https://github.com/guillaumesimler/nanofsp2)

License
----

The **current version** is under [_MIT License_](https://github.com/guillaumesimler/nanofsp2/blob/master/LICENSE.txt)