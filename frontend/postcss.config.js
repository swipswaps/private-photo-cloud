module.exports = {
    plugins: [
        require('autoprefixer')({}),
        require('postcss-color-short')({}),
        require('postcss-focus')({}),
        require('postcss-short-size')({})
    ]
};
