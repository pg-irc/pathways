# Read header from standard in
# Replace strings with algolia strings
# write header to standard out
# write the rest of the file to standard out
# TODO remove the phone numbers that just have {"isprivate":"FALSE"}
# to invoke:

# cat snippet.csv | \
# iconv -t utf8 --byte-subst="$" | \
# python fix_header.py | \
# csvtojson --ignoreEmpty=true \
#       --colParser='{"_geoloc.lng":"number","_geoloc.lat":"number"}'  > \
# snippet-fixed.csv
# mongoimport --db test --collection services --drop --jsonArray --file snippet-fixed.csv


# Mongo
# find all the records with zero parent id: { parent_id: "0" }
# find all the records with non-zero parent id: { parent_id: { "$ne":"0" } }


import sys


line_number = 0


def fix(word):
    header_name_map = {
        'ResourceAgencyNum': '_id',
        'ParentAgencyNum': 'parent_id',
        'PublicName': 'name',
        'AgencyDescription': 'description',
        'AlternateName': 'alternate_name',
        'EmailAddressMain': 'email',
        'WebsiteAddress': 'url',
        'LastVerifiedOn': 'last_verified_on-x',

        'MailingAddress1': 'mailing_address.address_1',
        'MailingAddress2': 'mailing_address.address_2',
        'MailingAddress3': 'mailing_address.address_3',
        'MailingAddress4': 'mailing_address.address_4',
        'MailingCity': 'mailing_address.city',
        'MailingStateProvince': 'mailing_address.state_province',
        'MailingPostalCode': 'mailing_address.postal_code',
        'MailingCountry': 'mailing_address.country',

        'PhysicalAddress1': 'physical_address.address_1',
        'PhysicalAddress2': 'physical_address.address_2',
        'PhysicalAddress3': 'physical_address.address_3',
        'PhysicalAddress4': 'physical_address.address_4',
        'PhysicalCity': 'physical_address.city',
        'PhysicalStateProvince': 'physical_address.state_province',
        'PhysicalPostalCode': 'physical_address.postal_code',
        'PhysicalCountry': 'physical_address.country',

        'Latitude': '_geoloc.lat',
        'Longitude': '_geoloc.lng',

        'Phone1Number': 'number',
        'Phone1Type': 'type',
        'Phone1Name': 'description',
        'PhoneFax': 'number',

    }

    add_phone_number_fields(header_name_map)
    to_map_from = word
    default_value = word
    return header_name_map.get(to_map_from, default_value)


def add_phone_number_fields(header_name_map):
    for index in range(1, 5):
        for phone_field in ['Phone1Number', 'Phone1Name', 'Phone1Description', 'Phone1IsPrivate', 'Phone1Type']:
            map_from = phone_field.replace('1', str(index))
            index_with_dot = str(index) + '.'
            map_to = phone_field.replace('1', index_with_dot).lower()
            header_name_map[map_from] = map_to


def fix_header(line):
    words = [fix(word) for word in line.split(',')]
    return ','.join(words)





for line in sys.stdin:
    if line_number == 0:
        print(fix_header(line.strip()))
    else:
        print(line.strip())
    line_number += 1

