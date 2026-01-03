import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("GetGene-Center-Resource")

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
    import uvicorn
    # mcp.sse_app is a factory method, must be called to get the app
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8080)