#!/usr/bin/env node

/**
 * Test script for frontend integration with the hackathon agent
 * Run with: node test_frontend_integration.js
 */

const https = require('https');

class AgentTester {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.sessionId = null;
    this.userId = 'test_user_' + Math.random().toString(36).substr(2, 9);
  }

  async makeRequest(path, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(path, this.baseUrl);
      const options = {
        hostname: url.hostname,
        port: url.port || 443,
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
          'User-Agent': 'AgentTester/1.0'
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            resolve({ status: res.statusCode, data: jsonData });
          } catch (e) {
            resolve({ status: res.statusCode, data: data });
          }
        });
      });

      req.on('error', (err) => {
        reject(err);
      });

      if (body) {
        req.write(JSON.stringify(body));
      }
      req.end();
    });
  }

  async testHealth() {
    console.log('🔍 Testing health endpoint...');
    try {
      const response = await this.makeRequest('/health');
      console.log(`✅ Health check: ${response.status} - ${JSON.stringify(response.data)}`);
      return response.status === 200;
    } catch (error) {
      console.log(`❌ Health check failed: ${error.message}`);
      return false;
    }
  }

  async createSession() {
    console.log('🔍 Creating session...');
    try {
      const response = await this.makeRequest(
        `/apps/hackathon_agent/users/${this.userId}/sessions`,
        'POST',
        {}
      );
      
      if (response.status === 200) {
        this.sessionId = response.data.id;
        console.log(`✅ Session created: ${this.sessionId}`);
        return true;
      } else {
        console.log(`❌ Session creation failed: ${response.status} - ${JSON.stringify(response.data)}`);
        return false;
      }
    } catch (error) {
      console.log(`❌ Session creation error: ${error.message}`);
      return false;
    }
  }

  async sendMessage(message) {
    if (!this.sessionId) {
      console.log('❌ No session ID available');
      return false;
    }

    console.log(`🔍 Sending message: "${message}"`);
    try {
      const response = await this.makeRequest('/run', 'POST', {
        appName: 'hackathon_agent',
        userId: this.userId,
        sessionId: this.sessionId,
        newMessage: {
          parts: [{ text: message }]
        }
      });

      if (response.status === 200) {
        console.log(`✅ Message sent successfully`);
        console.log(`📝 Response: ${JSON.stringify(response.data, null, 2)}`);
        return true;
      } else {
        console.log(`❌ Message sending failed: ${response.status} - ${JSON.stringify(response.data)}`);
        return false;
      }
    } catch (error) {
      console.log(`❌ Message sending error: ${error.message}`);
      return false;
    }
  }

  async runTests() {
    console.log('🚀 Starting agent integration tests...\n');
    
    // Test 1: Health check
    const healthOk = await this.testHealth();
    if (!healthOk) {
      console.log('❌ Health check failed, stopping tests');
      return;
    }
    console.log('');

    // Test 2: Create session
    const sessionOk = await this.createSession();
    if (!sessionOk) {
      console.log('❌ Session creation failed, stopping tests');
      return;
    }
    console.log('');

    // Test 3: Send simple message
    await this.sendMessage('Hello, what can you help me with?');
    console.log('');

    // Test 4: Send restaurant inquiry
    await this.sendMessage('What restaurants are available for delivery?');
    console.log('');

    // Test 5: Send code generation request
    await this.sendMessage('Generate a Python function to calculate fibonacci numbers');
    console.log('');

    console.log('🎉 Tests completed!');
  }
}

// Main execution
async function main() {
  const baseUrl = 'https://hackathon-agent-655406354323.europe-west1.run.app';
  
  // Get token from environment or prompt user
  let token = process.env.GOOGLE_TOKEN;
  if (!token) {
    console.log('⚠️  No GOOGLE_TOKEN environment variable found.');
    console.log('Please set it with: export GOOGLE_TOKEN=$(gcloud auth print-identity-token)');
    console.log('Or run: GOOGLE_TOKEN=$(gcloud auth print-identity-token) node test_frontend_integration.js\n');
    return;
  }

  const tester = new AgentTester(baseUrl, token);
  await tester.runTests();
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { AgentTester }; 