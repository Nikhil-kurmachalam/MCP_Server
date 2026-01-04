import httpx
import asyncio
import os
from mcp.server.fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Initialize FastMCP Server
mcp = FastMCP("GetGene-Center-Resource")

# Get the underlying FastAPI app and configure it
app = mcp._app

# Allow all hosts (including Cloud Run URLs)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Configure CORS for Claude MCP connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Claude MCP - adjust if you need more restriction
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health check endpoints for Cloud Run
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "GetGene-Center-Resource MCP Server"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# Open Targets GraphQL Endpoint
OT_URL = "https://api.platform.opentargets.org/api/v4/graphql"

@mcp.tool()
async def fetch_gt_list(disease_id: str):
    """
    Fetches raw Genetic (G), Expression (E), and Target/Drug (T) data for a disease.
    Example disease_id: 'EFO_0000249' (Alzheimer's)
    """
    query = """
    query diseaseAssociations($efoId: String!) {
      disease(efoId: $efoId) {
        name
        associatedTargets(page: {index: 0, size: 50}) {
          rows {
            target {
              id
              approvedSymbol
              # E-List: RNA Expression
              expressions { tissue { label } rna { value } }
              # T-List: Drug Tractability
              tractability { modality value }
            }
            # G-List: Genetic Data Sources
            datatypeScores { id score }
          }
        }
      }
    }
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(OT_URL, json={"query": query, "variables": {"efoId": disease_id}})
        if response.status_code != 200:
            return {"error": "Failed to fetch data from Open Targets"}
        
        data = response.json()
        rows = data['data']['disease']['associatedTargets']['rows']
        
        # LOGIC: Custom Prioritization (Moving beyond 'Lazy' scores)
        processed_results = []
        for row in rows:
            symbol = row['target']['approvedSymbol']
            # Find Genetic Score (G)
            g_score = next((item['score'] for item in row['datatypeScores'] if item['id'] == 'genetic_association'), 0)
            # Find RNA value (E) - taking Brain/Cortex if available
            e_score = 0
            for exp in row['target']['expressions']:
                if "cortex" in exp['tissue']['label'].lower():
                    e_score = exp['rna']['value']
            
            processed_results.append({
                "gene": symbol,
                "g_score": round(g_score, 3),
                "e_value": round(e_score, 3),
                "target_id": row['target']['id']
            })
            
        return sorted(processed_results, key=lambda x: x['g_score'], reverse=True)

if __name__ == "__main__":
    # Cloud Run sets PORT env variable, default to 8080 for local development
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting MCP server on 0.0.0.0:{port}")
    # Listen on 0.0.0.0 (all interfaces) and use SSE transport for Claude MCP
    mcp.run(transport="sse", host="0.0.0.0", port=port)