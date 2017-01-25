'use strict';

import info from '../img/info.svg';

import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/catalog.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import {onDomLoaded} from './helpers';

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

onDomLoaded().then(() => {
    ReactDOM.render(<CatalogApp />, document.getElementById('root'));
});
