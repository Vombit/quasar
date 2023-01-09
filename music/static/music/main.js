var fac = new FastAverageColor();
var base_image = new Image();

var like_btn = document.querySelector('.btn.liked svg')
var shuffle_btn = document.querySelector('.btn.shuffle svg')
var repeat_btn = document.querySelector('.btn.repeat svg')

var volume_line = $("#volume_container")[0];

var visual_block = document.querySelector(".visual");
var canvas = document.getElementById("canvas_visual");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var centerX = canvas.width / 2;
var centerY = canvas.height / 2;

var spline = canvas.getContext("2d");
var source, frequencyArray;
var canvas_color;

let vol = 0.2;
var songIndex = 0;

let player = document.querySelector('.Controls'),
    playBtn = document.querySelector('.play'),
    prevBtn = document.querySelector('.prev'),
    nextBtn = document.querySelector('.next'),
    progressContainer = document.querySelector('.progress_container'),
    progress = document.querySelector('.progress'),
    imgSrc = document.querySelector('.img_src'),
    title = document.querySelector('.cover_name'),
    author = document.querySelector('.cover_author'),
    cover = document.querySelector('.cover_img'),
    cover_time = document.querySelector('.cover_time'),
    cover_current_time = document.querySelector('.cover_current_time'),
    track_name = document.querySelector(".visual_track_name"),
    track_author = document.querySelector(".visual_track_author");


