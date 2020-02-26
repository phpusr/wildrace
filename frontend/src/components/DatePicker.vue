<template>
    <v-menu
            :close-on-content-click="false"
            v-model="menu"
            :nudge-right="40"
            lazy
            transition="scale-transition"
            offset-y
            full-width
            min-width="290px"
    >
        <v-text-field
                slot="activator"
                :value="viewFormattedDate"
                :label="label"
                prepend-icon="event"
                readonly
                clearable
                @click:clear="$emit('input')"
        />
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