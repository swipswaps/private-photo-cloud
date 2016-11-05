var files2upload = [];
var files2upload_size = 0;
var files_w_error = [];
var counter = 1;
var UPLOAD_QUEUE = 0;
var UPLOAD_QUEUE_SIZE = 3;

function initUpload() {
    window.addEventListener("dragenter", dragenter, true);
    window.addEventListener("dragleave", dragleave, true);
    document.documentElement.addEventListener("dragover", dragover, false);
    document.documentElement.addEventListener("drop", drop, false);
}

function dragenter(e) {
    e.preventDefault();
    enableDrop(e);
}

function dragleave(e) {
    disableDrop(e);
}

function dragover(e) {
    e.preventDefault();
}

function drop(e) {
    e.preventDefault();
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

var BYTES_RANGES = [
    'B',
    'kB',
    'MB',
    'GB',
    'TB',
];

function bytes2text(bytes_num) {
    var num = bytes_num;
    var level = 0;
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
    var n = [
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
    var hexCodes = [];
    var view = new DataView(buffer);
    var padding = '00000000';
    for (var i = 0; i < view.byteLength; i += 4) {
        // Using getUint32 reduces the number of iterations needed (we process 4 bytes each time)
        // toString(16) will give the hex representation of the number without padding
        var value = view.getUint32(i).toString(16);
        // We use concatenation and slice for padding
        hexCodes.push((padding + value).slice(-padding.length));
    }

    // Join all the hex strings into one
    return hexCodes.join("");
}

function sha1(text) {
    return crypto.subtle.digest("SHA-1", new TextEncoder("utf-8").encode(text)
      ).then(function(buffer) {
        return hex(buffer);
      });
  }

function uploadFiles(files) {
    var upload_div = document.getElementById('images_to_upload');

    upload_div.classList.remove('hidden');

    for(let file of files) {
        var file_obj = {file: file, id: counter++};
        files2upload.push(file_obj);
        files2upload_size += file.size;

        var div = document.createElement('div');

        var content_type = file.type.split('/')[0];

        div.setAttribute('id', `upload_${file_obj.id}`);
        div.classList.add('upload_file');

        if(content_type) {
            div.classList.add(`type_${content_type}`);
        }

        var title = [
            file.name,
            bytes2text(file.size),
            file.type,
            `Updated at: ${date2text(new Date(file.lastModified))}`
        ].join("\n");

        div.setAttribute('title', title);

        var progress_div = document.createElement('div');
        progress_div.setAttribute('id', `upload_${file_obj.id}_progress`);
        progress_div.classList.add('progress');
        div.appendChild(progress_div);

        upload_div.appendChild(div);
    }

    processUploadQueue();
}

function processUploadQueue() {
    document.getElementById('upload_remaining').innerText = `${files2upload.length + files_w_error.length + UPLOAD_QUEUE} files: ${bytes2text(files2upload_size)}`;

    var num, file;

    while(true) {
        // try to acquire worker
        num = ++UPLOAD_QUEUE;
        if(num > UPLOAD_QUEUE_SIZE) {
            // release worker
            return UPLOAD_QUEUE--;
        }
        // worker is ready to process

        // get task for work
        file = files2upload.shift();

        if( !file) {
            // release worker
            return UPLOAD_QUEUE--;
        }

        // process file
        uploadFile(file);
    }
}

/* TODO: Implement Promise.all that have concurrency limit + failsafe */

function finishFileUpload(file) {
    // release worker
    UPLOAD_QUEUE--;
    files2upload_size -= file.file.size;
    document.getElementById(`upload_${file.id}`).remove();
    processUploadQueue();
}

function errorFileUpload(file) {
    UPLOAD_QUEUE--;
    files_w_error.push(file);
    document.getElementById(`upload_${file.id}`).classList.add('error');
    processUploadQueue();
}

function get_file_sha1(file) {
    return new Promise(function(resolve, reject) {
        var reader = new FileReader();
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

function check_for_duplicated(file) {
    return fetch(`/upload/media/sha1_${file.sha1}/`, {
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

function getCookie(name) {
    function escape(s) { return s.replace(/([.*+?\^${}()|\[\]\/\\])/g, '\\$1'); };
    var match = document.cookie.match(RegExp('(?:^|;\\s*)' + escape(name) + '=([^;]*)'));
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
        return file;
    }

    var data = new FormData();
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
        if(!response.ok) {
            throw Error('Failed to upload');
        }
        return response.json().then(function(json){
            file.media = json.media;
            return file;
        });
    });
}

function uploadFile(file) {
    return get_file_sha1(file
    ).then(check_for_duplicated
    ).then(upload_file
    ).then(function(uploaded_file) {
        console.log(uploaded_file);
        return uploaded_file;
    }).then(finishFileUpload).catch(function(err){
        console.error(err);
        errorFileUpload(file);
    });
}

function fetch_w_progress(url, settings, onprogress) {
    var xhr = new XMLHttpRequest();
    xhr.open(settings.method || 'GET', url, true); // async

    if(settings.credentials && settings.credentials != 'omit') {
        xhr.withCredentials = true;
    }

    if(settings.headers) {
        for(var k in settings.headers) {
            xhr.setRequestHeader(k, settings.headers[k]);
        }
    }
    return new Promise(function(resolve, reject){
        xhr.onerror = reject;
        xhr.onload = function(e) {
            console.log(e);
            var response = e.target;
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
