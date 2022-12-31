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
  echo ""
  echo "Re-index from old to new"
  echo ""
  curl -X POST \
    http://localhost:9205/_reindex \
    -H 'cache-control: no-cache' \
    -H 'content-type: application/json' \
    -d '{
    "source": {
      "index": "'${INDEX_NAME}'"
    },
    "dest": {
      "index": "'${INDEX_NAME}-cloned'"
    }
  }'
done