class Helper {

  static hex(buffer) {
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

  static sha1(text) {
    var that = this;
    return crypto.subtle.digest("SHA-1", new TextEncoder("utf-8").encode(text)
      ).then(function(buffer) {
        return that.hex(buffer);
      });
  }
}

export default Helper;
