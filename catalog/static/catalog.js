'use strict';


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

function renderMonthMedia(medias) {
    let container = document.getElementById('media');
    for(let media of medias.media) {
        container.appendChild(renderMedia(media));
    }
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

function renderMedia(media) {
    let div = document.createElement('span');

    div.innerHTML = `
    <img src="${MEDIA_URL + media.thumbnail}"
    width="${media.thumbnail_width}"
    height="${media.thumbnail_height}"
    title="${escapeHTML(JSON.stringify(media))}"
    />
    `;

    return div;
}

window.addEventListener("DOMContentLoaded", initCatalog, true);
