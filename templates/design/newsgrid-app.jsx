// NEWSGRID — app shell, header, category nav, browse / watch views
const { CATEGORIES, VIDEOS, formatViews } = window.NEWSGRID_DATA;

function useMediaQuery(q) {
  const [m, setM] = React.useState(() => typeof window !== 'undefined' && window.matchMedia(q).matches);
  React.useEffect(() => {
    const mm = window.matchMedia(q);
    const fn = (e) => setM(e.matches);
    mm.addEventListener('change', fn);
    return () => mm.removeEventListener('change', fn);
  }, [q]);
  return m;
}

// ---------- Header ----------
function Header({ query, setQuery, onOpenMenu }) {
  const [focused, setFocused] = React.useState(false);
  return (
    <header className="sticky top-0 z-40 bg-ink-950/85 backdrop-blur-xl border-b border-ink-800/70">
      <div className="max-w-[1400px] mx-auto px-4 md:px-8 h-16 flex items-center gap-4 md:gap-8">
        {/* Mobile menu */}
        <button
          type="button"
          onClick={onOpenMenu}
          className="md:hidden p-2 -ml-2 text-ink-300 hover:text-ink-100"
          aria-label="Open menu"
        >
          <Icon name="menu" size={20} />
        </button>

        {/* Logo */}
        <a href="#" className="flex items-center gap-2.5 shrink-0 group">
          <span className="relative inline-flex items-center justify-center w-7 h-7 rounded-sm bg-ember text-ink-950">
            <span className="font-serif text-[18px] leading-none translate-y-px">N</span>
            <span className="absolute -right-0.5 -bottom-0.5 w-1.5 h-1.5 rounded-full bg-ink-100 ring-2 ring-ink-950" />
          </span>
          <div className="flex items-baseline gap-1.5">
            <span className="font-serif text-[22px] leading-none text-ink-100 tracking-tight">NEWSGRID</span>
            <span className="hidden sm:inline font-mono text-[10px] uppercase tracking-[0.2em] text-ink-500 translate-y-px">/ video</span>
          </div>
        </a>

        {/* Nav links (desktop) */}
        <nav className="hidden lg:flex items-center gap-1 text-[13px] text-ink-400">
          {['Home', 'Shows', 'Live', 'Politics', 'Nation', 'Newsletters'].map((l, i) => (
            <a
              key={l}
              href="#"
              className={`px-3 py-2 rounded-md hover:text-ink-100 transition ${i === 1 ? 'text-ink-100' : ''}`}
            >
              {l}
            </a>
          ))}
        </nav>

        {/* Search */}
        <div className={`flex-1 max-w-xl ml-auto md:ml-0 transition-all ${focused ? 'md:max-w-2xl' : ''}`}>
          <label className={`group relative flex items-center gap-2 h-10 rounded-md bg-ink-900 ring-1 transition px-3
            ${focused ? 'ring-ember/50 bg-ink-850' : 'ring-ink-800 hover:ring-ink-700'}`}
          >
            <Icon name="search" size={16} className="text-ink-500 group-focus-within:text-ember" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="Search shows, hosts, topics…"
              className="flex-1 bg-transparent outline-none text-[14px] placeholder:text-ink-600 text-ink-100"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="text-ink-500 hover:text-ink-200 p-1 -mr-1"
                aria-label="Clear search"
              >
                <Icon name="x" size={14} />
              </button>
            )}
            <span className="hidden md:inline-flex items-center gap-1 font-mono text-[10px] text-ink-600 pl-2 ml-1 border-l border-ink-800">
              <kbd className="px-1 py-0.5 rounded bg-ink-900 ring-1 ring-ink-800">⌘</kbd>
              <kbd className="px-1 py-0.5 rounded bg-ink-900 ring-1 ring-ink-800">K</kbd>
            </span>
          </label>
        </div>

        {/* Right utilities */}
        <div className="hidden md:flex items-center gap-1 shrink-0">
          <button className="p-2 text-ink-400 hover:text-ink-100 transition rounded-md" aria-label="Notifications">
            <Icon name="bell" size={18} />
          </button>
          <button className="p-2 text-ink-400 hover:text-ink-100 transition rounded-md" aria-label="Saved">
            <Icon name="bookmark" size={18} />
          </button>
          <button className="ml-2 inline-flex items-center gap-2 h-9 px-3 rounded-md bg-ink-100 text-ink-950 text-[13px] font-medium hover:bg-white transition">
            <Icon name="user" size={14} strokeWidth={2} />
            Sign in
          </button>
        </div>
      </div>
    </header>
  );
}

