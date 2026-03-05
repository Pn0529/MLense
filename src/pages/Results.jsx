import React from 'react';
import { Link, useLocation } from 'react-router-dom';

// Helper: map a similarity percentage (0-100) to a human-readable relevance label and row colour
const getRelevanceInfo = (pct) => {
    if (pct === undefined || pct === null) return { label: 'N/A', color: 'inherit' };
    const roundedPct = Math.round(pct);
    if (roundedPct >= 70) return { label: `Both (GATE & College) — ${roundedPct}%`, color: 'var(--priority-high)' };
    if (roundedPct >= 40) return { label: `GATE Only — ${roundedPct}%`, color: 'var(--priority-medium)' };
    return { label: `College Only — ${roundedPct}%`, color: 'var(--priority-low)' };
};

const Results = () => {
    const location = useLocation();
    const { results, branch } = location.state || {};

    // ---- Download plan (client-side, no extra API call needed) ----
    const handleDownloadPlan = () => {
        const lines = [];
        lines.push(`GATE 2026 Personalised Study Plan`);
        lines.push(`Branch: ${branch}`);
        lines.push(`Generated: ${new Date().toLocaleString()}`);
        lines.push('');

        if (score !== undefined && score !== null) {
            lines.push(`Overall Similarity Score: ${Math.round(score)}%`);
            lines.push('');
        }

        if (topics.length > 0) {
            lines.push('=== GAP ANALYSIS ===');
            topics.forEach((topic, i) => {
                const name = topic.gate_topic || `Topic ${i + 1}`;
                const pct = topic.similarity !== undefined ? `${Math.round(topic.similarity)}%` : '';
                const status = topic.priority || 'Evaluated';
                lines.push(`${i + 1}. ${name}  |  ${status}  ${pct}`);
            });
            lines.push('');
        }

        if (lectures.length > 0) {
            lines.push('=== RECOMMENDED LECTURES ===');
            lectures.forEach((lec, i) => {
                const title = lec.video?.title || `Lecture ${i + 1}`;
                const url = lec.video?.url || '';
                lines.push(`${i + 1}. ${title}`);
                if (url) lines.push(`   ${url}`);
            });
        }

        const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `GATE_${branch}_Study_Plan.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    };

    // ---- No results yet (user navigated directly) ----
    if (!results) {
        return (
            <main className="container">
                <div className="section-header">
                    <h2>Evaluation Results</h2>
                    <p>No analysis data found. Please&nbsp;
                        <Link to="/upload" style={{ color: 'var(--primary-navy)' }}>upload your syllabus</Link>
                        &nbsp;first.
                    </p>
                </div>
            </main>
        );
    }

    // ---- Normalise the response ----
    const topics = results.results ?? [];
    const score = results.overall_similarity;
    const lectures = results.recommendations ?? [];
    const comparisonSummary = results.comparison_result;

    return (
        <main className="container">
            <div className="section-header">
                <h2>Evaluation Results</h2>
                <p>GATE Branch: <strong>{branch}</strong> &mdash; AI-powered syllabus gap analysis.</p>
            </div>

            {/* Similarity score pill & Summary */}
            {score !== undefined && score !== null && (
                <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                    <div style={{ marginBottom: '1rem' }}>
                        <span style={{
                            display: 'inline-block',
                            padding: '0.6rem 1.6rem',
                            background: 'var(--primary-navy)',
                            color: '#fff',
                            borderRadius: '2rem',
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            boxShadow: '0 4px 15px rgba(44,62,80,0.25)'
                        }}>
                            Overall Similarity Score: {Math.round(score)}%
                        </span>
                    </div>
                    {comparisonSummary && (
                        <p style={{ color: '#555', fontSize: '1.05rem', maxWidth: '800px', margin: '0 auto', lineHeight: '1.5' }}>
                            {comparisonSummary}
                        </p>
                    )}
                </div>
            )}

            {/* Topic gap table */}
            {topics.length > 0 ? (
                <div className="table-container">
                    <table className="results-table">
                        <thead>
                            <tr>
                                <th>Subject / Topic</th>
                                <th>Relevance</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topics.map((topic, index) => {
                                const topicName = topic.gate_topic || JSON.stringify(topic);
                                const { label, color } = getRelevanceInfo(topic.similarity ?? score);
                                return (
                                    <tr key={index} style={{ backgroundColor: color }}>
                                        <td>
                                            <strong>{topicName}</strong>
                                            {topic.matched_topic && (
                                                <div style={{ fontSize: '0.85em', color: '#555', marginTop: '4px' }}>
                                                    Matched with: {topic.matched_topic}
                                                </div>
                                            )}
                                        </td>
                                        <td><strong>{label}</strong></td>
                                        <td>{topic.priority ?? 'Evaluated'}</td>
                                        <td>
                                            <Link to="/resources" state={{ recommendations: lectures, topic: topic.gate_topic }} style={{ color: 'var(--primary-navy)' }}>
                                                <i className="fa-solid fa-arrow-right"></i> View
                                            </Link>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#555' }}>
                    <i className="fa-solid fa-circle-check" style={{ fontSize: '2rem', color: '#2ecc71', marginBottom: '1rem', display: 'block' }}></i>
                    No gaps found! Your syllabus covers all the relevant GATE topics.
                </div>
            )}

            {/* YouTube lecture recommendations */}
            {lectures.length > 0 && (
                <div style={{ marginTop: '2rem' }}>
                    <h3 style={{ color: 'var(--primary-navy)', marginBottom: '1rem' }}>
                        <i className="fa-brands fa-youtube" style={{ color: '#ff0000', marginRight: '8px' }}></i>
                        Recommended Lectures
                    </h3>
                    <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {lectures.map((lec, i) => {
                            const url = lec.video?.url || '#';
                            const title = lec.video?.title || `Lecture ${i + 1}`;
                            const summary = lec.video?.summary;
                            return (
                                <li key={i} style={{ background: '#fff', padding: '1rem', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                                    <a href={url} target="_blank" rel="noopener noreferrer"
                                        style={{ color: 'var(--primary-navy)', textDecoration: 'none', fontWeight: 600, fontSize: '1.05rem', display: 'flex', alignItems: 'center' }}>
                                        <i className="fa-solid fa-play-circle" style={{ marginRight: '8px', color: '#ff0000', fontSize: '1.2rem' }}></i>
                                        {title}
                                    </a>
                                    {summary && (
                                        <p style={{ marginTop: '0.5rem', color: '#555', fontSize: '0.95rem', lineHeight: '1.4' }}>
                                            {summary}
                                        </p>
                                    )}
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            {/* Download plan */}
            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                    id="download-plan-btn"
                    className="btn"
                    onClick={handleDownloadPlan}
                    style={{ padding: '1rem 2rem', fontSize: '1.1rem', boxShadow: '0 4px 15px rgba(46, 204, 113, 0.4)' }}
                >
                    <i className="fa-solid fa-download" style={{ marginRight: '8px' }}></i>
                    Download Personalised Study Plan
                </button>
            </div>

            {/* Topic of the day */}
            {results.topic_of_the_day && (
                <div className="topic-of-day"
                    style={{ marginTop: '3rem', background: 'var(--bg-white)', borderRadius: 'var(--border-radius)', padding: '2rem', boxShadow: 'var(--box-shadow)', textAlign: 'center', border: '2px solid var(--primary-green)' }}>
                    <h3 style={{ color: 'var(--primary-navy)', marginBottom: '1rem' }}>
                        <i className="fa-solid fa-star" style={{ color: '#f1c40f' }}></i> Topic of the Day: {results.topic_of_the_day["Topic Name"]}
                    </h3>
                    <p style={{ marginBottom: '1.5rem', color: '#555', fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto 1.5rem' }}>
                        {results.topic_of_the_day["Explanation"]}
                    </p>
                    <Link to="/resources" state={{ recommendations: lectures, topic_of_the_day: results.topic_of_the_day }} className="btn">
                        Learn More <i className="fa-solid fa-arrow-right" style={{ marginLeft: '5px' }}></i>
                    </Link>
                </div>
            )}
        </main>
    );
};

export default Results;
