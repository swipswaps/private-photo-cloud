'use strict';

let files2upload = [];
let files2upload_size = 0;
let files_w_error = [];
let files_by_hash = {};
let counter = 1;
let UPLOAD_WORKERS_NUM = 0;
let UPLOAD_WORKERS_NUM_MAX = 3;
let last_dragenter_target = null;

function initUpload() {
    document.documentElement.addEventListener("dragenter", dragenter, false);
    document.documentElement.addEventListener("dragleave", dragleave, false);
    document.documentElement.addEventListener("dragover", dragover, false);
    document.documentElement.addEventListener("drop", drop, false);
}

/* Drag-n-Drop

Drag and dro is rather complex thing. By default dragenter and dragleave runs on parent and ALL children.
So that if we listen to all events, we have a lot of garbage.

Events log for common scenario (move to page -> move to page element -> move to page -> leave page)

1. dragenter @ page

2. dragenter @ sub-element
3. dragleave @ page         => leave page while already entered sub-element

4. dragenter @ page
5. dragleave @ sub-element  => leave sub-element while already entered page

6. dragleave @ page         => leave page while last entered page

Solution: only if we dragleave the element we dragenter-ed last -> this leave should be counted.
*/

function dragenter(e) {
    // track last element we dragenter. It always runs BEFORE dragleave of another element (see Drag-n-Drop topic).
    last_dragenter_target = e.target;
    e.preventDefault();
    enableDrop(e);
}

function dragleave(e) {
    e.preventDefault();

    if(e.target !== last_dragenter_target) {
        return;
    }
    disableDrop(e);
}

function dragover(e) {
    e.preventDefault();
    e.stopPropagation();
}

function drop(e) {
    e.preventDefault();
    e.stopPropagation();
    disableDrop(e);
    // unfortunatelly we cannot recognize directories and read their content
    // see https://bugzilla.mozilla.org/show_bug.cgi?id=876480
    // in future we might do: http://www.rajeshsegu.com/2012/08/html5-drag-and-drop-a-folder/
    // E.g.: dt.items[0].getAsEntry().isFile / isDirectory
    uploadFiles(e.dataTransfer.files);
}

function enableDrop(e) {
    document.documentElement.setAttribute("dragenter", true);
    document.getElementById('drop-info').classList.remove('hidden');
}

function disableDrop(e) {
    document.documentElement.removeAttribute("dragenter");
    document.getElementById('drop-info').classList.add('hidden');
}

let BYTES_RANGES = [
    'B',
    'kB',
    'MB',
    'GB',
    'TB'
];

function bytes2text(bytes_num) {
    let num = bytes_num;
    let level = 0;
    while(num > 1000) {
        level += 1;
        num /= 1000;
    }

    num = Math.round(num * 100) / 100;

    return `${num} ${BYTES_RANGES[level]}`;
}

function lpad(num, len) {
    num = '' + num;
    while(num.length < len) {
        num = '0'+num;
    }
    return num;
}

function date2text(date) {
    let n = [
        date.getFullYear(),
        date.getMonth()+1,
        date.getDate(),
        date.getHours(),
        date.getMinutes(),
        date.getSeconds()
    ];

    n = n.map(function(num){
        return lpad(num, 2);
    });

    return `${n[0]}.${n[1]}.${n[2]} ${n[3]}:${n[4]}:${n[5]}`;
}

function hex(buffer) {
    // Using getUint32 reduces the number of iterations needed (we process 4 bytes each time)
    buffer = uint8_to_uint32(buffer);
    let chars = [];
    let padding = '00000000';
    for(let num of buffer) {
        // toString(16) will give the hex representation of the number without padding
        chars.push((padding + num.toString(16)).slice(-padding.length));
    }
    return chars.join("");
}

function uint8_to_uint32(buffer) {
    buffer = new DataView(buffer);
    let result = new Uint32Array(buffer.byteLength / 4);
    for(let i=0;i<buffer.byteLength;i+=4) {
        result[i / 4] = buffer.getUint32(i);
    }
    return result;
}

function sha1(text) {
    return crypto.subtle.digest("SHA-1", new TextEncoder("utf-8").encode(text)
      ).then(function(buffer) {
        return hex(buffer);
      });
  }

function getSizeGroup(size) {
    if(size < 1000000) {
        return 0;
    }
    if(size < 7000000) {
        return 1;
    }
    if(size < 20000000) {
        return 2;
    }
    return 3;
}

function getTypeGroup(type) {
    type = type.split('/')[0];
    if(type == 'image') {
        return 0;
    }
    if(type == 'video') {
        return 1;
    }
    return 2;
}

let CLASS_BY_GROUP = ['tiny', 'small', 'medium', 'large'];
let CLASS_BY_TYPE = ['type_image', 'type_video', 'type_other'];

