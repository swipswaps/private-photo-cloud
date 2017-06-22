const path = require("path");
const webpack = require('webpack');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

const NODE_ENV = process.env.NODE_ENV || 'development';

module.exports = {
    context: path.resolve(__dirname, "js"),
    entry: {
        catalog: './catalog',
        upload: './upload',
        common: ["react", "react-dom"]
    },
    output: {
        path: path.resolve(__dirname, "public"),
        publicPath: "/static/public/",
        filename: "[name].js",
        chunkFilename: "[id].js",
        sourceMapFilename: "[file].map"
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "babel-loader"
            },
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: [
                        {
                            loader: 'css-loader',
                            query: {
                                discardComments: {removeAll: true}
                            }
                        },
                        {
                            loader: 'postcss-loader',
                        }
                    ]
                }),
            },
            {
                test: /.*\.(gif|png|jpg|jpeg|svg)$/i,
                loaders: [
                    {
                        loader: "file-loader",
                        query: {
                            hash: "md5",
                            digest: "hex",
                            name: '[name].[hash].[ext]'
                        }
                    },
                    {
                        loader: 'image-webpack-loader',
                        query: {
                            gifsicle: {
                                interlaced: false,
                            },
                            mozjpeg: {
                                quality: 65,
                                progressive: true,
                                interlaced: false
                            },
                            optipng: {
                                optimizationLevel: (NODE_ENV === 'development') ? 1 : 7
                            },
                            pngquant: {
                                quality: '65-90',
                                speed: 4
                            },
                            svgo: {
                                plugins: [
                                    {removeViewBox: false},
                                    {removeEmptyAttrs: false}
                                ]
                            }
                        }
                    }
                ]
            }]
    },
    plugins: [
        new webpack.NoEmitOnErrorsPlugin(),
        new webpack.NamedModulesPlugin(),
        new webpack.DefinePlugin({
            NODE_ENV: JSON.stringify(NODE_ENV),
            'process.env': {
                NODE_ENV: JSON.stringify(NODE_ENV),
            },
            LANG: JSON.stringify('en')
        }),
        new webpack.optimize.CommonsChunkPlugin({name: "common"}),
        new ExtractTextPlugin({filename: "[name].css", allChunks: true}),
        new webpack.optimize.ModuleConcatenationPlugin(),
    ],
    devtool: (NODE_ENV === 'development') ? 'cheap-module-source-map' : false,
    devServer: {
        contentBase: './',
        inline: true,
        noInfo: true,   // do not print tons or debug info
        proxy: {
            '/': {target: 'http://backend:8000'}
        }
    }
};

if (NODE_ENV === "production") {
    console.log('Compress...');
    module.exports.plugins.unshift(
        new webpack.LoaderOptionsPlugin({
            minimize: true,
            debug: false
        })
    );
    module.exports.plugins.push(
        // Minify the code. You need ES5 here -- see https://github.com/mishoo/UglifyJS2/issues/448
        new webpack.optimize.UglifyJsPlugin({
            output: {comments: false},
            compressor: {warnings: false}
        })
    );
}
