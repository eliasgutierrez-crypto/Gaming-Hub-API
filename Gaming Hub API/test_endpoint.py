from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.post('/users/', json={
    'username': 'testuser123',
    'email': 'test123@example.com',
    'password': 'Test@1234'
})

print(f'Status: {response.status_code}')
print(f'Response: {response.text[:500]}')
if response.status_code != 200 and response.status_code != 201:
    print('ERROR')
    import traceback
    if response.status_code == 422:
        print('Validation error:', response.json())
