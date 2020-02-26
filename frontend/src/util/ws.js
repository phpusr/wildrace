import SockJS from "sockjs-client"
import {Stomp} from "@stomp/stompjs"

let stompClient = null
let connected = false
const handlers = []
const messages = []

export function connectToWS() {
    const socket = new SockJS("/wild-race-ws")
    stompClient = Stomp.over(socket)
    stompClient.debug = () => {}
    stompClient.connect({}, () => {
        connected = true
        handlers.forEach(h => stompClient.subscribe(h.id, message =>
            h.handler(JSON.parse(message.body))
        ))
        handlers.splice(0, handlers.length)
        messages.forEach(m => stompClient.send(m.action, m.json))
        messages.splice(0, messages.length)

        socket.onerror = socketFail.bind(this, "Error")
        socket.onclose = socketFail.bind(this, "Close")
    })
}

function socketFail(cause) {
    connected = false
    if (confirm(`${cause} connect to ws. Reload page?`)) {
        location.reload()
    }
}

export function addHandler(id, handler) {
    if (connected) {
        stompClient.subscribe(id, message =>
            handler(JSON.parse(message.body))
        )
        return
    }

    handlers.push({ id, handler })
}

export function disconnect() {
    if (stompClient !== null && connected) {
        stompClient.disconnect()
    }
}

export function sendData(action, object) {
    if (connected) {
        stompClient.send(action, {}, JSON.stringify(object))
        return
    }

    messages.push({ action, json: JSON.stringify(object) })
}
