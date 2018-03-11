##: references: https://github.com/git/git/blob/master/contrib/subtree/git-subtree.txt

ls-subt:
	git log | grep git-subtree-dir | tr -d ' ' | cut -d ":" -f2 | sort | uniq
push-subt:
	git subtree push --prefix=django-simple-imports git@github.com-ahammouda:ahammouda/django-simple-imports.git master
pull-subt:
	git subtree pull --prefix=django-simple-imports git@github.com-ahammouda:ahammouda/django-simple-imports.git master