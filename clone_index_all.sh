INDICIES=(
  "jper-routed201907"
  "jper-routed201908"
  "jper-routed201909"
  "jper-routed201910"
  "jper-routed201911"
  "jper-routed201912"
  "jper-routed202001"
  "jper-routed202002"
  "jper-routed202003"
  "jper-routed202004"
  "jper-routed202005"
  "jper-routed202006"
  "jper-routed202007"
  "jper-routed202008"
  "jper-routed202009"
  "jper-routed202010"
  "jper-routed202011"
  "jper-routed202012"
  "jper-routed202101"
  "jper-routed202102"
  "jper-routed202103"
  "jper-routed202104"
  "jper-routed202105"
  "jper-routed202106"
  "jper-routed202107"
  "jper-routed202108"
  "jper-routed202109"
  "jper-routed202110"
  "jper-routed202111"
  "jper-routed202112"
  "jper-routed202201"
  "jper-routed202202"
  "jper-routed202203"
  "jper-routed202204"
  "jper-routed202205"
  "jper-routed202206"
  "jper-routed202207"
  "jper-routed202208"
  "jper-routed202209"
  "jper-routed202210"
  "jper-routed202211"
)

for INDEX_NAME in ${INDICIES[@]}; do
  NEW_INDEX_NAME=${INDEX_NAME}-cloned

  # Delete an index
  echo ""
  echo "Deleting index ${INDEX_NAME}"
  curl -X DELETE \
    http://localhost:9205/${INDEX_NAME} \
    -H 'content-type: application/json'

  # Make index read only
  echo ""
  echo "Make index ${INDEX_NAME}-cloned read only"
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
  curl -X POST \
    http://localhost:9205/${INDEX_NAME}-cloned/_clone/${INDEX_NAME} \
    -H 'content-type: application/json'

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
