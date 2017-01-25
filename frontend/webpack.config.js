const path = require("path");
const webpack = require('webpack');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

const NODE_ENV = process.env.NODE_ENV || 'development';

module.exports = {
    context: path.resolve(__dirname, "js"),
    entry: {
        catalog: './catalog',
        upload: './upload',
        common: ["babel-polyfill", "react", "react-dom"]
    },
    output: {
        path: path.resolve(__dirname, "public"),
        publicPath: "/static/public/",
        filename: "[name].js",
        chunkFilename: "[id].js",
        sourceMapFilename: "[file].map"
    },
    module: {
        loaders: [
            {test: /\.js$/, exclude: /node_modules/, loader: "babel-loader"},
            {
                test: /\.css$/, exclude: /node_modules/, loader: ExtractTextPlugin.extract(
                "style-loader",
                ["css-loader?importLoaders=1",
                    "postcss-loader"]
            )
            },
            {
                test: /\.(jpg|jpeg|png|gif|svg)$/i, loaders: [
                'file?hash=md5&digest=hex&name=[name].[hash].[ext]',
                'image-webpack'
            ]
            }
        ]
    },
    imageWebpackLoader: {
        optimizationLevel: (NODE_ENV === 'development') ? 1 : 7,
        interlaced: false,
        mozjpeg: {
            quality: 65
        },
        pngquant: {
            quality: "65-90",
            speed: 4
        },
        svgo: {
            plugins: [
                {removeViewBox: false},
                {removeEmptyAttrs: false}
            ]
        }
    },
    plugins: [
        new webpack.NoErrorsPlugin(),
        new webpack.DefinePlugin({
            NODE_ENV: JSON.stringify(NODE_ENV),
            'process.env': {
                NODE_ENV: JSON.stringify(NODE_ENV),
            },
            LANG: JSON.stringify('en')
        }),
        new webpack.optimize.DedupePlugin(),
        new webpack.optimize.CommonsChunkPlugin({name: "common"}),
        new ExtractTextPlugin("[name].css"),
    ],
    devtool: (NODE_ENV === 'development') ? 'cheap-module-source-map' : null,
    devServer: {
        contentBase: './',
        inline: true,
        progress: true,
        noInfo: true,   // do not print tons or debug info
        proxy: {
            '/': {target: 'http://backend:8000'}
        }
    }
};

if (NODE_ENV === "production") {
    module.exports.plugins.push(
        // Minify the code. You need ES5 here -- see https://github.com/mishoo/UglifyJS2/issues/448
        new webpack.optimize.UglifyJsPlugin({
            compress: {warnings: false},
            output: {comments: false}
        })
    );
}