var array_fav_tracks = {};
function get_fav_tracks() {
    $.get("/music/get_favorite")
        .done(function( data ) {
            array_fav_tracks = data.message.array_tracks_id

            document.querySelectorAll('.tracks_array .track .favorite').forEach(function(e) {
                var has_track = array_fav_tracks.includes(e.id);
                if (has_track) {
                    e.querySelector('svg').classList.add("liked");
                }
            });
        });
}
function favTrack(e, track) {
    elem = e.querySelector('svg')
    if ($(elem).hasClass("liked")) {
        $.get(`/application/manage/${track}&remove`)
            .done(function() {
                $(elem).removeClass('liked')
                get_fav_tracks()
            });
    } else {
        $.get(`/application/manage/${track}&add`)
            .done(function() {
                $(elem).addClass('liked')
                get_fav_tracks()
            });
    }
}
function panel_like_track() {
    if ($(like_btn).hasClass("liked")) {
        $.get(`/application/manage/${array_tracks[songIndex].id}&remove`)
            .done(function() {
                $(like_btn).removeClass('liked')
                get_fav_tracks()
            })
    } else {
        $.get(`/application/manage/${array_tracks[songIndex].id}&add`)
            .done(function() {
                $(like_btn).addClass('liked')
                get_fav_tracks()
            })
    }
}
function header_color_set() {
    var bck_img = document.querySelector('.content_info_block img');
    var colorize = document.querySelector('.content_header');
    var img = new Image();
        img.src = $(bck_img).attr('src');
    img.onload = function() {
        colorize.style.backgroundColor = fac.getColor((bck_img),{ignoredColor:[0, 0, 0, 0]}).hex;
    };
}
function shuffle(trck_array){
    for (var i = 0; i < trck_array.length - 1; i++) {
        var j = i + Math.floor(Math.random() * (trck_array.length - i));
        var temp = trck_array[j];
        trck_array[j] = trck_array[i];
        trck_array[i] = temp;
    }
    return trck_array;
}
function trackTime(time) {
    var seconds = time % 60;
    var foo = time - seconds;
    var minutes = foo / 60;
    var dur = minutes + ":" + Math.floor(seconds);
    if(seconds < 10){
        dur = minutes + ":0" + Math.floor(seconds);
    }
    return  dur
}
$(document).on('click', 'a.link', function () {
    var url = $(this).attr('href');
    $.post(url, {csrfmiddlewaretoken: csrf})
        .done(function(data) {
            $("div#main_page_elements").html(data);
            window.history.pushState({route: url}, "EVILEG", url);
            header_color_set();
            get_fav_tracks();
        });
    return false;
});
// update volume sound if change on server
$("#volume_container").mouseup(function() {
    updateData()
});
// like button on panel
like_btn.addEventListener('click', () => {
    panel_like_track()
})
// shuffle button on panel
shuffle_btn.addEventListener('click', () => {
    let next_track = songIndex+1;
    let prev_track = songIndex-1;
    if ($(shuffle_btn).hasClass("btn_shuffled")) {
        $(shuffle_btn).removeClass('btn_shuffled')
    } else {
        array_tracks = shuffle(array_tracks)
        $(shuffle_btn).addClass('btn_shuffled')
        $(".prev_track .queue_title").text(array_tracks.at([prev_track]).name);
        if (songIndex >= array_tracks.length-1 ) {
            $(".next_track .queue_title").text(array_tracks[0].name);
        } else {
            $(".next_track .queue_title").text(array_tracks[next_track].name);
        }
    }
})
// repeat button on panel
repeat_btn.addEventListener('click', () => {
    if ($(repeat_btn).hasClass("btn_active")) {
        $(repeat_btn).removeClass('btn_active');
        // audio.loop = false;
    } else {
        $(repeat_btn).addClass('btn_active');
        // audio.loop = true;
    }
})
// hot-keys
document.addEventListener("keydown", e => {
    var height = $("#volume_container").height();
    var activeElement = document.activeElement;
    var inputs = ['input', 'select', 'button', 'textarea'];

    if (activeElement && inputs.indexOf(activeElement.tagName.toLowerCase()) == -1) {
        try {
            // e.preventDefault() //unbind default
            if (e.keyCode == 32) { // SPACE
                if (mySMSound.paused || !mySMSound.playState) {
                    playSong();
                } else {
                    pauseSong();
                }
            } else if (e.keyCode == 74) { // J
                nextSong();
            } else if (e.keyCode == 70) { // F
                prevSong();
            } else if (e.keyCode == 39) { // RIGHT
                mySMSound.setPosition(mySMSound.position+5000);
            } else if (e.keyCode == 37) { // LEFT
                mySMSound.setPosition(mySMSound.position-5000);
            } else if (e.keyCode == 40) { // DOWN
                mySMSound.setVolume(mySMSound.volume - 0.5);
                volumes = mySMSound.volume/100
                if (mySMSound.volume <= 0.6) mySMSound.setVolume(0); volumes = mySMSound.volume/100
                $("#volume_variable").height(height / vol * mySMSound.volume/100);
            } else if (e.keyCode == 38) { // UP
                mySMSound.setVolume(mySMSound.volume + 0.5);
                volumes = mySMSound.volume/100
                if (mySMSound.volume >= vol*100) mySMSound.setVolume(vol*100); volumes = mySMSound.volume/100
                $("#volume_variable").height(height / vol * mySMSound.volume/100);
            } else if (e.keyCode == 80) { // P
                visual_block.style.display = "block";
                if (!source) equalizer()
            }
        } catch {
            return;
        }
    }
});
// resize window
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    centerX = canvas.width / 2;
    centerY = canvas.height / 2;
    base_image.src = base_image.src
})
function equalizer() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    var audioElement = soundManager.sounds[soundManager.soundIDs[0]]._a;

    context = new AudioContext();
    analyser = context.createAnalyser();

    source = context.createMediaElementSource(audioElement);
    source.connect(analyser);
    analyser.connect(context.destination);
    frequencyArray = new Uint8Array(analyser.frequencyBinCount);

    canvas_color = fac.getColor(cover);
    var radius = 139;
    var sticks = 124;
    var sticksWidth = 3;

    base_image.src = $(cover).attr('src');
    base_image.onload = function() {    
        spline.imageSmoothingQuality = "high"; 
        spline.drawImage(base_image, centerX-128, centerY-128, 256, 256);
    };
    equalizer_anim()
    function equalizer_anim() {
        var chunk_time = mySMSound.position / mySMSound.duration;

        spline.beginPath();
        spline.arc(centerX, centerY, radius*2, 0, 2 * Math.PI);
        spline.lineWidth = 300.5;
        spline.strokeStyle = '#000';
        spline.stroke();

        spline.beginPath();
        spline.arc(centerX, centerY, radius, 1.5 * Math.PI, (Math.PI * (2 * chunk_time))+(1.5 * Math.PI));
        spline.lineWidth = 6;
        spline.strokeStyle = canvas_color.rgb;
        spline.stroke();
        analyser.getByteFrequencyData(frequencyArray);
        for (let i = 0; i <= sticks; i++) {
            frequency_lines(1, i)
            frequency_lines(0, i)
        }
        requestAnimationFrame(equalizer_anim);
    }

    function frequency_lines(positive, i) {
        if (positive != 1) positive = -1;
        rads = positive * Math.PI / sticks;
        var barHeight = frequencyArray[i] * 0.6;
        var x = centerX + Math.cos(rads * i - Math.PI/2) * (radius+10);
        var y = centerY + Math.sin(rads * i - Math.PI/2) * (radius+10);
        var xEnd = centerX + Math.cos(rads * i - Math.PI/2) * ((radius+11) + barHeight);
        var yEnd = centerY + Math.sin(rads * i - Math.PI/2) * ((radius+11) + barHeight);
        draw_lines(x, y, xEnd, yEnd, sticksWidth, frequencyArray[i]);
    }
    function draw_lines(x1, y1, x2, y2, width, frequency) {
        var lineColor = `rgb(${(canvas_color.value[0] + frequency+48)/2}, ${canvas_color.value[1]+24}, ${canvas_color.value[2]+24})`;
        spline.strokeStyle = lineColor;
        spline.lineWidth = width;
        spline.beginPath();
        spline.moveTo(x1, y1);
        spline.lineTo(x2, y2);
        spline.stroke();
    }
}
canvas.addEventListener('click', () => {
    visual_block.style.display = "none";
})
document.querySelector('.cover_img').addEventListener('click', () => {
    visual_block.style.display = "block";
    if (!source) equalizer()
})

