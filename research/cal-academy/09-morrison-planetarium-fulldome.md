# Morrison Planetarium — projection system, formats, and getting a real-time app onto the dome

Research track report (7 Nov 2026). Academy pages were read in full; vendor/integrator facts are from
search summaries and are marked [search].

## 1. Dome specs
| Item | Value | Source |
|---|---|---|
| Screen diameter | 75 ft / 23 m (Spitz lists 22.9 m); outer architectural dome ~90 ft | Academy exhibit page; Spitz NanoSeam reference [search] |
| Tilt | 30° | Spitz reference doc; SFCV venue page [search] |
| Dome elevation | 165° (screen extends ~15° below the spring line) | Spitz reference [search, medium] |
| Seating | 290 theatre seats; 100 reception; ~1,300 sq ft | Academy Plan-an-Event |
| Screen | Spitz NanoSeam perforated aluminium on a recycled-steel frame | Academy exhibit page; Spitz customer lists |
| Opened | Sept 2008 (1952 65-ft dome retired 2003) | Academy blog |
| Seating orientation | Unidirectional, facing front; laser shows "much more difficult given the tilted configuration" | Academy blog |

## 2. Projection history
| Era | System |
|---|---|
| 2008 | Global Immersion Fidelity Bright: six projectiondesign F30 sx+ (1400x1050), edge-blended, ~3600² effective; Global Immersion media server + Sky-Skan Definiti cluster + SCISS Uniview real-time cluster [search] |
| 2016-17 upgrade (Mechdyne, TEECOM) | **Six Sony VPL-GTZ270 4K SXRD laser projectors** (4096x2160, 5,000 lm; five around, one at zenith); GBvi Chronos optical blending; Scalable Display Manager camera warp/blend; **7thSense Delta media server**; one Mechdyne Dome Display Manager per projector (6 inputs, cross-fade, warp applied inside); Barco Medialon show control; Uniview retained as a DDM input; custom 4K60 cross-fade [search: Mechdyne, Installation International, Scalable, GBvi] |
| 2019 Academy statement | "six 4K resolution video outputs ... about 30 million pixels on our dome" (Academy blog) |
| 2023-26 | No refresh found. GTZ270 discontinued 2021; confirm with Planetarium Engineering. |

Resolution: ~30 Mpx raw across six 4K channels; single-domemaster equivalent not published (between 4K and ~6K). Signal chain built for 4K60. Produced shows are 30 fps. No published gamma/colour spec; industry norm Rec.709, gamma 2.2-2.4.

## 3. Playback and real-time software
- Pre-rendered: 7thSense Delta (frame-sequence playback, dome-master fisheye mode, NDI capture since Delta 2.8, Datapath capture cards).
- Real-time: **OpenSpace** drives the live shows ("Tour of the Universe" daily, "Tour of the Solar System", NightLife live shows, monthly "Cosmic Conversations"); legacy SCISS Uniview cluster still an input. Not Digistar, not Sky-Skan Dark Matter.
- Visualization Studio: Houdini-based pipeline, PipelineFX Qube render farm, in-house dailies dome playback; nine in-house shows 2008-2023, "Timescapes" (2025).
- External real-time input: architecturally yes (DDM inputs, Delta NDI/capture). **Unknown** whether the chain accepts one domemaster and slices/warps it to six projectors, or needs six genlocked per-projector 4K channels warped with Scalable mesh files. Ask Planetarium Engineering.

