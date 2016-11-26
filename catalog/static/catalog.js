'use strict';

let HIDPI_SCALE = 2;


function initCatalog() {
    fetch('/images/months.json', {
        credentials: 'same-origin'
    }).then(function(response){
        return response.json();
    }).then(renderMonths);
}

function renderMonths(dates) {
    let container = document.getElementById('months');
    for(let month of dates.months) {
        container.appendChild(renderMonth(month));
    }
}

function renderMonth(month) {
    let div = document.createElement('div');
    div.innerText = month;
    div.addEventListener('click', function(e) {
        loadMonth(month);
    }, false);
    return div;
}

function loadMonth(month) {
    fetch(`/images/${month}.json`, {
        credentials: 'same-origin',
    }).then(function(response){
        return response.json();
    }).then(renderMonthMedia);
}

function renderDayContainer(day) {
    let div = document.createElement('div');
    div.classList.add("day-container");

    // TODO: Format date into human-readable format

    div.innerHTML = `
        <div class="day-title">${day}</div>
    `;

    return div;
}

const MEDIA_TYPES = [null, 'media_image', 'media_video', 'media_other'];

function renderMonthMedia(medias) {
    let container = document.getElementById('media');
    // erase content
    container.innerHTML = '';

    if(!medias.media.length) {
        return;
    }

    let prev_day = null;
    let day_container = null;
    for(let media of medias.media) {
        let day = media.show_at.substring(0, 10);    // cut 2016-01-01

        if(day != prev_day) {
            if(day_container) {
                container.append(day_container);
            }
            day_container = renderDayContainer(day);
            prev_day = day;
        }

        day_container.appendChild(renderMedia(media));
    }
    container.append(day_container);
}

// Fastest way according to https://jsperf.com/htmlencoderegex/35
let DOMtext = document.createTextNode("html");
let DOMnative = document.createElement("span");
DOMnative.appendChild(DOMtext);

function escapeHTML(html) {
    DOMtext.nodeValue = html;
    // by default it does not escape " and '
    return DOMnative.innerHTML.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// end

const render_container = document.createElement('div');

function renderElement(html) {
    render_container.innerHTML = html;
    return render_container.children[0];
}

function renderElements(html) {
    render_container.innerHTML = html;
    return render_container.children;
}

function showMedia(e) {
    let $media = e.target;
    // we could have clicked on child element, so go till the "media" element
    while(!$media.classList.contains('media')) {
        $media = $media.parentElement;
    }
    location.href = MEDIA_URL + $media.dataset.content;
}

function renderMedia(media) {
    let content = '';

    if(media.media_type == 2) {
        // video
        content = `<img src="${STATIC_URL}play.svg" class="play-video" />`;
    }

    let title = [];
    for(let k of Object.keys(media)) {
        title.push(`${k}: ${media[k]}`);
    }

    return renderElement(`
        <div class="media ${MEDIA_TYPES[media.media_type]}"
        style="background-image: url(${MEDIA_URL + media.thumbnail}); width: ${media.thumbnail_width / HIDPI_SCALE}px; height: ${media.thumbnail_height / HIDPI_SCALE}px;"
        title="${escapeHTML(title.join("\n"))}"
        data-content="${media.content}"
        onclick="showMedia(event)"
        >${content}</div>
    `);
}

window.addEventListener("DOMContentLoaded", initCatalog, true);
