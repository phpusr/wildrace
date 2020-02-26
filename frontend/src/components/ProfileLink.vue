<template>
    <a :href="vkLink">{{ firstName }} {{ lastName }}</a>
</template>

<script>
    export default {
        props: {
            vkLink: String,
            firstName: String,
            lastName: String
        }
    }
</script>