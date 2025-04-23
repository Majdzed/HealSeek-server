const WebSocket = require('ws'); // Import the WebSocket library
console.log("jjjjjjjjjjjjjjj")

const userId = 890590; // Replace with the desired user ID
try {
    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${userId}`);
    
socket.onopen = () => {
    console.log("Connected to WebSocket");
    // Send a message to the server (optional)
    socket.send(JSON.stringify({ message: "Hello from client!" }));
    socket.onmessage = (event) => {
        console.log("Received notification:", event.data);
    };
    
    socket.onclose = () => {
        console.log("WebSocket connection closed");
    };
    
    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
};
} catch (error) {
    console.log(error.message)
}




