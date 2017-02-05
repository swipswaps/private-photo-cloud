'use strict';

import info from '../img/info.svg';

import 'normalize-css/normalize.css';
import '../css/common.css';
import '../css/catalog.css';

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import {onDomLoaded} from './helpers';


const HIDPI_SCALE = 2;
const MEDIA_IMAGE = 1;
const MEDIA_VIDEO = 2;


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
            this.setState({
                months: data.months.map(m => ({...m, expanded: false, media: []}))
            });
        });
    }

    render() {
        return (
            <ul>
                {this.state.months.map(m => (
                    <li key={m.month} onClick={this.toggleMonth.bind(this, m.month, !m.expanded)}>
                        {m.month} ({m.num})
                        {m.expanded ? (<MonthCatalog key={m.month} month={m.month} media={m.media} />) : null}
                    </li>
                ))}
            </ul>
        );
    }

    toggleMonth(month, expand) {
        if(expand) {
            this.loadMonth(month);
        }
        this.setState({
            months: this.state.months.map(m => m.month === month ? {...m, expanded: expand, media: []} : m)
        });
    }

    loadMonth(month) {
        fetch(`/images/${month}.json`, {
            credentials: 'same-origin',
        }).then(function(response){
            return response.json();
        }).then(data => {
            this.setState({
                months: this.state.months.map(m => m.month === month ? {...m, media: data.media} : m)
            });
        });
    }
}

function MonthCatalog(props) {
    return (
        <ul>
            {props.media.map(media => (<Media media={media} key={media.id} />))}
        </ul>
    );
}

function Media(props) {
    let media = props.media;
    let title = [];
    for(let k of Object.keys(media)) {
        title.push(`${k}: ${media[k]}`);
    }

    return (
        <li>
            <div id={`media-${media.id}`}
                 className={`media ${MEDIA_TYPES[media.media_type]}`}
                 style={{
                     backgroundImage: `url(${MEDIA_URL + media.thumbnail})`,
                     width: `${media.thumbnail_width / HIDPI_SCALE}px`,
                     height: `${media.thumbnail_height / HIDPI_SCALE}px`
                 }}
                 title={title.join("\n")}
                 data-id={media.id}
                 data-content={media.content}
                 data-media_type={media.media_type}
                 data-screenshot={media.screenshot || null}
            >
                {media.media_type === MEDIA_VIDEO ? (<img src={`${STATIC_URL}play.svg`} className="play-video" />) : null}
            </div>
        </li>
    );
}


onDomLoaded().then(() => {
    ReactDOM.render(<CatalogApp />, document.getElementById('root'));
});
