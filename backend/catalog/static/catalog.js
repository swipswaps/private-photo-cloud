'use strict';

// TODO: Rewrite with ES6
// TODO: Rewrite using React JS

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

function renderMonths(data) {
    let container = document.getElementById('months');
    for(let m of data.months) {
        container.appendChild(renderMonth(m.month));
    }
}

window.pgettext = window.pgettext || function(){};
window.gettext = window.gettext || function(){};

const MONTHS = [
    null,
    pgettext('month', 'January'),
    pgettext('month', 'February'),
    pgettext('month', 'March'),
    pgettext('month', 'April'),
    pgettext('month', 'May'),
    pgettext('month', 'June'),
    pgettext('month', 'July'),
    pgettext('month', 'August'),
    pgettext('month', 'September'),
    pgettext('month', 'October'),
    pgettext('month', 'November'),
    pgettext('month', 'December')
];

const MONTHS_OF = [
    null,
    pgettext('of month', 'January'),
    pgettext('of month', 'February'),
    pgettext('of month', 'March'),
    pgettext('of month', 'April'),
    pgettext('of month', 'May'),
    pgettext('of month', 'June'),
    pgettext('of month', 'July'),
    pgettext('of month', 'August'),
    pgettext('of month', 'September'),
    pgettext('of month', 'October'),
    pgettext('of month', 'November'),
    pgettext('of month', 'December')
];

const DAY_OF_WEEK = [
    null,
    gettext('Monday'),
    gettext('Tuesday'),
    gettext('Wednesday'),
    gettext('Thursday'),
    gettext('Friday'),
    gettext('Saturday'),
    gettext('Sunday')
];

function formatMonth(text) {
    text = text.split('-').map(n => Number.parseInt(n));
    let year = text[0];
    let month = text[1];

    return `${MONTHS[month]} ${year}`;
}

function formatDay(text) {
    let date = text.split('-').map(n => Number.parseInt(n));
    let year = date[0];
    let month = date[1];
    let day = date[2];

    let day_of_week = (new Date(text)).getDay() || 7;

    return `${day} ${MONTHS_OF[month]} ${year}, ${DAY_OF_WEEK[day_of_week]}`;
}

function renderMonth(month) {
    let $month_container = document.createElement('div');

    let $month_div = document.createElement('div');
    $month_div.classList.add('show-month');
    $month_div.innerText = formatMonth(month);

    let $month_images = document.createElement('div');
    $month_images.classList.add('images');

    $month_div.addEventListener('click', toggleMonth.bind(null, month, $month_div, $month_images), false);

    $month_container.appendChild($month_div);
    $month_container.appendChild($month_images);

    return $month_container;

}

function toggleMonth(month, $month_div, $month_images) {
    $month_images.innerHTML = '';
    if($month_images.classList.contains('expanded')) {
        $month_images.classList.remove('expanded');
    } else {
        $month_images.classList.add('expanded');
        loadMonth(month, $month_images);
    }
}

function loadMonth(month, container) {
    fetch(`/images/${month}.json`, {
        credentials: 'same-origin',
    }).then(function(response){
        return response.json();
    }).then(renderMonthMedia.bind(null, container));
}

function renderDayContainer(day) {
    return renderElement(`
        <div class="date-container">
            <div class="day-title">${formatDay(day)}</div>
        </div>
    `);
}

const MEDIA_TYPES = [null, 'media_image', 'media_video', 'media_other'];


function renderMonthMedia(container, medias) {
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

    // TODO: Hide popup if [Esc] was pressed.
    // TODO: For images -- go to the next media when clicked on image itself.

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
