<template>
    <v-flex>
        <v-card :max-height="maxHeight">
            <v-card-title primary-title>
                <v-flex>
                    <v-layout align-start>
                        <v-avatar class="elevation-2">
                            <img :src="post.from.photo_50" alt="" />
                        </v-avatar>
                        <div class="ml-2">
                            <h3>
                                <a :href="post.link" target="_blank">#{{post.number}}</a>
                                {{post.from.firstName}}
                                {{post.from.lastName}}
                            </h3>
                            <div class="caption grey--text lighten-3">{{date}}</div>
                        </div>
                        <post-parser-status :status-id="post.statusId" class="ml-2" />

                        <v-tooltip top v-if="post.lastUpdate">
                            <v-btn icon class="blue-grey lighten-4" slot="activator">
                                <v-icon>how_to_reg</v-icon>
                            </v-btn>
                            <span>{{$t("post.manualEditing")}}</span>
                        </v-tooltip>

                        <v-spacer />
                        <v-btn v-if="userIsAdmin" icon @click="postEditHandler">
                            <v-icon>edit</v-icon>
                        </v-btn>
                    </v-layout>
                    <div v-if="post.distance" class="mt-3 display-1 blue--text font-weight-bold">+{{post.distance}}</div>
                    <div class="display-1 green--text">{{post.sumDistance}}</div>
                    <div class="mt-3 font-italic break-word" v-html="textOfPost" />
                </v-flex>
            </v-card-title>
            <v-card-actions v-if="largeTextOfPost">
                <v-btn flat color="orange" @click="expandPost">{{textExpandPostButton}}</v-btn>
            </v-card-actions>
            <div v-if="post.editReason" class="orange lighten-4 pa-2">
                <span class="font-weight-medium">{{$t("post.editReason")}}:</span>
                {{post.editReason}}
            </div>
        </v-card>
    </v-flex>
</template>

<script>
    import PostParserStatus from "./PostParserStatus"
    import dateFormat from "date-format"
    import {mapGetters} from "vuex"

    const maxLength = 170
    const maxHeight = 500

    export default {
        components: {PostParserStatus},
        props: {
            post: Object
        },
        data: () => ({
            maxHeight
        }),
        computed: {
            ...mapGetters(["userIsAdmin"]),
            date() {
                return dateFormat("hh:mm dd.MM.yyyy", new Date(this.post.date))
            },
            largeTextOfPost() {
                return this.post.text.length > maxLength
            },
            textExpandPostButton() {
                return this.$t(this.maxHeight ? "post.expand" : "post.squeeze")
            },
            textOfPost() {
                let {text} = this.post
                if (this.maxHeight) {
                    text = text.length > maxLength ? text.substr(0, maxLength) + "..." : text
                }
                return text.replace(/\n/g, "<br/>")
            }
        },
        methods: {
            postEditHandler() {
                this.$router.push({
                    path: `/post/${this.post.id}/edit`,
                    query: this.$route.query
                })
            },
            expandPost() {
                this.maxHeight = this.maxHeight ? null : maxHeight
            }
        }
    }
</script>

<style>
    .break-word {
        word-wrap: break-word;
    }
</style>