function renderUploadItem(file_obj) {
    let div = document.createElement('div');

    div.setAttribute('id', `upload_${file_obj.id}`);
    div.classList.add('upload_file', CLASS_BY_TYPE[file_obj.type_group], CLASS_BY_GROUP[file_obj.size_group]);

    let title = [
        file_obj.file.name,
        bytes2text(file_obj.file.size),
        file_obj.file.type,
        `Updated at: ${date2text(new Date(file_obj.file.lastModified))}`
    ].join("\n");

    div.setAttribute('title', title);

    let progress_div = document.createElement('div');
    progress_div.setAttribute('id', `upload_${file_obj.id}_progress`);
    progress_div.classList.add('progress');
    div.appendChild(progress_div);

    return div;
}

function renderUploadedItem(file_obj) {
    // Media.id is a hard identifier, no need to use any other unique value, e.g. SHA1 sum
    let element;
    if(file_obj.media.thumbnail) {
        element = document.createElement('img');
        element.setAttribute('src', file_obj.media.thumbnail);
    } else {
        element = document.createElement('div');
    }

    element.setAttribute('id', `media_${file_obj.media.id}`);
    element.classList.add('media');
    return element;
}

function compareFiles(a, b) {
    if(a.size_group == b.size_group && a.type_group == b.type_group) {
        return 0;
    }
    if((a.size_group < b.size_group) || (a.size_group == b.size_group && a.type_group < b.type_group)) {
        return -1;
    }
    return 1;
}

function uploadFiles(files) {
    let upload_div = document.getElementById('images_to_upload');

    upload_div.classList.remove('hidden');

    let files_list = [];

    for(let file of files) {
        files_list.push({
            file: file,
            id: counter++,
            size_group: getSizeGroup(file.size),
            type_group: getTypeGroup(file.type)
        });
        files2upload_size += file.size;
    }

    files_list.sort(compareFiles);

    // process already processed files
    for(let file_obj of files_list) {
        upload_div.appendChild(renderUploadItem(file_obj));
    }

    // append new files to existing queue
    Array.prototype.push.apply(files2upload, files_list);

    files2upload.sort(compareFiles);

    processUploadQueue();
}

function eraseUploadState() {
    let upload_status_div = document.getElementById('upload_remaining');
    upload_status_div.classList.add('hidden');
    upload_status_div.innerText = '';
    files_by_hash = {};
    /* Assert following state:
    files2upload = []
    files2upload_size = 0
    files_w_error = []
    files_by_hash = {}
    UPLOAD_WORKERS_NUM = 0
    */
}

function processUploadQueue() {
    // DEBUG: return;
    if(!(files2upload.length + UPLOAD_WORKERS_NUM)) {
        // Once all uploads are finished -- reset the state
        eraseUploadState();
        return
    }

    let upload_status_div = document.getElementById('upload_remaining');
    upload_status_div.classList.remove('hidden');
    upload_status_div.innerText = `${files2upload.length + files_w_error.length + UPLOAD_WORKERS_NUM} files: ${bytes2text(files2upload_size)}`;

    let num, file;

    while(true) {
        // try to acquire worker
        num = ++UPLOAD_WORKERS_NUM;
        if(num > UPLOAD_WORKERS_NUM_MAX) {
            // release worker
            return UPLOAD_WORKERS_NUM--;
        }
        // worker is ready to process

        // get task for work
        file = files2upload.shift();

        if( !file) {
            // release worker
            return UPLOAD_WORKERS_NUM--;
        }

        // process file
        uploadFile(file);
    }
}

/* TODO: Implement Promise.all that have concurrency limit + failsafe */

function finishFileUpload(file) {
    // release worker
    UPLOAD_WORKERS_NUM--;
    files2upload_size -= file.file.size;
    // document.getElementById(`upload_${file.id}`).remove();

    let upload_div = document.getElementById(`upload_${file.id}`);

    let uploaded_div = document.getElementById('uploaded_images');

    uploaded_div.classList.remove('hidden');

    upload_div.addEventListener('transitionend', upload_div.remove.bind(upload_div), false);
    //addAnimation(upload_div, 'opacity: 0; transition: opacity 0.1s;'); => do via css
    upload_div.classList.add('uploaded');

    if(!file.is_duplicate) {
        let media_div = renderUploadedItem(file);

        let old_media_div = document.getElementById(media_div.id);
        if(old_media_div) {
            old_media_div.remove();
        }

        uploaded_div.appendChild(media_div);

        // animateMoveToObj(upload_div, media_div);
    } else {
        // TODO: Find an element that should be a source
    }

    processUploadQueue();
}

function deleteCssRule(stylesheet, selector) {
    for(let i=0;i<stylesheet.cssRules.length;i++) {
        if(stylesheet.cssRules[i].selectorText === selector) {
            stylesheet.deleteRule(i);
            return;
        }
    }
}

function addAnimation(obj, rule) {
    let stylesheet = document.styleSheets[0];
    let selector = `#${obj.id}.animate`;
    stylesheet.insertRule(`${selector}{ ${rule} }`, 0);
    obj.classList.add('animate');
    obj.addEventListener('transitionend', function(e){
        deleteCssRule(stylesheet, selector);
    }, false);
}

