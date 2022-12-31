The elasticsearch index needs to be modified to accommodate embargo change to string frominteger as a part of the license management changes

For this we need to 
1. Create a new index with the modified mapping (INDEX_NAME-cloned)
2. Reindex the data in INDEX_NAME to INDEX_NAME-cloned
3. Make the new index read only
4. Delete the old index
5. Clone the new index to old ondex
6. Make the old and new index read write

