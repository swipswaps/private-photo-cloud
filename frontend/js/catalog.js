'use strict';

import info from '../img/info.svg';

import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/catalog.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import {onDomLoaded} from './helpers';

function CatalogApp() {
    return (
        <div className="App">
            Months:
            <AllYearsCatalog />
        </div>
    );
}

class AllYearsCatalog extends Component {
    constructor(props) {
        super(props);
        this.state = {
            months: []
        };
    }
    componentDidMount() {
        fetch('/images/months.json', {credentials: 'same-origin'}
        ).then(response => response.json()
        ).then(data => {
            console.log(data);
            this.setState({
                months: data.months.map(m => ({month: m, expanded: false}))
            });
        });
    }

    render() {
        return (
            <ul>
                {this.state.months.map(month => (
                    <li key={month.month} onClick={this.toggleMonth.bind(this, month.month)}>
                        {month.month}
                        {month.expanded ? (<MonthCatalog key={month.month} month={month.month} />) : null}
                    </li>
                ))}
            </ul>
        );
    }

    toggleMonth(month) {
        this.setState({
            months: this.state.months.map(m => m.month === month ? {...m, expanded: !m.expanded} : m)
        });
    }
}

function MonthCatalog(props) {
    return (
        <ul>
            <li>{props.month}</li>
        </ul>
    );
}


onDomLoaded().then(() => {
    ReactDOM.render(<CatalogApp />, document.getElementById('root'));
});
