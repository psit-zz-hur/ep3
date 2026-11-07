// Scuba presence: mask vignette, breathing cycle (buoyancy rise on inhale, sink on exhale), exhaled bubbles,
// and a "hover" mode for reading plaques (hold R or look at a plaque and stop moving).
import * as THREE from 'three';

export function buildDiver(scene, camera) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;inset:0;pointer-events:none;opacity:0;transition:opacity .6s;background:radial-gradient(ellipse 62% 58% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 78%, rgba(0,0,0,.92) 100%)';
  document.body.appendChild(el);
  // mask frame edge + faint glass smear
  const glass = document.createElement('div'); glass.style.cssText = 'position:fixed;inset:0;pointer-events:none;opacity:0;transition:opacity .6s;background:radial-gradient(circle at 30% 20%, rgba(255,255,255,.08), transparent 35%), radial-gradient(circle at 70% 80%, rgba(255,255,255,.05), transparent 30%)'; document.body.appendChild(glass);
  const breathUI = document.createElement('div'); breathUI.style.cssText = 'position:fixed;left:50%;bottom:36px;transform:translateX(-50%);width:120px;height:3px;background:rgba(255,255,255,.12);pointer-events:none;opacity:0;transition:opacity .6s'; const breathBar = document.createElement('div'); breathBar.style.cssText = 'height:100%;width:50%;background:rgba(200,240,255,.7)'; breathUI.appendChild(breathBar); document.body.appendChild(breathUI);

  // bubbles: small instanced spheres rising from the regulator
  const N = 160; const geo = new THREE.SphereGeometry(0.035, 6, 5); const mat = new THREE.MeshPhysicalMaterial({ color: 0xdff6ff, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.75, transmission: 0.2 });
  const mesh = new THREE.InstancedMesh(geo, mat, N); mesh.frustumCulled = false; mesh.visible = false; scene.add(mesh);
  const b = []; for (let i = 0; i < N; i++) b.push({ p: new THREE.Vector3(), v: new THREE.Vector3(), life: -1, s: 1 });
  const dummy = new THREE.Object3D(); const fwd = new THREE.Vector3(), right = new THREE.Vector3();
  const state = { t: 0, phase: 0, period: 4.6, inhale: 0, breathOffset: 0, wet: false, bubbleTimer: 0 };

  function update(dt, wet, waterY, hovering) {
    state.wet = wet; el.style.opacity = wet ? '1' : '0'; glass.style.opacity = wet ? '1' : '0'; breathUI.style.opacity = wet ? '1' : '0'; mesh.visible = wet;
    if (!wet) { state.breathOffset = 0; return 0; }
    state.t += dt; const ph = (state.t % state.period) / state.period;  // 0..1, inhale first 40%, exhale 60%
    const inh = ph < 0.4 ? Math.sin(ph / 0.4 * Math.PI / 2) : Math.cos((ph - 0.4) / 0.6 * Math.PI / 2);
    state.inhale = inh; breathBar.style.width = (20 + 60 * inh) + '%';
    // buoyancy: lungs full -> slight rise, empty -> slight sink. ~ +-8 cm when hovering, less when swimming
    state.breathOffset = (inh - 0.5) * (hovering ? 0.16 : 0.06);
    // bubbles on exhale
    const exhaling = ph >= 0.4 && ph < 0.75;
    state.bubbleTimer -= dt;
    camera.getWorldDirection(fwd); right.crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
    if (exhaling && state.bubbleTimer <= 0) {
      state.bubbleTimer = 0.05; const n = 3 + Math.floor(Math.random() * 3);
      for (let k = 0; k < n; k++) { const bb = b.find(x => x.life < 0); if (!bb) break; bb.p.copy(camera.position).addScaledVector(fwd, 0.25).addScaledVector(right, (Math.random() - 0.5) * 0.12); bb.p.y -= 0.12; bb.v.set((Math.random() - 0.5) * 0.3, 0.6 + Math.random() * 0.5, (Math.random() - 0.5) * 0.3).addScaledVector(fwd, 0.3); bb.life = 0; bb.s = 0.5 + Math.random() * 1.2; }
    }
    for (let i = 0; i < N; i++) {
      const bb = b[i];
      if (bb.life >= 0) { bb.life += dt; bb.v.y += dt * 1.2; bb.v.x += Math.sin(bb.life * 9 + i) * dt * 0.6; bb.v.z += Math.cos(bb.life * 7 + i) * dt * 0.6; bb.p.addScaledVector(bb.v, dt); bb.s += dt * 0.4; if (bb.p.y > waterY - 0.05 || bb.life > 6) bb.life = -1; }
      dummy.position.copy(bb.life >= 0 ? bb.p : new THREE.Vector3(0, -999, 0)); dummy.scale.setScalar(bb.life >= 0 ? bb.s : 0.001); dummy.updateMatrix(); mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    return state.breathOffset;
  }
  return { update, state };
}
