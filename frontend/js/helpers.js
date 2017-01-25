'use strict';

export function hex(buffer) {
    let hexCodes = [];
    let view = new DataView(buffer);
    let padding = '00000000';
    for (let i = 0; i < view.byteLength; i += 4) {
        // Using getUint32 reduces the number of iterations needed (we process 4 bytes each time)
        // toString(16) will give the hex representation of the number without padding
        let value = view.getUint32(i).toString(16);
        // We use concatenation and slice for padding
        hexCodes.push((padding + value).slice(-padding.length));
    }

    // Join all the hex strings into one
    return hexCodes.join("");
}

export function sha1(text) {
    return crypto.subtle.digest("SHA-1", new TextEncoder("utf-8").encode(text)).then(buffer => Helper.hex(buffer));
}

export function onDomLoaded() {
    return new Promise((resolve, reject) => {
        document.addEventListener('DOMContentLoaded', resolve);
    });
}
