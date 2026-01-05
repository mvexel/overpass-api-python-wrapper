#!/usr/bin/env node

/*
Generate GeoJSON fixtures using osmtogeojson.
Usage: node tools/osmtogeojson_fixture.js input.json output.geojson
*/

const fs = require("fs");
const osmtogeojson = require("osmtogeojson");

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
