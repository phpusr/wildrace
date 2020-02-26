<template>
    <v-dialog v-model="show" persistent scrollable width="500">
        <v-btn slot="activator" color="info">
            {{$t("user.login")}}
        </v-btn>

        <v-card>
            <v-card-title class="headline grey lighten-2">{{$t("user.loginTitle")}}</v-card-title>

            <v-card-text>
                <v-alert
                        :value="alertMessage"
                        color="error"
                        icon="warning"
                        outline
                >
                    {{alertMessage}}
                </v-alert>

                <v-form v-model="valid" class="mt-1">
                    <v-text-field
                            v-model="user.username"
                            :label="$t('user.username')"
                    />
                    <v-text-field
                            v-model="user.password"
                            :label="$t('user.password')"
                            :append-icon="showPassword ? 'visibility_off' : 'visibility'"
                            :type="showPassword ? 'text' : 'password'"
                            @click:append="showPassword = !showPassword"
                            @keyup.enter="login"
                    />
                </v-form>
            </v-card-text>

            <v-divider/>

            <v-card-actions>
                <v-spacer/>
                <v-btn color="primary" @click="login">
                    {{$t("user.login")}}
                </v-btn>
                <v-btn @click="cancel">
                    {{$t("default.cancelButton")}}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
    import {mapActions} from "vuex"

    export default {
        data: () => ({
            show: false,
            valid: false,
            user: {},
            showPassword: false,
            alertMessage: null
        }),
        methods: {
            ...mapActions(["loginAction"]),
            async login() {
                try {
                    await this.loginAction(this.user)
                    this.show = false
                    this.alertMessage = null
                } catch(e) {
                    if (e.status === 401) {
                        this.alertMessage = this.$t("user.loginNotFound")
                    } else {
                        this.alertMessage = `${e.status}: ${e.statusText}`
                    }
                }
            },
            cancel() {
                this.show = false
                this.alertMessage = null
            }
        }
    }
</script>