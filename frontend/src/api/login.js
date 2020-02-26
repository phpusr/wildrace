import Vue from "vue"

export default {
    async login(username, password) {
        return await Vue.http.post("/api/auth/login", {username, password}, {emulateJSON: true})
    },
    logout: () => Vue.http.post("/api/auth/logout")
}