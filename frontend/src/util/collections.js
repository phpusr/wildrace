
export function replaceObject(list, object) {
    const index = list.findIndex(el => el.id === object.id)
    if (index > -1) {
        list.splice(index, 1, object)
    }
}

export function deleteObject(list, id) {
    const index = list.findIndex(el => el.id === id)
    if (index > -1) {
        list.splice(index, 1)
        return true
    }

    return false
}

/**
 * src: https://stackoverflow.com/questions/4994201/is-object-empty
 */
export function isEmptyObject(obj) {
    if (obj == null) return true

    if (obj.length > 0) return false
    if (obj.length === 0) return true

    if (typeof obj !== "object") return true

    for (const key in obj) {
        if (hasOwnProperty.call(obj, key)) return false
    }

    return true
}