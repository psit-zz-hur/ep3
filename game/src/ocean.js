// OCEAN: the flood surface as a GPU FFT ocean (WebGL2). Drop-in for water_simple.js (same state / update / toggle / setTarget / meshes / isWet).
// Method ported from Noniv/web-ocean (MIT; WebGPU): JONSWAP + Hasselmann spreading + swell, Tessendorf FFT cascades with choppy displacement,
// Jacobian foam with persistence, LEAN slope moments for roughness + sun glitter. Surface shading: Schlick Fresnel, planar reflection (mirrored
// camera, oblique clip), depth-absorbing refraction grab, GGX + LEAN sun, foam, subsurface tint, underside with total internal reflection.
// Per frame GPU work (256 setting): 3 cascades (256 @ 250 m, 128 @ 50 m, 128 @ 8 m): evolve + 2*log2(N) Stockham passes + resolve each
// (~50 small draw calls, ~0.35 M texels * 2 MRT), then the reflection pass (half res) and the refraction grab (0.6 res) of the scene.
import * as THREE from 'three';
import { L, layerAt, insideFootprint } from './layout.js';
import { buildWater as buildSimple } from './water_simple.js';

const G = 9.81;
const GLSL_PRE = 'precision highp float; precision highp int; precision highp sampler2D;\n';

// ---------------------------------------------------------------- shaders: spectrum / FFT
const VS_QUAD = 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }';

const FS_INIT = GLSL_PRE + `
layout(location = 0) out vec4 o0;
uniform float uN, uL, uKlo, uKhi, uWind, uWdir, uWp, uAlpha, uWps, uAlphaS, uSdir, uSeed;
const float G = 9.81;
uint pcg(uint v){ uint s = v * 747796405u + 2891336453u; uint w = ((s >> ((s >> 28u) + 4u)) ^ s) * 277803737u; return (w >> 22u) ^ w; }
float rnd(uvec3 p){ return float(pcg(p.x + pcg(p.y + pcg(p.z)))) / 4294967295.0; }
vec2 gauss(ivec2 p){
  uint sd = uint(uSeed);
  float u1 = max(rnd(uvec3(uint(p.x), uint(p.y), sd)), 1e-6); float u2 = rnd(uvec3(uint(p.x), uint(p.y), sd + 7u));
  return sqrt(-2.0 * log(u1)) * vec2(cos(6.2831853 * u2), sin(6.2831853 * u2)) * 0.70710678;   // E|xi|^2 = 1
}
float jonswap(float w, float wp, float alpha, float gam){
  float sg = w <= wp ? 0.07 : 0.09; float r = exp(-(w - wp) * (w - wp) / (2.0 * sg * sg * wp * wp));
  return alpha * G * G / pow(w, 5.0) * exp(-1.25 * pow(wp / w, 4.0)) * pow(gam, r);
}
float spreadH(float th, float s){ return pow(abs(cos(0.5 * th)), 2.0 * s) * sqrt(s + 0.25) * 0.28209479; }   // Q(s) ~ sqrt(s+1/4) / (2 sqrt(pi))
float F(vec2 k){
  float kl = length(k); if (kl < max(uKlo, 1.0e-4) || kl >= uKhi) return 0.0;
  float w = sqrt(G * kl); float dwdk = 0.5 * G / w; float th = atan(k.y, k.x);
  float r = w / uWp;
  float s = r < 1.05 ? 6.97 * pow(r, 4.06) : 9.77 * pow(r, -2.33 - 1.45 * (uWind * uWp / G - 1.17));   // Hasselmann directional spreading
  float Sw = jonswap(w, uWp, uAlpha, 3.3) * spreadH(th - uWdir, s);
  float Ss = uAlphaS > 0.0 ? jonswap(w, uWps, uAlphaS, 7.0) * spreadH(th - uSdir, 40.0) : 0.0;           // swell: narrow, long
  return (Sw + Ss) * dwdk / kl * exp(-kl * kl * 1.0e-4);
}
void main(){
  ivec2 ij = ivec2(gl_FragCoord.xy); int N = int(uN); float dk = 6.2831853 / uL;
  vec2 k = (vec2(ij) - 0.5 * uN) * dk; ivec2 ijm = ivec2((N - ij.x) % N, (N - ij.y) % N);
  vec2 h0 = gauss(ij) * sqrt(F(k) * 0.5) * dk; vec2 h0m = gauss(ijm) * sqrt(F(-k) * 0.5) * dk;
  o0 = vec4(h0, h0m.x, -h0m.y);                       // h0(k), conj(h0(-k))
}`;

const FS_EVOLVE = GLSL_PRE + `
layout(location = 0) out vec4 o0; layout(location = 1) out vec4 o1;
uniform sampler2D uH0; uniform float uN, uL, uPhase, uAmp;      // uPhase = t / loop period (0..1)
const float G = 9.81;
vec2 cm(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }
vec2 ci(vec2 a){ return vec2(-a.y, a.x); }                       // multiply by i
void main(){
  ivec2 ij = ivec2(gl_FragCoord.xy); float dk = 6.2831853 / uL; vec2 k = (vec2(ij) - 0.5 * uN) * dk; float kl = length(k);
  vec4 h0 = texelFetch(uH0, ij, 0);
  float w = sqrt(G * kl); float loopT = 100.0; float w0 = 6.2831853 / loopT;            // omega snapped to the loop so t wraps seamlessly
  float ph = 6.2831853 * fract(floor(w / w0 + 0.5) * uPhase); vec2 e = vec2(cos(ph), sin(ph));
  vec2 hk = (cm(h0.xy, e) + cm(h0.zw, vec2(e.x, -e.y))) * uAmp;
  float ik = kl > 1e-6 ? 1.0 / kl : 0.0;
  vec2 Dx = cm(vec2(0.0, -k.x * ik), hk), Dz = cm(vec2(0.0, -k.y * ik), hk);
  vec2 sx = cm(vec2(0.0, k.x), hk), sz = cm(vec2(0.0, k.y), hk);
  vec2 Dxx = hk * (k.x * k.x * ik), Dzz = hk * (k.y * k.y * ik), Dxz = hk * (k.x * k.y * ik);
  o0 = vec4(hk + ci(Dx), Dz + ci(sx));                              // two real fields per complex FFT
  o1 = vec4(sz + ci(Dxx), Dzz + ci(Dxz));
}`;

