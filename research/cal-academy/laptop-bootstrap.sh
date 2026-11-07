#!/usr/bin/env bash
# Pulls the open / public-domain data for the Cal Academy project into ./data.
# Run from the repo root on the laptop:  bash research/cal-academy/laptop-bootstrap.sh
set -euo pipefail
D="${1:-data/cal-academy}"; mkdir -p "$D"/{lidar2023,lidar2010,dem,vector,drawings,maps,archdaily}
UA="ep3-research/1.0"
get(){ [ -s "$2" ] || curl -sSL --retry 3 -A "$UA" -o "$2" "$1" && echo "ok  $2"; }

echo "== 2023 USGS lidar (public domain)"
get https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/metadata/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/reports/CA_SanFrancisco_LiDAR_ProjectReport.pdf "$D/lidar2023/project_report.pdf"
for t in 04650260 04600260 04650255 04600255 04650265 04600265; do
  get "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/LAZ/USGS_LPC_CA_SanFrancisco_B23_${t}.laz" "$D/lidar2023/USGS_LPC_CA_SanFrancisco_B23_${t}.laz" || true
  get "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/OPR/Projects/CA_SanFrancisco_B23/CA_SanFrancisco_1_B23/TIFF/USGS_OPR_CA_SanFrancisco_B23_${t}.tif" "$D/dem/USGS_OPR_CA_SanFrancisco_B23_${t}.tif" || true
done
get https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SanFrancisco_B23/TIFF/USGS_1M_10_x54y418_CA_SanFrancisco_B23.tif "$D/dem/USGS_1M_10_x54y418.tif"
get https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SanFrancisco_B23/TIFF/USGS_1M_10_x54y419_CA_SanFrancisco_B23.tif "$D/dem/USGS_1M_10_x54y419.tif"

echo "== 2010 lidar (NOAA COPC, public domain)"
get https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100512_ca_arra_goldengate_0915.copc.laz "$D/lidar2010/gg2010_0915.copc.laz"
get https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/geoid18/5007/20100529_ca_arra_goldengate_0875.copc.laz "$D/lidar2010/gg2010_0875.copc.laz"

echo "== EPT clip of the 2023 cloud (needs PDAL)"
cat > "$D/lidar2023/ept_clip.json" <<'JSON'
[
  {"type":"readers.ept","filename":"https://s3-us-west-2.amazonaws.com/usgs-lidar-public/CA_SanFrancisco_1_B23/ept.json","bounds":"([-13633521,-13632407],[4546633,4547408])","requests":16},
  {"type":"filters.range","limits":"Classification![7:7],Classification![18:18]"},
  {"type":"filters.reprojection","in_srs":"EPSG:3857","out_srs":"EPSG:26910"},
  {"type":"writers.copc","filename":"calacademy_2023_utm10.copc.laz"}
]
JSON
if command -v pdal >/dev/null; then (cd "$D/lidar2023" && pdal pipeline ept_clip.json && echo "ok  EPT clip"); else echo "skip EPT clip: install PDAL (conda install -c conda-forge pdal) or run scripts/lidar_ept_fetch.py"; fi

echo "== Vectors"
get "https://overpass-api.de/api/map?bbox=-122.4740,37.7660,-122.4600,37.7740" "$D/vector/site.osm" || true
get "https://data.sfgov.org/api/geospatial/ynuv-fyni?method=export&format=GeoJSON" "$D/vector/sf_building_footprints.geojson" || true
get "https://data.sfgov.org/api/geospatial/3nje-yn2u?method=export&format=GeoJSON" "$D/vector/sf_parks.geojson" || true

echo "== Drawings (copyright RPBW, reference only)"
get https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences.pdf "$D/drawings/fondazione_catalogue.pdf"
get https://www.fondazionerenzopiano.org/en/page/california-california-academy-of-sciences/download-book "$D/drawings/fondazione_booklet.pdf"
for n in 235 352 289 613 337 243 240 336 275 328 279 285 311 354 355 303 304; do
  get "https://www.fondazionerenzopiano.org/en/project/california-academy-of-sciences/drawing-${n}.pdf" "$D/drawings/drawing-${n}.pdf"
done
get https://cdn.sanity.io/images/zi3g9jaq/production/9037e5ae3a056f89e4e311055a5b8f15e203f05c-1400x343.jpg "$D/drawings/rpbw_long_section.jpg"
get https://cdn.sanity.io/images/zi3g9jaq/production/4c998f3c54927ae6e708e8583119c19361fd92db-1320x1023.jpg "$D/drawings/rpbw_roof_section_detail.jpg"
curl -sSL -A "Mozilla/5.0" https://www.archdaily.com/6810/california-academy-of-sciences-renzo-piano \
 | grep -oE 'https://images\.adsttc\.com/media/images/[^"'"'"' ?]+/medium_jpg/stringio\.jpg' | sort -u | sed 's/medium_jpg/large_jpg/' \
 | awk '{printf "%s\n", $0}' | while read -r u; do n=$(echo "$u" | cut -d/ -f7-8 | tr / _); get "$u" "$D/archdaily/ad_${n}.jpg"; done

echo "== Historic maps (David Rumsey, CC BY-NC-SA)"
get "https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~1576~170034/full/full/0/default.jpg" "$D/maps/rumsey_1896_blum_golden_gate_park.jpg"
get "https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~313936~90082810/6550,6075,10500,9550/4000,/0/default.jpg" "$D/maps/rumsey_1948_aerial_sheet131_concourse_4k.jpg"
get "https://www.davidrumsey.com/luna/servlet/iiif/RUMSEY~8~1~214199~5501554/full/full/0/default.jpg" "$D/maps/rumsey_1905_sanborn_vol6_index.jpg"

echo "== Done. Manual items (accounts / browser): see 02-downloads-manifest.md sections C, D4, E."
