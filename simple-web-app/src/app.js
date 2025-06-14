// Simple Web App JavaScript
// This file provides basic interactivity for the test application

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Main application initialization function
 */
function initializeApp() {
    setupButtonHandlers();
    setupFormHandlers();
    setupNavigationHandlers();
    displayWelcomeMessage();
}

/**
 * Set up event handlers for buttons
 */
function setupButtonHandlers() {
    const testButton = document.getElementById('test-button');
    if (testButton) {
        testButton.addEventListener('click', handleTestButtonClick);
    }
}

/**
 * Handle test button click event
 */
function handleTestButtonClick() {
    const messages = [
        'Hello! This is a test application.',
        'Webbench is evaluating this app\'s performance!',
        'Thanks for testing our simple web application.',
        'This button demonstrates basic JavaScript functionality.',
        'Performance, accessibility, and code quality matter!'
    ];

    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    alert(randomMessage);

    // Log to console for debugging
    console.log('Test button clicked:', randomMessage);
}

/**
 * Set up form handling
 */
function setupFormHandlers() {
    const contactForm = document.querySelector('form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }
}

/**
 * Handle form submission
 * @param {Event} event - The form submission event
 */
function handleFormSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: formData.get('message')
    };

    // Validate form data
    if (validateFormData(data)) {
        alert('Thank you for your message! (This is just a demo)');
        event.target.reset();
        console.log('Form submitted:', data);
    }
}

/**
 * Validate form data
 * @param {Object} data - Form data object
 * @returns {boolean} - Whether the data is valid
 */
function validateFormData(data) {
    if (!data.name || data.name.trim().length < 2) {
        alert('Please enter a valid name (at least 2 characters)');
        return false;
    }

    if (!data.email || !isValidEmail(data.email)) {
        alert('Please enter a valid email address');
        return false;
    }

    if (!data.message || data.message.trim().length < 10) {
        alert('Please enter a message (at least 10 characters)');
        return false;
    }

    return true;
}

/**
 * Check if email is valid
 * @param {string} email - Email address to validate
 * @returns {boolean} - Whether the email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Set up smooth scrolling for navigation links
 */
function setupNavigationHandlers() {
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', handleNavLinkClick);
    });
}

/**
 * Handle navigation link clicks for smooth scrolling
 * @param {Event} event - The click event
 */
function handleNavLinkClick(event) {
    event.preventDefault();

    const targetId = event.target.getAttribute('href').substring(1);
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Display a welcome message in the console
 */
function displayWelcomeMessage() {
    console.log('🚀 Simple Web App loaded successfully!');
    console.log('📊 This app is designed for webbench performance testing');
    console.log('🎯 Metrics being evaluated: Performance, Accessibility, SEO, Code Quality, Build Time, Bundle Size');
}

/**
 * Utility function to format current date and time
 * @returns {string} - Formatted date string
 */
function getCurrentDateTime() {
    const now = new Date();
    return now.toLocaleString();
}

// Export functions for testing (if in Node.js environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeApp,
        validateFormData,
        isValidEmail,
        getCurrentDateTime
    };
}
