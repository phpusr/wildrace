import Vue from "vue"

export default {
    get: (params) => Vue.http.get("/api/stat/", {params}),
    publishPost: (params) => Vue.http.post("/api/stat/", params)
}