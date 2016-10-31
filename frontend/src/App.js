import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class App extends Component {
    constructor(props) {
        super(props);

        var generatePhoto = function(n) {
          return {
            name: String.fromCharCode(n + (n < 26 ? 97 : (65-26))),
            id: n
          };
        };

        this.state = {
            photos: Array.apply(null, Array(52)).map((_, n) => generatePhoto(n))
        };

        this.render = this.render.bind(this);
        this.renderPhotos = this.renderPhotos.bind(this);
        this.renderPhoto = this.renderPhoto.bind(this);
        this.onClick = this.onClick.bind(this);
    }

  hex(buffer) {
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

  sha1(text) {
    var that = this;
    return crypto.subtle.digest("SHA-1", new TextEncoder("utf-8").encode(text)
      ).then(function(buffer) {
        return that.hex(buffer);
      });
  }

  onClick(e) {
    var text = e.target.innerText;
    this.sha1(text).then(function(hex){
      alert(`clicked: ${text}: ${hex}`);
    })
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <img src={logo} className="App-logo" alt="logo10" />
        </div>
        {this.renderPhotos()}
      </div>
    );
  }

  renderPhotos() {
    return (
      <div className="photosList">
        {this.state.photos.map(photo => this.renderPhoto(photo))}
      </div>
      );
  }

  renderPhoto(photo) {
    return (
      <div className="photo" onClick={this.onClick} key={photo.id}>{photo.name}</div>
    );
  }
}

export default App;
