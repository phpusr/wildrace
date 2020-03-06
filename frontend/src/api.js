import Vue from "vue"

let post_res = Vue.resource("/api/posts/{id}/")

Vue.config.errorHandler = (error, vm, info) => {
    if (error.status && error.statusText && error.url) {
        alert(`${error.status}: ${error.statusText} on "${error.url}"`)
        return
    }

    alert(`Error: ${error}, ${info}`)
}

export const postApi = {
    getOne: id => post_res.get({id}),
    getAll: params => Vue.http.get("/api/posts/", {params}),
    getStat: () => post_res.get({id: "getStat"}, {params: {test: 1}}),
    getLastSyncDate: () => post_res.get({id: "getLastSyncDate"}),
    update: (post, updateNextPosts) => Vue.http.put(`/api/posts/${post.id}/`, post, {
        params: {"update_next_posts": updateNextPosts}
    }),
    remove: (id, updateNextPosts) => Vue.http.delete(`/api/posts/${id}/`, {
        params: {"update_next_posts": updateNextPosts}
    }),
    sync: () => post_res.update({id: "sync"}, {})
}

const config_res = Vue.resource("/api/config/1/")

export const configApi = {
    get: () => config_res.get(),
    update: (data) => config_res.update(data)
}

export const statApi = {
    get: (params) => Vue.http.get("/api/stat/", {params}),
    publishPost: (params) => Vue.http.post("/api/stat/publish/", params)
}

