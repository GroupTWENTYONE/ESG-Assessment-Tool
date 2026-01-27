db = db.getSiblingDB("company_db");
db.createCollection("companies");

load("/docker-entrypoint-initdb.d/company_db.companies.js");

db.companies.insertMany(companies);
