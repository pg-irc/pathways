-- use csvtojson (https://github.com/Keyang/node-csvtojson/), not csv2json

-- sudo npm install --global csvtojson

-- psql -d pathways_local -F $',' -A -t -c 'select location_id, phone_number, phone_number_type_id from phone_at_location_phoneatlocation' > phones_data.csv
-- psql -d pathways_local -F $',' -A -t -c "select s.service_id, t.name from services_service_taxonomy_terms as s, taxonomies_taxonomyterm as t where s.taxonomyterm_id=t.id" > taxonomy_data.csv
-- ubuntu: psql -d pathways_local -F $',' -A -f utility/algolia/dump_services.sql | head -n -1 |                     csvtojson --colParser='{"_geoloc.lng":"number","_geoloc.lat":"number","organization.service_count":"number"}' > services.json
-- mac   : psql -d pathways_local -F $',' -A -f utility/algolia/dump_services.sql | tail -r | tail -n +2 | tail -r | csvtojson --colParser='{"_geoloc.lng":"number","_geoloc.lat":"number","organization.service_count":"number"}' > services.json
-- python utility/algolia/add_phone_numbers_to_services.py phones_data.csv taxonomy_data.csv services.json output_data.json

-- Column names _geoloc.lng and _geoloc.lat are special. csvtojson understands to convert this to
-- "_geoloc":{"lng":-122.724,"lat":49.110044}. The --colParser option define the lat and long to be
-- numbers, rather than strings. With the special names _geoloc, lng and lat, Algolia understands
-- this to mean a geolocation point.

select distinct
	service.id as service_id,
	'"' || serviceStrings.name || '"' as service_name,
	left(regexp_replace(serviceStrings.description, E'[\\n\\r\\t;,]+', ' ', 'g' ), 5000) as service_description,
    service.last_verified_date as last_verified_date,
	serviceStrings.alternate_name as alternate_name,
	organization.id as "organization.id",
	'"' || organizationStrings.name || '"' as "organization.name",
	organization.website as "organization.website",
	organization.email as "organization.email",
	counts.service_count as "organization.service_count",
	regexp_replace(address.address, E'[\\n\\r;,]+', ' ', 'g' ) as "address.address",
	'"' || address.city || '"' as "address.city",
	'"' || address.state_province || '"' as "address.state_province",
	'"' || address.postal_code || '"' as "address.postal_code",
	address.country as "address.country",
	ST_X(location.point) as "_geoloc.lng",
	ST_Y(location.point) as "_geoloc.lat",
	location.id as "location_id"
from
	services_service as service,
	services_service_translation as serviceStrings,
	locations_location as location,
	locations_serviceatlocation as servicesAtLocation,
	locations_locationaddress as locationAddress,
	addresses_address as address,
	organizations_organization as organization,
	organizations_organization_translation as organizationStrings,
	(select
		count(s.id) as service_count,
		o.id as organization_id
	from
		services_service as s,
		organizations_organization as o
	where
		s.organization_id=o.id
	group by
		o.id
	) as counts
where
	service.id=serviceStrings.master_id and
	service.id=servicesAtLocation.service_id and
	location.id=servicesAtLocation.location_id and
	servicesAtLocation.location_id=locationAddress.location_id and
	locationAddress.address_id=address.id and
	locationAddress.address_type_id='physical_address' and
	organization.id=service.organization_id and
	organization.id=organizationStrings.master_id and
	organization.id=counts.organization_id
order by
	service_name;
