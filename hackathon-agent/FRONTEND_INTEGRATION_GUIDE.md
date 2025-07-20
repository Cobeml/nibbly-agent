# Frontend Integration Guide for Hackathon Agent

## Overview
Your agent is deployed at: `https://hackathon-agent-655406354323.europe-west1.run.app`

## API Endpoints

### 1. Health Check
```bash
GET https://hackathon-agent-655406354323.europe-west1.run.app/health
```
**Response**: `{"status":"healthy","service":"hackathon-agent"}`

### 2. Create Session
```bash
POST https://hackathon-agent-io2nn6gusq-ew.a.run.app/apps/{app_name}/users/{user_id}/sessions
```

**Example**:
```bash
curl -H "Authorization: Bearer ${TOKEN}" \
  -X POST "https://hackathon-agent-655406354323.europe-west1.run.app/apps/hackathon_agent/users/test_user/sessions" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response**:
```json
{
  "id": "600563ed-ffd2-4599-996b-fbe5c40dd86e",
  "appName": "snack_bot",
  "userId": "test_user",
  "state": {},
  "events": [],
  "lastUpdateTime": 1753006917.1904538
}
```

### 3. Send Message to Agent
```bash
POST https://hackathon-agent-io2nn6gusq-ew.a.run.app/run
```

**Request Body**:
```json
{
  "appName": "hackathon_agent",
  "userId": "test_user",
  "sessionId": "600563ed-ffd2-4599-996b-fbe5c40dd86e",
  "newMessage": {
    "parts": [
      {
        "text": "What restaurants are available for delivery?"
      }
    ]
  }
}
```

## JavaScript/TypeScript Integration

### 1. Basic Integration
```javascript
class AgentClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.sessionId = null;
    this.userId = 'user_' + Math.random().toString(36).substr(2, 9);
  }

  async createSession() {
    const response = await fetch(
      `${this.baseUrl}/apps/snack_bot/users/${this.userId}/sessions`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      }
    );
    
    const session = await response.json();
    this.sessionId = session.id;
    return session;
  }

  async sendMessage(message) {
    if (!this.sessionId) {
      await this.createSession();
    }

    const response = await fetch(`${this.baseUrl}/run`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
              body: JSON.stringify({
          appName: 'hackathon_agent',
          userId: this.userId,
          sessionId: this.sessionId,
          newMessage: {
            parts: [{ text: message }]
          }
        })
    });

    return await response.json();
  }
}
```

### 2. React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useAgent = (baseUrl, token) => {
  const [sessionId, setSessionId] = useState(null);
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createSession = async () => {
    try {
      const response = await fetch(
        `${baseUrl}/apps/snack_bot/users/${userId}/sessions`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({})
        }
      );
      
      const session = await response.json();
      setSessionId(session.id);
      return session;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const sendMessage = async (message) => {
    setLoading(true);
    setError(null);
    
    try {
      if (!sessionId) {
        await createSession();
      }

      const response = await fetch(`${baseUrl}/run`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          appName: 'snack_bot',
          userId: userId,
          sessionId: sessionId,
          newMessage: {
            parts: [{ text: message }]
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setLoading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  return { sendMessage, loading, error, sessionId };
};
```

### 3. React Component Example
```jsx
import React, { useState } from 'react';
import { useAgent } from './useAgent';

const AgentChat = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const { sendMessage, loading, error } = useAgent(
    'https://hackathon-agent-655406354323.europe-west1.run.app',
    'YOUR_TOKEN_HERE'
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');

    try {
      const response = await sendMessage(message);
      
      // Add agent response
      const agentMessage = { 
        role: 'agent', 
        content: response[0]?.content?.parts?.[0]?.text || 'No response' 
      };
      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Agent'}:</strong> {msg.content}
          </div>
        ))}
        {loading && <div className="message agent">Thinking...</div>}
        {error && <div className="message error">Error: {error}</div>}
      </div>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !message.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};
```

## Authentication

### 1. Get Google Cloud Token
```bash
# Get authentication token
TOKEN=$(gcloud auth print-identity-token)
```

### 2. Frontend Token Management
For production, you should:
1. Set up a backend service to proxy requests
2. Use service-to-service authentication
3. Implement proper session management

## Troubleshooting

### Common Issues

1. **"Session not found"**
   - Create a session first using the sessions endpoint
   - Use the returned session ID in subsequent requests

2. **"Internal Server Error"**
   - Check if environment variables are set in Cloud Run
   - Verify GEMMA_URL is configured
   - Check Cloud Run logs for detailed error messages

3. **Authentication Errors**
   - Ensure you're using a valid Google Cloud token
   - Check if the service allows unauthenticated access

### Environment Variables Required
Make sure these are set in your Cloud Run deployment:
- `GEMMA_URL`: URL to your Gemma model
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `GOOGLE_CLOUD_LOCATION`: Your Google Cloud location
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to "true"

### Debugging Steps
1. Check service health: `GET /health`
2. Verify session creation: `POST /apps/snack_bot/users/{user_id}/sessions`
3. Test with simple message: `POST /run` with "Hello"
4. Check Cloud Run logs for detailed errors

## Agent Capabilities

Your agent can:
1. **Answer questions** using the Gemma model
2. **Generate code** in various programming languages
3. **Brainstorm ideas** for projects
4. **Explain concepts** at different complexity levels
5. **Get restaurant options** from your ROS2 backend
6. **Create delivery orders** via ROS2 WebSocket
7. **Track order status** in real-time

## Example Conversations

### Restaurant Inquiry
```
User: "What restaurants are available for delivery?"
Agent: [Will call get_restaurant_options() and return available restaurants]
```

### Order Creation
```
User: "I want to order a pizza from Joe's Pizza"
Agent: [Will help create a delivery order using create_delivery_order()]
```

### Code Generation
```
User: "Generate a Python function to calculate fibonacci numbers"
Agent: [Will call generate_code() and return the code with explanation]
```

## Next Steps

1. **Test the API endpoints** using the provided examples
2. **Implement the frontend integration** using the JavaScript examples
3. **Set up proper authentication** for production use
4. **Add error handling** and retry logic
5. **Implement streaming responses** if needed (use `/run_sse` endpoint)

## Support

If you encounter issues:
1. Check the Cloud Run logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test with the health endpoint first
4. Ensure your Google Cloud project has the necessary permissions 