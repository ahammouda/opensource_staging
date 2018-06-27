django-simple-imports
=====================

##### Sponsor
This project began with the generous sponsorship of [Bridge Financial Technology](http://www.bridgeft.com/)

##### License
BSD 2-Clause "Simplified" License.

#### Prior Work
There are a number of different tools which work to make import/export a generic problem for the django ORM, 
however the most popular library appears to be [django-import-export](https://github.com/django-import-export/django-import-export).
I would highly recommend exploring this library while considering ours - they may be better suited for your needs.  

#### Overview
A data import library for the django ORM.  Allows for richness in foreigkey ('data dependency')
constraint specification for imports, that other libraries struggle with (see prior work).  
There are extensive ambitions for this library, but for now aims to simply solve the problem of 
bulk importing rows for a single model, given an arbitray depth of depency relationships that 
must be maintained/referenced during import.

Check out the [this animation](https://raasama-concept.herokuapp.com/draw-re-sim) for a basic idea of what the tool does.  It's a work in progress

##### Main Pieces

* ModelImporter (import_configuration_v2.py)

* ImportManager (import_managers_v3.py)

* SystemImporter (system_importer_v2.py)


##### Requirements
* python 3.6 -- ordering of dependencies effect topological sort outcomes and must remain static

##### Status And Limitations
* Creating objects with m2m dependencies will require at least O(n) trips to the database. 
This appears to be a limitation of the django ORM however - will nee to do a bit more research 
to confirm.

##### TODO
* Exception handling in importer_manager (if referenced object not found, etc --> should log informative error message
* Verify/prove possible topological sort issues (ensure uniqueness, etc), and constraints to put in place:
  https://math.stackexchange.com/questions/2051092/unique-topological-sort-for-dag
* Implement an iterative dfs in sorter.py (to avoid recurision depth issues)
