import React, { useState, useEffect } from 'react';
import './LandingPage.css';

function LandingPage() {
  const [file, setFile] = useState(null);
  const [userName, setUserName] = useState('');
  const [downloadUrl, setDownloadUrl] = useState(''); // State for download URL
  const [verifyMessage, setVerifyMessage] = useState(''); // State for verification message

  useEffect(() => {
    const name = localStorage.getItem('userName');
    if (name) {
      setUserName(name);
    }
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setDownloadUrl(''); // Clear previous download URL
    setVerifyMessage(''); // Clear previous verification message
  };

  const handleUpload = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/upload/', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          setDownloadUrl(url); // Set download URL
          alert('File uploaded successfully!');
        } else {
          alert('Failed to upload the file.');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file.');
      }
    } else {
      alert('Please select a file first.');
    }
  };

  const checkIntegrity = async () => {
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/verify/', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          setVerifyMessage(result); // Display verification message
          alert('File integrity check completed successfully!');
        } else {
          alert('Failed to verify file integrity.');
        }
      } catch (error) {
        console.error('Error verifying file:', error);
        alert('Error verifying file.');
      }
    } else {
      alert('Please select a file first.');
    }
  };

  return (
    <div className="landing-page">
      <header className="header">
        <div className="logo">DataSecure</div>
        <nav>
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#about">About Us</a>
          <a href="#contact">Contact</a>
        </nav>
      </header>
      <main>
        <div className="hero-section">
          <h1>Hey, {userName}!</h1>
          <p>Welcome to our Data Integrity Platform</p>
          <p>Ensure your files are secure with our advanced integrity verification system.</p>
          <div className="upload-section">
            <label className="custum-file-upload" htmlFor="file">
              <div className="icon">
                {/* SVG icon here */}
              </div>
              <div className="text">
                <span>Click to upload File</span>
              </div>
              <input type="file" id="file" onChange={handleFileChange} />
            </label>
            <div className="button-group">
              <button className="btn-upload" onClick={handleUpload}>Upload File</button>
              <button className="btn-integrity" onClick={checkIntegrity}>Check File Integrity</button>
            </div>
            {downloadUrl && (
              <div className="download-section">
                <a href={downloadUrl} download={`updated_${file.name}`}>
                  <button className="btn-download">Download Updated File</button>
                </a>
              </div>
            )}
            {verifyMessage && (
              <div className="verify-message">
                <p>{verifyMessage}</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default LandingPage;
