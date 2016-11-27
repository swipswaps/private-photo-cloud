'use strict';

const HIDPI_SCALE = 2;
const MEDIA_IMAGE = 1;
const MEDIA_VIDEO = 2;


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

    // TODO: Format date into human-readable format: 1 Мая 2016, Понедельник
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

function getTargetByClass(e, classname) {
    // event might caught by child -> iterate ascenting till get element with needed class
    let $element = e.target;
    while(!$element.classList.contains(classname)) {
        $element = $element.parentElement;
    }
    return $element;
}

function showMedia(e) {
    let $media = getTargetByClass(e, 'media');

    // TODO: Show popup for supported content types
    // TODO: Add navigation for viewing next / previous media
    // TODO: Show metadata if requested

    let media = $media.dataset;

    let inner = '';

    if(media.media_type == MEDIA_IMAGE) {
        inner = `<img src="${MEDIA_URL + media.content}" />`;
    } else if(media.media_type == MEDIA_VIDEO) {
        inner = `
        <video src="${MEDIA_URL + media.content}"
        controls="true"
        autoplay="true"
        poster="${MEDIA_URL + media.screenshot}"
        />`;
    } else {
        // MEDIA_OTHER
        inner = `<a href="${MEDIA_URL + media.content}">Download ${escapeHTML(media.source_filename)}</a>`;
    }

    for(let $popup of document.querySelectorAll('.popup-media')) {
        $popup.remove();
    }

    let div = renderElement(`
        <div class="popup-media" onclick="closeMediaShow(event)">
        ${inner}
        </div>
    `);
    document.documentElement.classList.add('noscrolling');
    document.documentElement.appendChild(div);
}

function closeMediaShow(e) {
    document.documentElement.classList.remove('noscrolling');
    let $div = getTargetByClass(e, 'popup-media');
    $div.remove();
}

function renderMedia(media) {
    let content = '';

    if(media.media_type == MEDIA_VIDEO) {
        // video
        // TODO: Reduce size of the icon
        content = `<img src="${STATIC_URL}play.svg" class="play-video" />`;
    }

    // TODO: Check show_at != shot_at => ask user to confirm the date
    // TODO: Check is_image && orientation is null => ask user to rotate
    // TODO: Check if no GPS => ask use to confirm location

    // TODO: Generate human-readable metadata explanation
    let title = [];
    for(let k of Object.keys(media)) {
        title.push(`${k}: ${media[k]}`);
    }

    // TODO: Have the same height for all the media, but cut it. Show cut areas on hover

    return renderElement(`
        <div class="media ${MEDIA_TYPES[media.media_type]}"
        style="background-image: url(${MEDIA_URL + media.thumbnail}); width: ${media.thumbnail_width / HIDPI_SCALE}px; height: ${media.thumbnail_height / HIDPI_SCALE}px;"
        title="${escapeHTML(title.join("\n"))}"
        data-content="${media.content}"
        data-media_type="${media.media_type}"
        data-screenshot="${media.screenshot}"
        onclick="showMedia(event)"
        >${content}</div>
    `);
}

window.addEventListener("DOMContentLoaded", initCatalog, true);
