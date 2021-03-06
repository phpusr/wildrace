import Vue from "vue"
import Vuex from "vuex"
import {deleteObject, replaceObject} from "./util/collections"
import dateFormat from "date-format"
import {postApi} from "./api"
import i18n from "./i18n"
import {postSortDirection} from "./util/data"

Vue.use(Vuex)

function formatDate(date) {
    return dateFormat("hh:mm:ss (dd.MM.yyyy)", new Date(date))
}

function sortPosts(posts) {
    const direction = postSortDirection === "desc" ? -1 : 1
    posts.sort((a, b) => {
        if (a.date > b.date) {
            return direction
        }

        if (a.date < b.date) {
            return -1 * direction
        }

        return 0
    })
}

const {user, stat, lastSyncDate, config} = document.frontendData

export default new Vuex.Store({
    state: {
        user,
        post: {
            posts: [],
            totalElements: 0,
            stat
        },
        lastSyncDate: formatDate(lastSyncDate),
        config,
        webSocketStatus: {
            connected: false
        }
    },
    getters: {
        userIsAdmin: state => {
            if (state.user == null) {
                return null
            }
            return state.user.isStaff
        }
    },
    mutations: {
        setUserMutation(state, user) {
            state.user = user
        },
        addPostMutation(state, post) {
            const data = state.post
            const index = data.posts.findIndex(el => el.id === post.id)
            if (index === -1) {
                data.posts.unshift(post)
                sortPosts(data.posts)
                data.totalElements++
            } else {
                replaceObject(data.posts, post)
            }
        },
        addPostsMutation(state, {results, count}) {
            if (results.length) {
                state.post.posts.push(...results)
                sortPosts(state.post.posts)
            }
            state.post.totalElements = count
        },
        resetPostsMutation(state) {
            state.post.posts = []
        },
        updatePostMutation(state, post) {
            replaceObject(state.post.posts, post)
        },
        removePostMutation(state, postId) {
            if (deleteObject(state.post.posts, postId)) {
                state.post.totalElements--
            }
        },
        updatePostStatMutation(state, stat) {
            state.post.stat = stat
        },
        updateLastSyncDateMutation(state, date) {
            state.lastSyncDate = formatDate(date)
        },
        setWebSocketStatusMutation(state, status) {
            state.webSocketStatus = status
        }
    },
    actions: {
        async syncPosts() {
            if (confirm(i18n.tc("sync.confirm"))) {
                await postApi.sync()
                alert(i18n.tc("sync.success"))
            }
        }
    }
})