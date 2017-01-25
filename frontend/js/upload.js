'use strict';

// import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/upload.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

class UploadApp extends Component {
    componentDidMount() {
        // it is the right place to load data (with low overhead)
    }

    render() {
        return (
            <div className="App">
                Upload
            </div>
        );
    }
}


document.addEventListener('DOMContentLoaded', () => {
    ReactDOM.render(<UploadApp />, document.getElementById('root'));
});
