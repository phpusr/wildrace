<template>
    <v-row class="root" align="" align-content="center" justify="space-around">
        <v-col cols="3" v-for="i in 10" :key="i">
            <v-card height="100%" outlined tile>
                <v-card-title>Test {{ i }}</v-card-title>
                <v-card-subtitle>Subtitle</v-card-subtitle>
                <v-card-text>Text</v-card-text>
                <v-card-actions>
                    <v-btn>OK</v-btn>
                </v-card-actions>
            </v-card>
        </v-col>
    </v-row>
</template>

<script>
    export default {

        data: () => ({
        }),

        methods: {

        }
    }
</script>

<style>
    .root {
        height: 500px;
        background: #eee;
    }
</style>