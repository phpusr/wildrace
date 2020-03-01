<template>
    <v-col md="8" lazy-validation>
        <v-form ref="form" v-model="valid">
            <v-checkbox
                    v-model="config.syncPosts"
                    :label="$t('config.syncPosts')"
                    :readonly="show"
            />
            <v-checkbox
                    v-model="config.publishStat"
                    :label="$t('config.publishStat')"
                    :readonly="show"
            />
            <v-checkbox
                    v-model="config.commenting"
                    :label="$t('config.commenting')"
                    :readonly="show"
            />
            <v-checkbox
                    v-model="config.commentFromGroup"
                    :label="$t('config.commentFromGroup')"
                    :readonly="show"
            />
            <v-text-field
                    v-model="config.groupId"
                    :label="$t('config.groupId')"
                    :rules="requiredRules"
                    mask="###############"
                    required
                    :readonly="show"
                    :solo="show"
            />
            <v-textarea
                    v-model="config.commentAccessToken"
                    :label="$t('config.commentAccessToken')"
                    :rules="requiredRules"
                    required
                    :readonly="show"
                    :solo="show"
                    :append-icon="show ? null : 'refresh'"
                    @click:append="updateAccessToken"
            />

            <div v-if="show">
                <v-btn to="/config/edit">{{$t("default.editButton")}}</v-btn>
            </div>
            <div v-else>
                <div>
                    <v-btn :disabled="!valid" @click="save" color="primary">{{$t("default.saveButton")}}</v-btn>
                    <v-btn @click="cancel" primary>{{$t("default.cancelButton")}}</v-btn>
                </div>
            </div>
        </v-form>
    </v-col>
</template>

<script>
    import {configApi} from "../api"

    export default {
        data: () => ({
            valid: true,
            config: {},
            authorizeUrl: "#",
            requiredRules: [v => !!v || "Filed is required"]
        }),
        computed: {
            show() {
                return this.$route.path === "/config"
            }
        },
        methods: {
            async fetchData() {
                const response = await configApi.get()
                this.config = response.body
                this.authorizeUrl = this.config.authorizeUrl

                const {access_token, error} = this.$route.query
                if (access_token) {
                    this.config.commentAccessToken = access_token
                } else if (error) {
                    alert(error)
                }
            },
            updateAccessToken() {
                if (this.authorizeUrl.indexOf("vk.com/blank.html") >= 0) {
                    const win = window.open(this.authorizeUrl, "_blank")
                    win.focus()
                } else {
                    document.location = this.authorizeUrl
                }
            },
            async save() {
                if (this.$refs.form.validate()) {
                    const response = await configApi.update(this.config)
                    this.config = response.body
                    this.$router.push("/config")
                }
            },
            cancel () {
                this.$router.push("/config")
            }
        },
        created() {
            this.fetchData()
        },
        beforeRouteUpdate (to, from, next) {
            next()

            this.fetchData()
        }
    }
</script>