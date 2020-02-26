<template>
    <v-dialog v-model="show" persistent scrollable width="500">
        <v-card>
            <v-card-title class="headline grey lighten-2">{{$t("post.editDialogTitle")}}</v-card-title>

            <v-card-text>
                <v-form v-model="valid">
                    <v-text-field
                            v-model="post.number"
                            :label="$t('post.number')"
                    />
                    <v-select
                            :value="post.status + ''"
                            @change="post.status = +$event"
                            :items="statuses"
                            :label="$t('post.status')"
                            required
                    />
                    <v-text-field
                            v-model="post.distance"
                            :label="$t('post.distance')"
                    />
                    <v-text-field
                            v-model="post.sumDistance"
                            :label="$t('post.sumDistance')"
                    />
                    <v-textarea
                            v-model="post.editReason"
                            :label="$t('post.editReason')"
                    />

                </v-form>
            </v-card-text>

            <v-divider/>

            <v-card-actions class="py-0">
                <v-checkbox
                        v-model="updateNextPosts"
                        :label="$t('post.updateNextPosts')"
                />
            </v-card-actions>

            <v-card-actions>
                <v-btn color="error" @click="remove">
                    <v-icon :left="smAndUp">delete</v-icon>
                    <span v-if="smAndUp">{{$t("default.deleteButton")}}</span>
                </v-btn>
                <v-spacer/>
                <v-btn color="primary" @click="update">
                    <v-icon :left="smAndUp">save</v-icon>
                    <span v-if="smAndUp">{{$t("default.saveButton")}}</span>
                </v-btn>
                <v-btn @click="goToMainPage">
                    {{$t("default.cancelButton")}}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
    import postApi from "../api/post"

    export default {
        data() {
            return {
                valid: false,
                post: {},
                updateNextPosts: false
            }
        },
        created() {
            this.fetchData()
        },
        computed: {
            postId() {
                return this.$route.params.postId
            },
            show() {
                return !!this.postId
            },
            statuses() {
                const statuses = this.$t("post.statuses")
                return Object.keys(statuses).map(key => (
                    { value: key, text: statuses[key] }
                ))
            },
            smAndUp() {
                return this.$vuetify.breakpoint.smAndUp
            }
        },
        methods: {
            async fetchData() {
                const {body} = await postApi.getOne(this.postId)
                this.post = body
            },
            update() {
                postApi.update(this.post, this.updateNextPosts)
                this.goToMainPage()
            },
            remove() {
                if (confirm(this.$t("default.confirmDelete"))) {
                    postApi.remove(this.post.id, this.updateNextPosts)
                    this.goToMainPage()
                }
            },
            goToMainPage() {
                this.$router.push({ path: "/", query: this.$route.query })
            }
        }
    }
</script>