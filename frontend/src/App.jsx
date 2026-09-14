import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion';
import {
  Bot, AlertTriangle, CheckCircle2, ShieldAlert,
  Send, RefreshCw, Sparkles, Copy, Check, MessageSquare, BarChart3, Info, Zap, TrendingUp, Award, Layers
} from 'lucide-react';
import DepthCarousel from './DepthCarousel';
import GhostCursor from './GhostCursor';

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

/* ─── Tilt Card ─── */
function TiltCard({ children, className, style }) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-0.5, 0.5], [8, -8]);
  const rotateY = useTransform(x, [-0.5, 0.5], [-8, 8]);
  const springX = useSpring(rotateX, { stiffness: 200, damping: 20 });
  const springY = useSpring(rotateY, { stiffness: 200, damping: 20 });

  const handleMouseMove = (e) => {
    const rect = ref.current.getBoundingClientRect();
    x.set((e.clientX - rect.left) / rect.width - 0.5);
    y.set((e.clientY - rect.top) / rect.height - 0.5);
  };
  const handleMouseLeave = () => { x.set(0); y.set(0); };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX: springX, rotateY: springY, transformStyle: 'preserve-3d', ...style }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/* ─── Floating Orb ─── */
function Orb({ size, color, top, left, delay }) {
  return (
    <motion.div
      style={{
        position: 'fixed', width: size, height: size, borderRadius: '50%',
        background: color, filter: 'blur(80px)', opacity: 0.18,
        top, left, pointerEvents: 'none', zIndex: 0,
      }}
      animate={{ scale: [1, 1.2, 1], x: [0, 30, 0], y: [0, -20, 0] }}
      transition={{ duration: 8, repeat: Infinity, delay, ease: 'easeInOut' }}
    />
  );
}

/* ─── Animated Counter ─── */
function AnimatedNumber({ value, suffix = '' }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const target = parseFloat(value);
    let start = 0;
    const step = target / 40;
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setDisplay(target); clearInterval(timer); }
      else setDisplay(start);
    }, 30);
    return () => clearInterval(timer);
  }, [value]);
  return <>{typeof value === 'string' && value.includes('.') ? display.toFixed(1) : Math.round(display)}{suffix}</>;
}

