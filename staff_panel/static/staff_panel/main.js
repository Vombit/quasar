var select = document.getElementById("filterableSelect");
var oldOptions = Array.apply(undefined, select.options); // копируем все OPTION. По ним будем искать
let csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
let content_body = document.getElementById('content_body')

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

let sendSearch = (data) => {
  content_body.innerHTML = "";
  $.ajax({
      type:'POST',
      url:'/get_info',
      data: {
          'csrfmiddlewaretoken':csrf,
          'data':data,
      },
      success: (res) => {
        content_body.innerHTML = res;
      },
      error: (err) => {
          return
      }
  })
}


select.addEventListener('change', function (e) {
  console.log("Changed to: " + e.target.value)

  sendSearch(e.target.value)


})