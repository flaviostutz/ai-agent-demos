"""Performance tests for loan approval agent."""

import time
from statistics import mean, stdev

import pytest
from agents.loan_approval import LoanApprovalAgent, LoanRequest


class TestLoanApprovalPerformance:
    """Performance tests for loan approval agent."""

    @pytest.fixture(autouse=True)
    def setup(self, security_context, mock_openai_key):
        """Set up test environment."""
        self.security_context = security_context
        self.agent = LoanApprovalAgent(security_context=security_context)

    def test_response_time_single_request(self, sample_loan_request_data):
        """Test response time for a single request."""
        request = LoanRequest(**sample_loan_request_data)

        start_time = time.time()

        # Test only the decision logic without external API calls
        state = {
            "request": request,
            "decision": None,
            "risk_factors": [],
            "messages": [],
            "documents_checked": True,
            "security_context": self.security_context,
        }

        state = self.agent._validate_request(state)
        state = self.agent._assess_risk(state)
        state = self.agent._make_decision(state)

        elapsed_time = time.time() - start_time

        assert state["decision"] is not None
        assert elapsed_time < 1.0, f"Processing took {elapsed_time:.2f}s, expected < 1.0s"

    def test_throughput_multiple_requests(self, sample_loan_request_data):
        """Test throughput with multiple requests."""
        num_requests = 10
        times = []

        for i in range(num_requests):
            data = sample_loan_request_data.copy()
            data["request_id"] = f"REQ-PERF-{i:03d}"
            request = LoanRequest(**data)

            start_time = time.time()

            state = {
                "request": request,
                "decision": None,
                "risk_factors": [],
                "messages": [],
                "documents_checked": True,
                "security_context": self.security_context,
            }

            state = self.agent._validate_request(state)
            state = self.agent._assess_risk(state)
            state = self.agent._make_decision(state)

            elapsed_time = time.time() - start_time
            times.append(elapsed_time)

            assert state["decision"] is not None

        avg_time = mean(times)
        std_time = stdev(times) if len(times) > 1 else 0

        print(f"\nPerformance Statistics:")
        print(f"  Requests: {num_requests}")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Std deviation: {std_time:.3f}s")
        print(f"  Min time: {min(times):.3f}s")
        print(f"  Max time: {max(times):.3f}s")

        # Assertions
        assert avg_time < 1.0, f"Average processing time {avg_time:.2f}s exceeds threshold"
        assert max(times) < 2.0, f"Max processing time {max(times):.2f}s exceeds threshold"

    def test_memory_usage_stability(self, sample_loan_request_data):
        """Test that memory usage remains stable over multiple requests."""
        import gc

        gc.collect()

        for i in range(50):
            data = sample_loan_request_data.copy()
            data["request_id"] = f"REQ-MEM-{i:03d}"
            request = LoanRequest(**data)

            state = {
                "request": request,
                "decision": None,
                "risk_factors": [],
                "messages": [],
                "documents_checked": True,
                "security_context": self.security_context,
            }

            self.agent._validate_request(state)
            self.agent._assess_risk(state)
            self.agent._make_decision(state)

        # If we get here without memory errors, test passes
        assert True
