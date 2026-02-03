import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { updateProfile, queryAI } from '../api';
import './Onboarding.css';

const Onboarding = () => {
    const [step, setStep] = useState(1);
    const [gender, setGender] = useState('');
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [size, setSize] = useState('');
    const [loading, setLoading] = useState(false);
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (!storedUser) {
            navigate('/login');
        } else {
            const parsedUser = JSON.parse(storedUser);
            if (parsedUser.gender && parsedUser.size) {
                navigate('/');
            }
            setUser(parsedUser);
        }
    }, [navigate]);

    const handleGenderSelect = async (selectedGender) => {
        setGender(selectedGender);
        setLoading(true);
        try {
            // Fetch categories for the selected gender using the AI query agent
            const response = await queryAI({
                prompt: `Show me categories for ${selectedGender}`,
                user_id: user.id
            });

            // Extract unique categories from the products returned
            const uniqueCats = [...new Set(response.data.products.map(p => p.product_category))];
            setCategories(uniqueCats.length > 0 ? uniqueCats : (selectedGender === 'women' ? ['Dresses', 'Tops'] : ['Shirts', 'T-shirts']));
            setStep(2);
        } catch (err) {
            console.error("Failed to fetch categories", err);
            setCategories(selectedGender === 'women' ? ['Dresses', 'Tops', 'Sarees'] : ['Shirts', 'T-shirts', 'Pants']);
            setStep(2);
        } finally {
            setLoading(false);
        }
    };

    const handleCategorySelect = (cat) => {
        setSelectedCategory(cat);
        setStep(3);
    };

    const handleSave = async () => {
        if (!gender || !size) return;
        setLoading(true);
        try {
            // Save preferences including selected category group
            const response = await updateProfile(user.id, {
                gender,
                size,
                preferences: { preferred_category: selectedCategory }
            });
            const updatedUser = response.data.user;
            localStorage.setItem('user', JSON.stringify(updatedUser));
            navigate('/');
        } catch (err) {
            alert("Failed to save preferences");
        } finally {
            setLoading(false);
        }
    };

    if (!user) return null;

    return (
        <div className="onboarding-overlay">
            <div className="onboarding-card">
                <div className="onboarding-header">
                    <h2>Personalize Your Style</h2>
                    <p>Help our AI find the best outfits for you.</p>
                </div>

                <div className="onboarding-steps">
                    <div className={`step-indicator ${step >= 1 ? 'active' : ''}`}>1</div>
                    <div className="step-line"></div>
                    <div className={`step-indicator ${step >= 2 ? 'active' : ''}`}>2</div>
                    <div className="step-line"></div>
                    <div className={`step-indicator ${step >= 3 ? 'active' : ''}`}>3</div>
                </div>

                {step === 1 && (
                    <div className="step-content fade-in">
                        <h3>What is your gender?</h3>
                        <div className="gender-options">
                            <button className={`gender-btn ${gender === 'women' ? 'selected' : ''}`} onClick={() => handleGenderSelect('women')}>
                                Women
                            </button>
                            <button className={`gender-btn ${gender === 'men' ? 'selected' : ''}`} onClick={() => handleGenderSelect('men')}>
                                Men
                            </button>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="step-content fade-in">
                        <h3>Your Preferred Outfit</h3>
                        <div className="category-options">
                            {categories.map(cat => (
                                <button key={cat} className={`cat-chip ${selectedCategory === cat ? 'selected' : ''}`} onClick={() => handleCategorySelect(cat)}>
                                    {cat}
                                </button>
                            ))}
                        </div>
                        <button className="back-link" onClick={() => setStep(1)}>Back</button>
                    </div>
                )}

                {step === 3 && (
                    <div className="step-content fade-in">
                        <h3>Select your size</h3>
                        <div className="size-options">
                            {['S', 'M', 'L', 'XL', 'XXL'].map(s => (
                                <button key={s} className={`size-btn ${size === s ? 'selected' : ''}`} onClick={() => setSize(s)}>
                                    {s}
                                </button>
                            ))}
                        </div>
                        <button className="save-onboarding-btn" disabled={!size || loading} onClick={handleSave}>
                            {loading ? "Saving..." : "Save & Start Shopping"}
                        </button>
                        <button className="back-link" onClick={() => setStep(2)}>Back</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Onboarding;
