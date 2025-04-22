// Modern Hero Slider Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Hero Slider
    const heroSlider = new Swiper('.hero-slider', {
        loop: true,
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
        speed: 1000,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        on: {
            slideChangeTransitionStart: function() {
                // Add animation class to slide content elements
                const activeSlide = document.querySelector('.swiper-slide-active .slide-content');
                if (activeSlide) {
                    activeSlide.style.opacity = '0';
                    activeSlide.style.transform = 'translateY(40px)';
                    
                    setTimeout(() => {
                        activeSlide.style.opacity = '1';
                        activeSlide.style.transform = 'translateY(0)';
                        activeSlide.style.transition = 'all 1s ease';
                    }, 100);
                }
            }
        }
    });

    // Search Form Functionality
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const treatmentType = document.getElementById('treatment-type').value;
            const hotelType = document.getElementById('hotel-type').value;
            const checkIn = document.getElementById('check-in').value;
            const checkOut = document.getElementById('check-out').value;
            const guests = document.getElementById('guests').value;
            
            // Validate dates
            if (checkIn && checkOut) {
                const checkInDate = new Date(checkIn);
                const checkOutDate = new Date(checkOut);
                
                if (checkOutDate <= checkInDate) {
                    alert('Çıxış tarixi giriş tarixindən sonra olmalıdır');
                    return;
                }
            }
            
            // For demonstration purposes, alert the form data
            console.log('Form submitted:', {
                treatmentType,
                hotelType,
                checkIn,
                checkOut,
                guests
            });
            
            // Here you would typically redirect to search results page with query parameters
            // window.location.href = `search-results.html?treatment=${treatmentType}&hotel=${hotelType}&checkin=${checkIn}&checkout=${checkOut}&guests=${guests}`;
            
            // For now, show success message
            const searchButton = document.querySelector('.btn-search');
            const originalText = searchButton.innerHTML;
            searchButton.innerHTML = '<i class="fas fa-check"></i> Axtarış tamamlandı';
            searchButton.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                searchButton.innerHTML = originalText;
                searchButton.style.backgroundColor = '';
            }, 2000);
        });
    }

    // Animate search box on scroll
    let searchBox = document.querySelector('.search-box');
    if (searchBox) {
        window.addEventListener('scroll', function() {
            if (window.innerWidth > 992) { // Only apply on larger screens
                let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (scrollTop > 100) {
                    searchBox.style.transform = 'translateY(-10px)';
                    searchBox.style.opacity = '0.9';
                } else {
                    searchBox.style.transform = 'translateY(0)';
                    searchBox.style.opacity = '1';
                }
            }
        });
    }

    // Add parallax effect to hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const slides = document.querySelectorAll('.hero-slider .swiper-slide');
            
            slides.forEach(slide => {
                // Create parallax effect by moving background slightly
                if (scrollTop < heroSection.offsetHeight) {
                    slide.style.backgroundPositionY = `${scrollTop * 0.5}px`;
                }
            });
        });
    }
});
