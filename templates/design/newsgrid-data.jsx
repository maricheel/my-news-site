// NEWSGRID — mock data
// Categories are factual show-name labels; all visual treatment is original.

const CATEGORIES = [
  'All Shows',
  'Morning Joe',
  'Chris Jansing Reports',
  'Katy Tur Reports',
  'Deadline: White House',
  'The Beat',
  'The Weeknight',
  'All In',
  'Rachel Maddow',
  'Jen Psaki',
  "Lawrence O'Donnell",
  '11th Hour',
  'The Weekend',
  'Velshi',
  'Alex Witt',
  'Politics',
  'Nation',
  'Weekend Primetime',
];

// Curated abstract palettes used to generate striped SVG placeholders.
// Each palette is intentionally muted to read as editorial, not stock-photo.
const PALETTES = [
  ['oklch(0.34 0.06 30)',  'oklch(0.22 0.04 25)',  'oklch(0.55 0.13 35)'],   // ember dusk
  ['oklch(0.30 0.04 250)', 'oklch(0.20 0.03 250)', 'oklch(0.48 0.08 245)'],  // slate blue
  ['oklch(0.32 0.05 145)', 'oklch(0.22 0.03 145)', 'oklch(0.50 0.09 140)'],  // pine
  ['oklch(0.34 0.05 80)',  'oklch(0.24 0.03 80)',  'oklch(0.55 0.10 75)'],   // umber
  ['oklch(0.30 0.04 320)', 'oklch(0.21 0.03 320)', 'oklch(0.48 0.10 315)'],  // mauve
  ['oklch(0.32 0.03 210)', 'oklch(0.22 0.02 210)', 'oklch(0.50 0.06 205)'],  // gunmetal
  ['oklch(0.30 0.05 50)',  'oklch(0.21 0.03 50)',  'oklch(0.52 0.11 45)'],   // copper
];

const HEADLINES = [
  ['Senate Floor Erupts Over Late-Night Vote',                'Lawmakers traded sharp accusations as a procedural motion stalled past midnight, exposing fault lines that could reshape next month\'s budget fight.'],
  ['Inside the West Wing\'s Quiet Reshuffle',                  'Three senior advisors have rotated portfolios in the last ten days. We map the new chain of command and what it signals about policy priorities.'],
  ['Court Hands Down Surprise Ruling on Voting Maps',         'A 5–4 decision sends the case back to a three-judge panel and reopens questions about boundaries drawn in seven contested districts.'],
  ['The Quiet Economy: What the Jobs Report Missed',          'Beneath the headline number, sectors are diverging. Our reporter walks through the regional charts and what they mean for the fall.'],
  ['Foreign Capitals React to the New Sanctions Package',     'Allies are calibrating their public statements while privately pressing for carve-outs. We have reporting from three embassies.'],
  ['A Mayor, a Federal Probe, and a City on Edge',            'Documents obtained this week describe a widening inquiry. The mayor denies wrongdoing and vows to finish the term.'],
  ['Climate Bill Passes Committee on Razor-Thin Margin',      'Two centrist defections nearly killed the package. The lead sponsor walks us through the late-night negotiation that saved it.'],
  ['The Generals Are Talking. Quietly.',                      'Retired commanders are increasingly weighing in on civilian policy. A conversation about norms, restraint, and the line between the two.'],
  ['What the Polling Actually Says About the Suburbs',        'Crosstabs from the last four national surveys point to a more complicated picture than the headlines suggest. We dig into the data.'],
  ['A Long Conversation with the Outgoing Whip',              'Forty minutes on legacy, regret, the future of the caucus, and the one vote she says she would take back.'],
  ['The Local Race That National Parties Are Watching',       'A special election in a mid-sized district has become an unlikely test case for messaging, turnout, and the cost of a single ad buy.'],
  ['Markets Wobble on Inflation Print',                       'Equities slipped in early trading as a hotter-than-expected reading complicates the Fed\'s next move. Three analysts weigh in.'],
  ['The Border, By the Numbers',                              'New monthly figures from CBP, parsed against the rhetoric. Where the data confirms the talking points — and where it doesn\'t.'],
  ['Hospital Systems Brace for Funding Cliff',                'Administrators in four states describe contingency plans as a key reimbursement program approaches expiration.'],
  ['A Trial, A Verdict, A Question of Precedent',             'Legal scholars are split on how narrowly today\'s ruling can be read. We asked five of them to draw the line.'],
  ['The Memo That Quietly Changed Everything',                'A two-page document circulated inside the agency last spring is now at the center of a Congressional inquiry. Read the key passages.'],
  ['Saturday Politics, In Plain English',                     'The week\'s biggest stories, sorted by what actually mattered, what didn\'t, and what got buried under the noise.'],
  ['One Senator, One Filibuster, One Quiet Backroom',         'How a single procedural objection became the lever that moved an entire week of floor business.'],
  ['Governors\' Roundtable: The Year Ahead',                   'Three governors, one moderator, and a candid conversation about what the states are doing while Washington argues.'],
  ['The Speech That Wasn\'t Supposed to Land',                 'Aides expected polite applause. They got a standing ovation. What changed in the room — and what it means going forward.'],
  ['Anatomy of a Walkout',                                    'A minute-by-minute reconstruction of yesterday\'s dramatic committee exit, assembled from staff interviews and floor video.'],
  ['Why This Primary Isn\'t Over',                             'The frontrunner has the delegates. But the math, the calendar, and the donor class all tell a more complicated story.'],
  ['The Quiet Diplomacy of the Last 72 Hours',                'A timeline of back-channel calls between three capitals, and the deal that almost — but didn\'t quite — get done.'],
  ['Saturday Long Read: The Education Fight Nobody\'s Watching','Curriculum battles in two school districts are quietly reshaping how civics is taught nationwide. A 20-minute deep-dive.'],
  ['Late Night: The Stories We Couldn\'t Get To',              'Five threads from today\'s news cycle that deserved more attention than the segment clock allowed. We catch up on all of them.'],
  ['The Witness List Just Got Longer',                        'Two new names were added to next week\'s hearing roster. Both have direct knowledge of the events in question.'],
  ['How the New Tariffs Land at the Port',                    'We spent the morning on a dock in Long Beach. Here\'s what the operators, drivers, and customs brokers are actually seeing.'],
  ['A Question for the Attorney General',                     'It has been forty-one days since the press office last took a question on this topic. We compiled the ones still waiting.'],
];

