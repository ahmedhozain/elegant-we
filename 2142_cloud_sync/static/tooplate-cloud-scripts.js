/*

Tooplate 2142 Cloud Sync

https://www.tooplate.com/view/2142-cloud-sync

*/


// JavaScript Document

        // Interactive Pricing Calculator
        const teamSlider = document.getElementById('teamSlider');
        const storageSlider = document.getElementById('storageSlider');
        const teamSizeDisplay = document.getElementById('teamSize');
        const storageSizeDisplay = document.getElementById('storageSize');
        
        const starterPriceEl = document.getElementById('starterPrice');
        const proPriceEl = document.getElementById('proPrice');
        const enterprisePriceEl = document.getElementById('enterprisePrice');

        function calculatePricing() {
            const teamSize = parseInt(teamSlider.value);
            const storageSize = parseInt(storageSlider.value);
            
            // Update displays
            teamSizeDisplay.textContent = teamSize;
            storageSizeDisplay.textContent = storageSize + ' GB';
            
            // Calculate prices based on team size and storage
            const baseStarterPrice = 29;
            const baseProPrice = 149;
            const baseEnterprisePrice = 299;
            
            // Price per additional team member
            const teamMultiplier = Math.max(1, teamSize / 10);
            const storageMultiplier = Math.max(1, storageSize / 500);
            
            const starterPrice = Math.round(baseStarterPrice * Math.min(teamMultiplier, 2) * Math.min(storageMultiplier, 1.5));
            const proPrice = Math.round(baseProPrice * Math.min(teamMultiplier, 3) * Math.min(storageMultiplier, 2));
            const enterprisePrice = Math.round(baseEnterprisePrice * teamMultiplier * storageMultiplier);
            
            // Animate price changes
            animatePrice(starterPriceEl, starterPrice);
            animatePrice(proPriceEl, proPrice);
            animatePrice(enterprisePriceEl, enterprisePrice);
        }

        function animatePrice(element, newPrice) {
            const currentPrice = parseInt(element.textContent);
            const difference = newPrice - currentPrice;
            const steps = 20;
            const stepValue = difference / steps;
            let step = 0;
            
            const interval = setInterval(() => {
                step++;
                element.textContent = Math.round(currentPrice + (stepValue * step));
                
                if (step >= steps) {
                    element.textContent = newPrice;
                    clearInterval(interval);
                }
            }, 20);
        }

        if (teamSlider && storageSlider && teamSizeDisplay && storageSizeDisplay && starterPriceEl && proPriceEl && enterprisePriceEl) {
            teamSlider.addEventListener('input', calculatePricing);
            storageSlider.addEventListener('input', calculatePricing);
        }

        // Scroll animations
        window.addEventListener('scroll', () => {
            const nav = document.querySelector('nav');
            if (window.scrollY > 100) {
                nav.style.padding = '0.5rem 2rem';
                nav.style.background = 'rgba(255, 255, 255, 0.98)';
            } else {
                nav.style.padding = '1rem 2rem';
                nav.style.background = 'rgba(255, 255, 255, 0.95)';
            }
        });

        // Set active navigation link based on current page/section
        function setActiveNavLink() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-links a, .mobile-nav a');
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                
                // Check for page-based links
                if (currentPath.includes('about') && link.textContent.toLowerCase().includes('about')) {
                    link.classList.add('active');
                } else if (currentPath.includes('services') && link.textContent.toLowerCase().includes('services')) {
                    link.classList.add('active');
                } else if (link.getAttribute('href') === '#services' && window.location.hash === '#services') {
                    link.classList.add('active');
                } else if (link.getAttribute('href') === '#about' && window.location.hash === '#about') {
                    link.classList.add('active');
                } else if (link.getAttribute('href') === '#contact' && window.location.hash === '#contact') {
                    link.classList.add('active');
                } else if (link.getAttribute('href') === '#pricing' && window.location.hash === '#pricing') {
                    link.classList.add('active');
                } else if (currentPath === '/' && (link.textContent.toLowerCase().includes('home') || link.getAttribute('href') === '/')) {
                    link.classList.add('active');
                }
            });
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    // Close mobile menu if open (guarded)
                    if (typeof mobileNav !== 'undefined' && mobileNav) {
                        mobileNav.classList.remove('active');
                    }
                    if (typeof mobileMenuToggle !== 'undefined' && mobileMenuToggle) {
                        mobileMenuToggle.classList.remove('active');
                    }
                    // Update active link after scrolling
                    setTimeout(setActiveNavLink, 100);
                }
            });
        });

        // Set active nav link on page load
        document.addEventListener('DOMContentLoaded', setActiveNavLink);
        
        // Update active nav link on hash change
        window.addEventListener('hashchange', setActiveNavLink);

        // Mobile menu functionality
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const mobileNav = document.getElementById('mobileNav');

        if (mobileMenuToggle && mobileNav) {
            mobileMenuToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                this.classList.toggle('active');
                mobileNav.classList.toggle('active');
            });

            // Close mobile menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!mobileMenuToggle.contains(e.target) && !mobileNav.contains(e.target)) {
                    mobileNav.classList.remove('active');
                    mobileMenuToggle.classList.remove('active');
                }
            });
        }

        // Contact form handling
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Get form values
                const formData = {
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    governorate: document.getElementById('governorate').value,
                    message: document.getElementById('message').value
                };
                
                // Submit form
                const submitButton = this.querySelector('.submit-button');
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Sending...';
                submitButton.disabled = true;
                
                // Send to API
                fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        submitButton.textContent = 'Message Sent! ✓';
                        submitButton.style.background = 'var(--secondary)';
                        
                        // Reset form
                        contactForm.reset();
                        
                        // Show success message
                        alert(data.message);
                        
                        // Reset button after 3 seconds
                        setTimeout(() => {
                            submitButton.textContent = originalText;
                            submitButton.style.background = '';
                            submitButton.disabled = false;
                        }, 3000);
                    } else {
                        submitButton.textContent = originalText;
                        submitButton.disabled = false;
                        alert(data.message || 'An error occurred. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    submitButton.textContent = originalText;
                    submitButton.disabled = false;
                    alert('An error occurred. Please try again later.');
                });
            });
        }

        // Animate stats on scroll
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.8s ease-out forwards';
                }
            });
        }, observerOptions);

        // Observe stat cards
        document.querySelectorAll('.stat-card').forEach(card => {
            observer.observe(card);
        });

        // Interactive Ball Menu - Pure CSS hover effect, no JS needed

        // Hero background image auto-rotation
        document.addEventListener('DOMContentLoaded', function() {
            const heroBackgrounds = document.querySelectorAll('.hero-bg');
            let currentBgIndex = 0;

            function showBackground(index) {
                // Hide all backgrounds
                heroBackgrounds.forEach((bg) => {
                    bg.style.setProperty('opacity', '0', 'important');
                });
                
                // Show current background
                if (heroBackgrounds[index]) {
                    heroBackgrounds[index].style.setProperty('opacity', '1', 'important');
                }
            }

            function showNextBackground() {
                currentBgIndex = (currentBgIndex + 1) % heroBackgrounds.length;
                showBackground(currentBgIndex);
            }

            // Start with first image immediately
            if (heroBackgrounds.length > 0) {
                showBackground(0);
                
                // Auto-rotate every 3 seconds
                setInterval(showNextBackground, 3000);
            }
        });

        // Horizontal scroll buttons for success stories
        setTimeout(function() {
            const scrollLeftBtn = document.getElementById('scrollLeft');
            const scrollRightBtn = document.getElementById('scrollRight');
            const storiesScroll = document.getElementById('storiesScroll');

            console.log('Scroll elements:', scrollLeftBtn, scrollRightBtn, storiesScroll);

            if (scrollLeftBtn && scrollRightBtn && storiesScroll) {
                scrollLeftBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Left button clicked');
                    storiesScroll.scrollLeft -= 370;
                });

                scrollRightBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Right button clicked');
                    storiesScroll.scrollLeft += 370;
                });
            } else {
                console.log('Elements not found');
            }
        }, 100);