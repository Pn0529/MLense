import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_BASE_URL } from '../constants';

const Resources = () => {
    const navigate = useNavigate();

    const handleDone = (topic) => {
        let completedTopics = JSON.parse(localStorage.getItem('completedTopics') || '[]');
        if (!completedTopics.includes(topic)) {
            completedTopics.push(topic);
            localStorage.setItem('completedTopics', JSON.stringify(completedTopics));
        }
        navigate('/dashboard');
    };

    const location = useLocation();
    // If navigation state contains recommendations (from Results page), use them; otherwise fallback to hardcoded resources.
    const fallbackResources = [
        {
            topic: 'OS: Memory Management',
            icon: 'fa-microchip',
            youtube: 'https://youtube.com',
            notes: '#',
            pyqs: '#'
        },
        {
            topic: 'CN: TCP/IP Model',
            icon: 'fa-network-wired',
            youtube: 'https://youtube.com',
            notes: '#',
            pyqs: '#'
        },
        {
            topic: 'DBMS: Normalization',
            icon: 'fa-database',
            youtube: 'https://youtube.com',
            notes: '#',
            pyqs: '#'
        }
    ];
    const recommendations = location.state?.recommendations || [];
    const [todData, setTodData] = React.useState(null);
    const [loadingTod, setLoadingTod] = React.useState(false);

    React.useEffect(() => {
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
                })
                .catch(err => {
                    console.error("Failed to fetch TOD:", err);
                    setLoadingTod(false);
                });
        }
    }, [location.state?.topic_of_the_day]);


    // Transform recommendations into the same shape as fallbackResources for rendering.
    const dynamicResources = recommendations.map((rec, idx) => ({
        topic: rec.topic || `Recommendation ${idx + 1}`,
        icon: 'fa-solid fa-video', // generic icon for video recommendation
        youtube: rec.video?.url || '#',
        notes: '#',
        pyqs: '#'
    }));
    const resources = dynamicResources.length ? dynamicResources : fallbackResources;

    // Use fetched TOD data if available, otherwise fallback to navigation state
    const tod = todData || location.state?.topic_of_the_day;

    return (
        <main className="container">
            <div className="section-header">
                <h2>Study Resources</h2>
                <p>Access our curated collection of materials to help you succeed.</p>
            </div>

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

                    {/* Best Video Card */}
                    {tod["Best Video"] && (
                        <div style={{ background: 'linear-gradient(135deg, #1a1a2e, #16213e)', borderRadius: '12px', overflow: 'hidden', color: '#fff' }}>
                            {/* Thumbnail */}
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
                                {/* Title */}
                                <a href={tod["Best Video"]["Link"]} target="_blank" rel="noopener noreferrer"
                                    style={{ color: '#fff', fontWeight: 700, fontSize: '1.1rem', textDecoration: 'none', display: 'block', marginBottom: '0.5rem', lineHeight: 1.4 }}>
                                    {tod["Best Video"]["Title"]}
                                </a>
                                {/* Channel + Stats */}
                                <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem', color: '#aaa', marginBottom: '1rem', flexWrap: 'wrap' }}>
                                    <span><i className="fa-solid fa-circle-play" style={{ color: '#ff0000', marginRight: '4px' }}></i>{tod["Best Video"]["Channel"]}</span>
                                    <span><i className="fa-solid fa-eye" style={{ marginRight: '4px' }}></i>👁 {tod["Best Video"]["Views"]} views</span>
                                    <span><i className="fa-solid fa-thumbs-up" style={{ marginRight: '4px' }}></i>👍 {tod["Best Video"]["Likes"]} likes</span>
                                </div>
                                {/* Big CTA Button */}
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
                            </div>
                        </div>
                    )}

                    {/* No video available (API key not set) */}
                    {!tod["Best Video"] && (
                        <div style={{ background: '#f8f9fa', padding: '1rem', borderRadius: '8px', color: '#888', textAlign: 'center' }}>
                            <i className="fa-brands fa-youtube" style={{ fontSize: '1.5rem', color: '#ccc', marginBottom: '0.5rem', display: 'block' }}></i>
                            YouTube recommendation could not be fetched. Please check that YOUTUBE_API_KEY is configured.
                        </div>
                    )}
                </div>
            )}

            <div className="resources-grid">
                {resources.map((res, index) => (
                    <div key={index} className="resource-card">
                        <div className="resource-icon" style={{ height: '80px', fontSize: '2.5rem' }}>
                            <i className={`fa-solid ${res.icon}`}></i>
                        </div>
                        <div className="resource-content">
                            <h3>{res.topic}</h3>
                            <div style={{ margin: '1rem 0', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                                <a href={res.youtube} target="_blank" rel="noopener noreferrer" className="resource-link">
                                    <i className="fa-brands fa-youtube" style={{ color: '#ff0000', fontSize: '1.2rem' }}></i> Watch Lecture
                                </a>
                                <a href={res.notes} className="resource-link">
                                    <i className="fa-solid fa-file-pdf" style={{ color: 'var(--primary-navy)', fontSize: '1.2rem' }}></i> Download Notes
                                </a>
                                <a href={res.pyqs} className="resource-link">
                                    <i className="fa-solid fa-file-circle-question" style={{ color: 'var(--primary-green)', fontSize: '1.2rem' }}></i> View PYQs
                                </a>
                            </div>
                            <button className="btn btn-done" onClick={() => handleDone(res.topic)}
                                style={{ width: '100%', marginTop: 'auto' }}>I am Done</button>
                        </div>
                    </div>
                ))}
            </div>
        </main>
    );
};

export default Resources;
