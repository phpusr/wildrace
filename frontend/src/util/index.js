import dateFormat from "date-format"
import {dateTab, distanceTab} from "../util/data"

export function fetchHandler(e) {
    alert(`${e.status}: ${e.body.error} on "${e.url}"`)
}

export function stringToInt(str) {
    if (!checkValue(str)) {
        return null
    }

    return +str
}

export function parseJSDate(stringDate) {
    return dateFormat.parse("yyyy-MM-dd", stringDate)
}

export function checkValue(value) {
    return value != null && value !== "" && value !== "-"
}

export function convertStatParams(params) {
    const {startRange, endRange, type} = params
    const newParams = { type }
    if (type === dateTab.name) {
        newParams.type = dateTab.name
        if (checkValue(startRange)) {
            newParams.startRange = parseJSDate(startRange).getTime()
        }
        if (checkValue(endRange)) {
            newParams.endRange = parseJSDate(endRange).getTime()
        }
    } else {
        newParams.type = distanceTab.name
        if (checkValue(startRange)) {
            newParams.startRange = +startRange
        }
        if (checkValue(endRange)) {
            newParams.endRange = +endRange
        }
    }

    return newParams
}

export function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value
}