/*
function animateMoveToObj(source, target) {
    let from = source.getBoundingClientRect();
    let to = target.getBoundingClientRect();

    source.style.position = 'absolute';
    source.style.left = `${from.left}px`;
    source.style.top = `${from.top}px`;

    addAnimation(source, `opacity: 0.5; transform: translate(${window.pageXOffset + to.left - from.left}px, ${window.pageYOffset + to.top - from.top}px); width: ${to.width}px; height: ${to.height}px; transition: transform 3s, width 3s, height 3s, opacity 3s;`);
}
*/

function errorFileUpload(file) {
    UPLOAD_WORKERS_NUM--;
    files_w_error.push(file);
    document.getElementById(`upload_${file.id}`).classList.add('error');
    processUploadQueue();
}

function get_file_sha1(file) {
    // TODO: Consider iterative hashing, since we cannot handle >= 3 GB files
    // See: https://lists.w3.org/Archives/Public/public-webcrypto/2016Nov/0000.html
    return new Promise(function(resolve, reject) {
        let reader = new FileReader();
        reader.onloadend = function(e){
            crypto.subtle.digest("SHA-1", e.target.result).then(hex).then(resolve, reject);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file.file);
    }).then(function(digest){
        file.sha1 = digest;
        return file;
    });
}

function check_duplicate(file) {
    let source_file = files_by_hash[file.sha1];
    if(source_file) {
        file.is_duplicate = true;
        console.info('Prevented duplicate upload', file, 'base', source_file);
    } else {
        // for javascript there is no difference in performance if key is not set => skip setting the key
        files_by_hash[file.sha1] = file;
    }
    return file;
}

function check_already_uploaded(file) {
    return fetch(`/upload/media/sha1_${file.sha1}_${file.file.size}/`, {
        credentials: 'same-origin'
    }).then(function(response){
        if(!response.ok){
            throw Error('failed to check duplicates');
        }
        return response.json();
    }).then(function(json){
        file.media = json.media;
        return file;
    });
}

function escape(s) {
    return s.replace(/([.*+?\^${}()|\[\]\/\\])/g, '\\$1');
}

function getCookie(name) {
    let match = document.cookie.match(new RegExp('(?:^|;\\s*)' + escape(name) + '=([^;]*)'));
    return match ? match[1] : null;
}

function update_progress(file, e) {
    if(!e.lengthComputable || e.loaded == e.total) {
        return;
    }
    document.getElementById(`upload_${file.id}_progress`).style.height = `${100 * e.loaded / e.total}%`;
}

function upload_file(file) {
    if(file.media) {
        console.log('File already uploaded', file);
        return file;
    }

    if(file.is_duplicate) {
        return file;
    }

    let data = new FormData();
    data.set('session_id', UPLOAD_SESSION_ID);
    data.set('name', file.file.name);
    data.set('size', file.file.size);
    data.set('type', file.file.type);
    data.set('last_modified', file.file.lastModified);
    data.set('sha1', file.sha1);
    data.set('file', file.file);

    return fetch_w_progress('/upload/file/', {
        method: 'POST',
        credentials: 'same-origin',
        body: data,
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    }, function(e){
        update_progress(file, e);
    }).then(function(response){
        // Extract error from JSON response first
        return response.json().then(function(json){
            if(json.error) {
                throw Error(json.error);
            } else if(!response.ok) {
                throw Error('Failed to upload');
            }
            return json;
        }, function(){
            throw Error('Failed to upload');
        }).then(function(json){
            file.media = json.media;
            console.log('Uploaded file', file);
            return file;
        });
    });
}

function uploadFile(file) {
    return get_file_sha1(file)
    .then(check_duplicate)
    .then(check_already_uploaded)
    .then(upload_file)
    .then(finishFileUpload)
    .catch(function(err){
        console.error(err);
        errorFileUpload(file);
    });
}

function fetch_w_progress(url, settings, onprogress) {
    let xhr = new XMLHttpRequest();
    xhr.open(settings.method || 'GET', url, true); // async

    if(settings.credentials && settings.credentials != 'omit') {
        xhr.withCredentials = true;
    }

    if(settings.headers) {
        for(let k of Object.keys(settings.headers)) {
            xhr.setRequestHeader(k, settings.headers[k]);
        }
    }
    return new Promise(function(resolve, reject){
        xhr.onerror = reject;
        xhr.onloadend = function(e) {
            let response = e.target;
            response.ok = (response.status >= 200 && response.status < 300);
            response.json = function() {
                return new Promise(function(resolve, reject){
                    resolve(JSON.parse(response.responseText));
                });
            };
            resolve(response);
        };
        xhr.upload.onprogress = onprogress;
        xhr.send(settings.body || null);
    });
}

window.addEventListener("DOMContentLoaded", initUpload, true);
