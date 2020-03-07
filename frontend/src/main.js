import Vue from "vue"
import App from "./App.vue"
import "./plugins/resource"
import vuetify from "./plugins/vuetify"
import VueRouter from "vue-router"
import router from "./router"
import i18n from "./i18n"
import {connectToWebSocket} from "./util/ws"
import store from "./store"
import {getCsrfToken} from "./util"

connectToWebSocket(store)

Vue.config.productionTip = false

Vue.use(VueRouter)

new Vue({
    render: h => h(App),
    vuetify,
    router,
    i18n,
    store
}).$mount("#app")

Vue.http.headers.common["X-CSRFToken"] = getCsrfToken()