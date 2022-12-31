INDICIES=(
  "jper-failed"
  "jper-license"
  "jper-match_prov"
  "jper-routed"
  "jper-routed202212"
  "jper-unrouted"
)

for INDEX_NAME in ${INDICIES[@]}; do
  NEW_INDEX_NAME=${INDEX_NAME}-cloned

  # Make index read-write
  echo ""
  echo "Make index ${INDEX_NAME} read write"
  curl -X PUT \
    http://localhost:9205/${INDEX_NAME}/_settings \
    -H 'content-type: application/json' \
    -d '{
    "settings": {
      "index.blocks.write": false
    }
  }'

  # Make new index read-write
  echo ""
  echo "Make index ${INDEX_NAME}-cloned read write"
  curl -X PUT \
    http://localhost:9205/${INDEX_NAME}-cloned/_settings \
    -H 'content-type: application/json' \
    -d '{
    "settings": {
      "index.blocks.write": false
    }
  }'

  echo ""
  echo "completed"
  echo ""
done