const FS_FFT = GLSL_PRE + `
layout(location = 0) out vec4 o0; layout(location = 1) out vec4 o1;
uniform sampler2D uA; uniform sampler2D uB; uniform int uDir; uniform int uNs; uniform int uN;
vec2 cm(vec2 a, vec2 b){ return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }
void main(){                                                       // Stockham autosort radix-2, inverse (+i) twiddles
  ivec2 ij = ivec2(gl_FragCoord.xy); int p = uDir == 0 ? ij.x : ij.y;
  int k = p & (uNs - 1); int j = (p / (2 * uNs)) * uNs + k; bool up = (p & uNs) != 0;
  ivec2 a0 = uDir == 0 ? ivec2(j, ij.y) : ivec2(ij.x, j); ivec2 a1 = uDir == 0 ? ivec2(j + uN / 2, ij.y) : ivec2(ij.x, j + uN / 2);
  float ang = 6.2831853 * float(k) / float(2 * uNs); vec2 w = vec2(cos(ang), sin(ang));
  vec4 x0 = texelFetch(uA, a0, 0), x1 = texelFetch(uA, a1, 0); vec4 t = vec4(cm(w, x1.xy), cm(w, x1.zw)); o0 = up ? x0 - t : x0 + t;
  vec4 y0 = texelFetch(uB, a0, 0), y1 = texelFetch(uB, a1, 0); vec4 u = vec4(cm(w, y1.xy), cm(w, y1.zw)); o1 = up ? y0 - u : y0 + u;
}`;

const FS_RESOLVE = GLSL_PRE + `
layout(location = 0) out vec4 o0; layout(location = 1) out vec4 o1; layout(location = 2) out vec4 o2;
uniform sampler2D uA; uniform sampler2D uB; uniform sampler2D uPrev; uniform float uLambda, uDt, uDecay, uThr, uGain;
void main(){
  ivec2 ij = ivec2(gl_FragCoord.xy); float sg = (((ij.x + ij.y) & 1) == 1) ? -1.0 : 1.0;   // (-1)^(x+y) from the centred spectrum
  vec4 a = sg * texelFetch(uA, ij, 0), b = sg * texelFetch(uB, ij, 0);
  float h = a.x, Dx = a.y, Dz = a.z, sx = a.w, sz = b.x, Dxx = b.y, Dzz = b.z, Dxz = b.w;
  float jxx = 1.0 + uLambda * Dxx, jzz = 1.0 + uLambda * Dzz;
  float J = jxx * jzz - uLambda * uLambda * Dxz * Dxz;
  vec2 s = vec2(sx / max(jxx, 0.3), sz / max(jzz, 0.3));
  float prev = texelFetch(uPrev, ij, 0).z;
  float foam = max(prev * exp(-uDt * uDecay), clamp((uThr - J) * uGain, 0.0, 1.0));
  o0 = vec4(uLambda * Dx, h, uLambda * Dz, J);
  o1 = vec4(s, foam, 0.0);
  o2 = vec4(s.x * s.x, s.y * s.y, s.x * s.y, 0.0);              // LEAN second moments (mip-filtered into slope variance)
}`;

// ---------------------------------------------------------------- shaders: surface
const VS_SURF = `
uniform sampler2D uD0; uniform sampler2D uD1; uniform sampler2D uD2; uniform vec3 uInvL; uniform vec3 uCamP; uniform float uMode;
varying vec3 vWp; varying vec2 vXZ; varying float vH;
void main(){
  vec3 w0 = (modelMatrix * vec4(position, 1.0)).xyz; vXZ = w0.xz;
  float dc = length(w0.xz - uCamP.xz) + abs(w0.y - uCamP.y);
  float f2 = 1.0 - smoothstep(6.0, 22.0, dc);
  vec3 d = textureLod(uD0, w0.xz * uInvL.x, 0.0).xyz + textureLod(uD1, w0.xz * uInvL.y, 0.0).xyz + f2 * textureLod(uD2, w0.xz * uInvL.z, 0.0).xyz;
  vH = d.y; vWp = w0 + d; gl_Position = projectionMatrix * viewMatrix * vec4(vWp, 1.0);
}`;

