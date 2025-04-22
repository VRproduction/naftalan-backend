// DOM Elements
const header = document.querySelector('.header');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');
const backToTopBtn = document.querySelector('.back-to-top');
const filterBtns = document.querySelectorAll('.filter-btn');
const hotelGrid = document.querySelector('.hotel-grid');
const galleryFilterBtns = document.querySelectorAll('.gallery-filter button');
const galleryGrid = document.querySelector('.gallery-grid');

// Initialize Swiper instances after DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Testimonial Slider
    const testimonialSlider = new Swiper('.testimonial-slider', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            768: {
                slidesPerView: 2,
            },
            992: {
                slidesPerView: 3,
            },
        },
    });

    // Hero Slider
    const heroSlider = new Swiper('.hero-slider', {
        slidesPerView: 1,
        loop: true,
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
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
    });
});

// Sample Data
const hotels = [
    {
        id: 1,
        name: 'Luxury Suite',
        image: 'images/hotels/luxury-suite.jpg',
        price: 299,
        rating: 5,
        amenities: ['King Bed', 'Ocean View', 'Private Balcony', 'Jacuzzi'],
        category: 'luxury'
    },
    {
        id: 2,
        name: 'Deluxe Room',
        image: 'images/hotels/deluxe-room.jpg',
        price: 199,
        rating: 4,
        amenities: ['Queen Bed', 'City View', 'Mini Bar', 'Work Desk'],
        category: 'deluxe'
    },
    {
        id: 3,
        name: 'Standard Room',
        image: 'images/hotels/standard-room.jpg',
        price: 149,
        rating: 3,
        amenities: ['Twin Beds', 'Garden View', 'TV', 'Air Conditioning'],
        category: 'standard'
    }
];

const treatments = [
    {
        id: 1,
        name: 'Oil Treatment',
        icon: 'fas fa-oil-can',
        description: 'Traditional oil treatment for various conditions',
        details: ['Duration: 60 minutes', 'Price: $100', 'Includes full body massage']
    },
    {
        id: 2,
        name: 'Mud Therapy',
        icon: 'fas fa-spa',
        description: 'Therapeutic mud treatment for skin conditions',
        details: ['Duration: 45 minutes', 'Price: $80', 'Includes facial treatment']
    },
    {
        id: 3,
        name: 'Hydrotherapy',
        icon: 'fas fa-water',
        description: 'Water-based treatment for relaxation',
        details: ['Duration: 30 minutes', 'Price: $60', 'Includes steam room access']
    }
];

const galleryItems = [
    {
        id: 1,
        image: 'images/gallery/spa-1.jpg',
        title: 'Spa Center',
        category: 'spa'
    },
    {
        id: 2,
        image: 'images/gallery/hotel-1.jpg',
        title: 'Hotel Exterior',
        category: 'hotel'
    },
    {
        id: 3,
        image: 'images/gallery/treatment-1.jpg',
        title: 'Oil Treatment',
        category: 'treatment'
    }
];

const blogPosts = [
    {
        id: 1,
        title: 'Benefits of Oil Treatment',
        image: 'images/blog/oil-treatment.jpg',
        date: '2024-03-15',
        category: 'Treatments',
        excerpt: 'Discover the amazing benefits of traditional oil treatments...'
    },
    {
        id: 2,
        title: 'Best Time to Visit',
        image: 'images/blog/best-time.jpg',
        date: '2024-03-10',
        category: 'Travel Tips',
        excerpt: 'Learn about the best seasons to visit our resort...'
    }
];

// Functions
function toggleMobileMenu() {
    navLinks.classList.toggle('active');
    mobileMenuBtn.classList.toggle('active');
}

function handleScroll() {
    // Header scroll effect
    if (window.scrollY > 100) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }

    // Back to top button
    if (window.scrollY > 300) {
        backToTopBtn.classList.add('active');
    } else {
        backToTopBtn.classList.remove('active');
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function filterHotels(category) {
    filterBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });

    const filteredHotels = category === 'all' 
        ? hotels 
        : hotels.filter(hotel => hotel.category === category);

    renderHotels(filteredHotels);
}

