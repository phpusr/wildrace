<template>
    <v-footer dark class="pa-4">
        <v-layout justify-center>
            <div class="text-block">
                <v-layout column class="text-block text-center">
                    <div class="font-weight-bold">{{$t("default.projectName")}} v{{config.projectVersion}}</div>
                    <div>
                        Created by <a href="http://vk.com/phpusr">Sergey Doronin</a>
                    </div>
                </v-layout>
            </div>
            <div class="pt-1">
                <a href="https://github.com/phpusr/wildrace" target="_blank">
                    <img src="/static/app/img/GitHub-Mark-32px.png" class="logo" alt="GitHub logo">
                </a>
            </div>
        </v-layout>
    </v-footer>
</template>

<script>
    import {mapState} from "vuex"

    export default {
        computed: mapState(["config"])
    }
</script>

<style>
    .text-block {
        width: 200px;
    }
    .logo {
        filter: invert(100%);
        height: 32px;
    }
</style>