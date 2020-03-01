import Vue from "vue"

let api = Vue.resource("/api/posts/{id}/")

export const postApi = {
    getOne: id => api.get({id}),
    getAll: params => Vue.http.get("/api/posts/", {params}),
    getStat: () => api.get({id: "getStat"}, {params: {test: 1}}),
    getLastSyncDate: () => api.get({id: "getLastSyncDate"}),
    update: (post, updateNextPosts) => Vue.http.put(`/api/posts/${post.id}/`, post, {params: {updateNextPosts}}),
    remove: (id, updateNextPosts) => Vue.http.delete(`/api/posts/${id}/`, {params: {updateNextPosts}}),
    sync: () => api.update({id: "sync"}, {})
}

api = Vue.resource("/api/config/1/")

export const configApi = {
    get: () => api.get(),
    update: (data) => api.update(data)
}

export const statApi = {
    get: (params) => Vue.http.get("/api/stat/", {params}),
    publishPost: (params) => Vue.http.post("/api/stat/", params)
}

