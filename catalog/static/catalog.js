'use strict';

// TODO: Rewrite with ES6

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
    div.classList.add('show-month');
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
    // TODO: Format date into human-readable format: 1 Мая 2016, Понедельник
    return renderElement(`
        <div class="date-container">
            <div class="day-title">${day}</div>
        </div>
    `);
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
    let day = null;
    let day_container = null;
    for(let media of medias.media) {
        day = media.show_at.substring(0, 10);    // cut 2016-01-01

        if(day != prev_day) {
            if(day_container) {
                container.appendChild(day_container);
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

function onShowMedia(e) {
    showMedia(getTargetByClass(e, 'media'));
}

function showMedia($media) {
    if(!$media) {
        return;
    }

    let media = $media.dataset;

    let inner = '';

    // TODO: Do not show image for not supported types
    // TODO: Show "optimized" version instead of "raw" material
    // TODO: Show metadata if requested

    // TODO: Indicate information about media from the same shot / burst

    if(media.media_type == MEDIA_IMAGE) {
        inner = `<img src="${MEDIA_URL + media.content}" />`;
    } else if(media.media_type == MEDIA_VIDEO) {
        inner = `
        <video src="${MEDIA_URL + media.content}"
        controls="true"
        autoplay="true"
        poster="${MEDIA_URL + media.screenshot}"
        ></video>`;
    } else {
        // MEDIA_OTHER
        inner = `<a href="${MEDIA_URL + media.content}">Download ${escapeHTML(media.source_filename)}</a>`;
    }

    for(let $popup of document.querySelectorAll('.popup-media')) {
        // TODO: Stop and delete video tags
        $popup.remove();
    }

    // later elements overlay previous
    let div = renderElement(`
        <div class="popup-media" data-media_id="${media.id}">
            ${inner}
            <div class="popup-media-controls popup-media-prev" onclick="showPrevMedia(event)">&lArr;</div>
            <div class="popup-media-controls popup-media-next" onclick="showNextMedia(event)">&rArr;</div>
            <div class="popup-media-controls popup-media-close" onclick="onCloseMediaShow(event)">&times;</div>
        </div>
    `);
    document.documentElement.classList.add('noscrolling');
    document.documentElement.appendChild(div);
}

function closeMediaShow($div) {
    document.documentElement.classList.remove('noscrolling');
    $div.remove();
}

function onCloseMediaShow(e) {
    e.preventDefault();
    closeMediaShow(getTargetByClass(e, 'popup-media'));
}


function showPrevMedia(e) {
    e.preventDefault();
    let $div = getTargetByClass(e, 'popup-media');
    let $media = document.getElementById(`media-${$div.dataset.media_id}`);
    showMedia(getPrevMedia($media));
}


function showNextMedia(e) {
    e.preventDefault();
    let $div = getTargetByClass(e, 'popup-media');
    let $media = document.getElementById(`media-${$div.dataset.media_id}`);
    showMedia(getNextMedia($media));
}


function getPrevMedia($media) {
    let $prev = $media.previousElementSibling;
    if($prev && $prev.classList.contains('media')) {
        return $prev;
    }

    // TODO: Check performance and maybe implement recursive algorithm

    let $elements = document.querySelectorAll('.media');

    for(let i=0;i<$elements.length;i++) {
        if($elements[i].id == $media.id) {
            return i > 0 ? $elements[i-1] : null;
        }
    }
    return null;
}


function getNextMedia($media) {
    let $next = $media.nextElementSibling;
    if($next && $next.classList.contains('media')) {
        return $next;
    }

    // TODO: Check performance and maybe implement recursive algorithm

    let $elements = document.querySelectorAll('.media');

    for(let i=0;i<$elements.length;i++) {
        if($elements[i].id == $media.id) {
            return (i + 1 < $elements.length) ? $elements[i+1] : null;
        }
    }
    return null;
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

    // TODO: Indicate presence of other media in the same shot / burst
    // TODO: Have the same height for all the media, but cut it. Show cut areas on hover
    // TODO: Show an overlay to rotate the media

    return renderElement(`
        <div id="media-${media.id}"
        class="media ${MEDIA_TYPES[media.media_type]}"
        style="background-image: url(${MEDIA_URL + media.thumbnail}); width: ${media.thumbnail_width / HIDPI_SCALE}px; height: ${media.thumbnail_height / HIDPI_SCALE}px;"
        title="${escapeHTML(title.join("\n"))}"
        data-id="${media.id}"
        data-content="${media.content}"
        data-media_type="${media.media_type}"
        data-screenshot="${media.screenshot}"
        onclick="onShowMedia(event)"
        >${content}</div>
    `);
}

window.addEventListener("DOMContentLoaded", initCatalog, true);
