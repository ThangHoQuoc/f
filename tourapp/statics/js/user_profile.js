// Dropdown functionality
function toggleDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    const dropdownIcon = document.getElementById('dropdownArrow');
    if (dropdown.style.display === "none") {
        dropdown.style.display = "block";
        dropdownIcon.classList.add('rotate');
    } else {
        dropdown.style.display = "none";
        dropdownIcon.classList.remove('rotate');
    }
    if (dropdown.style.display === "block") {
        document.addEventListener('mousedown', handleClickOutside);
    } else {
        document.removeEventListener('mousedown', handleClickOutside);
    }
}

function handleClickOutside(event) {
    var dropdown = document.getElementById('dropdownMenu');
    var button = document.querySelector('.avatar-button');
    if (dropdown && !dropdown.contains(event.target) &&
        button && !button.contains(event.target)) {
        dropdown.style.display = "none";
        var arrow = document.getElementById('dropdownArrow');
        if (arrow) arrow.classList.remove("rotate");
        document.removeEventListener('mousedown', handleClickOutside);
    }
}

// Cover image functionality
let isEditing = false;
let isDragging = false;
let startX = 0, startY = 0;
let posX = 50, posY = 50; // Default position
let lastX = 50, lastY = 50;

function updateCoverPosition() {
    const coverImg = document.getElementById('coverImg');
    const coverX = document.getElementById('coverX');
    const coverY = document.getElementById('coverY');
    
    if (coverImg) {
        coverImg.style.backgroundPosition = `${posX}% ${posY}%`;
    }
    if (coverX) coverX.value = posX;
    if (coverY) coverY.value = posY;
}

function saveCoverPosition() {
    localStorage.setItem('profileCoverX', posX.toString());
    localStorage.setItem('profileCoverY', posY.toString());
}

function loadSavedCover() {
    // Load saved cover image
    const savedCover = localStorage.getItem('profileCoverImage');
    if (savedCover) {
        const coverImg = document.getElementById('coverImg');
        const coverBlur = document.querySelector('.cover-blur');
        if (coverImg) {
            coverImg.style.backgroundImage = `url('${savedCover}')`;
        }
        if (coverBlur) {
            coverBlur.style.backgroundImage = `url('${savedCover}')`;
        }
    }
    
    // Load saved position
    const savedX = localStorage.getItem('profileCoverX');
    const savedY = localStorage.getItem('profileCoverY');
    if (savedX && savedY) {
        posX = parseInt(savedX);
        posY = parseInt(savedY);
        lastX = posX;
        lastY = posY;
        updateCoverPosition();
    }
}

function setCoverImage(imageUrl) {
    const coverImg = document.getElementById('coverImg');
    const coverBlur = document.querySelector('.cover-blur');
    
    if (coverImg) {
        coverImg.style.backgroundImage = `url('${imageUrl}')`;
    }
    if (coverBlur) {
        coverBlur.style.backgroundImage = `url('${imageUrl}')`;
    }
    
    localStorage.setItem('profileCoverImage', imageUrl);
}

