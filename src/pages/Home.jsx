import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <section className="hero">
            <h1>Bridge the Gap to Success</h1>
            <p>A modern platform to manage, upload, and track your examination resources and results efficiently.</p>
            <div className="hero-btns">
                <Link to="/upload" className="btn">Get Started</Link>
                <Link to="/dashboard" className="btn btn-outline">View Dashboard</Link>
            </div>
        </section>
    );
};

export default Home;
