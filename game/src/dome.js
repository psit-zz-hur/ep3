// Domemaster (equidistant fisheye, 180 deg, front at bottom) renderer for fulldome playback,
// with the registration pattern overlay. Convention follows the IMERSA Dome Master spec.
import * as THREE from 'three';

export function buildDome(renderer, scene, camera, opts = {}) {
  const faceRes = opts.faceRes || 1024, outRes = opts.outRes || 2048;
  const cubeRT = new THREE.WebGLCubeRenderTarget(faceRes, { generateMipmaps: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
  const cubeCam = new THREE.CubeCamera(0.1, 2000, cubeRT);
  const outRT = new THREE.WebGLRenderTarget(outRes, outRes);
  const fishMat = new THREE.ShaderMaterial({
    uniforms: { uCube: { value: cubeRT.texture }, uRot: { value: new THREE.Matrix3() }, uFov: { value: Math.PI }, uTilt: { value: THREE.MathUtils.degToRad(30) }, uGrid: { value: null }, uGridMix: { value: 0 }, uHorizon: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
    fragmentShader: `precision highp float; varying vec2 vUv; uniform samplerCube uCube; uniform mat3 uRot; uniform float uFov; uniform float uTilt; uniform sampler2D uGrid; uniform float uGridMix; uniform float uHorizon;
      void main(){
        vec2 p = vUv * 2.0 - 1.0; float r = length(p);
        if (r > 1.0) { gl_FragColor = vec4(0.0,0.0,0.0,1.0); return; }
        float theta = r * uFov * 0.5;            // equidistant: angle from the dome apex
        float phi = atan(p.y, p.x);
        // dome frame: right=+X, apex=+Y, front=-Z (front of dome = bottom of the image, p.y = -1)
        vec3 d = vec3(sin(theta) * cos(phi), cos(theta), sin(theta) * sin(phi));
        // pitch the lookup so the game horizon sits near the audience sweet spot on a tilted dome
        float c = cos(uTilt), s = sin(uTilt);
        d = vec3(d.x, d.y * c - d.z * s, d.y * s + d.z * c);
        vec3 w = uRot * d;
        vec4 col = textureCube(uCube, vec3(-w.x, w.y, w.z));  // three.js cubemap handedness
        // faint horizon ring for calibration
        float h = 1.0 - smoothstep(0.0, 0.004, abs(w.y));
        col.rgb += h * uHorizon * vec3(1.0, 0.6, 0.2);
        if (uGridMix > 0.0) { vec4 gtex = texture2D(uGrid, vUv); col.rgb = mix(col.rgb, gtex.rgb, uGridMix * gtex.a); }
        gl_FragColor = vec4(col.rgb, 1.0);
      }`
  });
  const quadScene = new THREE.Scene(); const quadCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), fishMat));
  // on-screen presentation of the square domemaster (letterboxed)
  const showMat = new THREE.MeshBasicMaterial({ map: outRT.texture });
  const showScene = new THREE.Scene(); const showQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), showMat); showScene.add(showQuad);
  const showCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  new THREE.TextureLoader().load('./assets/dome_registration_pdb_v14.png', (t) => { t.colorSpace = THREE.SRGBColorSpace; fishMat.uniforms.uGrid.value = t; });
  const state = { enabled: false, gridMix: 0, tiltDeg: 30, fovDeg: 180, horizon: 0 };
  const rot = new THREE.Matrix3(); const q = new THREE.Quaternion(); const m4 = new THREE.Matrix4();

  function render(hiddenForCapture) {
    cubeCam.position.copy(camera.position); cubeCam.update(renderer, scene);
    camera.getWorldQuaternion(q); m4.makeRotationFromQuaternion(q); rot.setFromMatrix4(m4); fishMat.uniforms.uRot.value.copy(rot);
    fishMat.uniforms.uTilt.value = THREE.MathUtils.degToRad(state.tiltDeg); fishMat.uniforms.uFov.value = THREE.MathUtils.degToRad(state.fovDeg); fishMat.uniforms.uGridMix.value = state.gridMix; fishMat.uniforms.uHorizon.value = state.horizon;
    renderer.setRenderTarget(outRT); renderer.render(quadScene, quadCam); renderer.setRenderTarget(null);
    if (hiddenForCapture) return;
    const w = renderer.domElement.width, h = renderer.domElement.height; const sz = Math.min(w, h);
    renderer.setViewport((w - sz) / 2, (h - sz) / 2, sz, sz); renderer.setScissor((w - sz) / 2, (h - sz) / 2, sz, sz); renderer.setScissorTest(true);
    renderer.render(showScene, showCam); renderer.setScissorTest(false); renderer.setViewport(0, 0, w, h);
  }
  function capture(res = 4096) {
    // render once at full res and download a PNG domemaster
    const big = new THREE.WebGLRenderTarget(res, res); const bigCube = new THREE.WebGLCubeRenderTarget(Math.min(res / 2, 2048)); const bc = new THREE.CubeCamera(0.1, 2000, bigCube);
    bc.position.copy(camera.position); bc.update(renderer, scene); const prev = fishMat.uniforms.uCube.value; fishMat.uniforms.uCube.value = bigCube.texture;
    renderer.setRenderTarget(big); renderer.render(quadScene, quadCam); const px = new Uint8Array(res * res * 4); renderer.readRenderTargetPixels(big, 0, 0, res, res, px); renderer.setRenderTarget(null); fishMat.uniforms.uCube.value = prev;
    const c = document.createElement('canvas'); c.width = res; c.height = res; const g = c.getContext('2d'); const id = g.createImageData(res, res);
    for (let y = 0; y < res; y++) id.data.set(px.subarray((res - 1 - y) * res * 4, (res - y) * res * 4), y * res * 4); // flip Y
    g.putImageData(id, 0, 0); big.dispose(); bigCube.dispose();
    const a = document.createElement('a'); a.download = `freeswim_domemaster_${res}_${Date.now()}.png`; a.href = c.toDataURL('image/png'); a.click();
  }
  return { state, render, capture };
}
