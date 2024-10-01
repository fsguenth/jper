#! /bin/bash

REPO=""
ALL=N
PROGNAME=`basename $0`
TMPFILE="/tmp/${PROGNAME}.tmp"

UPLOADPRGM="post-to-confluence"  
SPACE="DGS"
PAGE="Lizenzen im Produktivsystem"

help() {
    cat << EOT

$PROGNAME - show licenses

usage: $PROGNAME [-a][-e EZBID ] -h
 -e EZBID   show licensses for a repository
 -a         show all licenses
 -c         upload all licenses to Confluence

EOT
}

# working on a local tunnel
if [ `hostname` == "probibw41" ]; then
    ESHOST="localhost"
fi

# check ESHOST environment variable
if [ -z "$ESHOST" ] ; then
    echo; echo "ERROR: ESHOST environment variable missing"; help; exit 1 ;
fi

ES="http://${ESHOST}:9200"
HTML='N'

# parse arguments
while getopts "ache:" option; do
   case ${option} in
    e)  REPO=$OPTARG ;;
    a)  ALL=Y;;
    h)  help; exit 1 ;;
    c)  ALL=Y; HTML=Y;;
    *)  echo; echo "ERROR: invalid agrument or option"; help; exit 1 ;;
   esac
done 

if [ "$ALL" == "N" ] && [ -z "$REPO" ]; then
    help
    exit 1
fi


if [ "$ALL" == "Y" ]; then
  echo ES: $ES
  if [ "$HTML" == "Y" ]; then
    echo '<table>' > $TMPFILE
    echo '<tr><th> Name </th><th> Id </th><th> Type </th></tr>' >> $TMPFILE
    curl -s "${ES}/jper-license/_search?size=50" | jq '.hits.hits[]._source|.name,.id,.type ' | sed -e 's/^"//' -e 's/"$//' | sed -e 'N;N;s#\n#</td><td>#g' -e 's#^#<tr><td>#'  -e 's#$#</td></tr>#' >> $TMPFILE
    echo '</table>' >> $TMPFILE
    echo '<table>'  >> $TMPFILE
    echo '<tr><th> Particpants-ID </th><th> License-Id </th><th> Identifier </th></tr>' >> $TMPFILE
    curl -s "$ES/jper-alliance/_search?size=50" | jq '.hits.hits[]._source|.id,.license_id,.identifier[].id' | sed -e 's/^"//' -e 's/"$//' | sed -e 'N;N;s#\n#</td><td>#g' -e 's#^#<tr><td>#'  -e 's#$#</td></tr>#' >> $TMPFILE
    echo '</table>' >> $TMPFILE
    echo 'generated on' >> $TMPFILE
    date >> $TMPFILE
    $UPLOADPRGM -s $SPACE -t "$PAGE" < $TMPFILE
  else
    echo '| Name | Id | Type |'
    curl -s "${ES}/jper-license/_search?size=50" | jq '.hits.hits[]._source|.name,.id,.type ' | sed -e 's/^"//' -e 's/"$//' | sed -e 'N;N;s/\n/ | /g' -e 's/^/| /'  -e 's/$/ |/'

    echo
    echo '| Particpants-ID | License-Id | Identifier |'
    curl -s "$ES/jper-alliance/_search?size=50" | jq '.hits.hits[]._source|.id,.license_id,.identifier[].id' | sed -e 's/^"//' -e 's/"$//' | sed -e 'N;N;s/\n/ | /g' -e 's/^/| /'  -e 's/$/ |/'
  fi
  exit 0
fi

if [ -n "$REPO" ]; then
  echo REPO=$REPO
  echo '| License-Id | Identifier |'
  curl -s "$ES/jper-alliance/_search?size=50&q=$REPO" | jq '.hits.hits[]._source|.license_id,.identifier[].id'  | sed -e 's/^"//' -e 's/"$//' | sed -e 'N;s/\n/ | /g' -e 's/^/| /'  -e 's/$/ |/'
fi
