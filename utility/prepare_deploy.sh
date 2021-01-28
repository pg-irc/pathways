#!/bin/bash

fail() {
    exit -1
}

while (( "$#" )); do
    if [ "$1" == "--bc211Path" ]
    then
        BC211Path=$2
        shift 2
    elif [ "$1" == "--cityLatLongs" ]
    then
        CityLatLongs=$2
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
        fail
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
    echo "                The path to the BC211 data set in CSV iCarol format."
    echo
    echo "    --cityLatLongs"
    echo "                The path to the city and latlong dictionary in CSV format."
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
        fail
    fi
    if [ ! -f "$1" ]; then
        echo "$1: not a file"
        usage
        fail
    fi
}

validateDirectoryPath () {
    if [ "$1" == "" ]; then
        echo "Missing a required argument: $2"
        usage
        fail
    fi
    if [ ! -d "$1" ]; then
        echo "$1: not a directory"
        usage
        fail
    fi
}

validateNewcomersGuidePath () {
    if [ "$NewcomersGuidePath" == "" ]; then
        echo "Missing required argument: Newcomers Guide path"
        usage
        fail
    fi
    if [ ! -d $NewcomersGuidePath ]; then
        echo "$NewcomersGuidePath: directory does not exist"
        usage
        fail
    fi
}

validateOutputFile () {
    if [ "$OutputFile" == "" ]; then
        echo "Missing a required argument for output"
        usage
        fail
    fi
    if [ -f $OutputFile ]; then
        echo "$OutputFile: Output file already exists"
        fail
    fi
}


validateFilePath "$BC211Path" "BC 211 data"

validateFilePath "$CityLatLongs" "Latlong Replacement file"

validateNewcomersGuidePath

validateDirectoryPath "$ManualRecommendations" "Recommendations to add"

validateOutputFile

echo "About to reinitialize database with data from:"
echo "BC211 data at:                $BC211Path"
echo "Latlong replacement file at:  $CityLatLongs"
echo "Newcomers data at:            $NewcomersGuidePath"
echo "Manual recommendations:       $ManualRecommendations"
echo "Output file:                  $OutputFile"
read -p "Enter to continue, Ctrl-C to abort "

checkForSuccess () {
    if [ "$?" != "0" ]
    then
        echo "failed to $1"
        fail
    fi
}

echo "updating BC211 version string in bc211/__init.py__"
echo "__bc211_version__ = '$CurrentDate'" > ./bc211/__init__.py

./manage.py reset_db
checkForSuccess "reset database"

./manage.py migrate
checkForSuccess "migrate database"

echo "converting iCarol BC-211 CSV to open referral standard..."
mkdir -p ./open_referral_csv_files
./manage.py convert_icarol_csv $BC211Path ./open_referral_csv_files
checkForSuccess "convert iCarol BC-211 data into open referral standard"

echo "importing BC-211 open referral csv data into the database..."
./manage.py import_open_referral_csv ./open_referral_csv_files --cityLatLongs $CityLatLongs
checkForSuccess "import Bc-211 open referral data into the database"

echo "converting organizationAsService CSV to open referral standard..."
mkdir -p ./open_referral_csv_files_org_services
./manage.py convert_icarol_csv ../content/organizationAsServices.csv ./open_referral_csv_files_org_services
checkForSuccess "convert organizationAsService data into open referral standard"

echo "importing organizationAsService open referral csv data into the database..."
./manage.py import_open_referral_csv ./open_referral_csv_files_org_services --cityLatLongs $CityLatLongs
checkForSuccess "import organizationAsService open referral data into the database"

echo "converting additional libraries CSV to open referral standard..."
mkdir -p ./open_referral_csv_files_libraries
./manage.py convert_icarol_csv ../content/additionalLibraries.csv ./open_referral_csv_files_libraries
checkForSuccess "convert additional libraries data into open referral standard"

echo "importing additional libraries open referral csv data into the database..."
./manage.py import_open_referral_csv ./open_referral_csv_files_libraries --cityLatLongs $CityLatLongs
checkForSuccess "import additional libraries open referral data into the database"

./manage.py import_newcomers_guide $NewcomersGuidePath
checkForSuccess "import newcomers guide data into the database"

echo "computing similarity scores ..."
./manage.py compute_text_similarity_scores --related_topics 3 --related_services 0 $NewcomersGuidePath
checkForSuccess "compute similarity scores"

echo "adding manual similarity scores ..."
./manage.py manage_manual_recommendations $ManualRecommendations
checkForSuccess "add manual similarity scores"

echo "saving database content to $OutputFile ..."
./manage.py dumpdata --natural-foreign --exclude auth.permission --exclude contenttypes --indent 4 > $OutputFile
checkForSuccess "saving database content"
