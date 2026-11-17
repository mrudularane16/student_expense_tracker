document.addEventListener("DOMContentLoaded", function () {
  var radios = document.querySelectorAll('input[name="type"]');
  var categoryWrap = document.getElementById("category-wrap");
  var category = document.getElementById("category");
  var submitBtn = document.getElementById("submit-btn");
  var editing = submitBtn.dataset.editing === "true";

  function sync() {
    var type = document.querySelector('input[name="type"]:checked').value;
    var isExpense = type === "expense";
    categoryWrap.classList.toggle("hidden", !isExpense);
    category.required = isExpense;
    submitBtn.textContent = (editing ? "Update " : "Save ") + type;
  }

  radios.forEach(function (r) { r.addEventListener("change", sync); });
  sync();
});