$(".btn.sound").click(function(){
    $(".volume_container").toggleClass("hidden");
});
$("#volume_container").mouseup(function(e) {
    let height = $(this).height();
    let clickY = e.offsetY;
    let volum = (height-clickY)/height
    if (volum < 0.05) {
        volum = 0;
        clickY = height;
    } else if(volum > 0.95){
        volum = 1;
        clickY = 0;
    }
    mySMSound.setVolume(volum*vol*100);
    volumes = mySMSound.volume/100
    $("#volume_variable").height(height-clickY);
});


$(document).ready(function() {
    get_fav_tracks();
    header_color_set();
    loadData();
    setInterval(function() {if(!mySMSound.paused && mySMSound.playState) updateData();}, 10000);
})





function imgError(image) {
    image.src = "/static/music/images/empty.png";
    return true;
}



function updateData() {
    var data = {
        'track': array_tracks[songIndex].id,
        'curtime': mySMSound.position/1000,
        'curvolume': mySMSound.volume/100
    }
    $.post('/datacloud/', { 'csrfmiddlewaretoken':csrf, data });
}






var array_tracks;
var songIndex = 0;
var canvas_color;
var mySMSound;


function pauseSong() {
    player.classList.remove('play')
    $('.icon.play').removeClass('hidden');
    $('.icon.pause').addClass('hidden');

    soundManager.pause('track_main');
}
function nextSong() {
    songIndex++
    if (songIndex > array_tracks.length -1 ) {songIndex = 0}
    loadSong(array_tracks[songIndex])
    playSong()
}
nextBtn.addEventListener('click', nextSong)

function prevSong() {
    songIndex--
    if (songIndex < 0 ) {songIndex = array_tracks.length-1}
    loadSong(array_tracks[songIndex])
    playSong()
}
prevBtn.addEventListener('click', prevSong)



function setCurrentTime(e) {
    var width = this.clientWidth;
    var clickX = e.offsetX;
    var duration = mySMSound.duration;
    var curtime = (clickX / width) * duration;
    mySMSound.setPosition(curtime);
}
progressContainer.addEventListener('click', setCurrentTime)


playBtn.addEventListener('click', () => {
    const playing = player.classList.contains('play')
    if (playing) {
        pauseSong()
    } else {
        playSong()
    }
})








function playSong() {
    let next_track = songIndex+1;
    let prev_track = songIndex-1;
    player.classList.add('play')
    $('.icon.play').addClass('hidden');
    $('.icon.pause').removeClass('hidden');

    if(mySMSound.paused && !mySMSound.playState) {
        soundManager.resume('track_main');
    } else {
        soundManager.play('track_main', {
            onfinish: function() {nextSong()},
            whileplaying: function() {
                var duration = this.duration;
                var currentTime = this.position;
                var progressPrecent = (currentTime / duration) * 100
                progress.style.width = `${progressPrecent}%`
                cover_time.innerHTML = trackTime(duration/1000)
                cover_current_time.innerHTML = trackTime(currentTime/1000)
            }
        });
    }

    $(".prev_track .queue_title").text(array_tracks.at([prev_track]).name);
    if (songIndex >= array_tracks.length-1 ) {
        $(".next_track .queue_title").text(array_tracks[0].name);
    } else {
        $(".next_track .queue_title").text(array_tracks[next_track].name);
    }
    updateData()
}

