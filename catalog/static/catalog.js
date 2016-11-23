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

function renderMedia(media) {
    let div = document.createElement('div');

    let img = document.createElement('img');
    img.setAttribute('src', MEDIA_URL + media.thumbnail);
    img.setAttribute('width', media.thumbnail_width);
    img.setAttribute('height', media.thumbnail_height);
    img.setAttribute('title', JSON.stringify(media));
    div.appendChild(img);

    return div;
}

window.addEventListener("DOMContentLoaded", initCatalog, true);
