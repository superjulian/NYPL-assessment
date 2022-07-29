# NYPL Coding Assessment API
This API queries the NYPL Digital Collections API with a user provided search string. 
It then returns the physical locations of the items matching that search term in the digital collections catalog.

## End Points
### GET: /locations/<query>
__PARAMS__:
- query: the query to pass to the NYPL digital collections api

__Return Value__:
- locations: key, value pairs of a location name and the number of distinct items at the location which match the query.
- numResults: the total number of NYPL items matching the query.
- resultsExcluded: the number of items matched by the query in excess of the maximum supported (60).

Since each item requires its own request to find the location, this api only looks up the location For the first 60 items matching a query. 
This is because I've set up the MODS requests to run sequentially and also because I was worried about being throttled. 
I've tested it with up to 200 and it should support 1,000s of results, though it would take an infeasibly long time to execute without running the MODS requests asynchronously.

__Example URL__
[http://127.0.0.1:\<port\>/locations/monster](http://127.0.0.1:5000/locations/monster)
