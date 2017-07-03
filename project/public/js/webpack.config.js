var webpack = require("webpack");

module.exports = {
  context: __dirname,
  entry: "./src/main.js",
  output: {
    path: __dirname,
    filename: "app.min.js"
  },
  plugins: [
    new webpack.ProvidePlugin({
      jQuery: 'jquery',
      $: 'jquery',
      jquery: 'jquery'
    })
  ]
}