// Building layout in game units (metres). Derived from the 2023 USGS lidar frame
// (assets/site_meta.json) plus RPBW drawings. X = building long axis (east is -X),
// Y = up (0 = main floor at grade, 77.05 m NAVD88), Z = short axis (+Z = concourse / north side).
// Interior placement of halls and tanks is approximate; see game/README.md.
export const L = {
  bbox: { x0: -84.5, x1: 84.5, z0: -54.5, z1: 55.5 },
  levels: { b2: -12.5, aquarium: -7.6, main: 0, mezz: 4.6, roofSlab: 9.6, deck: 11.45, crown: 19.3 },
  domeR: 13.7,
  planetarium: { x: 29, y: 5.6, z: 4, name: 'Morrison Planetarium (flooded)' },   // west dome
  rainforest:  { x: -29, y: 5.6, z: 4, name: 'Osher Rainforest (dry, airlock)' }, // east dome
  piazza: { x: 0, z: 3, w: 36, d: 28 },
  skylight: { x: 0, z: 3, w: 20, d: 27.4 },   // 66 x 90 ft opening, glass retracted
  reefTank: { x: -52, z: -28, w: 14, d: 10, top: 0, bottom: -7.6, name: 'Philippine Coral Reef' },
  lagoon:   { x: -8, z: -30, w: 22, d: 9, top: 0, bottom: -1.6, name: 'Reef Lagoon' },
  calCoast: { x: 30, z: -38, w: 18, d: 8, top: -1.0, bottom: -7.6, name: 'California Coast (cold)' },
  swamp:    { x: 14, z: 28, r: 6, top: 0, bottom: -7.6, name: 'The Swamp (sealed)' },
  amazon:   { x: -29, z: 4, r: 11, top: -1.0, bottom: -7.6, name: 'Amazon Flooded Forest (sealed)' },
  africanHall: { x0: 56, x1: 84, z0: -54, z1: 18, vaultTop: 9.2, name: 'African Hall' },
  penguins: { x0: 56, x1: 84, z0: -54, z1: -42, name: 'Penguins (sealed)' },
  cafe:     { x0: 56, x1: 84, z0: 24, z1: 55, name: 'Academy Café (dry)', door: { x: 84.5, z: 40 } },
  terrace:  { x0: -104, x1: -86, z0: -12, z1: 12, name: 'The Terrace (dry)', door: { x: -104, z: 0 } },
  airlock:  { x0: -17, x1: -11, z0: 0, z1: 8, y0: 0, y1: 3.2, name: 'Rainforest airlock', outer: { x: -11, z: 4 }, inner: { x: -17, z: 4 } },
  researchWing: { x0: -84, x1: 56, z0: -54.5, z1: -42, name: 'Research / collections / admin (sealed)' },
  lss: { x0: -84, x1: 84, z0: -54.5, z1: 55.5, y0: -12.5, y1: -7.6, name: 'Life-support + mechanical B2 (sealed)' },
  liftTower: { x: -92, z: 16, r: 2.6, y0: 0, y1: 11.45, name: 'Dive Tower (exterior lift, Terrace to roof)' },
  westStair: { x: 88, z: 40, w: 3, d: 8, y0: 0, y1: 11.45, name: 'Exterior stair (café terrace to roof)' },
  hatches: [
    { name: 'Planetarium porthole (dive entry)', x: 29, y: 19.3, z: 4, r: 2.4, into: 'planetarium', wet: true },
    { name: 'Rainforest hatch (airlock, dry)', x: -29, y: 19.3, z: 4, r: 2.4, into: 'rainforest', wet: false },
    { name: 'Piazza skylight (retracted)', x: 0, y: 9.6, z: 3, r: 10, into: 'piazza', wet: true },
  ],
  columnGrid: 7.3,
  waterLayers: [
    { name: 'SUNLIT · reef',      minY: -2.0, color: 0x1a8fa8, fogNear: 2, fogFar: 70, light: 1.0 },
    { name: 'MID-WATER · halls',  minY: -6.5, color: 0x0f4f78, fogNear: 2, fogFar: 42, light: 0.6 },
    { name: 'TWILIGHT ZONE',      minY: -99,  color: 0x071a33, fogNear: 1, fogFar: 20, light: 0.25 },
  ],
  // Flood-zone plan for the map overlay. kind: flood | dry | sealed | airlock | outside
  zones: [
    { name: 'Piazza + main-floor circulation', kind: 'flood', x0: -56, x1: 56, z0: -42, z1: 55.5 },
    { name: 'Steinhart Aquarium level', kind: 'flood', x0: -84, x1: 56, z0: -42, z1: 55.5, level: 'aquarium' },
    { name: 'Morrison Planetarium', kind: 'flood', circle: { x: 29, z: 4, r: 13.7 } },
    { name: 'African Hall', kind: 'flood', x0: 56, x1: 84, z0: -42, z1: 18 },
    { name: 'Philippine Coral Reef (glass retracted)', kind: 'flood', x0: -59, x1: -45, z0: -33, z1: -23 },
    { name: 'Reef Lagoon (glass retracted)', kind: 'flood', x0: -19, x1: 3, z0: -34.5, z1: -25.5 },
    { name: 'Osher Rainforest', kind: 'dry', circle: { x: -29, z: 4, r: 13.7 } },
    { name: 'Rainforest airlock', kind: 'airlock', x0: -17, x1: -11, z0: 0, z1: 8 },
    { name: 'Academy Café', kind: 'dry', x0: 56, x1: 84, z0: 24, z1: 55 },
    { name: 'The Terrace', kind: 'dry', x0: -104, x1: -86, z0: -12, z1: 12 },
    { name: 'Dive Tower lift (exterior)', kind: 'route', circle: { x: -92, z: 16, r: 2.6 } },
    { name: 'Exterior stair at café', kind: 'route', x0: 86.5, x1: 89.5, z0: 36, z1: 44 },
    { name: 'Roof deck (dry, public)', kind: 'route', x0: -84.5, x1: 84.5, z0: -54.5, z1: 55.5, level: 'roof' },
    { name: 'Penguins', kind: 'sealed', x0: 56, x1: 84, z0: -54, z1: -42 },
    { name: 'The Swamp (alligator)', kind: 'sealed', circle: { x: 14, z: 28, r: 6 } },
    { name: 'Amazon tank (freshwater, under dome)', kind: 'sealed', circle: { x: -29, z: 4, r: 11 }, level: 'aquarium' },
    { name: 'California Coast (cold)', kind: 'sealed', x0: 21, x1: 39, z0: -42, z1: -34 },
    { name: 'Research / collections / admin / Project Lab', kind: 'sealed', x0: -84, x1: 56, z0: -54.5, z1: -42 },
    { name: 'Store / restrooms / theatres / stairs above L0', kind: 'sealed', x0: 56, x1: 84, z0: 18, z1: 24 },
  ],
};
export function insideFootprint(x, z, pad = 0) {
  return x > L.bbox.x0 - pad && x < L.bbox.x1 + pad && z > L.bbox.z0 - pad && z < L.bbox.z1 + pad;
}
export function inBox(b, x, y, z, y0 = -99, y1 = 99) {
  return x > b.x0 && x < b.x1 && z > b.z0 && z < b.z1 && y > y0 && y < y1;
}
export function layerAt(y) {
  for (const l of L.waterLayers) if (y > l.minY) return l;
  return L.waterLayers[L.waterLayers.length - 1];
}
const d2 = (x, y, z, c) => (x - c.x) ** 2 + (y - c.y) ** 2 + (z - c.z) ** 2;
// Dry zones: returns a zone id if (x,y,z) is in air inside a sealed room, else null.
export function dryZone(x, y, z) {
  if (d2(x, y, z, L.rainforest) < (L.domeR - 0.6) ** 2 && y > L.amazon.top) return 'rainforest';
  if (inBox(L.cafe, x, y, z, -0.5, L.levels.roofSlab)) return 'cafe';
  if (inBox(L.terrace, x, y, z, -0.5, 6)) return 'terrace';
  if (inBox(L.airlock, x, y, z, L.airlock.y0 - 0.5, L.airlock.y1)) return 'airlock';
  return null;
}
// Solid volumes the player cannot enter (sealed rooms), as a pushout vector or null.
export function sealedPush(x, y, z) {
  if (inBox(L.penguins, x, y, z, -8, 10)) return { x: 0, z: L.penguins.z1 + 0.5 - z };
  if (inBox(L.researchWing, x, y, z, -8, 10)) return { x: 0, z: L.researchWing.z1 + 0.5 - z };
  if (inBox(L.calCoast, x, y, z, -8, -1)) return { y: -1 + 0.4 - y };
  const sw = (x - L.swamp.x) ** 2 + (z - L.swamp.z) ** 2;
  if (sw < L.swamp.r ** 2 && y < 0.2) return { y: 0.2 - y };
  const am = (x - L.amazon.x) ** 2 + (z - L.amazon.z) ** 2;
  if (am < L.amazon.r ** 2 && y < L.amazon.top + 0.2) return { y: L.amazon.top + 0.2 - y };
  if (y < L.levels.aquarium + 0.4 && insideFootprint(x, z)) return { y: L.levels.aquarium + 0.4 - y };
  return null;
}
