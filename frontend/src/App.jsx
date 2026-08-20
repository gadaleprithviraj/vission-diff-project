import React, { useState } from 'react';
import './index.css';

function App() {
  const [beforeFile, setBeforeFile] = useState(null);
  const [afterFile, setAfterFile] = useState(null);
  const [beforePreview, setBeforePreview] = useState(null);
  const [afterPreview, setAfterPreview] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const trialPairs = [
    { id: 1, label: 'Construction site', before: '/trials/before-1.jpg', after: '/trials/after-1.jpg' },
    { id: 2, label: 'Mountain road', before: '/trials/before-2.jpg', after: '/trials/after-2.jpg' },
    { id: 3, label: 'City street', before: '/trials/before-3.jpg', after: '/trials/after-3.jpg' },
  ];

  const steps = [
    'Preprocessing',
    'Computing image differences',
    'Detecting changed regions',
    'Generating result',
  ];

  const handleFileChange = (e, setFile, setPreview) => {
    const file = e.target.files[0];
    if (file) {
      setFile(file);
      setPreview(URL.createObjectURL(file));
    }
  };

  const removeFile = (setterFile, setterPreview) => {
    setterFile(null);
    setterPreview(null);
  };

  const loadTrialPair = async (trial) => {
    const responses = await Promise.all([fetch(trial.before), fetch(trial.after)]);
    if (responses.some(response => !response.ok)) throw new Error('Trial images could not be loaded.');
    const blobs = await Promise.all(responses.map(response => response.blob()));
    setBeforeFile(new File([blobs[0]], `before-${trial.id}.jpg`, { type: blobs[0].type }));
    setAfterFile(new File([blobs[1]], `after-${trial.id}.jpg`, { type: blobs[1].type }));
    setBeforePreview(trial.before);
    setAfterPreview(trial.after);
    setError('');
  };

  const analyze = async () => {
    setError('');
    setProcessing(true);
    setProgressStep(0);
    setResult(null);
    try {
      let selectedBefore = beforeFile;
      let selectedAfter = afterFile;
      if (!selectedBefore || !selectedAfter) {
        await loadTrialPair(trialPairs[0]);
        const responses = await Promise.all([fetch(trialPairs[0].before), fetch(trialPairs[0].after)]);
        const blobs = await Promise.all(responses.map(response => response.blob()));
        selectedBefore = new File([blobs[0]], 'before-trial.jpg', { type: blobs[0].type });
        selectedAfter = new File([blobs[1]], 'after-trial.jpg', { type: blobs[1].type });
      }
      const form = new FormData();
      form.append('before_image', selectedBefore);
      form.append('after_image', selectedAfter);
      const response = await fetch('/api/detect-changes', {
        method: 'POST',
        body: form,
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Server error');
      }
      // Simulate progress for UI friendliness
      for (let i = 0; i < steps.length; i++) {
        setProgressStep(i + 1);
        await new Promise(r => setTimeout(r, 500));
      }
      const data = await response.json();
      setResult(data.results);
    } catch (e) {
      setError(e.message);
    } finally {
      setProcessing(false);
      setProgressStep(0);
    }
  };

  const [activeTab, setActiveTab] = useState('Before');
  const renderImage = (base64) => (
    <img src={`data:image/jpeg;base64,${base64}`} alt="result" className="result-img" />
  );

  return (
    <div className="container">
      <h1>SiteVision – Image Change Detection</h1>
      <p className="subtitle">Upload two images of the same scene to identify visual changes.</p>
      <section className="showcase" aria-label="Featured before and after example">
        <div className="section-kicker">Featured example · always ready to explore</div>
        <div className="showcase-grid">
          <figure><img src={trialPairs[0].before} alt="Featured before" /><figcaption>Before</figcaption></figure>
          <div className="showcase-arrow" aria-hidden="true">→</div>
          <figure><img src={trialPairs[0].after} alt="Featured after" /><figcaption>After</figcaption></figure>
        </div>
      </section>
      <section className="trial-section">
        <div><h2>Try a sample pair</h2><p>Choose a prepared scene, or upload your own images below.</p></div>
        <div className="trial-grid">
          {trialPairs.map((trial) => (
            <button className="trial-card" key={trial.id} onClick={() => loadTrialPair(trial)} type="button">
              <span className="trial-thumbnails"><img src={trial.before} alt="" /><img src={trial.after} alt="" /></span>
              <span>{trial.label}</span>
            </button>
          ))}
        </div>
      </section>
      <div className="upload-section">
        <div className="upload-box">
          <label>BEFORE</label>
          {beforePreview ? (
            <div className="preview">
              <img src={beforePreview} alt="Before preview" />
              <button onClick={() => removeFile(setBeforeFile, setBeforePreview)} className="remove-btn">✕</button>
            </div>
          ) : (
            <input type="file" accept="image/*" onChange={(e) => handleFileChange(e, setBeforeFile, setBeforePreview)} />
          )}
        </div>
        <div className="upload-box">
          <label>AFTER</label>
          {afterPreview ? (
            <div className="preview">
              <img src={afterPreview} alt="After preview" />
              <button onClick={() => removeFile(setAfterFile, setAfterPreview)} className="remove-btn">✕</button>
            </div>
          ) : (
            <input type="file" accept="image/*" onChange={(e) => handleFileChange(e, setAfterFile, setAfterPreview)} />
          )}
        </div>
      </div>
      <button
        className="analyze-btn"
        disabled={processing}
        onClick={analyze}
      >
        {processing ? 'Analyzing…' : 'Analyze Changes'}
      </button>
      {processing && (
        <div className="progress-box">
          <p>Running OpenCV image-processing pipeline...</p>
          <ol>
            {steps.map((s, i) => (
              <li key={i} className={i < progressStep ? 'done' : ''}>{s}</li>
            ))}
          </ol>
        </div>
      )}
      {error && <div className="error-msg">Error: {error}</div>}
      {result && (
        <div className="result-section">
          <h2>Results</h2>
          <div className="tabs">
            {['Before', 'After', 'Difference', 'Detected Changes'].map((tab) => (
              <button
                key={tab}
                className={activeTab === tab ? 'active' : ''}
                onClick={() => setActiveTab(tab)}
              >{tab}</button>
            ))}
          </div>
          <div className="image-display">
            {activeTab === 'Before' && renderImage(result.before_image)}
            {activeTab === 'After' && renderImage(result.after_image)}
            {activeTab === 'Difference' && renderImage(result.difference_image)}
            {activeTab === 'Detected Changes' && renderImage(result.detected_changes)}
          </div>
          <div className="info-box">
            <p>Detected Regions: {result.number_of_regions}</p>
            {result.change_regions.slice(0, 5).map((r, i) => (
              <div key={i} className="region-info">
                Region {i + 1}: x={r.x}, y={r.y}, w={r.width}, h={r.height}
              </div>
            ))}
          </div>
          <button
            className="download-btn"
            onClick={() => {
              const link = document.createElement('a');
              link.href = `data:image/jpeg;base64,${result.detected_changes}`;
              link.download = 'detected_changes.jpg';
              link.click();
            }}
          >Download Result</button>
        </div>
      )}
      <div className="limitation-box">
        <p>Best results are obtained when both images show the same scene from a similar viewpoint. Camera movement, rotation, scale changes, and lighting differences can produce false detections.</p>
        <p>Future improvement: feature‑based image registration using ORB/SIFT and homography.</p>
      </div>
    </div>
  );
}

export default App;
