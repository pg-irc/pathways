#!/bin/bash

if [ "$#" != "5" ]
then
    echo "Expected five arguments: BC211 file path, Newcomers Guide folder path, Topics to remove, Manual recommendations, output file path"
    exit
fi

BC211Path=$1
NewcomersGuidePath=$2
TopicsToRemove=$3
ManualRecommendations=$4
CurrentDate=`date '+%Y'-'%m'-'%d'`
OutputFile=$5/$CurrentDate.json

if [ ! -f $BC211Path ]; then
    echo "$BC211Path: BC211 data file not found"
    exit
fi

if [ ! -d $NewcomersGuidePath ]; then
    echo "$NewcomersGuidePath: Newcomers Guide content not found"
    exit
fi

if [ ! -f $ManualRecommendations ]; then
    echo "$ManualRecommendations: Manual recommendations not found"
    exit
fi

if [ ! -f $TopicsToRemove ]; then
    echo "$TopicsToRemove: topics to remove not found"
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

echo "About to reinitialize database with data from:"
echo "BC211 data at:           $BC211Path"
echo "Newcomers data at:       $NewcomersGuidePath"
echo "Topics to not recommend: $TopicsToRemove"
echo "Manual recommendations:  $ManualRecommendations"
echo "Path to place output file eg ../build/ : $OutputFile"
read -p "Enter to continue, Ctrl-C to abort "

checkForSuccess () {
    if [ "$?" != "0" ]
    then
        echo "failed to $1"
        exit
    fi
}

echo "updating BC211 version string in bc211/__init.py__"
echo "__bc211_version__ = '$CurrentDate'" > ./bc211/__init__.py

./manage.py reset_db
checkForSuccess "reset database"

./manage.py migrate
checkForSuccess "migrate database"

echo "importing BC-211 data ..."
./manage.py import_bc211_data $BC211Path
checkForSuccess "import BC211 data"

./manage.py import_newcomers_guide --save_topics_to_db $NewcomersGuidePath
checkForSuccess "create newcomers guide fixtures"

echo "computing similarity scores ..."
./manage.py compute_text_similarity_scores --related_topics 3 --related_services 100 $NewcomersGuidePath
checkForSuccess "compute similarity scores"

echo "adding manual similarity scores ..."
./manage.py set_manual_similarity_scores $ManualRecommendations
checkForSuccess "add manual similarity scores"

echo "removing invalid similarity scores ..."
./manage.py remove_recommendations_for_topics $TopicsToRemove
checkForSuccess "remove similarity scores"

./manage.py dumpdata --natural-foreign --exclude auth.permission --exclude contenttypes --indent 4 > $OutputFile

checkForSuccess "dump data"
