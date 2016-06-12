# Multi User Blog

Foreword
----
This project was quite a training in "agile development", with regular adaptations of the specs.

Table of content
----
- [Authors](#section1)
- [Project description](#section2)
- [How to use](#section3)
- [Deviations from Rubrics](#section4)
- [Used resources](#section5)
- [File structure](#section6)
- [Data structure](#section7)
- [Bugs](#section8)
- [Repository](#section9)
- [License](#section10)


<div id='section1'/>
Authors
----
* **[Steve Huffmann](https://www.linkedin.com/in/shuffman56)**, the course instructor which structured a lot of this historic code through quizzes and homeworks.
	- What is exactly yours -Steve- and mine, I can't tell anymore. 
	- What is certain is my deepest gratitude to have had you, Steve, as instructor!!!
* **Guillaume Simler**, a Udacity Frontend Nanodegree graduate and Full Stack Web Developer Student, more information and contact details on my [Github profile](https://github.com/guillaumesimler)

<div id='section2'/>
Project description
----

A multiuser blog with a user access management in order to train:
* the use of Google App Engine, templates and its Datastore Database
* the implementation of access (&) right management

<div id='section3'/>
How to use
----

#### Initialize the project

1. Clone the [Repo](https://github.com/guillaumesimler/nanofsp2)
2. Open the project with Google App Engine
3. Open the local host with the designed port
4. try and use (be certain to use [your local host]/blog)

#### Or simply

* launch the following [webpage](http://guillaume-udacity-blog.appspot.com/blog)


<div id='section4'/>
Deviations from Rubrics
----

There are a few deviations from the **project rubric**, I asked yout to accept:
* the "error messages" for editing the posts or comments are not implemented as a different solution was already coded:
	- if you're the author, you'll see the edit button
	- if you're not, you won't see it
* the "error message" was implemented for the personal like or dislike button. The logic would be the same

* the "login errors" are not specific, ie. it doesn't matter if your password or your login name is wrong, you will get the same error message. The idea is not to reveal which one is wrong (in case of abuses)

<div id='section5'/>
Used resources
----

### Libraries & frameworks: **python**

* [**jinja2**](http://jinja.pocoo.org/), a templating library for Python & natively implemented in Google App Engine
* **webapp2**, GAE's main library
* **db**, the old version of the Google Datastore which was part of the course, unlike [~~ndb, the newest version~~](https://cloud.google.com/appengine/docs/python/ndb/db_to_ndb)
* **hmac**, **hlib** to enable encoding
* **re** to enable Regular Expression checks in Pythons

### Libraries & frameworks: **html, css, js**

* no specific libraries, frameworks or templates were used

### App Engine

* [Google App Engine (GAE)](https://cloud.google.com/appengine/docs/python/), Google's [platform as a service solution](https://en.wikipedia.org/wiki/Google_App_Engine)

<div id='section6'/>
File structure
---
After the first review, I tried to structure the file in a MVM configuration

The files of the project are the following:
* **The Viewmodel File**:
	- **multiuserblog.py**: the main file of project

* **Model files:** (stored in models\), describe in the [next section](#section7))
	- **__init__.py**, 
	- **userdata.py** storing the user data
	- **postcomments.py** storing the comment data
	- **blogentries.py** storing the blogentry data


#### Additional files, templates and helpers
* **security.py**: for obvious security reasons, the security management is "outsourced" in a file which would have restricted access right in a multi programmer environment (stored in a specific folder)
* **templates**:
	- starting with 0x: the templates managing the views of the main blog. 01 being the generic template head
	- starting with 1x: the templates managing the login and restructuring. 11 being the specific generic template for these pages
	- starting with 9x: special, rather admin templates
* **GAE files**:
	- app.yaml and index.yaml
* **Documentation** (selfexplaining):
	- readme.md
	- license.txt


<div id='section7'/>
Data structure
---

The entity (GAE datastore's name for table) is composed of the following elements:

* **Blogentries** (the main table)
	- **title**, a mandatory string, storing the entry's title
	- **bodytext**, a mandatory text field (containing more than the 500 characters of the string datatype), storing the entry's main text
	- **contributor**, a mandatory string, storing the contributor's name, filled automatically with the login data (coming from __UserData__)
	- **date**, an automated time stamp of the first editing
	- modified, an automated time of the last editing (currently not used)
	- **likes**, a string with a default value of 0, which will count the number of likes
	- **dislikes**, a string with a default value of 0, which will count the number of dislikes
	- **comments**, a string with a default value of 0, which will count the number of comments
	- **liker**, a StringList, one great Input after the second review!!!!

* **Comments**: this table might be discussed. If no editing would be required it could be a subpart of Blogentries, if it accepts list items
	- **postkey**, a string which is use as a __primary key__ to link __Blogentries__ and __Comments__+
	- **author**, identical to the **contributor** of Blogentries
	- **comment**, a textfield containing the comments
	- **date**, an automated save of the creation date

* **UserData**
	- **Username**, a string which is use as a __primary key__ to link __Blogentries__, __Userdata__ and __Comments__+ 	
	- **hPassword**, a string to save the hashes password
	- **Email**, an optional string to save an Email if granted

* **Primary Keys**
	- **Username**, **author**, **contributor**:  the two last elements are filled by the first creating a strong 1:n relationship
	- **postkey** which saves the Blogentries.key of the row to create a n:1 relationship


<div id='section8'/>
Bugs
----

Bugs can be reported on the [Github section](https://github.com/guillaumesimler/nanofsp2/issues)

They will be discussed there or on ["blog/debug"]()

<div id='section9'/>
Repository
----
* the [working project](https://github.com/guillaumesimler/nanofsp2)

<div id='section10'/>
License
----

The **current version** is under [_MIT License_](https://github.com/guillaumesimler/nanofsp2/blob/master/LICENSE.txt)