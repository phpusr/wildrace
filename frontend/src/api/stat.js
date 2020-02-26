import Vue from "vue"

export default {
    get: (params) => Vue.http.get("/stat", {params}),
    publishPost: (params) => Vue.http.post("/stat/publishPost", {}, {params})
}