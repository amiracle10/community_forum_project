document.addEventListener('DOMContentLoaded', function () {
  const homeForm = document.getElementById('discussion-form');
  const forumForm = document.getElementById('forum-discussion-form');

  const handleFormSubmit = async (form) => {
    const category = form.querySelector('[name="category_id"]')?.value;
    const title = form.querySelector('[name="title"]').value;
    const body = form.querySelector('[name="body"]').value;

    try {
      const response = await fetch('/post/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: new URLSearchParams({ category_id: category, title, body }),
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else {
        const data = await response.json();
        alert(data.message || data.error || 'Unknown error');
      }
    } catch (err) {
      alert('Network error: ' + err.message);
    }
  };

  if (homeForm) {
    homeForm.addEventListener('submit', function (e) {
      e.preventDefault();
      handleFormSubmit(homeForm);
    });
  }

  if (forumForm) {
    forumForm.addEventListener('submit', function (e) {
      e.preventDefault();
      handleFormSubmit(forumForm);
    });
  }

  function getCookie(name) {
    const cookieStr = document.cookie;
    const cookies = cookieStr.split(';');
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) return decodeURIComponent(value);
    }
    return null;
  }
});
