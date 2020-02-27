import {addHandler} from "./ws"
import {mapMutations} from "vuex"
import {isEmptyObject} from "./collections"

export const methods = mapMutations(["addPostMutation", "updatePostMutation", "removePostMutation",
    "updatePostStatMutation", "updateLastSyncDateMutation"])

export function activityHandler(component) {
    addHandler("/topic/activity", data => {
        const body = data.body
        if (data.objectType === "Post") {
            switch(data.eventType) {
                case "Create":
                    if (isEmptyObject(component.$route.query)) {
                        component.addPostMutation(body)
                    }
                    break
                case "Update":
                    component.updatePostMutation(body)
                    break
                case "Remove":
                    component.removePostMutation(body.id)
                    break
                default:
                    throw new Error(`Looks like the event type is unknown: "${data.eventType}"`)
            }
        } else if (data.objectType === "Stat") {
            component.updatePostStatMutation(body)
        } else if (data.objectType === "LastSyncDate") {
            component.updateLastSyncDateMutation(body)
        } else {
            throw new Error(`Looks like the object type is unknown: "${data.objectType}"`)
        }
    })
}