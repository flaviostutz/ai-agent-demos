# Creating New Agents

This guide walks you through creating a new AI agent from scratch.

## Quick Start

```bash
make create-agent AGENT_NAME=my_new_agent
```

This creates:
- Agent implementation skeleton (`agents/my_new_agent/`)
- FastAPI API (`agents/my_new_agent/api.py`)
- Test structure (`tests/agents/my_new_agent/`)
- Package initialization

## Step-by-Step Guide

### 1. Create Agent Structure

```bash
make create-agent AGENT_NAME=fraud_detection
```

### 2. Define Request/Response Schemas

Edit `agents/fraud_detection/agent.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime

class FraudDetectionRequest(BaseModel):
    """Request schema for fraud detection."""
    
    request_id: str = Field(description="Unique request identifier")
    transaction_id: str = Field(description="Transaction ID")
    amount: float = Field(description="Transaction amount", gt=0)
    merchant: str = Field(description="Merchant name")
    location: str = Field(description="Transaction location")
    user_id: str = Field(description="User ID")
    timestamp: datetime = Field(default_factory=datetime.now)

class FraudDetectionResponse(BaseModel):
    """Response schema for fraud detection."""
    
    request_id: str
    is_fraudulent: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_factors: list[str]
    recommended_action: str
    processed_at: datetime = Field(default_factory=datetime.now)
```

### 3. Define Agent State

```python
from typing_extensions import TypedDict
from shared.security import SecurityContext

class AgentState(TypedDict):
    """State for the fraud detection agent."""
    
    request: FraudDetectionRequest
    response: FraudDetectionResponse | None
    risk_factors: list[str]
    historical_data: dict | None
    security_context: SecurityContext
```

### 4. Implement Agent Logic

```python
from langgraph.graph import END, StateGraph
from shared.logging_utils import get_logger
from shared.metrics import get_metrics_collector
from shared.config import get_config

class FraudDetectionAgent:
    """Fraud detection agent implementation."""
    
    def __init__(self, security_context: SecurityContext):
        self.config = get_config().get_agent_config("fraud_detection")
        self.logger = get_logger(__name__, agent_id="fraud_detection")
        self.metrics = get_metrics_collector("fraud_detection")
        self.security_context = security_context
        
        # Initialize LLM if needed
        # self.llm = ChatOpenAI(...)
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("validate", self._validate_request)
        workflow.add_node("fetch_history", self._fetch_user_history)
        workflow.add_node("analyze", self._analyze_transaction)
        workflow.add_node("decide", self._make_decision)
        
        # Add edges
        workflow.set_entry_point("validate")
        workflow.add_edge("validate", "fetch_history")
        workflow.add_edge("fetch_history", "analyze")
        workflow.add_edge("analyze", "decide")
        workflow.add_edge("decide", END)
        
        return workflow.compile()
    
    def _validate_request(self, state: AgentState) -> AgentState:
        """Validate the incoming request."""
        self.logger.info(f"Validating request {state['request'].request_id}")
        
        # Add validation logic
        state["risk_factors"] = []
        return state
    
    def _fetch_user_history(self, state: AgentState) -> AgentState:
        """Fetch user transaction history."""
        self.logger.info("Fetching user history")
        
        # Fetch from database/API
        state["historical_data"] = {}
        return state
    
    def _analyze_transaction(self, state: AgentState) -> AgentState:
        """Analyze the transaction for fraud indicators."""
        self.logger.info("Analyzing transaction")
        
        request = state["request"]
        risk_factors = []
        
        # Example analysis logic
        if request.amount > 10000:
            risk_factors.append("High transaction amount")
        
        # Add more analysis...
        
        state["risk_factors"] = risk_factors
        return state
    
    def _make_decision(self, state: AgentState) -> AgentState:
        """Make final fraud decision."""
        self.logger.info("Making fraud decision")
        
        request = state["request"]
        risk_factors = state["risk_factors"]
        
        # Decision logic
        is_fraudulent = len(risk_factors) >= 3
        confidence = len(risk_factors) / 10.0
        
        if is_fraudulent:
            action = "block_transaction"
        elif risk_factors:
            action = "require_verification"
        else:
            action = "approve"
        
        state["response"] = FraudDetectionResponse(
            request_id=request.request_id,
            is_fraudulent=is_fraudulent,
            confidence_score=min(confidence, 1.0),
            risk_factors=risk_factors,
            recommended_action=action,
        )
        
        return state
    
    def process_request(
        self, 
        request: FraudDetectionRequest
    ) -> FraudDetectionResponse:
        """Process a fraud detection request."""
        self.logger.info(f"Processing request {request.request_id}")
        
        with self.metrics.measure_duration():
            try:
                initial_state = AgentState(
                    request=request,
                    response=None,
                    risk_factors=[],
                    historical_data=None,
                    security_context=self.security_context,
                )
                
                result = self.graph.invoke(initial_state)
                response = result["response"]
                
                self.metrics.record_request(
                    status="fraudulent" if response.is_fraudulent else "legitimate"
                )
                
                return response
                
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                self.metrics.record_error(error_type=type(e).__name__)
                raise
```

### 5. Create FastAPI Endpoints

Edit `agents/fraud_detection/api.py`:

