document.querySelectorAll('#like-link').forEach(function(element) {
    element.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default behavior of the anchor tag
        
        const postID = this.getAttribute('data-post-id');
        const heartIcon = this.querySelector('i');
        
        fetch(`/post/${postID}/like`, {
        method: "POST",
        // Add any required headers and data here
        })
        .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to like/unlike post');
        }
        })
        .then(data => {
        // Update the heart icon style and any other UI changes here if needed
        this.classList.toggle('liked');
        this.classList.toggle('not-liked');
        heartIcon.classList.toggle('fa-solid');
        heartIcon.classList.toggle('fa-regular');
        })
        .catch(error => {
        console.error(error);
        });
    });
    });