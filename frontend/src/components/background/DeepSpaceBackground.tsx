import { useEffect, useRef } from 'react';
import * as THREE from 'three';

function detectSoftwareWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return true;
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    const param = ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER;
    const gpu = String(gl.getParameter(param));
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return /SwiftShader|llvmpipe|softpipe|Software|Basic Render/i.test(gpu);
  } catch {
    return true;
  }
}

export function DeepSpaceBackground() {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const isSoftwareGl = detectSoftwareWebGL();
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: !isSoftwareGl,
        powerPreference: 'high-performance',
        preserveDrawingBuffer: true,
      });
    } catch {
      return;
    }

    const pixelRatio = isSoftwareGl ? 1 : Math.min(window.devicePixelRatio || 1, 1.75);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.48;
    renderer.domElement.style.position = 'fixed';
    renderer.domElement.style.inset = '0';
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.pointerEvents = 'none';
    renderer.domElement.setAttribute('aria-hidden', 'true');
    container.appendChild(renderer.domElement);

    const bgScene = new THREE.Scene();
    const bgCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const bgMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uAspect: { value: window.innerWidth / Math.max(1, window.innerHeight) },
      },
      vertexShader: `varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position,1.0);}`,
      fragmentShader: `
        precision highp float;
        varying vec2 vUv;
        uniform float uTime;
        uniform float uAspect;
        float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
        float noise(vec2 p){
          vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
          return mix(mix(hash(i),hash(i+vec2(1.,0.)),f.x),
                     mix(hash(i+vec2(0.,1.)),hash(i+vec2(1.,1.)),f.x),f.y);
        }
        float fbm(vec2 p){
          float v=0.,a=.5;
          mat2 r=mat2(1.6,1.2,-1.2,1.6);
          for(int i=0;i<6;i++){v+=noise(p)*a;p=r*p;a*=.52;}
          return v;
        }
        void main(){
          vec2 uv=vUv;
          vec2 p=(uv-.5)*vec2(uAspect,1.);
          float t=uTime*.012;
          vec2 warp=vec2(fbm(p*1.35+vec2(t,-t*.55)),fbm(p*1.35+vec2(4.2-t*.7,2.8+t*.4)));
          vec2 q=p*1.55+(warp-.5)*1.25+vec2(t*.22,-t*.13);
          float mass=fbm(q*1.45);
          float detail=fbm(q*3.5+vec2(-t*.35,t*.28));
          float filament=fbm(q*6.5+detail);
          float cloud=smoothstep(.28,.75,mass*.72+detail*.28);
          float wisp=smoothstep(.30,.76,detail*.58+filament*.42);
          vec3 col=vec3(.009,.014,.042);
          float distantGlow=fbm(p*1.05+vec2(-t*.08,t*.05));
          col+=vec3(.055,.088,.24)*smoothstep(.16,.78,distantGlow);
          col+=vec3(.085,.165,.42)*cloud*1.05;
          col+=vec3(.38,.12,.68)*cloud*wisp*1.25;
          col+=vec3(.11,.38,.72)*smoothstep(.38,.78,filament)*cloud*1.05;
          col+=vec3(.32,.20,.54)*pow(max(0.,mass-.40),2.)*2.5;
          float glow=exp(-length((uv-vec2(.54,.50))*vec2(uAspect,1.))*1.85);
          col+=vec3(.075,.058,.20)*glow;
          col*=.86+.14*smoothstep(1.10,.10,length(p));
          gl_FragColor=vec4(col,1.);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`,
    });
    const bgGeo = new THREE.PlaneGeometry(2, 2);
    const bgQuad = new THREE.Mesh(bgGeo, bgMaterial);
    bgScene.add(bgQuad);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      62,
      window.innerWidth / Math.max(1, window.innerHeight),
      0.1,
      1500,
    );
    camera.position.set(0, 0, 28);

    const starMaterials: THREE.ShaderMaterial[] = [];
    const starGeometries: THREE.BufferGeometry[] = [];

    function createStarLayer(
      count: number,
      spread: number,
      depthMin: number,
      depthMax: number,
      size: number,
      opacity: number,
    ) {
      const pos = new Float32Array(count * 3);
      const col = new Float32Array(count * 3);
      const sizes = new Float32Array(count);
      const palette = [
        new THREE.Color(0xdce8ff),
        new THREE.Color(0xaacaff),
        new THREE.Color(0xe8d9ff),
        new THREE.Color(0xffffff),
      ];
      for (let i = 0; i < count; i++) {
        pos[i * 3] = (Math.random() - 0.5) * spread;
        pos[i * 3 + 1] = (Math.random() - 0.5) * spread * 0.62;
        pos[i * 3 + 2] = -(depthMin + Math.random() * (depthMax - depthMin));
        const c = palette[Math.floor(Math.random() * palette.length)];
        col.set([c.r, c.g, c.b], i * 3);
        sizes[i] = size * (0.35 + Math.pow(Math.random(), 3) * 1.7);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      geo.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
      const mat = new THREE.ShaderMaterial({
        transparent: true,
        depthWrite: false,
        vertexColors: true,
        uniforms: {
          uRatio: { value: renderer.getPixelRatio() },
          uOpacity: { value: opacity },
          uTime: { value: 0 },
        },
        vertexShader: `attribute float aSize;varying vec3 vColor;uniform float uRatio;uniform float uTime;
          void main(){vColor=color;vec4 mv=modelViewMatrix*vec4(position,1.);
          float tw=.82+.18*sin(uTime*1.3+position.x*2.7+position.y*3.1);
          gl_PointSize=clamp(aSize*uRatio*tw*(210.0/-mv.z),.55,6.5);
          gl_Position=projectionMatrix*mv;}`,
        fragmentShader: `varying vec3 vColor;uniform float uOpacity;
          void main(){float d=length(gl_PointCoord-.5);float a=1.-smoothstep(.08,.5,d);
          gl_FragColor=vec4(vColor,a*uOpacity);}`,
      });
      starGeometries.push(geo);
      starMaterials.push(mat);
      const points = new THREE.Points(geo, mat);
      scene.add(points);
      return points;
    }

    const far = createStarLayer(12500, 520, 150, 700, 1.0, 0.72);
    const mid = createStarLayer(5000, 260, 70, 300, 1.35, 0.82);
    const near = createStarLayer(1200, 120, 28, 95, 1.7, 0.88);

    let px = 0;
    let py = 0;
    let zoom = 28;
    let zoomTarget = 28;

    const handlePointerMove = (e: PointerEvent) => {
      px = (e.clientX / Math.max(1, window.innerWidth) - 0.5) * 2;
      py = (e.clientY / Math.max(1, window.innerHeight) - 0.5) * 2;
    };

    const handleWheel = (e: WheelEvent) => {
      zoomTarget = THREE.MathUtils.clamp(zoomTarget + e.deltaY * 0.012, 18, 43);
    };

    const handleResize = () => {
      const w = window.innerWidth;
      const h = Math.max(1, window.innerHeight);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
      const pr = isSoftwareGl ? 1 : Math.min(window.devicePixelRatio || 1, 1.75);
      renderer.setPixelRatio(pr);
      bgMaterial.uniforms.uAspect.value = w / h;
      for (const m of starMaterials) {
        m.uniforms.uRatio.value = renderer.getPixelRatio();
      }
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: true });
    window.addEventListener('wheel', handleWheel, { passive: true });
    window.addEventListener('resize', handleResize);

    const startTime = performance.now();
    const lookTarget = new THREE.Vector3();
    let frameId = 0;
    let disposed = false;

    function afterDraw(cb: () => void) {
      const gl = renderer.getContext() as WebGL2RenderingContext;
      if (!gl || typeof gl.fenceSync !== 'function') {
        frameId = window.setTimeout(cb, 80);
        return;
      }
      const sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
      gl.flush();
      const poll = () => {
        if (disposed) {
          if (sync) gl.deleteSync(sync);
          return;
        }
        const state = sync && gl.getSyncParameter(sync, gl.SYNC_STATUS);
        if (state === gl.UNSIGNALED) {
          frameId = window.setTimeout(poll, 5);
        } else {
          if (sync) gl.deleteSync(sync);
          frameId = window.setTimeout(cb, 80);
        }
      };
      frameId = window.setTimeout(poll, 5);
    }

    function tick() {
      if (disposed) return;
      const t = (performance.now() - startTime) * 0.001;
      bgMaterial.uniforms.uTime.value = t;
      for (const m of starMaterials) {
        m.uniforms.uTime.value = t;
      }

      zoom += (zoomTarget - zoom) * 0.018;
      const flightX = Math.sin(t * 0.115) * 4.0 + Math.sin(t * 0.047 + 1.2) * 1.8 + px * 1.25;
      const flightY = Math.sin(t * 0.083 + 0.7) * 2.25 + Math.cos(t * 0.039) * 0.8 - py * 0.85;
      const flightZ = zoom + Math.sin(t * 0.072) * 1.35 + Math.sin(t * 0.031) * 0.8;

      camera.position.x += (flightX - camera.position.x) * 0.018;
      camera.position.y += (flightY - camera.position.y) * 0.018;
      camera.position.z += (flightZ - camera.position.z) * 0.018;

      lookTarget.set(
        Math.sin(t * 0.105 + 1.0) * 2.6 + px * 0.35,
        Math.cos(t * 0.078 + 0.4) * 1.35 - py * 0.25,
        -42,
      );
      camera.lookAt(lookTarget);
      camera.rotation.z = Math.sin(t * 0.052) * 0.012 + Math.sin(t * 0.021) * 0.006;

      far.position.x = Math.sin(t * 0.025) * 2.2;
      far.position.y = Math.cos(t * 0.019) * 0.8;
      mid.position.x = Math.sin(t * 0.043 + 1.0) * 1.5;
      mid.position.y = Math.cos(t * 0.032 + 0.5) * 0.65;
      near.position.x = Math.sin(t * 0.064 + 2.0) * 0.85;
      near.position.y = Math.cos(t * 0.051 + 1.0) * 0.4;

      renderer.autoClear = true;
      renderer.render(bgScene, bgCamera);
      renderer.clearDepth();
      renderer.render(scene, camera);

      if (isSoftwareGl) {
        afterDraw(tick);
      } else {
        frameId = window.requestAnimationFrame(tick);
      }
    }

    tick();

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frameId);
      window.clearTimeout(frameId);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('resize', handleResize);
      bgGeo.dispose();
      bgMaterial.dispose();
      starGeometries.forEach((g) => g.dispose());
      starMaterials.forEach((m) => m.dispose());
      renderer.dispose();
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      data-testid="deep-space-canvas"
      className="fixed inset-0 z-0 pointer-events-none"
      aria-hidden="true"
    />
  );
}
