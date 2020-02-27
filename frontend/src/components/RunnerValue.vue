<template>
    <span v-if="number">
        <profile-link v-bind="profile" />
        <span> - {{ runningCount }}</span>
        <span> {{ $t("default.trainings") }}</span>
    </span>
    <span v-else>
        <profile-link v-bind="profile" />
        <span> - {{ distanceSum }}</span>
        <span> {{ $t("default.km") }}</span>
    </span>
</template>

<script>
    import ProfileLink from "./ProfileLink"

    export default {
        components: {ProfileLink},
        props: {
            number: Boolean,
            profile: Object,
            distanceSum: Number,
            runningCount: Number
        }
    }
</script>