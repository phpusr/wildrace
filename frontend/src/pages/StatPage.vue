<template>
    <v-flex md10>
        <stat-filter />

        <v-container v-bind="containerConfig" class="my-3 pa-0">
            <v-layout wrap>
                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.topIntervalRunners')">
                        <ol>
                            <li v-for="r in stat.topIntervalRunners" :key="r.id">
                                <runner-value v-bind="r" />
                            </li>
                        </ol>
                    </stat-card>
                </v-flex>

                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.topAllRunners')">
                        <ol>
                            <li v-for="r in stat.topAllRunners" :key="r.id">
                                <runner-value v-bind="r" />
                            </li>
                        </ol>
                    </stat-card>
                </v-flex>

                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.daysCount')">
                        <div>- {{ $t("stat.daysCountAll") }} - {{ stat.daysCountAll }} {{ $t("default.days") }}</div>
                        <div>- {{ $t("stat.daysCountInterval") }} - {{ stat.daysCountInterval }} {{ $t("default.days") }}</div>
                    </stat-card>
                </v-flex>

                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.distance')">
                        <div>- {{ $t("stat.distancePerDayAvg") }} - {{ stat.distancePerDayAvg.toFixed(1) }} {{ $t("default.kmPerDay") }}</div>
                        <div>- {{ $t("stat.distancePerTrainingAvg") }} - {{ stat.distancePerTrainingAvg.toFixed(1) }} {{ $t("default.kmPerTraining") }}</div>
                        <div>- {{ $t("stat.distanceMaxOneMan") }} - <runner-value v-bind="stat.distanceMaxOneMan" /></div>
                    </stat-card>
                </v-flex>

                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.runners')">
                        <div>- {{ $t("stat.runnersCountAll") }} - {{ stat.runnersCountAll }} {{ $t("default.people") }}</div>
                        <div>- {{ $t("stat.runnersCountInterval") }} - {{ stat.runnersCountInterval }} {{ $t("default.peoplePerDay") }}</div>
                        <div>
                            <span>- {{ $t("stat.newRunners") }} - {{ stat.countNewRunners }} {{ $t("default.people") }} {{ "(" }}</span>
                            <span v-for="(r, index) in stat.newRunners" :key="r.id">
                                <profile-link v-bind="r" />
                                <span v-if="index < stat.newRunners.length - 1">, </span>
                            </span>
                            <span v-if="stat.newRunners.length < stat.countNewRunners"> ...</span>
                            {{ ")" }}
                        </div>
                    </stat-card>
                </v-flex>

                <v-flex d-flex sm6 xs12>
                    <stat-card :title="$t('stat.trainings')">
                        <div>- {{ $t("stat.trainingCountAll") }} - {{ stat.trainingCountAll }} {{ $t("default.trainings") }}</div>
                        <div>- {{ $t("stat.trainingCountPerDayAvgFunction") }} - {{ stat.trainingCountPerDayAvg.toFixed(1) }} {{ $t("default.trainingsPerDay") }}</div>
                        <div>- {{ $t("stat.trainingMaxOneMan") }} - <runner-value v-bind="stat.trainingMaxOneMan" number /></div>
                    </stat-card>
                </v-flex>

            </v-layout>
        </v-container>
    </v-flex>
</template>

<script>
    import StatFilter from "../components/StatFilter"
    import StatCard from "../components/StatCard"
    import ProfileLink from "../components/ProfileLink"
    import RunnerValue from "../components/RunnerValue"
    import statApi from "../api/stat"
    import {convertStatParams, fetchHandler} from "../util"

    export default {
        components: {StatFilter, StatCard, ProfileLink, RunnerValue},
        data: () => ({
            stat: {
                distancePerDayAvg: 0.0,
                distancePerTrainingAvg: 0.0,
                trainingCountPerDayAvg: 0.0,
                newRunners: []
            }
        }),
        computed: {
            containerConfig() {
                return {
                    ["grid-list-" + this.$vuetify.breakpoint.name]: true
                }
            }
        },
        methods: {
            async fetchData() {
                const params = convertStatParams(this.$route.params)
                statApi.get(params)
                    .then(({body}) => this.stat = body)
                    .catch(fetchHandler)
            }
        },
        created() {
            this.fetchData()
        },
        beforeRouteUpdate (to, from, next) {
            next()

            this.fetchData()
        }
    }
</script>