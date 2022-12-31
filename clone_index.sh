INDEX_NAME=jper-routed202212
NEW_INDEX_NAME=${INDEX_NAME}-cloned

# Delete an index
echo ""
echo "Deleting index ${INDEX_NAME}"
echo ""
curl -X DELETE \
  http://localhost:9205/${INDEX_NAME} \
  -H 'content-type: application/json'

# Make index read only
echo ""
echo "Make index ${INDEX_NAME}-cloned read only"
echo ""
curl -X PUT \
  http://localhost:9205/${INDEX_NAME}-cloned/_settings \
  -H 'content-type: application/json' \
  -d '{
  "settings": {
    "index.blocks.write": true
  }
}'

# Clone the index
echo ""
echo "Clone the index"
echo ""
curl -X POST \
  http://localhost:9205/${INDEX_NAME}-cloned/_clone/${INDEX_NAME} \
  -H 'content-type: application/json'

echo ""
echo "completed"
echo ""