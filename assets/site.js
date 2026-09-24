// macombinjury.law — header shadow on scroll, scroll reveals, footer year.
(function () {
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  var items = document.querySelectorAll('.rv');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  // Page text for the interactive pieces. English is the default; the /es/
  // and /ar/ pages set window.MJ_I18N with the same keys to translate them.
  var EN = {
    lang: 'en',
    aiQ2: "I was hurt in a crash in Macomb County, Michigan and I have been reading about Michael Jernukian, the car accident trial attorney at Morgan & Morgan. Before I call anyone, what actually happens on a free consultation, am I committing to anything just by calling, and how do contingency fees work if my case does not work out? Do most injury cases settle or go to trial, roughly how long do they take, and what Michigan deadlines should I know about right now?",
    aiH2: 'Still deciding?',
    aiT2: 'Ask an AI what a free consultation actually involves, and what you would be committing to:',
    title: 'Do I have a case?',
    tag: 'Free &middot; 30 seconds &middot; no personal information needed',
    back: '&larr; Back',
    steps: [
      { q: 'What happened?', o: ['Car crash', 'Truck crash', 'Motorcycle crash', 'I was a pedestrian', 'Something else'] },
      { q: 'Did you have auto insurance at the time?', o: ['Yes', 'No', 'Not sure'] },
      { q: 'Did the other driver have insurance?', o: ['Yes', 'No', "I don't know yet"] },
      { q: 'When did it happen?', o: ['Within the last year', '1 to 3 years ago', 'More than 3 years ago'] }
    ],
    R: {
      under1yr: "On timing, you are likely still inside the deadlines, but Michigan's one-year no-fault deadlines run out faster than most people expect. Don't sit on it.",
      '1to3': 'Some one-year deadlines may already be gone, but the main claim against the at-fault driver generally has three years. It is worth moving now.',
      over3: 'More than three years is a real problem for some claims, though not always all of them. It costs nothing to have the dates checked properly.',
      uninsured: "You may have been told that being uninsured ends your case. It doesn't always. Some claims can survive, and it is worth having Michael look at yours.",
      unsure: "If it turns out you were uninsured, don't assume that ends things. Some claims can survive.",
      them: 'When the at-fault driver has no insurance, or nobody knows yet, Michigan has options most people never hear about, including your own coverage and the Michigan Assigned Claims Plan.',
      truck: 'Truck cases can involve the driver, the trucking company and federal safety rules. The evidence needs to be preserved early.',
      motorcycle: 'Riders get blamed. A motorcycle case needs to be built to answer that from the start.',
      close: 'This is general information, not legal advice, and every case turns on its facts. The fastest way to a real answer is to have Michael look at it. Free, and no pressure.'
    },
    rhead: 'Here&rsquo;s what matters in your situation.',
    ph: 'Your phone number',
    send: 'Have Michael take a look',
    alt: 'Or call now at {PHONE} and ask for MJ.',
    bad: 'Please enter a phone number with area code.',
    done: 'Got it. Michael will reach out.',
    fail: 'That didn&rsquo;t go through. Please call {PHONE} and ask for MJ.',
    restart: 'Start over'
  };
  var T = window.MJ_I18N || EN;
  function t(k) { return T[k] != null ? T[k] : EN[k]; }

  // Returning visitors already know who Michael is, so the Ask-an-AI box
  // switches to the question they have now. The visible label changes with it.
  (function askaiReturning() {
    var n = 0;
    try {
      if (!sessionStorage.getItem('mj_seen')) {
        n = (parseInt(localStorage.getItem('mj_visits') || '0', 10) || 0) + 1;
        localStorage.setItem('mj_visits', String(n));
        sessionStorage.setItem('mj_seen', '1');
      } else {
        n = parseInt(localStorage.getItem('mj_visits') || '1', 10) || 1;
      }
    } catch (e) { return; }
    if (n < 2) return;
    var q = t('aiQ2');
    document.querySelectorAll('.askai-row a').forEach(function (a) {
      try { var u = new URL(a.href); u.searchParams.set('q', q); a.href = u.toString(); } catch (e) {}
    });
    var h = document.querySelector('.askai-h'), p = document.querySelector('.askai-t');
    if (h) h.textContent = t('aiH2');
    if (p) p.textContent = t('aiT2');
  })();

  // "Do I have a case?" guided intake: buttons only, no free text until the
  // optional phone number. Only a submitted phone number is sent anywhere.
  // Leads always reach Michael in English, tagged with the page language.
  (function intake() {
    var box = document.getElementById('intake');
    if (!box) return;
    var TEL = 'tel:+13135408512';
    var PHONE = '<a href="' + TEL + '"><bdi dir="ltr">(313) 540-8512</bdi></a>';
    var KEYS = ['what', 'you', 'them', 'when'];
    var VALUES = [
      ['car', 'truck', 'motorcycle', 'pedestrian', 'other'],
      ['insured', 'uninsured', 'unsure'],
      ['insured', 'none', 'unknown'],
      ['under1yr', '1to3', 'over3']
    ];
    var steps = t('steps'), R = t('R');
    var st = {}, pick = {}, i = 0;
    function esc(x) { return String(x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function fill(x) { return x.replace('{PHONE}', PHONE); }
    function head(pct, step) {
      return '<div class="ihead"><span class="ititle">' + t('title') + '</span>' + (step ? '<span class="istep"><bdi dir="ltr">' + step + ' / 4</bdi></span>' : '') + '</div>' +
        '<div class="ibar"><i style="width:' + pct + '%"></i></div>';
    }
    function focusFirst(sel) { var el = box.querySelector(sel); if (el && box.dataset.started) el.focus({ preventScroll: true }); }
    function render() {
      if (i >= KEYS.length) return result();
      var s = steps[i];
      box.innerHTML = head(i * 25, i + 1) + '<p class="itag">' + t('tag') + '</p>' +
        '<div class="iq">' + s.q + '</div><div class="iopts">' +
        s.o.map(function (o, j) { return '<button type="button" class="iopt" data-j="' + j + '">' + esc(o) + '</button>'; }).join('') + '</div>' +
        (i > 0 ? '<button type="button" class="iback">' + t('back') + '</button>' : '');
      box.querySelectorAll('.iopt').forEach(function (b) {
        b.addEventListener('click', function () {
          var j = +b.dataset.j; st[KEYS[i]] = VALUES[i][j]; pick[KEYS[i]] = j; i++; box.dataset.started = '1'; render();
        });
      });
      var bk = box.querySelector('.iback'); if (bk) bk.addEventListener('click', function () { i--; render(); });
      focusFirst('.iopt');
    }
    function result() {
      var L = [];
      L.push(R[st.when]);
      if (st.you === 'uninsured') L.push(R.uninsured); else if (st.you === 'unsure') L.push(R.unsure);
      if (st.them === 'none' || st.them === 'unknown') L.push(R.them);
      if (st.what === 'truck') L.push(R.truck);
      if (st.what === 'motorcycle') L.push(R.motorcycle);
      box.innerHTML = head(100) + '<div class="iq">' + t('rhead') + '</div>' +
        '<div class="ires">' + L.map(function (l) { return '<p>' + l + '</p>'; }).join('') + '<p>' + R.close + '</p></div>' +
        '<form class="iform" novalidate><label class="skip" for="ip">' + t('ph') + '</label>' +
        '<input id="ip" type="tel" name="phone" dir="ltr" placeholder="' + t('ph') + '" autocomplete="tel" inputmode="tel" required>' +
        '<button class="btn btn-brass" type="submit">' + t('send') + '</button></form>' +
        '<p class="ialt">' + fill(t('alt')) + '</p>' +
        '<button type="button" class="iback">' + t('restart') + '</button>';
      var form = box.querySelector('.iform');
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var inp = form.querySelector('input'), phone = inp.value.trim();
        var old = form.parentNode.querySelector('.ierr'); if (old) old.remove();
        if (phone.replace(/\D/g, '').length < 10) {
          form.insertAdjacentHTML('afterend', '<p class="ierr">' + t('bad') + '</p>'); inp.focus(); return;
        }
        var btn = form.querySelector('button'); btn.disabled = true;
        var en = function (k, n) { return EN.steps[n].o[pick[k]]; };
        var lang = { en: 'English', es: 'Spanish', ar: 'Arabic' }[t('lang')] || t('lang');
        var detail = [en('what', 0), 'caller insured: ' + en('you', 1), 'other driver insured: ' + en('them', 2), 'when: ' + en('when', 3), 'site language: ' + lang].join(' | ');
        fetch('/', {
          method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ 'form-name': 'case-check', 'bot-field': '', phone: phone, detail: detail, type: 'Do I have a case? lead (' + lang + ')', page: location.pathname }).toString()
        }).then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.outerHTML = '<p class="idone">' + t('done') + '</p>';
        }).catch(function () {
          btn.disabled = false;
          form.insertAdjacentHTML('afterend', '<p class="ierr">' + fill(t('fail')) + '</p>');
        });
      });
      box.querySelector('.iback').addEventListener('click', function () { i = 0; st = {}; pick = {}; render(); });
      focusFirst('.iopt, input');
    }
    render();
  })();

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