export default function App() {
  const [inputText, setInputText] = useState('@AmazonHelp Where is my package #112-9988-7711? It was due yesterday!');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('simulator');
  const [typingDots, setTypingDots] = useState('');

  const presets = [
    { title: '📦 Late Delivery', text: '@AmazonHelp Where is my package #112-9988-7711? It was due yesterday!' },
    { title: '🔄 Return & Refund', text: '@AmazonHelp I dropped off my return at UPS 5 days ago. When will my refund process?' },
    { title: '💔 Damaged Item', text: '@AmazonHelp My laptop screen arrived completely shattered! Box was damaged.' },
    { title: '📱 Account & Prime', text: '@AmazonHelp Cannot log into my Amazon account. Password reset email is not coming.' },
    { title: '🚨 Billing Fraud', text: '@AmazonHelp Unauthorized charge of $250 on my credit card! I will take legal action if not resolved!' },
    { title: '🚚 Driver Complaint', text: '@AmazonHelp Your delivery driver threw my box over the gate and broke my porch lights!' },
  ];

  const stats = [
    { label: 'Fallback Accuracy', value: '61.5', suffix: '%', icon: <TrendingUp size={20} />, color: '#6ee7b7' },
    { label: 'Fallback Macro F1', value: '60.1', suffix: '%', icon: <Award size={20} />, color: '#93c5fd' },
    { label: 'Escalation F1', value: '49.21', suffix: '%', icon: <ShieldAlert size={20} />, color: '#fca5a5' },
    { label: 'Reply Quality', value: '4.35', suffix: '/5', icon: <Sparkles size={20} />, color: '#fcd34d' },
  ];

  // ── Local heuristic classifier (mirrors backend fallback logic) ──────────────
  // Used when the FastAPI server is offline so the demo still shows meaningful,
  // per-intent results rather than a hardcoded ORDER_STATUS_DELIVERY every time.
  const localClassify = (text) => {
    const t = text.toLowerCase();

    const HIGH_RISK = ['lawsuit', 'legal action', 'police', 'fraud', 'unauthorized', 'stolen',
                       'hacked', 'melted', 'hazard', 'charger', 'fire', 'injury', 'attorney'];

    const scores = {
      ORDER_STATUS_DELIVERY:    0,
      RETURNS_REFUNDS:          0,
      PRODUCT_ISSUE_DEFECT:     0,
      ACCOUNT_DIGITAL_PRIME:    0,
      PAYMENT_BILLING:          0,
      GENERAL_FEEDBACK_COMPLAINT: 0,
    };

    // Keyword scoring
    if (/where is|track|delivery|delivered|shipping|shipped|carrier|delay|arriving|package|where's my|out for delivery/.test(t)) scores.ORDER_STATUS_DELIVERY    += 3;
    if (/return|refund|replace|exchange|money back|send back|drop.?off|ups|kohl/.test(t))                                      scores.RETURNS_REFUNDS         += 3;
    if (/broken|damaged|defective|wrong item|faulty|not working|shattered|missing item|cracked|leaked|melted|empty box/.test(t)) scores.PRODUCT_ISSUE_DEFECT   += 3;
    if (/prime|video|kindle|login|password|account|sign in|subscription|app|two.?factor|locked out/.test(t))                   scores.ACCOUNT_DIGITAL_PRIME   += 3;
    if (/charge|billed|payment|card|promo|discount|double charge|unauthorized|invoice|billing|cost/.test(t))                   scores.PAYMENT_BILLING         += 3;
    if (/driver|worst|terrible|bad service|thanks|great|complaint|rude|shoutout|feedback|experience/.test(t))                  scores.GENERAL_FEEDBACK_COMPLAINT += 2;

    const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
    const intent = best[1] === 0 ? 'GENERAL_FEEDBACK_COMPLAINT' : best[0];
    const confidence = best[1] === 0 ? 0.62 : Math.min(0.70 + best[1] * 0.07, 0.93);

    const highRiskHit = HIGH_RISK.filter(kw => t.includes(kw));
    const needs_escalation = highRiskHit.length > 0 ||
      intent === 'PAYMENT_BILLING' ||
      (confidence < 0.70);
    const priority = highRiskHit.length > 0 ? 'URGENT'
                   : needs_escalation        ? 'MEDIUM'
                   : 'AUTOMATED';
    const escalation_reason = needs_escalation
      ? (highRiskHit.length > 0
          ? `Contains high-risk keywords: ${highRiskHit.join(', ')}`
          : intent === 'PAYMENT_BILLING'
            ? 'Billing disputes require manual financial investigation.'
            : `Low confidence (${(confidence * 100).toFixed(0)}%) — routing to human review.`)
      : 'Routine inquiry; standard automated workflow.';

    const replies = {
      ORDER_STATUS_DELIVERY:     "We'd love to look into your delivery status! Please send us a DM with your order number so we can check in real-time. - Alex",
      RETURNS_REFUNDS:           "Sorry to hear about your return! Please DM us your order number and the email on your account and we'll get this sorted right away. - Sam",
      PRODUCT_ISSUE_DEFECT:      "We sincerely apologise for the damaged item. Please send us a DM with your order details and a photo if possible — we'll arrange a replacement or refund. - Taylor",
      ACCOUNT_DIGITAL_PRIME:     "We're here to help with your account! Please DM us your registered email address so our technical team can investigate securely. - Morgan",
      PAYMENT_BILLING:           "We take payment concerns very seriously. Please send us a secure DM with your order ID so we can investigate the charge immediately. - Jordan",
      GENERAL_FEEDBACK_COMPLAINT:"Thank you for reaching out. We're sorry you had this experience. Please DM us your details so we can escalate your feedback to the right team. - Chris",
    };

    return {
      text,
      intent,
      confidence: Math.round(confidence * 1000) / 1000,
      needs_escalation,
      escalation_reason,
      priority,
      suggested_reply: replies[intent],
      _offline: true,   // flag so we can show the offline banner
    };
  };

  const handleClassify = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post(`${API_BASE}/api/classify`, { text: inputText });
      setResult(response.data);
    } catch {
      // API offline — use local heuristic so each preset gives a unique, meaningful result
      setResult(localClassify(inputText));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { handleClassify(); }, []);

  useEffect(() => {
    if (!loading) return;
    const timer = setInterval(() => {
      setTypingDots(d => d.length >= 3 ? '' : d + '.');
    }, 400);
    return () => clearInterval(timer);
  }, [loading]);

  const handleCopy = () => {
    if (result?.suggested_reply) {
      navigator.clipboard.writeText(result.suggested_reply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getPriorityColor = () => {
    if (!result?.needs_escalation) return { bg: 'rgba(20,83,45,0.4)', border: 'rgba(74,222,128,0.3)', text: '#4ade80' };
    if (result.priority === 'URGENT') return { bg: 'rgba(127,29,29,0.4)', border: 'rgba(248,113,113,0.3)', text: '#f87171' };
    return { bg: 'rgba(120,53,15,0.4)', border: 'rgba(251,191,36,0.3)', text: '#fbbf24' };
  };

  const colors = getPriorityColor();

  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflowX: 'hidden' }}>
      {/* ── Ghost cursor overlay (full viewport, pointer-events none) ── */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 9999, pointerEvents: 'none' }}>
        <GhostCursor
          color="#B497CF"
          brightness={2}
          edgeIntensity={0}
          trailLength={50}
          inertia={0.5}
          grainIntensity={0.05}
          bloomStrength={0.1}
          bloomRadius={1}
          bloomThreshold={0.025}
          fadeDelayMs={1000}
          fadeDurationMs={1500}
        />
      </div>
      {/* Animated background orbs */}
      <Orb size="600px" color="#6366f1" top="-100px" left="-100px" delay={0} />
      <Orb size="500px" color="#8b5cf6" top="40%" left="60%" delay={2} />
      <Orb size="400px" color="#06b6d4" top="70%" left="10%" delay={4} />
      <Orb size="350px" color="#f59e0b" top="20%" left="80%" delay={6} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '1280px', margin: '0 auto', padding: '28px 24px' }}>

        {/* ─── Header ─── */}
        <motion.header
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              style={{ fontSize: '40px', filter: 'drop-shadow(0 0 20px rgba(251,191,36,0.6))' }}
            >
              🐝
            </motion.div>
            <div>
              <h1 style={{ margin: 0, fontSize: '26px', fontWeight: 800, background: 'linear-gradient(135deg, #e2e8f0 0%, #94a3b8 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Hiver AI Support Agent
              </h1>
              <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>
                Target: <span style={{ color: '#fb923c', fontWeight: 600 }}>@AmazonHelp</span> · Real-World Customer Support AI
              </p>
            </div>
          </div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '10px 18px', borderRadius: '999px',
              background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(12px)',
              border: '1px solid rgba(255,255,255,0.1)',
              fontSize: '13px', fontWeight: 500, color: '#94a3b8',
            }}
          >
            <motion.div
              animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#22c55e' }}
            />
            FastAPI · Port 8000
          </motion.div>
        </motion.header>

        {/* ─── Tabs ─── */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          style={{ display: 'flex', gap: '8px', marginBottom: '28px' }}
        >
          {[
            { id: 'simulator', label: 'Live Tweet Simulator', icon: <MessageSquare size={16} /> },
            { id: 'benchmark', label: 'Benchmark (200 Golden Set)', icon: <BarChart3 size={16} /> },
            { id: 'showcase', label: 'Scenario Showcase', icon: <Layers size={16} /> },
          ].map(tab => (
            <motion.button
              key={tab.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setActiveTab(tab.id)}
              style={{
                position: 'relative', display: 'flex', alignItems: 'center', gap: '8px',
                padding: '10px 22px', borderRadius: '10px', border: 'none',
                fontSize: '14px', fontWeight: 500, cursor: 'pointer',
                background: activeTab === tab.id ? 'rgba(99,102,241,0.25)' : 'rgba(255,255,255,0.04)',
                color: activeTab === tab.id ? '#a5b4fc' : '#64748b',
                backdropFilter: 'blur(8px)',
                boxShadow: activeTab === tab.id ? '0 0 20px rgba(99,102,241,0.3), inset 0 1px 0 rgba(255,255,255,0.1)' : 'none',
                outline: activeTab === tab.id ? '1px solid rgba(99,102,241,0.4)' : '1px solid rgba(255,255,255,0.06)',
                transition: 'all 0.2s',
              }}
            >
              {tab.icon} {tab.label}
              {activeTab === tab.id && (
                <motion.div layoutId="tabIndicator" style={{ position: 'absolute', inset: 0, borderRadius: '10px', background: 'rgba(99,102,241,0.1)' }} />
              )}
            </motion.button>
          ))}
        </motion.div>

        <AnimatePresence mode="wait">

          {/* ═══════════ SIMULATOR TAB ═══════════ */}
          {activeTab === 'simulator' && (
            <motion.div
              key="simulator"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.4 }}
              style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}
            >
              {/* ── Left: Input Card ── */}
              <TiltCard style={{ borderRadius: '20px' }}>
                <div style={glassCard}>
                  <div style={{ position: 'absolute', inset: 0, borderRadius: '20px', background: 'linear-gradient(135deg, rgba(99,102,241,0.08) 0%, transparent 60%)', pointerEvents: 'none' }} />

                  <h2 style={cardTitle}>
                    <motion.span animate={{ rotate: [0, 20, 0] }} transition={{ duration: 2, repeat: Infinity, repeatDelay: 2 }}>
                      <Sparkles size={20} color="#fbbf24" />
                    </motion.span>
                    Incoming Tweet Simulator
                  </h2>

                  {/* Preset chips */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '18px' }}>
                    {presets.map((p, i) => (
                      <motion.button
                        key={i}
                        whileHover={{ scale: 1.06, y: -2 }}
                        whileTap={{ scale: 0.94 }}
                        onClick={() => setInputText(p.text)}
                        style={{
                          padding: '6px 13px', borderRadius: '999px', cursor: 'pointer',
                          fontSize: '12px', fontWeight: 500,
                          background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)',
                          color: '#cbd5e1', backdropFilter: 'blur(4px)',
                          transition: 'all 0.2s',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                        }}
                      >
                        {p.title}
                      </motion.button>
                    ))}
                  </div>

                  {/* Textarea */}
                  <div style={{ position: 'relative', marginBottom: '16px' }}>
                    <textarea
                      rows={4}
                      value={inputText}
                      onChange={e => setInputText(e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) handleClassify(); }}
                      placeholder="Type or select a customer tweet..."
                      style={{
                        width: '100%', boxSizing: 'border-box',
                        padding: '14px 16px', borderRadius: '12px',
                        background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                        color: '#e2e8f0', fontSize: '14px', lineHeight: 1.6,
                        fontFamily: 'inherit', resize: 'vertical', outline: 'none',
                        backdropFilter: 'blur(4px)',
                        transition: 'border-color 0.2s, box-shadow 0.2s',
                      }}
                      onFocus={e => { e.target.style.borderColor = 'rgba(99,102,241,0.6)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.15)'; }}
                      onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; e.target.style.boxShadow = 'none'; }}
                    />
                    <span style={{ position: 'absolute', bottom: '10px', right: '12px', fontSize: '11px', color: '#475569' }}>
                      ⌘↵ to send
                    </span>
                  </div>

                  {/* Submit button */}
                  <motion.button
                    whileHover={{ scale: 1.02, boxShadow: '0 8px 30px rgba(99,102,241,0.5)' }}
                    whileTap={{ scale: 0.97, y: 2 }}
                    onClick={handleClassify}
                    disabled={loading}
                    style={{
                      width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '10px',
                      padding: '13px', borderRadius: '12px', border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
                      background: loading ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                      color: '#fff', fontSize: '15px', fontWeight: 700,
                      boxShadow: '0 4px 20px rgba(99,102,241,0.35), inset 0 1px 0 rgba(255,255,255,0.2)',
                      transition: 'all 0.2s',
                      letterSpacing: '0.3px',
                    }}
                  >
                    {loading
                      ? <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}><RefreshCw size={18} /></motion.div> Analyzing{typingDots}</>
                      : <><Send size={18} /> Classify &amp; Process Tweet</>
                    }
                  </motion.button>
                </div>
              </TiltCard>

              {/* ── Right: Results Card ── */}
              <TiltCard style={{ borderRadius: '20px' }}>
                <div style={glassCard}>
                  <div style={{ position: 'absolute', inset: 0, borderRadius: '20px', background: 'linear-gradient(135deg, rgba(139,92,246,0.07) 0%, transparent 60%)', pointerEvents: 'none' }} />

                  <h2 style={cardTitle}>
                    <Bot size={20} color="#93c5fd" />
                    Agent Classification Output
                  </h2>

                  <AnimatePresence mode="wait">
                    {loading && (
                      <motion.div
                        key="loading"
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 0', gap: '16px' }}
                      >
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                          style={{ width: 56, height: 56, borderRadius: '50%', border: '3px solid rgba(99,102,241,0.2)', borderTopColor: '#6366f1', boxShadow: '0 0 20px rgba(99,102,241,0.4)' }}
                        />
                        <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>Processing tweet with the support agent{typingDots}</p>
                      </motion.div>
                    )}

                    {!loading && result && (
                      <motion.div
                        key="result"
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.4 }}
                      >
                        {/* Offline banner */}
                        {result._offline && (
                          <motion.div
                            initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }}
                            style={{
                              display: 'flex', alignItems: 'center', gap: '8px',
                              padding: '8px 14px', borderRadius: '8px', marginBottom: '12px',
                              background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.25)',
                              fontSize: '12px', color: '#fbbf24',
                            }}
                          >
                            <span>⚡</span>
                            <span><strong>Offline mode</strong> — backend not detected on :8000. Showing local heuristic classification.</span>
                          </motion.div>
                        )}

                        {/* Intent + Confidence */}
                        <motion.div
                          initial={{ scale: 0.95 }} animate={{ scale: 1 }}
                          style={{
                            padding: '16px', borderRadius: '12px', marginBottom: '14px',
                            background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                            <span style={{
                              background: 'linear-gradient(135deg, rgba(59,130,246,0.3), rgba(99,102,241,0.3))',
                              border: '1px solid rgba(99,102,241,0.4)',
                              color: '#a5b4fc', padding: '6px 14px', borderRadius: '8px',
                              fontWeight: 700, fontSize: '13px', letterSpacing: '0.5px',
                            }}>
                              {result.intent}
                            </span>
                            <span style={{ fontSize: '13px', fontWeight: 700, color: '#94a3b8' }}>
                              {(result.confidence * 100).toFixed(1)}% confidence
                            </span>
                          </div>

                          {/* Progress bar */}
                          <div style={{ height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${result.confidence * 100}%` }}
                              transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
                              style={{ height: '100%', borderRadius: '3px', background: 'linear-gradient(90deg, #6366f1, #8b5cf6)' }}
                            />
                          </div>
                        </motion.div>

                        {/* Escalation badge */}
                        <motion.div
                          initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.2 }}
                          style={{
                            display: 'flex', alignItems: 'flex-start', gap: '12px',
                            padding: '14px 16px', borderRadius: '12px', marginBottom: '14px',
                            background: colors.bg, border: `1px solid ${colors.border}`,
                          }}
                        >
                          {result.needs_escalation
                            ? (result.priority === 'URGENT'
                              ? <ShieldAlert size={22} color={colors.text} />
                              : <AlertTriangle size={22} color={colors.text} />)
                            : <CheckCircle2 size={22} color={colors.text} />
                          }
                          <div>
                            <strong style={{ fontSize: '13px', color: colors.text, letterSpacing: '0.5px' }}>
                              {result.needs_escalation
                                ? `HUMAN ESCALATION · ${result.priority} PRIORITY`
                                : 'AUTOMATED RESOLUTION PATHWAY'
                              }
                            </strong>
                            <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#94a3b8' }}>
                              {result.needs_escalation ? result.escalation_reason : 'Query meets auto-handling criteria. No human intervention required.'}
                            </p>
                          </div>
                        </motion.div>

                        {/* Suggested reply */}
                        <motion.div
                          initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.35 }}
                          style={{
                            padding: '16px', borderRadius: '12px',
                            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                            <span style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                              Drafted Response
                            </span>
                            <motion.button
                              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                              onClick={handleCopy}
                              style={{
                                display: 'flex', alignItems: 'center', gap: '5px',
                                padding: '5px 12px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                                background: copied ? 'rgba(34,197,94,0.15)' : 'rgba(255,255,255,0.07)',
                                color: copied ? '#4ade80' : '#94a3b8', fontSize: '12px', fontWeight: 500,
                                outline: copied ? '1px solid rgba(74,222,128,0.3)' : '1px solid rgba(255,255,255,0.1)',
                                transition: 'all 0.2s',
                              }}
                            >
                              {copied ? <Check size={13} /> : <Copy size={13} />}
                              {copied ? 'Copied!' : 'Copy'}
                            </motion.button>
                          </div>
                          <p style={{ margin: 0, fontSize: '14px', color: '#cbd5e1', fontStyle: 'italic', lineHeight: 1.6 }}>
                            "{result.suggested_reply}"
                          </p>
                        </motion.div>
                      </motion.div>
                    )}

                    {!loading && !result && (
                      <motion.div
                        key="empty"
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        style={{ textAlign: 'center', padding: '48px 0', color: '#475569' }}
                      >
                        <Bot size={48} style={{ opacity: 0.3, marginBottom: '12px' }} />
                        <p style={{ margin: 0 }}>Submit a tweet to see classification output</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </TiltCard>
            </motion.div>
          )}

          {/* ═══════════ BENCHMARK TAB ═══════════ */}
          {activeTab === 'benchmark' && (
            <motion.div
              key="benchmark"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.4 }}
            >
              <div style={{ ...glassCard, borderRadius: '20px', marginBottom: '24px' }}>
                <div style={{ position: 'absolute', inset: 0, borderRadius: '20px', background: 'linear-gradient(135deg, rgba(139,92,246,0.08) 0%, rgba(6,182,212,0.05) 100%)', pointerEvents: 'none' }} />

                <h2 style={{ ...cardTitle, marginBottom: '24px' }}>
                  <BarChart3 size={20} color="#c084fc" />
                  Benchmark Performance · 200-Sample Golden Evaluation Set
                </h2>

                {/* Stats grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
                  {stats.map((s, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      whileHover={{ scale: 1.04, y: -4 }}
                      style={{
                        padding: '20px', borderRadius: '14px', textAlign: 'center',
                        background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
                        boxShadow: `0 4px 20px rgba(0,0,0,0.2), 0 0 0 1px rgba(255,255,255,0.04)`,
                        cursor: 'default',
                      }}
                    >
                      <div style={{ color: s.color, marginBottom: '8px', display: 'flex', justifyContent: 'center' }}>
                        {s.icon}
                      </div>
                      <div style={{ fontSize: '28px', fontWeight: 800, color: s.color, lineHeight: 1 }}>
                        <AnimatedNumber value={s.value} suffix={s.suffix} />
                      </div>
                      <div style={{ fontSize: '11px', color: '#64748b', marginTop: '6px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                        {s.label}
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Comparison table */}
                <div style={{ borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ background: 'rgba(255,255,255,0.06)' }}>
                        {['Model Architecture', 'Accuracy', 'Macro F1', 'Escalation F1', 'Reply Score'].map(h => (
                          <th key={h} style={{ padding: '14px 16px', textAlign: 'left', fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.6px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { name: 'Baseline 1: Trivial (Majority Class)', acc: '16.5%', f1: '4.7%', esc: '0.0%', reply: '4.0/5.0', highlight: false },
                        { name: 'Baseline 2: Simple (TF-IDF + Rules)', acc: '64.0%', f1: '64.2%', esc: '21.1%', reply: '4.75/5.0', highlight: false },
                        { name: '⚡ Main Model: Claude AI Support Agent', acc: '94.5%', f1: '94.1%', esc: '88.5%', reply: '4.86/5.0', highlight: true },
                      ].map((row, i) => (
                        <motion.tr
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.2 + i * 0.1 }}
                          style={{
                            background: row.highlight ? 'rgba(99,102,241,0.12)' : 'transparent',
                            borderBottom: '1px solid rgba(255,255,255,0.05)',
                          }}
                        >
                          <td style={{ padding: '14px 16px', fontSize: '13px', color: row.highlight ? '#a5b4fc' : '#94a3b8', fontWeight: row.highlight ? 700 : 400 }}>{row.name}</td>
                          <td style={{ padding: '14px 16px', fontSize: '13px', color: row.highlight ? '#6ee7b7' : '#64748b', fontWeight: row.highlight ? 700 : 400 }}>{row.acc}</td>
                          <td style={{ padding: '14px 16px', fontSize: '13px', color: row.highlight ? '#6ee7b7' : '#64748b', fontWeight: row.highlight ? 700 : 400 }}>{row.f1}</td>
                          <td style={{ padding: '14px 16px', fontSize: '13px', color: row.highlight ? '#6ee7b7' : '#64748b', fontWeight: row.highlight ? 700 : 400 }}>{row.esc}</td>
                          <td style={{ padding: '14px 16px', fontSize: '13px', color: row.highlight ? '#fbbf24' : '#64748b', fontWeight: row.highlight ? 700 : 400 }}>{row.reply}</td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* LLM Judge note */}
                <motion.div
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
                  style={{
                    display: 'flex', gap: '12px', alignItems: 'flex-start',
                    padding: '16px', borderRadius: '12px', marginTop: '20px',
                    background: 'rgba(37,99,235,0.1)', border: '1px solid rgba(59,130,246,0.2)',
                  }}
                >
                  <Zap size={20} color="#60a5fa" style={{ flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <strong style={{ fontSize: '13px', color: '#93c5fd' }}>LLM-as-Judge · Human Alignment Evidence</strong>
                    <p style={{ margin: '6px 0 0', fontSize: '13px', color: '#64748b', lineHeight: 1.6 }}>
                      Validated against 30 human-annotated ground-truth ratings:&nbsp;
                      <span style={{ color: '#93c5fd', fontWeight: 600 }}>76.67% Exact Agreement</span>,&nbsp;
                      <span style={{ color: '#93c5fd', fontWeight: 600 }}>100% Adjacent Agreement (±1)</span>, and&nbsp;
                      <span style={{ color: '#93c5fd', fontWeight: 600 }}>0.679 Cohen's Kappa</span>.
                    </p>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* ═══════════ SHOWCASE TAB ═══════════ */}
          {activeTab === 'showcase' && (
            <motion.div
              key="showcase"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.4 }}
            >
              <div style={{ ...glassCard, borderRadius: '20px' }}>
                <div style={{ position: 'absolute', inset: 0, borderRadius: '20px', background: 'linear-gradient(135deg, rgba(99,102,241,0.07) 0%, rgba(6,182,212,0.04) 100%)', pointerEvents: 'none' }} />

                <h2 style={{ ...cardTitle, marginBottom: '8px' }}>
                  <Layers size={20} color="#a5b4fc" />
                  Scenario Showcase
                </h2>
                <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '32px' }}>
                  Six real-world @AmazonHelp tweet scenarios — click a card to load it into the simulator.
                </p>

                <div style={{ height: '520px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <DepthCarousel
                    items={[
                      { image: 'https://picsum.photos/seed/delivery/800/1000', alt: 'Late Delivery',    label: '📦 Late Delivery',    intent: 'ORDER_STATUS_DELIVERY',    text: '@AmazonHelp Where is my package #112-9988-7711? It was due yesterday!' },
                      { image: 'https://picsum.photos/seed/return/800/1000',   alt: 'Return & Refund',  label: '🔄 Return & Refund',  intent: 'RETURNS_REFUNDS',           text: '@AmazonHelp I dropped off my return at UPS 5 days ago. When will my refund process?' },
                      { image: 'https://picsum.photos/seed/damage/800/1000',   alt: 'Damaged Item',     label: '💔 Damaged Item',     intent: 'PRODUCT_ISSUE_DEFECT',      text: '@AmazonHelp My laptop screen arrived completely shattered! Box was damaged.' },
                      { image: 'https://picsum.photos/seed/account/800/1000',  alt: 'Account & Prime',  label: '📱 Account & Prime',  intent: 'ACCOUNT_DIGITAL_PRIME',     text: '@AmazonHelp Cannot log into my Amazon account. Password reset email is not coming.' },
                      { image: 'https://picsum.photos/seed/fraud/800/1000',    alt: 'Billing Fraud',    label: '🚨 Billing Fraud',    intent: 'PAYMENT_BILLING',           text: '@AmazonHelp Unauthorized charge of $250 on my credit card! I will take legal action!' },
                      { image: 'https://picsum.photos/seed/driver/800/1000',   alt: 'Driver Complaint', label: '🚚 Driver Complaint', intent: 'GENERAL_FEEDBACK_COMPLAINT', text: '@AmazonHelp Your delivery driver threw my box over the gate and broke my porch lights!' },
                    ].map(item => ({
                      image: item.image,
                      alt: item.alt,
                      overlay: (
                        <div style={{ position: 'absolute', inset: 0, zIndex: 3, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '20px', background: 'linear-gradient(to top, rgba(4,6,15,0.95) 0%, transparent 55%)' }}>
                          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase', color: '#a5b4fc', marginBottom: '6px' }}>{item.intent.replace(/_/g,' ')}</span>
                          <span style={{ fontSize: '15px', fontWeight: 700, color: '#e2e8f0' }}>{item.label}</span>
                          <span style={{ fontSize: '11px', color: '#64748b', marginTop: '6px', lineHeight: 1.5 }}>{item.text.slice(0, 60)}…</span>
                        </div>
                      ),
                      onSelect: () => { setInputText(item.text); setActiveTab('simulator'); },
                    }))}
                    depth={220}
                    spread={90}
                    tilt={22}
                    tiltDirection="right"
                    perspective={1400}
                    visibleCards={4}
                    falloff={0.2}
                    blur={6}
                    autoplay={false}
                    loop
                    cardWidth={280}
                    cardHeight={380}
                    radius={18}
                    tint="#05060a"
                    duration={700}
                    ease="power3.out"
                    autoplayDelay={3200}
                    showControls
                    showIndicators
                  />
                </div>

                <p style={{ textAlign: 'center', fontSize: '12px', color: '#475569', marginTop: '16px' }}>
                  Click any card to load the scenario into the Live Tweet Simulator
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ─── Shared styles ─── */
const glassCard = {
  position: 'relative',
  background: 'rgba(15,23,42,0.6)',
  backdropFilter: 'blur(20px)',
  WebkitBackdropFilter: 'blur(20px)',
  borderRadius: '20px',
  padding: '28px',
  border: '1px solid rgba(255,255,255,0.08)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
  overflow: 'hidden',
};

const cardTitle = {
  display: 'flex', alignItems: 'center', gap: '10px',
  margin: '0 0 20px 0', fontSize: '17px', fontWeight: 700, color: '#e2e8f0',
};
