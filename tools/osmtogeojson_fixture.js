#!/usr/bin/env node

/*
Generate GeoJSON fixtures using osmtogeojson.
Usage: node tools/osmtogeojson_fixture.js input.json output.geojson
*/

const fs = require("fs");
let osmtogeojson;
try {
  osmtogeojson = require("osmtogeojson");
} catch (err) {
  const { execSync } = require("child_process");
  const path = require("path");
  try {
    const globalRoot = execSync("npm root -g", { encoding: "utf-8" }).trim();
    osmtogeojson = require(path.join(globalRoot, "osmtogeojson"));
  } catch (err2) {
    console.error("osmtogeojson not found. Install with: npm install --global osmtogeojson");
    process.exit(2);
  }
}

if (process.argv.length < 4) {
  console.error("Usage: node tools/osmtogeojson_fixture.js input.json output.geojson");
  process.exit(2);
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];

const raw = fs.readFileSync(inputPath, "utf-8");
const data = JSON.parse(raw);
const geojson = osmtogeojson(data);

fs.writeFileSync(outputPath, JSON.stringify(geojson, null, 2));
console.log(`Wrote ${outputPath}`);
