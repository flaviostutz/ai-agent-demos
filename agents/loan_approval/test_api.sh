#!/bin/bash

# Sample Loan Approval API Test Script
# This script demonstrates how to test the loan approval API with a sample request

API_URL="${API_URL:-http://localhost:8000}"
SAMPLE_FILE="${1:-agents/loan_approval/datasets/sample_approved_request.json}"

echo "Testing Loan Approval API"
echo "========================="
echo ""
echo "API URL: $API_URL"
echo "Sample Request: $SAMPLE_FILE"
echo ""

# Check if API is running
echo "Checking API health..."
curl -s "${API_URL}/health" | jq '.'
echo ""

# Submit loan request
echo "Submitting loan application..."
echo ""
curl -X POST "${API_URL}/api/v1/loan/evaluate" \
  -H "Content-Type: application/json" \
  -d @"$SAMPLE_FILE" \
  | jq '.'

echo ""
echo "Test complete!"
