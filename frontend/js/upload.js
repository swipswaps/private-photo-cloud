'use strict';

import info from '../img/info.svg';

import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/upload.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import {onDomLoaded} from './helpers';

class UploadApp extends Component {
    constructor(props) {
        super(props);
        window.uploader = this;
        this.state = {
            uploaded: []
        };
    }

    render() {
        return (
            <div>
            {this.state.uploaded.map(media => (
                <UploadedMedia id={media.id} thumbnail={media.thumbnail} key={media.id} />
            ))}
            </div>
        );
    }

    add_media(media) {
        this.setState({
            uploaded: this.state.uploaded.filter(m => m.id !== media.id).concat(media)
        });
    }

    replace_media(media) {
        this.setState({
            uploaded: this.state.uploaded.map(m => m.id === media.id ? media : m)
        });
    }
}

function UploadedMedia(props) {
    if(!props.thumbnail) {
        return (<div className="media" id={`media_${props.id}`} />);
    }
    else if(props.thumbnail === '!') {
        return (<img className="media" id={`media_${props.id}`} src={window.PLACEHOLDER_IMAGE_SRC} />);
    }
    return (<img className="media" id={`media_${props.id}`} src={props.thumbnail} />);
}


onDomLoaded().then(() => {
    ReactDOM.render(<UploadApp />, document.getElementById('uploaded_images'));
});
