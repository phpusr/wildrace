<template>
    <v-col md="10">
        <stat-filter />

        <v-row>
            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.topIntervalRunners')">
                    <ol>
                        <li v-for="r in stat.topIntervalRunners" :key="r.id">
                            <runner-value v-bind="r" />
                        </li>
                    </ol>
                </stat-card>
            </v-col>

            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.topAllRunners')">
                    <ol>
                        <li v-for="r in stat.topAllRunners" :key="r.id">
                            <runner-value v-bind="r" />
                        </li>
                    </ol>
                </stat-card>
            </v-col>

            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.daysCount')">
                    <div>- {{ $t("stat.daysCountAll") }} - {{ stat.allDaysCount }} {{ $t("default.days") }}</div>
                    <div>- {{ $t("stat.daysCountInterval") }} - {{ stat.intervalDaysCount }} {{ $t("default.days") }}</div>
                </stat-card>
            </v-col>

            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.distance')">
                    <div>- {{ $t("stat.distancePerDayAvg") }} - {{ stat.distancePerDay.toFixed(1) }} {{ $t("default.kmPerDay") }}</div>
                    <div>- {{ $t("stat.distancePerTrainingAvg") }} - {{ stat.distancePerTraining.toFixed(1) }} {{ $t("default.kmPerTraining") }}</div>
                    <div>- {{ $t("stat.distanceMaxOneMan") }} - <runner-value v-bind="stat.maxOneManDistance" /></div>
                </stat-card>
            </v-col>

            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.runners')">
                    <div>- {{ $t("stat.runnersCountAll") }} - {{ stat.allRunnersCount }} {{ $t("default.people") }}</div>
                    <div>- {{ $t("stat.runnersCountInterval") }} - {{ stat.intervalRunnersCount }} {{ $t("default.peoplePerDay") }}</div>
                    <div>
                        <span>- {{ $t("stat.newRunners") }} - {{ stat.newRunnersCount }} {{ $t("default.people") }} {{ "(" }}</span>
                        <span v-for="(r, index) in stat.newRunners" :key="r.id">
                                <profile-link v-bind="r" />
                                <span v-if="index < stat.newRunners.length - 1">, </span>
                            </span>
                        <span v-if="stat.newRunners.length < stat.newRunnersCount"> ...</span>
                        {{ ")" }}
                    </div>
                </stat-card>
            </v-col>

            <v-col cols="12" sm="6">
                <stat-card :title="$t('stat.trainings')">
                    <div>- {{ $t("stat.trainingCountAll") }} - {{ stat.allTrainingCount }} {{ $t("default.trainings") }}</div>
                    <div>- {{ $t("stat.trainingCountPerDayAvgFunction") }} - {{ stat.trainingCountPerDay.toFixed(1) }} {{ $t("default.trainingsPerDay") }}</div>
                    <div>- {{ $t("stat.trainingMaxOneMan") }} - <runner-value v-bind="stat.maxOneManTrainingCount" number /></div>
                </stat-card>
            </v-col>
        </v-row>
    </v-col>
</template>

<script>
    import StatFilter from "../components/StatFilter"
    import StatCard from "../components/StatCard"
    import ProfileLink from "../components/ProfileLink"
    import RunnerValue from "../components/RunnerValue"
    import {statApi} from "../api"
    import {convertStatParams} from "../util"

    export default {
        components: {StatFilter, StatCard, ProfileLink, RunnerValue},
        data: () => ({
            stat: {
                distancePerDay: 0.0,
                distancePerTraining: 0.0,
                trainingCountPerDay: 0.0,
                newRunners: []
            }
        }),
        methods: {
            async fetchData() {
                const params = convertStatParams(this.$route.params)
                const {body} = await statApi.get(params)
                this.stat = body
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