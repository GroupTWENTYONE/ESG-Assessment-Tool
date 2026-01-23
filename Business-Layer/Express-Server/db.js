const { MongoClient } = require("mongodb");

const uri = "mongodb://root:password@mongodb:27017/?authSource=admin&readPreference=primary&appname=n8n&ssl=false";
const client = new MongoClient(uri);

let db;

async function connectDB(){
  if(!db){
    await client.connect();
    db = client.db("company_db");
  }
  return db;
}

module.exports = { connectDB };
