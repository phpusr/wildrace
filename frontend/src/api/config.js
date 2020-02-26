import Vue from "vue"

const api = Vue.resource("/config")

export default {
    get: () => api.get(),
    update: (data) => api.update(data)
}