const FS_SURF = GLSL_PRE + `
#include <packing>
uniform sampler2D uS0; uniform sampler2D uS1; uniform sampler2D uS2; uniform sampler2D uM0; uniform sampler2D uM1; uniform sampler2D uM2;
uniform sampler2D uRefr; uniform sampler2D uDepth; uniform sampler2D uRefl; uniform mat4 uTexMat; uniform vec2 uInvRes; uniform vec3 uInvL; uniform vec3 uCamP;
uniform float uCamNear, uCamFar, uMode, uReflect, uGlitter, uFoam, uTime, uLevel, uSunI, uLight, uFogNear, uFogFar, uDensity;
uniform vec3 uSun, uFogColor, uC0, uC1, uC2, uAbsorb;
varying vec3 vWp; varying vec2 vXZ; varying float vH;
float hash21(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(hash21(i), hash21(i + vec2(1, 0)), f.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p){ return 0.5 * vnoise(p) + 0.25 * vnoise(p * 2.13 + 7.1) + 0.125 * vnoise(p * 4.37 + 3.3) + 0.0625 * vnoise(p * 8.9 + 1.7); }
vec3 skyCol(vec3 R){ float h = max(R.y, 0.0); vec3 c = mix(vec3(0.10, 0.07, 0.12), vec3(0.02, 0.03, 0.07), clamp(h * 2.0, 0.0, 1.0)); c = mix(vec3(0.45, 0.22, 0.18), c, clamp(h * 6.0 + 0.2, 0.0, 1.0)); return c * 0.8 + vec3(1.0, 0.7, 0.45) * pow(max(dot(R, uSun), 0.0), 24.0) * 0.5; }
float schlick(float c, float f0){ float m = 1.0 - clamp(c, 0.0, 1.0); float m2 = m * m; return f0 + (1.0 - f0) * m2 * m2 * m; }
float eyeD(float d){ return -perspectiveDepthToViewZ(d, uCamNear, uCamFar); }
void main(){
  vec3 wp = vWp; vec3 toC = cameraPosition - wp; float dist = length(toC); vec3 V = toC / dist; bool under = V.y < 0.0;
  // ---- slopes + LEAN variance from the three cascades
  vec4 a0 = texture2D(uS0, vXZ * uInvL.x), a1 = texture2D(uS1, vXZ * uInvL.y), a2 = texture2D(uS2, vXZ * uInvL.z);
  vec4 m0 = texture2D(uM0, vXZ * uInvL.x), m1 = texture2D(uM1, vXZ * uInvL.y), m2 = texture2D(uM2, vXZ * uInvL.z);
  float f2 = 1.0 - smoothstep(30.0, 120.0, dist);                 // finest cascade fades into variance far away (its mip chain carries it)
  vec2 mu = a0.xy + a1.xy + a2.xy * f2;
  vec3 cv0 = m0.xyz - vec3(a0.x * a0.x, a0.y * a0.y, a0.x * a0.y), cv1 = m1.xyz - vec3(a1.x * a1.x, a1.y * a1.y, a1.x * a1.y), cv2 = m2.xyz - vec3(a2.x * a2.x, a2.y * a2.y, a2.x * a2.y);
  vec3 cov = max(cv0, vec3(0.0, 0.0, -1.0)) + max(cv1, vec3(0.0, 0.0, -1.0)) + max(cv2, vec3(0.0, 0.0, -1.0)) * (0.35 + 0.65 * f2);
  if (cv0.x < 0.0 || cv0.y < 0.0) cov = max(cov, vec3(0.0, 0.0, -1.0));
  vec3 Nu = normalize(vec3(-mu.x, 1.0, -mu.y));                    // upward-facing normal
  vec3 N = under ? -Nu : Nu;
  vec3 L = normalize(uSun);
  float foam = clamp(a0.z + a1.z + a2.z * f2, 0.0, 1.0) * uFoam;
  float eSurf = -(viewMatrix * vec4(wp, 1.0)).z;
  vec2 suv = gl_FragCoord.xy * uInvRes;
  float nz = fbm(vXZ * 1.7 + uTime * 0.05) + 0.5 * fbm(vXZ * 6.0 - uTime * 0.08);

  vec3 col; float thick = 30.0;
  if (uMode > 0.5) {                                              // simple path (dome cube faces): no render-target taps
    float F = schlick(dot(N, V), 0.02); vec3 R = reflect(-V, N);
    col = mix(uC0 * 0.5 * uLight, skyCol(R), F);
    if (under) col = mix(uC1 * 0.6, uC0, 0.3);
  } else if (!under) {
    // ---- above the surface
    float NdV = max(dot(N, V), 0.02); float F = schlick(NdV, 0.02);
    vec3 R = reflect(-V, N);
    vec4 rp = uTexMat * vec4(wp, 1.0); vec2 ruv = rp.xy / rp.w + N.xz * 0.04 * clamp(1.0 - exp(-dist * 0.05), 0.2, 1.0);
    vec3 refl = uReflect > 0.5 ? texture2D(uRefl, clamp(ruv, 0.001, 0.999)).rgb : skyCol(R);
    // refraction grab with depth-based absorption
    float e0 = eyeD(texture2D(uDepth, suv).r); float t0 = max(e0 - eSurf, 0.0) * dist / max(eSurf, 0.05);
    vec2 uv2 = suv + Nu.xz * 0.06 * clamp(t0 * 0.2, 0.04, 1.0) * clamp(8.0 / max(eSurf, 1.0), 0.15, 1.0);
    float e2 = eyeD(texture2D(uDepth, uv2).r); if (e2 < eSurf) { uv2 = suv; e2 = e0; }
    thick = clamp(max(e2 - eSurf, 0.0) * dist / max(eSurf, 0.05), 0.0, 80.0);
    vec3 scene = texture2D(uRefr, uv2).rgb;
    vec3 T = exp(-uAbsorb * uDensity * thick);
    vec3 scat = mix(uC0, uC1, smoothstep(0.5, 20.0, thick)); scat = mix(scat, uC2, smoothstep(20.0, 60.0, thick)) * (0.55 + 0.45 * uLight);
    vec3 refr = scene * T + scat * (1.0 - T);
    // subsurface: light through wave backs facing away from the sun
    float sss = pow(clamp(dot(V, -normalize(L + Nu * 0.55)), 0.0, 1.0), 3.0) * smoothstep(-0.1, 0.5, vH) * clamp(L.y * 2.0, 0.0, 1.0);
    refr += vec3(0.04, 0.42, 0.34) * sss * 0.9 * (uSunI * 0.35);
    // sun: GGX lobe + LEAN anisotropic glitter
    vec3 H = normalize(L + V); vec2 sh = -H.xz / max(H.y, 0.05);
    float vx = cov.x + 0.00025, vz = cov.y + 0.00025, cxz = clamp(cov.z, -0.9 * sqrt(vx * vz), 0.9 * sqrt(vx * vz));
    float det = max(vx * vz - cxz * cxz, 1e-9); vec2 dS = sh - mu;
    float q = (vz * dS.x * dS.x - 2.0 * cxz * dS.x * dS.y + vx * dS.y * dS.y) / det;
    float P = exp(-0.5 * min(q, 60.0)) / (6.2831853 * sqrt(det));
    float Fh = schlick(dot(H, V), 0.02);
    float glit = uSunI * Fh * (P / pow(max(H.y, 0.05), 4.0)) / (4.0 * max(V.y, 0.06)) * L.y;
    float a2g = clamp(vx + vz + 0.01, 0.01, 0.6); float nh = max(dot(Nu, H), 0.0); float dg = a2g / (3.14159 * pow(nh * nh * (a2g - 1.0) + 1.0, 2.0));
    float ggx = uSunI * Fh * dg / (4.0 * max(V.y, 0.06)) * L.y * 0.08;
    float sunMask = clamp(L.y * 6.0, 0.0, 1.0);
    vec3 sunC = vec3(1.0, 0.82, 0.58);
    col = mix(refr, refl, F) + sunC * (glit * uGlitter + ggx) * sunMask;
    // foam: whitecaps + a contact line where the surface meets walls and columns
    float shore = (1.0 - smoothstep(0.0, 0.5 + 0.5 * nz, thick)) * step(thick, 60.0);
    float fm = clamp(smoothstep(0.15, 0.7, foam * (0.55 + 0.9 * nz)) + shore * 0.9 * uFoam, 0.0, 1.0);
    vec3 fcol = vec3(0.86, 0.9, 0.9) * (0.45 + 0.85 * max(dot(Nu, L), 0.0)) * (0.5 + 0.5 * uLight) + vec3(0.18, 0.2, 0.2);
    col = mix(col, fcol, fm * 0.92);
  } else {
    // ---- below the surface: Snell's window + total internal reflection
    float NdV = clamp(dot(N, V), 0.0, 1.0); float s2 = 1.0 - NdV * NdV; float eta = 1.33;
    bool tir = eta * eta * s2 >= 1.0; float cT = tir ? 0.0 : sqrt(1.0 - eta * eta * s2);
    float F = tir ? 1.0 : schlick(cT, 0.02);
    vec3 R = reflect(-V, N);
    vec4 rp = uTexMat * vec4(wp, 1.0); vec2 ruv = rp.xy / rp.w + N.xz * 0.03;
    vec3 refl = uReflect > 0.5 ? texture2D(uRefl, clamp(ruv, 0.001, 0.999)).rgb : mix(uC1, uC2, 0.5);
    vec3 trans = texture2D(uRefr, clamp(suv + Nu.xz * 0.08, 0.001, 0.999)).rgb;     // the world above, seen through the window
    float edge = smoothstep(0.0, 0.35, 1.0 - eta * sqrt(s2));
    trans *= mix(0.35, 1.0, edge);
    col = mix(trans, refl * 0.85 + uC0 * 0.08, F);
    col += vec3(0.9, 0.95, 0.95) * foam * 0.12 * (0.5 + nz);
    col = mix(col, uC0 * (0.4 + 0.6 * uLight), 0.12);
  }
  float fogF = clamp((dist - uFogNear) / max(uFogFar - uFogNear, 1.0), 0.0, 1.0); col = mix(col, uFogColor, fogF);
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;

// ---------------------------------------------------------------- module
function half(u) { const s = (u & 0x8000) ? -1 : 1, e = (u >> 10) & 31, f = u & 1023; return e === 0 ? s * 5.960464477539063e-8 * f : e === 31 ? NaN : s * Math.pow(2, e - 15) * (1 + f / 1024); }

export function buildWater(scene, renderer, camera) {
  const hasF = renderer && renderer.extensions && renderer.extensions.has('EXT_color_buffer_float');
  const hasH = renderer && renderer.extensions && renderer.extensions.has('EXT_color_buffer_half_float');
  if (!renderer || !camera || (!hasF && !hasH)) { console.warn('ocean: needs renderer + camera + float render targets, falling back to water_simple'); return buildSimple(scene); }
  const fftType = hasF ? THREE.FloatType : THREE.HalfFloatType;

  const B = L.bbox, W = B.x1 - B.x0, D = B.z1 - B.z0, cx = (B.x0 + B.x1) / 2, cz = (B.z0 + B.z1) / 2;
  const state = { level: L.levels.aquarium - 0.2, target: L.levels.aquarium - 0.2, speed: 0.6, flooding: false };
  const params = {
    windSpeed: 6, windDir: 35, fetch: 6000, choppiness: 1.0, swell: 0.4, foam: 0.45, glitter: 1.0, reflection: true, fftSize: 256,
    amplitude: 1.0, timeScale: 1.0, foamDecay: 1.4, patch: [250, 50, 8], density: 1.0, sunIntensity: 3.0, refrScale: 0.6, reflScale: 0.5,
    swellLength: 60,
  };
  const SPECTRAL = new Set(['windSpeed', 'windDir', 'fetch', 'swell', 'swellLength', 'patch']);

  // ---- sun: follow the scene's directional light unless overridden
  const sunDir = new THREE.Vector3(-0.55, 0.41, 0.73).normalize();
  scene.traverse((o) => { if (o.isDirectionalLight && !o.__oceanSeen) { o.__oceanSeen = true; sunDir.copy(o.position).sub(o.target ? o.target.position : new THREE.Vector3()).normalize(); } });

  // ---- full-screen pass helper
  const quadScene = new THREE.Scene(), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2)); quad.frustumCulled = false; quadScene.add(quad);
  const mk = (fs, uniforms) => new THREE.ShaderMaterial({ glslVersion: THREE.GLSL3, vertexShader: VS_QUAD, fragmentShader: fs, uniforms, depthTest: false, depthWrite: false, blending: THREE.NoBlending });
  const U = (v) => ({ value: v });
  const matInit = mk(FS_INIT, { uN: U(256), uL: U(250), uKlo: U(0), uKhi: U(1), uWind: U(6), uWdir: U(0), uWp: U(3), uAlpha: U(0.02), uWps: U(1), uAlphaS: U(0), uSdir: U(0), uSeed: U(1) });
  const matEvolve = mk(FS_EVOLVE, { uH0: U(null), uN: U(256), uL: U(250), uPhase: U(0), uAmp: U(1) });
  const matFFT = mk(FS_FFT, { uA: U(null), uB: U(null), uDir: U(0), uNs: U(1), uN: U(256) });
  const matResolve = mk(FS_RESOLVE, { uA: U(null), uB: U(null), uPrev: U(null), uLambda: U(1), uDt: U(0.016), uDecay: U(1.4), uThr: U(0.9), uGain: U(4) });
  const pass = (mat, target) => { quad.material = mat; renderer.setRenderTarget(target); renderer.render(quadScene, ortho); };

  // ---- cascades
  let cascades = [];
  const rtOpts = (extra) => Object.assign({ format: THREE.RGBAFormat, depthBuffer: false, stencilBuffer: false, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, type: fftType }, extra);
  function makeCascades() {
    for (const c of cascades) { c.h0.dispose(); c.A.dispose(); c.B.dispose(); c.out[0].dispose(); c.out[1].dispose(); }
    const S = params.fftSize, sizes = [S, S / 2, S / 2]; cascades = [];
    for (let i = 0; i < 3; i++) {
      const N = sizes[i], Lp = params.patch[i];
      const h0 = new THREE.WebGLRenderTarget(N, N, rtOpts({ count: 1 }));
      const A = new THREE.WebGLRenderTarget(N, N, rtOpts({ count: 2 })), Bt = new THREE.WebGLRenderTarget(N, N, rtOpts({ count: 2 }));
      const outOpts = { format: THREE.RGBAFormat, type: THREE.HalfFloatType, depthBuffer: false, count: 3, generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter, wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping };
      const o0 = new THREE.WebGLRenderTarget(N, N, outOpts), o1 = new THREE.WebGLRenderTarget(N, N, outOpts);
      for (const o of [o0, o1]) for (const tx of o.textures) { tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.anisotropy = 4; }
      cascades.push({ N, L: Lp, h0, A, B: Bt, out: [o0, o1], cur: 0, kLo: 0, kHi: 1 });
    }
    // band limits: each cascade owns 0.5 of its Nyquist (the last one 0.9), starting where the previous one stops
    let lo = 0; cascades.forEach((c, i) => { const nyq = Math.PI * c.N / c.L; c.kLo = lo; c.kHi = nyq * (i < 2 ? 0.5 : 0.9); lo = c.kHi; });
    specDirty = true; surfU.uInvL.value.set(1 / params.patch[0], 1 / params.patch[1], 1 / params.patch[2]);
  }
  let specDirty = true;
  function computeSpectra() {
    const U10 = Math.max(params.windSpeed, 0.5), F = Math.max(params.fetch, 100);
    const wp = 22 * Math.pow(G * G / (U10 * F), 1 / 3), alpha = 0.076 * Math.pow(U10 * U10 / (F * G), 0.22);
    const wps = Math.sqrt(G * 2 * Math.PI / Math.max(params.swellLength, 8));
    const Hs = 0.7 * params.swell, E = (Hs / 4) * (Hs / 4), alphaS = params.swell > 1e-3 ? E * 5 * Math.pow(wps, 4) / (G * G) / 2.4 : 0;
    const wd = THREE.MathUtils.degToRad(params.windDir), sd = wd + THREE.MathUtils.degToRad(25);
    cascades.forEach((c, i) => {
      const u = matInit.uniforms; u.uN.value = c.N; u.uL.value = c.L; u.uKlo.value = c.kLo; u.uKhi.value = c.kHi; u.uWind.value = U10; u.uWdir.value = wd;
      u.uWp.value = wp; u.uAlpha.value = alpha; u.uWps.value = wps; u.uAlphaS.value = alphaS; u.uSdir.value = sd; u.uSeed.value = 11 + i * 101;
      pass(matInit, c.h0);
    });
    specDirty = false;
  }
  function evolve(dt, t) {
    const tm = (t * params.timeScale) % 100;
    cascades.forEach((c) => {
      const N = c.N, stages = Math.log2(N);
      matEvolve.uniforms.uH0.value = c.h0.texture; matEvolve.uniforms.uN.value = N; matEvolve.uniforms.uL.value = c.L; matEvolve.uniforms.uPhase.value = tm / 100; matEvolve.uniforms.uAmp.value = params.amplitude;
      pass(matEvolve, c.A);
      let src = c.A, dst = c.B; const u = matFFT.uniforms; u.uN.value = N;
      for (let dir = 0; dir < 2; dir++) for (let s = 0; s < stages; s++) {
        u.uDir.value = dir; u.uNs.value = 1 << s; u.uA.value = src.textures[0]; u.uB.value = src.textures[1]; pass(matFFT, dst); const tmp = src; src = dst; dst = tmp;
      }
      const prev = c.out[1 - c.cur], cur = c.out[c.cur]; const r = matResolve.uniforms;
      r.uA.value = src.textures[0]; r.uB.value = src.textures[1]; r.uPrev.value = prev.textures[1]; r.uLambda.value = params.choppiness; r.uDt.value = dt; r.uDecay.value = params.foamDecay;
      r.uThr.value = THREE.MathUtils.lerp(0.5, 0.95, params.foam); r.uGain.value = 3.5;
      pass(matResolve, cur);
      c.cur = 1 - c.cur;                                    // the one just written is now out[1 - cur]
    });
    renderer.setRenderTarget(null);
  }

  // ---- surface
  const dummy = new THREE.Texture();
  const surfU = {
    uD0: U(dummy), uD1: U(dummy), uD2: U(dummy), uS0: U(dummy), uS1: U(dummy), uS2: U(dummy), uM0: U(dummy), uM1: U(dummy), uM2: U(dummy),
    uInvL: U(new THREE.Vector3(1 / 250, 1 / 50, 1 / 8)), uCamP: U(new THREE.Vector3()), uRefr: U(dummy), uDepth: U(dummy), uRefl: U(dummy), uTexMat: U(new THREE.Matrix4()), uInvRes: U(new THREE.Vector2(1, 1)),
    uCamNear: U(0.1), uCamFar: U(1500), uMode: U(0), uReflect: U(1), uGlitter: U(1), uFoam: U(1), uTime: U(0), uLevel: U(0), uSunI: U(3), uLight: U(1), uFogNear: U(60), uFogFar: U(900), uDensity: U(1),
    uSun: U(sunDir.clone()), uFogColor: U(new THREE.Color()), uC0: U(new THREE.Color(L.waterLayers[0].color)), uC1: U(new THREE.Color(L.waterLayers[1].color)), uC2: U(new THREE.Color(L.waterLayers[2].color)), uAbsorb: U(new THREE.Vector3(0.32, 0.065, 0.04)),
  };
  const surfMat = new THREE.ShaderMaterial({ uniforms: surfU, vertexShader: VS_SURF, fragmentShader: FS_SURF, side: THREE.DoubleSide, transparent: false, depthWrite: true });
  const geo = new THREE.PlaneGeometry(W, D, Math.round(W / 0.5), Math.round(D / 0.5)); geo.rotateX(-Math.PI / 2);
  const surf = new THREE.Mesh(geo, surfMat); surf.position.set(cx, state.level, cz); surf.frustumCulled = false; surf.renderOrder = 5; scene.add(surf);

  // ---- caustics on the floor plane (unchanged from water_simple)
  const causMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uT: { value: 0 }, uStr: { value: 0 } },
    vertexShader: `varying vec3 vWp; void main(){ vWp=(modelMatrix*vec4(position,1.0)).xyz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `varying vec3 vWp; uniform float uT; uniform float uStr; void main(){ vec2 p=vWp.xz*1.3; float v = sin(p.x*3.0+uT)*sin(p.y*2.4-uT*1.2) + sin((p.x+p.y)*2.2+uT*0.7); v = pow(max(v,0.0),3.0); gl_FragColor=vec4(vec3(0.5,0.8,0.9)*v*uStr,1.0);} ` });
  const caus = new THREE.Mesh(new THREE.PlaneGeometry(W, D), causMat); caus.rotation.x = -Math.PI / 2; caus.position.set(cx, 0.06, cz); caus.renderOrder = 4; scene.add(caus);

  const airFog = { color: new THREE.Color(0x0b0f14), near: 60, far: 900 };
  scene.fog = new THREE.Fog(airFog.color.clone(), airFog.near, airFog.far);
  const tint = document.createElement('div'); tint.style.cssText = 'position:fixed;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:0;transition:opacity .4s;background:#1a8fa8'; document.body.appendChild(tint);

  // ---- planar reflection + refraction grab (rendered from surf.onBeforeRender for the main camera only)
  let reflRT = null, refrRT = null, busy = false, lastFrame = -1, skinMesh = null;
  const virtualCam = new THREE.PerspectiveCamera(), _v2 = new THREE.Vector2();
  const rPos = new THREE.Vector3(), cPos = new THREE.Vector3(), normal = new THREE.Vector3(), view = new THREE.Vector3(), look = new THREE.Vector3(), target = new THREE.Vector3(), rot = new THREE.Matrix4(), plane = new THREE.Plane(), clip = new THREE.Vector4(), qv = new THREE.Vector4();
  function ensureTargets() {
    renderer.getDrawingBufferSize(_v2); const w = Math.max(64, Math.round(_v2.x)), h = Math.max(64, Math.round(_v2.y));
    const rw = Math.max(32, Math.round(w * params.refrScale)), rh = Math.max(32, Math.round(h * params.refrScale)), qw = Math.max(32, Math.round(w * params.reflScale)), qh = Math.max(32, Math.round(h * params.reflScale));
    if (!refrRT || refrRT.width !== rw || refrRT.height !== rh) {
      if (refrRT) { refrRT.dispose(); refrRT.depthTexture.dispose(); }
      refrRT = new THREE.WebGLRenderTarget(rw, rh, { type: THREE.HalfFloatType, format: THREE.RGBAFormat, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: true });
      refrRT.depthTexture = new THREE.DepthTexture(rw, rh, THREE.UnsignedIntType); refrRT.depthTexture.minFilter = refrRT.depthTexture.magFilter = THREE.NearestFilter;
    }
    if (!reflRT || reflRT.width !== qw || reflRT.height !== qh) {
      if (reflRT) reflRT.dispose();
      reflRT = new THREE.WebGLRenderTarget(qw, qh, { type: THREE.HalfFloatType, format: THREE.RGBAFormat, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: true });
    }
    surfU.uRefr.value = refrRT.texture; surfU.uDepth.value = refrRT.depthTexture; surfU.uRefl.value = reflRT.texture; surfU.uInvRes.value.set(1 / w, 1 / h);
  }
  function findSkin() { if (skinMesh) return skinMesh; scene.traverse((o) => { if (!skinMesh && o.material && o.material.uniforms && o.material.uniforms.uClipN) skinMesh = o; }); return skinMesh; }
  function passes(cam, under) {
    ensureTargets();
    const prevRT = renderer.getRenderTarget(), prevXr = renderer.xr.enabled, prevShadow = renderer.shadowMap.autoUpdate, prevAuto = renderer.autoClear;
    renderer.xr.enabled = false; renderer.shadowMap.autoUpdate = false; renderer.autoClear = true;
    surf.visible = false;
    const fog = scene.fog, bg = scene.background, fogSave = fog ? { c: fog.color.clone(), n: fog.near, f: fog.far } : null;
    // refraction grab: the scene behind the surface (from below: the world above, so use the air fog)
    if (under && fog) { fog.color.copy(airFog.color); fog.near = airFog.near; fog.far = airFog.far; }
    renderer.setRenderTarget(refrRT); renderer.render(scene, cam);
    if (under && fog) { fog.color.copy(fogSave.c); fog.near = fogSave.n; fog.far = fogSave.f; }
    // planar reflection with a mirrored camera and an oblique near plane (three/addons/objects/Reflector.js)
    if (params.reflection) {
      rPos.set(cx, surf.position.y, cz); cPos.setFromMatrixPosition(cam.matrixWorld); normal.set(0, under ? -1 : 1, 0);
      view.subVectors(rPos, cPos); view.reflect(normal).negate(); view.add(rPos);
      rot.extractRotation(cam.matrixWorld); look.set(0, 0, -1).applyMatrix4(rot).add(cPos);
      target.subVectors(rPos, look); target.reflect(normal).negate(); target.add(rPos);
      virtualCam.position.copy(view); virtualCam.up.set(0, 1, 0).applyMatrix4(rot).reflect(normal); virtualCam.lookAt(target);
      virtualCam.near = cam.near; virtualCam.far = cam.far; virtualCam.updateMatrixWorld(); virtualCam.projectionMatrix.copy(cam.projectionMatrix);
      const tm = surfU.uTexMat.value; tm.set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1); tm.multiply(virtualCam.projectionMatrix); tm.multiply(virtualCam.matrixWorldInverse);
      plane.setFromNormalAndCoplanarPoint(normal, rPos); plane.applyMatrix4(virtualCam.matrixWorldInverse); clip.set(plane.normal.x, plane.normal.y, plane.normal.z, plane.constant);
      const pm = virtualCam.projectionMatrix; qv.x = (Math.sign(clip.x) + pm.elements[8]) / pm.elements[0]; qv.y = (Math.sign(clip.y) + pm.elements[9]) / pm.elements[5]; qv.z = -1; qv.w = (1 + pm.elements[10]) / pm.elements[14];
      clip.multiplyScalar(2 / clip.dot(qv)); pm.elements[2] = clip.x; pm.elements[6] = clip.y; pm.elements[10] = clip.z + 1 - 0.003; pm.elements[14] = clip.w;
      // the raymarched pool skin reads its own camera uniforms: give it the mirrored camera for this pass
      const sk = findSkin(); let saved = null;
      if (sk && sk.visible) {
        const u = sk.material.uniforms; saved = { p: u.uCamPos.value.clone(), pr: u.uProj.value.clone(), v: u.uView.value.clone() };
        u.uCamPos.value.copy(virtualCam.position); u.uProj.value.copy(pm); u.uView.value.copy(virtualCam.matrixWorldInverse);
        u.uClipN.value.set(0, under ? -1 : 1, 0); u.uClipD.value = under ? -rPos.y : rPos.y;
      }
      renderer.setRenderTarget(reflRT); renderer.render(scene, virtualCam);
      if (saved) { const u = sk.material.uniforms; u.uCamPos.value.copy(saved.p); u.uProj.value.copy(saved.pr); u.uView.value.copy(saved.v); u.uClipN.value.set(0, 0, 0); u.uClipD.value = 0; }
    }
    surf.visible = true; scene.background = bg;
    renderer.setRenderTarget(prevRT); renderer.xr.enabled = prevXr; renderer.shadowMap.autoUpdate = prevShadow; renderer.autoClear = prevAuto;
  }
  surf.onBeforeRender = (r, sc, cam) => {
    surfU.uCamP.value.copy(cam.position);
    if (cam !== camera || busy) { surfU.uMode.value = 1; return; }               // dome faces and anything else: cheap path
    surfU.uMode.value = 0; surfU.uCamNear.value = cam.near; surfU.uCamFar.value = cam.far;
    busy = true; try { passes(cam, cam.position.y < surf.position.y); } finally { busy = false; }
  };

  // ---- API
  function isWet(x, y, z) { return y < state.level && insideFootprint(x, z, 0.5); }
  let lastT = 0;
  function update(dt, t, cam, dry) {
    if (state.flooding) { state.level = THREE.MathUtils.damp(state.level, state.target, 0.8, dt); if (Math.abs(state.level - state.target) < 0.02) state.flooding = false; }
    surf.position.y = state.level; causMat.uniforms.uT.value = t;
    if (!cascades.length) makeCascades();
    if (surf.visible) { if (specDirty) computeSpectra(); evolve(Math.max(dt, 1e-3), t); }
    cascades.forEach((c, i) => { const o = c.out[1 - c.cur]; surfU['uD' + i].value = o.textures[0]; surfU['uS' + i].value = o.textures[1]; surfU['uM' + i].value = o.textures[2]; });
    const wet = !dry && isWet(cam.x, cam.y, cam.z);
    surfU.uTime.value = t; surfU.uLevel.value = state.level; surfU.uReflect.value = params.reflection ? 1 : 0; surfU.uGlitter.value = params.glitter; surfU.uFoam.value = params.foam > 0.001 ? 0.35 + 0.65 * params.foam : 0;
    surfU.uSunI.value = params.sunIntensity; surfU.uDensity.value = params.density; surfU.uSun.value.copy(sunDir);
    causMat.uniforms.uStr.value = state.level > 0.3 ? THREE.MathUtils.clamp((state.level - 0.3) / 3, 0, 1) * 0.18 : 0;
    let res;
    if (wet) {
      const lay = layerAt(cam.y); const c = new THREE.Color(lay.color);
      scene.fog.color.lerp(c, 0.15); scene.fog.near = THREE.MathUtils.lerp(scene.fog.near, lay.fogNear, 0.15); scene.fog.far = THREE.MathUtils.lerp(scene.fog.far, lay.fogFar, 0.15);
      scene.background = scene.fog.color; tint.style.background = '#' + c.getHexString(); tint.style.opacity = '0.35'; surfU.uLight.value = lay.light;
      res = { wet, layer: lay };
    } else {
      scene.fog.color.lerp(airFog.color, 0.2); scene.fog.near = THREE.MathUtils.lerp(scene.fog.near, airFog.near, 0.2); scene.fog.far = THREE.MathUtils.lerp(scene.fog.far, airFog.far, 0.2); scene.background = scene.fog.color; tint.style.opacity = '0'; surfU.uLight.value = 1;
      res = { wet: false, layer: null };
    }
    surfU.uFogColor.value.copy(scene.fog.color); surfU.uFogNear.value = scene.fog.near; surfU.uFogFar.value = scene.fog.far;
    return res;
  }
  function setTarget(y) { state.target = y; state.flooding = true; }
  function toggle() { setTarget(state.target > 5 ? L.levels.aquarium - 0.2 : L.levels.roofSlab - 0.3); }
  function setParam(name, v) {
    if (!(name in params)) return;
    params[name] = v;
    if (name === 'fftSize') { makeCascades(); return; }
    if (name === 'patch') { makeCascades(); return; }
    if (SPECTRAL.has(name)) specDirty = true;
  }
  function setSun(vec) { sunDir.copy(vec).normalize(); }
  // debug: RMS of height per cascade + foam coverage (reads the half-float output back)
  async function debug() {
    const out = [];
    for (const c of cascades) {
      const o = c.out[1 - c.cur], n = c.N; const buf = new Uint16Array(n * n * 4); const buf2 = new Uint16Array(n * n * 4);
      renderer.readRenderTargetPixels(o, 0, 0, n, n, buf, undefined, 0); renderer.readRenderTargetPixels(o, 0, 0, n, n, buf2, undefined, 1);
      let s = 0, s2 = 0, fm = 0, mx = 0, sl = 0; for (let i = 0; i < n * n; i++) { const h = half(buf[i * 4 + 1]); s += h; s2 += h * h; mx = Math.max(mx, Math.abs(h)); const sx = half(buf2[i * 4]), sz = half(buf2[i * 4 + 1]); sl += sx * sx + sz * sz; if (half(buf2[i * 4 + 2]) > 0.2) fm++; }
      const m = s / (n * n); out.push({ N: n, patch: c.L, rms: Math.sqrt(s2 / (n * n) - m * m), maxAbs: mx, slopeRms: Math.sqrt(sl / (n * n)), foamFrac: fm / (n * n) });
    }
    return out;
  }
  return { meshes: [surf, caus], state, update, setTarget, toggle, isWet, surface: surf, params, setParam, setSun, sunDir, debug, cascades: () => cascades, isOcean: true };
}
