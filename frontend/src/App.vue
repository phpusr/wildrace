<template>
    <div id="app">
        <v-app>
            <navigation-drawer v-model="drawer" />
            <toolbar @click="drawer = !drawer" />
            <v-content>
                <v-container>
                    <v-row>
                        <v-col offset-md="2" class="px-1">
                            <h1 v-html="title" class="text-center text-md-left"/>
                            <router-view class="px-0" />
                        </v-col>
                    </v-row>
                </v-container>
            </v-content>
            <app-footer />
        </v-app>
    </div>
</template>

<script>
    import NavigationDrawer from "./components/NavigationDrawer"
    import Toolbar from "./components/Toolbar"
    import Footer from "./components/Footer"
    import {activityHandler, methods} from "./util/topicActivityHandler"

    export default {
        name: "app",
        components: {NavigationDrawer, Toolbar, AppFooter: Footer},
        data() {
            return {
                drawer: this.$vuetify.breakpoint.mdAndUp
            }
        },
        computed: {
            title() {
                const {path} = this.$route
                const endIndex = path.substr(1).indexOf("/")
                const code = path.substring(0, endIndex > 0 ? endIndex + 1 : undefined)
                return this.$t("pages")[code]
            }
        },
        methods,
        created() {
            activityHandler(this)
        }
    }
</script>