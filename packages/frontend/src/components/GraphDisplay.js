import React, { useState } from 'react';

function GraphDisplay({ graphData }) {
  const [showDetails, setShowDetails] = useState(false);

  if (!graphData || (!graphData.nodes && !graphData.edges)) {
    return null;
  }

  const nodeCount = graphData.nodes ? graphData.nodes.length : 0;
  const edgeCount = graphData.edges ? graphData.edges.length : 0;

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div className="graph-display">
      <h4>Knowledge Graph Data</h4>
      <p>
        This response includes a knowledge graph with {nodeCount} nodes and {edgeCount} edges.
      </p>
      
      <button className="graph-toggle" onClick={toggleDetails}>
        {showDetails ? 'Hide Details' : 'Show Details'}
      </button>
      
      {showDetails && (
        <pre className="graph-data">
          {JSON.stringify(graphData, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default GraphDisplay;
