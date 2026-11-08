// Flood state, water surface and underwater atmosphere (stratified layers).
import * as THREE from 'three';
import { L, layerAt, insideFootprint } from './layout.js';

export function buildWater(scene) {
  const B = L.bbox, W = B.x1 - B.x0, D = B.z1 - B.z0;
  const state = { level: L.levels.aquarium - 0.2, target: L.levels.aquarium - 0.2, speed: 0.6, flooding: false };
  const surfMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uT: { value: 0 }, uColor: { value: new THREE.Color(0x3fb6d8) }, uUnder: { value: 0 } },
    vertexShader: `varying vec2 vUv; varying vec3 vWp; uniform float uT; void main(){ vUv=uv; vec3 p=position; p.y += 0.06*sin(p.x*0.8+uT*1.3)+0.05*sin(p.z*1.1-uT*1.7); vWp=(modelMatrix*vec4(p,1.0)).xyz; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);} `,
    fragmentShader: `varying vec2 vUv; varying vec3 vWp; uniform float uT; uniform vec3 uColor; uniform float uUnder;
      void main(){ float c = 0.5+0.5*sin(vWp.x*2.1+uT*2.0)*sin(vWp.z*1.7-uT*1.4); float a = mix(0.55, 0.85, uUnder);
      vec3 col = mix(uColor, vec3(0.9,0.98,1.0), c*0.25); gl_FragColor = vec4(col, a*(0.6+0.4*c)); }`
  });
  const surf = new THREE.Mesh(new THREE.PlaneGeometry(W, D, 80, 60), surfMat); surf.rotation.x = -Math.PI / 2; surf.position.set((B.x0 + B.x1) / 2, state.level, (B.z0 + B.z1) / 2); surf.renderOrder = 5; scene.add(surf);
  // Caustic light pattern projected on floors: a large plane with additive animated texture under the surface (cheap)
  const causMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uT: { value: 0 }, uStr: { value: 0 } },
    vertexShader: `varying vec3 vWp; void main(){ vWp=(modelMatrix*vec4(position,1.0)).xyz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} `,
    fragmentShader: `varying vec3 vWp; uniform float uT; uniform float uStr; void main(){ vec2 p=vWp.xz*1.3; float v = sin(p.x*3.0+uT)*sin(p.y*2.4-uT*1.2) + sin((p.x+p.y)*2.2+uT*0.7); v = pow(max(v,0.0),3.0); gl_FragColor=vec4(vec3(0.5,0.8,0.9)*v*uStr,1.0);} ` });
  const caus = new THREE.Mesh(new THREE.PlaneGeometry(W, D), causMat); caus.rotation.x = -Math.PI / 2; caus.position.set((B.x0 + B.x1) / 2, 0.06, (B.z0 + B.z1) / 2); caus.renderOrder = 4; scene.add(caus);

  const airFog = { color: new THREE.Color(0x0b0f14), near: 60, far: 900 };
  scene.fog = new THREE.Fog(airFog.color.clone(), airFog.near, airFog.far);
  const tint = document.createElement('div'); tint.style.cssText = 'position:fixed;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:0;transition:opacity .4s;background:#1a8fa8'; document.body.appendChild(tint);

  function isWet(x, y, z) { return y < state.level && insideFootprint(x, z, 0.5); }
  function update(dt, t, cam, dry) {
    if (state.flooding) { state.level = THREE.MathUtils.damp(state.level, state.target, 0.8, dt); if (Math.abs(state.level - state.target) < 0.02) state.flooding = false; }
    surf.position.y = state.level; surfMat.uniforms.uT.value = t; causMat.uniforms.uT.value = t;
    const wet = !dry && isWet(cam.x, cam.y, cam.z);
    surfMat.uniforms.uUnder.value = wet ? 1 : 0;
    causMat.uniforms.uStr.value = state.level > 0.3 ? THREE.MathUtils.clamp((state.level - 0.3) / 3, 0, 1) * 0.18 : 0;
    if (wet) {
      const lay = layerAt(cam.y); const c = new THREE.Color(lay.color);
      scene.fog.color.lerp(c, 0.15); scene.fog.near = THREE.MathUtils.lerp(scene.fog.near, lay.fogNear, 0.15); scene.fog.far = THREE.MathUtils.lerp(scene.fog.far, lay.fogFar, 0.15);
      scene.background = scene.fog.color; tint.style.background = '#' + c.getHexString(); tint.style.opacity = '0.35';
      return { wet, layer: lay };
    }
    scene.fog.color.lerp(airFog.color, 0.2); scene.fog.near = THREE.MathUtils.lerp(scene.fog.near, airFog.near, 0.2); scene.fog.far = THREE.MathUtils.lerp(scene.fog.far, airFog.far, 0.2); scene.background = scene.fog.color; tint.style.opacity = '0';
    return { wet: false, layer: null };
  }
  function setTarget(y) { state.target = y; state.flooding = true; }
  function toggle() { setTarget(state.target > 5 ? L.levels.aquarium - 0.2 : L.levels.roofSlab - 0.3); }
  return { meshes: [surf, caus], state, update, setTarget, toggle, isWet, surface: surf };
}
