import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function GhostCursor({
  color         = '#B497CF',
  brightness    = 2,
  edgeIntensity = 0,
  trailLength   = 50,
  inertia       = 0.5,
  grainIntensity   = 0.05,
  bloomStrength    = 0.1,
  bloomRadius      = 1,
  bloomThreshold   = 0.025,
  fadeDelayMs      = 1000,
  fadeDurationMs   = 1500,
}) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    /* ── sizes ── */
    const W = mount.clientWidth;
    const H = mount.clientHeight;

    /* ── renderer ── */
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(W, H);
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);
    Object.assign(renderer.domElement.style, {
      position: 'absolute', top: 0, left: 0,
      width: '100%', height: '100%',
      pointerEvents: 'none', zIndex: 9999,
    });

    /* ── scene / camera ── */
    const scene  = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-W/2, W/2, H/2, -H/2, 0.1, 10);
    camera.position.z = 1;

    /* ── trail geometry ── */
    const positions = new Float32Array(trailLength * 3);
    const alphas    = new Float32Array(trailLength);
    const geo       = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('alpha',    new THREE.BufferAttribute(alphas,    1));

    const col = new THREE.Color(color);

    /* ── trail shader ── */
    const mat = new THREE.ShaderMaterial({
      uniforms: {
        uColor:      { value: new THREE.Vector3(col.r, col.g, col.b) },
        uBrightness: { value: brightness },
        uEdge:       { value: edgeIntensity },
        uGlobalAlpha:{ value: 1.0 },
      },
      vertexShader: `
        attribute float alpha;
        varying   float vAlpha;
        void main(){
          vAlpha = alpha;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = mix(18.0, 4.0, 1.0 - alpha);
        }
      `,
      fragmentShader: `
        uniform vec3  uColor;
        uniform float uBrightness;
        uniform float uEdge;
        uniform float uGlobalAlpha;
        varying float vAlpha;
        void main(){
          vec2  uv = gl_PointCoord - 0.5;
          float d  = length(uv) * 2.0;
          if(d > 1.0) discard;
          float core = 1.0 - smoothstep(0.0, 0.6, d);
          float edge = smoothstep(0.5, 1.0, d) * uEdge;
          float a    = (core + edge) * vAlpha * uGlobalAlpha;
          gl_FragColor = vec4(uColor * uBrightness, a);
        }
      `,
      transparent:  true,
      depthWrite:   false,
      blending:     THREE.AdditiveBlending,
    });

    const points = new THREE.Points(geo, mat);
    scene.add(points);

    /* ── dot (cursor head) ── */
    const dotGeo = new THREE.CircleGeometry(5, 32);
    const dotMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(color), transparent: true, opacity: 0.9 });
    const dot    = new THREE.Mesh(dotGeo, dotMat);
    scene.add(dot);

    /* ── post-process: bloom via render-target ping-pong (simple additive glow) ── */
    const bloomTarget = new THREE.WebGLRenderTarget(W, H, { format: THREE.RGBAFormat });
    const bloomScene  = new THREE.Scene();
    const bloomCamera = camera.clone();

    const blurHMat = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse:   { value: bloomTarget.texture },
        uRes:       { value: new THREE.Vector2(W, H) },
        uStrength:  { value: bloomStrength },
        uRadius:    { value: bloomRadius },
        uThreshold: { value: bloomThreshold },
      },
      vertexShader: `
        varying vec2 vUv;
        void main(){ vUv = uv; gl_Position = vec4(position, 1.0); }
      `,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform vec2  uRes;
        uniform float uStrength;
        uniform float uRadius;
        uniform float uThreshold;
        varying vec2 vUv;
        void main(){
          vec4 base = texture2D(tDiffuse, vUv);
          vec4 blur = vec4(0.0);
          float total = 0.0;
          for(int i=-4; i<=4; i++){
            float w = exp(-float(i*i)*0.15);
            vec2 off = vec2(float(i)*uRadius/uRes.x, 0.0);
            vec4 s = texture2D(tDiffuse, vUv + off);
            float lum = dot(s.rgb, vec3(0.299,0.587,0.114));
            if(lum > uThreshold){ blur += s * w; total += w; }
          }
          if(total > 0.0) blur /= total;
          gl_FragColor = base + blur * uStrength;
        }
      `,
      transparent: true,
      depthWrite: false,
    });
    const blurPlane = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), blurHMat);
    bloomScene.add(blurPlane);

    /* ── grain overlay ── */
    const grainScene  = new THREE.Scene();
    const grainMat    = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uIntensity: { value: grainIntensity } },
      vertexShader:   `varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position,1.0); }`,
      fragmentShader: `
        uniform float uTime;
        uniform float uIntensity;
        varying vec2 vUv;
        float rand(vec2 co){ return fract(sin(dot(co,vec2(12.9898,78.233)))*43758.5453); }
        void main(){
          float n = rand(vUv + uTime) * uIntensity;
          gl_FragColor = vec4(vec3(n), n * 0.5);
        }
      `,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const grainPlane = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), grainMat);
    grainScene.add(grainPlane);
    const grainCamera = new THREE.OrthographicCamera(-1,1,1,-1,0,1);

    /* ── state ── */
    const trail       = Array.from({ length: trailLength }, () => ({ x: 0, y: 0 }));
    let   mouseX      = W / 2,  mouseY = H / 2;
    let   currentX    = W / 2,  currentY = H / 2;
    let   globalAlpha = 1.0;
    let   fadeTimer   = null;
    let   fadeStart   = null;
    let   fading      = false;
    let   mounted     = true;

    /* ── pointer tracking (relative to mount) ── */
    const onMove = (e) => {
      const rect = mount.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;

      // reset fade
      fading      = false;
      globalAlpha = 1.0;
      if (fadeTimer) clearTimeout(fadeTimer);
      fadeTimer = setTimeout(() => {
        fading    = true;
        fadeStart = performance.now();
      }, fadeDelayMs);
    };
    mount.addEventListener('mousemove', onMove);

    /* ── animation loop ── */
    let rafId;
    const tick = (now) => {
      if (!mounted) return;
      rafId = requestAnimationFrame(tick);

      // inertia
      currentX += (mouseX - currentX) * (1 - inertia);
      currentY += (mouseY - currentY) * (1 - inertia);

      // shift trail
      trail.unshift({ x: currentX, y: currentY });
      if (trail.length > trailLength) trail.pop();

      // fade-out
      if (fading && fadeStart !== null) {
        const t = Math.min((now - fadeStart) / fadeDurationMs, 1);
        globalAlpha = 1 - t;
        if (t >= 1) { fading = false; }
      }

      // update geometry — convert to NDC-ish orthographic coords
      for (let i = 0; i < trailLength; i++) {
        const p = trail[i] || trail[trail.length - 1];
        positions[i*3]   =  p.x - W/2;
        positions[i*3+1] = -(p.y - H/2);
        positions[i*3+2] = 0;
        alphas[i] = (1 - i / trailLength) * globalAlpha;
      }
      geo.attributes.position.needsUpdate = true;
      geo.attributes.alpha.needsUpdate    = true;

      // dot
      dot.position.set(currentX - W/2, -(currentY - H/2), 0);
      dotMat.opacity = 0.9 * globalAlpha;

      mat.uniforms.uGlobalAlpha.value = globalAlpha;

      // render main scene to bloom target
      renderer.setRenderTarget(bloomTarget);
      renderer.render(scene, camera);
      renderer.setRenderTarget(null);

      // bloom pass
      blurHMat.uniforms.tDiffuse.value = bloomTarget.texture;
      renderer.autoClear = false;
      renderer.render(bloomScene, bloomCamera);

      // grain
      grainMat.uniforms.uTime.value = now * 0.0001;
      renderer.render(grainScene, grainCamera);
      renderer.autoClear = true;
    };
    rafId = requestAnimationFrame(tick);

    /* ── resize ── */
    const onResize = () => {
      const nW = mount.clientWidth;
      const nH = mount.clientHeight;
      renderer.setSize(nW, nH);
      bloomTarget.setSize(nW, nH);
      camera.left = -nW/2; camera.right = nW/2;
      camera.top  =  nH/2; camera.bottom = -nH/2;
      camera.updateProjectionMatrix();
      blurHMat.uniforms.uRes.value.set(nW, nH);
    };
    const ro = new ResizeObserver(onResize);
    ro.observe(mount);

    return () => {
      mounted = false;
      cancelAnimationFrame(rafId);
      mount.removeEventListener('mousemove', onMove);
      ro.disconnect();
      if (fadeTimer) clearTimeout(fadeTimer);
      renderer.dispose();
      bloomTarget.dispose();
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
  }, [color, brightness, edgeIntensity, trailLength, inertia, grainIntensity, bloomStrength, bloomRadius, bloomThreshold, fadeDelayMs, fadeDurationMs]);

  return (
    <div
      ref={mountRef}
      style={{ width: '100%', height: '100%', position: 'relative', cursor: 'none' }}
    />
  );
}