function renderHotels(hotelsToRender) {
    hotelGrid.innerHTML = hotelsToRender.map(hotel => `
        <div class="hotel-card">
            <img src="${hotel.image}" alt="${hotel.name}">
            <div class="hotel-info">
                <h3>${hotel.name}</h3>
                <div class="rating">
                    ${Array(hotel.rating).fill('<i class="fas fa-star"></i>').join('')}
                </div>
                <div class="price">$${hotel.price} <span>per night</span></div>
                <ul class="amenities">
                    ${hotel.amenities.map(amenity => `<li><i class="fas fa-check"></i> ${amenity}</li>`).join('')}
                </ul>
                <button class="book-now" onclick="bookHotel(${hotel.id})">Book Now</button>
            </div>
        </div>
    `).join('');
}

function filterGallery(category) {
    galleryFilterBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });

    const filteredItems = category === 'all' 
        ? galleryItems 
        : galleryItems.filter(item => item.category === category);

    renderGallery(filteredItems);
}

function renderGallery(items) {
    galleryGrid.innerHTML = items.map(item => `
        <div class="gallery-item">
            <img src="${item.image}" alt="${item.title}">
            <div class="gallery-overlay">
                <h3>${item.title}</h3>
                <a href="#" class="gallery-link" onclick="openGalleryModal(${item.id})">
                    <i class="fas fa-plus"></i>
                </a>
            </div>
        </div>
    `).join('');
}

function renderTreatments() {
    const treatmentGrid = document.querySelector('.treatment-grid');
    treatmentGrid.innerHTML = treatments.map(treatment => `
        <div class="treatment-card">
            <div class="treatment-icon">
                <i class="${treatment.icon}"></i>
            </div>
            <h3>${treatment.name}</h3>
            <p>${treatment.description}</p>
            <ul class="treatment-details">
                ${treatment.details.map(detail => `<li>${detail}</li>`).join('')}
            </ul>
            <a href="#" class="btn btn-outline" onclick="bookTreatment(${treatment.id})">Book Treatment</a>
        </div>
    `).join('');
}

function renderBlogPosts() {
    const blogGrid = document.querySelector('.blog-grid');
    blogGrid.innerHTML = blogPosts.map(post => {
        const date = new Date(post.date);
        return `
            <div class="blog-card">
                <div class="blog-image">
                    <img src="${post.image}" alt="${post.title}">
                    <div class="blog-date">
                        <span class="day">${date.getDate()}</span>
                        <span class="month">${date.toLocaleString('default', { month: 'short' })}</span>
                    </div>
                </div>
                <div class="blog-content">
                    <span class="blog-category">${post.category}</span>
                    <h3>${post.title}</h3>
                    <p>${post.excerpt}</p>
                    <a href="#" class="btn btn-text" onclick="readBlogPost(${post.id})">
                        Read More <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

function bookHotel(hotelId) {
    // Implement booking logic
    console.log(`Booking hotel ${hotelId}`);
}

function bookTreatment(treatmentId) {
    // Implement treatment booking logic
    console.log(`Booking treatment ${treatmentId}`);
}

function readBlogPost(postId) {
    // Implement blog post reading logic
    console.log(`Reading blog post ${postId}`);
}

function openGalleryModal(itemId) {
    // Implement gallery modal logic
    console.log(`Opening gallery modal for item ${itemId}`);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    renderHotels(hotels);
    renderTreatments();
    renderBlogPosts();
    renderGallery(galleryItems);

    // Add event listeners
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    window.addEventListener('scroll', handleScroll);
    backToTopBtn.addEventListener('click', scrollToTop);

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => filterHotels(btn.dataset.category));
    });

    galleryFilterBtns.forEach(btn => {
        btn.addEventListener('click', () => filterGallery(btn.dataset.category));
    });

    // Form validation
    const bookingForm = document.querySelector('.booking-form form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Implement form validation and submission logic
            console.log('Booking form submitted');
        });
    }

    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Implement contact form validation and submission logic
            console.log('Contact form submitted');
        });
    }

    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Implement newsletter subscription logic
            console.log('Newsletter form submitted');
        });
    }
});
