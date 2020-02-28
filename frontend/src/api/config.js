import Vue from "vue"

const api = Vue.resource("/api/config/1/")

export default {
    get: () => api.get(),
    update: (data) => api.update(data)
}