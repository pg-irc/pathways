#!/bin/bash

while (( "$#" )); do
    if [ "$1" == "--bc211Path" ]
    then
        BC211Path=$2
        shift 2
    elif [ "$1" == "--newComersGuidePath" ]
    then
        NewcomersGuidePath=$2
        shift 2
    elif [ "$1" == "--recommendationsToAddPath" ]
    then
        ManualRecommendations=$2
        shift 2
    elif [ "$1" == "--outputDir" ]
    then
        CurrentDate=`date '+%Y'-'%m'-'%d'`
        OutputFile=$2/data-$CurrentDate.json
        shift 2
    else
        echo "$1: Invalid command argument"
        usage
        exit
    fi
done

usage() {
    echo
    echo "Usage:"
    echo
    echo "    $0 [arguments]"
    echo
    echo "Mandatory arguments:"
    echo
    echo "    --bc211Path"
    echo "                The path to the BC211 data set in XML iCarol format."
    echo
    echo "    --newComersGuidePath"
    echo "                The path to the Newcomers' guide content."
    echo
    echo "    --recommendationsToAddPath"
    echo "                The path to the folder containing files with manual recommendations."
    echo
    echo "    --outputDir"
    echo "                The directory where the output json file will be placed."
    echo
}

validateFilePath () {
    if [ "$1" == "" ]; then
        echo "Missing a required argument: $2"
        usage
        exit
    fi
    if [ ! -f "$1" ]; then
        echo "$1: not a file"
        usage
        exit
    fi
}

validateDirectoryPath () {
    if [ "$1" == "" ]; then
        echo "Missing a required argument: $2"
        usage
        exit
    fi
    if [ ! -d "$1" ]; then
        echo "$1: not a directory"
        usage
        exit
    fi
}

validateNewcomersGuidePath () {
    if [ "$NewcomersGuidePath" == "" ]; then
        echo "Missing required argument: Newcomers Guide path"
        usage
        exit
    fi
    if [ ! -d $NewcomersGuidePath ]; then
        echo "$NewcomersGuidePath: directory does not exist"
        usage
        exit
    fi
}

validateOutputFile () {
    if [ "$OutputFile" == "" ]; then
        echo "Missing a required argument for output"
        usage
        exit
    fi
    if [ -f $OutputFile ]; then
        echo "$OutputFile: Output file already exists"
        exit
    fi
}


validateFilePath "$BC211Path" "BC 211 data"

validateNewcomersGuidePath

validateDirectoryPath "$ManualRecommendations" "Recommendations to add"

validateOutputFile

echo "About to reinitialize database with data from:"
echo "BC211 data at:             $BC211Path"
echo "Newcomers data at:         $NewcomersGuidePath"
echo "Manual recommendations:    $ManualRecommendations"
echo "Output file:               $OutputFile"
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
./manage.py compute_text_similarity_scores --related_topics 3 --related_services 0 $NewcomersGuidePath
checkForSuccess "compute similarity scores"

echo "adding manual similarity scores ..."
./manage.py manage_manual_recommendations $ManualRecommendations
checkForSuccess "add manual similarity scores"

echo "saving database content to $OutputFile ..."
./manage.py dumpdata --natural-foreign --exclude auth.permission --exclude contenttypes --indent 4 > $OutputFile
checkForSuccess "saving database content"
