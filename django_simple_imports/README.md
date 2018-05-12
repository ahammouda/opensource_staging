django-simple-imports
=====================

##### Authors
Adam Hammouda

##### Sponsor
This project begain with the generous sponsorship of [Bridge Financial Technology](http://www.bridgeft.com/about/)

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
must be maintained during import.

##### Main Pieces

* ModelImporter (import_configuration_v2.py)

* ImportManager (import_managers_v3.py)

* SystemImporter (system_importer_v2.py)


##### Requirements
* (N.B: Subject to testing):  python 3.6 -- ordering of dependencies effect topological sort outcomes and must remain static

##### Status And Limitations
* Creating objects with m2m dependencies will have require at least O(n) trips to the database. 
This appears to be a limitation of the django ORM however - will nee to do a bit more research 
to confirm.

##### TODO (High Wave Number):
2.) Implement updates (table stakes)

3.) Derive methods bulk-getting dependent imports, before mapping their fks into the relevant objects
    -->  First thought here: maybe derive some manual caching layer that the importer_mananger references??

4.) Test performance to see if it's as fast as some custom 'getter'

5.) Eventually implement interactive prompt to infer dependencies of desired set of tables to import (i.e:
    auto-generate transitive closure of a couple of models)


##### Table Stakes
* Exception handling in importer_manager (if referenced object not found, etc --> should spit out specification for importing that object alone


##### Deal with while documenting
* Verify possible topological sort issues (ensure uniqueness, etc), and constraints to put in place:
  https://math.stackexchange.com/questions/2051092/unique-topological-sort-for-dag
* Implement an iterative dfs in sorter.py (to avoid recurision depth issues)