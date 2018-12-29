filters = {'deny': ['^.*\//blog\..*',
		           '^.*/accounts/login/.*',
		           '^.*/accounts/twitter/.*',
		           '^.*/accounts/facebook/.*',
		           '^.*/accounts/google/.*', #Nuisance
		           '^.*\.php\?.*', #Python based sites don't call into PHP code (except if its a FB script)
		           '.*#.*', #Ignore Anchor Links to same page
		      	   ]
		   }

exclude_domains = ["feedspot.com",
                   "rottentomatoes.com",
                   "google.com",
                   "indiatimes.com",
                   "news18.com",
                   "copyscape.com",
                   "prchecker.info",
                   "blogadda.com",
                   "blogcritics.org",
                   "wikipedia.org",
                   "zemanta.com",
                   "yahoo.com",
                   ]
