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

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
