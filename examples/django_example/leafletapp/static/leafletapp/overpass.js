var map;
var overpassLayer;

function init() {
	// Initialize the map
	map = L.map('map').setView([51.505, -0.09], 16);
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osmLayer = new L.TileLayer(
		osmUrl, {
			minZoom: 14,
			maxZoom: 18,
			attribution:
			osmAttrib});
	overpassLayer = new L.geoJson();
	map.addLayer(osmLayer, overpassLayer);
};

function loadFromOverpass() {
	console.log('loadFromOverpass');
	var key = $("#key").val();
	var value = $("#value").val() || "---";
	var osmtype = $("#osmtype").val();
	var bounds = map.getBounds();
	var url = 'overpass/' + osmtype + '/' + key + '/' + value + '/' + [
			bounds.getSouthWest().lat,
			bounds.getSouthWest().lng,
			bounds.getNorthEast().lat,
			bounds.getNorthEast().lng,
		].join('/');
	console.log(url);
	// Load --> Wait
	$("#load").unbind("click").prop('disabled', true).text("Wait...");
	$.ajax(url, {
		success: function(data) {
			overpassLayer.clearLayers();
			overpassLayer.addData(data);
			map.addLayer(overpassLayer);
			$('#message').text(data.features.length + ' features loaded');
			$("#load").click(loadFromOverpass).prop('disabled', false).text("Load!");
		}
	});
};