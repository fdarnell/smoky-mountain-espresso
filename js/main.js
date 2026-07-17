// Smoky Mountain Espresso — shared script: nav toggle, click-to-load map, form UX.
(function () {
  "use strict";

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("open") && !nav.contains(e.target)) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Click-to-load Google map (keeps ~1MB of map scripts off initial load)
  var mapBtn = document.getElementById("map-load");
  if (mapBtn) {
    mapBtn.addEventListener("click", function () {
      var shell = document.getElementById("map-shell");
      var iframe = document.createElement("iframe");
      iframe.src = mapBtn.getAttribute("data-map-src");
      iframe.title = "Map to Smoky Mountain Espresso, 1259 Middle Creek Rd, Sevierville TN";
      iframe.setAttribute("loading", "lazy");
      iframe.setAttribute("allowfullscreen", "");
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      shell.textContent = "";
      shell.appendChild(iframe);
    });
  }

  // Contact form: posts to the endpoint in data-endpoint (Formspree).
  // Until a real endpoint is configured, fails safe with a call-us message
  // instead of silently dropping the submission.
  var form = document.getElementById("contact-form");
  if (form) {
    var status = document.getElementById("form-status");
    var endpoint = form.getAttribute("data-endpoint");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!endpoint || endpoint.indexOf("TODO") !== -1) {
        status.textContent =
          "Online messages aren't set up yet - please call (865) 366-1685 or message us on Facebook.";
        return;
      }
      var data = new FormData(form);
      status.textContent = "Sending...";
      fetch(endpoint, {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" },
      })
        .then(function (res) {
          if (res.ok) {
            form.reset();
            status.textContent = "Got it - thanks! We'll get back to you soon.";
          } else {
            throw new Error("bad status");
          }
        })
        .catch(function () {
          status.textContent =
            "Something went wrong sending that - please call (865) 366-1685 instead.";
        });
    });
  }
})();
