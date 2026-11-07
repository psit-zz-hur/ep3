// Optional: the legacy Google-era SketchUp model of the building from 3D Warehouse
// (id 1a4c209a43561ba445f5590ac69325a5, 3,694 polygons, 27 materials, georeferenced, SKP8/KMZ/GLB).
// Download it yourself with a free Trimble account (GLB or KMZ->Collada), save as game/assets/cas_3dwarehouse.glb,
// then open the game with ?model=1. The transform below aligns 3D Warehouse's local frame to the lidar frame;
// tune MODEL_ALIGN once and commit the numbers.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { L } from './layout.js';

export const MODEL_ALIGN = {
  scale: 1.0,              // GLB from 3D Warehouse is in metres; a Collada from KMZ may be in inches (0.0254)
  rotationY: THREE.MathUtils.degToRad(137.5 - 180),  // site rotation applied to the lidar frame (site_meta.json), sign/offset to verify on the laptop
  offset: new THREE.Vector3(0, 0, 0),                  // translate after rotation so the roof lands on the lidar roof (deck at y = 11.45)
  opacity: 0.6,
};

export async function loadWarehouseModel(scene, url = './assets/cas_3dwarehouse.glb') {
  const head = await fetch(url, { method: 'HEAD' }).catch(() => null);
  if (!head || !head.ok) return null;
  const gltf = await new GLTFLoader().loadAsync(url);
  const root = gltf.scene; root.name = 'cas-3dwarehouse';
  root.traverse((o) => { if (o.isMesh) { o.material = o.material.clone(); o.material.transparent = true; o.material.opacity = MODEL_ALIGN.opacity; o.material.side = THREE.DoubleSide; } });
  // centre the model's footprint on the building centre, floor at main level, then apply the alignment
  const box = new THREE.Box3().setFromObject(root); const c = box.getCenter(new THREE.Vector3());
  root.position.set(-c.x, -box.min.y, -c.z); const g = new THREE.Group(); g.add(root);
  g.scale.setScalar(MODEL_ALIGN.scale); g.rotation.y = MODEL_ALIGN.rotationY; g.position.copy(MODEL_ALIGN.offset); g.position.y += L.levels.main;
  scene.add(g); console.log('3D Warehouse model loaded', box.getSize(new THREE.Vector3()));
  return g;
}
