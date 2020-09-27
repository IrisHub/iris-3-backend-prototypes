#!/bin/bash

POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -n|--name)
	NAME="$2"
	shift
	shift
	;;
    -d|--deployment)
    DEPLOY="$2"
    shift
    shift
    ;;
	-p|--permission)
	PERM="$2"
	PERM="${PERM:-default}"
	shift
	shift
	;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

pip install -r --target ./package requirements.txt
cd package
zip -r9 ${OLDPWD}/function.zip
cd ${OLDPWD}
zip -g function.zip "${POSITIONAL[@]}"
if [ "${DEPLOY}" = launch ]
then
    case "${PERM}" in
        "default") aws lambda create-function --function-name "${NAME}" --runtime python3.8 --zip-file fileb://function.zip --handler main.event_handler --role arn:aws:iam::180390500254:role/lambda_default
        ;;
        "dynamodb_full") aws lambda create-function --function-name "${NAME}" --runtime python3.8 --zip-file fileb://function.zip --handler main.event_handler --role arn:aws:iam::180390500254:role/lambda_dynamodb_full
        ;;
        "s3_dynamodb_full") aws lambda create-function --function-name "${NAME}" --runtime python3.8 --zip-file fileb://function.zip --handler main.event_handler --role arn:aws:iam::180390500254:role/lambda_s3_dynamodb_full
        ;;
    esac
fi
if [ "${DEPLOY}" = update ]
then
    aws lambda update-function-code --function-name "${NAME}" --zip-file fileb://function.zip
fi
rm ./function.zip
rm -rf ./package