function loadSong(song) {
    soundManager.destroySound('track_main');
    soundManager.createSound({
        id: 'track_main',
        url: `/music/${song.id}`,
        stream: true,
        autoLoad: true,
        multiShot: false, 
        volume: volumes*100,
        onload: function() { 
            mySMSound = soundManager.getSoundById('track_main');
        }
    });


    title.innerHTML = song.name;
    author.innerHTML = `<a href="/artist/${song.author_url}" style="color:#89798e" class='link'>${song.author}</a>`;
    cover.src = `/media/${song.image}`;
    canvas_color = fac.getColor(cover);
    base_image.src = `/media/${song.image}`;
    track_name.innerHTML = song.name;
    track_author.innerHTML = song.author;
    var lk = document.querySelector('.btn.liked svg');
        var has_track = array_fav_tracks.includes(song.id);
        if (has_track) {
            $(lk).addClass("liked");
        } else {
            $(lk).removeClass("liked");
        }
}
function updateIndex(e) {
    songIndex = array_tracks.findIndex(function(item, i){
        return item.id === e
    });
    loadSong(array_tracks[songIndex]);
}
var array_data;
var volumes;
function loadData() {
    return new Promise(function(resolve){
        $.get("/music/sync/", function(e) {
            array_data = e.message
            array_tracks = array_data.playlist
            volumes = array_data.curvol
            updateIndex(array_data.track)
            cover_time.innerHTML = trackTime(soundManager.onPosition('track_main').duration/1000)
            $("#volume_variable").height($("#volume_container").height()*volumes/0.2);
            resolve();
        })
    });
}
function startPlayTracks(track, type, id) {
    array_tracks = [];
    $.post( "/music/sync/", {csrfmiddlewaretoken: csrf, type:type, id:id, track:track })
        .done(function() {
            loadData().then(playSong)
        });
}


function addremove_playlist(trk_id) {
    var voidd;
    $.ajax({
        type:'GET',
        url:'/application/manage/playlist',
        success: (res) => {
            document.getElementsByTagName("body")[0].innerHTML += res;

            $('#get_playlists').bind("click", function(e) {
                $.get(`/application/manage/playlist/${e['target'].getAttribute('id')}&${trk_id}`)
                .done(function() {
                    document.getElementById("get_playlists").remove();
                });
            })
        }
    })


    // 
}

function context_menu_creator(e) {
    var context = document.createElement('div');
    context.id = "context_menu";
    context.innerHTML = `
        <div id="add_to_playlist" onclick="addremove_playlist('${e.target.parentElement.getElementsByClassName('favorite')[0].getAttribute('id')}')">Добавить(удалить) в плейлист</div>
        <div class="btn_context">Добавить в очередь</div>
        <div class="btn_context">Похожее</div><hr>
        <div class="btn_context">Поделиться</div>
        <div class="btn_context report">report</div>
    `;
    context.style.top = e.y + 'px';
    context.style.left = e.x + 'px';
    document.getElementsByTagName("body")[0].appendChild(context);
}

document.addEventListener("contextmenu", function(e) {
    if (e.target.parentElement.className == 'track') {
        if (!document.getElementById("context_menu")) {
            context_menu_creator(e)
        } else {
            document.getElementById("context_menu").remove();
            context_menu_creator(e)
        }
    }
    window.event.returnValue = false;
}, false);
$(document).bind("click", function(e) {
    if (e.target.id != "context_menu" && document.getElementById("context_menu")) {
        document.getElementById("context_menu").remove();
    }
});

function create_playlist() {
    $.ajax({
        type:'GET',
        url:'/application/manage/playlist/create',
        success: (res) => {
            document.getElementsByTagName("body")[0].innerHTML += res;
            $(document).bind("click", function(e) {
                if ($(e.target.offsetParent).attr('class') != "playlist_creator" && document.getElementsByClassName("playlist_creator")[0]) {
                    document.getElementsByClassName("playlist_creator")[0].remove();
                }
            });
        }
    })
}