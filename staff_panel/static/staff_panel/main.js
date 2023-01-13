var select = document.getElementById("filterableSelect");
var oldOptions = Array.apply(undefined, select.options); // копируем все OPTION. По ним будем искать

document.getElementById('selectFilter').onkeyup = function(e) {
  // спец. сочетания пропускаем
  if (e.ctrlKey || e.altKey || e.metaKey) return;

  select.options.length = 0;
  var regexp = new RegExp(this.value, "ig");
  for (var i = 0; i < oldOptions.length; i++) {
    if (oldOptions[i].innerText.search(regexp) >= 0) {
      select.appendChild(oldOptions[i]);
    }
  }
};