## 4. Formats
- Academy licensing page: **"All shows are filmed in 4K at 30 fps, and feature 5.1 stereo audio."** Contacts: businesspartnerships@calacademy.org (licensing), planet@calacademy.org (studio). Distribution partners include Cosm/E&S, Sky-Skan, Loch Ness, RSA Cosmos, e-Planetarium, Fulldome Film Society. Shows: Expedition Reef (2018, 1K-4K, 30 fps, 5.1), Habitat Earth (2015), Living Worlds (2021, 4K/30), Spark (2023), Earthquake, Life, Fragile Planet, Incoming!, Big Astronomy, Timescapes.
- Industry master spec to follow (IMERSA Dome Master Specifications 2019, https://imersa.org/images/standards/Dome_Master_Specifications_2019.pdf): equidistant azimuthal fisheye, 180° x 360°; square frame with the circle inscribed; outside the circle black except show name / timecode / frame number upper-left; resolutions 1024-4096 "or greater"; image sequences (host slices/encodes) plus an HD .mov preview and poster; audio as per-channel WAV stems (_L,_R,_Ls,_Rs,_C,_LFE); **bottom of frame = front of dome**; safe area roughly 10-60° latitude.
- Facility examples: Melbourne Planetarium delivery spec (six 4K projectors; H.264 MP4 or image sequence + separate audio); festivals accept HEVC MP4 at 4096²; Cosm/LED domes want 16-bit TIFF/DPX/EXR, Rec.709 g2.4 or P3/XYZ g2.6.
- Conversions: Paul Bourke's dome pages (cube2fish, fishtilt, test patterns) http://paulbourke.net/dome/ ; ffmpeg v360.

## 5. Real-time on a dome: techniques
- Core: render a cubemap, resample to an equidistant fisheye in a fragment shader (θ = r·90° for 180°). Five cube faces suffice.
- Unity: rsodre/FulldomeCameraForUnity, prefrontalcortex/DomeTools (NDI), XJINE/Unity_DomeMaster. Unreal: nDisplay + Scalable plugin. OpenSpace/SGCT: `FisheyeProjection` with `fov`, `quality`, **`tilt`** (for tilted domes) and warp meshes, which is a good proxy for what Morrison's chain expects since it already runs OpenSpace.
- Three.js: no canonical example; drei `<Fisheye>`, prohfessor/fulldome-web-player, diroru/domemod, sonarkon/Dome-Sim. Our `game/src/dome.js` implements the cubemap-to-domemaster path with tilt, FOV and registration-grid overlay.

## 6. The registration pattern ("PDB V14 2560")
Consistent with Paul D. Bourke's "Digital fulldome test pattern" (first released June 2018, versions v09-v12 visible online, page updated 2022): resolution wedges, colour and grey patches, concentric rings, 0-360° azimuth marks and 10-80° elevation rings, with identifying text and the version number at the pole. "PDB" = Bourke's initials, "V14" = version 14, "2560" = the rendered size of that file (the supplied copy is 2000 px). Use: project at increasing resolutions until a higher-resolution pattern no longer looks sharper; the polar grid verifies orientation (front at bottom), centering and per-projector alignment. Free to use unmodified. [PDB/V14 reading is an inference; paulbourke.net was unreachable.]

## 7. Recommended pipeline for the Three.js app
1. Game camera for input; a `CubeCamera` at the viewer with 2048 px faces (≈1:1 sampling for a 4096² output).
2. Fisheye shader: p = (2u-1, 2v-1), r = |p|, θ = r·fov/2 (fov 180°, optionally 165° to match the dome), φ = atan2; dome frame right=+X, apex=+Y, front=−Z (front at bottom); apply a configurable pitch (SGCT-style tilt, ≈30°) before the cubemap lookup so the horizon lands near the audience sweet spot; mind three.js cubemap handedness. Output sRGB, black outside the circle, optional show name and frame counter upper-left.
3. Live output: a 4K60 DP/HDMI feed into a DDM input or NDI into 7thSense Delta. On a 3840x2160 output the live domemaster is 2160² unless a square timing is accepted.
4. Offline fallback that matches the house format exactly: 4096² PNG/TIFF sequence at 30 fps + 5.1 WAV stems + HD preview, playable from Delta. The game's P key saves single 4096² frames; a fixed-step capture loop is the next step.
5. Validate with the PDB pattern loaded directly as a domemaster, then with the in-game horizon ring (uHorizon) to tune tilt.
6. Hardware: RTX-class PC; budget 30 fps at 4096² or 60 fps at ~3072².

## 8. Getting a demo onto the dome
- Contacts: planet@calacademy.org (Morrison Planetarium & Visualization Studio); businesspartnerships@calacademy.org; specialevents@calacademy.org, (415) 379-5497, https://www.calacademy.org/plan-an-event (planetarium: 290 seats).
- People (Academy MPVS staff page): Ryan Wyatt, Senior Director of Morrison Planetarium and Science Visualization; Matthew Wrenne, Manager of Planetarium Engineering ("bringing researchers' work into the dome ... real-time systems"); Dylan Salas and Jamie Rogers, Planetarium & Production Support Engineers; Jon Britton; Dennis Alikpala (show distribution); Jacque Benitez (programs).
- Precedents for outside real-time content: NightLife "Vortex 2.0" events showcasing outside fulldome artists; Benjamin Dean lectures where engineers put researcher content on the dome; daily OpenSpace live tours.
- Hiring signals: "Planetarium & Production Support Engineer" (Greenhouse, Experience Engineering team); an "Associate Director of Experience Design" listing (Experience Studio).
- Suggested approach: send a 4096² domemaster test render plus the PDB grid to planet@ and Planetarium Engineering and ask for the input spec; propose a NightLife/Vortex slot or Dean-lecture tech demo; bring a live build (NDI + DP 4K60) and a PNG-sequence fallback.

## Unverified
Single-domemaster vs six-channel input; current projectors; colour/gamma spec; effective resolution; NanoSeam vs "Astro-tec" attribution; 165° elevation figure; PDB V14 reading; IMERSA frame-rate/bit-depth details; no public Academy delivery-spec document.

## Key sources
https://www.calacademy.org/exhibits/morrison-planetarium · https://www.calacademy.org/fulldome-show-licensing · https://www.calacademy.org/mpvs · https://www.calacademy.org/staff-biographies-mpvs · https://www.calacademy.org/plan-an-event · https://www.calacademy.org/explore-science/theater-of-the-stars · https://www.mechdyne.com/av-vr-solutions/case_study/california-academy-of-sciences/ · https://www.installation-international.com/technology/six-4k-projectors-create-highly-immersive-experience-morrison-planetarium · https://www.scalabledisplay.com/company/news/morrison-planetarium-california-academy-sciences/ · https://gbvi.co.uk/gbvis-chronos-optical-blend-technology-installed-at-morrison-planetarium-california-academy-of-sciences/ · https://www.es.com/wp-content/uploads/2021/09/Nanoseam-Reference-doc-SEPT-21.pdf · https://www.openspaceproject.com/weekly-tours · https://imersa.org/guidelines · https://sgct.github.io/config/projection/fisheyeprojection · http://paulbourke.net/dome/ · https://paulbourke.net/dome/testpattern/ · https://fddb.org/shows/expedition-reef
