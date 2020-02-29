<template>
    <v-menu
            :close-on-content-click="false"
            v-model="menu"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="290px"
    >
        <template v-slot:activator="{ on }">
            <v-text-field
                    v-on="on"
                    :value="viewFormattedDate"
                    :label="label"
                    prepend-icon="mdi-calendar"
                    readonly
                    clearable
                    @click:clear="$emit('input')"
            />
        </template>
        <v-date-picker
                :value="isoFormattedDate"
                @input="input"
                no-title scrollable
                first-day-of-week="1"
        />
    </v-menu>
</template>

<script>
    import dateFormat from "date-format"

    export default {
        data: () => ({
            menu: false
        }),
        props: {
            value: [Number, String],
            label: String,
            number: Boolean
        },
        computed: {
            viewFormattedDate() {
                if (!this.value || this.value === "-") {
                    return null
                }

                return dateFormat(this.$t("default.datePattern"), this.dateObject)
            },
            isoFormattedDate() {
                if (!this.value || this.value === "-") {
                    return null
                }

                return dateFormat(this.$t("default.isoDatePattern"), this.dateObject)
            },
            dateObject() {
                return this.number ? new Date(this.value) : this.parseIsoDateString(this.value)
            }
        },
        methods: {
            input(inputIsoDateString) {
                const returnDate = this.number ? this.parseIsoDateString(inputIsoDateString).getTime() : inputIsoDateString
                this.$emit("input", returnDate)
                this.menu = false
            },
            parseIsoDateString(dateString) {
                return new Date(dateString + "T00:00:00")
            }
        }
    }
</script>