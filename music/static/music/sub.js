$(".menu_dropdown_profile").click(function(){
    $(".head_profile_sub").toggleClass("hidden");
});
$(document).mouseup(function (e) {
    if ($(".menu_dropdown_profile").has(e.target).length === 0){    
        $(".head_profile_sub").addClass("hidden");
    }
})
let sendSearch = (data) => {
    result_box.innerHTML = "";
    $.ajax({
        type:'POST',
        url:'/search',
        data: {
            'csrfmiddlewaretoken':csrf,
            'data':data,
        },
        success: (res) => {
            var authors = res.message.authors
            var albums = res.message.albums
            var tracks = res.message.tracks
            result_box.innerHTML = "";
            if (authors.length > 0) {
                result_box.innerHTML += `<div>Авторы</div>`
                authors.forEach(authors => {
                    result_box.innerHTML += `
                        <a href="/artist/${authors.url}" class="search_block link block author" title="${authors.name}"> 
                            <figure>
                                <img src="/media/${authors.image}" onerror="imgError(this);">
                                <figcaption>${authors.name}</figcaption>
                            </figure>
                        </a>`
                });
            }
            if (albums.length > 0) {
                result_box.innerHTML += `<div>Альбомы</div>`
                albums.forEach(albums => {
                    result_box.innerHTML += `
                        <a href="/album/${albums.url}" class="search_block link block album" title="${albums.name}"> 
                            <figure>
                                <img src="/media/${albums.image}" onerror="imgError(this);">
                                <figcaption>${albums.name}</figcaption>
                            </figure>
                        </a>`
                });
            }
            if (tracks.length > 0) {
                result_box.innerHTML += `<div>Музыка</div>`
                tracks.forEach(tracks => {
                    result_box.innerHTML += `
                        <a href="/album/${tracks.url}" class="search_block link block search_track">
                            <img src="/media/${tracks.image}" onerror="imgError(this);">
                            <div>${tracks.author} – ${tracks.name}</div>
                        </a>`
                });
            }
        },
        error: (err) => {
            return
        }
    })
}
let search_input = document.getElementById('search_input')
let result_box = document.getElementById('result_box')
let csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
search_input.addEventListener('keyup', e=>{
    sendSearch(e.target.value)
});
$("#search_form").focusin(function() {
    result_box.classList.remove('hidden');
});
$("#search_form").focusout(function() {
    setTimeout(function () {
        result_box.classList.add('hidden');
    }, 500);
});