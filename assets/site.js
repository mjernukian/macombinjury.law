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
    var q = "I was hurt in a crash in Macomb County, Michigan and I have been reading about Michael Jernukian, the car accident trial attorney at Morgan & Morgan. Before I call anyone, what actually happens on a free consultation, am I committing to anything just by calling, and how do contingency fees work if my case does not work out? Do most injury cases settle or go to trial, roughly how long do they take, and what Michigan deadlines should I know about right now?";
    document.querySelectorAll('.askai-row a').forEach(function (a) {
      try { var u = new URL(a.href); u.searchParams.set('q', q); a.href = u.toString(); } catch (e) {}
    });
    var h = document.querySelector('.askai-h'), t = document.querySelector('.askai-t');
    if (h) h.textContent = 'Still deciding?';
    if (t) t.textContent = 'Ask an AI what a free consultation actually involves, and what you would be committing to:';
  })();

  // "Do I have a case?" guided intake: buttons only, no free text until the
  // optional phone number. Only a submitted phone number is sent anywhere.
  (function intake() {
    var box = document.getElementById('intake');
    if (!box) return;
    var PHONE = '(313) 540-8512', TEL = 'tel:+13135408512';
    var steps = [
      { k: 'what', q: 'What happened?', o: [['Car crash', 'car'], ['Truck crash', 'truck'], ['Motorcycle crash', 'motorcycle'], ['I was a pedestrian', 'pedestrian'], ['Something else', 'other']] },
      { k: 'you', q: 'Did you have auto insurance at the time?', o: [['Yes', 'insured'], ['No', 'uninsured'], ['Not sure', 'unsure']] },
      { k: 'them', q: 'Did the other driver have insurance?', o: [['Yes', 'insured'], ['No', 'none'], ["I don't know yet", 'unknown']] },
      { k: 'when', q: 'When did it happen?', o: [['Within the last year', 'under1yr'], ['1 to 3 years ago', '1to3'], ['More than 3 years ago', 'over3']] }
    ];
    var R = {
      under1yr: "On timing, you are likely still inside the deadlines, but Michigan's one-year no-fault deadlines run out faster than most people expect. Don't sit on it.",
      '1to3': 'Some one-year deadlines may already be gone, but the main claim against the at-fault driver generally has three years. It is worth moving now.',
      over3: 'More than three years is a real problem for some claims, though not always all of them. It costs nothing to have the dates checked properly.',
      uninsured: "You may have been told that being uninsured ends your case. It doesn't always. Some claims can survive, and it is worth having Michael look at yours.",
      unsure: "If it turns out you were uninsured, don't assume that ends things. Some claims can survive.",
      them: 'When the at-fault driver has no insurance, or nobody knows yet, Michigan has options most people never hear about, including your own coverage and the Michigan Assigned Claims Plan.',
      truck: 'Truck cases can involve the driver, the trucking company and federal safety rules. The evidence needs to be preserved early.',
      motorcycle: 'Riders get blamed. A motorcycle case needs to be built to answer that from the start.',
      close: 'This is general information, not legal advice, and every case turns on its facts. The fastest way to a real answer is to have Michael look at it. Free, and no pressure.'
    };
    var st = {}, label = {}, i = 0;
    function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function head(pct, step) {
      return '<div class="ihead"><span class="ititle">Do I have a case?</span>' + (step ? '<span class="istep">' + step + ' / 4</span>' : '') + '</div>' +
        '<div class="ibar"><i style="width:' + pct + '%"></i></div>';
    }
    function focusFirst(sel) { var el = box.querySelector(sel); if (el && box.dataset.started) el.focus({ preventScroll: true }); }
    function render() {
      if (i >= steps.length) return result();
      var s = steps[i];
      box.innerHTML = head(i * 25, i + 1) + '<p class="itag">Free &middot; 30 seconds &middot; no personal information needed</p>' +
        '<div class="iq">' + s.q + '</div><div class="iopts">' +
        s.o.map(function (o, j) { return '<button type="button" class="iopt" data-j="' + j + '">' + esc(o[0]) + '</button>'; }).join('') + '</div>' +
        (i > 0 ? '<button type="button" class="iback">&larr; Back</button>' : '');
      box.querySelectorAll('.iopt').forEach(function (b) {
        b.addEventListener('click', function () {
          var o = s.o[+b.dataset.j]; st[s.k] = o[1]; label[s.k] = o[0]; i++; box.dataset.started = '1'; render();
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
      box.innerHTML = head(100) + '<div class="iq">Here&rsquo;s what matters in your situation.</div>' +
        '<div class="ires">' + L.map(function (l) { return '<p>' + l + '</p>'; }).join('') + '<p>' + R.close + '</p></div>' +
        '<form class="iform" novalidate><label class="skip" for="ip">Your phone number</label>' +
        '<input id="ip" type="tel" name="phone" placeholder="Your phone number" autocomplete="tel" inputmode="tel" required>' +
        '<button class="btn btn-brass" type="submit">Have Michael take a look</button></form>' +
        '<p class="ialt">Or call Michael now at <a href="' + TEL + '">' + PHONE + '</a>.</p>' +
        '<button type="button" class="iback">Start over</button>';
      var form = box.querySelector('.iform');
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var inp = form.querySelector('input'), phone = inp.value.trim();
        var old = form.parentNode.querySelector('.ierr'); if (old) old.remove();
        if (phone.replace(/\D/g, '').length < 10) {
          form.insertAdjacentHTML('afterend', '<p class="ierr">Please enter a phone number with area code.</p>'); inp.focus(); return;
        }
        var btn = form.querySelector('button'); btn.disabled = true;
        var detail = [label.what, 'caller insured: ' + label.you, 'other driver insured: ' + label.them, 'when: ' + label.when].join(' | ');
        fetch('/', {
          method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ 'form-name': 'case-check', 'bot-field': '', phone: phone, detail: detail, type: 'Do I have a case? lead', page: location.pathname }).toString()
        }).then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.outerHTML = '<p class="idone">Got it. Michael will reach out.</p>';
        }).catch(function () {
          btn.disabled = false;
          form.insertAdjacentHTML('afterend', '<p class="ierr">That didn&rsquo;t go through. Please call Michael at <a href="' + TEL + '">' + PHONE + '</a>.</p>');
        });
      });
      box.querySelector('.iback').addEventListener('click', function () { i = 0; st = {}; label = {}; render(); });
      focusFirst('.iopt, input');
    }
    render();
  })();

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
