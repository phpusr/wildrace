<template>
    <v-flex md8>
        <router-view />
        <v-container class="pa-0">
            <v-row no-gutters>
                <v-col cols="4" v-for="v in statTitles" :key="v.title" :class="v.class">
                    <v-card class="text-center">
                        <v-card-text>
                            <v-list-item-title :class="statTitleClass">{{v.value}}</v-list-item-title>
                            <div>{{v.title}}</div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <v-row no-gutters class="mt-5">
                <v-col cols="12" v-for="p in post.posts" :key="p.id" :class="postClass">
                    <post :post="p"/>
                </v-col>
            </v-row>

            <infinite-loading :identifier="infiniteId"  @infinite="infiniteHandler">
                <div slot="no-more">{{$t("post.noMoreMessages")}}</div>
                <div slot="no-results">{{$t("post.noResults")}}</div>
            </infinite-loading>
        </v-container>
    </v-flex>
</template>

<script>
    import Post from "../components/Post"
    import InfiniteLoading from "vue-infinite-loading"
    import postApi from "../api/post"
    import {mapMutations, mapState} from "vuex"

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
                        limit: 10,
                        offset: this.page * 10
                })
                this.addPostsMutation(body)

                const {results} = body
                if (results.length) {
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
                const postCount = (data.totalElements === stat.postCount) ? stat.postCount : `${data.totalElements} / ${stat.postCount}`
                return [
                    {title: this.$t("post.totalDistanceSum"), value: stat.distanceSum},
                    {title: this.$t("post.runningCount"), value: stat.runningCount, class: "px-1 px-sm-3"},
                    {title: this.$t("post.postCount"), value: postCount}
                ]
            },
            isMobileView() {
                return this.$vuetify.breakpoint.name === "xs"
            },
            statTitleClass() {
                return this.isMobileView ? 'headline' : 'display-1'
            },
            postClass() {
                return this.isMobileView ? 'my-1' : 'my-3'
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