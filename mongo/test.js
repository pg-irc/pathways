#!/usr/local/bin/mongo

connection  = new Mongo();
db = connection.getDB('test');

db.services.aggregate([
    { $match: { parent_id: "0"} },
    { $out: { db: 'test', coll: 'organizations'}}
])

db.services.aggregate([
    { $match: { parent_id : { $ne: "0"}}},
    { $lookup: {
        from: 'organizations',
        localField: 'parent_id',
        foreignField: '_id',
        as: 'parentOrg',
    }},
    { $project: {
        name: 1,
        description: 1,
        parent_id: 1,
        mailing_address: 1,
        physical_address: 1,
        _geoloc: 1,
        phone1: 1,
        phone2: 1,
        phone3: 1,
        phone4: 1,
        phone5: 1,
        parentOrg: 1,
        url: 1,
        'last_verified_on-x': 1,
    }},
    { $out: { db: 'test', coll: 'the_services'}},
]);

// Add organization props to services



// use aggregation to build the data as we need it
// use aggregation stage $out to write the result of the aggregation to a new collection,
//    this erases the current content of the collecion if it already exists
