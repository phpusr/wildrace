<template>
    <v-layout>
        <v-flex>
            <v-tabs v-model="activeTabIndex" color="cyan" dark slider-color="yellow">
                <v-tab ripple>{{ $t("stat.distanceRange") }}</v-tab>
                <v-tab ripple>{{ $t("stat.dateRange") }}</v-tab>

                <v-tab-item>
                    <v-card flat>
                        <v-card-text>
                            <v-layout wrap>
                                <v-flex xs5 sm3>
                                    <v-text-field v-model="startDistance" mask="##########" solo @keyup.enter="recount" clearable />
                                </v-flex>

                                <v-flex xs1>
                                    <div class="mt-1 display-1 text-xs-center">-</div>
                                </v-flex>

                                <v-flex xs5 sm3>
                                    <v-text-field v-model="endDistance" mask="##########" solo @keyup.enter="recount" clearable />
                                </v-flex>

                                <v-flex xs1>
                                    <div class="ml-2 mt-2 headline">{{ $t("default.km") }}</div>
                                </v-flex>

                                <v-flex xs4 sm2>
                                    <v-btn @click="recount" color="info">{{$t("stat.recount")}}</v-btn>
                                </v-flex>

                                <v-flex xs4 sm2>
                                    <v-btn v-if="userIsAdmin" @click="publishPost" color="error"
                                           :title="$t('stat.titlePublishButton')">
                                        {{$t('stat.textPublishButton')}}
                                    </v-btn>
                                </v-flex>
                            </v-layout>
                        </v-card-text>
                    </v-card>
                </v-tab-item>

                <v-tab-item>
                    <v-card flat>
                        <v-card-text>
                            <v-layout wrap>
                                <v-flex xs5 sm3>
                                    <date-picker v-model="startDate" />
                                </v-flex>

                                <v-flex xs1>
                                    <div class="mt-2 display-1 text-xs-center">-</div>
                                </v-flex>

                                <v-flex xs5 sm3>
                                    <date-picker v-model="endDate" />
                                </v-flex>

                                <v-flex xs4 sm2>
                                    <v-btn @click="recount" color="info">{{$t("stat.recount")}}</v-btn>
                                </v-flex>

                                <v-flex xs4 sm2>
                                    <v-btn v-if="userIsAdmin" @click="publishPost" color="error"
                                           :title="$t('stat.titlePublishButton')">
                                        {{$t('stat.textPublishButton')}}
                                    </v-btn>
                                </v-flex>
                            </v-layout>
                        </v-card-text>
                    </v-card>
                </v-tab-item>
            </v-tabs>
        </v-flex>
    </v-layout>
</template>

<script>
    import DatePicker from "./DatePicker"
    import statApi from "../api/stat"
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