// ---------- Category sub-nav ----------
function CategoryBar({ categories, active, setActive, counts }) {
  const scrollRef = React.useRef(null);
  const [edges, setEdges] = React.useState({ left: false, right: true });

  const updateEdges = React.useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const left = el.scrollLeft > 4;
    const right = el.scrollLeft + el.clientWidth < el.scrollWidth - 4;
    setEdges({ left, right });
  }, []);

  React.useEffect(() => {
    updateEdges();
    const el = scrollRef.current;
    if (!el) return;
    el.addEventListener('scroll', updateEdges, { passive: true });
    window.addEventListener('resize', updateEdges);
    return () => {
      el.removeEventListener('scroll', updateEdges);
      window.removeEventListener('resize', updateEdges);
    };
  }, [updateEdges]);

  const scrollBy = (dir) => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollBy({ left: dir * Math.max(240, el.clientWidth * 0.6), behavior: 'smooth' });
  };

  return (
    <div className="sticky top-16 z-30 bg-ink-950/85 backdrop-blur-xl border-b border-ink-800/70">
      <div className="relative max-w-[1400px] mx-auto px-4 md:px-8">
        {/* fade masks */}
        <div className={`pointer-events-none absolute left-4 md:left-8 top-0 bottom-0 w-12 bg-gradient-to-r from-ink-950 to-transparent transition-opacity ${edges.left ? 'opacity-100' : 'opacity-0'}`} />
        <div className={`pointer-events-none absolute right-4 md:right-8 top-0 bottom-0 w-12 bg-gradient-to-l from-ink-950 to-transparent transition-opacity ${edges.right ? 'opacity-100' : 'opacity-0'}`} />

        {/* L/R arrows on wide screens */}
        <button
          onClick={() => scrollBy(-1)}
          className={`hidden md:flex items-center justify-center absolute left-1 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-ink-900 ring-1 ring-ink-800 text-ink-300 hover:text-ink-100 hover:bg-ink-850 transition z-10 ${edges.left ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          aria-label="Scroll categories left"
        >
          <Icon name="chevron-left" size={14} />
        </button>
        <button
          onClick={() => scrollBy(1)}
          className={`hidden md:flex items-center justify-center absolute right-1 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-ink-900 ring-1 ring-ink-800 text-ink-300 hover:text-ink-100 hover:bg-ink-850 transition z-10 ${edges.right ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
          aria-label="Scroll categories right"
        >
          <Icon name="chevron-right" size={14} />
        </button>

        <div
          ref={scrollRef}
          className="no-scrollbar overflow-x-auto -mx-1 px-1"
        >
          <div className="flex items-stretch min-w-max">
            {categories.map((c) => (
              <CategoryChip
                key={c}
                label={c}
                count={counts[c]}
                active={active === c}
                onClick={() => setActive(c)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- Hero (featured) ----------
function Hero({ featured, onOpen }) {
  return (
    <section className="relative overflow-hidden rounded-xl ring-1 ring-white/5 bg-ink-900">
      <div className="grid lg:grid-cols-[1.45fr_1fr]">
        {/* Visual */}
        <div className="relative">
          <Thumbnail video={featured} overlay={false} ratio="16/9" />
          <div className="absolute inset-0 bg-gradient-to-r from-ink-950/85 via-ink-950/30 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink-950/75 via-transparent to-transparent lg:hidden" />

          {/* On-air strip */}
          <div className="absolute top-5 left-5 flex items-center gap-2">
            {featured.isLive ? (
              <span className="inline-flex items-center gap-2 rounded-sm bg-live px-2.5 py-1 font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-ink-100">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-ink-100 live-dot" />
                LIVE · ON AIR
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-sm bg-ember px-2.5 py-1 font-mono text-[11px] font-medium uppercase tracking-[0.18em] text-ink-950">
                FEATURED
              </span>
            )}
            <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-ink-300">{featured.category}</span>
          </div>

          {/* On the air ticker */}
          <div className="absolute bottom-5 left-5 right-5 flex items-center gap-3 font-mono text-[11px] text-ink-300 lg:hidden">
            <span className="inline-flex items-center gap-1.5">
              <Icon name="users" size={12} />
              {formatViews(featured.views)} watching
            </span>
            <span className="text-ink-700">·</span>
            <span>{featured.host}</span>
          </div>
        </div>

        {/* Text panel */}
        <div className="relative p-6 md:p-10 lg:p-12 flex flex-col justify-center bg-gradient-to-br from-ink-900 to-ink-950">
          <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-ember-soft mb-3">
            The Lead · {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </div>
          <h1 className="font-serif text-3xl md:text-4xl lg:text-[44px] leading-[1.05] text-ink-100 text-balance">
            {featured.title}
          </h1>
          <p className="mt-4 text-[15px] leading-relaxed text-ink-400 text-pretty max-w-prose">
            {featured.description}
          </p>

          <div className="mt-7 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => onOpen(featured)}
              className="group inline-flex items-center gap-2.5 h-11 px-5 rounded-md bg-ink-100 text-ink-950 font-medium text-[14px] hover:bg-white transition"
            >
              <span className="relative inline-flex items-center justify-center w-5 h-5 rounded-full bg-ember text-ink-950">
                <Icon name="play" size={11} strokeWidth={2.5} />
              </span>
              {featured.isLive ? 'Watch live' : 'Play now'}
            </button>
            <button className="inline-flex items-center gap-2 h-11 px-4 rounded-md ring-1 ring-ink-700 hover:ring-ink-500 hover:bg-ink-900 text-ink-200 text-[14px] transition">
              <Icon name="plus" size={14} />
              Add to list
            </button>
            <div className="hidden md:flex items-center gap-2 ml-1 font-mono text-[11px] text-ink-500">
              <Icon name="users" size={12} />
              {formatViews(featured.views)} watching
            </div>
          </div>

          {/* meta row */}
          <div className="mt-8 pt-6 border-t border-ink-800 grid grid-cols-3 gap-4 text-[12px]">
            <div>
              <div className="font-mono uppercase tracking-[0.16em] text-ink-600 mb-1">Anchor</div>
              <div className="text-ink-200">{featured.host}</div>
            </div>
            <div>
              <div className="font-mono uppercase tracking-[0.16em] text-ink-600 mb-1">Updated</div>
              <div className="text-ink-200">{featured.uploaded}</div>
            </div>
            <div>
              <div className="font-mono uppercase tracking-[0.16em] text-ink-600 mb-1">Segment</div>
              <div className="text-ink-200">{featured.chip}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ---------- Mobile drawer ----------
function MobileDrawer({ open, onClose, categories, active, setActive, counts }) {
  return (
    <div className={`fixed inset-0 z-50 md:hidden ${open ? '' : 'pointer-events-none'}`}>
      <div
        className={`absolute inset-0 bg-ink-950/70 backdrop-blur-sm transition-opacity ${open ? 'opacity-100' : 'opacity-0'}`}
        onClick={onClose}
      />
      <aside
        className={`absolute left-0 top-0 bottom-0 w-[82%] max-w-sm bg-ink-900 border-r border-ink-800 transition-transform duration-300 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="h-16 px-5 flex items-center justify-between border-b border-ink-800">
          <span className="font-serif text-xl text-ink-100">NEWSGRID</span>
          <button onClick={onClose} className="p-2 text-ink-300" aria-label="Close menu"><Icon name="x" /></button>
        </div>
        <div className="px-3 py-4 overflow-y-auto h-[calc(100%-4rem)] scrollbar-thin">
          <div className="px-2 pb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-600">Shows & sections</div>
          <ul className="space-y-1">
            {categories.map((c) => (
              <li key={c}>
                <button
                  onClick={() => { setActive(c); onClose(); }}
                  className={`w-full text-left flex items-center justify-between px-3 py-2.5 rounded-md text-[14px] transition
                    ${active === c ? 'bg-ink-850 text-ink-100' : 'text-ink-300 hover:bg-ink-850/60 hover:text-ink-100'}`}
                >
                  <span className="inline-flex items-center gap-2">
                    {active === c && <span className="inline-block w-1 h-4 bg-ember rounded-full" />}
                    {c}
                  </span>
                  <span className="font-mono text-[11px] text-ink-600">{counts[c] ?? 0}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
}

// ---------- Watch view ----------
function WatchView({ video, all, onOpen, onClose }) {
  const related = React.useMemo(() => {
    return all
      .filter((v) => v.id !== video.id)
      .sort((a, b) => {
        const sameA = a.category === video.category ? 0 : 1;
        const sameB = b.category === video.category ? 0 : 1;
        if (sameA !== sameB) return sameA - sameB;
        return b.views - a.views;
      })
      .slice(0, 10);
  }, [video, all]);

  React.useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [video.id]);

  return (
    <div className="fade-up">
      <button
        type="button"
        onClick={onClose}
        className="inline-flex items-center gap-2 mb-5 text-[13px] text-ink-400 hover:text-ink-100 transition"
      >
        <Icon name="arrow-left" size={14} />
        Back to all shows
      </button>

      <div className="grid lg:grid-cols-[1fr_360px] gap-8">
        {/* Main column */}
        <div>
          <PlayerSurface video={video} onClose={onClose} />

          <div className="mt-6 flex items-center gap-2 text-[11px] font-mono uppercase tracking-[0.18em]">
            <span className="text-ember-soft">{video.chip}</span>
            <span className="text-ink-700">·</span>
            <span className="text-ink-400">{video.category}</span>
            <span className="text-ink-700">·</span>
            <span className="text-ink-500">{video.uploaded}</span>
          </div>

          <h1 className="mt-3 font-serif text-3xl md:text-4xl text-ink-100 leading-tight text-balance">
            {video.title}
          </h1>

          <div className="mt-5 flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-ink-800">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-ember-deep to-ember flex items-center justify-center text-ink-950 font-serif text-lg">
                {video.host.charAt(0)}
              </div>
              <div>
                <div className="text-[14px] text-ink-100">{video.host}</div>
                <div className="font-mono text-[11px] text-ink-500">Anchor · {video.category}</div>
              </div>
              <button className="ml-3 h-8 px-3 rounded-md bg-ink-100 text-ink-950 text-[12px] font-medium hover:bg-white transition">Follow</button>
            </div>
            <div className="flex items-center gap-1 text-ink-400">
              {[
                ['thumbs-up', formatViews(Math.floor(video.views * 0.08))],
                ['message-square', formatViews(Math.floor(video.views * 0.01))],
                ['share-2', 'Share'],
                ['bookmark', 'Save'],
                ['more-horizontal', null],
              ].map(([ic, label]) => (
                <button key={ic} className="inline-flex items-center gap-1.5 h-8 px-3 rounded-md hover:bg-ink-900 hover:text-ink-100 transition text-[12px]">
                  <Icon name={ic} size={14} />
                  {label && <span>{label}</span>}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5 rounded-lg bg-ink-900/70 ring-1 ring-ink-800 p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink-500">
                {formatViews(video.views)} views · Aired {video.uploaded}
              </div>
              <button className="font-mono text-[11px] text-ember-soft hover:text-ember transition">Transcript →</button>
            </div>
            <p className="text-[15px] leading-relaxed text-ink-300 text-pretty">{video.description}</p>
            <p className="mt-3 text-[15px] leading-relaxed text-ink-400 text-pretty">
              This segment is part of NEWSGRID's daily coverage. Replays available for thirty days. Captions in EN, ES.
            </p>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {[video.category, video.chip, 'Politics', 'Daily Brief', '2026'].map((t) => (
                <span key={t} className="inline-flex items-center px-2 py-1 rounded font-mono text-[10px] uppercase tracking-wider bg-ink-850 text-ink-300 ring-1 ring-ink-800">
                  #{t.replace(/[\s:]/g, '')}
                </span>
              ))}
            </div>
          </div>

          {/* Chapter list (faux) */}
          <div className="mt-8">
            <SectionHeader kicker="In this episode" title="Chapters" />
            <ol className="divide-y divide-ink-850 rounded-lg ring-1 ring-ink-800 bg-ink-900/40">
              {[
                ['00:00', 'Cold open'],
                ['02:14', 'The day in five minutes'],
                ['07:35', 'On-the-ground report'],
                ['18:02', 'Panel: what changed today'],
                ['31:48', 'One more thing'],
              ].map(([t, label], i) => (
                <li key={i} className="flex items-center gap-4 px-4 py-3 hover:bg-ink-900 transition cursor-pointer">
                  <span className="font-mono text-[12px] text-ember-soft tabular-nums w-14">{t}</span>
                  <span className="text-ink-100 text-[14px] flex-1">{label}</span>
                  <Icon name="play" size={14} className="text-ink-500" />
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Sidebar */}
        <aside className="lg:sticky lg:top-32 self-start">
          <div className="font-mono text-[11px] uppercase tracking-[0.22em] text-ink-500 mb-3 px-1">Up Next</div>
          <div className="space-y-1">
            {related.map((v) => (
              <RelatedCard key={v.id} video={v} onOpen={onOpen} />
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}

// ---------- Browse view ----------
function BrowseView({ videos, allVisible, activeCategory, query, onOpen, featured }) {
  const showHero = activeCategory === 'All Shows' && !query;
  const rows = videos;

  return (
    <div className="space-y-12">
      {showHero && featured && <Hero featured={featured} onOpen={onOpen} />}

      {showHero && (
        <section>
          <SectionHeader
            kicker="Now playing across the network"
            title="On air now"
            action={
              <a href="#" className="hidden md:inline-flex items-center gap-1 text-[12px] text-ink-400 hover:text-ink-100 font-mono uppercase tracking-wider">
                Full schedule <Icon name="arrow-right" size={12} />
              </a>
            }
          />
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-5 gap-y-8">
            {allVisible.filter((v) => v.isLive).slice(0, 4).map((v) => (
              <VideoCard key={v.id} video={v} onOpen={onOpen} />
            ))}
            {allVisible.filter((v) => v.isLive).length === 0 && (
              <div className="col-span-full text-ink-500 text-sm">No segments live at the moment.</div>
            )}
          </div>
        </section>
      )}

      <section>
        <SectionHeader
          kicker={query ? `Results for "${query}"` : activeCategory === 'All Shows' ? 'Latest across every show' : `Latest from ${activeCategory}`}
          title={query ? `${rows.length} ${rows.length === 1 ? 'segment' : 'segments'}` : (activeCategory === 'All Shows' ? 'Latest video' : activeCategory)}
          action={
            <div className="hidden md:flex items-center gap-2 text-[12px] text-ink-500 font-mono">
              <Icon name="sliders-horizontal" size={12} />
              <span className="text-ink-400">Sort:</span>
              <span className="text-ink-100">Newest</span>
              <Icon name="chevron-down" size={12} />
            </div>
          }
        />

        {rows.length === 0 ? (
          <div className="rounded-lg ring-1 ring-ink-800 bg-ink-900/40 p-12 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-ink-850 text-ink-400 mb-4">
              <Icon name="search-x" size={20} />
            </div>
            <div className="font-serif text-xl text-ink-100">Nothing matches that search.</div>
            <div className="text-ink-500 text-sm mt-1">Try a different term, or clear filters to see every segment.</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-5 gap-y-10">
            {rows.map((v) => (
              <VideoCard key={v.id} video={v} onOpen={onOpen} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

// ---------- App ----------
function App() {
  const [query, setQuery] = React.useState('');
  const [active, setActive] = React.useState('All Shows');
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [playing, setPlaying] = React.useState(null); // video being watched

  // ⌘K focuses search
  React.useEffect(() => {
    const fn = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const input = document.querySelector('input[placeholder^="Search"]');
        input?.focus();
      }
      if (e.key === 'Escape' && playing) setPlaying(null);
    };
    window.addEventListener('keydown', fn);
    return () => window.removeEventListener('keydown', fn);
  }, [playing]);

  // Filter by category + search
  const allVisible = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return VIDEOS.filter((v) => {
      if (active !== 'All Shows' && v.category !== active) return false;
      if (!q) return true;
      return (
        v.title.toLowerCase().includes(q) ||
        v.description.toLowerCase().includes(q) ||
        v.host.toLowerCase().includes(q) ||
        v.category.toLowerCase().includes(q)
      );
    });
  }, [query, active]);

  const counts = React.useMemo(() => {
    const c = { 'All Shows': VIDEOS.length };
    for (const v of VIDEOS) c[v.category] = (c[v.category] || 0) + 1;
    return c;
  }, []);

  const featured = VIDEOS[0];

  // When activeCategory is the default and no search, hero shows. Otherwise grid only.
  const onOpen = (v) => setPlaying(v);
  const onCloseWatch = () => setPlaying(null);

  return (
    <div className="min-h-screen text-ink-100">
      <Header query={query} setQuery={setQuery} onOpenMenu={() => setDrawerOpen(true)} />
      <CategoryBar
        categories={CATEGORIES}
        active={active}
        setActive={(c) => { setActive(c); setPlaying(null); }}
        counts={counts}
      />
      <MobileDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        categories={CATEGORIES}
        active={active}
        setActive={setActive}
        counts={counts}
      />

      <main className="max-w-[1400px] mx-auto px-4 md:px-8 py-8 md:py-10">
        {playing ? (
          <WatchView
            video={playing}
            all={VIDEOS}
            onOpen={onOpen}
            onClose={onCloseWatch}
          />
        ) : (
          <BrowseView
            videos={allVisible}
            allVisible={VIDEOS /* live strip pulls from full library */}
            activeCategory={active}
            query={query}
            onOpen={onOpen}
            featured={featured}
          />
        )}
      </main>

      <footer className="border-t border-ink-800 mt-16">
        <div className="max-w-[1400px] mx-auto px-4 md:px-8 py-10 grid md:grid-cols-4 gap-8 text-[13px]">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5">
              <span className="relative inline-flex items-center justify-center w-7 h-7 rounded-sm bg-ember text-ink-950">
                <span className="font-serif text-[18px] leading-none translate-y-px">N</span>
              </span>
              <span className="font-serif text-xl text-ink-100">NEWSGRID</span>
            </div>
            <p className="mt-3 text-ink-500 max-w-sm">
              An independent video newsroom. Replays available for thirty days. Captions and transcripts in every language we cover.
            </p>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-600 mb-3">Network</div>
            <ul className="space-y-2 text-ink-400">
              <li><a href="#" className="hover:text-ink-100">Shows</a></li>
              <li><a href="#" className="hover:text-ink-100">Live schedule</a></li>
              <li><a href="#" className="hover:text-ink-100">Anchors</a></li>
              <li><a href="#" className="hover:text-ink-100">Newsletters</a></li>
            </ul>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-600 mb-3">Company</div>
            <ul className="space-y-2 text-ink-400">
              <li><a href="#" className="hover:text-ink-100">About</a></li>
              <li><a href="#" className="hover:text-ink-100">Careers</a></li>
              <li><a href="#" className="hover:text-ink-100">Press</a></li>
              <li><a href="#" className="hover:text-ink-100">Terms & Privacy</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-ink-850">
          <div className="max-w-[1400px] mx-auto px-4 md:px-8 py-5 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono uppercase tracking-[0.18em] text-ink-600">
            <span>© 2026 NEWSGRID Media</span>
            <span>Built for the way news actually moves.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
