import React, { useState, useEffect, useRef, useMemo } from 'react';
import cytoscape from 'cytoscape';
import panzoom from 'cytoscape-panzoom';
import coseBilkent from 'cytoscape-cose-bilkent';

cytoscape.use(panzoom);
cytoscape.use(coseBilkent);

export default function GraphDisplay({ graphData }) {
  const [view, setView] = useState(null);
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  // Build Cytoscape elements, deriving URL for chunk nodes
  const elements = useMemo(() => {
    if (!graphData) return [];

    const nodes = graphData.nodes.map(n => {
      let url = null;
      // match "processed_<file>_chunk_" and link to "<file>.pdf"
      const m = n.id.match(/^processed_(.+?)_chunk_/);
      if (m) {
        url = `http://localhost:3001/diabetes_care/${m[1]}.pdf`;
      }
      return {
        data: {
          id: n.id,
          label: n.name || (n.text ? n.text.slice(0, 50) + '…' : n.id),
          url
        }
      };
    });

    const edges = graphData.edges.map(e => ({
      data: {
        source: e.source,
        target: e.target,
        relation: e.type
      }
    }));

    return [...nodes, ...edges];
  }, [graphData]);

  // Initialize / destroy Cytoscape when view === 'graph'
  useEffect(() => {
    if (view !== 'graph' || !elements.length || !containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            shape: 'ellipse',
            label: 'data(label)',
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            width: '100px',
            height: 'label',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '8px',
            color: '#fff',
            'background-color': '#1b273c',
            padding: '4px'
          }
        },
        {
          selector: 'node.custom-selected',
          style: {
            'background-color': '#bbb',
            color: '#000'
          }
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#555',
            opacity: 0.8,
            label: 'data(relation)',
            'font-size': '6px',
            'text-rotation': 'autorotate',
            'curve-style': 'bezier',
            'text-margin-y': -6
          }
        }
      ],
      layout: {
        name: 'cose-bilkent',
        fit: true,
        padding: 20,
        animate: false,
        idealEdgeLength: 150,
        nodeDimensionsIncludeLabels: true,
        avoidOverlap: true,
        avoidOverlapPadding: 10,
        spacingFactor: 1.2,
        gravity: 1.0,
        gravityRange: 3.8,
        numIter: 1000,
        tile: true
      },
      wheelSensitivity: 0.2,
      boxSelectionEnabled: false
    });

    cy.panzoom({ slider: true, zoomFactor: 0.05 });
    cy.fit();

    // Click a node to see full information + link
    cy.on('tap', 'node', evt => {
      const node = evt.target;
      const info = document.getElementById('graph-node-info');
      if (!info) return;

      if (node.hasClass('custom-selected')) {
        node.removeClass('custom-selected');
        info.innerHTML = '';
      } else {
        cy.nodes().removeClass('custom-selected');
        node.addClass('custom-selected');

        const d = node.data();
        const related = cy
          .edges()
          .filter(e => {
            const ed = e.data();
            return ed.source === d.id || ed.target === d.id;
          })
          .map(e => e.data());

        info.innerHTML = `
          <pre>${JSON.stringify({ node: d, edges: related }, null, 2)}</pre>
          ${
            d.url
              ? `<div style="margin-top:8px">
                   <a href="${d.url}" target="_blank" rel="noopener noreferrer">
                     Open source doc
                   </a>
                 </div>`
              : ''
          }
        `;
      }
    });

    // Click background: clear selection & info
    cy.on('tap', evt => {
      if (evt.target === cy) {
        cy.nodes().removeClass('custom-selected');
        const info = document.getElementById('graph-node-info');
        if (info) info.innerHTML = '';
      }
    });

    cyRef.current = cy;
    return () => cy.destroy();
  }, [view, elements]);

  if (!graphData) return null;

  return (
    <div className="graph-display">
      <h4>Knowledge Graph Data</h4>
      <p>
        This response includes a knowledge graph with{' '}
        <strong>{graphData.nodes.length}</strong> nodes and{' '}
        <strong>{graphData.edges.length}</strong> edges.
      </p>

      <div className="graph-controls">
        <button onClick={() => setView('json')}>Show JSON</button>
        <button onClick={() => setView('graph')}>Show Graph</button>
      </div>

      {view === 'json' && (
        <pre className="graph-data" id="graph-json-data">
          {JSON.stringify(graphData, null, 2)}
        </pre>
      )}

      {view === 'graph' && (
        <>
          <div ref={containerRef} className="graph-container" />
          <div id="graph-node-info" className="graph-node-info" />
        </>
      )}
    </div>
  );
}
