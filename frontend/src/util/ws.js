import ReconnectingWebSocket from "ReconnectingWebSocket"

const handlers = []

export function connectToWebSocket(store) {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws"
    const socket = new ReconnectingWebSocket(`${protocol}://${window.location.host}/ws/wild-race/`)

    socket.onopen = () => {
        store.commit("setWebSocketStatusMutation", {connected: true})
    }

    socket.onmessage = message => {
        const data = JSON.parse(message.data)
        handlers.forEach(h => {
            if (data.type ===  h.type) {
                h.handler(data)
            }
        })
    }

    socket.onclose = () => {
        store.commit("setWebSocketStatusMutation", {connected: false})
    }
}

export function addHandler(type, handler) {
    handlers.push({ type, handler })
}
