const path = require("path")

module.exports = {
    outputDir: path.resolve(__dirname, '../backend/app/static/front'),
    transpileDependencies: [
        "vuetify"
    ]
}