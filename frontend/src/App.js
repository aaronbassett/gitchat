import React, { useEffect, useState } from "react"

function App() {
  const [socket, setSocket] = useState(null)
  const [newMessage, setNewMessage] = useState("")
  const [messages, setMessages] = useState([])
  const [messageElements, setMessageElements] = useState(null)

  useEffect(() => {
    setSocket(new WebSocket("ws://localhost:8000/chat"))
  }, [])

  useEffect(() => {
    if (socket) {
      socket.addEventListener("open", function (event) {
        console.log("WebSocket Connected")
      })

      socket.addEventListener("close", function (event) {
        console.log("WebSocket Disconnected")
      })

      socket.addEventListener("message", function (event) {
        setMessages(JSON.parse(event.data))
      })
    }
  }, [socket])

  useEffect(() => {
    const messageCards = messages.reverse().map((message) => {
      return (
        <div class="card">
          <div class="card-content">
            <p class="subtitle">{message.author}</p>
            <p class="title is-4">{message.message}</p>
          </div>
          <footer class="card-footer">
            <p class="card-footer-item">
              <span>{message.authored_on}</span>
            </p>
          </footer>
        </div>
      )
    })

    setMessageElements(messageCards)
  }, [messages])

  function sendNewMessage() {
    socket.send(newMessage)
  }

  return (
    <>
      <div className="container mt-3">
        {messageElements}

        <footer class="footer mt-6">
          <div class="content has-text-centered">
            <textarea
              class="textarea"
              placeholder="e.g. Hello world"
              value={newMessage}
              onChange={(event) => setNewMessage(event.target.value)}
            ></textarea>

            <button onClick={sendNewMessage}>Send Message</button>
          </div>
        </footer>
      </div>
    </>
  )
}

export default App
