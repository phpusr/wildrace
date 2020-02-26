<template>
    <v-navigation-drawer :value="value" @input="$emit('input', $event)" clipped app dark>
        <v-toolbar flat class="transparent">
            <v-list class="pt-4" :class="mobile ? 'pl-0' : 'pl-4'">
                <v-list-tile avatar>
                    <v-list-tile-avatar>
                        <img :src="defaultAvatar"  alt="Default avatar" />
                    </v-list-tile-avatar>

                    <v-list-tile-content>
                        <v-list-tile-title v-if="user">{{user.username}}</v-list-tile-title>
                        <login-dialog v-else />
                    </v-list-tile-content>

                    <v-btn v-if="user" flat icon>
                        <v-icon @click="logoutAction">exit_to_app</v-icon>
                    </v-btn>
                </v-list-tile>
            </v-list>
        </v-toolbar>

        <router-view name="menu" class="px-4 mt-5" />

        <v-list class="mt-3">
            <v-list-tile v-if="mobile && userIsAdmin" to="/config">
                <v-list-tile-action>
                    <v-icon>settings</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>{{$t("pages./config")}}</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>

            <v-list-tile v-if="mobile && userIsAdmin" @click="syncPosts" class="mt-2">
                <v-list-tile-action>
                    <v-icon>sync</v-icon>
                </v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>{{$t("sync.title")}}</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>

            <v-list-tile v-if="mobile" :href="config.groupLink" target="_blank" exact>
                <v-list-tile-action class="font-weight-bold">VK</v-list-tile-action>
                <v-list-tile-content>
                    <v-list-tile-title>{{$t("pages.vkGroup")}}</v-list-tile-title>
                </v-list-tile-content>
            </v-list-tile>

            <v-list-tile class="mt-2">
                <v-list-tile-action>
                    <span class="subheading grey--text text--lighten-1">
                        <span class="font-weight-medium">{{$t("post.lastSyncDate")}}: </span>
                        <span>{{lastSyncDate}}</span>
                    </span>
                </v-list-tile-action>
            </v-list-tile>
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
        methods: mapActions(["logoutAction", "syncPosts"])
    }
</script>
