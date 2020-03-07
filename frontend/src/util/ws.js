let connected = false
const handlers = []

export function connectToWS(store) {
    const socket = new WebSocket(`ws://${window.location.host}/ws/wild-race/`)

    socket.onopen = () => {
        connected = true
        store.commit("setWebSocketStatusMutation", {connected})
    }

    socket.onmessage = message => {
        const data = JSON.parse(message.data)
        handlers.forEach(h => {
            if (data.type ===  h.type) {
                h.handler(data)
            }
        })
    }

    socket.onerror = socketFail.bind(null, store, "error")
    socket.onclose = socketFail.bind(null, store, "close")
}

function socketFail(store, cause) {
    console.error("Web Socket", cause)
    connected = false
    store.commit("setWebSocketStatusMutation", {connected})
}

export function addHandler(type, handler) {
    handlers.push({ type, handler })
}
