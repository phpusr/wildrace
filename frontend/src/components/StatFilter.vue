<template>
    <v-tabs v-model="activeTabIndex" color="cyan" dark slider-color="yellow">
        <v-tab ripple>{{ $t("stat.distanceRange") }}</v-tab>
        <v-tab ripple>{{ $t("stat.dateRange") }}</v-tab>

        <v-tab-item>
            <v-card flat>
                <v-card-text class="pa-0 pt-7">
                    <v-row no-gutters>
                        <v-col cols="12" sm="6" class="d-flex">
                            <v-text-field v-model="startDistance" mask="##########" solo @keyup.enter="recount" clearable />
                            <div class="mx-3 mt-1 display-1 text-center">-</div>
                            <v-text-field v-model="endDistance" mask="##########" solo @keyup.enter="recount" clearable />
                            <div class="ml-3 mt-1 headline">{{ $t("default.km") }}</div>
                        </v-col>

                        <v-col cols="8" sm="4" class="ml-sm-5">
                            <v-btn @click="recount" color="info">{{$t("stat.recount")}}</v-btn>
                            <v-btn v-if="userIsAdmin" @click="publishPost" color="error"  class="ml-3"
                                   :title="$t('stat.titlePublishButton')">
                                {{$t('stat.textPublishButton')}}
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>
        </v-tab-item>

        <v-tab-item>
            <v-card flat>
                <v-card-text class="pa-0 pt-7">
                    <v-row no-gutters>
                        <v-col cols="12" sm="6" class="d-flex">
                            <date-picker v-model="startDate" />
                            <div class="mx-3 mt-2 display-1 text-center">-</div>
                            <date-picker v-model="endDate" />
                        </v-col>

                        <v-col cols="8" sm="4" class="ml-sm-5">
                            <v-btn @click="recount" color="info">{{$t("stat.recount")}}</v-btn>
                            <v-btn v-if="userIsAdmin" @click="publishPost" color="error" class="ml-3"
                                   :title="$t('stat.titlePublishButton')">
                                {{$t('stat.textPublishButton')}}
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>
        </v-tab-item>
    </v-tabs>
</template>

<script>
    import DatePicker from "./DatePicker"
    import {statApi} from "../api"
    import {checkValue, convertStatParams, fetchHandler, stringToInt} from "../util"
    import {mapGetters} from "vuex"
    import {dateTab, distanceTab} from "../util/data"

    export default {
        components: {DatePicker},
        data() {
            const {type, startRange, endRange} = this.$route.params
            const activeTab = type === dateTab.name ? dateTab : distanceTab
            return {
                activeTabIndex: activeTab.tabIndex,
                startDistance: activeTab.isDistanceTab  ? startRange : null,
                endDistance: activeTab.isDistanceTab ? endRange : null,
                startDate: activeTab.isDateTab ? startRange : null,
                endDate: activeTab.isDateTab ? endRange : null
            }
        },
        computed: {
            ...mapGetters(["userIsAdmin"]),
            params() {
                const {activeTab} = this
                const startRange = activeTab.isDistanceTab ? stringToInt(this.startDistance) : this.startDate
                const endRange = activeTab.isDistanceTab ? stringToInt(this.endDistance) : this.endDate
                return {
                    type: activeTab.name,
                    startRange: startRange != null ? startRange : "-",
                    endRange: endRange != null ? endRange : "-"
                }
            },
            activeTab() {
                return this.activeTabIndex === 0 ? distanceTab : dateTab
            }
        },
        methods: {
            recount() {
                if (!this.checkRange()) {
                    return
                }

                this.$router.push({name: "stat", params: this.params})
            },
            publishPost() {
                if (!confirm(this.$t("stat.confirmPublish"))) {
                    return
                }

                if (!this.checkRange()) {
                    return
                }

                const params = convertStatParams(this.params)

                statApi.publishPost(params)
                    .then(({body}) => alert(this.$t("stat.successPublishPost", {id: body})))
                    .catch(fetchHandler)
            },
            checkRange() {
                const {startRange, endRange} = this.params
                if (checkValue(startRange) && checkValue(endRange) && startRange > endRange) {
                    alert(this.$t("stat.startRangeLessEndRange"))
                    return false
                }

                return true
            }
        }
    }
</script>