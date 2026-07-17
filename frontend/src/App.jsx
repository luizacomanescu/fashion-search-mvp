import { useRef, useState, useCallback, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const GENDERS = ["women", "men", "unisex"];

const CURRENCY_SYMBOLS = { GBP: "£", USD: "$", EUR: "€" };
function priceLabel(item) {
  const sym = CURRENCY_SYMBOLS[item.currency_code] || "";
  return sym ? `${sym}${item.price}` : item.price;
}

function SparkleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3L13.5 8.5L19 10L13.5 11.5L12 17L10.5 11.5L5 10L10.5 8.5L12 3Z"/>
      <path d="M19 3L19.75 5.25L22 6L19.75 6.75L19 9L18.25 6.75L16 6L18.25 5.25L19 3Z"/>
      <path d="M5 16L5.5 17.5L7 18L5.5 18.5L5 20L4.5 18.5L3 18L4.5 17.5L5 16Z"/>
    </svg>
  );
}

function CameraIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
      <circle cx="12" cy="13" r="4"/>
    </svg>
  );
}

function ResetIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="1 4 1 10 7 10"/>
      <path d="M3.51 15a9 9 0 1 0 .49-4.65"/>
    </svg>
  );
}

function ExternalIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  );
}

function ResultCard({ item, index }) {
  return (
    <div
      className="result-card"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="card-image-wrap">
        <img src={item.image} alt={item.name} className="card-image" />
        <div className="card-match">{item.match}%</div>
      </div>
      <div className="card-body">
        <div className="card-meta">
          <span className="card-store">{item.store}</span>
          <span className="card-category">{item.category}</span>
        </div>
        <p className="card-name">{item.name}</p>
        <div className="card-footer">
          <span className="card-price">{priceLabel(item)}</span>
          <a href={item.url} className="card-link" target="_blank" rel="noopener noreferrer">
            View <ExternalIcon />
          </a>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const fileInputRef = useRef(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [activeStore, setActiveStore] = useState("All");
  const [gender, setGender] = useState(null); // null = search all (women+men)
  const [file, setFile] = useState(null);
  const [availableStores, setAvailableStores] = useState([]);

  // Load the stores we actually have products for, so the UI never
  // advertises a store the catalogue can't deliver.
  useEffect(() => {
    fetch(`${API_URL}/stores`)
      .then(r => r.json())
      .then(setAvailableStores)
      .catch(() => setAvailableStores([]));
  }, []);

  const doSearch = useCallback(async (fileObj, genderValue) => {
    setLoading(true);
    setResults([]);

    const formData = new FormData();
    formData.append("file", fileObj);

    // null = search all genders; otherwise pass the explicit choice so the
    // backend filters to that gender (+ unisex). Unisex is sent explicitly
    // so it returns 0 until we actually stock unisex products.
    const qs = genderValue ? `?gender=${genderValue}` : "";

    const [res] = await Promise.all([
      fetch(`${API_URL}/search${qs}`, {
        method: "POST",
        body: formData,
      }),
      new Promise(r => setTimeout(r, 1000)) // minimum 1 second loading
    ]);

    const data = await res.json();
    setResults(data);
    setLoading(false);
  }, []);

  const processFile = useCallback(async (fileObj) => {
    if (!fileObj || !fileObj.type.startsWith("image/")) return;
    setFile(fileObj);
    setImageUrl(URL.createObjectURL(fileObj));
    await doSearch(fileObj, gender);
  }, [gender, doSearch]);

  const changeGender = useCallback((g) => {
    setGender(g);
    if (file) doSearch(file, g);
  }, [file, doSearch]);

  const handleFileChange = (e) => processFile(e.target.files?.[0]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    processFile(e.dataTransfer.files?.[0]);
  }, [processFile]);

  const handleDragOver = (e) => { e.preventDefault(); setDragging(true); };
  const handleDragLeave = () => setDragging(false);

  const reset = () => {
    setImageUrl(null);
    setResults([]);
    setActiveStore("All");
    setGender(null); // back to "search all" on new search
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const filtered = activeStore === "All"
    ? results
    : results.filter(r => r.store === activeStore);

  // Results-page filter: only stores present in THIS result set (so a
  // store never shows a tab that returns nothing for the current search).
  const resultStores = ["All", ...new Set(results.map(r => r.store).filter(Boolean))];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          font-family: 'Inter', system-ui, sans-serif;
          background: #0A0B0E;
          color: #E8E4DE;
          min-height: 100vh;
          -webkit-font-smoothing: antialiased;
        }

        #root {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        /* ── NAV ── */
        .nav {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 32px;
          height: 60px;
          border-bottom: 1px solid #1C1E24;
          position: sticky;
          top: 0;
          background: rgba(10,11,14,0.92);
          backdrop-filter: blur(10px);
          z-index: 100;
        }
        .nav-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 15px;
          font-weight: 600;
          letter-spacing: 0.06em;
          color: #E8E4DE;
          text-transform: uppercase;
        }
        .nav-logo-dot {
          width: 6px; height: 6px;
          border-radius: 50%;
          background: #A8C8E8;
        }
        .nav-pill {
          font-size: 11px;
          font-weight: 500;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #A8C8E8;
          background: rgba(123, 92, 240, 0.1);
          border: 1px solid rgba(123, 92, 240, 0.2);
          padding: 4px 10px;
          border-radius: 20px;
        }

        /* ── MAIN ── */
        .main {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 80px 24px 80px;
        }

        /* ── UPLOAD STATE ── */
        .upload-view {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
          max-width: 520px;
        }
        .upload-eyebrow {
          font-size: 11px;
          font-weight: 500;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: #A8C8E8;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .upload-heading {
          font-size: 38px;
          font-weight: 300;
          letter-spacing: -0.03em;
          line-height: 1.15;
          color: #E8E4DE;
          text-align: center;
          margin-bottom: 12px;
        }
        .upload-heading em {
          font-style: normal;
          color: #A8C8E8;
        }
        .upload-sub {
          font-size: 14px;
          color: #6B6D77;
          text-align: center;
          margin-bottom: 48px;
          line-height: 1.6;
        }
        .drop-zone {
          width: 100%;
          border: 1.5px dashed #2A2D36;
          border-radius: 20px;
          padding: 56px 40px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
          cursor: pointer;
          transition: border-color 0.2s, background 0.2s;
          background: transparent;
          position: relative;
          user-select: none;
        }
        .drop-zone:hover, .drop-zone.drag-over {
          border-color: #A8C8E8;
          background: rgba(168, 200, 232, 0.04);
        }
        .drop-zone-icon {
          width: 56px; height: 56px;
          border-radius: 16px;
          background: #161820;
          border: 1px solid #2A2D36;
          display: flex; align-items: center; justify-content: center;
          color: #6B6D77;
          transition: color 0.2s, border-color 0.2s;
        }
        .drop-zone:hover .drop-zone-icon, .drop-zone.drag-over .drop-zone-icon {
          color: #A8C8E8;
          border-color: rgba(168, 200, 232, 0.3);
        }
        .drop-label {
          font-size: 15px;
          color: #9EA6B2;
        }
        .drop-label strong {
          color: #E8E4DE;
          font-weight: 500;
        }
        .drop-hint {
          font-size: 12px;
          color: #434651;
          letter-spacing: 0.04em;
        }
        .upload-stores {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-top: 36px;
          flex-wrap: wrap;
          justify-content: center;
        }
        .stores-label {
          font-size: 11px;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: #434651;
        }
        .store-tag {
          font-size: 12px;
          color: #555862;
          padding: 4px 10px;
          border: 1px solid #1C1E24;
          border-radius: 20px;
        }
        .gender-row {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 20px;
          flex-wrap: wrap;
        }
        .upload-view .gender-row {
          margin-top: 28px;
        }

        /* ── RESULTS STATE ── */
        .results-view {
          width: 100%;
          max-width: 1100px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .results-header {
          width: 100%;
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          margin-bottom: 32px;
          gap: 24px;
          flex-wrap: wrap;
        }
        .query-panel {
          display: flex;
          align-items: flex-start;
          gap: 16px;
        }
        .query-image {
          width: 80px;
          height: 80px;
          object-fit: cover;
          border-radius: 12px;
          border: 1px solid #2A2D36;
          flex-shrink: 0;
        }
        .query-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          padding-top: 4px;
        }
        .query-eyebrow {
          font-size: 10px;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: #434651;
        }
        .query-title {
          font-size: 20px;
          font-weight: 500;
          color: #E8E4DE;
          letter-spacing: -0.02em;
        }
        .query-count {
          font-size: 13px;
          color: #6B6D77;
        }
        .query-count span {
          color: #A8C8E8;
          font-weight: 500;
        }
        .reset-btn {
          display: flex;
          align-items: center;
          gap: 7px;
          font-size: 13px;
          font-weight: 400;
          color: #6B6D77;
          background: none;
          border: 1px solid #1C1E24;
          padding: 8px 14px;
          border-radius: 8px;
          cursor: pointer;
          transition: color 0.2s, border-color 0.2s;
          white-space: nowrap;
          font-family: inherit;
        }
        .reset-btn:hover { color: #E8E4DE; border-color: #2A2D36; }

        /* ── FILTER BAR ── */
        .filter-bar {
          width: 100%;
          display: flex;
          gap: 8px;
          margin-bottom: 28px;
          flex-wrap: wrap;
        }
        .filter-btn {
          font-size: 12px;
          font-weight: 500;
          letter-spacing: 0.06em;
          padding: 6px 14px;
          border-radius: 20px;
          border: 1px solid #2A2D36;
          background: transparent;
          color: #6B6D77;
          cursor: pointer;
          transition: all 0.15s;
          font-family: inherit;
        }
        .filter-btn:hover { color: #E8E4DE; border-color: #3A3D48; }
        .filter-btn.active {
          background: #A8C8E8;
          border-color: #A8C8E8;
          color: #0A0B0E;
        }

        /* ── LOADING ── */
        .loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
          padding: 80px 0;
        }
        .loading-bar {
          width: 200px;
          height: 2px;
          background: #1C1E24;
          border-radius: 2px;
          overflow: hidden;
        }
        .loading-bar-fill {
          height: 100%;
          background: #A8C8E8;
          border-radius: 2px;
          animation: loadBar 1.4s ease-in-out infinite;
        }
        @keyframes loadBar {
          0% { width: 0%; margin-left: 0; }
          50% { width: 70%; margin-left: 0; }
          100% { width: 0%; margin-left: 100%; }
        }
        .loading-text {
          font-size: 13px;
          color: #434651;
          letter-spacing: 0.06em;
        }

        /* ── GRID ── */
        .results-grid {
          width: 100%;
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 16px;
        }
        .result-card {
          background: #111318;
          border: 1px solid #1C1E24;
          border-radius: 14px;
          overflow: hidden;
          transition: border-color 0.2s, transform 0.2s;
          animation: fadeUp 0.4s ease both;
        }
        .result-card:hover {
          border-color: #2A2D36;
          transform: translateY(-2px);
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .card-image-wrap {
          position: relative;
          overflow: hidden;
        }
        .card-image {
          width: 100%;
          height: 240px;
          object-fit: cover;
          display: block;
          transition: transform 0.3s ease;
        }
        .result-card:hover .card-image { transform: scale(1.03); }
        .card-match {
          position: absolute;
          top: 10px;
          left: 10px;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.04em;
          color: #0A0B0E;
          background: #A8C8E8;
          padding: 3px 8px;
          border-radius: 20px;
        }
        .card-body { padding: 14px 16px 16px; }
        .card-meta {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 6px;
        }
        .card-store {
          font-size: 10px;
          font-weight: 600;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: #A8C8E8;
        }
        .card-category {
          font-size: 10px;
          color: #434651;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }
        .card-name {
          font-size: 14px;
          font-weight: 400;
          color: #C8C4BD;
          line-height: 1.4;
          margin-bottom: 12px;
        }
        .card-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .card-price {
          font-size: 16px;
          font-weight: 600;
          color: #E8E4DE;
          letter-spacing: -0.02em;
        }
        .card-link {
          display: flex;
          align-items: center;
          gap: 5px;
          font-size: 11px;
          font-weight: 500;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #434651;
          text-decoration: none;
          transition: color 0.2s;
        }
        .card-link:hover { color: #A8C8E8; }

        /* ── RESPONSIVE ── */
        @media (max-width: 600px) {
          .nav { padding: 0 20px; }
          .main { padding: 48px 16px 60px; }
          .upload-heading { font-size: 28px; }
          .results-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
          .query-panel { gap: 12px; }
          .query-title { font-size: 17px; }
        }
      `}</style>

      <nav className="nav">
        <div className="nav-logo">
          <div className="nav-logo-dot" />
          Modeva
        </div>
        <span className="nav-pill">Visual Search</span>
      </nav>

      <main className="main">
        {!imageUrl && (
          <div className="upload-view">
            <p className="upload-eyebrow">
              <SparkleIcon /> AI-powered
            </p>
            <h1 className="upload-heading">
              Find it by<br /><em>showing</em> it
            </h1>
            <p className="upload-sub">
              Upload any fashion photo. We'll find similar pieces<br />
              across your favourite stores in seconds.
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />

            <div
              className={`drop-zone ${dragging ? "drag-over" : ""}`}
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <div className="drop-zone-icon">
                <CameraIcon />
              </div>
              <p className="drop-label">
                <strong>Choose a photo</strong> or drag it here
              </p>
              <p className="drop-hint">JPEG, PNG, WEBP — up to 10 MB</p>
            </div>

            <div className="gender-row">
              <span className="stores-label">Shopping for</span>
              <div className="filter-bar" style={{ marginBottom: 0, marginTop: 4 }}>
                {GENDERS.map(g => (
                  <button
                    key={g}
                    className={`filter-btn ${gender === g ? "active" : ""}`}
                    onClick={() => setGender(g)}
                  >
                    {g.charAt(0).toUpperCase() + g.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {availableStores.length > 0 && (
              <div className="upload-stores">
                <span className="stores-label">Searches across</span>
                {availableStores.map(s => (
                  <span key={s} className="store-tag">{s}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {imageUrl && (
          <div className="results-view">
            <div className="results-header">
              <div className="query-panel">
                <img src={imageUrl} alt="Your search" className="query-image" />
                <div className="query-info">
                  <span className="query-eyebrow">Searching for</span>
                  <p className="query-title">Similar items</p>
                  {!loading && (
                    <p className="query-count">
                      <span>{filtered.length}</span> matches found
                    </p>
                  )}
                </div>
              </div>
              <button className="reset-btn" onClick={reset}>
                <ResetIcon /> New search
              </button>
            </div>

            {loading ? (
              <div className="loading-state">
                <div className="loading-bar">
                  <div className="loading-bar-fill" />
                </div>
                <p className="loading-text">Scanning stores…</p>
              </div>
            ) : (
              <>
                <div className="gender-row">
                  <span className="stores-label">Shopping for</span>
                  <div className="filter-bar" style={{ marginBottom: 0, marginTop: 4 }}>
                    {GENDERS.map(g => (
                      <button
                        key={g}
                        className={`filter-btn ${gender === g ? "active" : ""}`}
                        onClick={() => changeGender(g)}
                      >
                        {g.charAt(0).toUpperCase() + g.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="filter-bar">
                  {resultStores.map(s => (
                    <button
                      key={s}
                      className={`filter-btn ${activeStore === s ? "active" : ""}`}
                      onClick={() => setActiveStore(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
                <div className="results-grid">
                  {filtered.map((item, i) => (
                    <ResultCard key={item.id} item={item} index={i} />
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </>
  );
}