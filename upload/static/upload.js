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

function uploadFiles(files) {
    console.log(files);
}

window.addEventListener("DOMContentLoaded", initUpload, true);
