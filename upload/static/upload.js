var files2upload = [];
var files2upload_size = 0;
var files_w_error = [];
var counter = 1;
var UPLOAD_QUEUE = [];
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
        div.classList.add(`type_${content_type}`);

        var title = [
            file.name,
            bytes2text(file.size),
            file.type,
            `Updated at: ${date2text(new Date(file.lastModified))}`
        ].join("\n");

        div.setAttribute('title', title);

        upload_div.appendChild(div);
    }

    processUploadQueue();
}

function processUploadQueue() {
    document.getElementById('upload_remaining').innerText = `${files2upload.length + files_w_error.length + UPLOAD_QUEUE.length} files: ${bytes2text(files2upload_size)}`;
    while(files2upload.length && (UPLOAD_QUEUE.length < UPLOAD_QUEUE_SIZE)) {
        var file = files2upload.shift();
        UPLOAD_QUEUE.push(file);
        uploadFile(file);
    }
}

function finishFileUpload(file) {
    UPLOAD_QUEUE.splice(UPLOAD_QUEUE.indexOf(file), 1);
    files2upload_size -= file.file.size;
    document.getElementById(`upload_${file.id}`).remove();
    processUploadQueue();
}

function errorFileUpload(file) {
    UPLOAD_QUEUE.splice(UPLOAD_QUEUE.indexOf(file), 1);
    files_w_error.push(file);
    document.getElementById(`upload_${file.id}`).classList.add('error');
    processUploadQueue();
}

function uploadFile(file) {
    return new Promise(function(resolve, reject) {
        setTimeout(function(){resolve(file)}, 1000);
    }).then(finishFileUpload).catch(errorFileUpload);
}

window.addEventListener("DOMContentLoaded", initUpload, true);
