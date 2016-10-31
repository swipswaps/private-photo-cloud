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

  onClick() {
    alert('clicked!');
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
