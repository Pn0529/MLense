import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../constants';

const Resources = () => {
    const navigate = useNavigate();
    const location = useLocation();
    
    const recommendations = location.state?.recommendations || [];
    const [todData, setTodData] = useState(null);
    const [loadingTod, setLoadingTod] = useState(false);
    const [topicVideos, setTopicVideos] = useState({});
    const [loadingVideos, setLoadingVideos] = useState(false);
    const [todPyqs, setTodPyqs] = useState([]);
    const [loadingTodPyqs, setLoadingTodPyqs] = useState(false);
    const [isTodCompleted, setIsTodCompleted] = useState(false);
    const [showQuizWarning, setShowQuizWarning] = useState(false);
    const [completedRecommendations, setCompletedRecommendations] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem('completedRecommendations') || '[]');
        } catch {
            return [];
        }
    });
    const [recQuizWarnings, setRecQuizWarnings] = useState({});

    // Check if Topic of the Day is already completed
    useEffect(() => {
        if (location.state?.topic_of_the_day) {
            const topicName = location.state.topic_of_the_day["Topic Name"] || location.state.topic_of_the_day["Topic"];
            if (topicName) {
                const completed = JSON.parse(localStorage.getItem('completedTopics') || '[]');
                setIsTodCompleted(completed.includes(topicName));
            }
        }
    }, [location.state?.topic_of_the_day]);

    // Check if user has completed quizzes for a specific topic
    const hasCompletedQuizzesForTopic = (topicName) => {
        if (!topicName) return false;
        const quizHistory = JSON.parse(localStorage.getItem('quizHistory') || '[]');
        return quizHistory.some(q => q.topic === topicName);
    };

    // Handle marking a recommendation topic as complete
    const handleRecommendationComplete = (topic) => {
        if (!topic) return;

        // Check if quizzes are completed
        if (!hasCompletedQuizzesForTopic(topic)) {
            setRecQuizWarnings(prev => ({ ...prev, [topic]: true }));
            return;
        }

        const completed = JSON.parse(localStorage.getItem('completedRecommendations') || '[]');
        if (!completed.includes(topic)) {
            completed.push(topic);
            localStorage.setItem('completedRecommendations', JSON.stringify(completed));
            setCompletedRecommendations(completed);
            setRecQuizWarnings(prev => ({ ...prev, [topic]: false }));
            
            // Also add to main completed topics for dashboard
            const mainCompleted = JSON.parse(localStorage.getItem('completedTopics') || '[]');
            if (!mainCompleted.includes(topic)) {
                mainCompleted.push(topic);
                localStorage.setItem('completedTopics', JSON.stringify(mainCompleted));
                window.dispatchEvent(new StorageEvent('storage', {
                    key: 'completedTopics',
                    newValue: JSON.stringify(mainCompleted)
                }));
            }
            
            // Send quiz score email
            sendQuizScoreEmail();
        }
    };

    // Handle marking Topic of the Day as complete
    const handleTodComplete = () => {
        if (!todData) return;
        
        const topicName = todData["Topic Name"] || todData["Topic"];
        if (!topicName) return;

        // Check if quizzes are completed
        if (!hasCompletedQuizzesForTopic(topicName)) {
            setShowQuizWarning(true);
            return;
        }

        const completed = JSON.parse(localStorage.getItem('completedTopics') || '[]');
        if (!completed.includes(topicName)) {
            completed.push(topicName);
            localStorage.setItem('completedTopics', JSON.stringify(completed));
            setIsTodCompleted(true);
            setShowQuizWarning(false);
            
            // Trigger storage event for other tabs
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'completedTopics',
                newValue: JSON.stringify(completed)
            }));
            
            // Send quiz score email
            sendQuizScoreEmail();
        }
    };

    // Send quiz score email
    const sendQuizScoreEmail = async () => {
        try {
            const token = localStorage.getItem('jwt_token');
            const response = await fetch(`${API_BASE_URL}/send_quiz_score_email`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                console.log('Quiz score email sent successfully:', data);
                // Show success message to user
                alert(`📧 Progress report sent! Average score: ${data.average_score}%`);
            } else {
                console.error('Failed to send email:', data.msg);
            }
        } catch (error) {
            console.error('Error sending quiz score email:', error);
        }
    };

    // Fetch Topic of the Day
    useEffect(() => {
        if (location.state?.topic_of_the_day) {
            setLoadingTod(true);
            const token = localStorage.getItem('jwt_token');
            fetch(`${API_BASE_URL}/topic-of-the-day`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(data => {
                    setTodData(data);
                    setLoadingTod(false);
                    
                    // Fetch PYQs for the topic
                    const topicName = data["Topic Name"] || data["Topic"];
                    if (topicName) {
                        setLoadingTodPyqs(true);
                        fetch(`${API_BASE_URL}/pyqs/${encodeURIComponent(topicName)}`)
                            .then(res => res.json())
                            .then(pyqData => {
                                setTodPyqs(pyqData.results || []);
                                setLoadingTodPyqs(false);
                            })
                            .catch(err => {
                                console.error("Failed to fetch PYQs for TOD:", err);
                                setLoadingTodPyqs(false);
                            });
                    }
                })
                .catch(err => {
                    console.error("Failed to fetch TOD:", err);
                    setLoadingTod(false);
                });
        }
    }, [location.state?.topic_of_the_day]);

    // Fetch ranked videos for each recommendation topic
    useEffect(() => {
        if (recommendations.length > 0) {
            setLoadingVideos(true);
            const fetchAllVideos = async () => {
                const videosMap = {};
                
                for (const rec of recommendations) {
                    const topic = rec.topic || rec.gate_topic;
                    if (topic) {
                        try {
                            const response = await fetch(`${API_BASE_URL}/resources/${encodeURIComponent(topic)}`);
                            if (response.ok) {
                                const data = await response.json();
                                videosMap[topic] = data.videos || [];
                            }
                        } catch (err) {
                            console.error(`Failed to fetch videos for ${topic}:`, err);
                            videosMap[topic] = [];
                        }
                    }
                }
                
                setTopicVideos(videosMap);
                setLoadingVideos(false);
            };
            
            fetchAllVideos();
        }
    }, [recommendations]);

    const handleDownloadNotes = (topic, summary) => {
        const content = `Study Notes for: ${topic}\n\nAI-Generated Summary:\n${summary}\n\nGenerated by ExamBridge Nexus`;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${topic.replace(/[^a-z0-9]/gi, '_')}_Summary.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    };

    const handleDone = (topic) => {
        let completedTopics = JSON.parse(localStorage.getItem('completedTopics') || '[]');
        if (!completedTopics.includes(topic)) {
            completedTopics.push(topic);
            localStorage.setItem('completedTopics', JSON.stringify(completedTopics));
        }
        navigate('/dashboard');
    };

    // Get Score Color based on TubeMatix score
    const getScoreColor = (score) => {
        if (score >= 80) return '#2ecc71'; // Green
        if (score >= 60) return '#f39c12'; // Orange
        return '#e74c3c'; // Red
    };

    const tod = todData || location.state?.topic_of_the_day;

    return (
        <main className="container">
            <div className="section-header">
                <h2>Study Resources</h2>
                <p>Access our curated collection of TubeMatix-ranked learning materials.</p>
            </div>

            {/* Topic of the Day Section */}
            {loadingTod && (
                <div style={{ textAlign: 'center', padding: '2rem', background: '#fff', borderRadius: '8px', marginBottom: '2rem' }}>
                    <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--primary-navy)' }}></i>
                    <p style={{ marginTop: '1rem' }}>Fetching the best YouTube resources for your Topic of the Day...</p>
                </div>
            )}

            {!loadingTod && tod && (
                <div style={{ marginBottom: '3rem', background: '#fff', borderRadius: '12px', padding: '2rem', borderLeft: '5px solid var(--primary-green)', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
                    <h3 style={{ color: 'var(--primary-navy)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <i className="fa-solid fa-fire" style={{ color: '#e74c3c' }}></i>
                        📚 Topic of the Day: {tod["Topic Name"] || tod["Topic"]}
                    </h3>
                    <p style={{ color: '#555', fontSize: '1.05rem', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                        {tod["Explanation"]}
                    </p>

                    {tod["Best Video"] && (
                        <div style={{ background: 'linear-gradient(135deg, #1a1a2e, #16213e)', borderRadius: '12px', overflow: 'hidden', color: '#fff' }}>
                            {tod["Best Video"]["Thumbnail"] && (
                                <a href={tod["Best Video"]["Link"]} target="_blank" rel="noopener noreferrer">
                                    <img
                                        src={tod["Best Video"]["Thumbnail"]}
                                        alt="Video thumbnail"
                                        style={{ width: '100%', maxHeight: '220px', objectFit: 'cover', display: 'block' }}
                                    />
                                </a>
                            )}
                            <div style={{ padding: '1.2rem' }}>
                                <a href={tod["Best Video"]["Link"]} target="_blank" rel="noopener noreferrer"
                                    style={{ color: '#fff', fontWeight: 700, fontSize: '1.1rem', textDecoration: 'none', display: 'block', marginBottom: '0.5rem', lineHeight: 1.4 }}>
                                    {tod["Best Video"]["Title"]}
                                </a>
                                <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem', color: '#aaa', marginBottom: '1rem', flexWrap: 'wrap' }}>
                                    <span><i className="fa-solid fa-circle-play" style={{ color: '#ff0000', marginRight: '4px' }}></i>{tod["Best Video"]["Channel"]}</span>
                                    <span><i className="fa-solid fa-eye" style={{ marginRight: '4px' }}></i>👁 {tod["Best Video"]["Views"]} views</span>
                                    <span><i className="fa-solid fa-thumbs-up" style={{ marginRight: '4px' }}></i>👍 {tod["Best Video"]["Likes"]} likes</span>
                                </div>
                                <a href={tod["Best Video"]["Link"]} target="_blank" rel="noopener noreferrer"
                                    style={{
                                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                                        background: '#ff0000', color: '#fff', fontWeight: 700,
                                        padding: '0.7rem 1.5rem', borderRadius: '8px',
                                        textDecoration: 'none', fontSize: '1rem',
                                        boxShadow: '0 4px 15px rgba(255,0,0,0.4)', transition: 'transform 0.2s'
                                    }}>
                                    <i className="fa-brands fa-youtube"></i> Watch on YouTube
                                </a>
                                <a href={`/pyqs/${encodeURIComponent(tod["Topic Name"] || tod["Topic"])}`}
                                    style={{
                                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                                        background: 'var(--primary-navy)', color: '#fff', fontWeight: 700,
                                        padding: '0.7rem 1.5rem', borderRadius: '8px',
                                        textDecoration: 'none', fontSize: '1rem',
                                        boxShadow: '0 4px 15px rgba(44, 62, 80, 0.4)', transition: 'transform 0.2s',
                                        marginLeft: '10px'
                                    }}>
                                    <i className="fa-solid fa-question-circle"></i> Practice PYQs
                                </a>
                                <button
                                    onClick={() => {
                                        const summaryContent = tod["Best Video"]["Summary"] || `Summary not available for this video.\n\nVideo: ${tod["Best Video"]["Title"]}\nChannel: ${tod["Best Video"]["Channel"]}`;
                                        const content = `Video: ${tod["Best Video"]["Title"]}\nChannel: ${tod["Best Video"]["Channel"]}\nURL: ${tod["Best Video"]["Link"]}\n\nAI Summary:\n${summaryContent}\n\nGenerated by ExamBridge AI`;
                                        const blob = new Blob([content], { type: 'text/plain' });
                                        const url = window.URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = `${tod["Best Video"]["Title"].replace(/[^a-zA-Z0-9]/g, '_')}_Summary.txt`;
                                        document.body.appendChild(a);
                                        a.click();
                                        a.remove();
                                        window.URL.revokeObjectURL(url);
                                    }}
                                    style={{
                                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                                        background: 'linear-gradient(135deg, #3498db, #2980b9)', color: '#fff', fontWeight: 700,
                                        padding: '0.7rem 1.5rem', borderRadius: '8px',
                                        border: 'none', cursor: 'pointer', fontSize: '1rem',
                                        boxShadow: '0 4px 15px rgba(52, 152, 219, 0.4)', transition: 'transform 0.2s',
                                        marginLeft: '10px'
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                    onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                >
                                    <i className="fa-solid fa-download"></i> Summary
                                </button>
                            </div>
                        </div>
                    )}

                    {!tod["Best Video"] && (
                        <div style={{ background: 'linear-gradient(135deg, #1a1a2e, #16213e)', borderRadius: '12px', padding: '1.5rem', color: '#fff', textAlign: 'center' }}>
                            <i className="fa-brands fa-youtube" style={{ fontSize: '2.5rem', color: '#ff0000', marginBottom: '0.8rem', display: 'block' }}></i>
                            <p style={{ color: '#ccc', marginBottom: '1rem', fontSize: '1rem' }}>
                                Search for the best lectures on this topic directly on YouTube!
                            </p>
                            <a
                                href={`https://www.youtube.com/results?search_query=${encodeURIComponent((tod["Topic Name"] || tod["Topic"]) + " GATE lecture")}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                                    background: '#ff0000', color: '#fff', fontWeight: 700,
                                    padding: '0.7rem 1.5rem', borderRadius: '8px',
                                    textDecoration: 'none', fontSize: '1rem',
                                    boxShadow: '0 4px 15px rgba(255,0,0,0.4)'
                                }}>
                                <i className="fa-brands fa-youtube"></i> Search on YouTube
                            </a>
                        </div>
                    )}

                    {/* Mark as Complete Button */}
                    {!isTodCompleted ? (
                        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                            {showQuizWarning && (
                                <div style={{ 
                                    background: '#ffeaa7', 
                                    border: '1px solid #fdcb6e', 
                                    borderRadius: '8px', 
                                    padding: '1rem', 
                                    marginBottom: '1rem',
                                    color: '#d63031'
                                }}>
                                    <i className="fa-solid fa-exclamation-triangle" style={{ marginRight: '8px' }}></i>
                                    <strong>Please complete the practice quiz first!</strong>
                                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                                        You need to attempt at least one quiz before marking this topic as complete.
                                    </p>
                                </div>
                            )}
                            <button
                                onClick={handleTodComplete}
                                style={{
                                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                                    background: 'linear-gradient(135deg, #2ecc71, #27ae60)', 
                                    color: '#fff', fontWeight: 700,
                                    padding: '1rem 2rem', borderRadius: '8px',
                                    border: 'none', cursor: 'pointer', fontSize: '1.1rem',
                                    boxShadow: '0 4px 15px rgba(46, 204, 113, 0.4)',
                                    transition: 'transform 0.2s'
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            >
                                <i className="fa-solid fa-check-circle"></i> I'm Done - Mark as Complete
                            </button>
                            <p style={{ fontSize: '0.85rem', color: '#7f8c8d', marginTop: '0.5rem' }}>
                                Click after watching the video and completing practice questions
                            </p>
                        </div>
                    ) : (
                        <div style={{ marginTop: '1.5rem', textAlign: 'center', padding: '1rem', background: '#d5f4e6', borderRadius: '8px' }}>
                            <i className="fa-solid fa-check-circle" style={{ color: '#2ecc71', fontSize: '1.5rem', marginBottom: '0.5rem' }}></i>
                            <p style={{ color: '#27ae60', fontWeight: 600, margin: '0' }}>
                                Topic Completed! 🎉
                            </p>
                            <p style={{ fontSize: '0.85rem', color: '#2ecc71', margin: '0.5rem 0 0 0' }}>
                                This topic has been marked as complete in your dashboard.
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* Recommendations with TubeMatix-Ranked Videos */}
            {loadingVideos && (
                <div style={{ textAlign: 'center', padding: '2rem', background: '#fff', borderRadius: '8px', marginBottom: '2rem' }}>
                    <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--primary-navy)' }}></i>
                    <p style={{ marginTop: '1rem' }}>Loading TubeMatix-ranked videos for your topics...</p>
                </div>
            )}

            {recommendations.length > 0 && !loadingVideos && (
                <div>
                    <h2 style={{ color: 'var(--primary-navy)', marginBottom: '2rem', marginTop: '2rem' }}>
                        <i className="fa-brands fa-youtube" style={{ color: '#ff0000', marginRight: '10px' }}></i>
                        Learning Resources by Topic
                    </h2>

                    {recommendations.map((rec, idx) => {
                        const topic = rec.topic || rec.gate_topic;
                        const videos = topicVideos[topic] || [];

                        return (
                            <div key={idx} style={{ marginBottom: '3rem' }}>
                                {/* Topic Header */}
                                <div style={{
                                    background: 'linear-gradient(135deg, #2c3e50, #34495e)',
                                    color: '#fff',
                                    padding: '1.5rem',
                                    borderRadius: '12px 12px 0 0',
                                    marginBottom: '1.5rem'
                                }}>
                                    <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.3rem' }}>
                                        <i className="fa-solid fa-book" style={{ marginRight: '8px', color: '#3498db' }}></i>
                                        {topic}
                                    </h3>
                                    <p style={{ margin: '0', fontSize: '0.95rem', color: '#bdc3c7' }}>
                                        {videos.length} high-quality tutorials ranked by TubeMatix
                                    </p>
                                </div>

                                {/* Videos Grid */}
                                {videos.length > 0 ? (
                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                                        gap: '1.5rem',
                                        marginBottom: '2rem'
                                    }}>
                                        {videos.map((video, vidIdx) => (
                                            <div
                                                key={vidIdx}
                                                style={{
                                                    background: '#fff',
                                                    borderRadius: '12px',
                                                    overflow: 'hidden',
                                                    boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
                                                    transition: 'transform 0.3s, box-shadow 0.3s',
                                                    display: 'flex',
                                                    flexDirection: 'column',
                                                    cursor: 'pointer'
                                                }}
                                                onMouseOver={(e) => {
                                                    e.currentTarget.style.transform = 'translateY(-5px)';
                                                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                                                }}
                                                onMouseOut={(e) => {
                                                    e.currentTarget.style.transform = 'translateY(0)';
                                                    e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
                                                }}
                                            >
                                                {/* Thumbnail */}
                                                <a
                                                    href={`https://www.youtube.com/results?search_query=${encodeURIComponent(topic + " GATE lecture tutorial")}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    style={{
                                                        position: 'relative',
                                                        overflow: 'hidden',
                                                        height: '200px'
                                                    }}
                                                >
                                                    <img
                                                        src={video.thumbnail}
                                                        alt={video.title}
                                                        style={{
                                                            width: '100%',
                                                            height: '100%',
                                                            objectFit: 'cover',
                                                            transition: 'transform 0.3s'
                                                        }}
                                                    />
                                                    {/* Play Button Overlay */}
                                                    <div style={{
                                                        position: 'absolute',
                                                        inset: 0,
                                                        background: 'rgba(0,0,0,0.3)',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        transition: 'background 0.3s'
                                                    }}>
                                                        <i className="fa-solid fa-play" style={{
                                                            fontSize: '3rem',
                                                            color: '#fff',
                                                            textShadow: '0 2px 4px rgba(0,0,0,0.5)'
                                                        }}></i>
                                                    </div>

                                                    {/* TubeMatix Score Badge */}
                                                    <div style={{
                                                        position: 'absolute',
                                                        top: '10px',
                                                        right: '10px',
                                                        background: getScoreColor(video.tubematix_score),
                                                        color: '#fff',
                                                        padding: '0.5rem 0.8rem',
                                                        borderRadius: '8px',
                                                        fontWeight: 700,
                                                        fontSize: '0.9rem',
                                                        boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
                                                    }}>
                                                        TubeMatix: {video.tubematix_score.toFixed(1)}
                                                    </div>
                                                </a>

                                                {/* Content */}
                                                <div style={{ padding: '1.2rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                                    {/* Title */}
                                                    <a
                                                        href={`https://www.youtube.com/results?search_query=${encodeURIComponent(topic + " GATE lecture tutorial")}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        style={{
                                                            color: 'var(--primary-navy)',
                                                            fontWeight: 700,
                                                            fontSize: '1.05rem',
                                                            textDecoration: 'none',
                                                            marginBottom: '0.5rem',
                                                            lineHeight: 1.3,
                                                            display: '-webkit-box',
                                                            WebkitLineClamp: 2,
                                                            WebkitBoxOrient: 'vertical',
                                                            overflow: 'hidden'
                                                        }}
                                                    >
                                                        {video.title}
                                                    </a>

                                                    {/* Channel */}
                                                    <p style={{ color: '#7f8c8d', fontSize: '0.9rem', margin: '0.3rem 0 1rem 0' }}>
                                                        <i className="fa-solid fa-play-circle" style={{ color: '#e74c3c', marginRight: '4px' }}></i>
                                                        {video.channel}
                                                    </p>

                                                    {/* Stats */}
                                                    <div style={{
                                                        display: 'flex',
                                                        gap: '1rem',
                                                        fontSize: '0.85rem',
                                                        color: '#95a5a6',
                                                        marginBottom: '1rem',
                                                        flexWrap: 'wrap'
                                                    }}>
                                                        <span>
                                                            <i className="fa-solid fa-eye" style={{ marginRight: '4px' }}></i>
                                                            {video.views > 0 ? `${(video.views / 1000000).toFixed(1)}M` : 'N/A'} views
                                                        </span>
                                                        <span>
                                                            <i className="fa-solid fa-thumbs-up" style={{ marginRight: '4px' }}></i>
                                                            {video.likes > 0 ? `${(video.likes / 1000).toFixed(1)}K` : 'N/A'} likes
                                                        </span>
                                                    </div>

                                                    {/* Summary Display */}
                                                    {video.summary && !video.summary.includes("Transcript not available") ? (
                                                        <div style={{ 
                                                            background: '#f8f9fa', 
                                                            padding: '0.75rem', 
                                                            borderRadius: '6px', 
                                                            marginBottom: '0.75rem',
                                                            fontSize: '0.85rem',
                                                            color: '#555',
                                                            borderLeft: '3px solid #3498db'
                                                        }}>
                                                            <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600 }}>
                                                                <i className="fa-solid fa-file-lines" style={{ marginRight: '6px', color: '#3498db' }}></i>
                                                                {video.summary.includes("AI-Generated") ? "AI Summary" : "Video Summary"}
                                                            </p>
                                                            <p style={{ margin: 0, lineHeight: 1.4 }}>{video.summary.replace("\n\n[AI-Generated Summary - Transcript Unavailable]", "").substring(0, 150)}...</p>
                                                        </div>
                                                    ) : null}

                                                    {/* CTA Buttons */}
                                                    <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                                                        <a
                                                            href={video.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            style={{
                                                                flex: 1,
                                                                display: 'inline-flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                gap: '6px',
                                                                background: 'linear-gradient(135deg, #e74c3c, #c0392b)',
                                                                color: '#fff',
                                                                fontWeight: 700,
                                                                padding: '0.6rem 0.8rem',
                                                                borderRadius: '6px',
                                                                textDecoration: 'none',
                                                                fontSize: '0.9rem',
                                                                boxShadow: '0 4px 12px rgba(231, 76, 60, 0.3)',
                                                                transition: 'all 0.2s'
                                                            }}
                                                            onMouseOver={(e) => {
                                                                e.currentTarget.style.transform = 'scale(1.05)';
                                                                e.currentTarget.style.boxShadow = '0 6px 16px rgba(231, 76, 60, 0.4)';
                                                            }}
                                                            onMouseOut={(e) => {
                                                                e.currentTarget.style.transform = 'scale(1)';
                                                                e.currentTarget.style.boxShadow = '0 4px 12px rgba(231, 76, 60, 0.3)';
                                                            }}
                                                        >
                                                            <i className="fa-brands fa-youtube"></i> Watch
                                                        </a>
                                                        <button
                                                            onClick={() => {
                                                                const summaryContent = video.summary || `Summary not available for this video.\n\nVideo: ${video.title}\nChannel: ${video.channel}`;
                                                                const content = `Video: ${video.title}\nChannel: ${video.channel}\nURL: ${video.url}\n\nAI Summary:\n${summaryContent}\n\nGenerated by ExamBridge AI`;
                                                                const blob = new Blob([content], { type: 'text/plain' });
                                                                const url = window.URL.createObjectURL(blob);
                                                                const a = document.createElement('a');
                                                                a.href = url;
                                                                a.download = `${video.title.replace(/[^a-zA-Z0-9]/g, '_')}_Summary.txt`;
                                                                document.body.appendChild(a);
                                                                a.click();
                                                                a.remove();
                                                                window.URL.revokeObjectURL(url);
                                                            }}
                                                            style={{
                                                                display: 'inline-flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                gap: '6px',
                                                                background: 'linear-gradient(135deg, #3498db, #2980b9)',
                                                                color: '#fff',
                                                                fontWeight: 700,
                                                                padding: '0.6rem 0.8rem',
                                                                borderRadius: '6px',
                                                                border: 'none',
                                                                cursor: 'pointer',
                                                                fontSize: '0.9rem',
                                                                boxShadow: '0 4px 12px rgba(52, 152, 219, 0.3)',
                                                                transition: 'all 0.2s'
                                                            }}
                                                            onMouseOver={(e) => {
                                                                e.currentTarget.style.transform = 'scale(1.05)';
                                                                e.currentTarget.style.boxShadow = '0 6px 16px rgba(52, 152, 219, 0.4)';
                                                            }}
                                                            onMouseOut={(e) => {
                                                                e.currentTarget.style.transform = 'scale(1)';
                                                                e.currentTarget.style.boxShadow = '0 4px 12px rgba(52, 152, 219, 0.3)';
                                                            }}
                                                        >
                                                            <i className="fa-solid fa-download"></i> Summary
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div style={{
                                        background: '#f8f9fa',
                                        padding: '2rem',
                                        borderRadius: '0 0 12px 12px',
                                        textAlign: 'center',
                                        color: '#7f8c8d'
                                    }}>
                                        <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}></i>
                                        <p>No videos available for this topic at the moment.</p>
                                    </div>
                                )}

                                {/* Action Buttons Section */}
                                <div style={{
                                    background: 'linear-gradient(135deg, #9b59b6, #8e44ad)',
                                    color: '#fff',
                                    padding: '1.5rem',
                                    borderRadius: '0 0 12px 12px',
                                    marginTop: '-1px'
                                }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {/* Watch Top Video */}
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                                            <div>
                                                <h4 style={{ margin: '0 0 0.3rem 0', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <i className="fa-solid fa-play-circle"></i>
                                                    Watch Top-Ranked Video
                                                </h4>
                                                <p style={{ margin: 0, fontSize: '0.9rem', color: '#e8daef' }}>
                                                    Jump straight to the highest TubeMatix-scored lecture
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => {
                                                    const topVideo = videos[0];
                                                    if (topVideo && topVideo.url) {
                                                        window.open(topVideo.url, '_blank', 'noopener,noreferrer');
                                                    } else {
                                                        alert('Video is still loading. Please wait a moment and try again.');
                                                    }
                                                }}
                                                disabled={videos.length === 0}
                                                style={{
                                                    background: videos.length === 0 ? '#ccc' : '#fff',
                                                    color: videos.length === 0 ? '#666' : '#9b59b6',
                                                    fontWeight: 700,
                                                    border: 'none',
                                                    padding: '0.7rem 1.5rem',
                                                    borderRadius: '6px',
                                                    cursor: videos.length === 0 ? 'not-allowed' : 'pointer',
                                                    fontSize: '0.95rem',
                                                    boxShadow: videos.length === 0 ? 'none' : '0 4px 12px rgba(0,0,0,0.2)',
                                                    transition: 'all 0.2s',
                                                    whiteSpace: 'nowrap'
                                                }}
                                                onMouseOver={(e) => {
                                                    if (videos.length > 0) {
                                                        e.currentTarget.style.transform = 'scale(1.05)';
                                                        e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.3)';
                                                    }
                                                }}
                                                onMouseOut={(e) => {
                                                    if (videos.length > 0) {
                                                        e.currentTarget.style.transform = 'scale(1)';
                                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                                                    }
                                                }}
                                            >
                                                <i className="fa-brands fa-youtube" style={{ marginRight: '6px' }}></i>
                                                {videos.length === 0 ? 'Loading...' : 'Watch Now'}
                                            </button>
                                        </div>

                                        {/* Divider */}
                                        <div style={{ height: '1px', background: 'rgba(255,255,255,0.3)', margin: '0.5rem 0' }}></div>

                                        {/* PYQ Quiz */}
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                                            <div>
                                                <h4 style={{ margin: '0 0 0.3rem 0', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <i className="fa-solid fa-file-circle-question"></i>
                                                    Practice with PYQs
                                                </h4>
                                                <p style={{ margin: 0, fontSize: '0.9rem', color: '#e8daef' }}>
                                                    Test your knowledge with GATE exam questions
                                                </p>
                                            </div>
                                            <button
                                                onClick={() => navigate('/pyqs', { state: { topic } })}
                                                style={{
                                                    background: '#fff',
                                                    color: '#9b59b6',
                                                    fontWeight: 700,
                                                    border: 'none',
                                                    padding: '0.7rem 1.5rem',
                                                    borderRadius: '6px',
                                                    cursor: 'pointer',
                                                    fontSize: '0.95rem',
                                                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                                                    transition: 'all 0.2s',
                                                    whiteSpace: 'nowrap'
                                                }}
                                                onMouseOver={(e) => {
                                                    e.currentTarget.style.transform = 'scale(1.05)';
                                                    e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.3)';
                                                }}
                                                onMouseOut={(e) => {
                                                    e.currentTarget.style.transform = 'scale(1)';
                                                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                                                }}
                                            >
                                                <i className="fa-solid fa-play" style={{ marginRight: '6px' }}></i>
                                                Start Quiz
                                            </button>
                                        </div>

                                        {/* Divider */}
                                        <div style={{ height: '1px', background: 'rgba(255,255,255,0.3)', margin: '0.5rem 0' }}></div>

                                        {/* I'm Done Button */}
                                        {completedRecommendations.includes(topic) ? (
                                            <div style={{ 
                                                textAlign: 'center', 
                                                padding: '0.75rem', 
                                                background: 'rgba(46, 204, 113, 0.2)', 
                                                borderRadius: '6px',
                                                border: '1px solid rgba(46, 204, 113, 0.5)'
                                            }}>
                                                <i className="fa-solid fa-check-circle" style={{ color: '#2ecc71', marginRight: '8px' }}></i>
                                                <span style={{ color: '#2ecc71', fontWeight: 600 }}>Topic Completed!</span>
                                            </div>
                                        ) : (
                                            <div>
                                                {recQuizWarnings[topic] && (
                                                    <div style={{ 
                                                        background: 'rgba(255, 234, 167, 0.9)', 
                                                        border: '1px solid #fdcb6e', 
                                                        borderRadius: '6px', 
                                                        padding: '0.75rem', 
                                                        marginBottom: '0.75rem',
                                                        color: '#d63031',
                                                        fontSize: '0.85rem'
                                                    }}>
                                                        <i className="fa-solid fa-exclamation-triangle" style={{ marginRight: '6px' }}></i>
                                                        Complete the quiz first!
                                                    </div>
                                                )}
                                                <button
                                                    onClick={() => handleRecommendationComplete(topic)}
                                                    style={{
                                                        width: '100%',
                                                        background: 'linear-gradient(135deg, #2ecc71, #27ae60)',
                                                        color: '#fff',
                                                        fontWeight: 700,
                                                        border: 'none',
                                                        padding: '0.8rem 1.5rem',
                                                        borderRadius: '6px',
                                                        cursor: 'pointer',
                                                        fontSize: '1rem',
                                                        boxShadow: '0 4px 12px rgba(46, 204, 113, 0.3)',
                                                        transition: 'all 0.2s',
                                                        display: 'inline-flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        gap: '8px'
                                                    }}
                                                    onMouseOver={(e) => {
                                                        e.currentTarget.style.transform = 'scale(1.02)';
                                                        e.currentTarget.style.boxShadow = '0 6px 16px rgba(46, 204, 113, 0.4)';
                                                    }}
                                                    onMouseOut={(e) => {
                                                        e.currentTarget.style.transform = 'scale(1)';
                                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(46, 204, 113, 0.3)';
                                                    }}
                                                >
                                                    <i className="fa-solid fa-check-circle"></i>
                                                    I'm Done - Mark Complete
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {/* Mark Done Button */}
                    <div style={{ textAlign: 'center', marginTop: '3rem' }}>
                        <button
                            onClick={() => navigate('/dashboard')}
                            style={{
                                background: 'linear-gradient(135deg, #2ecc71, #27ae60)',
                                color: '#fff',
                                fontWeight: 700,
                                padding: '1rem 2.5rem',
                                borderRadius: '8px',
                                border: 'none',
                                fontSize: '1rem',
                                cursor: 'pointer',
                                boxShadow: '0 4px 15px rgba(46, 204, 113, 0.3)',
                                transition: 'all 0.2s'
                            }}
                            onMouseOver={(e) => {
                                e.currentTarget.style.transform = 'scale(1.05)';
                                e.currentTarget.style.boxShadow = '0 6px 20px rgba(46, 204, 113, 0.4)';
                            }}
                            onMouseOut={(e) => {
                                e.currentTarget.style.transform = 'scale(1)';
                                e.currentTarget.style.boxShadow = '0 4px 15px rgba(46, 204, 113, 0.3)';
                            }}
                        >
                            <i className="fa-solid fa-check-circle" style={{ marginRight: '8px' }}></i>
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            )}

            {recommendations.length === 0 && !loadingVideos && (
                <div style={{ textAlign: 'center', padding: '3rem', background: '#f8f9fa', borderRadius: '12px' }}>
                    <i className="fa-solid fa-info-circle" style={{ fontSize: '2.5rem', color: 'var(--primary-navy)', marginBottom: '1rem', display: 'block' }}></i>
                    <h3 style={{ color: 'var(--primary-navy)' }}>No Topics to Learn</h3>
                    <p style={{ color: '#7f8c8d', marginBottom: '1.5rem' }}>
                        Great job! Your syllabus is well-aligned with the GATE curriculum. All topics have been mastered.
                    </p>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <button
                            onClick={() => navigate('/dashboard')}
                            style={{
                                background: 'var(--primary-navy)',
                                color: '#fff',
                                fontWeight: 700,
                                padding: '0.8rem 1.5rem',
                                borderRadius: '6px',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1rem'
                            }}
                        >
                            Go to Dashboard
                        </button>
                        <button
                            onClick={() => navigate('/upload')}
                            style={{
                                background: 'var(--primary-green)',
                                color: '#fff',
                                fontWeight: 700,
                                padding: '0.8rem 1.5rem',
                                borderRadius: '6px',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '1rem'
                            }}
                        >
                            Analyze New Syllabus
                        </button>
                    </div>
                </div>
            )}
        </main>
    );
};

export default Resources;
