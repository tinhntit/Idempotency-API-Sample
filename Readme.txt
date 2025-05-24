curl -X POST http://localhost:4000/generate-token \
  -H "Content-Type: application/json" \
  -d '{"username": "tinker", "password": "tyme-test"}'

curl -X POST http://localhost:4000/payment \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 11223-44556-67788-12345" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODExNDgxOCwianRpIjoiN2IyMDE0M2ItYjBkZS00ZTk5LTk5NjctNmI1YzQyNTM2ZTNkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRpbmtlcjo5Y2E0NWY5ZC1kYWJiLTQwNGItODkzMy1iZGE0YTcyNDgxZmYiLCJuYmYiOjE3NDgxMTQ4MTgsImNzcmYiOiI2MDUxODQwZi0zM2U5LTRlZjctODY1Ni1hNmYzNDIyNGE2ODEiLCJleHAiOjE3NDgxMTU0MTh9.CYIi5HeYIGCVnvBNmYOFmlsiIuFLmYaI5am3MhnTJDc"\
  -d '{"amount": 100, "account_number": "tinker-test-tyme"}'