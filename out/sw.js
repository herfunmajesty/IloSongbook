// Service Worker for Krakow Ukulele Songbook PWA
const CACHE_NAME = 'uke-songbook-20261122133520';

// Core application shell files needed for basic offline functionality
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/songs.html',
  '/how.html',
  '/manifest.json',
  '/images/icon.png',
  '/images/icon.PNG',
  '/images/icon-192.png',
  '/images/icon-512.png',
  '/images/icon-maskable-512.png',
  '/images/qrcode.png',
  '/images/ukulele-krakow.PNG',
  '/images/ukulele-krakow-trans.png',
  '/images/ukulele-krakow-trans-dark.png',
  '/images/ukulele-krakow-trans-light.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
  'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
  'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap'
];

// Pre-cached song pages and chord diagrams (JSON encoded to prevent syntax errors with quotes or emojis)
const ALL_SONGS_AND_CHORDS = [
  "/(I-Can't-Get-No)-Satisfaction.html",
  "/19-2000.html",
  "/500-Miles-(I'm-Gonna-Be).html",
  "/A-Little-Respect.html",
  "/Accidentally-In-Love.html",
  "/After-Hours.html",
  "/Ain't-No-Sunshine.html",
  "/All-About-That-Bass.html",
  "/All-Apologies.html",
  "/All-Star-(Shrek).html",
  "/American-Idiot.html",
  "/Another-Brick-In-The-Wall.html",
  "/Another-Love.html",
  "/Bad-Moon-Rising.html",
  "/Bad-Romance.html",
  "/Bang-Bang.html",
  "/Basket-Case.html",
  "/Beggin'.html",
  "/Billie-Jean.html",
  "/Bitter-Sweet-Symphony.html",
  "/Black.html",
  "/Blinding-Lights.html",
  "/🔥Blister-in-the-Sun.html",
  "/Blowing-In-The-Wind.html",
  "/Bohemian-Rhapsody.html",
  "/Boys-Don't-Cry.html",
  "/Brown-Eyed-Girl.html",
  "/Budapest.html",
  "/California-Dreaming.html",
  "/Californication.html",
  "/Can't-Get-You-Out-Of-My-Head.html",
  "/Can't-Help-Falling-In-Love-With-You.html",
  "/Can't-Stop.html",
  "/Can't-Take-My-Eyes-Off-You.html",
  "/Careless-Whisper.html",
  "/Cecilia.html",
  "/Chop-Suey.html",
  "/Cold-Heart.html",
  "/🔥Colors-Of-The-Wind.html",
  "/Crazy.html",
  "/Crazy-Little-Thing-Called-Love.html",
  "/Creep.html",
  "/Dancing-Queen.html",
  "/Do-I-Wanna-Know.html",
  "/🔥Dog-Days-Are-Over.html",
  "/Don't-Let-Me-Be-Misunderstood.html",
  "/Don't-Let-Me-Down.html",
  "/Don't-Look-Back-In-Anger.html",
  "/Don't-Stop-Me-Now.html",
  "/Don't-Worry-Be-Happy.html",
  "/Dream-A-Little-Dream-Of-Me.html",
  "/Englishman-In-New-York.html",
  "/Enjoy-The-Silence.html",
  "/Every-Breath-You-Take.html",
  "/Everywhere.html",
  "/Eye-Of-The-Tiger.html",
  "/Flowers.html",
  "/Fluorescent-Adolescent.html",
  "/Fly-Away.html",
  "/Fly-Me-To-The-Moon.html",
  "/Friday-I'm-In-Love.html",
  "/Get-Lucky.html",
  "/🔥Go-Your-Own-Way.html",
  "/Hallelujah.html",
  "/Happy.html",
  "/🎂Happy-Birthday.html",
  "/Happy-Together.html",
  "/Have-You-Ever-Seen-The-Rain.html",
  "/Here-Comes-The-Sun.html",
  "/Hey-Jude.html",
  "/Hey-There-Delilah.html",
  "/Hey-Ya.html",
  "/Highway-To-Hell.html",
  "/Hit-Me-Baby-One-More-Time.html",
  "/Hit-The-Road-Jack.html",
  "/Ho-Hey.html",
  "/🔥Home.html",
  "/Hotel-California.html",
  "/House-Of-Gold.html",
  "/House-Of-The-Rising-Sun.html",
  "/How-You-Remind-Me.html",
  "/I-Heard-It-Through-The-Grapevine.html",
  "/🔥I-Knew-You-Were-Trouble.html",
  "/I-Still-Haven't-Found-What-I'm-Looking-For.html",
  "/I-Wanna-Be-Like-You-(The-Monkey-Song).html",
  "/I-Want-It-That-Way.html",
  "/I-Want-To-Break-Free.html",
  "/I-Was-Made-For-Lovin'-You.html",
  "/I-Will-Survive.html",
  "/I'll-Be-There-For-You-(Friends-Theme).html",
  "/I'm-A-Believer-(From-Shrek).html",
  "/I'm-Still-Standing.html",
  "/I'm-Yours.html",
  "/Imagine.html",
  "/In-The-Summertime.html",
  "/It's-My-Life.html",
  "/It's-Raining-Men.html",
  "/Jammin'.html",
  "/Jolene.html",
  "/🔥Just-Like-Heaven.html",
  "/Karma-Police.html",
  "/Kids.html",
  "/Killing-Me-Softly.html",
  "/Knocking-On-Heaven's-Door.html",
  "/La-Bamba.html",
  "/La-Vie-En-Rose.html",
  "/🔥Lake-Of-Fire.html",
  "/Lazy-Song,-The.html",
  "/Lemon-Tree.html",
  "/Let-Her-Go.html",
  "/Let-It-Be.html",
  "/Light-My-Fire.html",
  "/Lion-Sleeps-Tonight,-The.html",
  "/Little-Lion-Man.html",
  "/🔥Little-Talks.html",
  "/Loneliest.html",
  "/Losing-My-Religion.html",
  "/Lost-On-You.html",
  "/Love-Of-My-Life.html",
  "/Lovesong.html",
  "/Lucy-In-The-Sky-With-Diamonds.html",
  "/Mad-World.html",
  "/Mamma-Mia.html",
  "/Maria.html",
  "/Maybe-Tomorrow.html",
  "/Mr-Brightside.html",
  "/🔥Mr-Sandman.html",
  "/My-Girl.html",
  "/My-Heart-Will-Go-On-(Titanic).html",
  "/🔥Never-Gonna-Give-You-Up.html",
  "/Number-1-Party-Anthem.html",
  "/One-Love.html",
  "/Otherside.html",
  "/People-Are-Strange.html",
  "/Postcards-From-Italy.html",
  "/Psycho-Killer.html",
  "/Pumped-Up-Kicks.html",
  "/Raindrops-Keep-Fallin'-On-My-Head.html",
  "/🔥Relax,-Take-It-Easy.html",
  "/Ring-Of-Fire.html",
  "/Riptide.html",
  "/Rolling-In-The-Deep.html",
  "/Roxanne.html",
  "/Sailing.html",
  "/Save-My-Soul.html",
  "/Shake-It-Off.html",
  "/Shallow.html",
  "/🔥She-Loves-You.html",
  "/Shiny-Happy-People.html",
  "/Snow-(Hey-Oh).html",
  "/Somebody-To-Love.html",
  "/🔥Somebody-Told-Me.html",
  "/Somewhere-Over-The-Rainbow.html",
  "/Sounds-Of-Silence.html",
  "/Space-Oddity.html",
  "/Stand-By-Me.html",
  "/Stay-With-Me.html",
  "/Summer-Nights.html",
  "/Sunshine-Reggae.html",
  "/🔥Sweater-Weather.html",
  "/Sweet-Caroline.html",
  "/Sweet-Child-Of-Mine.html",
  "/Sweet-Dreams.html",
  "/Take-Me-Home-Country-Roads.html",
  "/Take-Me-Out.html",
  "/Take-On-Me.html",
  "/🔥Teenage-Dirtbag.html",
  "/Tender.html",
  "/The-Final-Countdown.html",
  "/The-Judge.html",
  "/The-Man-Who-Sold-The-World.html",
  "/The-Scientist.html",
  "/There-Is-A-Light-That-Never-Goes-Out.html",
  "/These-Boots-Are-Made-For-Walking.html",
  "/Thinking-Out-Loud.html",
  "/This-Charming-Man.html",
  "/Three-Little-Birds.html",
  "/Times-Like-These.html",
  "/🔥Titanium.html",
  "/Toxic.html",
  "/Toxicity.html",
  "/Twist-And-Shout.html",
  "/Under-Pressure.html",
  "/Use-Somebody.html",
  "/Valerie.html",
  "/Wake-Me-Up.html",
  "/🔥What-Is-Love-(Baby-Don't-Hurt-Me).html",
  "/What's-Up.html",
  "/Where-Is-My-Mind.html",
  "/Why-Don't-You-Get-A-Job.html",
  "/Wicked-Game.html",
  "/Wish-You-Were-Here.html",
  "/Wonderwall.html",
  "/Yellow.html",
  "/You-Are-My-Sunshine.html",
  "/You-Know-I'm-No-Good.html",
  "/You-Will-Never-Know.html",
  "/Zombie.html",
  "/archive/(Sittin'-on-the)-Dock-of-the-Bay.html",
  "/archive/🎅All-I-Want-For-Christmas-Is-You.html",
  "/archive/🎅Happy-Xmas.html",
  "/archive/🎅Have-Yourself-A-Merry-Little-Christmas.html",
  "/archive/🎅Jingle-Bell-Rock.html",
  "/archive/🎅Jingle-Bells.html",
  "/archive/🎅Last-Christmas.html",
  "/archive/🎅Let-It-Snow.html",
  "/archive/🎅Santa-Claus-Is-Coming-To-Town.html",
  "/archive/Stir-It-Up.html",
  "/archive/🎅White-Christmas.html",
  "/archive/You-And-I.html",
  "/chords/A.gif",
  "/chords/A7.gif",
  "/chords/A7sus4.gif",
  "/chords/Am.gif",
  "/chords/Am7.gif",
  "/chords/Am9.gif",
  "/chords/Asus4.gif",
  "/chords/B.gif",
  "/chords/B7.gif",
  "/chords/Bb.gif",
  "/chords/Bbm.gif",
  "/chords/Bbm6.gif",
  "/chords/Bbmaj7.gif",
  "/chords/Bm.gif",
  "/chords/Bm7.gif",
  "/chords/C.gif",
  "/chords/C+.gif",
  "/chords/C7.gif",
  "/chords/Cdim.gif",
  "/chords/Cm.gif",
  "/chords/Cmaj7.gif",
  "/chords/Csharpdim.gif",
  "/chords/Csharpm.gif",
  "/chords/Csus4.gif",
  "/chords/D.gif",
  "/chords/D7.gif",
  "/chords/Dm.gif",
  "/chords/Dm7.gif",
  "/chords/Dsus2.gif",
  "/chords/E.gif",
  "/chords/E7.gif",
  "/chords/Eb.gif",
  "/chords/Em.gif",
  "/chords/Em7.gif",
  "/chords/F.gif",
  "/chords/FC.gif",
  "/chords/Fm.gif",
  "/chords/Fmaj7.gif",
  "/chords/Fsharp.gif",
  "/chords/Fsharpm.gif",
  "/chords/Fsus2.gif",
  "/chords/G.gif",
  "/chords/G7.gif",
  "/chords/Gb.gif",
  "/chords/Gm.gif",
  "/chords/Gm7.gif",
  "/chords/Gmaj7.gif",
  "/chords/Gsharp.gif",
  "/chords/Gsus2.gif",
  "/chords/Gsus4.gif",
  "/chords/NC.gif"
];

