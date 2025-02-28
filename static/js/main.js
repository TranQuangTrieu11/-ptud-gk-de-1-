document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('post-form');
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const title = document.getElementById('title').value;
            const content = document.getElementById('content').value;

            if (title && content) {
                // Here you would typically send the data to the server
                console.log('Title:', title);
                console.log('Content:', content);
                // Example: send data using fetch API
                // fetch('/submit-post', {
                //     method: 'POST',
                //     headers: {
                //         'Content-Type': 'application/json'
                //     },
                //     body: JSON.stringify({ title, content })
                // }).then(response => {
                //     if (response.ok) {
                //         // Handle success
                //     } else {
                //         // Handle error
                //     }
                // });
            } else {
                alert('Please fill in both fields.');
            }
        });
    }
});