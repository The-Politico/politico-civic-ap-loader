# parse args
while getopts b:d:f:l:o:zt option
do
  case "${option}"
    in
    b) BUCKET=${OPTARG};;
    l) LEVEL=${OPTARG};;
    o) OUTPUT=${OPTARG};;
  esac
done

# deploy to s3
if [ $BUCKET ] ; then
  aws s3 cp ${OUTPUT}/election-results/$LEVEL s3://${BUCKET}/election-results/2018/ --recursive --acl "public-read" --cache-control "max-age=5"
fi
