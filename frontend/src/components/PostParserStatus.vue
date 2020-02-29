<template>
    <div>
        <v-tooltip v-if="mobile" top>
            <template v-slot:activator="{ on }">
                <v-btn :class="color" icon v-on="on">
                    <v-icon>{{icon}}</v-icon>
                </v-btn>
            </template>
            <span>{{value}}</span>
        </v-tooltip>
        <v-chip v-else :class="color" text-color="white">
            <v-icon left>{{icon}}</v-icon>
            <span :class="color">{{value}}</span>
        </v-chip>
    </div>
</template>

<script>
    import {postStatusColors, postStatusIcons} from "../util/data"

    export default {
        props: {
            statusId: Number
        },
        computed: {
            value() {
                return this.$t("post.statuses")[this.statusId]
            },
            icon() {
                return postStatusIcons[this.statusId]
            },
            color() {
                return postStatusColors[this.statusId]
            },
            mobile() {
                return this.$vuetify.breakpoint.xs
            }
        }
    }
</script>