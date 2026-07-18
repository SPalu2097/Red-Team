const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const DATA_FILE = path.join(__dirname, "data.json");

function readData() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
  } catch (err) {
    return [];
  }
}

function writeData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// POST data
app.post("/api/data", (req, res) => {
  const data = readData();

  const newEntry = {
    id: Date.now(),
    ...req.body,
    timestamp: new Date().toISOString()
  };

  data.push(newEntry);
  writeData(data);

  console.log("UUS:", newEntry);

  res.json({ ok: true, entry: newEntry });
});

// GET data
app.get("/api/data", (req, res) => {
  res.json(readData());
});

module.exports = app;