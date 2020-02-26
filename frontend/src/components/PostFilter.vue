<template>
    <v-layout v-if="userIsAdmin" row wrap>
        <v-flex class="mb-2" xs12>
            <span class="headline grey--text text--lighten-5">{{$t("post.filter")}}</span>
        </v-flex>
        <v-flex xs12>
            <v-select
                    :label="$t('post.status')"
                    :value="$route.query.statusId"
                    @change="changeQuery('statusId', $event)"
                    :items="statuses"
                    solo
                    clearable
            >
                <template slot="item" slot-scope="{ item }">
                    <span>
                        <v-icon :color="item.color">{{item.icon}}</v-icon>
                        <span class="ml-2">{{item.text}}</span>
                    </span>
                </template>
            </v-select>
        </v-flex>
        <v-flex xs12>
            <v-checkbox
                    :label="$t('post.manualEditing')"
                    :input-value="$route.query.manualEditing === 'true'"
                    @change="changeQuery('manualEditing', $event)"
            />
        </v-flex>
    </v-layout>
</template>

<script>
    import {postStatusColors, postStatusIcons} from "../util/data"
    import {mapGetters} from "vuex"

    export default {
        computed: {
            ...mapGetters(["userIsAdmin"]),
            statuses() {
                const statuses = this.$t("post.statuses")
                return Object.keys(statuses).map(key => (
                    { value: key, text: statuses[key], icon: postStatusIcons[key], color: postStatusColors[key] }
                ))
            }
        },
        methods: {
            changeQuery(name, value) {
                const query = { ...this.$route.query }
                if (value) {
                    query[name] = value
                } else {
                    delete query[name]
                }
                this.$router.push({ path: "/", query })
            }
        }
    }
</script>