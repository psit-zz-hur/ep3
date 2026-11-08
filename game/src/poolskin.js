// Pool skin: the interior below the tile line rendered as a raymarched signed-distance field with smooth unions
// (big fillets wherever surfaces meet) and a world-space tile grid projected on it. Drawn as a box volume that
// writes real depth, so fish, props and the water surface composite normally. Toggle with O; [ ] move the tile line.
import * as THREE from 'three';
import { L } from './layout.js';

export function buildPoolSkin(scene, camera) {
  const B = L.bbox; const y0 = L.levels.aquarium - 0.6, y1 = L.levels.roofSlab + 0.2;
  const geo = new THREE.BoxGeometry(B.x1 - B.x0 + 1, y1 - y0, B.z1 - B.z0 + 1);
  const u = {
    uCamPos: { value: new THREE.Vector3() }, uInvProj: { value: new THREE.Matrix4() }, uInvView: { value: new THREE.Matrix4() },
    uTileTop: { value: L.levels.roofSlab - 0.3 }, uTime: { value: 0 }, uFogColor: { value: new THREE.Color() }, uFogNear: { value: 1 }, uFogFar: { value: 100 },
    uWaterY: { value: -8 }, uSun: { value: new THREE.Vector3(-0.4, 0.8, 0.45).normalize() }, uLight: { value: 1 }, uTileSize: { value: 0.3 }, uFillet: { value: 0.9144 },  // 3 ft
    uCapital: { value: 1.6 }, uMode: { value: 0 },        // mode 0 = pool tile, 1 = poured concrete
    uDebug: { value: 0 }, uCaustic: { value: 0 }, uResolution: { value: new THREE.Vector2(1, 1) }, uProj: { value: new THREE.Matrix4() }, uView: { value: new THREE.Matrix4() },
  };
  const P = L; const f = (n) => n.toFixed(2);
  const glsl = `
    uniform vec3 uCamPos; uniform float uTileTop, uTime, uFogNear, uFogFar, uWaterY, uLight, uTileSize, uFillet, uCaustic, uDebug, uCapital, uMode; uniform vec3 uFogColor, uSun; uniform mat4 uProj, uView;
    varying vec3 vWorld;
    float sdBox(vec3 p, vec3 c, vec3 b){ vec3 q = abs(p - c) - b; return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0); }
    float sdSphere(vec3 p, vec3 c, float r){ return length(p - c) - r; }
    float sdCylY(vec3 p, vec2 c, float r, float y0, float y1){ float d = length(p.xz - c) - r; float h = max(y0 - p.y, p.y - y1); return min(max(d,h),0.0) + length(max(vec2(d,h),0.0)); }
    float smin(float a, float b, float k){ float h = clamp(0.5 + 0.5*(b-a)/k, 0.0, 1.0); return mix(b, a, h) - k*h*(1.0-h); }
    float smax(float a, float b, float k){ return -smin(-a, -b, k); }
    // ---- the building as an SDF (metres, same frame as layout.js) ----
    float map(vec3 p){
      float k = uFillet;
      // floors: aquarium level and main slab
      float d = p.y - (${f(L.levels.aquarium)});                                   // lower floor plane
      float slab = sdBox(p, vec3(${f((B.x0+B.x1)/2)}, -0.3, ${f((B.z0+B.z1)/2)}), vec3(${f((B.x1-B.x0)/2)}, 0.3, ${f((B.z1-B.z0)/2)}));
      // openings through the main slab: reef tank, lagoon, two stair voids by the piazza
      float reef = sdBox(p, vec3(${f(P.reefTank.x)}, -3.8, ${f(P.reefTank.z)}), vec3(${f(P.reefTank.w/2)}, 4.2, ${f(P.reefTank.d/2)}));
      float lag  = sdBox(p, vec3(${f(P.lagoon.x)}, -0.8, ${f(P.lagoon.z)}), vec3(${f(P.lagoon.w/2)}, 0.9, ${f(P.lagoon.d/2)}));
      float st1  = sdBox(p, vec3(${f(P.piazza.x - P.piazza.w/2 - 6)}, -3.8, ${f(P.piazza.z)}), vec3(3.0, 4.2, 6.0));
      float st2  = sdBox(p, vec3(${f(P.piazza.x + P.piazza.w/2 + 6)}, -3.8, ${f(P.piazza.z)}), vec3(3.0, 4.2, 6.0));
      slab = smax(slab, -reef, k); slab = smax(slab, -lag, k*0.6); slab = smax(slab, -st1, k); slab = smax(slab, -st2, k);
      d = smin(d, slab, k);
      // perimeter walls (inside face of the facade) as a hollow box shell
      float outer = sdBox(p, vec3(${f((B.x0+B.x1)/2)}, 2.0, ${f((B.z0+B.z1)/2)}), vec3(${f((B.x1-B.x0)/2 + 0.6)}, 12.0, ${f((B.z1-B.z0)/2 + 0.6)}));
      float inner = sdBox(p, vec3(${f((B.x0+B.x1)/2)}, 2.0, ${f((B.z0+B.z1)/2)}), vec3(${f((B.x1-B.x0)/2)}, 13.0, ${f((B.z1-B.z0)/2)}));
      float shell = max(outer, -inner); d = smin(d, shell, k);
      // columns on the 7.3 m grid (domain repetition), removed inside the piazza and the domes
      vec2 g = vec2(${f(L.columnGrid)}); vec2 q = mod(p.xz - vec2(${f(B.x0 + L.columnGrid/2)}, ${f(B.z0 + L.columnGrid/2)}) + 0.5*g, g) - 0.5*g;
      float col = length(q) - 0.42;
      float piazzaRegion = sdBox(p, vec3(${f(P.piazza.x)}, 4.0, ${f(P.piazza.z)}), vec3(${f(P.piazza.w/2 + 1.5)}, 20.0, ${f(P.piazza.d/2 + 1.5)}));
      float domeRegion = min(sdCylY(p, vec2(${f(P.planetarium.x)}, ${f(P.planetarium.z)}), ${f(L.domeR + 1.0)}, -20.0, 40.0), sdCylY(p, vec2(${f(P.rainforest.x)}, ${f(P.rainforest.z)}), ${f(L.domeR + 1.0)}, -20.0, 40.0));
      col = max(col, -piazzaRegion); col = max(col, -domeRegion); // mushroom capital: the shaft flares into the ceiling slab over the top 2.6 m (poured-concrete warehouse column)
      float flare = clamp((p.y - (${f(L.levels.roofSlab)} - 2.6)) / 2.6, 0.0, 1.0); col -= uCapital * flare * flare;
      col = max(col, p.y - ${f(L.levels.roofSlab)} - 0.6); // columns stop inside the ceiling slab
      d = smin(d, col, k * 0.7);
      // ceiling slab (underside of the roof structure) so capitals and walls fillet into it; the tile line clips it away in pool mode
      float ceil = sdBox(p, vec3(${f((B.x0+B.x1)/2)}, ${f(L.levels.roofSlab + 0.4)}, ${f((B.z0+B.z1)/2)}), vec3(${f((B.x1-B.x0)/2)}, 0.5, ${f((B.z1-B.z0)/2)}));
      ceil = smax(ceil, -sdBox(p, vec3(${f(P.skylight.x)}, ${f(L.levels.roofSlab + 0.4)}, ${f(P.skylight.z)}), vec3(${f(P.skylight.w/2)}, 2.0, ${f(P.skylight.d/2)})), k);
      d = smin(d, ceil, k);
      // planetarium: a tiled sphere (flooded dome), rainforest: NOT tiled (glass), only its base plinth
      d = smin(d, sdSphere(p, vec3(${f(P.planetarium.x)}, ${f(P.planetarium.y)}, ${f(P.planetarium.z)}), ${f(L.domeR)}), k);
      d = smin(d, sdCylY(p, vec2(${f(P.rainforest.x)}, ${f(P.rainforest.z)}), ${f(L.domeR - 0.5)}, ${f(L.levels.aquarium)}, ${f(P.amazon.top + 0.3)}), k);
      // mezzanine ring around the piazza
      float mz = sdBox(p, vec3(${f(P.piazza.x)}, ${f(L.levels.mezz)}, ${f(P.piazza.z)}), vec3(${f(P.piazza.w/2 + 6)}, 0.18, ${f(P.piazza.d/2 + 6)}));
      mz = max(mz, -sdBox(p, vec3(${f(P.piazza.x)}, ${f(L.levels.mezz)}, ${f(P.piazza.z)}), vec3(${f(P.piazza.w/2 + 2)}, 1.0, ${f(P.piazza.d/2 + 2)})));
      d = smin(d, mz, k * 0.6);
      // sealed rooms and the swamp drum become tiled plinths
      d = smin(d, sdBox(p, vec3(${f((P.researchWing.x0+P.researchWing.x1)/2)}, 4.5, ${f((P.researchWing.z0+P.researchWing.z1)/2)}), vec3(${f((P.researchWing.x1-P.researchWing.x0)/2)}, 4.6, ${f((P.researchWing.z1-P.researchWing.z0)/2)})), k);
      d = smin(d, sdBox(p, vec3(${f((P.researchWing2.x0+P.researchWing2.x1)/2)}, 4.5, ${f((P.researchWing2.z0+P.researchWing2.z1)/2)}), vec3(${f((P.researchWing2.x1-P.researchWing2.x0)/2)}, 4.6, ${f((P.researchWing2.z1-P.researchWing2.z0)/2)})), k);
      d = smin(d, sdBox(p, vec3(${f((P.shop.x0+P.shop.x1)/2)}, 4.5, ${f((P.shop.z0+P.shop.z1)/2)}), vec3(${f((P.shop.x1-P.shop.x0)/2)}, 4.6, ${f((P.shop.z1-P.shop.z0)/2)})), k);
      d = smin(d, sdBox(p, vec3(${f((P.penguins.x0+P.penguins.x1)/2)}, 2.5, ${f((P.penguins.z0+P.penguins.z1)/2)}), vec3(${f((P.penguins.x1-P.penguins.x0)/2)}, 3.0, ${f((P.penguins.z1-P.penguins.z0)/2)})), k);
      d = smin(d, sdCylY(p, vec2(${f(P.swamp.x)}, ${f(P.swamp.z)}), ${f(P.swamp.r)}, ${f(L.levels.aquarium)}, 0.9), k);
      d = smin(d, sdBox(p, vec3(${f(P.calCoast.x)}, -4.3, ${f(P.calCoast.z)}), vec3(${f(P.calCoast.w/2)}, 3.3, ${f(P.calCoast.d/2)})), k);
      // African Hall vault: a half cylinder along z, hollow
      float vaultR = ${f((P.africanHall.x1 - P.africanHall.x0)/2)}; vec3 vc = vec3(${f((P.africanHall.x0+P.africanHall.x1)/2)}, ${f(P.africanHall.vaultTop)} - vaultR, ${f((P.africanHall.z0+P.africanHall.z1)/2)});
      float vOut = length(p.xy - vc.xy) - (vaultR + 0.5); float vIn = length(p.xy - vc.xy) - vaultR; float vZ = abs(p.z - vc.z) - ${f((P.africanHall.z1-P.africanHall.z0)/2)};
      float vault = max(max(vOut, -vIn), vZ); vault = max(vault, vc.y - p.y); d = smin(d, vault, k);
      // the skin is a 15 cm layer on top of everything, cut at the tile line
      d -= 0.15;
      d = max(d, p.y - uTileTop);
      return d;
    }
    vec3 normalAt(vec3 p){ vec2 e = vec2(0.02, 0.0); return normalize(vec3(map(p+e.xyy)-map(p-e.xyy), map(p+e.yxy)-map(p-e.yxy), map(p+e.yyx)-map(p-e.yyx))); }
    float hash(vec3 p){ return fract(sin(dot(floor(p), vec3(127.1, 311.7, 74.7))) * 43758.5453); }
    float vnoise(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); float n = 0.0; for (int k=0;k<2;k++) for (int j=0;j<2;j++) for (int i2=0;i2<2;i2++) { vec3 o = vec3(float(i2),float(j),float(k)); n += hash(i+o) * (i2==1?f.x:1.0-f.x) * (j==1?f.y:1.0-f.y) * (k==1?f.z:1.0-f.z); } return n; }
    vec3 concrete(vec3 p, vec3 n){
      // smooth poured concrete: warm grey, large-scale mottling, faint formwork panel seams on a 2.4 m grid, tie holes
      float m = vnoise(p * 0.35) * 0.6 + vnoise(p * 1.7) * 0.3 + vnoise(p * 7.0) * 0.1;
      vec3 base = mix(vec3(0.58, 0.57, 0.55), vec3(0.74, 0.73, 0.70), m);
      vec3 an = abs(n); an /= (an.x + an.y + an.z);
      vec2 uv = p.xz * an.y + p.zy * an.x + p.xy * an.z; vec2 g = abs(fract(uv / 2.4) - 0.5);
      float seam = 1.0 - smoothstep(0.0, 0.012, min(g.x, g.y) * 2.4);
      vec2 th = fract(uv / 2.4) - vec2(0.25, 0.25); vec2 th2 = fract(uv / 2.4) - vec2(0.75, 0.75); float tie = smoothstep(0.03, 0.02, min(length(th), length(th2)));
      base = mix(base, base * 0.78, seam * 0.6 + tie * 0.5);
      float wax = 1.0 - smoothstep(0.0, 0.3, uTileTop - p.y); base = mix(base, base * 0.6, wax * 0.5);
      return base;
    }
    vec3 tiles(vec3 p, vec3 n){
      if (uMode > 0.5) return concrete(p, n);
      // triplanar world-space tile grid; grout lines; per-tile tint; darker band rows every 3 m of depth
      vec3 an = abs(n); an /= (an.x + an.y + an.z);
      vec2 uvx = p.zy / uTileSize, uvy = p.xz / uTileSize, uvz = p.xy / uTileSize;
      vec2 gx = abs(fract(uvx) - 0.5), gy = abs(fract(uvy) - 0.5), gz = abs(fract(uvz) - 0.5);
      float lx = smoothstep(0.42, 0.47, max(gx.x, gx.y)), ly = smoothstep(0.42, 0.47, max(gy.x, gy.y)), lz = smoothstep(0.42, 0.47, max(gz.x, gz.y));
      float grout = lx*an.x + ly*an.y + lz*an.z;
      vec3 cellX = vec3(0.0, floor(uvx)), cellY = vec3(floor(uvy.x), 0.0, floor(uvy.y)), cellZ = vec3(floor(uvz), 0.0);
      float tint = hash(cellX)*an.x + hash(cellY)*an.y + hash(cellZ)*an.z;
      vec3 base = mix(vec3(0.86, 0.95, 0.96), vec3(0.62, 0.86, 0.90), tint);   // pool white-blue
      float band = step(0.8, fract(p.y / 3.0 + 0.02)) * step(0.3, an.x + an.z);  // horizontal tile band on vertical faces
      base = mix(base, vec3(0.12, 0.35, 0.55), band * 0.9);
      float tileLine = 1.0 - smoothstep(0.0, 0.25, uTileTop - p.y);                 // the coping row at the tile line
      base = mix(base, vec3(0.16, 0.22, 0.30), tileLine);
      return mix(base, vec3(0.58, 0.64, 0.66), grout);
    }
    void main(){
      vec3 ro = uCamPos; vec3 rd = normalize(vWorld - uCamPos);
      // start at the camera if it is inside the volume, else at the box surface
      float t = 0.0; float d; vec3 p = ro; bool hit = false;
      for (int i = 0; i < 160; i++) { p = ro + rd * t; d = map(p); if (d < 0.004 * t + 0.002) { hit = true; break; } t += d * 0.9; if (t > 400.0) break; }
      if (!hit) { if (uDebug > 0.5) { gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0); gl_FragDepthEXT = 0.9999; return; } discard; }
      vec3 n = normalAt(p); vec3 col = tiles(p, n);
      if (uDebug > 0.5) { gl_FragColor = vec4(n * 0.5 + 0.5, 1.0); vec4 clipD = uProj * uView * vec4(p, 1.0); gl_FragDepthEXT = (clipD.z / clipD.w) * 0.5 + 0.5; return; }
      float diff = clamp(dot(n, uSun), 0.0, 1.0); float sky = 0.5 + 0.5 * n.y;
      vec3 lit = col * (0.35 * sky + 0.75 * diff) * uLight;
      if (uMode > 0.5) { vec3 v = normalize(uCamPos - p); vec3 h = normalize(v + uSun); lit += vec3(0.08) * pow(max(dot(n, h), 0.0), 24.0) * uLight; } // waxed concrete sheen
      // caustics on upward faces below the water
      if (p.y < uWaterY) { vec2 cp = p.xz * 1.3; float v = sin(cp.x*3.0+uTime)*sin(cp.y*2.4-uTime*1.2) + sin((cp.x+cp.y)*2.2+uTime*0.7); v = pow(max(v,0.0),3.0); lit += vec3(0.5,0.8,0.9) * v * uCaustic * max(n.y, 0.0); }
      float fogF = clamp((t - uFogNear) / (uFogFar - uFogNear), 0.0, 1.0); lit = mix(lit, uFogColor, fogF);
      gl_FragColor = vec4(lit, 1.0);
      // write real depth so meshes composite correctly
      vec4 clip = uProj * uView * vec4(p, 1.0); float ndc = clip.z / clip.w; gl_FragDepthEXT = ndc * 0.5 + 0.5;
    }`;
  const mat = new THREE.ShaderMaterial({
    uniforms: u, side: THREE.BackSide, transparent: false, depthTest: true, depthFunc: THREE.AlwaysDepth, depthWrite: true,
    vertexShader: `varying vec3 vWorld; void main(){ vWorld = (modelMatrix * vec4(position,1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vWorld,1.0); }`,
    fragmentShader: glsl,
  });
  const mesh = new THREE.Mesh(geo, mat); mesh.position.set((B.x0 + B.x1) / 2, (y0 + y1) / 2, (B.z0 + B.z1) / 2); mesh.frustumCulled = false; mesh.renderOrder = -1; mesh.visible = false; scene.add(mesh);
  const state = { enabled: false };
  function update(t, waterY, fog, light) {
    mesh.visible = state.enabled; if (!state.enabled) return;
    u.uCamPos.value.copy(camera.position); u.uProj.value.copy(camera.projectionMatrix); u.uView.value.copy(camera.matrixWorldInverse); u.uTime.value = t; u.uWaterY.value = waterY; u.uLight.value = light;
    u.uFogColor.value.copy(fog.color); u.uFogNear.value = fog.near; u.uFogFar.value = fog.far; u.uCaustic.value = waterY > 0.3 ? THREE.MathUtils.clamp((waterY - 0.3) / 3, 0, 1) * 0.25 : 0;
    // keep the volume box tall enough for the chosen tile line
  }
  return { mesh, state, uniforms: u, update, setTileTop: (y) => { u.uTileTop.value = y; }, get tileTop() { return u.uTileTop.value; },
    setFillet: (r) => { u.uFillet.value = Math.max(0.05, r); }, setMode: (m) => { u.uMode.value = m; }, get mode() { return u.uMode.value; }, setCapital: (c) => { u.uCapital.value = c; }, get fillet() { return u.uFillet.value; }, setTileSize: (t) => { u.uTileSize.value = Math.max(0.05, t); }, get tileSize() { return u.uTileSize.value; } };
}
