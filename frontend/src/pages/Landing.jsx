import { useState, useEffect } from "react";

const ACCENT = "#A8C8E8";
const BG = "#0A0B0E";
const CARD_BG = "#111318";
const BORDER = "#1C1E24";

const MOCK_RESULTS = [
  { name: "Linen Midi Dress", store: "Zara", price: "£39.99", match: 98, color: "#e8e4de" },
  { name: "Wool Blend Coat", store: "Massimo Dutti", price: "£129.00", match: 94, color: "#c8b89a" },
  { name: "Wide Leg Trousers", store: "Zara", price: "£35.99", match: 88, color: "#1a1a1a" },
];

function PhoneMockup() {
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState([]);

  useEffect(() => {
    const sequence = [
      () => setStep(1), // show upload
      () => setStep(2), // show loading
      () => setStep(3), // show results
      () => {
        setVisible([]);
        setTimeout(() => setVisible([0]), 200);
        setTimeout(() => setVisible([0, 1]), 500);
        setTimeout(() => setVisible([0, 1, 2]), 800);
      },
      () => { setStep(0); setVisible([]); },
    ];
    const intervals = [800, 1800, 2600, 3800, 6000];
    const runCycle = () =>
      intervals.map((delay, i) => setTimeout(() => { if (sequence[i]) sequence[i](); }, delay));
    let timers = runCycle();
    const loop = setInterval(() => {
      timers.forEach(clearTimeout);
      timers = runCycle();
    }, 6400);
    return () => { clearInterval(loop); timers.forEach(clearTimeout); };
  }, []);

  return (
    <div style={{
      width: 240,
      height: 480,
      background: BG,
      borderRadius: 36,
      border: `2px solid ${BORDER}`,
      boxShadow: `0 0 0 6px #0d0e12, 0 40px 80px rgba(0,0,0,0.6), 0 0 60px rgba(168,200,232,0.08)`,
      overflow: "hidden",
      position: "relative",
      flexShrink: 0,
    }}>
      {/* notch */}
      <div style={{
        position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)",
        width: 80, height: 24, background: BG,
        borderRadius: "0 0 16px 16px", zIndex: 10,
      }} />

      {/* nav */}
      <div style={{
        padding: "32px 16px 8px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: `1px solid ${BORDER}`,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 5, height: 5, borderRadius: "50%", background: ACCENT }} />
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "#e8e4de", fontFamily: "Inter, sans-serif" }}>MODEVA</span>
        </div>
        <div style={{ fontSize: 9, color: ACCENT, background: "rgba(168,200,232,0.1)", padding: "2px 6px", borderRadius: 10, fontFamily: "Inter, sans-serif" }}>AI Search</div>
      </div>

      {/* content */}
      <div style={{ padding: 12, height: "calc(100% - 72px)", display: "flex", flexDirection: "column" }}>
        {(step === 0 || step === 1) && (
          <div style={{
            flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12,
          }}>
            <div style={{
              width: 60, height: 60, borderRadius: 16,
              background: CARD_BG, border: `1px solid ${BORDER}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              color: step === 1 ? ACCENT : "#434651",
              transition: "color 0.4s",
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </div>
            <p style={{ fontSize: 10, color: "#6b6d77", textAlign: "center", fontFamily: "Inter, sans-serif", lineHeight: 1.4 }}>
              {step === 1 ? "Tap to upload a photo" : "Upload any fashion photo"}
            </p>
            <div style={{
              width: "80%", height: 1, background: BORDER, margin: "4px 0",
            }} />
            <p style={{ fontSize: 9, color: "#434651", fontFamily: "Inter, sans-serif" }}>Searches across Zara · Massimo Dutti</p>
          </div>
        )}

        {step === 2 && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12 }}>
            <div style={{
              width: 80, height: 80, borderRadius: 12, overflow: "hidden",
              border: `1px solid ${BORDER}`, background: "#1a1c22",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <div style={{ fontSize: 28 }}>👗</div>
            </div>
            <div style={{ width: 120, height: 2, background: BORDER, borderRadius: 2, overflow: "hidden" }}>
              <div style={{
                height: "100%", background: ACCENT, borderRadius: 2,
                animation: "loadBar 1.2s ease-in-out infinite",
                width: "60%",
              }} />
            </div>
            <p style={{ fontSize: 9, color: "#434651", fontFamily: "Inter, sans-serif", letterSpacing: "0.06em" }}>Scanning stores…</p>
          </div>
        )}

        {step === 3 && (
          <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", gap: 6 }}>
            <p style={{ fontSize: 9, color: "#6b6d77", fontFamily: "Inter, sans-serif", marginBottom: 2 }}>
              <span style={{ color: ACCENT, fontWeight: 600 }}>3</span> matches found
            </p>
            {MOCK_RESULTS.map((item, i) => (
              <div key={i} style={{
                background: CARD_BG, border: `1px solid ${BORDER}`,
                borderRadius: 10, overflow: "hidden",
                display: "flex", alignItems: "center", gap: 8,
                opacity: visible.includes(i) ? 1 : 0,
                transform: visible.includes(i) ? "translateY(0)" : "translateY(8px)",
                transition: "opacity 0.3s ease, transform 0.3s ease",
              }}>
                <div style={{
                  width: 44, height: 56, background: item.color, flexShrink: 0,
                  opacity: 0.8,
                }} />
                <div style={{ flex: 1, padding: "6px 4px 6px 0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 8, color: ACCENT, fontFamily: "Inter, sans-serif", fontWeight: 600, letterSpacing: "0.08em" }}>{item.store.toUpperCase()}</span>
                    <span style={{ fontSize: 8, background: ACCENT, color: BG, padding: "1px 5px", borderRadius: 8, fontWeight: 600, fontFamily: "Inter, sans-serif" }}>{item.match}%</span>
                  </div>
                  <p style={{ fontSize: 9, color: "#c8c4bd", fontFamily: "Inter, sans-serif", margin: "2px 0" }}>{item.name}</p>
                  <p style={{ fontSize: 10, color: "#e8e4de", fontFamily: "Inter, sans-serif", fontWeight: 600 }}>{item.price}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <style>{`
        @keyframes loadBar {
          0% { width: 0%; margin-left: 0; }
          50% { width: 70%; margin-left: 0; }
          100% { width: 0%; margin-left: 100%; }
        }
      `}</style>
    </div>
  );
}

function StoreTag({ name }) {
  return (
    <div style={{
      padding: "6px 14px", borderRadius: 20,
      border: `1px solid ${BORDER}`,
      fontSize: 12, color: "#555862",
      fontFamily: "Inter, sans-serif",
    }}>{name}</div>
  );
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div style={{
      background: CARD_BG, border: `1px solid ${BORDER}`,
      borderRadius: 16, padding: "24px",
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: "rgba(168,200,232,0.1)",
        border: `1px solid rgba(168,200,232,0.2)`,
        display: "flex", alignItems: "center", justifyContent: "center",
        marginBottom: 16, fontSize: 18,
      }}>{icon}</div>
      <h3 style={{
        fontSize: 16, fontWeight: 500, color: "#e8e4de",
        fontFamily: "Inter, sans-serif", marginBottom: 8,
      }}>{title}</h3>
      <p style={{
        fontSize: 13, color: "#6b6d77", lineHeight: 1.6,
        fontFamily: "Inter, sans-serif",
      }}>{desc}</p>
    </div>
  );
}

function StepCard({ num, title, desc }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 12 }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10,
        background: "rgba(168,200,232,0.1)",
        border: `1px solid rgba(168,200,232,0.3)`,
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 13, fontWeight: 600, color: ACCENT,
        fontFamily: "Inter, sans-serif",
      }}>{num}</div>
      <h3 style={{ fontSize: 18, fontWeight: 500, color: "#e8e4de", fontFamily: "Inter, sans-serif", margin: 0 }}>{title}</h3>
      <p style={{ fontSize: 14, color: "#6b6d77", lineHeight: 1.6, fontFamily: "Inter, sans-serif", margin: 0 }}>{desc}</p>
    </div>
  );
}

export default function ModevaLanding() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  return (
    <div style={{ background: BG, minHeight: "100vh", color: "#e8e4de", fontFamily: "Inter, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: ${BG}; }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-up { animation: fadeUp 0.6s ease both; }
        .fade-up-1 { animation-delay: 0.1s; }
        .fade-up-2 { animation-delay: 0.2s; }
        .fade-up-3 { animation-delay: 0.3s; }
        .fade-up-4 { animation-delay: 0.4s; }
        @media (max-width: 768px) {
          .lp-nav { padding: 0 20px !important; }
          .lp-nav-links { gap: 16px !important; }
          .lp-nav-secondary { display: none !important; }
          .lp-section { padding-left: 20px !important; padding-right: 20px !important; }
          .lp-hero { padding-top: 56px !important; padding-bottom: 48px !important; }
          .hero-inner { flex-direction: column !important; text-align: center; align-items: center !important; gap: 40px !important; }
          .hero-text { align-items: center !important; }
          .hero-headline { font-size: 38px !important; }
          .steps-grid { grid-template-columns: 1fr !important; }
          .features-grid { grid-template-columns: 1fr !important; }
          .lp-card { padding: 28px 20px !important; gap: 28px !important; flex-direction: column !important; }
          .cta-head { font-size: 32px !important; }
          .lp-footer { padding: 24px 20px !important; flex-direction: column !important; align-items: flex-start !important; }
        }
        @media (max-width: 380px) {
          .hero-headline { font-size: 32px !important; }
          .lp-section { padding-left: 16px !important; padding-right: 16px !important; }
        }
      `}</style>

      {/* NAV */}
      <nav className="lp-nav" style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 48px", height: 64,
        borderBottom: `1px solid ${BORDER}`,
        position: "sticky", top: 0,
        background: "rgba(10,11,14,0.92)", backdropFilter: "blur(10px)",
        zIndex: 100,
      }}>
        <a href="/" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none", cursor: "pointer" }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: ACCENT }} />
          <span style={{ fontSize: 14, fontWeight: 700, letterSpacing: "0.1em", color: "#e8e4de" }}>MODEVA</span>
        </a>
        <div className="lp-nav-links" style={{ display: "flex", gap: 32, alignItems: "center" }}>
          <a className="lp-nav-secondary" href="#how" style={{ fontSize: 13, color: "#6b6d77", textDecoration: "none" }}>How it works</a>
          <a className="lp-nav-secondary" href="#features" style={{ fontSize: 13, color: "#6b6d77", textDecoration: "none" }}>Features</a>
          <a href="#download" style={{
            fontSize: 13, fontWeight: 500, color: BG,
            background: ACCENT, padding: "8px 18px", borderRadius: 8,
            textDecoration: "none",
          }}>Try free</a>
        </div>
      </nav>

      {/* HERO */}
      <section className="lp-section lp-hero" style={{ padding: "100px 48px 80px", maxWidth: 1100, margin: "0 auto" }}>
        <div className="hero-inner" style={{ display: "flex", alignItems: "center", gap: 80, justifyContent: "space-between" }}>
          
          {/* Text */}
          <div className="hero-text" style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 520 }}>
            <div className="fade-up fade-up-1" style={{
              display: "inline-flex", alignItems: "center", gap: 6,
              fontSize: 11, fontWeight: 500, letterSpacing: "0.16em",
              color: ACCENT, textTransform: "uppercase",
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 3L13.5 8.5L19 10L13.5 11.5L12 17L10.5 11.5L5 10L10.5 8.5L12 3Z"/>
              </svg>
              AI-powered visual search
            </div>

            <h1 className="fade-up fade-up-2 hero-headline" style={{
              fontSize: 56, fontWeight: 300, letterSpacing: "-0.04em",
              lineHeight: 1.1, color: "#e8e4de",
            }}>
              See it.<br />
              <span style={{ color: ACCENT }}>Find it.</span><br />
              Shop it.
            </h1>

            <p className="fade-up fade-up-3" style={{
              fontSize: 16, color: "#6b6d77", lineHeight: 1.7,
            }}>
              Upload any fashion photo and discover visually similar items across your favourite stores — instantly. No typing. No guessing.
            </p>

            <div className="fade-up fade-up-4" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <a href="/search" style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                background: ACCENT, color: BG,
                padding: "14px 28px", borderRadius: 10,
                fontSize: 14, fontWeight: 600, textDecoration: "none",
                letterSpacing: "0.02em",
              }}>
                Try Modeva Free
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="5" y1="12" x2="19" y2="12"/>
                  <polyline points="12 5 19 12 12 19"/>
                </svg>
              </a>
              <a href="#how" style={{
                display: "inline-flex", alignItems: "center", gap: 8,
                border: `1px solid ${BORDER}`, color: "#9ea6b2",
                padding: "14px 28px", borderRadius: 10,
                fontSize: 14, textDecoration: "none",
              }}>
                Watch demo
              </a>
            </div>

            <div className="fade-up fade-up-4" style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, color: "#434651", letterSpacing: "0.1em", textTransform: "uppercase" }}>Searches across</span>
              {["Zara", "Massimo Dutti"].map(s => <StoreTag key={s} name={s} />)}
            </div>
          </div>

          {/* Phone mockup */}
          <div style={{ flexShrink: 0, position: "relative" }}>
            <div style={{
              position: "absolute", inset: -40,
              background: `radial-gradient(ellipse at center, rgba(168,200,232,0.08) 0%, transparent 70%)`,
              borderRadius: "50%",
              pointerEvents: "none",
            }} />
            <PhoneMockup />
          </div>
        </div>
      </section>

      {/* DIVIDER */}
      <div style={{ borderTop: `1px solid ${BORDER}` }} />

      {/* HOW IT WORKS */}
      <section id="how" className="lp-section" style={{ padding: "80px 48px", maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ marginBottom: 56, textAlign: "center" }}>
          <p style={{ fontSize: 11, letterSpacing: "0.16em", color: ACCENT, textTransform: "uppercase", marginBottom: 12 }}>How it works</p>
          <h2 style={{ fontSize: 36, fontWeight: 300, letterSpacing: "-0.03em", color: "#e8e4de" }}>
            Three steps to your next favourite outfit
          </h2>
        </div>
        <div className="steps-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 48 }}>
          <StepCard num="01" title="Upload" desc="Take a photo or upload any image — a screenshot, a street style shot, a film still. Anything works." />
          <StepCard num="02" title="Discover" desc="Our AI analyses style, colour and silhouette to find visually similar items across multiple stores in seconds." />
          <StepCard num="03" title="Shop" desc="Browse matches, compare prices, and click through to buy — all in one place. No switching between tabs." />
        </div>
      </section>

      {/* DIVIDER */}
      <div style={{ borderTop: `1px solid ${BORDER}` }} />

      {/* PROBLEM/SOLUTION */}
      <section className="lp-section" style={{ padding: "80px 48px", maxWidth: 1100, margin: "0 auto" }}>
        <div className="lp-card" style={{
          background: CARD_BG, border: `1px solid ${BORDER}`,
          borderRadius: 24, padding: "64px 48px",
          display: "flex", gap: 80, alignItems: "center", flexWrap: "wrap",
        }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <p style={{ fontSize: 11, letterSpacing: "0.16em", color: ACCENT, textTransform: "uppercase", marginBottom: 16 }}>The problem</p>
            <h2 style={{ fontSize: 32, fontWeight: 300, letterSpacing: "-0.03em", color: "#e8e4de", marginBottom: 20, lineHeight: 1.2 }}>
              You've seen it.<br />You can't find it.
            </h2>
            <p style={{ fontSize: 15, color: "#6b6d77", lineHeight: 1.7 }}>
              You spot the perfect jacket on someone in the street. You screenshot an outfit from Instagram. You see something in a film and need it immediately. Text search never quite works. Modeva does.
            </p>
          </div>
          <div style={{ flex: 1, minWidth: 280, display: "flex", flexDirection: "column", gap: 16 }}>
            {[
              { label: "Without Modeva", text: "Type vague keywords, scroll through hundreds of irrelevant results, give up." },
              { label: "With Modeva", text: "Upload the photo, get exact visual matches across multiple stores in seconds.", accent: true },
            ].map(({ label, text, accent }) => (
              <div key={label} style={{
                padding: "20px 24px", borderRadius: 14,
                border: `1px solid ${accent ? "rgba(168,200,232,0.3)" : BORDER}`,
                background: accent ? "rgba(168,200,232,0.05)" : "transparent",
              }}>
                <p style={{ fontSize: 11, fontWeight: 600, color: accent ? ACCENT : "#434651", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>{label}</p>
                <p style={{ fontSize: 14, color: accent ? "#c8c4bd" : "#555862", lineHeight: 1.6 }}>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="lp-section" style={{ padding: "80px 48px", maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ marginBottom: 56, textAlign: "center" }}>
          <p style={{ fontSize: 11, letterSpacing: "0.16em", color: ACCENT, textTransform: "uppercase", marginBottom: 12 }}>Features</p>
          <h2 style={{ fontSize: 36, fontWeight: 300, letterSpacing: "-0.03em", color: "#e8e4de" }}>Fashion search, finally done right</h2>
        </div>
        <div className="features-grid" style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
          <FeatureCard icon="🔍" title="Visual AI search" desc="Stop typing. Show us what you're looking for and let the AI do the rest. CLIP-powered image understanding." />
          <FeatureCard icon="🏪" title="Multi-store results" desc="One search. Multiple stores. The best matches, ranked by visual similarity — not ads or sponsorships." />
          <FeatureCard icon="💸" title="Real-time prices" desc="See current prices and sale items across all stores at once. Never overpay for the same piece again." />
        </div>
      </section>

      {/* DIVIDER */}
      <div style={{ borderTop: `1px solid ${BORDER}` }} />

      {/* CTA / DOWNLOAD */}
      <section id="download" className="lp-section" style={{ padding: "100px 48px", maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
        <p style={{ fontSize: 11, letterSpacing: "0.16em", color: ACCENT, textTransform: "uppercase", marginBottom: 16 }}>Get started</p>
        <h2 className="cta-head" style={{ fontSize: 44, fontWeight: 300, letterSpacing: "-0.04em", color: "#e8e4de", marginBottom: 16, lineHeight: 1.1 }}>
          Your wardrobe starts<br />with a photo.
        </h2>
        <p style={{ fontSize: 15, color: "#6b6d77", marginBottom: 48 }}>
          Live on web now. iOS and Android apps coming soon.
        </p>

        <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center", marginBottom: 48 }}>
          <div style={{ height: 1, width: 80, background: BORDER }} />
          <a href="/search" style={{ fontSize: 12, color: ACCENT, textDecoration: "none", letterSpacing: "0.04em" }}>Try the web version free today →</a>
          <div style={{ height: 1, width: 80, background: BORDER }} />
        </div>

        {/* Email signup */}
        <div style={{ maxWidth: 400, margin: "0 auto" }}>
          {submitted ? (
            <p style={{ fontSize: 14, color: ACCENT }}>✓ You're on the list — we'll be in touch soon.</p>
          ) : (
            <div style={{ display: "flex", gap: 8 }}>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="your@email.com"
                style={{
                  flex: 1, padding: "12px 16px", borderRadius: 10,
                  border: `1px solid ${BORDER}`, background: CARD_BG,
                  color: "#e8e4de", fontSize: 14, outline: "none",
                  fontFamily: "Inter, sans-serif",
                }}
              />
              <button
                onClick={() => email && setSubmitted(true)}
                style={{
                  padding: "12px 20px", borderRadius: 10,
                  background: ACCENT, color: BG, border: "none",
                  fontSize: 14, fontWeight: 600, cursor: "pointer",
                  fontFamily: "Inter, sans-serif",
                }}
              >
                Notify me
              </button>
            </div>
          )}
          <p style={{ fontSize: 12, color: "#434651", marginTop: 10 }}>Get early access when the app launches.</p>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="lp-footer" style={{
        borderTop: `1px solid ${BORDER}`,
        padding: "32px 48px",
        display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 5, height: 5, borderRadius: "50%", background: ACCENT }} />
          <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: "0.08em", color: "#e8e4de" }}>MODEVA</span>
        </div>
        <p style={{ fontSize: 12, color: "#434651" }}>© 2026 Modeva. Visual Fashion Search.</p>
        <div style={{ display: "flex", gap: 24 }}>
          {["Privacy", "Terms", "Contact"].map(l => (
            <a key={l} href="#" style={{ fontSize: 12, color: "#434651", textDecoration: "none" }}>{l}</a>
          ))}
        </div>
      </footer>
    </div>
  );
}
