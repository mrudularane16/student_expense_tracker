(function () {
  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function refresh() {
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.setAttribute("aria-pressed", current() === "dark" ? "true" : "false");
    });
  }

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
    refresh();
  }

  document.addEventListener("DOMContentLoaded", function () {
    refresh();
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setTheme(current() === "dark" ? "light" : "dark");
      });
    });
  });
})();