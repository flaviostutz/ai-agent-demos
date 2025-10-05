"""Script to create a new agent from template."""

import os
import sys
from pathlib import Path


AGENT_TEMPLATE = """'''Agent implementation for {agent_name}.'''

from datetime import datetime
from enum import Enum

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from shared.config import get_config
from shared.logging_utils import get_logger
from shared.metrics import get_metrics_collector
from shared.security import SecurityContext


class {agent_class}Request(BaseModel):
    '''Request schema for {agent_name}.'''

    request_id: str = Field(description="Unique request identifier")
    # Add your request fields here


class {agent_class}Response(BaseModel):
    '''Response schema for {agent_name}.'''

    request_id: str
    # Add your response fields here
    processed_at: datetime = Field(default_factory=datetime.now)


class AgentState(TypedDict):
    '''State for the {agent_name} agent.'''

    request: {agent_class}Request
    response: {agent_class}Response | None
    security_context: SecurityContext


class {agent_class}:
    '''Implementation of {agent_name} agent.'''

    def __init__(self, security_context: SecurityContext):
        self.config = get_config().get_agent_config("{agent_name}")
        self.logger = get_logger(__name__, agent_id="{agent_name}")
        self.metrics = get_metrics_collector("{agent_name}")
        self.security_context = security_context

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        '''Build the LangGraph workflow.'''
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("process", self._process)

        # Add edges
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        return workflow.compile()

    def _process(self, state: AgentState) -> AgentState:
        '''Process the request.'''
        self.logger.info(f"Processing request {{state['request'].request_id}}")

        # TODO: Implement your logic here

        state["response"] = {agent_class}Response(
            request_id=state["request"].request_id
        )

        return state

    def process_request(self, request: {agent_class}Request) -> {agent_class}Response:
        '''Process a request and return response.'''
        self.logger.info(f"Processing request {{request.request_id}}")

        with self.metrics.measure_duration():
            try:
                initial_state = AgentState(
                    request=request,
                    response=None,
                    security_context=self.security_context,
                )

                result = self.graph.invoke(initial_state)
                response = result["response"]
                self.metrics.record_request(status="success")

                return response

            except Exception as e:
                self.logger.error(f"Error processing request: {{e}}")
                self.metrics.record_error(error_type=type(e).__name__)
                raise
"""

API_TEMPLATE = """'''FastAPI REST API for {agent_name} agent.'''

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import make_asgi_app

from agents.{agent_name} import {agent_class}, {agent_class}Request, {agent_class}Response
from shared.logging_utils import get_logger
from shared.security import SecurityContext

logger = get_logger(__name__)
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Lifecycle manager for FastAPI app.'''
    logger.info("Starting {agent_name} Agent API")
    yield
    logger.info("Shutting down {agent_name} Agent API")


app = FastAPI(
    title="{agent_name} Agent API",
    description="AI Agent for {agent_name}",
    version="0.1.0",
    lifespan=lifespan,
)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


def get_security_context(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> SecurityContext:
    '''Extract security context from request.'''
    return SecurityContext(
        user_id="user_123",
        roles=["user"],
        permissions={{"tool:{agent_name}"}},
        allowed_data_domains={{"public"}},
    )


@app.get("/health")
async def health_check():
    '''Health check endpoint.'''
    return {{"status": "healthy", "service": "{agent_name}-agent"}}


@app.post("/api/v1/process", response_model={agent_class}Response)
async def process_request(
    request: {agent_class}Request,
    security_context: SecurityContext = Depends(get_security_context),
):
    '''Process a request.'''
    logger.info(f"Received request: {{request.request_id}}")

    try:
        agent = {agent_class}(security_context=security_context)
        response = agent.process_request(request)
        return response

    except Exception as e:
        logger.error(f"Error processing request: {{e}}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

INIT_TEMPLATE = """'''Package initialization for {agent_name} agent.'''

from agents.{agent_name}.agent import {agent_class}, {agent_class}Request, {agent_class}Response

__all__ = ["{agent_class}", "{agent_class}Request", "{agent_class}Response"]
"""

TEST_TEMPLATE = """'''Tests for {agent_name} agent.'''

import pytest
from agents.{agent_name} import {agent_class}, {agent_class}Request


class Test{agent_class}:
    '''Test cases for {agent_class}.'''

    @pytest.fixture(autouse=True)
    def setup(self, security_context):
        '''Set up test environment.'''
        self.security_context = security_context
        self.agent = {agent_class}(security_context=security_context)

    def test_process_request(self):
        '''Test basic request processing.'''
        request = {agent_class}Request(request_id="TEST-001")

        response = self.agent.process_request(request)

        assert response is not None
        assert response.request_id == "TEST-001"
"""


def create_agent(agent_name: str) -> None:
    """Create a new agent from template."""
    # Convert to snake_case and PascalCase
    agent_snake = agent_name.lower().replace("-", "_").replace(" ", "_")
    agent_class = "".join(word.capitalize() for word in agent_snake.split("_")) + "Agent"

    # Create agent directory
    agent_dir = Path("agents") / agent_snake
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Create files
    files = {
        "agent.py": AGENT_TEMPLATE,
        "api.py": API_TEMPLATE,
        "__init__.py": INIT_TEMPLATE,
    }

    for filename, template in files.items():
        file_path = agent_dir / filename
        content = template.format(agent_name=agent_snake, agent_class=agent_class)
        file_path.write_text(content)
        print(f"Created: {file_path}")

    # Create test directory
    test_dir = Path("tests") / "agents" / agent_snake
    test_dir.mkdir(parents=True, exist_ok=True)

    test_file = test_dir / "test_agent.py"
    test_content = TEST_TEMPLATE.format(agent_name=agent_snake, agent_class=agent_class)
    test_file.write_text(test_content)
    print(f"Created: {test_file}")

    print(f"\n✅ Agent '{agent_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"1. Implement your logic in agents/{agent_snake}/agent.py")
    print(f"2. Update the API in agents/{agent_snake}/api.py")
    print(f"3. Add tests in tests/agents/{agent_snake}/")
    print(f"4. Run: make test-agent AGENT_NAME={agent_snake}")
    print(f"5. Run: make dev-agent AGENT_NAME={agent_snake}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_agent.sh <agent_name>")
        sys.exit(1)

    agent_name = sys.argv[1]
    create_agent(agent_name)
