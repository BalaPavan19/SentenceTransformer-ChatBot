import React, { useState } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse('');
    
    if (!input.trim()) {
      setResponse('Please enter a question.');
      return;
    }

    setLoading(true); // Start loading

    try {
      const res = await fetch('http://127.0.0.1:5001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }), // Corrected to 'query'
      });

      if (!res.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await res.json();
      setResponse(data.answer); // Corrected response key
    } catch (error) {
      setResponse('Error: ' + error.message); // Display error message
    } finally {
      setLoading(false); // Stop loading
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything!"
          />
          <button type="submit">Send</button>
        </form>
        <div>
          <h2>Response:</h2>
          {loading ? <p className="loading">Loading...</p> : <p>{response}</p>}
        </div>
      </header>
    </div>
  );
}

export default App;
