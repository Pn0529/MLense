import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../constants';

// Supported GATE branches — values must exactly match the backend syllabus folder names
const GATE_BRANCHES = [
    { value: 'CE_2026', label: 'Civil Engineering (CE)' },
    { value: 'CH_2026', label: 'Chemical Engineering (CH)' },
    { value: 'CS_2026', label: 'Computer Science & Engineering (CS)' },
    { value: 'DA_2026', label: 'Data Science & Artificial Intelligence (DA)' },
    { value: 'EC_2026', label: 'Electronics & Communication Engineering (EC)' },
    { value: 'EE_2026', label: 'Electrical Engineering (EE)' },
    { value: 'ME_2026', label: 'Mechanical Engineering (ME)' },
];

const Upload = () => {
    const [fileName, setFileName] = useState('Supports PDF up to 10MB');
    const [selectedFile, setSelectedFile] = useState(null);
    const [branch, setBranch] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validate file size (10MB limit)
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                setError('File size exceeds 10MB limit. Please choose a smaller file.');
                setSelectedFile(null);
                setFileName('Supports PDF up to 10MB');
                return;
            }
            
            // Validate file type
            if (file.type !== 'application/pdf') {
                setError('Please select a valid PDF file.');
                setSelectedFile(null);
                setFileName('Supports PDF up to 10MB');
                return;
            }
            
            setSelectedFile(file);
            setFileName(`Selected: ${file.name}`);
            setError(''); // Clear any previous errors
        } else {
            setSelectedFile(null);
            setFileName('Supports PDF up to 10MB');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!selectedFile) {
            setError('Please select a PDF file to upload.');
            return;
        }
        if (!branch) {
            setError('Please select your GATE branch.');
            return;
        }

        setIsUploading(true);

        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes timeout

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const token = localStorage.getItem('jwt_token');
            
            const response = await fetch(
                `${API_BASE_URL}/analyze/${encodeURIComponent(branch)}`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData,
                    signal: controller.signal,
                    // Content-Type is intentionally omitted so the browser
                    // sets it automatically with the correct multipart boundary.
                }
            );

            clearTimeout(timeoutId);

            if (!response.ok) {
                let errMsg = `Server error: ${response.status} ${response.statusText}`;
                try {
                    const errData = await response.json();
                    if (errData?.detail) {
                        errMsg = Array.isArray(errData.detail)
                            ? errData.detail.map((d) => d.msg).join(', ')
                            : errData.detail;
                    }
                } catch (_) { /* ignore JSON parse failure */ }
                throw new Error(errMsg);
            }

            const data = await response.json();

            // Persist results for navigation/refresh safety
            localStorage.setItem('latestResults', JSON.stringify(data));
            localStorage.setItem('latestBranch', branch);

            // Also save to analysis history for dashboard
            const historyEntry = {
                branch: branch,
                overall_similarity: data.overall_similarity || 0,
                critical_gaps: data.results ? data.results.filter(r => r.priority && r.priority.includes('High')).length : 0,
                created_at: new Date().toISOString()
            };
            
            const existingHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
            existingHistory.unshift(historyEntry); // Add to beginning
            // Keep only last 20 entries
            const trimmedHistory = existingHistory.slice(0, 20);
            localStorage.setItem('analysisHistory', JSON.stringify(trimmedHistory));

            // Pass the raw API response to the Results page via navigation state
            navigate('/results', { state: { results: data, branch } });
        } catch (err) {
            clearTimeout(timeoutId);
            
            if (err.name === 'AbortError') {
                setError('Upload timed out. Please try again with a smaller file or check your connection.');
            } else if (err.name === 'TypeError' && err.message.includes('fetch')) {
                setError('Network error. Please check your internet connection and try again.');
            } else {
                setError(err.message || 'An unexpected error occurred. Please try again.');
            }
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <main className="container">
            <div className="section-header">
                <h2>Upload Documents</h2>
                <p>Upload your college syllabus PDF to compare with the GATE 2026 syllabus.</p>
            </div>

            <div className="upload-card">
                <form onSubmit={handleSubmit}>
                    {/* GATE Branch */}
                    <div className="form-group">
                        <label htmlFor="gate-branch">GATE Branch</label>
                        <select
                            id="gate-branch"
                            name="gate-branch"
                            className="form-control"
                            value={branch}
                            onChange={(e) => setBranch(e.target.value)}
                            required
                        >
                            <option value="" disabled>Select your GATE branch...</option>
                            {GATE_BRANCHES.map((b) => (
                                <option key={b.value} value={b.value}>{b.label}</option>
                            ))}
                        </select>
                    </div>

                    {/* Document Category (UI-only, backend only handles syllabus) */}
                    <div className="form-group">
                        <label htmlFor="category">Document Category</label>
                        <select id="category" name="category" className="form-control" required>
                            <option value="" disabled>Select a category...</option>
                            <option value="syllabus">Syllabus</option>
                        </select>
                    </div>

                    {/* File Upload */}
                    <div className="form-group">
                        <label>Upload File</label>
                        <div className="file-upload-wrapper" style={{ position: 'relative' }}>
                            <input
                                type="file"
                                id="exam-file"
                                name="file"
                                accept=".pdf"
                                onChange={handleFileChange}
                                required
                                style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
                            />
                            <i className="fa-solid fa-cloud-arrow-up upload-icon"></i>
                            <h4 style={{ color: 'var(--secondary-navy)' }}>Choose a PDF or drag it here</h4>
                            <p className="file-name-display">{fileName}</p>
                        </div>
                    </div>

                    {/* Error message */}
                    {error && (
                        <div style={{ color: '#e74c3c', background: '#fdecea', border: '1px solid #e74c3c', borderRadius: '6px', padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.95rem' }}>
                            <i className="fa-solid fa-circle-exclamation" style={{ marginRight: '8px' }}></i>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="btn"
                        style={{ width: '100%', marginTop: '1rem' }}
                        disabled={isUploading}
                    >
                        {isUploading ? (
                            <><i className="fa-solid fa-spinner fa-spin"></i> AI is mapping your syllabus to GATE 2026...</>
                        ) : (
                            'Upload & Analyze'
                        )}
                    </button>
                </form>
            </div>
        </main>
    );
};

export default Upload;