const HOSTS_BY_CATEGORY = {
  'Morning Joe':            ['Joe & Mika',        'Willie Geist'],
  'Chris Jansing Reports':  ['Chris Jansing'],
  'Katy Tur Reports':       ['Katy Tur'],
  'Deadline: White House':  ['Nicolle Wallace'],
  'The Beat':               ['Ari Melber'],
  'The Weeknight':          ['Symone, Alicia & Michael'],
  'All In':                 ['Chris Hayes'],
  'Rachel Maddow':          ['Rachel Maddow'],
  'Jen Psaki':              ['Jen Psaki'],
  "Lawrence O'Donnell":     ["Lawrence O'Donnell"],
  '11th Hour':              ['Stephanie Ruhle'],
  'The Weekend':            ['Symone, Alicia & Michael'],
  'Velshi':                 ['Ali Velshi'],
  'Alex Witt':              ['Alex Witt'],
  'Politics':               ['Newsroom Desk'],
  'Nation':                 ['National Desk'],
  'Weekend Primetime':      ['Weekend Anchors'],
};

const CHIPS = ['Breaking', 'Analysis', 'Interview', 'Live', 'Long Read', 'Recap', 'On the Record', 'Field Report'];

function rand(seed) {
  // Deterministic PRNG so the page renders identically every reload.
  let s = seed | 0;
  return () => {
    s = (s * 1664525 + 1013904223) | 0;
    return ((s >>> 0) % 100000) / 100000;
  };
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m >= 60) {
    const h = Math.floor(m / 60);
    const mm = m % 60;
    return `${h}:${String(mm).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  }
  return `${m}:${String(s).padStart(2,'0')}`;
}

function relTime(daysAgo, hoursAgo) {
  if (daysAgo === 0 && hoursAgo < 1) return 'Just now';
  if (daysAgo === 0) return `${hoursAgo}h ago`;
  if (daysAgo === 1) return 'Yesterday';
  if (daysAgo < 7)   return `${daysAgo}d ago`;
  if (daysAgo < 30)  return `${Math.floor(daysAgo / 7)}w ago`;
  return `${Math.floor(daysAgo / 30)}mo ago`;
}

function formatViews(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(n);
}

// Build a deterministic library of ~56 videos across the show categories.
function buildLibrary() {
  const r = rand(20260522);
  const showCats = CATEGORIES.slice(1);
  const out = [];
  let id = 1;

  for (let i = 0; i < 56; i++) {
    const cat = showCats[Math.floor(r() * showCats.length)];
    const [title, description] = HEADLINES[i % HEADLINES.length];
    const palette = PALETTES[Math.floor(r() * PALETTES.length)];
    const durationSec = 60 + Math.floor(r() * 60 * 55); // 1 min – ~55 min
    const hoursAgo = Math.floor(r() * 23) + 1;
    const daysAgo = Math.floor(r() * 21);
    const views = 1200 + Math.floor(r() * 980_000);
    const hosts = HOSTS_BY_CATEGORY[cat] || ['Newsroom'];
    const host = hosts[Math.floor(r() * hosts.length)];
    const chip = CHIPS[Math.floor(r() * CHIPS.length)];
    const isLive = i < 3 && r() > 0.55;

    out.push({
      id: id++,
      title,
      description,
      category: cat,
      host,
      chip,
      isLive,
      durationSec,
      duration: isLive ? 'LIVE' : formatDuration(durationSec),
      uploadedHoursAgo: hoursAgo,
      uploadedDaysAgo: daysAgo,
      uploaded: isLive ? 'On air now' : relTime(daysAgo, hoursAgo),
      views,
      viewsLabel: formatViews(views) + (views === 1 ? ' view' : ' views'),
      thumbnail: { palette, seed: i },
      videoUrl: 'about:blank', // placeholder — UI shows a poster + transport
    });
  }

  // Ensure one obvious "featured" lead story sits up top.
  out[0] = {
    ...out[0],
    title: 'The Hearing That Could Reset the Year',
    description:
      'Five witnesses, four hours of testimony, and a chair who has signaled this will not be the last session. Our political team walks you through what was said, what wasn\'t, and what to watch for when the committee reconvenes.',
    chip: 'Breaking',
    isLive: true,
    duration: 'LIVE',
    uploaded: 'On air now',
    category: 'Politics',
    host: 'Newsroom Desk',
  };

  return out;
}

const VIDEOS = buildLibrary();

window.NEWSGRID_DATA = { CATEGORIES, VIDEOS, formatDuration, formatViews, relTime };
