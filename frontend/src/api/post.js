import Vue from "vue"

const api = Vue.resource("/post/{id}")

export default {
    getOne: id => api.get({id}),
    getAll: params => Vue.http.get("/post", {params}),
    getStat: () => api.get({id: "getStat"}, {params: {test: 1}}),
    getLastSyncDate: () => api.get({id: "getLastSyncDate"}),
    update: (post, updateNextPosts) => Vue.http.put(`/post/${post.id}`, post, {params: {updateNextPosts}}),
    remove: (id, updateNextPosts) => Vue.http.delete(`/post/${id}`, {params: {updateNextPosts}}),
    sync: () => api.update({id: "sync"}, {})
}