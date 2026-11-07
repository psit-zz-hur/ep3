// Lidar exterior shell: 0.5 m DSM of the site (USGS 3DEP 2023, public domain) as a mesh.
import * as THREE from 'three';
import { L } from './layout.js';

async function loadPNG(url) {
  const img = await new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = url; });
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0);
  return { w: img.width, h: img.height, data: g.getImageData(0, 0, img.width, img.height).data };
}

export async function buildSite(scene) {
  const meta = await (await fetch('./assets/site_meta.json')).json();
  const [dsm, dtm, mask] = await Promise.all([loadPNG('./assets/site_dsm_rg.png'), loadPNG('./assets/site_dtm_rg.png'), loadPNG('./assets/site_bldg_mask.png')]);
  const W = dsm.w, H = dsm.h, res = meta.res_m, g0 = meta.ground_m, base = meta.z_base_m;
  const hAt = (p, i) => (p.data[i * 4] * 256 + p.data[i * 4 + 1]) * meta.z_scale + base - g0;
  const heights = new Float32Array(W * H), ground = new Float32Array(W * H), bldg = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) { heights[i] = hAt(dsm, i); ground[i] = hAt(dtm, i); bldg[i] = mask.data[i * 4] > 127 ? 1 : 0; }

  // Geometry: one vertex per pixel. x = -300 + i*res, z = -225 + j*res (image row = +Z = north side).
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(W * H * 3), col = new Float32Array(W * H * 3), kind = new Float32Array(W * H);
  const cGround = new THREE.Color(0x1b2a24), cTree = new THREE.Color(0x3b6b45), cRoof = new THREE.Color(0x6e7a5a), cHigh = new THREE.Color(0xb8c29a), cPath = new THREE.Color(0x2b2f33);
  const tmp = new THREE.Color();
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const k = j * W + i, y = heights[k];
    pos[k * 3] = -meta.width_m / 2 + i * res; pos[k * 3 + 1] = y; pos[k * 3 + 2] = -meta.height_m / 2 + j * res;
    const above = y - ground[k];
    if (bldg[k]) { tmp.copy(cRoof).lerp(cHigh, THREE.MathUtils.clamp((y - L.levels.deck) / 8, 0, 1)); kind[k] = 1; }
    else if (above > 2.5) { tmp.copy(cTree).lerp(cHigh, THREE.MathUtils.clamp((above - 3) / 25, 0, 0.8)); kind[k] = 2; }
    else { tmp.copy(cGround).lerp(cPath, THREE.MathUtils.clamp(above / 1.5, 0, 1) * 0.5); kind[k] = 0; }
    col[k * 3] = tmp.r; col[k * 3 + 1] = tmp.g; col[k * 3 + 2] = tmp.b;
  }
  const idx = new Uint32Array((W - 1) * (H - 1) * 6); let n = 0;
  for (let j = 0; j < H - 1; j++) for (let i = 0; i < W - 1; i++) {
    const a = j * W + i, b = a + 1, c = a + W, d = c + 1;
    idx[n++] = a; idx[n++] = c; idx[n++] = b; idx[n++] = b; idx[n++] = c; idx[n++] = d;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('kind', new THREE.BufferAttribute(kind, 1));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  geo.computeVertexNormals();

  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0.0, flatShading: false, transparent: true });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uRoofAlpha = { value: 1.0 }; sh.uniforms.uGrid = { value: 0.0 };
    mat.userData.sh = sh;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute float kind; varying float vKind; varying vec3 vWp;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvKind = kind; vWp = (modelMatrix * vec4(position,1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vKind; varying vec3 vWp; uniform float uRoofAlpha; uniform float uGrid;')
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
        // 10 m survey grid etched into the lidar surface (data aesthetic)
        vec2 gp = abs(fract(vWp.xz / 10.0) - 0.5);
        float gl = 1.0 - smoothstep(0.0, 0.04, min(gp.x, gp.y));
        gl_FragColor.rgb += gl * uGrid * vec3(0.25, 0.45, 0.5);
        if (vKind > 0.5 && vKind < 1.5) gl_FragColor.a *= uRoofAlpha;`);
  };
  const mesh = new THREE.Mesh(geo, mat); mesh.name = 'lidar-site'; mesh.receiveShadow = false;
  scene.add(mesh);

  // sampler for gameplay (height of lidar surface at x,z)
  const sample = (x, z) => {
    const i = Math.round((x + meta.width_m / 2) / res), j = Math.round((z + meta.height_m / 2) / res);
    if (i < 0 || j < 0 || i >= W || j >= H) return 0;
    return heights[j * W + i];
  };
  const isBuilding = (x, z) => {
    const i = Math.round((x + meta.width_m / 2) / res), j = Math.round((z + meta.height_m / 2) / res);
    if (i < 0 || j < 0 || i >= W || j >= H) return false;
    return bldg[j * W + i] === 1;
  };
  return { mesh, meta, sample, isBuilding, setRoofAlpha: (a) => { if (mat.userData.sh) mat.userData.sh.uniforms.uRoofAlpha.value = a; }, setGrid: (g) => { if (mat.userData.sh) mat.userData.sh.uniforms.uGrid.value = g; } };
}
