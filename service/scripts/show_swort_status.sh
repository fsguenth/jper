#! /bin/bash

#ESHOST=`hostname|sed -e 's/1\./4./'`
#ES="http://${ESHOST}:9200"

# working on a local tunnel
if [ `hostname` == "probibw41" ]; then
    ESHOST="localhost"
fi

# check ESHOST environment variable
if [ -z "$ESHOST" ] ; then
    echo; echo "ERROR: ESHOST environment variable missing"; help; exit 1 ;
fi

ES="http://${ESHOST}:9200"

echo '|| Id || Status || Last Deposit Date || Last Updated || Retries ||'
curl -s "${ES}/jper-sword_repository_status/_search?size=1000" \
 | jq '.hits.hits[]._source|.id,.status,.last_deposit_date,.last_updated,.retries' \
 | sed -e 'N;N;N;N;s/\n/ | /g' -e 's/^/| /'  -e 's/$/ |/' \
 | tr -d '"' \
 | sort -k1,1 \
 | sed -e 's/failing/failing   /' -e 's/problem/problem   /'

echo
echo '|| Id || Packaging || RepoURL ||'
curl -s 'sl64:9200/jper-account/_search?size=1000' \
 | jq  '.hits.hits[]._source|.id,.packaging[0],.sword.collection' \
 | sed -e 'N;N;s/\n/ | /g' \
 | egrep -v 'null$|""$' \
 | sort -k1,1 \
 | sed -e 's/^/| /'  -e 's/$/ |/' \
 | tr -d '"'
