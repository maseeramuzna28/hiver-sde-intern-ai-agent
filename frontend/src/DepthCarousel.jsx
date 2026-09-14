import React, { useRef, useState, useEffect, useCallback } from 'react';
import { gsap } from 'gsap';

export default function DepthCarousel({
  items = [],
  depth = 220,
  spread = 90,
  tilt = 22,
  tiltDirection = 'right',
  perspective = 1400,
  visibleCards = 4,
  falloff = 0.2,
  blur = 6,
  autoplay = false,
  loop = true,
  cardWidth = 300,
  cardHeight = 380,
  radius = 18,
  tint = '#05060a',
  duration = 700,
  ease = 'power3.out',
  autoplayDelay = 3200,
  showControls = true,
  showIndicators = true,
}) {
  const [active, setActive] = useState(0);
  const containerRef = useRef(null);
  const cardRefs = useRef([]);
  const autoplayRef = useRef(null);
  const count = items.length;

  const getOrder = useCallback((idx) => {
    const diff = ((idx - active) % count + count) % count;
    return diff <= count / 2 ? diff : diff - count;
  }, [active, count]);

  const animateCards = useCallback(() => {
    if (!containerRef.current) return;
    cardRefs.current.forEach((card, idx) => {
      if (!card) return;
      const order = getOrder(idx);
      const absOrder = Math.abs(order);
      const sign = order >= 0 ? 1 : -1;

      const zOffset = -absOrder * depth;
      const xOffset = sign * absOrder * spread;
      const yRot = tiltDirection === 'right'
        ? -order * tilt
        : order * tilt;
      const scale = 1 - absOrder * falloff;
      const blurVal = absOrder * blur;
      const opacity = absOrder > visibleCards ? 0 : 1 - absOrder * 0.18;
      const zIndex = count - absOrder;

      gsap.to(card, {
        x: xOffset,
        z: zOffset,
        rotateY: yRot,
        scale: Math.max(scale, 0.1),
        opacity,
        filter: `blur(${blurVal}px) brightness(${1 - absOrder * 0.12})`,
        zIndex,
        duration: duration / 1000,
        ease,
      });
    });
  }, [active, depth, spread, tilt, tiltDirection, visibleCards, falloff, blur, duration, ease, count, getOrder]);

  useEffect(() => { animateCards(); }, [animateCards]);

  const go = useCallback((dir) => {
    setActive(prev => {
      const next = prev + dir;
      if (!loop) return Math.max(0, Math.min(count - 1, next));
      return ((next % count) + count) % count;
    });
  }, [count, loop]);

  useEffect(() => {
    if (!autoplay) return;
    autoplayRef.current = setInterval(() => go(1), autoplayDelay);
    return () => clearInterval(autoplayRef.current);
  }, [autoplay, autoplayDelay, go]);

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
      {/* Stage */}
      <div
        ref={containerRef}
        style={{
          position: 'relative',
          width: cardWidth,
          height: cardHeight,
          perspective: `${perspective}px`,
          transformStyle: 'preserve-3d',
        }}
      >
        {items.map((item, idx) => (
          <div
            key={idx}
            ref={el => cardRefs.current[idx] = el}
            onClick={() => { setActive(idx); if (item.onSelect) item.onSelect(); }}
            style={{
              position: 'absolute',
              top: 0, left: 0,
              width: cardWidth,
              height: cardHeight,
              borderRadius: radius,
              overflow: 'hidden',
              cursor: 'pointer',
              transformOrigin: 'center center',
              transformStyle: 'preserve-3d',
              willChange: 'transform, opacity, filter',
              boxShadow: '0 24px 60px rgba(0,0,0,0.6)',
            }}
          >
            {/* tint overlay */}
            <div style={{
              position: 'absolute', inset: 0, zIndex: 2, borderRadius: radius,
              background: tint, mixBlendMode: 'multiply', pointerEvents: 'none',
            }} />
            {item.overlay && item.overlay}
            <img
              src={item.image}
              alt={item.alt || ''}
              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
              draggable={false}
            />
          </div>
        ))}
      </div>

      {/* Controls */}
      {showControls && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button onClick={() => go(-1)} style={btnStyle}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          {showIndicators && items.map((_, idx) => (
            <div
              key={idx}
              onClick={() => setActive(idx)}
              style={{
                width: idx === active ? 20 : 6,
                height: 6,
                borderRadius: 3,
                background: idx === active ? '#5df0a8' : 'rgba(255,255,255,0.25)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
            />
          ))}
          <button onClick={() => go(1)} style={btnStyle}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}

const btnStyle = {
  width: 36, height: 36, borderRadius: '50%',
  background: 'rgba(255,255,255,0.07)',
  border: '1px solid rgba(255,255,255,0.12)',
  color: '#fff', cursor: 'pointer',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  transition: 'background 0.2s',
};
