import Vue from "vue"

const api = Vue.resource("/api/posts/{id}/")

export default {
    getOne: id => api.get({id}),
    getAll: params => Vue.http.get("/api/posts/", {params}),
    getStat: () => api.get({id: "getStat"}, {params: {test: 1}}),
    getLastSyncDate: () => api.get({id: "getLastSyncDate"}),
    update: (post, updateNextPosts) => Vue.http.put(`/api/posts/${post.id}/`, post, {params: {updateNextPosts}}),
    remove: (id, updateNextPosts) => Vue.http.delete(`/api/posts/${id}/`, {params: {updateNextPosts}}),
    sync: () => api.update({id: "sync"}, {})
}