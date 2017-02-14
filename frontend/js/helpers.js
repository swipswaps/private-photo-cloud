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

export function formatMonth(text) {
    text = text.split('-').map(n => Number.parseInt(n));
    let year = text[0];
    let month = text[1];

    return `${MONTHS[month]} ${year}`;
}

export function formatDay(text) {
    let date = text.split('-').map(n => Number.parseInt(n));
    let year = date[0];
    let month = date[1];
    let day = date[2];

    let day_of_week = (new Date(text)).getDay() || 7;

    return `${DAY_OF_WEEK[day_of_week]}, ${day} ${MONTHS_OF[month]} ${year}`;
}

export function group_by(data, fn) {
    let rows;
    return [...data.map(row => [fn(row), row]).reduce((previousValue, [key, row]) => {
        rows = previousValue.get(key);
        if (!rows) {
            // assign returns the value
            previousValue.set(key, (rows = []));
        }
        rows.push(row);
        return previousValue;
    }, new Map()).entries()];
}
