import Vue from "vue"

export default {
    async login(username, password) {
        return await Vue.http.post("/login", {username, password}, {emulateJSON: true})
    },
    logout: () => Vue.http.post("/logout")
}