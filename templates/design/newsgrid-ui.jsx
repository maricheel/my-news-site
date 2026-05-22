// NEWSGRID — UI primitives
// All thumbnails are generated as inline SVGs with monospace captions, so the
// page works offline and there's no dependency on stock image hosts.

const { useEffect, useRef, useState, useMemo, useCallback } = React;

// ---------- Lucide icon wrapper ----------
function Icon({ name, size = 18, className = '', strokeWidth = 1.75 }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current || !window.lucide) return;
    ref.current.innerHTML = '';
    const el = document.createElement('i');
    el.setAttribute('data-lucide', name);
    ref.current.appendChild(el);
    window.lucide.createIcons({
      attrs: { width: size, height: size, 'stroke-width': strokeWidth },
      nameAttr: 'data-lucide',
    });
  }, [name, size, strokeWidth]);
  return <span ref={ref} className={`inline-flex items-center justify-center ${className}`} aria-hidden="true" />;
}

// ---------- Editorial SVG thumbnail ----------
// A muted abstract poster with show name in mono — feels like a chyron card.
function Thumbnail({ video, ratio = '16/9', overlay = true, scale = 1 }) {
  const { palette, seed } = video.thumbnail;
  const [bg, mid, accent] = palette;
  const angle = 110 + ((seed * 37) % 60);

  // Deterministic pseudo-random for sparkline-ish accent shape.
  const points = useMemo(() => {
    const pts = [];
    let s = (seed + 1) * 9301;
    for (let i = 0; i <= 12; i++) {
      s = (s * 1664525 + 1013904223) | 0;
      const y = 40 + (((s >>> 0) % 100) / 100) * 50;
      pts.push(`${(i / 12) * 320},${y}`);
    }
    return pts.join(' ');
  }, [seed]);

  return (
    <div
      className="relative w-full overflow-hidden bg-ink-900"
      style={{ aspectRatio: ratio }}
    >
      <svg viewBox="0 0 320 180" preserveAspectRatio="xMidYMid slice" className="absolute inset-0 w-full h-full">
        <defs>
          <linearGradient id={`g-${video.id}`} x1="0" y1="0" x2="1" y2="1" gradientTransform={`rotate(${angle}, 0.5, 0.5)`}>
            <stop offset="0%"  stopColor={bg} />
            <stop offset="55%" stopColor={mid} />
            <stop offset="100%" stopColor={accent} />
          </linearGradient>
          <pattern id={`stripes-${video.id}`} width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
            <rect width="14" height="14" fill="transparent" />
            <line x1="0" y1="0" x2="0" y2="14" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="320" height="180" fill={`url(#g-${video.id})`} />
        <rect width="320" height="180" fill={`url(#stripes-${video.id})`} />
        {/* faint horizon line */}
        <line x1="0" y1="120" x2="320" y2="120" stroke="rgba(255,255,255,0.06)" />
        {/* polyline accent — reads as "data" without being slop */}
        <polyline
          fill="none"
          stroke="rgba(255,255,255,0.22)"
          strokeWidth="1.25"
          points={points}
        />
        {/* small circle marker */}
        <circle cx="296" cy="24" r="3" fill="rgba(255,255,255,0.55)" />
      </svg>

      {overlay && (
        <>
          {/* gradient darkening for legibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-ink-950/85 via-ink-950/15 to-transparent" />

          {/* Show wordmark, mono, lower-left */}
          <div className="absolute left-3 bottom-3 right-3 flex items-end justify-between gap-2">
            <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-200/85 leading-tight">
              <div className="text-ink-300/70">{video.category}</div>
              <div className="text-ink-100/95">{video.host}</div>
            </div>
          </div>

          {/* Duration / LIVE badge, lower-right */}
          <div className="absolute right-3 top-3 flex items-center gap-1.5">
            {video.isLive ? (
              <span className="inline-flex items-center gap-1.5 rounded-sm bg-live/95 px-1.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.15em] text-ink-100">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-ink-100 live-dot" />
                LIVE
              </span>
            ) : (
              <span className="rounded-sm bg-ink-950/75 backdrop-blur-sm px-1.5 py-0.5 font-mono text-[10px] text-ink-100 ring-1 ring-white/10">
                {video.duration}
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ---------- Play affordance overlay ----------
function PlayOverlay({ size = 56 }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
      <div className="absolute inset-0 bg-ink-950/35" />
      <div
        className="relative rounded-full bg-ink-100 text-ink-950 flex items-center justify-center shadow-2xl shadow-black/40 ring-1 ring-white/40"
        style={{ width: size, height: size }}
      >
        <Icon name="play" size={Math.round(size * 0.42)} />
      </div>
    </div>
  );
}

// ---------- Video card (grid) ----------
function VideoCard({ video, onOpen, dense = false }) {
  return (
    <button
      type="button"
      onClick={() => onOpen(video)}
      className="group text-left fade-up focus:outline-none focus-visible:ring-2 focus-visible:ring-ember/70 focus-visible:ring-offset-2 focus-visible:ring-offset-ink-950 rounded-md"
    >
      <div className="relative overflow-hidden rounded-md ring-1 ring-white/5 group-hover:ring-white/15 transition">
        <Thumbnail video={video} />
        <PlayOverlay />
      </div>
      <div className={`mt-3 ${dense ? 'space-y-1' : 'space-y-1.5'}`}>
        <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.14em] text-ink-400">
          <span className="text-ember-soft">{video.chip}</span>
          <span className="text-ink-700">·</span>
          <span>{video.category}</span>
        </div>
        <h3 className="text-[15px] leading-snug font-medium text-ink-100 text-pretty group-hover:text-ember-soft transition-colors">
          {video.title}
        </h3>
        <div className="flex items-center gap-2 text-xs text-ink-500">
          <span>{video.host}</span>
          <span className="text-ink-700">·</span>
          <span>{video.uploaded}</span>
          <span className="text-ink-700">·</span>
          <span className="font-mono text-[11px]">{video.viewsLabel}</span>
        </div>
      </div>
    </button>
  );
}

// ---------- Compact "related" card (sidebar of watch view) ----------
function RelatedCard({ video, onOpen, active = false }) {
  return (
    <button
      type="button"
      onClick={() => onOpen(video)}
      className={`group w-full text-left flex gap-3 p-2 rounded-md transition ${
        active ? 'bg-ink-850 ring-1 ring-ember/30' : 'hover:bg-ink-900'
      }`}
    >
      <div className="relative w-36 shrink-0 overflow-hidden rounded ring-1 ring-white/5">
        <Thumbnail video={video} overlay={false} />
        <div className="absolute inset-0 bg-gradient-to-t from-ink-950/70 to-transparent" />
        <span className="absolute right-1.5 bottom-1.5 rounded-sm bg-ink-950/80 px-1 py-px font-mono text-[10px] text-ink-100">
          {video.duration}
        </span>
        {video.isLive && (
          <span className="absolute left-1.5 top-1.5 inline-flex items-center gap-1 rounded-sm bg-live/95 px-1 py-px font-mono text-[10px] uppercase tracking-wider text-ink-100">
            <span className="inline-block w-1 h-1 rounded-full bg-ink-100 live-dot" />
            LIVE
          </span>
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-[10px] font-mono uppercase tracking-[0.14em] text-ember-soft truncate">{video.category}</div>
        <div className="text-[13px] leading-snug text-ink-100 line-clamp-2 mt-0.5 group-hover:text-ember-soft transition-colors">
          {video.title}
        </div>
        <div className="text-[11px] text-ink-500 mt-1 truncate font-mono">{video.uploaded} · {video.viewsLabel}</div>
      </div>
    </button>
  );
}

// ---------- Category chip ----------
function CategoryChip({ label, active, count, onClick, innerRef }) {
  return (
    <button
      ref={innerRef}
      type="button"
      onClick={onClick}
      className={`relative whitespace-nowrap shrink-0 px-3 py-2 text-[13px] font-medium transition-colors
        ${active
          ? 'text-ink-100'
          : 'text-ink-400 hover:text-ink-200'
        }`}
    >
      <span className="inline-flex items-center gap-1.5">
        {label}
        {typeof count === 'number' && (
          <span className={`font-mono text-[10px] tabular-nums ${active ? 'text-ember-soft' : 'text-ink-600'}`}>
            {count}
          </span>
        )}
      </span>
      <span
        className={`pointer-events-none absolute left-2 right-2 -bottom-px h-px transition-colors ${
          active ? 'bg-ember' : 'bg-transparent'
        }`}
      />
    </button>
  );
}

// ---------- Faux player (poster + transport) ----------
function PlayerSurface({ video, onClose, compact = false }) {
  const [playing, setPlaying] = useState(true);
  const [progress, setProgress] = useState(video.isLive ? 1 : 0.18);
  const [muted, setMuted] = useState(false);
  const [seeking, setSeeking] = useState(false);
  const barRef = useRef(null);

  useEffect(() => {
    if (!playing || video.isLive || seeking) return;
    const t = setInterval(() => {
      setProgress((p) => (p >= 1 ? 1 : Math.min(1, p + 0.0035)));
    }, 250);
    return () => clearInterval(t);
  }, [playing, seeking, video.isLive]);

  const total = video.durationSec;
  const current = Math.floor(total * progress);
  const remaining = Math.max(0, total - current);

  const onScrub = (clientX) => {
    if (!barRef.current) return;
    const rect = barRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    setProgress(x);
  };

  return (
    <div className="relative w-full overflow-hidden bg-ink-950 rounded-lg ring-1 ring-white/10">
      <div className="relative">
        <Thumbnail video={video} overlay={false} ratio="16/9" />
        {/* Player vignette */}
        <div className="absolute inset-0 bg-gradient-to-t from-ink-950/85 via-ink-950/10 to-ink-950/35" />

        {/* Top strip */}
        <div className="absolute top-0 left-0 right-0 p-4 flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            {video.isLive && (
              <span className="inline-flex items-center gap-1.5 rounded-sm bg-live/95 px-2 py-1 font-mono text-[11px] font-medium uppercase tracking-[0.15em] text-ink-100">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-ink-100 live-dot" />
                LIVE
              </span>
            )}
            <span className="rounded-sm bg-ink-950/65 backdrop-blur-sm px-2 py-1 font-mono text-[11px] text-ink-200 ring-1 ring-white/10">
              {video.category}
            </span>
          </div>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-md bg-ink-950/65 backdrop-blur-sm p-2 text-ink-200 hover:text-ink-100 ring-1 ring-white/10 hover:ring-white/25 transition"
              aria-label="Close player"
            >
              <Icon name="x" size={16} />
            </button>
          )}
        </div>

        {/* Center play button */}
        <button
          type="button"
          onClick={() => setPlaying((p) => !p)}
          className="absolute inset-0 flex items-center justify-center group/play"
          aria-label={playing ? 'Pause' : 'Play'}
        >
          <span className={`rounded-full bg-ink-100/95 text-ink-950 flex items-center justify-center shadow-2xl shadow-black/50 ring-1 ring-white/40 transition-all
            ${playing ? 'opacity-0 group-hover/play:opacity-100 scale-90 group-hover/play:scale-100' : 'opacity-100 scale-100'}`}
            style={{ width: compact ? 64 : 80, height: compact ? 64 : 80 }}
          >
            <Icon name={playing ? 'pause' : 'play'} size={compact ? 26 : 32} />
          </span>
        </button>

        {/* Bottom transport */}
        <div className="absolute bottom-0 left-0 right-0 p-4 space-y-3">
          {!video.isLive && (
            <div
              ref={barRef}
              className="group/bar relative h-1 cursor-pointer"
              onMouseDown={(e) => { setSeeking(true); onScrub(e.clientX); }}
              onMouseMove={(e) => { if (seeking) onScrub(e.clientX); }}
              onMouseUp={() => setSeeking(false)}
              onMouseLeave={() => setSeeking(false)}
            >
              <div className="absolute inset-0 top-1/2 -translate-y-1/2 h-0.5 bg-white/15 rounded-full" />
              <div
                className="absolute top-1/2 -translate-y-1/2 h-0.5 bg-ember rounded-full"
                style={{ width: `${progress * 100}%` }}
              />
              <div
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-ember-soft shadow-md opacity-0 group-hover/bar:opacity-100 transition-opacity"
                style={{ left: `calc(${progress * 100}% - 6px)` }}
              />
            </div>
          )}
          <div className="flex items-center justify-between gap-3 text-ink-200">
            <div className="flex items-center gap-1">
              <button onClick={() => setPlaying((p) => !p)} className="p-2 hover:text-ink-100 transition" aria-label={playing ? 'Pause' : 'Play'}>
                <Icon name={playing ? 'pause' : 'play'} size={18} />
              </button>
              <button onClick={() => setProgress((p) => Math.max(0, p - 0.05))} className="p-2 hover:text-ink-100 transition" aria-label="Back 10s">
                <Icon name="rotate-ccw" size={16} />
              </button>
              <button onClick={() => setMuted((m) => !m)} className="p-2 hover:text-ink-100 transition" aria-label="Mute">
                <Icon name={muted ? 'volume-x' : 'volume-2'} size={18} />
              </button>
              <div className="ml-2 font-mono text-[12px] tabular-nums text-ink-300">
                {video.isLive ? (
                  <span className="text-live">● ON AIR</span>
                ) : (
                  <span>
                    {window.NEWSGRID_DATA.formatDuration(current)}
                    <span className="text-ink-600 mx-1.5">/</span>
                    <span className="text-ink-400">{window.NEWSGRID_DATA.formatDuration(total)}</span>
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button className="p-2 hover:text-ink-100 transition" aria-label="Captions"><Icon name="captions" size={18} /></button>
              <button className="p-2 hover:text-ink-100 transition" aria-label="Settings"><Icon name="settings" size={18} /></button>
              <button className="p-2 hover:text-ink-100 transition" aria-label="Fullscreen"><Icon name="maximize" size={18} /></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- Section header (editorial rule) ----------
function SectionHeader({ kicker, title, action }) {
  return (
    <div className="flex items-end justify-between gap-6 mb-5">
      <div>
        {kicker && (
          <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-ember-soft mb-2">
            {kicker}
          </div>
        )}
        <h2 className="font-serif text-2xl md:text-3xl text-ink-100 leading-none">{title}</h2>
      </div>
      {action}
    </div>
  );
}

Object.assign(window, { Icon, Thumbnail, PlayOverlay, VideoCard, RelatedCard, CategoryChip, PlayerSurface, SectionHeader });
