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

                <form id="login-form" class="mt-1" method="post" action="/api/auth/login/">
                    <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
                    <input type="hidden" name="next" value="/">

                    <v-text-field
                            name="username"
                            :label="$t('user.username')"
                    />
                    <v-text-field
                            name="password"
                            :label="$t('user.password')"
                            :append-icon="showPassword ? 'visibility_off' : 'visibility'"
                            :type="showPassword ? 'text' : 'password'"
                            @click:append="showPassword = !showPassword"
                            @keyup.enter="login"
                    />
                </form>
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
    import {getCsrfToken} from "../util"

    export default {
        data: () => ({
            show: false,
            showPassword: false,
            alertMessage: null,
            csrfToken: getCsrfToken()
        }),
        methods: {
            async login() {
                const form = document.getElementById("login-form")
                form.submit()
            },
            cancel() {
                this.show = false
                this.alertMessage = null
            }
        }
    }
</script>