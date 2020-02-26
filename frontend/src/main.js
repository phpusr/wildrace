import Vue from "vue"
import "./api/resource"
import App from "./App.vue"
import Vuetify from "vuetify"
import VueRouter from "vue-router"
import router from "./router"
import i18n from "./i18n"
// import {connectToWS} from "./util/ws"
import store from "./store"

import "vuetify/dist/vuetify.min.css"

// connectToWS()

Vue.config.productionTip = false

Vue.use(Vuetify)
Vue.use(VueRouter)

new Vue({
    render: h => h(App),
    router,
    i18n,
    store
}).$mount("#app")
