let connected = false
const handlers = []

export function connectToWS() {
    const socket = new WebSocket("ws://localhost:8000/ws/wild-race/")

    socket.onopen = event => {
        connected = true
        console.log("WebSocket open", event, connected)
    }

    socket.onmessage = message => {
        const data = JSON.parse(message.data)
        console.log('message', data)
        handlers.forEach(h => h.handler(data))
    }

    socket.onerror = socketFail.bind(null, "Error")
    socket.onclose = socketFail.bind(null, "Close")
}

function socketFail(cause) {
    console.log('socket', cause)
    connected = false
    //TODO
    // if (confirm(`${cause} connect to ws. Reload page?`)) {
    //     location.reload()
    // }
}

export function addHandler(id, handler) {
    handlers.push({ id, handler })
}
