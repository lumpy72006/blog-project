document.addEventListener('DOMContentLoaded', function() {
    const likeForm = document.getElementById('like-form');
    if (likeForm) {
        likeForm.addEventListener('submit', function(event) {
            event.preventDefault();
            fetch(likeForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    'post_slug': '{{ post.slug }}',
                })
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('likes-count').textContent = data.likes;
                    const likeButton = document.querySelector('.like-button');
                    if (data.user_has_liked) {
                        likeButton.classList.add('liked');
                    } else {
                        likeButton.classList.remove('liked');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    };

    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(commentForm);

            fetch(commentForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Clear the textarea
                        commentForm.querySelector('textarea').value = '';

                        // Update comments count in both places
                        const newCount = parseInt(document.getElementById('comments-count').textContent) + 1;
                        document.getElementById('comments-count').textContent = newCount;
                        document.getElementById('comments-count-display').textContent = newCount;

                        // Add the new comment to the list
                        const commentsList = document.getElementById('comments-list');
                        const noCommentsMsg = commentsList.querySelector('.no-comments');

                        if (noCommentsMsg) {
                            noCommentsMsg.remove();
                        }

                        const newComment = document.createElement('div');
                        newComment.className = 'comment';
                        newComment.innerHTML = `
                        <p class="comment-meta">
                            <span class="comment-author">${data.author}</span> 
                            on ${data.created_date}
                        </p>
                        <p class="comment-content">${data.content}</p>
                    `;

                        commentsList.insertBefore(newComment, commentsList.firstChild);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }
});
