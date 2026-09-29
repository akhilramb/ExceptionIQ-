from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_create_and_investigate_exception():
    payload = {
        'vendor': 'NovaTech Solutions',
        'invoice_number': 'TEST-INV-001',
        'po_number': 'TEST-PO-001',
        'invoice_amount': 106500,
        'po_amount': 100000,
        'exception_type': 'Invoice Amount Mismatch',
        'description': 'Automated workflow test',
    }
    created = client.post('/api/exceptions', json=payload)
    assert created.status_code == 201
    item = created.json()['data']
    assert item['difference'] == 6500

    investigated = client.post('/api/investigate', json={
        **payload,
        'difference': item['difference'],
    })
    assert investigated.status_code == 200
    result = investigated.json()
    assert 'recommendation' in result
    assert result['recommendation']['confidence'] <= 95
    assert isinstance(result['similar_memories'], list)


def test_memory_endpoint_shape():
    response = client.get('/api/memories')
    assert response.status_code == 200
    assert isinstance(response.json()['data'], list)
