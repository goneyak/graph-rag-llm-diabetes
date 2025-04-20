import React, { useState } from 'react';
import './Upload.css';
import SampleGraphDisplay from './SampleGraphDisplay';

function Upload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadStatus('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus('Please select a file first');
      return;
    }

    setUploading(true);
    setUploadStatus('Uploading...');

    try {
      // In a real application, this would upload to your S3 bucket
      // For now, we'll simulate the upload with a timeout
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setUploadStatus('File uploaded successfully! Processing graph data...');
      setFile(null);
      
      // Reset the file input
      document.getElementById('file-upload').value = '';
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('Error uploading file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page-container">
      <div className="upload-container">
        <h2>Upload Graph Data</h2>
        <p>Select a JSON or CSV file containing graph data</p>
        
        <div className="file-input-container">
          <input
            type="file"
            id="file-upload"
            accept=".json,.csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
          <button 
            onClick={handleUpload} 
            disabled={!file || uploading}
            className={!file || uploading ? 'button-disabled' : ''}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
        
        {uploadStatus && (
          <div className="status-message">
            {uploadStatus}
          </div>
        )}
        
        <div className="file-formats">
          <h3>Supported File Formats</h3>
          <div className="format-container">
            <div className="format">
              <h4>JSON Format</h4>
              <pre>
{`{
  "nodes": [
    {"id": "1", "label": "person", "properties": {"name": "John"}},
    {"id": "2", "label": "person", "properties": {"name": "Jane"}}
  ],
  "edges": [
    {"source": "1", "target": "2", "label": "knows"}
  ]
}`}
              </pre>
            </div>
            
            <div className="format">
              <h4>CSV Format</h4>
              <pre>
{`id,label,name,age
1,person,John,30
2,person,Jane,28

source,target,label,since
1,2,knows,2020`}
              </pre>
            </div>
          </div>
        </div>
        {/* Add the visualization section to show the sample knowledge graph */}
        <div className="visualization-container">
          <h3>Sample Knowledge Graph Visualization</h3>
          <SampleGraphDisplay />
        </div>
      </div>
    </div>
  );
}

export default Upload;
