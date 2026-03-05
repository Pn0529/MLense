import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../constants';

const PYQs = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const topicFromState = location.state?.topic || '';

    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [questions, setQuestions] = useState([]);
    const [currentQ, setCurrentQ] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [showResult, setShowResult] = useState(false);
    const [score, setScore] = useState(0);
    const [quizComplete, setQuizComplete] = useState(false);
    const [answers, setAnswers] = useState([]);
    const [loading, setLoading] = useState(false);

    // Fetch categories on mount
    useEffect(() => {
        fetch(`${API_BASE_URL}/pyqs/categories`)
            .then(res => res.json())
            .then(data => {
                setCategories(data.categories || []);
                // Auto-select category if topic was passed from Resources page
                if (topicFromState) {
                    fetchQuestions(topicFromState);
                }
            })
            .catch(err => console.error('Failed to fetch categories:', err));
    }, []);

    const fetchQuestions = (topic) => {
        setLoading(true);
        setSelectedCategory(topic);
        setCurrentQ(0);
        setScore(0);
        setQuizComplete(false);
        setAnswers([]);
        setSelectedAnswer(null);
        setShowResult(false);

        fetch(`${API_BASE_URL}/pyqs/${encodeURIComponent(topic)}`)
            .then(res => res.json())
            .then(data => {
                const allQuestions = (data.results || []).flatMap(r => r.questions);
                setQuestions(allQuestions);
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to fetch PYQs:', err);
                setLoading(false);
            });
    };

    const handleAnswer = (index) => {
        if (showResult) return;
        setSelectedAnswer(index);
    };

    const handleSubmitAnswer = () => {
        if (selectedAnswer === null) return;
        setShowResult(true);
        const isCorrect = selectedAnswer === questions[currentQ].answer;
        if (isCorrect) setScore(prev => prev + 1);
        setAnswers(prev => [...prev, { questionIndex: currentQ, selected: selectedAnswer, correct: questions[currentQ].answer, isCorrect }]);
    };

    const handleNext = async () => {
        if (currentQ + 1 >= questions.length) {
            setQuizComplete(true);

            // Send results to backend and also save to localStorage
            const token = localStorage.getItem('jwt_token');
            if (token) {
                const finalScore = score + (selectedAnswer === questions[currentQ].answer ? 1 : 0);
                const percentage = Math.round((finalScore / questions.length) * 100);
                
                // Save to localStorage for dashboard display
                const quizResult = {
                    topic: selectedCategory,
                    score: finalScore,
                    total: questions.length,
                    percentage: percentage,
                    created_at: new Date().toISOString()
                };
                
                const existingQuizHistory = JSON.parse(localStorage.getItem('quizHistory') || '[]');
                existingQuizHistory.unshift(quizResult);
                // Keep only last 50 quiz results
                const trimmedHistory = existingQuizHistory.slice(0, 50);
                localStorage.setItem('quizHistory', JSON.stringify(trimmedHistory));
                console.log("Quiz result saved to localStorage:", quizResult);
                
                try {
                    const response = await fetch(`${API_BASE_URL}/quiz_results`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            topic: selectedCategory,
                            score: finalScore,
                            total: questions.length,
                            percentage: percentage
                        })
                    });
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    console.log("Quiz result saved to API:", data);
                } catch (err) {
                    console.error("Failed to save quiz results to API:", err);
                }
            }
        } else {
            setCurrentQ(prev => prev + 1);
            setSelectedAnswer(null);
            setShowResult(false);
        }
    };

    const handleRestart = () => {
        setCurrentQ(0);
        setScore(0);
        setQuizComplete(false);
        setAnswers([]);
        setSelectedAnswer(null);
        setShowResult(false);
    };

    const q = questions[currentQ];

    // ─── Category Selection Screen ───
    if (!selectedCategory || questions.length === 0) {
        return (
            <main className="container">
                <div className="section-header">
                    <h2>📝 GATE Previous Year Questions</h2>
                    <p>Select a topic to practice with real GATE questions.</p>
                </div>

                {loading && (
                    <div style={{ textAlign: 'center', padding: '3rem' }}>
                        <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', color: 'var(--primary-navy)' }}></i>
                        <p style={{ marginTop: '1rem' }}>Loading questions...</p>
                    </div>
                )}

                {!loading && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
                        {categories.map((cat, index) => (
                            <button
                                key={index}
                                onClick={() => fetchQuestions(cat)}
                                style={{
                                    background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
                                    color: '#fff',
                                    border: 'none',
                                    borderRadius: '12px',
                                    padding: '2rem 1.5rem',
                                    cursor: 'pointer',
                                    textAlign: 'left',
                                    transition: 'transform 0.2s, box-shadow 0.2s',
                                    boxShadow: '0 4px 15px rgba(0,0,0,0.15)',
                                    fontSize: '1.1rem',
                                    fontWeight: 600,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px'
                                }}
                                onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.25)'; }}
                                onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.15)'; }}
                            >
                                <i className="fa-solid fa-book-open" style={{ fontSize: '1.4rem', color: 'var(--primary-green)' }}></i>
                                {cat}
                            </button>
                        ))}
                    </div>
                )}

                <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                    <button className="btn" onClick={() => navigate('/resources')} style={{ background: 'var(--primary-navy)' }}>
                        <i className="fa-solid fa-arrow-left" style={{ marginRight: '8px' }}></i> Back to Resources
                    </button>
                </div>
            </main>
        );
    }

    // ─── Quiz Complete Screen ───
    if (quizComplete) {
        const percentage = Math.round((score / questions.length) * 100);
        const emoji = percentage >= 80 ? '🏆' : percentage >= 50 ? '👍' : '💪';

        return (
            <main className="container">
                <div style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
                    <div style={{
                        background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
                        borderRadius: '16px',
                        padding: '3rem 2rem',
                        color: '#fff',
                        marginBottom: '2rem',
                        boxShadow: '0 8px 30px rgba(0,0,0,0.2)'
                    }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>{emoji}</div>
                        <h2 style={{ marginBottom: '0.5rem' }}>Quiz Complete!</h2>
                        <p style={{ fontSize: '1.1rem', color: '#aaa', marginBottom: '1.5rem' }}>{selectedCategory}</p>
                        <div style={{
                            display: 'inline-block',
                            background: percentage >= 80 ? 'var(--primary-green)' : percentage >= 50 ? '#f39c12' : '#e74c3c',
                            borderRadius: '50%',
                            width: '120px',
                            height: '120px',
                            lineHeight: '120px',
                            fontSize: '2.5rem',
                            fontWeight: 700,
                            marginBottom: '1.5rem',
                            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                        }}>
                            {percentage}%
                        </div>
                        <p style={{ fontSize: '1.2rem' }}>
                            You got <strong>{score}</strong> out of <strong>{questions.length}</strong> correct!
                        </p>
                    </div>

                    {/* Review Answers */}
                    <div style={{ textAlign: 'left' }}>
                        <h3 style={{ color: 'var(--primary-navy)', marginBottom: '1rem' }}>📋 Review Your Answers</h3>
                        {answers.map((a, i) => (
                            <div key={i} style={{
                                background: '#fff',
                                borderRadius: '10px',
                                padding: '1.2rem',
                                marginBottom: '1rem',
                                borderLeft: `4px solid ${a.isCorrect ? 'var(--primary-green)' : '#e74c3c'}`,
                                boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                            }}>
                                <p style={{ fontWeight: 600, marginBottom: '0.5rem', color: 'var(--primary-navy)' }}>
                                    Q{i + 1}. {questions[a.questionIndex].question}
                                </p>
                                <p style={{ color: a.isCorrect ? 'var(--primary-green)' : '#e74c3c', fontSize: '0.95rem' }}>
                                    {a.isCorrect ? '✅ Correct' : `❌ Wrong — You chose: "${questions[a.questionIndex].options[a.selected]}"`}
                                </p>
                                {!a.isCorrect && (
                                    <p style={{ color: 'var(--primary-green)', fontSize: '0.95rem' }}>
                                        Correct answer: "{questions[a.questionIndex].options[a.correct]}"
                                    </p>
                                )}
                                <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.5rem', fontStyle: 'italic' }}>
                                    {questions[a.questionIndex].explanation}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '2rem', flexWrap: 'wrap' }}>
                        <button className="btn" onClick={handleRestart} style={{ background: 'var(--primary-green)' }}>
                            <i className="fa-solid fa-redo" style={{ marginRight: '8px' }}></i> Try Again
                        </button>
                        <button className="btn" onClick={() => { setSelectedCategory(''); setQuestions([]); }} style={{ background: 'var(--primary-navy)' }}>
                            <i className="fa-solid fa-list" style={{ marginRight: '8px' }}></i> Other Topics
                        </button>
                        <button className="btn" onClick={() => navigate('/dashboard')} style={{ background: '#f39c12' }}>
                            <i className="fa-solid fa-chart-line" style={{ marginRight: '8px' }}></i> Dashboard
                        </button>
                        <button className="btn" onClick={() => navigate('/resources')} style={{ background: '#555' }}>
                            <i className="fa-solid fa-arrow-left" style={{ marginRight: '8px' }}></i> Resources
                        </button>
                    </div>
                </div>
            </main>
        );
    }

    // ─── Quiz Question Screen ───
    return (
        <main className="container">
            <div style={{ maxWidth: '750px', margin: '0 auto' }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <h2 style={{ color: 'var(--primary-navy)', margin: 0 }}>📝 {selectedCategory}</h2>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <span style={{ background: 'var(--primary-navy)', color: '#fff', padding: '0.4rem 1rem', borderRadius: '20px', fontSize: '0.9rem', fontWeight: 600 }}>
                            {currentQ + 1} / {questions.length}
                        </span>
                        <span style={{ background: 'var(--primary-green)', color: '#fff', padding: '0.4rem 1rem', borderRadius: '20px', fontSize: '0.9rem', fontWeight: 600 }}>
                            Score: {score}
                        </span>
                    </div>
                </div>

                {/* Progress bar */}
                <div style={{ background: '#e0e0e0', borderRadius: '10px', height: '8px', marginBottom: '2rem', overflow: 'hidden' }}>
                    <div style={{
                        background: 'linear-gradient(90deg, var(--primary-green), var(--primary-navy))',
                        height: '100%',
                        width: `${((currentQ + 1) / questions.length) * 100}%`,
                        borderRadius: '10px',
                        transition: 'width 0.4s ease'
                    }}></div>
                </div>

                {/* Question Card */}
                <div style={{
                    background: '#fff',
                    borderRadius: '16px',
                    padding: '2rem',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    marginBottom: '1.5rem'
                }}>
                    {/* Year badge */}
                    <span style={{
                        display: 'inline-block',
                        background: '#f0f4ff',
                        color: 'var(--primary-navy)',
                        padding: '0.3rem 0.8rem',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        marginBottom: '1rem'
                    }}>
                        {q.year}
                    </span>

                    <h3 style={{ color: 'var(--primary-navy)', lineHeight: '1.6', marginBottom: '1.5rem', fontSize: '1.15rem' }}>
                        {q.question}
                    </h3>

                    {/* Options */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                        {q.options.map((option, idx) => {
                            let bg = '#f8f9fa';
                            let border = '2px solid #e0e0e0';
                            let color = '#333';
                            let icon = null;

                            if (showResult) {
                                if (idx === q.answer) {
                                    bg = '#d4edda';
                                    border = '2px solid var(--primary-green)';
                                    color = '#155724';
                                    icon = <i className="fa-solid fa-check-circle" style={{ color: 'var(--primary-green)', marginRight: '8px' }}></i>;
                                } else if (idx === selectedAnswer && idx !== q.answer) {
                                    bg = '#f8d7da';
                                    border = '2px solid #e74c3c';
                                    color = '#721c24';
                                    icon = <i className="fa-solid fa-times-circle" style={{ color: '#e74c3c', marginRight: '8px' }}></i>;
                                }
                            } else if (idx === selectedAnswer) {
                                bg = '#e8f0fe';
                                border = '2px solid var(--primary-navy)';
                                color = 'var(--primary-navy)';
                            }

                            return (
                                <button
                                    key={idx}
                                    onClick={() => handleAnswer(idx)}
                                    style={{
                                        background: bg,
                                        border,
                                        color,
                                        borderRadius: '10px',
                                        padding: '1rem 1.2rem',
                                        fontSize: '1rem',
                                        textAlign: 'left',
                                        cursor: showResult ? 'default' : 'pointer',
                                        transition: 'all 0.2s',
                                        display: 'flex',
                                        alignItems: 'center',
                                        fontWeight: selectedAnswer === idx ? 600 : 400
                                    }}
                                >
                                    <span style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        width: '28px',
                                        height: '28px',
                                        borderRadius: '50%',
                                        background: selectedAnswer === idx ? 'var(--primary-navy)' : '#ddd',
                                        color: selectedAnswer === idx ? '#fff' : '#666',
                                        fontWeight: 700,
                                        fontSize: '0.85rem',
                                        marginRight: '12px',
                                        flexShrink: 0
                                    }}>
                                        {String.fromCharCode(65 + idx)}
                                    </span>
                                    {icon}
                                    {option}
                                </button>
                            );
                        })}
                    </div>

                    {/* Explanation */}
                    {showResult && (
                        <div style={{
                            marginTop: '1.5rem',
                            padding: '1rem',
                            background: '#f0f4ff',
                            borderRadius: '10px',
                            borderLeft: '4px solid var(--primary-navy)'
                        }}>
                            <p style={{ color: 'var(--primary-navy)', fontWeight: 600, marginBottom: '0.3rem' }}>
                                <i className="fa-solid fa-lightbulb" style={{ marginRight: '6px', color: '#f1c40f' }}></i> Explanation
                            </p>
                            <p style={{ color: '#555', lineHeight: '1.5', fontSize: '0.95rem' }}>{q.explanation}</p>
                        </div>
                    )}
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                    {!showResult ? (
                        <button
                            className="btn"
                            onClick={handleSubmitAnswer}
                            disabled={selectedAnswer === null}
                            style={{
                                padding: '0.8rem 2.5rem',
                                fontSize: '1.1rem',
                                opacity: selectedAnswer === null ? 0.5 : 1,
                                cursor: selectedAnswer === null ? 'not-allowed' : 'pointer'
                            }}
                        >
                            Submit Answer
                        </button>
                    ) : (
                        <button
                            className="btn"
                            onClick={handleNext}
                            style={{ padding: '0.8rem 2.5rem', fontSize: '1.1rem' }}
                        >
                            {currentQ + 1 >= questions.length ? 'View Results' : 'Next Question'}
                            <i className="fa-solid fa-arrow-right" style={{ marginLeft: '8px' }}></i>
                        </button>
                    )}
                </div>
            </div>
        </main>
    );
};

export default PYQs;
