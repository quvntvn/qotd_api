const functions = require("firebase-functions");
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());

// Ajoutez vos routes et gestionnaires d'API ici
app.get("/example", (req, res) => {
  res.send("Hello from Firebase Cloud Functions!");
});

exports.api = functions.https.onRequest(app);
