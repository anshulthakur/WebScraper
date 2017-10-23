filters = {'deny': ['^.*\//blog\..*',
		           '^.*/accounts/login/.*',
		           '^.*/accounts/twitter/.*',
		           '^.*/accounts/facebook/.*',
		           '^.*/accounts/google/.*', #Nuisance
		           '^.*\.php\?.*', #Python based sites don't call into PHP code (except if its a FB script)
		           '.*#.*', #Ignore Anchor Links to same page
		      	   ]
		   }
