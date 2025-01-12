db = db.getSiblingDB("company_db");

// Collection `companies` erstellen und initialisieren
db.createCollection("companies");

// Beispiel-Daten hinzufügen
db.companies.insertMany([
  {
    name: "Amazon",
    ticker: "AMZN",
    esg_components: {
      environment: [],
      social: [],
      governance: []
    }
  },
  {
    name: "Google",
    ticker: "GOOGL",
    esg_components: {
      environment: [],
      social: [],
      governance: []
    }
  }
]);
