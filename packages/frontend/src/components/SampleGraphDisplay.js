import React, { useEffect, useRef, useMemo } from 'react';
import cytoscape from 'cytoscape';
import panzoom from 'cytoscape-panzoom';
import coseBilkent from 'cytoscape-cose-bilkent';
import './SampleGraphDisplay.css';

cytoscape.use(panzoom);
cytoscape.use(coseBilkent);

// Inline sample JSON graph
const sampleGraph = {
  nodes: [
    { id: 'type2_diabetes', name: 'Type 2 Diabetes' },
    { id: 'high_glycemic', name: 'High Glycemic Index Foods' },
    { id: 'meta_analysis', name: 'Meta-analysis of Cohorts' },
    { id: 'hba1c_test', name: 'HbA1c Test' },
    { id: 'metformin', name: 'Metformin' }
  ],
  edges: [
    { source: 'high_glycemic', target: 'type2_diabetes', type: 'CAUSES' },
    { source: 'meta_analysis', target: 'type2_diabetes', type: 'DIAGNOSES' },
    { source: 'hba1c_test', target: 'type2_diabetes', type: 'TESTS_FOR' },
    { source: 'metformin', target: 'type2_diabetes', type: 'TREATS' }
  ]
};

export default function SampleGraphDisplay() {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  const elements = useMemo(() => {
    const nodes = sampleGraph.nodes.map(n => ({ data: { id: n.id, label: n.name } }));
    const edges = sampleGraph.edges.map(e => ({ data: { source: e.source, target: e.target, relation: e.type } }));
    return [...nodes, ...edges];
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;
    if (cyRef.current) cyRef.current.destroy();

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            shape: 'roundrectangle',
            label: 'data(label)',
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '10px',
            color: '#fff',
            'background-color': '#1b273c',
            padding: '6px',
            width: 'label',
            height: 'label'
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
            'curve-style': 'bezier',
            label: 'data(relation)',
            'font-size': '8px',
            'text-rotation': 'autorotate',
            'text-margin-y': -12,
            opacity: 0.8
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
        tile: true
      },
      wheelSensitivity: 0.2,
      boxSelectionEnabled: false
    });

    cy.panzoom({ slider: true, zoomFactor: 0.05 });
    cy.fit();

    cy.on('tap', 'node', evt => {
      const node = evt.target;
      const info = document.getElementById('sample-graph-info');
      if (node.hasClass('custom-selected')) {
        node.removeClass('custom-selected');
        if (info) info.innerHTML = '';
      } else {
        cy.nodes().removeClass('custom-selected');
        node.addClass('custom-selected');
        const d = node.data();
        const related = cy.edges().filter(e => {
          const ed = e.data();
          return ed.source === d.id || ed.target === d.id;
        }).map(e => e.data());
        if (info) {
          info.innerHTML = `<pre>${JSON.stringify({ node: d, edges: related }, null, 2)}</pre>`;
        }
      }
    });

    cy.on('tap', evt => {
      if (evt.target === cy) {
        cy.nodes().removeClass('custom-selected');
        const info = document.getElementById('sample-graph-info');
        if (info) info.innerHTML = '';
      }
    });

    cyRef.current = cy;
    return () => cy.destroy();
  }, [elements]);

  return (
    <div>
      <div ref={containerRef} className="sample-graph-container" />
      <div id="sample-graph-info" className="sample-graph-info" />
    </div>
  );
}
