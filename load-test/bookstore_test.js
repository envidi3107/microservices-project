import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 5 },  // Ramp up to 5 users
    { duration: '30s', target: 20 }, // maintain 20 users
    { duration: '10s', target: 0 },  // Ramp down
  ],
};

const BASE_URL = 'http://localhost:8000'; // API Gateway

export default function () {
  // Scenario 1: Health checks (Unauthenticated)
  const healthRes = http.get(`${BASE_URL}/health/`);
  check(healthRes, { 'health status is 200': (r) => r.status === 200 });

  // Scenario 2: Register & Login (Auth Service through Gateway)
  const uniqueId = Math.random().toString(36).substring(7);
  const email = `testuser_${uniqueId}@example.com`;
  const password = 'securepassword123';

  // Register
  const regPayload = JSON.stringify({ email: email, password: password, role: 'user' });
  const regHeaders = { 'Content-Type': 'application/json' };
  const regRes = http.post(`${BASE_URL}/api/auth/register/`, regPayload, { headers: regHeaders });
  
  check(regRes, { 'registered successfully': (r) => r.status === 201 });

  // Login
  const loginPayload = JSON.stringify({ email: email, password: password });
  const loginRes = http.post(`${BASE_URL}/api/auth/login/`, loginPayload, { headers: regHeaders });
  
  check(loginRes, { 'login successful': (r) => r.status === 200 });
  
  let token = null;
  let customerId = null;
  if (loginRes.status === 200) {
    const loginBody = loginRes.json();
    token = loginBody.token;
    customerId = loginBody.user_id;
  }

  // Scenario 3: Place an order (Authenticated Flow & Saga Orchestration)
  if (token && customerId) {
    const authHeaders = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };

    const orderPayload = JSON.stringify({
      customer_id: customerId,
      total_price: "49.99",
      address: "123 Load Test Ave",
      payment_method: "Credit Card",
      shipping_method: "Express"
    });

    const orderRes = http.post(`${BASE_URL}/api/orders/`, orderPayload, { headers: authHeaders });
    
    check(orderRes, { 
       'order created successfully': (r) => r.status === 201,
       'saga completed (status=CONFIRMED)': (r) => { 
           if(r.status === 201) return r.json().status === 'CONFIRMED'; 
           return false; 
       }
    });
  }

  sleep(1);
}
