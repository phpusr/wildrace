<template>
    <v-navigation-drawer :value="value" @input="$emit('input', $event)" clipped app dark width="350px">
        <v-toolbar flat class="transparent">
            <v-list class="pt-4" :class="mobile ? 'pl-0' : 'pl-4'">
                <v-list-item>
                    <v-list-item-avatar>
                        <img :src="defaultAvatar" alt="Default avatar" />
                    </v-list-item-avatar>

                    <v-list-item-content>
                        <v-list-item-title v-if="user">{{user.username}}</v-list-item-title>
                        <login-dialog v-else />
                    </v-list-item-content>

                    <form id="logout-form" action="/api/auth/logout/">
                        <input type="hidden" name="next" value="/">
                        <v-btn v-if="user" icon>
                            <v-icon @click="logout">mdi-exit-to-app</v-icon>
                        </v-btn>
                    </form>
                </v-list-item>
            </v-list>
        </v-toolbar>

        <router-view name="menu" class="mx-5 mt-5" />

        <v-list class="mt-3">
            <v-list-item v-if="mobile && userIsAdmin" to="/config">
                <v-list-item-action>
                    <v-icon>mdi-settings</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>{{$t("pages./config")}}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <v-list-item v-if="mobile && userIsAdmin" @click="syncPosts" class="mt-2">
                <v-list-item-action>
                    <v-icon>mdi-sync</v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>{{$t("sync.title")}}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <v-list-item v-if="mobile" :href="config.groupLink" target="_blank" exact>
                <v-list-item-action class="font-weight-bold">VK</v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title>{{$t("pages.vkGroup")}}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <v-list-item class="mt-2">
                <v-list-item-action>
                    <div class="subheading grey--text text--lighten-1">
                        <div class="font-weight-medium">{{$t("post.lastSyncDate")}}:</div>
                        <div>{{lastSyncDate}}</div>
                    </div>
                </v-list-item-action>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script>
    import {mapActions, mapGetters, mapState} from "vuex"
    import LoginDialog from "./LoginDialog"

    export default {
        components: {LoginDialog},
        props: {
            value: Boolean
        },
        data: () => ({
            defaultAvatar: "https://www.yourfirstpatient.com/assets/default-user-avatar-thumbnail@2x-ad6390912469759cda" +
                "3106088905fa5bfbadc41532fbaa28237209b1aa976fc9.png"
        }),
        computed: {
            ...mapState(["user", "lastSyncDate", "config"]),
            ...mapGetters(["userIsAdmin"]),
            mobile() {
                return this.$vuetify.breakpoint.smAndDown
            }
        },
        methods: {
            ...mapActions(["syncPosts"]),
            logout() {
                const form = document.getElementById("logout-form")
                form.submit()
            }
        }
    }
</script>