```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from agents.fraud_detection import (
    FraudDetectionAgent, 
    FraudDetectionRequest, 
    FraudDetectionResponse
)
from shared.security import SecurityContext

app = FastAPI(
    title="Fraud Detection Agent API",
    description="AI Agent for fraud detection",
    version="0.1.0",
)

security = HTTPBearer()

def get_security_context(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> SecurityContext:
    """Extract security context."""
    return SecurityContext(
        user_id="user_123",
        roles=["fraud_analyst"],
        permissions={"tool:fraud_detection"},
        allowed_data_domains={"public", "internal"},
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fraud-detection-agent"}

@app.post("/api/v1/detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest,
    security_context: SecurityContext = Depends(get_security_context),
):
    """Detect fraud in transaction."""
    try:
        agent = FraudDetectionAgent(security_context=security_context)
        response = agent.process_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
```

### 6. Write Tests

Create `tests/agents/fraud_detection/test_agent.py`:

```python
import pytest
from agents.fraud_detection import (
    FraudDetectionAgent,
    FraudDetectionRequest,
)

class TestFraudDetectionAgent:
    """Test cases for fraud detection agent."""
    
    @pytest.fixture(autouse=True)
    def setup(self, security_context):
        self.agent = FraudDetectionAgent(security_context=security_context)
    
    def test_high_amount_transaction(self, security_context):
        """Test detection of high amount transactions."""
        request = FraudDetectionRequest(
            request_id="TEST-001",
            transaction_id="TXN-001",
            amount=50000.0,
            merchant="Test Merchant",
            location="Unknown",
            user_id="USER-001",
        )
        
        response = self.agent.process_request(request)
        
        assert response is not None
        assert "High transaction amount" in response.risk_factors
    
    def test_legitimate_transaction(self, security_context):
        """Test legitimate transaction."""
        request = FraudDetectionRequest(
            request_id="TEST-002",
            transaction_id="TXN-002",
            amount=50.0,
            merchant="Regular Store",
            location="Home City",
            user_id="USER-001",
        )
        
        response = self.agent.process_request(request)
        
        assert response is not None
        assert not response.is_fraudulent
```

### 7. Add Configuration

Edit `config/config.yaml`:

```yaml
agents:
  fraud_detection:
    version: "0.1.0"
    llm:
      provider: "openai"
      model: "gpt-4"
      temperature: 0.0
    max_iterations: 5
    fraud_threshold: 0.7
```

### 8. Test Locally

```bash
# Run tests
make test-agent AGENT_NAME=fraud_detection

# Run API locally
make dev-agent AGENT_NAME=fraud_detection

# Test endpoint
curl -X POST http://localhost:8000/api/v1/detect \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "TEST-001",
    "transaction_id": "TXN-001",
    "amount": 5000.0,
    "merchant": "Test Store",
    "location": "New York",
    "user_id": "USER-123"
  }'
```

### 9. Add to CI/CD

The agent is automatically included in CI/CD pipelines. Just commit your changes:

```bash
git add agents/fraud_detection tests/agents/fraud_detection
git commit -m "feat: add fraud detection agent"
git push origin feature/fraud-detection
```

## Advanced Topics

### Adding RAG (Document Retrieval)

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class MyAgent:
    def __init__(self, security_context: SecurityContext):
        # ... existing code ...
        
        # Initialize vector store
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            collection_name="my_agent_docs",
            embedding_function=self.embeddings,
            persist_directory="./data/chroma/my_agent",
        )
    
    def _retrieve_documents(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents."""
        query = self._build_query(state["request"])
        docs = self.vectorstore.similarity_search(query, k=5)
        
        # Filter by permissions
        filtered = self.permission_manager.filter_documents(
            [{"content": doc.page_content} for doc in docs]
        )
        
        state["documents"] = filtered
        return state
```

### Adding MLFlow Tracking

```python
from shared.mlflow_tracking import get_agent_tracker

class MyAgent:
    def __init__(self, security_context: SecurityContext):
        # ... existing code ...
        self.tracker = get_agent_tracker("my_agent")
    
    def process_request(self, request: MyRequest) -> MyResponse:
        self.tracker.start_run(run_name=request.request_id)
        
        try:
            # Process request
            response = ...
            
            # Log metrics
            self.tracker.log_params({
                "input_size": len(request.data),
                "model": self.config.llm.model,
            })
            
            self.tracker.log_metrics({
                "confidence": response.confidence,
                "duration_ms": duration,
            })
            
            return response
        finally:
            self.tracker.end_run()
```

### Adding Custom Tools

```python
from langchain.tools import tool

@tool
def search_database(query: str) -> str:
    """Search the database for relevant information."""
    # Implement database search
    return "search results"

class MyAgent:
    def __init__(self, security_context: SecurityContext):
        # ... existing code ...
        self.tools = [search_database]
```

## Best Practices

1. **Start Simple**: Begin with basic functionality, then add complexity
2. **Test First**: Write tests as you develop
3. **Security**: Always implement security context checking
4. **Logging**: Add comprehensive logging at each step
5. **Metrics**: Track performance and usage metrics
6. **Documentation**: Document your agent's purpose and usage
7. **Error Handling**: Handle all potential errors gracefully

## Checklist

- [ ] Agent implementation complete
- [ ] Request/Response schemas defined
- [ ] Tests written (80%+ coverage)
- [ ] API endpoints created
- [ ] Configuration added
- [ ] Documentation updated
- [ ] Local testing successful
- [ ] Security context implemented
- [ ] Metrics tracking added
- [ ] Error handling comprehensive
- [ ] Code linted and formatted
- [ ] PR created and reviewed

---

Need help? Check the [Developer Guide](DEVELOPER_GUIDE.md) or ask in the team channel!
