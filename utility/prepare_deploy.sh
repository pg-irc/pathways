#!/bin/bash

if [ "$#" != "3" ]
then
    echo "Expected three arguments: BC211 file path, Newcomers Guide folder path, output file path"
    exit
fi

BC211Path=$1
NewcomersGuidePath=$2
OutputFile=$3

if [ ! -f $BC211Path ]; then
    echo "$BC211Path: BC211 data file not found"
    exit
fi

if [ ! -d $NewcomersGuidePath ]; then
    echo "$NewcomersGuidePath: Newcomers Guide content not found"
    exit
fi

if [ -f $OutputFile ]; then
    echo "$OutputFile: Output file already exists"
    exit
fi

if [ "${OutputFile:(-5)}" != ".json" ]; then
    echo "$OutputFile: Output file must end in .json"
    exit
fi

echo "About to reinitialize database with BC211 data at"
echo "$BC211Path and Newcomers Guide data at"
echo "$NewcomersGuidePath, saving result to"
echo "$OutputFile for upload"
read -p "Enter to continue, Ctrl-C to abort "

checkForSuccess () {
    if [ "$?" != "0" ]
    then
        echo "failed to $1"
        exit
    fi
}

./manage.py reset_db
checkForSuccess "reset database"

./manage.py migrate
checkForSuccess "migrate database"

echo "importing BC-211 data ..."
./manage.py import_bc211_data $BC211Path
checkForSuccess "import BC211 data"

echo "computing similarity scores ..."
./manage.py compute_text_similarity_scores --related_tasks 3 --related_services 20 $NewcomersGuidePath
checkForSuccess "compute similarity scores"

./manage.py dumpdata > $OutputFile
checkForSuccess "dump data"
