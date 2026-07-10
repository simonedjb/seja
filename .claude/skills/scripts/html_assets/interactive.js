// interactive.js — collapsible toggles, ToC scroll highlighting
(function () {
  "use strict";

  // ToC active-link highlighting on scroll
  function initTocHighlight() {
    var tocLinks = document.querySelectorAll(".toc-sidebar a");
    if (!tocLinks.length) return;

    var headings = [];
    tocLinks.forEach(function (link) {
      var id = link.getAttribute("href");
      if (id && id.startsWith("#")) {
        var el = document.getElementById(id.substring(1));
        if (el) headings.push({ el: el, link: link });
      }
    });

    if (!headings.length) return;

    function onScroll() {
      var scrollY = window.scrollY + 80;
      var current = headings[0];
      for (var i = 0; i < headings.length; i++) {
        if (headings[i].el.offsetTop <= scrollY) {
          current = headings[i];
        }
      }
      tocLinks.forEach(function (l) { l.classList.remove("active"); });
      if (current) current.link.classList.add("active");
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Smooth scroll for ToC links
  function initSmoothScroll() {
    document.querySelectorAll(".toc-sidebar a").forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = this.getAttribute("href");
        if (id && id.startsWith("#")) {
          var target = document.getElementById(id.substring(1));
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", id);
          }
        }
      });
    });
  }

  // Collapsible sections — ensure details/summary work even in older browsers
  function initCollapsibles() {
    document.querySelectorAll("details > summary").forEach(function (summary) {
      summary.addEventListener("click", function (e) {
        var details = this.parentElement;
        if (!("open" in document.createElement("details"))) {
          e.preventDefault();
          details.toggleAttribute("open");
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTocHighlight();
    initSmoothScroll();
    initCollapsibles();
  });
})();
