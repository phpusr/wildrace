<template>
    <v-app-bar app clipped-left dark>
        <v-app-bar-nav-icon @click.stop="$emit('click')" />

        <v-btn text to="/" class="text-capitalize">
            <v-toolbar-title>
                <span class="font-weight-regular">Wild</span>
                <span class="font-weight-bold">Race</span>
            </v-toolbar-title>
        </v-btn>

        <v-btn text to="/stat">{{$t("pages./stat")}}</v-btn>

        <v-toolbar-items v-if="this.$vuetify.breakpoint.mdAndUp">
            <v-btn v-if="userIsAdmin" text @click="syncPosts">{{$t("sync.title")}}</v-btn>
            <v-btn v-if="userIsAdmin" text to="/config">{{$t("pages./config")}}</v-btn>
            <v-btn text :href="config.groupLink" target="_blank" exact>{{$t("pages.vkGroup")}}</v-btn>
        </v-toolbar-items>

        <v-spacer />
    </v-app-bar>
</template>

<script>
    import {mapActions, mapGetters, mapState} from "vuex"

    export default {
        computed: {
            ...mapState(["config"]),
            ...mapGetters(["userIsAdmin"])
        },
        methods: mapActions(["syncPosts"])
    }
</script>