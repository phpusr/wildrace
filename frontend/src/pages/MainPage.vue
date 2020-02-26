<template>
    <v-flex md8>
        <router-view />
        <v-container v-bind="containerConfig" class="pa-0">
            <v-layout text-xs-center>
                <v-flex d-flex xs4 v-for="v in statTitles" :key="v.title">
                    <v-card>
                        <v-card-text>
                            <div class="display-1">{{v.value}}</div>
                            <div>{{v.title}}</div>
                        </v-card-text>
                    </v-card>
                </v-flex>
            </v-layout>

            <v-layout column>
                <post v-for="p in post.posts" :post="p" :key="p.id" />
                <infinite-loading :identifier="infiniteId"  @infinite="infiniteHandler">
                    <div slot="no-more">{{$t("post.noMoreMessages")}}</div>
                    <div slot="no-results">{{$t("post.noResults")}}</div>
                </infinite-loading>
            </v-layout>
        </v-container>
    </v-flex>
</template>

<script>
    import Post from "../components/Post"
    import InfiniteLoading from "vue-infinite-loading"
    import postApi from "../api/post"
    import {mapMutations, mapState} from "vuex"
    import {postSortDirection} from "../util/data"

    export default {
        components: {Post, InfiniteLoading},
        data: () => ({
            page: 0,
            infiniteId: +new Date()
        }),
        methods: {
            ...mapMutations(["addPostsMutation", "resetPostsMutation"]),
            resetData() {
                this.resetPostsMutation()
                this.page = 0
                this.infiniteId += 1
            },
            async infiniteHandler($state) {
                const params = this.$route.query
                const {body} = await postApi.getAll({
                        ...params,
                        size: 10,
                        sort: `date,${postSortDirection}`,
                        page: this.page
                })
                const {list} = body
                this.addPostsMutation(body)
                if (list.length) {
                    this.page += 1
                    $state.loaded()
                } else {
                    $state.complete()
                }
            }
        },
        computed: {
            ...mapState(["post"]),
            statTitles() {
                const data = this.post
                const stat = data.stat
                const numberOfPostsString = (data.totalElements === stat.numberOfPosts) ? stat.numberOfPosts : `${data.totalElements} / ${stat.numberOfPosts}`
                return [
                    {title: this.$t("post.totalSumDistance"), value: stat.sumDistance},
                    {title: this.$t("post.numberOfRuns"), value: stat.numberOfRuns},
                    {title: this.$t("post.numberOfPosts"), value: numberOfPostsString}
                ]
            },
            containerConfig() {
                return {
                    ["grid-list-" + this.$vuetify.breakpoint.name]: true
                }
            }
        },
        created() {
            this.resetData()
        },
        beforeRouteUpdate (to, from, next) {
            next()

            if (JSON.stringify(to.query) !== JSON.stringify(from.query)) {
                this.resetData()
            }
        }
    }
</script>

<style>

</style>