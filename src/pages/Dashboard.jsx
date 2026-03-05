import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Doughnut, Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import { API_BASE_URL } from '../constants';

const Dashboard = () => {
    const navigate = useNavigate();
    const [userName, setUserName] = useState(localStorage.getItem('userName') || 'User');
    const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || 'test@example.com');
    const [userPhone, setUserPhone] = useState(localStorage.getItem('userPhone') || '+917893140112');
    const [completedTopics, setCompletedTopics] = useState(JSON.parse(localStorage.getItem('completedTopics') || '[]'));
    const [history, setHistory] = useState([]);
    const [quizHistory, setQuizHistory] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('jwt_token');
            if (!token) {
                setIsLoading(false);
                return;
            }

            try {
                // Fetch analysis history
                const histRes = await fetch(`${API_BASE_URL}/history`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (histRes.ok) {
                    setHistory(await histRes.json());
                }

                // Fetch quiz history
                const quizRes = await fetch(`${API_BASE_URL}/quiz_history`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (quizRes.ok) {
                    setQuizHistory(await quizRes.json());
                }
            } catch (err) {
                console.error("Failed to fetch dashboard data:", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, []);

    // Refresh completed topics when page becomes visible or focus returns
    useEffect(() => {
        const handleVisibilityChange = () => {
            if (document.visibilityState === 'visible') {
                const updatedTopics = JSON.parse(localStorage.getItem('completedTopics') || '[]');
                setCompletedTopics(updatedTopics);
            }
        };

        const handleFocus = () => {
            const updatedTopics = JSON.parse(localStorage.getItem('completedTopics') || '[]');
            setCompletedTopics(updatedTopics);
        };

        const handleStorageChange = (e) => {
            if (e.key === 'completedTopics') {
                const updatedTopics = JSON.parse(e.newValue || '[]');
                setCompletedTopics(updatedTopics);
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('focus', handleFocus);
        window.addEventListener('storage', handleStorageChange);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('focus', handleFocus);
            window.removeEventListener('storage', handleStorageChange);
        };
    }, []);

    // Dynamic stats
    const totalUploads = history.length;
    const evaluatedItems = history.length; // In this app, every upload is evaluated

    // Average Quiz Score
    const avgQuizScore = quizHistory.length > 0
        ? Math.round(quizHistory.reduce((acc, curr) => acc + (curr.percentage || 0), 0) / quizHistory.length)
        : 0;

    const pendingReviews = history.reduce((acc, curr) => acc + (curr.critical_gaps || 0), 0);


    const handleDeleteAccount = () => {
        if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            localStorage.clear();
            navigate('/signin');
        }
    };

    const donutData = {
        labels: ['Completed Topics', 'Pending Topics'],
        datasets: [{
            data: [completedTopics.length, Math.max(0, pendingReviews - completedTopics.length)],
            backgroundColor: ['#2ecc71', '#e74c3c'],
            borderWidth: 0
        }]
    };

    const barData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Hours Studied',
            data: [2, 3.5, 1.5, 4, 2, 5, 3],
            backgroundColor: '#2c3e50',
            borderRadius: 4
        }]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom' }
        }
    };

    const barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            y: { beginAtZero: true }
        }
    };

    return (
        <main className="container">
            <div className="profile-header"
                style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '2rem', background: 'var(--bg-white)', padding: '2rem', borderRadius: 'var(--border-radius)', boxShadow: 'var(--box-shadow)' }}>
                <div className="profile-image"
                    style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--primary-green)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2.5rem', fontWeight: 'bold' }}>
                    <span>{userName.charAt(0).toUpperCase()}</span>
                </div>
                <div className="profile-info">
                    <h2 style={{ color: 'var(--primary-navy)', marginBottom: '0.2rem' }}>{userName.toUpperCase()}</h2>
                    <p style={{ color: '#666', fontSize: '1.1rem' }}>{userPhone}</p>
                </div>
            </div>

            <div className="dashboard-grid">
                <div className="stat-card">
                    <div className="stat-icon"><i className="fa-solid fa-file-arrow-up"></i></div>
                    <div className="stat-details"><h3>{totalUploads}</h3><p>Total Uploads</p></div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon"><i className="fa-solid fa-spinner"></i></div>
                    <div className="stat-details"><h3>{pendingReviews}</h3><p>Critical Gaps</p></div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon"><i className="fa-solid fa-graduation-cap"></i></div>
                    <div className="stat-details"><h3>{avgQuizScore}%</h3><p>Avg Quiz Score</p></div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon"><i className="fa-solid fa-check-double"></i></div>
                    <div className="stat-details"><h3>{completedTopics.length}</h3><p>Mastered</p></div>
                </div>
            </div>

            <div className="dashboard-panel" style={{ marginBottom: '2rem' }}>
                <ul className="activity-list">
                    <li className="activity-item" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 0', borderBottom: '1px solid #eee' }}>
                        <div style={{ color: 'var(--primary-navy)', fontSize: '1.2rem' }}><i className="fa-solid fa-chevron-right"></i></div>
                        <div className="activity-text">
                            <p style={{ fontSize: '1.1rem', color: 'var(--text-dark)' }}><strong>Profile Information</strong></p>
                        </div>
                    </li>
                    <li className="activity-item" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 0', borderBottom: '1px solid #eee' }}>
                        <div style={{ color: 'var(--primary-navy)', fontSize: '1.2rem' }}><i className="fa-solid fa-circle-question"></i></div>
                        <div className="activity-text">
                            <p style={{ fontSize: '1.1rem', color: 'var(--text-dark)' }}><strong>Help</strong></p>
                        </div>
                    </li>
                    <li className="activity-item" onClick={handleDeleteAccount} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 0' }}>
                        <div style={{ color: '#e74c3c', fontSize: '1.2rem' }}><i className="fa-solid fa-trash"></i></div>
                        <div className="activity-text">
                            <p style={{ fontSize: '1.1rem', color: '#e74c3c' }}><strong>Delete My Account</strong></p>
                        </div>
                    </li>
                </ul>
            </div>

            <div className="dashboard-content">
                <div className="dashboard-panel">
                    <h3>Recent Activity</h3>
                    <ul className="activity-list">
                        {history.length > 0 ? (
                            history.slice(0, 5).map((item, index) => (
                                <li key={index} className="activity-item">
                                    <div className="activity-dot"></div>
                                    <div className="activity-text">
                                        <p><strong>You</strong> analyzed <strong>{item.branch}</strong> Syllabus</p>
                                        <p style={{ fontSize: '0.85rem', color: '#666' }}>Match: {item.overall_similarity}% | Gaps: {item.critical_gaps}</p>
                                        <small>{new Date(item.created_at).toLocaleString()}</small>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <li className="activity-item">
                                <div className="activity-dot" style={{ backgroundColor: '#95a5a6' }}></div>
                                <div className="activity-text">
                                    <p>{isLoading ? 'Loading history...' : 'No recent activities found.'}</p>
                                    <small>Upload a syllabus to get started!</small>
                                </div>
                            </li>
                        )}
                    </ul>
                </div>

                <div className="dashboard-panel">
                    <h3>Completed Topics</h3>
                    <ul className="activity-list" id="completed-topics-list">
                        {completedTopics.length > 0 ? (
                            completedTopics.map((topic, index) => (
                                <li key={index} className="activity-item">
                                    <div style={{ color: '#3498db', fontSize: '1.2rem', marginTop: '4px' }}><i className="fa-solid fa-circle-check"></i></div>
                                    <div className="activity-text">
                                        <p><strong>Completed:</strong> {topic}</p>
                                        <small>Just now</small>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <li className="activity-item" style={{ color: '#666', fontStyle: 'italic' }}>No topics completed yet. Go to Resources to mark them done.</li>
                        )}
                    </ul>
                </div>
            </div>

            <div className="dashboard-content" style={{ marginTop: '1.5rem' }}>
                <div className="dashboard-panel">
                    <h3>Progress Overview</h3>
                    <div style={{ height: '300px' }}>
                        <Doughnut data={donutData} options={chartOptions} />
                    </div>
                </div>
                <div className="dashboard-panel">
                    <h3>Weekly Activity</h3>
                    <div style={{ height: '300px' }}>
                        <Bar data={barData} options={barOptions} />
                    </div>
                </div>
            </div>
        </main>
    );
};

export default Dashboard;