// Helper: cache files in sequential batches to prevent network congestion on mobile
async function cacheInBatches(cache, urls, batchSize = 10) {
  for (let i = 0; i < urls.length; i += batchSize) {
    const batch = urls.slice(i, i + batchSize);
    await Promise.allSettled(
      batch.map(async (rawUrl) => {
        try {
          const safeUrl = encodeURI(rawUrl);
          const res = await fetch(safeUrl, { cache: 'no-cache' });
          if (res && res.status === 200) {
            await cache.put(safeUrl, res.clone());
            if (safeUrl !== rawUrl) {
              await cache.put(rawUrl, res);
            }
          }
        } catch (e) {
          // Ignore individual fetch failure
        }
      })
    );
  }
}

// Install Event: cache core assets and all songs for offline use
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      // 1. Cache essential core shell first
      await Promise.allSettled(
        CORE_ASSETS.map(async (url) => {
          try {
            const res = await fetch(url, { cache: 'no-cache' });
            if (res && res.status === 200) {
              await cache.put(url, res);
            }
          } catch (e) {
            console.warn('Could not precache core asset:', url);
          }
        })
      );

      // 2. Pre-cache all song pages and chord diagrams in batches
      await cacheInBatches(cache, ALL_SONGS_AND_CHORDS, 12);

      // Force this service worker to activate immediately once cached
      await self.skipWaiting();
    })()
  );
});

