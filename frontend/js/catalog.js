'use strict';

// import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/catalog.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

class CatalogApp extends Component {
    componentDidMount() {
        // it is the right place to load data (with low overhead)
    }

    render() {
        return (
            <div className="App">
                Catalog
            </div>
        );
    }
}


document.addEventListener('DOMContentLoaded', () => {
    ReactDOM.render(<CatalogApp />, document.getElementById('root'));
});