function initCoverEdit() {
    const coverImg = document.getElementById('coverImg');
    const coverY = document.getElementById('coverY');
    const coverX = document.getElementById('coverX');
    const editBtn = document.getElementById('editCoverBtn');
    const coverGuide = document.getElementById('coverGuide');
    
    if (!coverImg || !editBtn) return;

    // Edit button functionality
    editBtn.addEventListener('click', function() {
        isEditing = !isEditing;
        coverImg.classList.toggle('editable', isEditing);
        if (isEditing) {
            editBtn.textContent = 'Lưu vị trí';
            if (coverGuide) coverGuide.classList.add('active');
        } else {
            editBtn.textContent = 'Chỉnh sửa ảnh';
            if (coverGuide) coverGuide.classList.remove('active');
        }
    });

    // Mouse drag functionality
    coverImg.addEventListener('mousedown', function(e) {
        if (!isEditing) return;
        isDragging = true;
        coverImg.classList.add('dragging');
        startX = e.clientX;
        startY = e.clientY;
        lastX = posX;
        lastY = posY;
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        const rect = coverImg.getBoundingClientRect();
        let newX = lastX + dx / rect.width * 100;
        let newY = lastY + dy / rect.height * 100;
        posX = Math.max(0, Math.min(100, newX));
        posY = Math.max(0, Math.min(100, newY));
        updateCoverPosition();
    });

    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            coverImg.classList.remove('dragging');
            document.body.style.userSelect = '';
            saveCoverPosition();
        }
    });

    // Slider functionality
    if (coverY && coverX) {
        coverY.addEventListener('input', function() {
            posY = parseInt(coverY.value, 10);
            updateCoverPosition();
            saveCoverPosition();
        });
        coverX.addEventListener('input', function() {
            posX = parseInt(coverX.value, 10);
            updateCoverPosition();
            saveCoverPosition();
        });
    }

    // Keyboard arrow keys
    document.addEventListener('keydown', function(e) {
        if (!isEditing) return;
        let moved = false;
        if (e.key === 'ArrowUp') { posY = Math.max(0, posY - 1); moved = true; }
        if (e.key === 'ArrowDown') { posY = Math.min(100, posY + 1); moved = true; }
        if (e.key === 'ArrowLeft') { posX = Math.max(0, posX - 1); moved = true; }
        if (e.key === 'ArrowRight') { posX = Math.min(100, posX + 1); moved = true; }
        if (moved) {
            updateCoverPosition();
            saveCoverPosition();
            e.preventDefault();
        }
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load saved cover and position
    loadSavedCover();
    
    // Initialize cover edit functionality
    initCoverEdit();
    
    // Initialize position
    updateCoverPosition();
});

document.addEventListener("DOMContentLoaded", function () {
    fetchUserProfile();
    fetchBookedTours();
});

function fetchUserProfile() {
    fetch('/api/user/profile/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            // Nếu cần token:
            // 'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hiển thị username
        const nameElement = document.querySelector('.profile-name');
        if (nameElement) nameElement.textContent = data.username;

        // Hiển thị avatar (nếu có)
        const avatarImg = document.querySelectorAll('img[alt="Avatar"]');
        avatarImg.forEach(img => {
            img.src = data.avatar_url || 'avatar.jpg';
        });

        // Hiển thị liên kết mạng xã hội
        const socialLinks = document.querySelector('.social-links');
        if (socialLinks) {
            socialLinks.innerHTML = `
                <span><a href="${data.facebook}" target="_blank"><i class="fa-brands fa-facebook"></i></a></span> • 
                <span><a href="${data.instagram}" target="_blank"><i class="fa-brands fa-instagram"></i></a></span> • 
                <span><a href="${data.twitter}" target="_blank"><i class="fa-brands fa-twitter"></i></a></span>
            `;
        }
    })
    .catch(error => console.error('Lỗi khi lấy dữ liệu user:', error));
}

function fetchBookedTours() {
    fetch('/api/user/booked-tours/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        const tourList = document.querySelector('.tour-list');
        if (!tourList) return;

        // Xóa các tour hiện tại
        tourList.innerHTML = '';

        data.forEach(tour => {
            const tourCard = document.createElement('div');
            tourCard.className = 'tour-card';
            tourCard.innerHTML = `
                <a href="/tours/${tour.id}/">
                    <img src="${tour.image_url}" alt="${tour.name}" />
                    <div class="tour-info">
                        <h2 class="tour-name-rating">
                            <span class="tour-name">${tour.name}</span>
                            <span class="tour-rating">
                                <span>${tour.rating}/5</span>
                                <i class="icon-star"></i>
                            </span>
                        </h2>
                        <p class="price">Giá: ${tour.price.toLocaleString('vi-VN')}đ</p>
                        <p class="time">Thời gian: ${tour.duration}</p>
                    </div>
                </a>
            `;
            tourList.appendChild(tourCard);
        });
    })
    .catch(error => console.error('Lỗi khi lấy danh sách tour:', error));
}
