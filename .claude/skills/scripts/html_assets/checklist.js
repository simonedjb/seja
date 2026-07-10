// checklist.js — checkbox state persistence via localStorage, progress tracking
(function () {
  "use strict";

  var STORAGE_PREFIX = document.body.getAttribute("data-checklist-prefix") || "seja-onboard";

  function storageKey(sectionId, index) {
    return STORAGE_PREFIX + ":" + sectionId + ":" + index;
  }

  function updateSectionProgress(section) {
    var boxes = section.querySelectorAll("input[type='checkbox']");
    var checked = 0;
    boxes.forEach(function (cb) { if (cb.checked) checked++; });
    var total = boxes.length;

    var label = section.querySelector(".checklist-section-progress");
    if (label) {
      label.textContent = checked + " / " + total;
    }
    return { checked: checked, total: total };
  }

  function updateGlobalProgress() {
    var sections = document.querySelectorAll(".checklist-section");
    var totalChecked = 0;
    var totalItems = 0;

    sections.forEach(function (section) {
      var result = updateSectionProgress(section);
      totalChecked += result.checked;
      totalItems += result.total;
    });

    var bar = document.querySelector(".progress-bar-inner");
    var label = document.querySelector(".progress-label");

    if (totalItems > 0) {
      var pct = Math.round((totalChecked / totalItems) * 100);
      if (bar) bar.style.width = pct + "%";
      if (label) label.textContent = totalChecked + " of " + totalItems + " complete (" + pct + "%)";
    }
  }

  function initChecklists() {
    var sections = document.querySelectorAll(".checklist-section");

    sections.forEach(function (section) {
      var sectionId = section.getAttribute("data-checklist-id") || "default";
      var items = section.querySelectorAll(".checklist-item");

      items.forEach(function (item, index) {
        var cb = item.querySelector("input[type='checkbox']");
        var label = item.querySelector("label");
        if (!cb) return;

        // Restore state
        var saved = localStorage.getItem(storageKey(sectionId, index));
        if (saved === "true") {
          cb.checked = true;
          item.classList.add("checked");
        }

        // Save on change
        cb.addEventListener("change", function () {
          localStorage.setItem(storageKey(sectionId, index), cb.checked ? "true" : "false");
          item.classList.toggle("checked", cb.checked);
          updateGlobalProgress();
        });

        // Click label to toggle
        if (label) {
          label.addEventListener("click", function (e) {
            if (e.target.tagName !== "INPUT") {
              cb.checked = !cb.checked;
              cb.dispatchEvent(new Event("change"));
            }
          });
        }
      });
    });

    updateGlobalProgress();
  }

  document.addEventListener("DOMContentLoaded", initChecklists);
})();
