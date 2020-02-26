<template>
    <span v-if="number">
        <profile-link v-bind="profile" />
        <span> - {{ numberOfRuns }}</span>
        <span> {{ $t("default.trainings") }}</span>
    </span>
    <span v-else>
        <profile-link v-bind="profile" />
        <span> - {{ sumDistance }}</span>
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
            sumDistance: Number,
            numberOfRuns: Number
        }
    }
</script>