// Activate Event: remove previous version caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
      await self.clients.claim();
    })()
  );
});

// Fetch Event: handle requests with offline cache fallback
self.addEventListener('fetch', (event) => {
  const request = event.request;

  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  if (!url.protocol.startsWith('http')) return;

  // External audio/video streaming (YouTube, Spotify) cannot be cached offline
  if (
    url.hostname.includes('youtube.com') ||
    url.hostname.includes('spotify.com') ||
    url.hostname.includes('googlevideo.com')
  ) {
    return;
  }

  // HTML / Navigation requests: Network-First with Cache Fallback
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      (async () => {
        try {
          // Attempt network request first
          const networkResponse = await fetch(request);
          if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        } catch (err) {
          // Network failed (Offline): search cache thoroughly with encoding fallbacks
          const cache = await caches.open(CACHE_NAME);

          let cached = await cache.match(request, { ignoreSearch: true });
          if (!cached) {
            cached =
              (await cache.match(encodeURI(request.url), { ignoreSearch: true })) ||
              (await cache.match(decodeURI(request.url), { ignoreSearch: true }));
          }
          if (!cached) {
            const pathname = url.pathname;
            cached =
              (await cache.match(pathname, { ignoreSearch: true })) ||
              (await cache.match(decodeURI(pathname), { ignoreSearch: true })) ||
              (await cache.match(encodeURI(pathname), { ignoreSearch: true }));
          }

          if (cached) return cached;

          // If a specific song wasn't found, fallback to song list
          return (await cache.match('/songs.html')) || (await cache.match('/index.html'));
        }
      })()
    );
    return;
  }

  // Static Assets (Chords, Images, Fonts, CSS): Cache-First with Network Fallback
  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE_NAME);

      let cachedResponse = await cache.match(request, { ignoreSearch: true });
      if (!cachedResponse) {
        const pathname = url.pathname;
        cachedResponse =
          (await cache.match(pathname, { ignoreSearch: true })) ||
          (await cache.match(decodeURI(pathname), { ignoreSearch: true })) ||
          (await cache.match(encodeURI(pathname), { ignoreSearch: true }));
      }

      if (cachedResponse) {
        return cachedResponse;
      }

      try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
          cache.put(request, networkResponse.clone());
        }
        return networkResponse;
      } catch (err) {
        // Silently fail for optional external assets if offline
      }
    })()
  );
});